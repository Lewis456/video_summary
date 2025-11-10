from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base
import enum  # 导入枚举模块

class MemberType(str, enum.Enum):  # 会员类型枚举
    """会员类型枚举"""
    NORMAL = "normal"  # 普通用户
    VIP = "vip"  # VIP用户

class User(Base):
    """用户模型"""
    __tablename__ = "users"  # 表名
    
    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    email = Column(String(100), unique=True, nullable=False, index=True, comment="邮箱")
    password = Column(String(255), nullable=False, comment="加密后的密码")
    member_type = Column(String(10), default="normal", nullable=False, comment="会员类型")  # 直接用String类型，避免枚举转换问题
    created_at = Column(DateTime(timezone=False), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<User {self.username}>"

