# -*- coding: utf8 -*-
import os
import ffmpeg
import alibabacloud_oss_v2 as oss
from recognize import fileTrans
from summarize_qwen import summarize_text
import datetime

# -----------------------
# 1. 视频转音频
# -----------------------
def video2audio(input_video="data/input/test1.mp4", output_dir="data/output"):
    """
    将视频提取为 16k 单声道音频文件，输出文件名带时间戳
    格式：output_YYYY-MM-DD_HH-MM-SS.mp3
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_audio = os.path.join(output_dir, f"output_{timestamp}.mp3")

    ffmpeg.input(input_video).output(output_audio, ac=1, ar=16000).run()
    return output_audio

# -----------------------
# 2. 上传音频到 OSS
# -----------------------
def upload_audio(file_path, object_name=None):
    """
    上传本地音频文件到 OSS
    :param file_path: 本地文件路径
    :param object_name: OSS 对象名（不传则用文件名）
    :return: OSS 公网 URL
    """
    credentials_provider = oss.credentials.EnvironmentVariableCredentialsProvider()
    cfg = oss.config.load_default()
    cfg.credentials_provider = credentials_provider
    cfg.region = "cn-shanghai"   # 修改为你的 bucket region
    client = oss.Client(cfg)

    if object_name is None:
        object_name = os.path.basename(file_path)

    with open(file_path, "rb") as f:
        result = client.put_object(
            oss.PutObjectRequest(
                bucket="videosummary-v1",   # 修改为你的 bucket 名称
                key=object_name,
                body=f
            )
        )

    print(f"上传完成: {file_path} -> oss://videosummary-v1/{object_name}")
    print(f"status code: {result.status_code}, request id: {result.request_id}, etag: {result.etag}")

    url = f"https://videosummary-v1.oss-cn-shanghai.aliyuncs.com/{object_name}"
    return url

# -----------------------
# 3. 语音识别
# -----------------------
def audio_rec(oss_url: str):
    """
    调用阿里云文件转写服务识别 OSS 上的音频
    :param oss_url: OSS 公网可访问的音频地址
    :return: 识别结果文本
    """
    ak_id = os.getenv("OSS_ACCESS_KEY_ID")
    ak_secret = os.getenv("OSS_ACCESS_KEY_SECRET")
    app_key = os.getenv("OSS_APP_KEY")

    if not ak_id or not ak_secret or not app_key:
        raise ValueError("缺少环境变量: OSS_ACCESS_KEY_ID / OSS_ACCESS_KEY_SECRET / OSS_APP_KEY")

    print("\n=== 开始语音识别 ===")
    resp = fileTrans(ak_id, ak_secret, app_key, oss_url)

    result = resp.get("Result") or resp
    if isinstance(result, dict) and result.get("ResultText"):
        return result["ResultText"]
    else:
        return str(result)

# -----------------------
# 保存识别结果到本地
# -----------------------
def save_result(text: str, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"\n=== 识别结果已保存到 {output_file} ===")

# -----------------------
# 4. 调用大模型分析总结
# -----------------------
def ai_summary(result_file, summary_file):
    summary = summarize_text(result_file, summary_file)
    if summary:
        print("\n=== 大模型总结 ===\n")
        print(summary)
    return summary

# -----------------------
# 5. 主流程
# -----------------------
def main():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Step1: 视频转音频
    input_video = "data/input/test1.mp4"
    audio_file = video2audio(input_video)
    print(f"\n=== 视频转音频完成 ===\n音频路径: {audio_file}")

    # Step2: 上传音频到 OSS
    object_name = f"audio/audio_{timestamp}.mp3"
    oss_url = upload_audio(audio_file, object_name)
    print("\n=== 上传成功，OSS 音频地址 ===")
    print(oss_url)

    # Step3: 调用语音识别
    try:
        transcript = audio_rec(oss_url)
        print("\n=== 识别结果 ===\n")
        print(transcript)

        # Step4: 保存识别结果
        result_file = os.path.join("data/output", f"result_{timestamp}.txt")
        save_result(transcript, result_file)
    except Exception as e:
        print("语音识别失败：", e)
        transcript = ""
        result_file = None

    # Step5: 调用大模型分析总结
    if result_file:
        summary_file = os.path.join("data/output", f"summary_{timestamp}.txt")
        ai_summary(result_file, summary_file)

if __name__ == "__main__":
    main()
