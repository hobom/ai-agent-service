from fastapi import FastAPI
import uvicorn
from logger import LoggingRoute
from config import settings

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)
# 全局应用自定义日志路由
app.router.route_class = LoggingRoute


@app.get("/health")
async def health_check():
    """健康检查接口"""
    # logger.info("健康检查接口被调用")
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level="info" if settings.DEBUG else "warning"
    )
