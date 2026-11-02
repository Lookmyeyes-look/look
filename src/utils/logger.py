# src/utils/logger.py
import sys
from loguru import logger
from pathlib import Path
from datetime import datetime


def setup_logger(
        log_file: str = "logs/health_check.log",
        rotation: str = "1 day",  # 每天轮转
        retention: str = "30 days",  # 保留30天
        level: str = "INFO"
) -> logger:
    """
    配置日志记录器

    Args:
        log_file: 日志文件路径
        rotation: 日志轮转策略
        retention: 日志保留策略
        level: 日志级别

    Returns:
        配置好的 logger 实例
    """
    # 确保日志目录存在
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # 移除默认的处理器
    logger.remove()

    # 控制台输出（带颜色）
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        level=level,
        colorize=True
    )

    # 文件输出（JSON格式，便于分析）
    logger.add(
        str(log_path),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
        level=level,
        rotation=rotation,
        retention=retention,
        compression="zip",  # 自动压缩旧日志
        enqueue=True,  # 线程安全
        backtrace=True,  # 显示错误堆栈
        diagnose=True
    )

    # 错误日志单独记录
    error_log_path = log_path.parent / f"error_{log_path.name}"
    logger.add(
        str(error_log_path),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
        level="ERROR",
        rotation=rotation,
        retention="90 days",  # 错误日志保留更久
        compression="zip"
    )

    return logger


# 创建默认的日志记录器
def get_logger(name: str = "rapidtv_health_check") -> logger:
    """获取指定名称的logger实例"""
    return logger.bind(name=name)


# 上下文管理器，用于记录代码块执行时间
class TimerContext:
    """计时器上下文管理器"""

    def __init__(self, name: str, logger_instance=None):
        self.name = name
        self.logger = logger_instance or get_logger()
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"开始执行: {self.name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = (datetime.now() - self.start_time).total_seconds()
        if exc_type is None:
            self.logger.info(f"完成执行: {self.name} | 耗时: {elapsed:.2f}秒")
        else:
            self.logger.error(f"执行失败: {self.name} | 错误: {exc_val} | 耗时: {elapsed:.2f}秒")
        return False


# 使用示例
if __name__ == "__main__":
    # 测试日志功能
    log = setup_logger()
    log.info("日志系统初始化成功")
    log.warning("这是一个警告")
    log.error("这是一个错误")

    # 使用计时器
    with TimerContext("测试任务"):
        import time

        time.sleep(0.5)
        log.info("任务执行中...")