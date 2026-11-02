import time
from typing import Dict, Any, Optional
from src.core.client import RapidTVClient


class LoginHealthChecker:
    """登录接口健康检查器"""

    def __init__(self, client: RapidTVClient):
        self.client = client
        self.check_history = []

    def check_login_health(self,
                           country: str = "US",
                           source: str = "fb",
                           user_strategy: int = 1) -> Dict[str, Any]:
        """
        执行登录健康检查

        Returns:
            {
                "timestamp": 时间戳,
                "success": bool,
                "response_time_ms": 响应时间(ms),
                "status_code": HTTP状态码,
                "error_code": 业务错误码,
                "error_message": 错误信息,
                "data": 响应数据
            }
        """
        start_time = time.time()

        try:
            response = self.client.login(country, source, user_strategy)
            elapsed_ms = (time.time() - start_time) * 1000

            result = {
                "timestamp": int(time.time()),
                "success": response.get('status_code') == 200,
                "response_time_ms": round(elapsed_ms, 2),
                "status_code": response.get('status_code'),
                "data": response.get('data', {})
            }

            # 检查业务错误码
            data = response.get('data', {})
            if data and 'sdevi' in data:
                result['error_code'] = data.get('sdevi')
                result['error_message'] = data.get('mbird', '')

                # sdevi=1 表示成功
                if data.get('sdevi') != 1:
                    result['success'] = False

            # 记录到历史
            self.check_history.append(result)
            if len(self.check_history) > 100:  # 保留最近100条
                self.check_history = self.check_history[-100:]

            return result

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            return {
                "timestamp": int(time.time()),
                "success": False,
                "response_time_ms": round(elapsed_ms, 2),
                "status_code": None,
                "error_code": "REQUEST_ERROR",
                "error_message": str(e),
                "data": {}
            }

    def get_health_summary(self, last_n: int = 10) -> Dict[str, Any]:
        """获取健康检查摘要"""
        if not self.check_history:
            return {"total_checks": 0, "success_rate": 0}

        recent = self.check_history[-last_n:]
        total = len(recent)
        successful = sum(1 for check in recent if check.get('success'))

        avg_response_time = sum(
            check.get('response_time_ms', 0) for check in recent
        ) / total if total > 0 else 0

        return {
            "total_checks": total,
            "successful_checks": successful,
            "success_rate": round(successful / total * 100, 2) if total > 0 else 0,
            "avg_response_time_ms": round(avg_response_time, 2),
            "last_check": self.check_history[-1] if self.check_history else None
        }

    def should_alert(self,
                     max_response_time: float = 5000,
                     success_threshold: float = 90.0) -> bool:
        """判断是否需要告警"""
        summary = self.get_health_summary(5)  # 最近5次

        if summary['total_checks'] == 0:
            return False

        # 响应时间超时
        if summary.get('avg_response_time_ms', 0) > max_response_time:
            return True

        # 成功率过低
        if summary.get('success_rate', 0) < success_threshold:
            return True

        return False
