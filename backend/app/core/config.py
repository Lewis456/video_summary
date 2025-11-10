import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库配置
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:password@localhost:3306/video_sum_db"
)

# JWT配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"  # JWT加密算法

# CORS配置
ALLOWED_ORIGINS = ["*"]

# SMTP 邮件配置
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.example.com")  # SMTP服务器主机名
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))  # SMTP端口（SSL常用465，STARTTLS常用587）
SMTP_USER = os.getenv("SMTP_USER", "no-reply@example.com")  # 发件邮箱账号
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your-smtp-password")  # 发件邮箱密码或授权码
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)  # 发件人显示邮箱
SMTP_USE_SSL = os.getenv("SMTP_USE_SSL", "true").lower() == "true"  # 是否使用SSL直连
SMTP_STARTTLS = os.getenv("SMTP_STARTTLS", "false").lower() == "true"  # 是否使用STARTTLS

# 阿里云语音转写配置（兼容你的变量名）
ALIYUN_AK_ID = os.getenv("OSS_ACCESS_KEY_ID") or os.getenv("ALIYUN_AK_ID", "")  # AccessKey ID
ALIYUN_AK_SECRET = os.getenv("OSS_ACCESS_KEY_SECRET") or os.getenv("ALIYUN_AK_SECRET", "")  # AccessKey Secret
ALIYUN_APP_KEY = os.getenv("OSS_APP_KEY") or os.getenv("ALIYUN_APP_KEY", "")  # 智能语音识别AppKey

# 通义千问API Key
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")

# OSS 存储配置（用于本地文件先上传再转写）
OSS_ENDPOINT = os.getenv("OSS_ENDPOINT", "")  # OSS地域Endpoint，如：https://oss-cn-shanghai.aliyuncs.com
OSS_BUCKET = os.getenv("OSS_BUCKET", "")  # OSS存储桶名称
OSS_PUBLIC_DOMAIN = os.getenv("OSS_PUBLIC_DOMAIN", "")  # 公网访问域名（可选），如 https://your-bucket.oss-cn-shanghai.aliyuncs.com
