import os  # 导入os库
import time  # 导入time库用于构造唯一文件名
import oss2  # 导入阿里云OSS SDK
from typing import Tuple, Optional  # 导入类型注解
from app.core.config import (
    ALIYUN_AK_ID,
    ALIYUN_AK_SECRET,
    OSS_ENDPOINT,
    OSS_BUCKET,
    OSS_PUBLIC_DOMAIN,
)


def get_bucket():  # 获取Bucket实例
    if not (ALIYUN_AK_ID and ALIYUN_AK_SECRET and OSS_ENDPOINT and OSS_BUCKET):  # 校验必需配置
        raise ValueError("缺少OSS配置：请设置 OSS_ENDPOINT/OSS_BUCKET 与访问密钥")  # 抛出异常
    auth = oss2.Auth(ALIYUN_AK_ID, ALIYUN_AK_SECRET)  # 创建认证对象
    bucket = oss2.Bucket(auth, OSS_ENDPOINT, OSS_BUCKET)  # 创建Bucket对象
    return bucket  # 返回Bucket


def upload_bytes_and_get_url(data: bytes, filename: str, content_type: str, folder: Optional[str] = None) -> str:  # 上传字节并返回URL
    bucket = get_bucket()  # 获取Bucket
    # 生成唯一对象名，保留原扩展名
    name, ext = os.path.splitext(filename)  # 拆分文件名和扩展名
    base_dir = folder.strip('/') if folder else 'uploads'  # 选择目录（默认uploads）
    object_key = f"{base_dir}/{int(time.time()*1000)}{ext}"  # 使用毫秒时间戳构造路径

    # 上传对象
    headers = {"Content-Type": content_type} if content_type else None  # 设置内容类型
    bucket.put_object(object_key, data, headers=headers)  # 直接上传字节数据

    # 生成公网可访问URL
    if OSS_PUBLIC_DOMAIN:  # 若配置了公网域名
        url = f"{OSS_PUBLIC_DOMAIN.rstrip('/')}/{object_key}"  # 使用自定义域名拼接URL
    else:  # 否则使用默认规则
        endpoint_host = OSS_ENDPOINT.replace("http://", "").replace("https://", "").rstrip('/')  # 去除协议
        url = f"https://{OSS_BUCKET}.{endpoint_host}/{object_key}"  # 拼接默认公网URL
    return url  # 返回URL
