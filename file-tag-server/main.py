from fastapi import FastAPI
from file_tag_app.models import Base, engine
from file_tag.urls import router
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from utilis import log

# 加载app应用
app = FastAPI()

# 加载数据库
Base.metadata.create_all(bind=engine)

# 加载URL
app.include_router(router)

origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许的源
    allow_credentials=True,  # 允许发送cookie
    allow_methods=["*"],  # 允许的HTTP方法
    allow_headers=["*"],  # 允许的HTTP头
)

if __name__ == '__main__':

    # 加载日志
    mylog = log.Log('./logs')

    try:
        mylog.info("now start server")
        uvicorn.run("main:app", host="127.0.0.1", port=25566, log_level="info")
    except Exception as e:
        mylog.error(f'server running exception: {e.args}')
