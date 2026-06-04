from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # 讯飞星火大模型配置
    SPARK_APP_ID: str = "ee10e7e2"
    SPARK_API_KEY: str = "dvYBNuTCyCqDOVrYPCUA:lUVaJYlVHSMeMbimBOTE"
    SPARK_API_SECRET: str = "OTE0OThmNjlkMDk0NGNhOGYwYmNhMDYx"
    SPARK_API_URL: str = "wss://spark-api.xf-yun.com/v3.5/chat"

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./data/app.db"

    # 向量数据库配置
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma"

    # JWT配置
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # 项目路径
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
