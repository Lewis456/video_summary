from fastapi import APIRouter, UploadFile, File, HTTPException  # 导入FastAPI组件
from app.services.recognize_service import fileTrans  # 导入语音转写服务
from app.services.summarize_service import summarize_text  # 导入文本总结服务
from app.core.config import ALIYUN_AK_ID, ALIYUN_AK_SECRET, ALIYUN_APP_KEY  # 导入配置
from app.services.oss_service import upload_bytes_and_get_url  # 导入OSS上传服务
from app.services.transcode_service import to_mp3_bytes  # 导入转码服务

# ============== 异步任务接口（前端调用） ==============
import threading  # 导入线程库
import uuid  # 导入uuid生成工具

router = APIRouter()  # 创建路由对象

# 任务状态存储（内存字典，生产可替换为Redis/数据库）
# 结构：tasks[task_id] = {"status": str, "progress": int, "stage": str, "error": str|None, "transcript": str|None, "summary": str|None, "cancelled": bool}
tasks = {}  # 初始化任务表

def _is_cancelled(task_id: str) -> bool:  # 检查任务是否被取消
    return tasks.get(task_id, {}).get("cancelled", False)  # 读取取消标记

def _run_task(task_id: str, file_link: str):  # 后台执行任务函数
    try:
        if _is_cancelled(task_id):  # 若已取消
            tasks[task_id].update({"status": "cancelled", "stage": "cancelled", "progress": 0})  # 标记取消
            return  # 结束
        tasks[task_id].update({"status": "running", "stage": "recognizing", "progress": 10})  # 更新为识别阶段
        # 调用转写（注意：此步骤内部轮询较久，取消会在步骤结束后生效）
        recog_resp = fileTrans(ALIYUN_AK_ID, ALIYUN_AK_SECRET, ALIYUN_APP_KEY, file_link)  # 执行转写
        if _is_cancelled(task_id):  # 步骤返回后再次检查取消
            tasks[task_id].update({"status": "cancelled", "stage": "cancelled", "progress": 0})
            return
        if not recog_resp or not isinstance(recog_resp, dict):
            raise RuntimeError("转写服务返回异常")  # 抛出异常
        # 提取转写文本
        transcript = ""
        try:
            result = recog_resp.get("Result") or {}
            sentences = result.get("Sentences") or []
            transcript = "".join([seg.get("Text", "") for seg in sentences])
            if not transcript:
                transcript = result.get("Result", "") or result.get("Text", "") or ""
        except Exception:
            transcript = ""
        if not transcript.strip():
            raise RuntimeError("未识别到有效语音内容")  # 无有效文本
        tasks[task_id].update({"progress": 60, "stage": "summarizing", "transcript": transcript})  # 更新进度与转写文本
        if _is_cancelled(task_id):  # 在进入总结前检查取消
            tasks[task_id].update({"status": "cancelled", "stage": "cancelled"})
            return
        # 生成总结
        import tempfile, os
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w', encoding='utf-8') as tf:
            tf.write(transcript)
            temp_path = tf.name
        try:
            summary = summarize_text(input_file=temp_path)
        finally:
            try:
                os.remove(temp_path)
            except Exception:
                pass
        if _is_cancelled(task_id):  # 总结后再检查一次取消
            tasks[task_id].update({"status": "cancelled", "stage": "cancelled"})
            return
        if not summary:
            summary = "(总结生成失败或为空)"  # 占位
        tasks[task_id].update({"status": "done", "progress": 100, "stage": "finished", "summary": summary})  # 完成
    except Exception as e:
        tasks[task_id].update({"status": "error", "stage": "failed", "error": str(e)})  # 标记失败

@router.post("/start")
def start_task(  # 提交任务接口
    file: UploadFile = File(...),  # 上传文件（必需）
):
    """提交任务，返回 task_id，后台异步执行识别与总结。上传本地文件后先转mp3再上传OSS。"""
    # 校验配置
    if not (ALIYUN_AK_ID and ALIYUN_AK_SECRET and ALIYUN_APP_KEY):
        raise HTTPException(status_code=500, detail="缺少阿里云语音识别配置")
    # 转mp3并上传到OSS
    try:
        file_bytes = file.file.read()
        mp3_bytes = to_mp3_bytes(file_bytes, file.filename or "upload.bin")  # 转为mp3
        file_link = upload_bytes_and_get_url(mp3_bytes, (file.filename or "upload").rsplit('.',1)[0] + '.mp3', 'audio/mpeg', folder='uploads/audio')  # 上传
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"转码或上传到OSS失败：{str(e)}")
    if not file_link:
        raise HTTPException(status_code=400, detail="文件处理失败，请重试")
    # 生成task_id并初始化状态
    task_id = uuid.uuid4().hex  # 生成唯一ID
    tasks[task_id] = {"status": "queued", "progress": 0, "stage": "queued", "error": None, "transcript": None, "summary": None, "cancelled": False}  # 初始化任务
    # 启动后台线程
    t = threading.Thread(target=_run_task, args=(task_id, file_link), daemon=True)  # 创建守护线程
    t.start()  # 启动线程
    return {"task_id": task_id}  # 返回任务ID

@router.get("/status")
def get_status(task_id: str):  # 查询任务状态接口
    """根据 task_id 查询任务状态与进度，返回部分结果（如有）"""
    data = tasks.get(task_id)  # 获取任务
    if not data:  # 未找到
        raise HTTPException(status_code=404, detail="任务不存在")  # 返回404
    # 返回当前状态
    return {
        "task_id": task_id,
        "status": data.get("status"),
        "progress": data.get("progress"),
        "stage": data.get("stage"),
        "error": data.get("error"),
        "transcript": data.get("transcript"),  # 识别完成后可返回
        "summary": data.get("summary"),  # 完成后返回
        "cancelled": data.get("cancelled", False),  # 是否已取消
    }

@router.post("/cancel")
def cancel_task(task_id: str):  # 取消任务接口
    """设置任务为取消状态（最佳努力取消，可能需等待当前步骤结束）"""
    if task_id not in tasks:  # 任务不存在
        raise HTTPException(status_code=404, detail="任务不存在")
    tasks[task_id]["cancelled"] = True  # 标记取消
    # 若尚未开始运行，可立即置为取消
    if tasks[task_id].get("status") in ("queued",):
        tasks[task_id].update({"status": "cancelled", "stage": "cancelled", "progress": 0})
    return {"msg": "任务已标记为取消", "task_id": task_id}  # 返回结果
