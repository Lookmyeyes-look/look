# 导入 Base64 解码工具，用于还原 HTTP 响应体中的密文。
import base64
# 导入 JSON 工具，用于解析解密后的响应内容。
import json
# 导入 Any 类型，用于标注 JSON 解析结果。
from typing import Any


# 定义响应解密器，统一处理当前协议和旧版协议。
class ResponseDecryptor:
    """RapidTV 响应解密器。"""

    # 初始化解密器，并保存应用侧的固定密钥。
    def __init__(self, secret_key: str):
        # 保存服务端约定的 secret。
        self.secret_key = secret_key

    # 将整数限制为 Java int 的有符号 32 位范围。
    @staticmethod
    def _to_int32(value: int) -> int:
        # 只保留最低 32 位，模拟 Java int 溢出。
        value &= 0xFFFFFFFF
        # 如果最高位为 1，就转换成负数表示。
        return value - 0x100000000 if value & 0x80000000 else value

    # 计算 Java 示例中的 FNV32 哈希值。
    @classmethod
    def fnv32_hash(cls, data: str) -> int:
        # 设置 Java 中 (int) 2166136261L 对应的初始有符号值。
        hash_value = -2128831035
        # 设置 FNV 算法使用的质数。
        prime = 16777619

        # Java 的 charAt 按 UTF-16 code unit 遍历字符串。
        utf16 = data.encode("utf-16-be", "surrogatepass")
        # 每两个字节读取一个 UTF-16 code unit。
        for index in range(0, len(utf16), 2):
            # 将当前两个字节转换成大端整数。
            char_code = int.from_bytes(utf16[index:index + 2], "big")
            # 执行 Java 中的 hash 与字符异或操作。
            hash_value = cls._to_int32(hash_value ^ char_code)
            # 执行乘法，并截断到 Java int 范围。
            hash_value = cls._to_int32(hash_value * prime)

        # 执行 Java 示例中的第一步雪崩混合。
        hash_value = cls._to_int32(hash_value + cls._to_int32(hash_value << 13))
        # 执行带符号右移 7 位并异或。
        hash_value = cls._to_int32(hash_value ^ (hash_value >> 7))
        # 执行第二步左移加法混合。
        hash_value = cls._to_int32(hash_value + cls._to_int32(hash_value << 3))
        # 执行带符号右移 17 位并异或。
        hash_value = cls._to_int32(hash_value ^ (hash_value >> 17))
        # 执行最后一步左移加法混合。
        hash_value = cls._to_int32(hash_value + cls._to_int32(hash_value << 5))

        # 处理 Java Math.abs(Integer.MIN_VALUE) 的特殊情况。
        return -0x80000000 if hash_value == -0x80000000 else abs(hash_value)

    # 将哈希结果转换为协议需要的 8 字节小端数组。
    @staticmethod
    def _long_to_bytes(value: int) -> bytes:
        # 创建 8 字节的可修改缓冲区。
        result = bytearray(8)
        # 逐字节写入低位到高位的数据。
        for index in range(8):
            # 取出当前整数最低 8 位。
            result[index] = value & 0xFF
            # 算术右移 8 位，准备处理下一个字节。
            value >>= 8
        # 返回不可修改的字节串作为 XOR 密钥。
        return bytes(result)

    # 使用循环 XOR 密钥就地解密字节数组。
    @staticmethod
    def _xor(content: bytearray, key: bytes) -> None:
        # 遍历所有密文字节。
        for index in range(len(content)):
            # 使用密钥取模实现循环 XOR。
            content[index] ^= key[index % len(key)]

    # 将 HTTP 响应体从 Base64 文本转换为密文字节。
    @staticmethod
    def _decode_body(base64_body: str) -> bytes:
        # 捕获 Base64 格式错误并转换为业务异常。
        try:
            # 去除响应体中可能存在的换行和空格。
            encoded = "".join(base64_body.split())
            # 严格校验 Base64 字符串并完成解码。
            return base64.b64decode(encoded, validate=True)
        # 将底层异常包装成明确的解码错误。
        except Exception as exc:
            # 保留原始异常作为上下文，便于定位问题。
            raise ValueError(f"Base64 解码失败: {exc}") from exc

    # 根据响应头生成当前协议和旧协议的候选密钥。
    def _candidate_keys(self, header_key: str) -> list[bytes]:
        # 初始化候选密钥列表。
        keys = []

        # 当前服务端协议直接使用 X-Edevic-Kweb 数值作为 8 字节密钥。
        try:
            # 将响应头中的十进制字符串转换成整数。
            header_number = int(header_key, 10)
            # 确认整数可以安全地放入无符号 64 位范围。
            if 0 <= header_number <= 0xFFFFFFFFFFFFFFFF:
                # 按协议使用小端序生成 8 字节密钥。
                keys.append(header_number.to_bytes(8, "little"))
        # 非数字响应头无法使用当前协议时，继续尝试旧协议。
        except ValueError:
            # 不在这里中断，因为旧协议仍可能可以处理该值。
            pass

        # 旧版协议使用 Header 和 secret 拼接后的 Java FNV32 结果。
        legacy_key = self._long_to_bytes(self.fnv32_hash(f"{header_key}{self.secret_key}"))
        # 避免两个协议恰好生成相同密钥时重复尝试。
        if legacy_key not in keys:
            # 将旧版密钥追加到候选列表末尾。
            keys.append(legacy_key)
        # 返回按优先级排列的候选密钥。
        return keys

    # 使用指定密钥解密一份已经完成 Base64 解码的密文。
    @classmethod
    def _decrypt_bytes(cls, encrypted: bytes, key: bytes) -> bytes:
        # 复制密文，避免修改调用方持有的原始字节。
        decrypted = bytearray(encrypted)
        # 对复制后的字节执行循环 XOR。
        cls._xor(decrypted, key)
        # 返回解密后的不可变字节串。
        return bytes(decrypted)

    # 解密 Base64 响应体并返回明文字符串。
    def decrypt_to_str(self, header_key: str, base64_body: str) -> str:
        # 校验响应头密钥是否存在。
        if not header_key:
            # 缺少响应头时无法生成任何协议密钥。
            raise ValueError("响应头 X-Edevic-Kweb 不能为空")
        # 空响应体直接返回空字符串。
        if not base64_body:
            # 保持调用方对空响应的原有处理方式。
            return ""

        # 将 Base64 文本转换为密文字节。
        encrypted = self._decode_body(base64_body)
        # 记录最后一次 UTF-8 解码错误。
        last_error = None
        # 按当前协议优先、旧协议回退的顺序尝试密钥。
        for key in self._candidate_keys(header_key):
            # 尝试使用当前候选密钥完成解密和 UTF-8 解码。
            try:
                # 解密字节后转换成明文字符串。
                return self._decrypt_bytes(encrypted, key).decode("utf-8")
            # 当前候选密钥不正确时通常会产生 UTF-8 错误。
            except UnicodeDecodeError as exc:
                # 保存错误，继续尝试下一个协议密钥。
                last_error = exc

        # 所有候选密钥都失败时抛出最后一次解码错误。
        raise ValueError(f"解密结果不是有效的 UTF-8: {last_error}")

    # 解密响应体并将明文解析为 JSON 对象。
    def decrypt_response(self, encrypted_body: str, x_edevic_kweb: str) -> dict:
        # 校验响应头密钥是否存在。
        if not x_edevic_kweb:
            # 缺少 Header 时直接返回明确错误。
            raise ValueError("解密失败: 响应头 X-Edevic-Kweb 不能为空")
        # 校验响应体是否存在。
        if not encrypted_body:
            # 空响应无法解析为 JSON。
            raise ValueError("解密失败: 响应体为空")

        # 先完成一次 Base64 解码，后续候选密钥共用结果。
        encrypted = self._decode_body(encrypted_body)
        # 保存每个候选密钥失败时的错误信息。
        errors = []
        # 依次尝试当前协议和旧版协议。
        for key in self._candidate_keys(x_edevic_kweb):
            # 使用候选密钥解密并解析 JSON。
            try:
                # 将解密后的字节转换成 UTF-8 文本。
                plaintext = self._decrypt_bytes(encrypted, key).decode("utf-8")
                # 将文本解析成 Python 对象。
                result: Any = json.loads(plaintext)
                # 接口约定响应根节点必须是 JSON 对象。
                if not isinstance(result, dict):
                    # 非对象响应不符合客户端返回类型约定。
                    raise ValueError("JSON 根节点不是对象")
                # 返回解析成功的 JSON 字典。
                return result
            # 记录当前密钥的解码、JSON 或类型错误。
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
                # 将错误转换成字符串，供最终异常汇总。
                errors.append(str(exc))

        # 汇总所有候选密钥的失败原因。
        detail = "; ".join(errors)
        # 所有协议都失败时返回带有详细原因的异常。
        raise ValueError(f"解密失败: 无法用响应头密钥解析 JSON ({detail})")


# 仅在直接运行本文件时执行简单的哈希冒烟测试。
if __name__ == "__main__":
    # 创建一个使用真实配置格式的解密器实例。
    decryptor = ResponseDecryptor(
        "vUayBSwQEt3MvpkrJFMBiFX6LJz91NEZJ7kAmbVX7CYbMk4D4b"
    )
    # 输出测试字符串对应的 FNV32 结果。
    print(decryptor.fnv32_hash("test_string"))
