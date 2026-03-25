import logging
import time
from logging.handlers import RotatingFileHandler
from typing import Callable, Optional

from fastapi import Request, Response
from fastapi.routing import APIRoute

from config import settings

# 日志配置常量
LOG_FILE = settings.LOG_FILE
MAX_LOG_SIZE = settings.LOG_MAX_SIZE
BACKUP_COUNT = settings.LOG_BACKUP_COUNT
LOG_LEVEL = getattr(logging, settings.LOG_LEVEL, logging.INFO)
LOG_FORMAT = (
    "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s"
)  # 日志格式


def setup_logger(name: str = "fastapi_app") -> logging.Logger:
    """
    初始化并配置全局日志器
    :param name: 日志器名称
    :return: 配置好的logger实例
    """
    # 创建日志器
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    logger.propagate = False  # 避免重复输出

    # 避免重复添加处理器
    if logger.handlers:
        return logger

    # 1. 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(console_formatter)

    # 2. 文件轮转处理器
    file_handler = RotatingFileHandler(
        filename=LOG_FILE,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT,
        encoding="utf-8"
    )
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(console_formatter)

    # 添加处理器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# 初始化全局日志器
logger = setup_logger()


class LoggingRoute(APIRoute):
    """
    自定义路由类，用于记录所有请求/响应日志
    """

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            # 1. 记录请求信息
            start_time = time.time()
            client_ip = request.client.host if request.client else "unknown"
            method = request.method
            url = str(request.url)
            headers = dict(request.headers)
            # 过滤敏感头信息
            sensitive_headers = ["authorization", "cookie", "x-token"]
            filtered_headers = {
                k: "***" if k.lower() in sensitive_headers else v
                for k, v in headers.items()
            }

            logger.info(
                f"REQUEST | IP: {client_ip} | METHOD: {method} | URL: {url} | HEADERS: {filtered_headers}"
            )

            try:
                # 执行原路由处理逻辑
                response: Response = await original_route_handler(request)

                # 2. 记录响应信息
                process_time = f"{(time.time() - start_time) * 1000:.2f}ms"
                logger.info(
                    f"RESPONSE | STATUS: {response.status_code} | PROCESS_TIME: {process_time} | URL: {url}"
                )

                return response

            except Exception as e:
                # 3. 记录异常信息
                process_time = f"{(time.time() - start_time) * 1000:.2f}ms"
                logger.error(
                    f"EXCEPTION | URL: {url} | PROCESS_TIME: {process_time} | ERROR: {str(e)}",
                    exc_info=True  # 记录完整异常栈
                )
                raise  # 重新抛出异常，不影响原有异常处理逻辑

        return custom_route_handler


def log_request_middleware(request: Request, call_next: Callable) -> Response:
    """
    可选：使用中间件记录日志（与LoggingRoute二选一）
    适合不需要精细控制路由级别的场景
    """
    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"
    method = request.method
    url = str(request.url)

    logger.info(f"REQUEST | IP: {client_ip} | METHOD: {method} | URL: {url}")

    response = call_next(request)

    process_time = f"{(time.time() - start_time) * 1000:.2f}ms"
    logger.info(
        f"RESPONSE | STATUS: {response.status_code} | PROCESS_TIME: {process_time} | URL: {url}"
    )

    return response