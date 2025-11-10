from fastapi import APIRouter, HTTPException, Depends  # 导入FastAPI路由与异常、依赖注入
from pydantic import BaseModel  # 导入Pydantic模型
from sqlalchemy.orm import Session  # 导入SQLAlchemy会话
from jose import jwt  # 导入JWT库
from datetime import datetime, timedelta  # 导入时间工具
import secrets  # 导入安全随机库
import hashlib  # 导入哈希库，用于SHA1加密
import re  # 导入正则表达式库，用于密码验证
from app.core.database import get_db  # 导入数据库会话依赖
from app.core.config import SECRET_KEY, ALGORITHM  # 导入JWT配置
from app.models.user import User  # 导入用户模型

# 新增导入：验证码模型与邮件服务
from app.models.verification_code import VerificationCode  # 导入验证码模型
from app.services.email_service import send_email  # 导入邮件发送服务

router = APIRouter()  # 创建路由对象

# 请求模型
class LoginRequest(BaseModel):  # 登录请求模型
    email: str  # 邮箱
    password: str  # 密码

class RegisterRequest(BaseModel):  # 注册请求模型
    username: str  # 用户名
    email: str  # 邮箱
    password: str  # 密码
    code: str  # 邮箱验证码

class SendCodeRequest(BaseModel):  # 发送验证码请求模型
    email: str  # 邮箱

class ResetPasswordRequest(BaseModel):  # 重置密码请求模型
    email: str  # 邮箱
    code: str  # 验证码
    new_password: str  # 新密码

# 密码验证函数
def validate_password(password: str) -> tuple[bool, str]:
    """
    验证密码格式
    要求：不少于6位，必须包含字母和数字（大小写不限）
    返回：(是否有效, 错误信息)
    """
    if not password or len(password) < 6:  # 检查密码长度是否少于6位
        return False, "密码长度不能少于6位"  # 返回错误信息
    has_letter = bool(re.search(r'[a-zA-Z]', password))  # 检查是否包含字母（大小写不限）
    has_number = bool(re.search(r'[0-9]', password))  # 检查是否包含数字
    if not has_letter:  # 如果没有字母
        return False, "密码必须包含至少一个字母"  # 返回错误信息
    if not has_number:  # 如果没有数字
        return False, "密码必须包含至少一个数字"  # 返回错误信息
    return True, ""  # 验证通过

# 密码加密函数
def hash_password_sha1(password: str) -> str:
    """
    密码加密函数：使用 password + "summary" 然后进行 SHA1 加密
    """
    if not isinstance(password, str):
        password = str(password)
    # 密码 + "summary" 作为盐值
    salted_password = password + "summary"  # 拼接盐值
    # 使用SHA1加密
    sha1_hash = hashlib.sha1(salted_password.encode('utf-8')).hexdigest()  # SHA1加密并转为十六进制字符串
    return sha1_hash  # 返回加密后的哈希值


def verify_password_sha1(plain_password: str, hashed_password: str) -> bool:
    """
    密码验证函数：将明文密码加密后与存储的哈希值比较
    """
    try:
        if not isinstance(plain_password, str):
            plain_password = str(plain_password)
        # 使用相同的加密方式对明文密码加密
        salted_password = plain_password + "summary"  # 拼接相同的盐值
        sha1_hash = hashlib.sha1(salted_password.encode('utf-8')).hexdigest()  # SHA1加密
        # 比较加密后的哈希值
        return sha1_hash == hashed_password  # 返回比较结果
    except Exception as e:
        print(f"[verify_password] 密码验证异常: {e}")
        return False


def create_access_token(data: dict, expires_delta: timedelta = None):  # 创建JWT令牌
    to_encode = data.copy()  # 复制数据
    if expires_delta:  # 如果传入过期时间
        expire = datetime.utcnow() + expires_delta  # 使用自定义过期
    else:  # 否则使用默认15分钟
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})  # 更新过期字段
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # 生成JWT
    return encoded_jwt  # 返回令牌

@router.post("/send-code")
def send_register_code(request: SendCodeRequest, db: Session = Depends(get_db)):  # 发送注册验证码接口
    """向邮箱发送注册/重置密码验证码，验证码有效期5分钟"""
    email = request.email.strip()  # 去除首尾空格
    if not email:  # 校验邮箱非空
        raise HTTPException(status_code=400, detail="邮箱不能为空")  # 抛出异常

    # 生成6位数字验证码
    code = "".join(secrets.choice("0123456789") for _ in range(6))  # 6位随机数字

    # 计算过期时间（5分钟）
    expires_at = datetime.utcnow() + timedelta(minutes=5)  # 过期时间点

    # 保存到数据库
    record = VerificationCode(email=email, code=code, expires_at=expires_at, used=False)  # 创建记录
    db.add(record)  # 加入会话
    db.commit()  # 提交事务

    # 发送邮件内容（HTML版）
    subject = "【智能视频总结】验证码"  # 邮件主题
    html_content = f"""
    <div style='font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#333;'>
      <p>您好，您正在进行账户安全操作（注册/重置密码）。</p>
      <p>本次验证码为：<strong style='font-size:20px'>{code}</strong></p>
      <p>验证码有效期 <strong>5分钟</strong>，请勿泄露给他人。</p>
      <p>如果非您本人操作，请忽略此邮件。</p>
      <hr/>
      <p style='color:#888;'>此为系统邮件，请勿直接回复。</p>
    </div>
    """

    try:
        send_email(to_email=email, subject=subject, html_content=html_content)  # 发送邮件
    except Exception as e:
        # 依然返回成功，避免用户已收邮件但接口报错
        print(f"[send-code] 邮件发送异常，但验证码已入库，email={email}, err={e}")
        return {"msg": "验证码已发送，请检查邮箱"}

    return {"msg": "验证码已发送，请检查邮箱"}

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):  # 用户登录接口
    # 查找用户
    user = db.query(User).filter(User.email == request.email).first()  # 通过邮箱查询用户
    if not user:  # 若用户不存在
        raise HTTPException(status_code=401, detail="邮箱或密码错误")  # 抛出未授权
    
    # 验证密码
    if not verify_password_sha1(request.password, user.password):  # 校验密码哈希
        raise HTTPException(status_code=401, detail="邮箱或密码错误")  # 抛出未授权
    
    # 创建JWT令牌
    access_token = create_access_token(  # 生成令牌
        data={"sub": user.email, "user_id": user.id},  # 载荷包含邮箱与用户ID
        expires_delta=timedelta(days=7)  # 7天有效期
    )
    
    return {  # 返回登录成功信息
        "msg": "登录成功",
        "token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }

@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):  # 用户注册接口
    """校验邮箱验证码（5分钟有效且未使用），成功后创建用户"""
    # 验证密码格式
    is_valid, error_msg = validate_password(request.password)  # 验证密码格式
    if not is_valid:  # 如果密码格式不正确
        raise HTTPException(status_code=400, detail=error_msg)  # 返回错误信息
    
    # 检查邮箱是否已存在
    existing_user = db.query(User).filter(User.email == request.email).first()  # 查询邮箱
    if existing_user:  # 若已存在
        raise HTTPException(status_code=400, detail="该邮箱已被注册")  # 返回错误
    
    # 检查用户名是否已存在
    existing_username = db.query(User).filter(User.username == request.username).first()  # 查询用户名
    if existing_username:  # 若已存在
        raise HTTPException(status_code=400, detail="该用户名已被使用")  # 返回错误

    # 校验验证码（未使用且未过期）
    code_record = (
        db.query(VerificationCode)
        .filter(VerificationCode.email == request.email)
        .filter(VerificationCode.code == request.code)
        .filter(VerificationCode.used == False)
        .order_by(VerificationCode.id.desc())
        .first()
    )  # 获取最新一条匹配记录

    if not code_record:  # 未找到记录
        raise HTTPException(status_code=400, detail="验证码错误")  # 返回错误

    if datetime.utcnow() > code_record.expires_at:  # 判断是否过期
        raise HTTPException(status_code=400, detail="验证码已过期")  # 返回错误

    # 标记验证码已使用
    code_record.used = True  # 设置为已使用
    db.add(code_record)  # 加入会话

    # 创建新用户
    hashed_password = hash_password_sha1(request.password)  # 生成密码哈希
    new_user = User(  # 构造用户对象
        username=request.username,
        email=request.email,
        password=hashed_password
    )
    
    db.add(new_user)  # 加入会话
    db.commit()  # 提交事务（同时保存验证码使用状态与新用户）
    db.refresh(new_user)  # 刷新新用户对象
    
    return {  # 返回注册成功信息
        "msg": f"注册成功，欢迎 {request.username}",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email
        }
    }

@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):  # 重置密码接口
    """根据邮箱+验证码重置密码（验证码5分钟有效且未使用）"""
    # 验证密码格式
    is_valid, error_msg = validate_password(request.new_password)  # 验证新密码格式
    if not is_valid:  # 如果密码格式不正确
        raise HTTPException(status_code=400, detail=error_msg)  # 返回错误信息
    
    # 查找用户
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 查找验证码
    code_record = (
        db.query(VerificationCode)
        .filter(VerificationCode.email == request.email)
        .filter(VerificationCode.code == request.code)
        .filter(VerificationCode.used == False)
        .order_by(VerificationCode.id.desc())
        .first()
    )
    if not code_record:
        raise HTTPException(status_code=400, detail="验证码错误")
    if datetime.utcnow() > code_record.expires_at:
        raise HTTPException(status_code=400, detail="验证码已过期")

    # 更新用户密码
    user.password = hash_password_sha1(request.new_password)
    # 标记验证码使用
    code_record.used = True
    db.add(user)
    db.add(code_record)
    db.commit()

    return {"msg": "密码已重置，请使用新密码登录"}
