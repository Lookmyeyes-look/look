#!/usr/bin/env python3
"""
手动执行健康检查
"""
import sys
import json
from pathlib import Path

# 添加 src 到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_config
from src.core.client import RapidTVClient
from src.services.health_check import LoginHealthChecker
from src.utils.logger import setup_logger


def main():
    logger = setup_logger()
    config = load_config()

    try:
        # 初始化客户端
        client = RapidTVClient(
            base_url=config['base_url'],
            package_name=config['package_name'],
            secret_key=config['secret_key'],
            device_id=config['device_id'],
            distinct_id=config['distinct_id']
        )

        checker = LoginHealthChecker(client)

        logger.info("开始执行登录接口健康检查...")

        # 执行检查
        result = checker.check_login_health(
            country=config['country'],
            source=config['source'],
            user_strategy=config['user_strategy']
        )

        # 打印结果
        print("\n" + "=" * 50)
        print("登录接口健康检查结果")
        print("=" * 50)
        print(f"时间: {result['timestamp']}")
        print(f"成功: {'✓' if result['success'] else '✗'}")
        print(f"响应时间: {result['response_time_ms']}ms")
        print(f"HTTP状态码: {result.get('status_code')}")

        if 'error_code' in result:
            print(f"业务错误码: {result['error_code']}")
        if 'error_message' in result:
            print(f"错误信息: {result['error_message']}")

        # 打印响应数据（如果成功）
        if result['success'] and result.get('data'):
            data = result['data']
            if data.get('dide'):
                user_id = data['dide'].get('uclos', 'N/A')
                print(f"用户ID: {user_id}")

        # 保存结果到 reports 目录
        reports_dir = Path(__file__).parent.parent / "reports"
        reports_dir.mkdir(exist_ok=True)
        result_file = reports_dir / "health_check_result.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"\n结果已保存到: {result_file}")

        return 0 if result['success'] else 1

    except Exception as e:
        logger.error(f"执行失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
