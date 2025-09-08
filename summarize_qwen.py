# summarize_qwen.py
import os
from http import HTTPStatus
from dashscope import Generation
import datetime

def summarize_text(input_file=None, output_file=None):
    """
    调用 Qwen 模型生成学习笔记总结
    :param input_file: 转写文本文件路径
    :param output_file: 总结输出文件路径，如果未指定，会在 output 目录生成带时间戳文件
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

    # 生成输出文件名（带时间戳）
    if output_file is None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_dir = "data/output"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"summary_{timestamp}.txt")

    # 保存结果
    if response.status_code == HTTPStatus.OK:
        summary = response.output["text"]
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(summary)
        print(f"\n=== 总结已保存到 {output_file} ===")
        return summary
    else:
        print("请求失败:", response)
        return None
