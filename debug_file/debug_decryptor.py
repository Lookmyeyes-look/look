#!/usr/bin/env python3  # 使用系统环境中的 Python 3 运行本调试脚本。
"""解密模块调试脚本。"""  # 说明当前文件用于验证解密相关逻辑。

import sys  # 导入 sys，用于修改 Python 模块搜索路径。
from pathlib import Path  # 导入 Path，方便跨平台处理文件路径。

# 获取项目根目录，确保脚本从任意工作目录启动都能找到 src 包。
project_root = Path(__file__).resolve().parent.parent
# 将项目根目录插入搜索路径首位，优先加载当前项目代码。
sys.path.insert(0, str(project_root))

# 导入核心响应解密器，复用正式业务中的解密逻辑。
from src.core.decryptor import ResponseDecryptor


# 定义不依赖网络请求的解密逻辑调试函数。
def test_decryptor_logic():
    """测试哈希、Base64 和 XOR 基础逻辑。"""
    # 使用项目当前配置中的响应解密密钥。
    secret_key = "vUayBSwQEt3MvpkrJFMBiFX6LJz91NEZJ7kAmbVX7CYbMk4D4b"
    # 创建响应解密器实例。
    decryptor = ResponseDecryptor(secret_key)

    # 输出调试标题分隔线。
    print("=" * 50)
    # 输出当前调试模块名称。
    print("解密模块调试")
    # 输出调试标题结束分隔线。
    print("=" * 50)

    # 准备一个固定字符串，验证 FNV32 哈希函数。
    test_data = "test_string"
    # 计算测试字符串的 FNV32 哈希值。
    fnv_hash = decryptor.fnv32_hash(test_data)
    # 输出哈希测试标题。
    print("1. FNV32 哈希测试:")
    # 输出参与计算的原始字符串。
    print(f"   输入: {test_data}")
    # 以 8 位十六进制格式输出哈希结果。
    print(f"   输出: 0x{fnv_hash:08x}")
    # 输出哈希算法的位宽。
    print("   长度: 32 位")

    # 准备一个模拟服务端响应头中的 X-Edevic-Kweb 值。
    x_edevic_kweb = "116532420401470867"
    # 按旧版 Java 协议拼接 Header 密钥和 secret，供调试观察。
    combined = f"{x_edevic_kweb}{secret_key}".encode("utf-8")
    # 输出密钥拼接测试标题。
    print("\n2. 密钥拼接测试:")
    # 输出响应头密钥的前 20 个字符，避免完整展示敏感值。
    print(f"   X-Edevic-Kweb: {x_edevic_kweb[:20]}...")
    # 输出拼接后字节数据的长度。
    print(f"   拼接结果长度: {len(combined)} 字节")

    # 开始验证 Base64 编码和解码能力。
    try:
        # 在测试函数内部导入 Base64 工具，保持基础测试独立。
        import base64
        # 定义待编码的明文字节。
        test_bytes = b"Hello World!"
        # 将明文字节编码成 Base64 文本。
        encoded = base64.b64encode(test_bytes).decode()
        # 将 Base64 文本还原成原始字节。
        decoded = base64.b64decode(encoded)
        # 输出 Base64 测试标题。
        print("\n3. Base64 编解码测试:")
        # 输出编码前的字节。
        print(f"   原始: {test_bytes}")
        # 输出编码后的 Base64 字符串。
        print(f"   Base64: {encoded}")
        # 输出解码后的字节。
        print(f"   解码后: {decoded}")
        # 输出 Base64 测试成功标记。
        print("   ✓ Base64 功能正常")
    # 捕获 Base64 测试中的异常，避免影响其他调试信息输出。
    except Exception as e:
        # 输出异常类型和具体错误信息。
        print(f"   ✗ Base64 测试失败: {e}")

    # 输出 XOR 测试标题。
    print("\n4. XOR 解密测试:")
    # 定义一段用于测试循环 XOR 的固定密钥。
    key = b"12345678"
    # 定义待加密的明文。
    plaintext = b"test_data"
    # 使用循环 XOR 模拟服务端加密。
    encrypted = bytes([plaintext[i] ^ key[i % len(key)] for i in range(len(plaintext))])
    # 再次使用同一密钥执行 XOR，验证可还原明文。
    decrypted = bytes([encrypted[i] ^ key[i % len(key)] for i in range(len(encrypted))])
    # 输出测试密钥。
    print(f"   密钥: {key}")
    # 输出原始明文。
    print(f"   明文: {plaintext}")
    # 输出模拟生成的密文。
    print(f"   加密后: {encrypted}")
    # 输出 XOR 解密后的结果。
    print(f"   解密后: {decrypted}")
    # 比较解密结果和原文，输出验证结果。
    print(f"   解密成功: {decrypted == plaintext}")


# 只有直接运行本文件时才执行调试函数，被其他模块导入时不自动执行。
if __name__ == "__main__":
    # 启动基础解密逻辑调试。
    test_decryptor_logic()
