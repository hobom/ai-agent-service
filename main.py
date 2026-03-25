from fastapi import FastAPI
import uvicorn
from utils.logger import logger, LoggingRoute

app = FastAPI()
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
    uvicorn.run(app, host="0.0.0.0", port=7490)
