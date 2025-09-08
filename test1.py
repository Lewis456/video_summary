import os
import ffmpeg
import whisper
from openai import OpenAI


# 1. 视频转音频
def video2audio(input_video="data/test1.mp4", output_audio="data/output1.mp3"):
    ffmpeg.input(input_video).output(output_audio, ac=1, ar=16000).run()
    return output_audio


# 2. Whisper 转写
def audio2text(audio_file="data/output1.mp3"):
    model = whisper.load_model("medium")  # 可选 "large"，更准
    result = model.transcribe(audio_file, language="zh", fp16=False)

    # 打印分段转写（可选）
    for seg in result["segments"]:
        print(f"[{seg['start']:.2f} - {seg['end']:.2f}] {seg['text']}")

    # 拼接全文
    full_text = " ".join([seg["text"] for seg in result["segments"]])
    print("\n=== 转写预览（前200字） ===\n")
    print(full_text[:200])
    return full_text


# 3. AI 总结
def ai_summary(full_text):
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    completion = client.chat.completions.create(
        model="qwen-plus",
        messages=[
            {
                "role": "system",
                "content": "你是一个课程视频总结助手，负责将长文本转写结果整理成清晰的学习笔记。",
            },
            {
                "role": "user",
                "content": f"""
以下是课程视频的转写文本，请你分章节总结其中的主要内容，并提炼学习要点：

{full_text}
"""
            },
        ],
    )
    return completion.choices[0].message.content


# 4. 主流程
if __name__ == "__main__":
    # 1. 视频转音频
    audio_file = video2audio()

    # 2. 音频转文字
    text = audio2text(audio_file)

    # 3. AI 总结
    summary = ai_summary(text)
    print("\n=== 总结结果 ===\n")
    print(summary)
