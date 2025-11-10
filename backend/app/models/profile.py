from sqlalchemy import Column, Integer, String, Date, ForeignKey  # 导入列与外键类型
from sqlalchemy.orm import relationship  # 导入关系
from app.core.database import Base  # 基类

class UserProfile(Base):  # 定义用户资料模型
    __tablename__ = "user_profiles"  # 表名

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")  # 主键
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, comment="用户ID")  # 一对一外键
    avatar_url = Column(String(255), nullable=True, comment="头像URL")  # 头像链接
    gender = Column(String(10), nullable=True, comment="性别")  # 性别：male/female/other
    birth_date = Column(Date, nullable=True, comment="出生日期")  # 出生日期

    user = relationship("User", backref="profile")  # 关联到User
