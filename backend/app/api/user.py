from fastapi import APIRouter, Depends, HTTPException, Header  # 导入FastAPI组件
from sqlalchemy.orm import Session  # 导入会话
from jose import jwt, JWTError  # 导入JWT
from datetime import date  # 导入日期类型
from typing import Optional  # 导入可选类型
from app.core.database import get_db  # 导入DB依赖
from app.core.config import SECRET_KEY  # 导入密钥
from app.models.user import User  # 导入用户模型
from app.models.profile import UserProfile  # 导入资料模型

# 新增导入：文件上传与OSS服务
from fastapi import UploadFile, File  # 导入上传文件类型
from app.services.oss_service import upload_bytes_and_get_url  # 导入OSS上传工具

router = APIRouter()  # 路由

# JWT令牌验证函数
def get_current_user(token: str = Header(...), db: Session = Depends(get_db)):
    """从JWT令牌获取当前用户"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="无法验证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])  # 解码JWT
        email: str = payload.get("sub")  # 获取邮箱
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()  # 查询用户
    if user is None:
        raise credentials_exception
    return user  # 返回用户

@router.get("/profile")
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前用户信息+资料"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()  # 查资料
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,  # 邮箱不可修改
        "member_type": current_user.member_type,  # 会员类型（已经是字符串）
        "is_vip": current_user.member_type == "vip",  # 是否为VIP
        "avatar_url": profile.avatar_url if profile else None,
        "gender": profile.gender if profile else None,
        "birth_date": profile.birth_date.isoformat() if (profile and profile.birth_date) else None,
    }

from pydantic import BaseModel  # 导入Pydantic
class UpdateProfileRequest(BaseModel):  # 定义更新请求
    username: str  # 用户名
    avatar_url: Optional[str] = None  # 头像（由上传接口生成URL）
    gender: Optional[str] = None  # 性别
    birth_date: Optional[str] = None  # 出生日期（YYYY-MM-DD）

@router.put("/profile")
def update_profile(body: UpdateProfileRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """更新当前用户资料（邮箱禁止修改）"""
    # 更新用户名
    if body.username:
        current_user.username = body.username  # 修改用户名
    # 解析出生日期
    birth = None
    if body.birth_date:
        try:
            year, month, day = map(int, body.birth_date.split('-'))
            birth = date(year, month, day)
        except Exception:
            raise HTTPException(status_code=400, detail="出生日期格式应为YYYY-MM-DD")
    # 获取或创建资料
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    # 更新资料字段
    if body.avatar_url is not None:
        profile.avatar_url = body.avatar_url  # 设置头像URL
    profile.gender = body.gender  # 设置性别
    profile.birth_date = birth  # 设置生日
    # 提交
    db.add(current_user)
    db.add(profile)
    db.commit()
    db.refresh(current_user)
    db.refresh(profile)
    return {"msg": "资料已更新"}

@router.post("/profile/avatar")
def upload_avatar(  # 上传头像接口
    file: UploadFile = File(...),  # 接收前端上传的文件
    current_user: User = Depends(get_current_user),  # 当前用户
    db: Session = Depends(get_db),  # 数据库会话
):
    """接收本地上传头像，上传到OSS，保存URL并返回"""
    try:
        file_bytes = file.file.read()  # 读取文件字节
        content_type = file.content_type or "application/octet-stream"  # 内容类型
        # 头像统一保存到 uploads/user 目录
        url = upload_bytes_and_get_url(file_bytes, file.filename or "avatar.png", content_type, folder='uploads/user')  # 上传并返回URL
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传头像失败：{str(e)}")  # 上传异常
    # 写入用户资料
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()  # 查询资料
    if not profile:
        profile = UserProfile(user_id=current_user.id)  # 创建资料
        db.add(profile)
    profile.avatar_url = url  # 设置头像URL
    db.add(profile)
    db.commit()  # 提交
    db.refresh(profile)  # 刷新
    return {"avatar_url": url}  # 返回URL

@router.get("/all")
def get_all_users(db: Session = Depends(get_db)):
    """获取所有用户（仅用于测试）"""
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }
        for user in users
    ]
