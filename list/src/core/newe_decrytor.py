import base64
import json
import re
from typing import Optional, Dict, Any


class FinalDecryptor:
    """
    最终修复版本 - 解决字符编码问题
    """

    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    def fnv_hash(self, data: str) -> int:
        """修复的 FNV 哈希算法"""
        p = 16777619
        # 使用 Java 的有符号初始值
        hash_val = -2128831035

        for char in data:
            char_code = ord(char)
            # 模拟 Java 的 32 位有符号整数运算
            hash_val ^= char_code
            # 强制转换为 32 位有符号
            hash_val = self._to_int32(hash_val * p)

        # 混合操作
        hash_val = self._to_int32(hash_val + self._to_int32(hash_val << 13))
        hash_val = self._to_int32(hash_val ^ (hash_val >> 7))
        hash_val = self._to_int32(hash_val + self._to_int32(hash_val << 3))
        hash_val = self._to_int32(hash_val ^ (hash_val >> 17))
        hash_val = self._to_int32(hash_val + self._to_int32(hash_val << 5))

        # Math.abs
        if hash_val < 0:
            hash_val = -hash_val

        return hash_val

    def _to_int32(self, n: int) -> int:
        """转换为 32 位有符号整数"""
        n = n & 0xFFFFFFFF
        if n & 0x80000000:
            n -= 0x100000000
        return n

    def long_to_bytes(self, value: int) -> bytes:
        """整数转 8 字节（小端序）"""
        # 将 32 位有符号整数转换为 64 位
        if value & 0x80000000:
            value = value | 0xFFFFFFFF00000000
        else:
            value = value & 0xFFFFFFFF

        result = bytearray(8)
        for i in range(8):
            result[i] = value & 0xFF
            value >>= 8

        return bytes(result)

    def decrypt_clean(self, encrypted_base64: str, header_key: str) -> Dict[str, Any]:
        """
        解密并清理结果

        返回:
            解析后的 JSON 字典
        """
        try:
            # 1. Base64 解码
            encrypted_bytes = bytearray(base64.b64decode(encrypted_base64))

            # 2. 计算密钥
            combined = f"{header_key}{self.secret_key}"
            hash_val = self.fnv_hash(combined)
            key_bytes = self.long_to_bytes(hash_val)

            print(f"密钥: {key_bytes.hex()}")

            # 3. 异或解密
            for i in range(len(encrypted_bytes)):
                encrypted_bytes[i] ^= key_bytes[i % 8]

            # 4. 转换为字符串（先尝试 UTF-8）
            try:
                decrypted_str = encrypted_bytes.decode('utf-8')
            except UnicodeDecodeError:
                # 如果 UTF-8 失败，尝试 Latin-1
                decrypted_str = encrypted_bytes.decode('latin-1')

            print(f"原始解密结果: {decrypted_str[:200]}")

            # 5. 清理控制字符
            cleaned = self._clean_control_chars(decrypted_str)
            print(f"清理后结果: {cleaned[:200]}")

            # 6. 尝试解析 JSON
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError as e:
                print(f"JSON 解析失败: {e}")

                # 尝试修复常见的 JSON 格式问题
                fixed = self._try_fix_json(cleaned)
                if fixed:
                    try:
                        return json.loads(fixed)
                    except:
                        pass

                # 如果还是失败，返回原始文本
                return {"raw_text": cleaned, "error": "JSON 解析失败"}

        except Exception as e:
            return {"error": str(e)}

    def _clean_control_chars(self, text: str) -> str:
        """
        清理控制字符

        保留 JSON 允许的控制字符：
        - \b (退格)
        - \f (换页)
        - \n (换行)
        - \r (回车)
        - \t (制表)
        """
        # 首先，替换控制字符为空格（除了 JSON 允许的）
        result = []
        for char in text:
            code = ord(char)
            if code == 0x08:  # \b
                result.append('\\b')
            elif code == 0x0C:  # \f
                result.append('\\f')
            elif code == 0x0A:  # \n
                result.append('\\n')
            elif code == 0x0D:  # \r
                result.append('\\r')
            elif code == 0x09:  # \t
                result.append('\\t')
            elif code < 32:  # 其他控制字符
                result.append(' ')  # 替换为空格
            else:
                result.append(char)

        cleaned = ''.join(result)

        # 修复常见的编码问题
        # 1. 修复乱码的引号
        cleaned = re.sub(r'[Ã¢âÃ¢â¬Ã¢â¬]', "'", cleaned)
        cleaned = re.sub(r'[Ã¢âÃ¢âÃ¢â¬Ã¢â¬]', '"', cleaned)

        # 2. 修复常见的乱码模式
        replacements = {
            'Ã©': 'é',
            'Ã¨': 'è',
            'Ãª': 'ê',
            'Ã«': 'ë',
            'Ã¡': 'á',
            'Ã ': 'à',
            'Ã¢': 'â',
            'Ã¤': 'ä',
            'Ã³': 'ó',
            'Ã²': 'ò',
            'Ã´': 'ô',
            'Ã¶': 'ö',
            'Ãº': 'ú',
            'Ã¹': 'ù',
            'Ã»': 'û',
            'Ã¼': 'ü',
            'Ã±': 'ñ',
            'Ã§': 'ç',
        }

        for wrong, right in replacements.items():
            cleaned = cleaned.replace(wrong, right)

        return cleaned

    def _try_fix_json(self, text: str) -> Optional[str]:
        """尝试修复 JSON 格式问题"""
        try:
            # 1. 确保以 { 开头
            if not text.strip().startswith('{'):
                # 查找第一个 {
                start = text.find('{')
                if start != -1:
                    text = text[start:]

            # 2. 确保以 } 结尾
            if not text.strip().endswith('}'):
                # 查找最后一个 }
                end = text.rfind('}')
                if end != -1:
                    text = text[:end + 1]

            # 3. 修复键的引号
            # 查找没有引号的键并添加
            import re
            # 匹配模式: {\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:
            pattern = r'{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:'
            match = re.search(pattern, text)
            if match and not text[match.start(1) - 1] == '"':
                # 键没有引号，需要添加
                key = match.group(1)
                text = text.replace(f'{key}:', f'"{key}":', 1)

            # 4. 修复字符串值中的转义字符
            text = re.sub(r'(?<!\\)"', '\\"', text)  # 转义未转义的引号

            return text

        except Exception as e:
            print(f"修复 JSON 失败: {e}")
            return None


# 专门针对你的结果的修复
def analyze_and_fix_your_result():
    """分析和修复你的特定结果"""

    # 你的解密结果
    your_result = '\x1a¿°%evi"X¬ïccpip@§óm"mbi\x10ùá{"suc\x01ø°2.",\x06ô§$":{"\x17þ¯.s":"P­õp3308[«õv3439U©õc}}'

    print("分析你的解密结果:")
    print("=" * 60)

    # 1. 转换为字节
    bytes_data = your_result.encode('latin-1')
    print(f"字节数据: {bytes_data[:50].hex()}")

    # 2. 尝试找出模式
    # 我们看到 "suc" 在位置？
    suc_pos = your_result.find('suc')
    if suc_pos != -1:
        print(f"'suc' 在位置: {suc_pos}")
        print(f"前后字符:")
        for i in range(max(0, suc_pos - 5), min(len(your_result), suc_pos + 8)):
            char = your_result[i]
            if 32 <= ord(char) < 127:
                print(f"  [{i}] '{char}' (0x{ord(char):02X})")
            else:
                print(f"  [{i}] \\x{ord(char):02X}")

    # 3. 猜测原始文本
    # 基于模式，原始可能是: {"status": "success", ...}
    # 让我们尝试计算密钥

    # 假设 "suc" 应该是 "success" 的一部分
    # 位置 suc_pos 是 's'，对应明文的 's'
    # 那么密钥在这个位置是: 密文 ^ 明文
    # 但我们不知道整个明文

    # 4. 尝试手动清理
    print(f"\n尝试清理控制字符:")

    cleaner = FinalDecryptor("dummy")
    cleaned = cleaner._clean_control_chars(your_result)
    print(f"清理后: {cleaned}")

    # 5. 提取可读部分
    print(f"\n可读部分（ASCII 字符）:")
    ascii_chars = []
    for i, char in enumerate(your_result):
        if 32 <= ord(char) < 127:
            ascii_chars.append(char)
        else:
            ascii_chars.append('.')

    ascii_str = ''.join(ascii_chars)
    print(f"ASCII 表示: {ascii_str}")

    # 查找可能的 JSON 片段
    import re
    json_pattern = r'[\{\}\"\:\,\[\]0-9a-zA-Z]+'
    matches = re.findall(json_pattern, ascii_str)
    for match in matches:
        if len(match) > 10 and ('{' in match or '}' in match):
            print(f"可能的 JSON 片段: {match}")


# 主程序
if __name__ == "__main__":
    # 你的数据
    SECRET_KEY = "vUayBSwQEt3MvpkrJFMBiFX6LJz91NEZJ7kAmbVX7CYbMk4D4b"
    HEADER_KEY = "116532420662488933"

    # 你提供的加密数据
    ENCRYPTED_BASE64 = "Cw9vB2V2aSJKHDBBY3BpcFIXLE8ibWJpAkk+WSJzdWMTSG8QLiIsIhREeAYiOnsiBU5wDHMiOiJCHSpSMzMwOEkbKlQzNDM5RxkqQX19"   # 填入完整数据

    if ENCRYPTED_BASE64:
        print("=" * 60)
        print("最终解密尝试")
        print("=" * 60)

        decryptor = FinalDecryptor(SECRET_KEY)

        # 解密
        result = decryptor.decrypt_clean(ENCRYPTED_BASE64, HEADER_KEY)

        print(f"\n解密结果:")
        if isinstance(result, dict):
            if 'error' in result:
                print(f"❌ 错误: {result['error']}")
            else:
                print(f"✅ 成功解析为 JSON:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"原始结果: {result}")

    # 分析你的特定结果
    print("\n" + "=" * 60)
    print("分析你的特定解密结果")
    print("=" * 60)
    analyze_and_fix_your_result()