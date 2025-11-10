import smtplib  # 导入SMTP库
import ssl  # 导入SSL库
from email.mime.text import MIMEText  # 导入纯文本邮件类
from email.mime.multipart import MIMEMultipart  # 导入多部分邮件类
from typing import Optional  # 导入可选类型
from app.core.config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASSWORD,
    SMTP_FROM,
    SMTP_USE_SSL,
    SMTP_STARTTLS,
)  # 导入SMTP配置


def send_email(to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> None:  # 定义发送邮件函数
    message = MIMEMultipart("alternative")  # 创建多格式邮件容器
    message["Subject"] = subject  # 设置邮件主题
    message["From"] = SMTP_FROM  # 设置发件人
    message["To"] = to_email  # 设置收件人

    if text_content:  # 如果存在纯文本内容
        part1 = MIMEText(text_content, "plain", "utf-8")  # 创建纯文本部分
        message.attach(part1)  # 附加纯文本部分

    part2 = MIMEText(html_content, "html", "utf-8")  # 创建HTML部分
    message.attach(part2)  # 附加HTML部分

    try:  # 捕获整体发送异常
        if SMTP_USE_SSL:  # 如果配置使用SSL直连
            context = ssl.create_default_context()  # 创建默认SSL上下文
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:  # 使用SSL方式连接SMTP服务器
                server.login(SMTP_USER, SMTP_PASSWORD)  # 登录SMTP服务器
                server.sendmail(SMTP_FROM, to_email, message.as_string())  # 发送邮件
        else:  # 非SSL直连
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:  # 非SSL明文连接
                server.ehlo()  # 打招呼
                if SMTP_STARTTLS:  # 如果启用STARTTLS
                    context = ssl.create_default_context()  # 创建SSL上下文
                    server.starttls(context=context)  # 升级到TLS
                    server.ehlo()  # 升级后再次打招呼
                server.login(SMTP_USER, SMTP_PASSWORD)  # 登录
                server.sendmail(SMTP_FROM, to_email, message.as_string())  # 发送
    except smtplib.SMTPAuthenticationError as e:  # 认证错误
        raise Exception(f"SMTP认证失败：{e.smtp_error.decode('utf-8', 'ignore') if hasattr(e, 'smtp_error') else str(e)}")  # 抛出更友好的异常
    except smtplib.SMTPConnectError as e:  # 连接失败
        raise Exception(f"SMTP连接失败：{str(e)}")  # 抛出异常
    except smtplib.SMTPException as e:  # 其他SMTP异常
        raise Exception(f"SMTP异常：{str(e)}")  # 抛出异常
    except Exception as e:  # 其他未知异常
        raise Exception(f"发送邮件失败：{str(e)}")  # 抛出异常
