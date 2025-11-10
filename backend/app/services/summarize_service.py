# summarize_qwen.py
import os
from http import HTTPStatus
from dashscope import Generation
import datetime
from app.services.oss_service import upload_bytes_and_get_url  # 导入OSS上传

def summarize_text(input_file=None):
    """
    调用 Qwen 模型生成学习笔记总结，并将结果保存到OSS的data目录（markdown格式）
    :param input_file: 转写文本文件路径
    :return: 生成的总结文本
    """
    if input_file is None:
        input_file = "data/output/result.txt"

    # 读取转写结果
    with open(input_file, "r", encoding="utf-8") as f:
        transcript = f.read()

    if not transcript.strip():
        raise ValueError("转写结果为空，无法总结")

    # 从环境变量读取 API Key
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("缺少环境变量 DASHSCOPE_API_KEY")

    # 调用 Qwen 模型
    response = Generation.call(
        model="qwen-plus",   # 可换成 qwen-max / qwen-turbo
        api_key=api_key,
        messages=[
            {
                "role": "system",
                "content": "你是一位专业的学习笔记助手，帮助用户从转写文本中生成条理清晰、分层详细的学习笔记。"
            },
            {
                "role": "user",
                "content": f"请根据以下转写文本生成学习笔记，要求：\
1. 保持逻辑结构（背景、目标、内容、特色、总结等），\
2. 每个要点下展开2~3句解释，避免只有简单标题，\
3. 使用 Markdown 格式，分层清晰，\
4. 尽量保留细节和举例。\
\n\n原始转写文本：\n{transcript}"
            }
        ]
    )

    # 处理结果
    if response.status_code == HTTPStatus.OK:
        summary = response.output["text"]
        # 上传到OSS的data目录（markdown格式）
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # 生成时间戳
        oss_filename = f"summary_{timestamp}.md"  # 使用.md后缀
        url = upload_bytes_and_get_url(
            summary.encode('utf-8'),  # 转为字节
            oss_filename,
            'text/markdown',  # content-type
            folder='data'  # 保存到OSS的data文件夹
        )
        print(f"\n=== 总结已保存到 OSS: {url} ===")
        return summary
    else:
        print("请求失败:", response)
        # 若内容不合规，返回友好提示而非None
        if response.code == "DataInspectionFailed":
            return "内容审核未通过，无法生成总结，请尝试其他视频。"
        return None
