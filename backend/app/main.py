from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, summary, user  # 导入所有API路由
from app.core.database import engine, Base

# 导入所有模型以确保表被创建
from app.models.user import User  # 导入用户模型
from app.models.verification_code import VerificationCode  # 导入验证码模型
from app.models.profile import UserProfile  # 导入用户资料模型

app = FastAPI(title="Smart Video Summary System")

# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建数据库表
@app.on_event("startup")
async def startup_event():
    """应用启动时创建数据库表"""
    Base.metadata.create_all(bind=engine)

# 注册子路由
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(summary.router, prefix="/api/summary", tags=["Summary"])
app.include_router(user.router, prefix="/api/user", tags=["User"])

@app.get("/")
def read_root():
    return {"msg": "Smart Video Summary API is running"}
