import os
from typing import List
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# 加载 .env 文件
load_dotenv()


class Settings(BaseSettings):
    """应用配置类"""

    # 应用配置
    APP_NAME: str = Field(default="ai-agent-service", description="应用名称")
    APP_ENV: str = Field(default="development", description="应用环境")
    DEBUG: bool = Field(default=False, description="调试模式")
    HOST: str = Field(default="0.0.0.0", description="主机地址")
    PORT: int = Field(default=7490, description="端口号")

    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    LOG_FILE: str = Field(default="logs/app.log", description="日志文件路径")
    LOG_MAX_SIZE: int = Field(default=10 * 1024 * 1024, description="日志文件最大大小 (字节)")
    LOG_BACKUP_COUNT: int = Field(default=5, description="日志备份数量")

    # API 配置
    API_PREFIX: str = Field(default="/api", description="API 前缀")
    CORS_ORIGINS: List[str] = Field(default=["*"], description="CORS 源列表")

    # 安全配置
    SECRET_KEY: str = Field(default="change-me-in-production", description="密钥")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="访问令牌过期时间 (分钟)")

    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置对象"""
    return settings
