import base64
import json
import struct


class DebugDecryptor:
    """
    带详细调试的解密器
    """

    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.debug_log = []

    def _log(self, msg: str, data=None):
        """记录调试日志"""
        entry = msg
        if data is not None:
            entry += f" -> {data}"
        self.debug_log.append(entry)
        print(f"[DEBUG] {entry}")

    def _to_int32(self, n: int) -> int:
        n = n & 0xFFFFFFFF
        return n - 0x100000000 if n & 0x80000000 else n

    def _fnv_hash(self, data: str) -> int:
        self._log(f"FNV输入: {data[:20]}... (长度: {len(data)})")

        p = 16777619
        hash_val = -2128831035
        self._log(f"初始哈希值: {hash_val} (0x{hash_val:08X})")

        for i, char in enumerate(data[:3]):  # 只打印前3个字符的处理
            char_code = ord(char)
            before_xor = hash_val
            hash_val ^= char_code
            hash_val = self._to_int32(hash_val)
            after_xor = hash_val
            hash_val *= p
            hash_val = self._to_int32(hash_val)
            after_mul = hash_val
            self._log(f"  字符{i}: '{char}' (0x{char_code:04X}) | "
                      f"异或前: 0x{before_xor:08X} | "
                      f"异或后: 0x{after_xor:08X} | "
                      f"乘后: 0x{after_mul:08X}")

        # 雪崩混合阶段
        steps = [
            ("+ <<13", lambda x: self._to_int32(x + self._to_int32(x << 13))),
            (">>7", lambda x: self._to_int32(x ^ (x >> 7))),
            ("+ <<3", lambda x: self._to_int32(x + self._to_int32(x << 3))),
            (">>17", lambda x: self._to_int32(x ^ (x >> 17))),
            ("+ <<5", lambda x: self._to_int32(x + self._to_int32(x << 5))),
        ]

        for name, func in steps:
            before = hash_val
            hash_val = func(hash_val)
            self._log(f"  混合{name}: 0x{before:08X} -> 0x{hash_val:08X}")

        # Math.abs
        if hash_val == -2147483648:
            result = -2147483648
        else:
            result = abs(hash_val)

        self._log(f"最终哈希值: {result} (0x{result:08X})")
        return result

    def _long_to_bytes(self, long_value: int) -> bytearray:
        result = bytearray(8)
        self._log(f"转换整数到字节: {long_value} (0x{long_value:016X})")

        for i in range(8):
            byte_val = long_value & 0xFF
            result[i] = byte_val
            self._log(f"  字节[{i}]: 0x{long_value & 0xFF:02X}")
            long_value >>= 8

        self._log(f"结果字节: {result.hex()}")
        return result

    def decrypt_with_debug(self, header_key: str, base64_body: str) -> str:
        """带详细调试的解密"""
        self.debug_log = []  # 清空日志

        self._log("=" * 50)
        self._log("开始解密")
        self._log("=" * 50)

        # 1. 检查输入
        self._log(f"Header Key: {header_key}")
        self._log(f"Base64 Body 长度: {len(base64_body)}")
        self._log(f"Base64 Body 前50字符: {base64_body[:50]}")

        # 2. Base64 解码
        try:
            decoded_bytes = bytearray(base64.b64decode(base64_body))
            self._log(f"Base64 解码成功")
            self._log(f"解码后长度: {len(decoded_bytes)} 字节")
            self._log(f"解码后16进制: {decoded_bytes[:20].hex()}...")
            self._log(f"解码后ASCII: {decoded_bytes[:20]!r}")
        except Exception as e:
            raise ValueError(f"Base64 解码失败: {e}")

        # 3. 拼接密钥
        combined_key = header_key + self.secret_key
        self._log(f"拼接密钥: {combined_key}")
        self._log(f"拼接密钥长度: {len(combined_key)}")

        # 4. 计算哈希
        hash_val = self._fnv_hash(combined_key)

        # 5. 生成密钥
        key_bytes = self._long_to_bytes(hash_val)
        self._log(f"生成解密密钥: {key_bytes.hex()}")
        self._log(f"密钥字节: {list(key_bytes)}")

        # 6. 异或解密
        original_bytes = decoded_bytes.copy()
        self._log("开始异或解密...")

        key_len = len(key_bytes)
        for i in range(min(10, len(decoded_bytes))):  # 只打印前10个字节
            before = decoded_bytes[i]
            key_byte = key_bytes[i % key_len]
            decoded_bytes[i] ^= key_byte
            after = decoded_bytes[i]
            self._log(f"  字节[{i}]: 0x{before:02X} ^ 0x{key_byte:02X} = 0x{after:02X} "
                      f"({before:3d} ^ {key_byte:3d} = {after:3d})")

        # 7. 尝试解码
        try:
            result = decoded_bytes.decode('utf-8')
            self._log(f"UTF-8 解码成功")
            self._log(f"解密结果前200字符: {result[:200]}")
            return result
        except UnicodeDecodeError as e:
            self._log(f"UTF-8 解码失败: {e}")

            # 尝试其他编码
            encodings = ['gbk', 'latin-1', 'iso-8859-1', 'cp1252']
            for enc in encodings:
                try:
                    result = decoded_bytes.decode(enc)
                    self._log(f"{enc} 解码成功")
                    return result
                except:
                    pass

            raise ValueError("无法解码为任何已知编码")

    def save_debug_log(self, filename: str = "decrypt_debug.log"):
        """保存调试日志"""
        with open(filename, 'w', encoding='utf-8') as f:
            for line in self.debug_log:
                f.write(line + '\n')
        print(f"调试日志已保存到: {filename}")


# 使用示例
if __name__ == "__main__":
    # 你的数据
    SECRET_KEY = "vUayBSwQEt3MvpkrJFMBiFX6LJz91NEZJ7kAmbVX7CYbMk4D4b"
    HEADER_KEY = "116532420652769667"
    BASE64_BODY = "QwE2dGV2aSICEmkyY3BpcBoZdTwibWJpSkdnKiJzdWNbRjZjLiIsIlxKIXUiOnsiTUApf3MiOiIKE3MhMzMwOAEVcyczNDM5DxdzMn19"  # 把你的实际 base64 数据放这里

    if BASE64_BODY:
        decryptor = DebugDecryptor(SECRET_KEY)

        try:
            result = decryptor.decrypt_with_debug(HEADER_KEY, BASE64_BODY)
            print(f"\n解密结果: {result[:200]}...")

            # 尝试解析 JSON
            try:
                json_data = json.loads(result)
                print(f"JSON 解析成功: {json_data}")
            except json.JSONDecodeError as e:
                print(f"JSON 解析失败: {e}")
                print(f"原始结果: {result[:500]}")
        except Exception as e:
            print(f"解密失败: {e}")

        # 保存调试日志
        decryptor.save_debug_log()