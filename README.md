# 智能视频总结系统后端

一个基于 FastAPI 的智能视频总结系统，支持视频上传、语音转写和AI文本总结功能。

## 项目结构

```
video-sum/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/          # API路由层
│   │   ├── core/         # 核心配置（数据库、配置）
│   │   ├── models/       # 数据模型
│   │   ├── services/     # 业务服务层
│   │   └── main.py       # 应用入口
│   └── init_db.py        # 数据库初始化
└── frontend/             # 前端应用
    ├── src/
    │   ├── views/        # 页面组件
    │   ├── router/      # 路由配置
    │   └── main.js      # 应用入口
    └── package.json     # 依赖配置
```

## 系统功能

### 用户认证
- 用户注册（邮箱验证码）
- 用户登录（JWT认证）
- 找回密码（邮箱验证码）

### 用户管理
- 用户资料管理（头像、性别、生日等）
- 会员类型管理（普通用户/VIP用户）

### 视频总结
- 视频文件上传（支持 mp4、mov、avi、mkv、webm 格式）
- 视频转音频（自动转换为 mp3）
- 语音转文字（基于阿里云智能语音识别）
- AI文本总结（基于通义千问大模型）
- 异步任务处理（支持任务状态查询和取消）
- 结果导出（Markdown格式）

## 技术栈

- **Web框架**: FastAPI
- **数据库**: MySQL + SQLAlchemy ORM
- **认证**: JWT (JSON Web Token)
- **语音识别**: 阿里云智能语音识别
- **AI总结**: 通义千问 (DashScope)
- **文件存储**: 阿里云OSS
- **视频转码**: ffmpeg-python

## 安装依赖

```bash
pip install -r app/requirements.txt
```

## 环境配置

### 1. 复制环境变量文件

```bash
cp .env.example .env
```

### 2. 编辑 `.env` 文件

配置以下环境变量：
位于backend文件夹下!
```env
# 数据库配置
DATABASE_URL=mysql+pymysql://用户名:密码@主机:端口/数据库名
SECRET_KEY=your-secret-key-here

# SMTP邮件配置（用于发送验证码）
SMTP_HOST=smtp.example.com
SMTP_PORT=465
SMTP_USER=no-reply@example.com
SMTP_PASSWORD=your-smtp-password
SMTP_FROM=no-reply@example.com
SMTP_USE_SSL=true
SMTP_STARTTLS=false

# 阿里云语音识别配置
ALIYUN_AK_ID=your-access-key-id
ALIYUN_AK_SECRET=your-access-key-secret
ALIYUN_APP_KEY=your-app-key

# 通义千问API配置
DASHSCOPE_API_KEY=your-dashscope-api-key

# 阿里云OSS配置（用于文件存储）
OSS_ENDPOINT=https://oss-cn-shanghai.aliyuncs.com
OSS_BUCKET=your-bucket-name
OSS_PUBLIC_DOMAIN=https://your-bucket.oss-cn-shanghai.aliyuncs.com
```

### 3. 创建数据库

```sql
CREATE DATABASE video_sum_db;
```

## 初始化数据库

```bash
python init_db.py
```

## 启动服务

### 开发模式（自动重载）

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 生产模式

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API访问

- **服务地址**: http://127.0.0.1:8000
- **API文档 (Swagger)**: http://127.0.0.1:8000/docs
- **API文档 (ReDoc)**: http://127.0.0.1:8000/redoc

## API接口说明

### 认证接口 (`/api/auth`)
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/send-code` - 发送邮箱验证码
- `POST /api/auth/reset-password` - 重置密码

### 用户接口 (`/api/user`)
- `GET /api/user/profile` - 获取用户资料
- `PUT /api/user/profile` - 更新用户资料
- `POST /api/user/avatar` - 上传头像

### 视频总结接口 (`/api/summary`)
- `POST /api/summary/start` - 提交视频总结任务（上传视频文件）
- `GET /api/summary/status` - 查询任务状态
- `POST /api/summary/cancel` - 取消任务

## 使用流程

1. **用户注册/登录**: 通过邮箱注册账号并登录系统
2. **上传视频**: 在生成页面选择并上传视频文件（支持拖拽上传）
3. **等待处理**: 系统自动进行视频转码、语音识别和文本总结
4. **查看结果**: 查看转写文本和AI生成的总结
5. **导出结果**: 将总结结果导出为Markdown文件

## 注意事项

- 视频文件会自动转换为mp3格式并上传到OSS
- 任务处理为异步执行，可通过任务ID查询进度
- 支持任务取消功能（最佳努力取消）
- 所有文件存储在阿里云OSS，请确保OSS配置正确

## 开发说明

- 任务状态存储在内存中（开发环境），生产环境建议使用Redis或数据库
- 支持CORS跨域请求
- 使用JWT进行用户认证，Token通过Header传递
