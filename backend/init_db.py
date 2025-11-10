"""
数据库初始化脚本
用于创建数据库和表结构
"""
from app.core.database import engine, Base
from app.models.user import User  # 导入用户模型
from app.models.verification_code import VerificationCode  # 导入验证码模型
from app.models.profile import UserProfile  # 导入用户资料模型

if __name__ == "__main__":
    print("开始创建数据库表...")
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")

