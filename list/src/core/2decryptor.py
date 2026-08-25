import  base64
import json


class ResponseDecryptor:
    """
    响应报文解密工具类（完美兼容 Java 32位溢出特性的 FNV Hash 算法）
    """

    def __init__(self, secret_key: str):
        """
        初始化解密器
        :param secret_key: 可接入包里提供的密钥 B
        """
        self.secret_key = secret_key

    @staticmethod
    def _to_int32(n: int) -> int:
        """
        内部方法：模拟 Java 的 32 位有符号整数溢出行为
        """
        n = n & 0xFFFFFFFF
        # 如果最高位（符号位）为 1，则转换为负数
        return n - 0x100000000 if n & 0x80000000 else n

    def _fnv_hash(self, data: str) -> int:
        """
        内部方法：对应 Java 的 fnvHash 方法
        包含雪崩效应混合阶段的魔改 FNV 算法
        """
        p = 16777619
        # Java 中 (int) 2166136261L 的实际值为 -2128831035
        hash_val = -2128831035

        for char in data:
            # Java 的 charAt 返回的是 16位 Unicode 编码，等同于 Python 的 ord()
            hash_val = self._to_int32(hash_val ^ ord(char))
            hash_val = self._to_int32(hash_val * p)

        # 雪崩混合阶段 (Avalanche phase)
        hash_val = self._to_int32(hash_val + self._to_int32(hash_val << 13))
        # Python 的 >> 对于负数也是算术右移（高位补1），完美契合 Java 的 >>
        hash_val = self._to_int32(hash_val ^ (hash_val >> 7))
        hash_val = self._to_int32(hash_val + self._to_int32(hash_val << 3))
        hash_val = self._to_int32(hash_val ^ (hash_val >> 17))
        hash_val = self._to_int32(hash_val + self._to_int32(hash_val << 5))

        # 模拟 Java 的 Math.abs(int) 陷阱
        # 注意：在 Java 中 Math.abs(Integer.MIN_VALUE) 依然是 Integer.MIN_VALUE (-2147483648)
        if hash_val == -2147483648:
            return -2147483648
        return abs(hash_val)

    @staticmethod
    def _long_to_bytes(long_value: int) -> bytearray:
        """
        内部方法：对应 Java 的 longToBytes 方法
        将整数转换为 8 字节的小端字节序数组
        """
        result = bytearray(8)
        for i in range(8):
            result[i] = long_value & 0xFF
            long_value >>= 8
        return result

    @staticmethod
    def _xor(content: bytearray, key: bytearray):
        """
        内部方法：对应 Java 的 xor 方法
        循环异或解密，直接在原数组上修改
        """
        key_length = len(key)
        if key_length == 0:
            return

        i = 0
        j = 0
        while i < len(content):
            content[i] ^= key[j]
            i += 1
            j = (j + 1) % key_length

    def decrypt_to_str(self, header_key: str, base64_body: str) -> str:
        """
        解密响应报文，返回原始字符串

        :param header_key: 响应头中提取出来的拼接因子 A (例如 "114280586036259940")
        :param base64_body: 响应体 (Base64编码的字符串)
        :return: 原始响应报文字符串 (通常是 JSON 格式)
        """
        if not header_key:
            raise ValueError("传入的 header_key 不能为空")

        if not base64_body:
            return ""

        # 1. Base64 解码，转为可修改的 bytearray
        try:
            decode_base64 = bytearray(base64.b64decode(base64_body))
        except Exception as e:
            raise ValueError(f"Base64 解码失败: {e}")

        # 2. 拼接字符串并计算 Hash
        combined_key = header_key + self.secret_key
        hash_val = self._fnv_hash(combined_key)

        # 3. 获取 8 字节的密钥数组
        key_bytes = self._long_to_bytes(hash_val)

        # 4. 执行循环异或解密
        self._xor(decode_base64, key_bytes)

        # 5. 解码为 utf-8 字符串
        return decode_base64.decode('utf-8')

    def decrypt_to_dict(self, header_key: str, base64_body: str) -> dict:
        """
        解密响应报文，并直接解析为 Python 字典

        :param header_key: 响应头中提取出来的拼接因子 A
        :param base64_body: 响应体 (Base64编码的字符串)
        :return: 解析后的 JSON 字典
        """
        raw_str = self.decrypt_to_str(header_key, base64_body)
        if not raw_str:
            return {}

        try:
            return json.loads(raw_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"解密成功，但解析 JSON 失败。原始解密内容: {raw_str} | 错误信息: {e}")


# ================= 实际调用示例 =================
if __name__ == '__main__':
    # 1. 在项目启动或初始化时，实例化解密器 (只需传入一次密钥)
    SECRET_KEY = "QwE2dGV2aSICEmkyY3BpcBoZdTwibWJpSkdnKiJzdWNbRjZjLiIsIlxKIXUiOnsiTUApf3MiOiIKE3MhMzMwOAEVcyczNDM5DxdzMn19"
    decryptor = ResponseDecryptor("vUayBSwQEt3MvpkrJFMBiFX6LJz91NEZJ7kAmbVX7CYbMk4D4b")

    # 2. 模拟从 HTTP 响应中获取的数据
    mock_header_value = "116532420652769667"

    # 假设这是服务端加密后返回的 base64 字符串
    # 此处仅为代码可运行提供的占位测试数据，运行会报 json 解析错误，因为占位数据不是真实加密出来的
    mock_base64_body = base64.b64encode(b"dummy_data").decode('utf-8')

    # 3. 业务代码中直接调用解密方法
    try:
        # 如果你确定服务端返回的是 JSON，推荐直接调用 decrypt_to_dict
        result_dict = decryptor.decrypt_to_dict(
            header_key=mock_header_value,
            base64_body=mock_base64_body
        )
        print("解密后的字典:", result_dict)
    except Exception as e:
        print("解密发生错误:", e)