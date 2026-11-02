# 标记当前文件名称，便于调试输出和人工识别脚本用途。
import json  # 导入 JSON 工具，用于格式化输出解密后的 raw_response。
import sys  # 导入 sys，用于将项目根目录加入模块搜索路径。
from pathlib import Path  # 导入 Path，方便计算项目根目录。

# 计算当前 debug_file 目录的上一级项目根目录。
project_root = Path(__file__).resolve().parent.parent
# 将项目根目录放到搜索路径首位，确保导入的是当前项目源码。
sys.path.insert(0, str(project_root))
# 导入正式客户端，复用真实请求和响应处理逻辑。
from src.core.client import RapidTVClient


# 定义客户端调试入口函数。
def debug_client():
    """调试客户端初始化、请求头、登录和响应解密功能。"""
    # 输出调试标题分隔线。
    print("=" * 50)
    # 输出调试模块名称。
    print("客户端模块调试")
    # 输出调试标题结束分隔线。
    print("=" * 50)

    # 创建客户端实例，填入测试环境连接配置。
    client = RapidTVClient(
        # 设置测试环境 API 基础地址。
        base_url='https://rptv-db-api-test.playapp365.com',
        # 设置服务端识别的应用包名。
        package_name='test.drama.short',
        # 设置响应解密所需的应用密钥。
        secret_key='vUayBSwQEt3MvpkrJFMBiFX6LJz91NEZJ7kAmbVX7CYbMk4D4b',
        # 设置用于生成请求头的调试设备标识。
        device_id='debug_device_001x',
        # 设置用于生成请求头的调试用户标识。
        distinct_id='debug_distinct_001x'
    )

    # 输出客户端初始化完成提示。
    print("1. 客户端初始化完成")
    # 输出当前使用的 API 基础地址。
    print(f"   Base URL: {client.base_url}")
    # 输出当前设备标识。
    print(f"   Device ID: {client.device_id}")
    # 输出当前用户标识。
    print(f"   Distinct ID: {client.distinct_id}")

    # 调用客户端生成公共请求头，但不发送网络请求。
    headers = client._get_common_headers()
    # 输出请求头调试标题。
    print("\n2. 公共请求头:")
    # 遍历并输出每一个公共请求头。
    for key, value in headers.items():
        # 对时间字段只展示前 10 位，避免输出完整动态值。
        if key == 'X-Tove':
            # 截断时间字段，保持调试输出简洁。
            value = f"{value[:10]}..."
        # 输出请求头名称和值。
        print(f"   {key}: {value}")

    # 输出登录请求模拟标题，不会在此处发送网络请求。
    print("\n3. 登录请求数据模拟:")
    # 构造与登录接口一致的示例请求体。
    login_data = {
        # 设置用户或安装实例标识。
        "dper": "debug_distinct_001x",
        # 设置登录国家。
        "cconce": "US",
        # 设置用户来源渠道。
        "sleave": "fb",
        # 设置用户版本策略。
        "umai": 1,
        # 设置客户端初始化时间戳字段。
        "ofligh": 1785236624846,
    }
    # 输出登录接口路径。
    print("   接口: api/ulov/uplace/lshin")
    # 输出模拟请求体。
    print(f"   数据: {login_data}")

    # 询问是否执行真实登录请求。
    test_actual = input("\n是否实际发送测试请求？(y/n): ").strip().lower()
    # 仅在用户明确输入 y 时发送真实请求。
    if test_actual == 'y':
        # 输出实际请求开始提示。
        print("\n4. 发送实际请求...")
        # 捕获网络、解密和响应处理过程中的异常。
        try:
            # 调用登录接口，客户端会自动处理加密响应。
            response = client.login(country="US", source="fb", user_strategy=1)

            # 输出接口返回的 HTTP 状态码。
            print(f"   状态码: {response.get('status_code')}")

            # 输出完整响应字段，但排除后面单独处理的 data 和 headers。
            print("\n=== 错误详情（完整响应字段，不含 data 和 headers）===")
            # 遍历客户端标准响应字典中的所有字段。
            for key, value in response.items():
                # 避免重复输出业务数据和响应头。
                if key not in ('data', 'headers'):
                    # 输出字段名称和值。
                    print(f"   {key}: {value}")
            # 输出字段分隔线。
            print("   -------------------------------------")

            # 如果客户端已经成功解密，则读取业务数据。
            if 'data' in response:
                # 获取解密后的业务 JSON。
                data = response['data']
                # 输出业务状态码。
                print(f"   业务码 (sdevi): {data.get('sdevi', 'N/A')}")
                # 输出服务端业务消息。
                print(f"   消息 (mbird): {data.get('mbird', 'N/A')}")
                # 如果响应包含用户信息，则输出用户 ID。
                if 'dide' in data:
                    # 从 dide.uclos 读取用户 ID。
                    print(f"   用户ID: {data['dide'].get('uclos', 'N/A')}")

            # 如果客户端返回错误，则输出错误文本和解密 Header。
            if 'error' in response:
                # 输出客户端捕获的错误信息。
                print(f"   错误: {response['error']}")
                # 输出用于生成解密密钥的响应头。
                print(f"   X-Edevic-Kweb: {response.get('headers', {}).get('X-Edevic-Kweb', 'N/A')}")

            # 读取原始 Base64 响应体，便于独立验证解密逻辑。
            raw_response = response.get('raw_response')
            # 读取本次响应对应的解密 Header。
            response_key = response.get('headers', {}).get('X-Edevic-Kweb')
            # 只有原始响应体和解密 Header 都存在时才执行独立解析。
            if raw_response and response_key:
                # 捕获独立解密过程中的异常。
                try:
                    # 直接调用解密器解析 raw_response 为 Python 字典。
                    raw_json = client.decryptor.decrypt_response(
                        # 传入原始 Base64 响应体。
                        raw_response,
                        # 传入响应头中的解密因子。
                        response_key,
                    )
                    # 输出独立解析结果标题。
                    print("\n=== raw_response JSON ===")
                    # 以缩进和中文可读格式输出 JSON。
                    print(json.dumps(raw_json, ensure_ascii=False, indent=2))
                # 如果原始响应无法解析，则输出详细错误。
                except Exception as e:
                    # 输出异常类型和错误内容。
                    print(f"   raw_response JSON 解析失败: {type(e).__name__}: {e}")

            # 再次输出业务数据，兼容原有调试输出结构。
            if 'data' in response:
                # 获取解密后的业务 JSON。
                data = response['data']
                # 输出业务状态码。
                print(f"   业务码 (sdevi): {data.get('sdevi', 'N/A')}")
                # 输出服务端业务消息。
                print(f"   消息 (mbird): {data.get('mbird', 'N/A')}")
                # 如果响应包含用户信息，则输出用户 ID。
                if 'dide' in data:
                    # 从 dide.uclos 读取用户 ID。
                    print(f"   用户ID: {data['dide'].get('uclos', 'N/A')}")

            # 获取响应头，用于检查登录 Token。
            headers = response.get('headers', {})
            # 只有响应包含 Acar 时才处理 Token。
            if 'Acar' in headers:
                # 读取响应头中的 Token 字符串。
                token = headers.get('Acar', '')
                # 只打印 Token 前 20 个字符，避免完整泄露凭证。
                print(f"   获取到Token: {token[:20]}...")
                # 将 Token 保存到客户端，供后续接口使用。
                client.token = token

                # 输出需要 Token 的用户信息接口测试标题。
                print("\n5. 测试获取用户信息...")
                # 调用需要登录认证的用户信息接口。
                user_info = client.get_user_info()
                # 输出用户信息接口状态码。
                print(f"   状态码: {user_info.get('status_code')}")
                # 如果用户信息接口成功解密，则输出用户 ID。
                if 'data' in user_info:
                    # 从嵌套业务对象中读取用户 ID。
                    print(f"   用户信息: {user_info['data'].get('dide', {}).get('uclos', 'N/A')}")

        # 捕获真实请求过程中的未处理异常。
        except Exception as e:
            # 输出异常类型和错误信息。
            print(f"   请求异常: {type(e).__name__}: {e}")

    # 输出调试流程结束提示。
    print("\n✅ 客户端调试完成")


# 只有直接执行本文件时才启动调试入口。
if __name__ == "__main__":
    # 运行客户端调试函数。
    debug_client()
