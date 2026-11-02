# 导入时间工具，用于生成毫秒级请求时间戳。
import time
# 保留 UUID 工具，兼容项目中可能存在的旧调用。
import uuid
# 导入 requests，用于发送 HTTP 请求并维护会话。
import requests
# 导入类型标注，帮助 IDE 和静态检查理解数据结构。
from typing import Dict, Any, Optional
# 导入响应解密器，处理服务端返回的加密数据。
from .decryptor import ResponseDecryptor


# 定义 RapidTV API 客户端。
class RapidTVClient:
    """RapidTV API 客户端，封装请求、Token 和响应解密逻辑。"""

    # 初始化客户端所需的基础配置。
    def __init__(self, base_url: str, package_name: str, secret_key: str, device_id: str, distinct_id: str):
        # 去掉基础 URL 末尾的斜杠，避免拼接接口时出现双斜杠。
        self.base_url = base_url.rstrip('/')
        # 保存应用包名，用于生成 X-Pcombi 请求头。
        self.package_name = package_name
        # 保存应用密钥，用于初始化响应解密器。
        self.secret_key = secret_key
        # 保存设备标识，用于生成设备相关请求头。
        self.device_id = device_id
        # 保存用户或安装实例标识，用于生成用户相关请求头。
        self.distinct_id = distinct_id
        # 创建与当前客户端绑定的响应解密器。
        self.decryptor = ResponseDecryptor(secret_key)

        # 创建 requests 会话，以便复用连接并保留会话级配置。
        self.session = requests.Session()
        # 设置所有请求默认携带的客户端标识和响应类型。
        self.session.headers.update({
            # 设置客户端 User-Agent。
            'User-Agent': 'RapidTV-Health-Check/1.0.0',
            # 声明客户端优先接收 JSON 响应。
            'Accept': 'application/json',
        })

        # 初始化 Token，登录后会根据响应头更新。
        self.token: Optional[str] = None
        # 预留 Token 过期时间字段，当前由服务端响应头决定是否填充。
        self.token_expiry: Optional[int] = None

    # 生成请求唯一标识或请求时间戳。
    @staticmethod
    def _generate_request_id() -> str:  # 生成请求 ID。
        # 返回当前 Unix 时间的毫秒表示。
        return str(int(time.time() * 1000))

    # 生成所有接口共用的混淆请求头。
    def _get_common_headers(self, requires_token: bool = False) -> Dict[str, str]:
        # 获取当前毫秒时间戳，供多个时间相关请求头共用。
        request_timestamp = str(int(time.time() * 1000))
        # 创建公共请求头字典。
        headers = {
            # 设置应用包名。
            'X-Pcombi': self.package_name,
            # 设置客户端平台。
            'X-Dtas-Ttill': 'ANDROID',
            # 设置应用版本号。
            'X-Alib-Vasso': '1.3.0',
            # 设置设备标识。
            'X-Dtas-Iangle': self.device_id,
            # 设置用户或安装实例标识。
            'X-Dstaff-Iangle': self.distinct_id,
            # 设置请求时间或请求标识。
            'X-Rres-Iangle': request_timestamp,
            # 设置服务端要求的客户端规格字段。
            'X-Cspec-Vasso': 'X-Cspec-Vasso',
            # 设置服务端要求的时间字段。
            'X-Tove': request_timestamp,
            # 声明请求体格式为 JSON。
            'Content-Type': 'application/json',
        }

        # 只有需要 Token 且当前已经保存 Token 时才添加认证头。
        if requires_token and self.token:
            # 将登录得到的 Token 放入 Acar 请求头。
            headers['Acar'] = self.token

        # 返回生成好的公共请求头。
        return headers

    # 发送 HTTP 请求，并根据响应头自动解密响应体。
    def request(
            self,
            method: str,  # HTTP 方法，例如 GET 或 POST。
            endpoint: str,  # 接口路径，例如 /api/ulov/uplace/lshin。
            data: Optional[Dict] = None,  # 要序列化为 JSON 的请求数据。
            requires_token: bool = False,  # 是否要求请求携带 Token。
            auto_decrypt: bool = True  # 是否根据响应头自动解密。
    ) -> Dict[str, Any]:  # 返回包含状态、响应头和业务数据的字典。
        """发送请求并自动处理加密或明文响应。"""

        # 将基础 URL 和接口路径拼接成完整请求地址。
        url = f"{self.base_url}{endpoint}"
        # 根据接口是否需要 Token 生成请求头。
        headers = self._get_common_headers(requires_token)

        # 发送 HTTP 请求并等待服务端响应。
        response = self.session.request(
            # 传入调用方指定的 HTTP 方法。
            method=method,
            # 传入拼接后的完整 URL。
            url=url,
            # 让 requests 将字典序列化为 JSON 请求体。
            json=data,
            # 传入本次请求使用的请求头。
            headers=headers,
            # 设置 30 秒网络超时，避免请求永久阻塞。
            timeout=30
        )

        # 如果服务端返回新的 Acar，就更新客户端保存的 Token。
        if 'Acar' in response.headers:
            # 读取响应头中的新 Token。
            new_token = response.headers.get('Acar')
            # 仅在新 Token 非空且与旧 Token 不同的时候更新。
            if new_token and new_token != self.token:
                # 保存最新 Token，供后续需要认证的接口使用。
                self.token = new_token
                # 只打印 Token 前 20 个字符，避免完整泄露认证信息。
                print(f"Token 已刷新: {new_token[:20]}...")

        # 有效响应头且开启自动解密时，按加密响应处理。
        if auto_decrypt and 'X-Edevic-Kweb' in response.headers:
            # 读取未经处理的 Base64 加密响应体。
            encrypted_body = response.text
            # 读取服务端提供的解密因子。
            x_edevic_kweb = response.headers.get('X-Edevic-Kweb')

            # 尝试解密并解析业务 JSON。
            try:
                # 调用解密器处理当前响应。
                decrypted = self.decryptor.decrypt_response(encrypted_body, x_edevic_kweb)
                # 返回状态、响应头、解密数据和原始响应体。
                return {
                    # 保存 HTTP 状态码。
                    'status_code': response.status_code,
                    # 将 requests 的响应头转换成普通字典。
                    'headers': dict(response.headers),
                    # 保存解密后的业务 JSON。
                    'data': decrypted,
                    # 保存原始 Base64 响应，便于后续调试。
                    'raw_response': encrypted_body
                }
            # 解密或 JSON 解析失败时，返回错误和原始响应体。
            except Exception as e:
                # 保留响应头，便于调用方查看 X-Edevic-Kweb 等调试信息。
                return {
                    # 保存 HTTP 状态码。
                    'status_code': response.status_code,
                    # 返回完整响应头字典。
                    'headers': dict(response.headers),
                    # 返回带上下文的解密错误。
                    'error': f"解密失败: {e}",
                    # 保留导致失败的原始响应体。
                    'raw_response': encrypted_body
                }
        else:
            # 没有加密标识或主动关闭解密时，按明文响应处理。
            try:
                # 返回状态、响应头、明文 JSON 和原始文本。
                return {
                    # 保存 HTTP 状态码。
                    'status_code': response.status_code,
                    # 将响应头转换成普通字典。
                    'headers': dict(response.headers),
                    # 有响应体时解析 JSON，没有响应体时返回空字典。
                    'data': response.json() if response.text else {},
                    # 保存原始明文响应。
                    'raw_response': response.text
                }
            # 明文响应不是合法 JSON 时，仍返回原始文本供调用方处理。
            except Exception:
                # 返回状态、响应头和未经解析的响应文本。
                return {
                    # 保存 HTTP 状态码。
                    'status_code': response.status_code,
                    # 将响应头转换成普通字典。
                    'headers': dict(response.headers),
                    # 保存原始响应文本。
                    'raw_response': response.text
                }

    # 调用登录接口并保存服务端返回的 Token。
    def login(
            self,
            country: str = "US",  # 登录国家或地区代码。
            source: str = "fb",  # 用户来源渠道。
            user_strategy: int = 1,  # 用户版本策略。
            ofligh: int = 1785236624846,  # 客户端初始化时间戳或业务字段。
    ) -> Dict:  # 返回登录接口的标准响应字典。
        """调用用户登录接口。"""

        # 设置登录接口路径。
        endpoint = "/api/ulov/uplace/lshin"

        # 构造登录接口所需的业务请求体。
        data = {
            # 传入当前客户端的用户或安装实例标识。
            "dper": self.distinct_id,
            # 传入登录国家或地区。
            "cconce": country,
            # 传入用户来源渠道。
            "sleave": source,
            # 传入用户版本策略。
            "umai": user_strategy,
            # 传入客户端初始化时间戳字段。
            "ofligh": ofligh,
        }

        # 预留可选的广告标识字段，目前不主动发送。
        # if gaid:
        #     data["ghor"] = gaid

        # 发送登录请求，登录接口本身不要求已有 Token。
        response = self.request("POST", endpoint, data, requires_token=False)

        # 只有 HTTP 状态码为 200 时才尝试保存登录 Token。
        if response.get('status_code') == 200:
            # 从标准响应结构中读取响应头。
            headers = response.get('headers', {})
            # 如果响应包含 Acar，则保存该 Token。
            if 'Acar' in headers:
                # 更新客户端当前 Token。
                self.token = headers.get('Acar')
                # Token 过期时间在 Tdri 头中，当前保留待后续处理。

        # 返回登录接口的完整响应结果。
        return response

    # 获取当前登录用户的信息。
    def get_user_info(self, need_stats: bool = False) -> Dict:
        """调用需要登录认证的用户信息接口。"""

        # 设置用户信息接口路径。
        endpoint = "/api/ulov/uplace/gcal"
        # 构造是否返回统计信息的请求体。
        data = {"nrea": need_stats}
        # 发送需要 Token 的用户信息请求。
        return self.request("POST", endpoint, data, requires_token=True)
