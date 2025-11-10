import tempfile  # 临时文件工具
import os  # 文件操作
import ffmpeg  # ffmpeg-python封装

VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}  # 常见视频扩展名
AUDIO_EXTS = {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg"}  # 常见音频扩展名


def is_video_filename(filename: str) -> bool:  # 判断是否为视频文件
    ext = os.path.splitext(filename or "")[1].lower()  # 提取扩展名
    return ext in VIDEO_EXTS  # 返回是否属于视频扩展


def to_mp3_bytes(file_bytes: bytes, src_filename: str) -> bytes:  # 将任意音视频转为mp3字节
    # 将输入字节写入临时源文件
    with tempfile.NamedTemporaryFile(delete=False) as f_src:  # 创建临时源文件
        f_src.write(file_bytes)  # 写入字节
        src_path = f_src.name  # 记录路径
    # 目标mp3临时文件
    dst_fd, dst_path = tempfile.mkstemp(suffix=".mp3")  # 创建目标文件
    os.close(dst_fd)  # 关闭多余fd
    try:
        # 使用ffmpeg转为mp3，采样率16000Hz（阿里云推荐），码率128k
        (
            ffmpeg
            .input(src_path)
            .output(dst_path, acodec='libmp3lame', ar='16000', audio_bitrate='128k', vn=None)
            .overwrite_output()
            .run(quiet=True)
        )  # 执行转码
        with open(dst_path, 'rb') as f:  # 读取转码结果
            return f.read()  # 返回字节
    finally:
        try:
            os.remove(src_path)  # 删除源文件
        except Exception:
            pass
        try:
            os.remove(dst_path)  # 删除目标文件
        except Exception:
            pass
