#!/usr/bin/env python3
"""
定时健康检查调度器
每小时执行一次登录接口检查
"""
import sys
import time
import schedule
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_config
from src.core.client import RapidTVClient
from src.services.health_check import LoginHealthChecker
from src.utils.logger import setup_logger


def run_health_check():
    """执行单次健康检查"""
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

        # 执行检查
        logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始健康检查...")
        result = checker.check_login_health(
            country=config['country'],
            source=config['source'],
            user_strategy=config['user_strategy']
        )

        # 记录结果
        if result['success']:
            logger.info(f"✓ 检查成功 | 响应时间: {result['response_time_ms']}ms | "
                        f"业务码: {result.get('error_code', 'N/A')}")
        else:
            logger.error(f"✗ 检查失败 | 状态码: {result.get('status_code')} | "
                         f"错误: {result.get('error_message')}")

        # 检查是否需要告警
        max_response_time = config['monitor'].get('max_response_time_ms', 5000)
        if checker.should_alert(max_response_time=max_response_time):
            logger.warning("⚠️ 检测到服务异常，建议检查服务状态")

        # 打印摘要
        summary = checker.get_health_summary(5)
        logger.info(f"📊 最近5次检查摘要: 成功率 {summary['success_rate']}%, "
                    f"平均响应 {summary['avg_response_time_ms']}ms")

    except Exception as e:
        logger.error(f"健康检查执行失败: {e}")


def main():
    """主调度函数"""
    logger = setup_logger()
    config = load_config()
    interval_hours = config['monitor'].get('check_interval_hours', 1)

    logger.info("=" * 50)
    logger.info("RapidTV 登录接口健康检查调度器启动")
    logger.info(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"检查频率: 每 {interval_hours} 小时一次")
    logger.info("=" * 50)

    # 立即执行一次
    run_health_check()

    # 设置定时任务
    schedule.every(interval_hours).hours.do(run_health_check)

    # 也可以设置为每分钟（用于测试）
    # schedule.every(1).minutes.do(run_health_check)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)  # 降低CPU占用
    except KeyboardInterrupt:
        logger.info("调度器被用户中断")
    except Exception as e:
        logger.error(f"调度器异常退出: {e}")


if __name__ == "__main__":
    main()
