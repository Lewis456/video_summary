from sqlalchemy import Column, Integer, String, DateTime, Boolean  # 导入列类型
from sqlalchemy.sql import func  # 导入SQL函数工具
from app.core.database import Base  # 导入基础模型类

class VerificationCode(Base):  # 定义验证码模型类
    __tablename__ = "verification_codes"  # 指定表名

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")  # 自增主键
    email = Column(String(100), nullable=False, index=True, comment="邮箱")  # 绑定的邮箱
    code = Column(String(10), nullable=False, comment="验证码")  # 验证码内容
    expires_at = Column(DateTime(timezone=False), nullable=False, comment="过期时间")  # 过期时间
    used = Column(Boolean, default=False, nullable=False, comment="是否已使用")  # 是否已被使用
    created_at = Column(DateTime(timezone=False), server_default=func.now(), comment="创建时间")  # 创建时间
