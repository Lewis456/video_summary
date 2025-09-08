# app.py
from fastapi import FastAPI, UploadFile, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os, uuid, asyncio, json, datetime
from main import video2audio, upload_audio, audio_rec, save_result, ai_summary

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 存储任务进度
progress_store = {}

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload_video/")
async def upload_video(file: UploadFile):
    task_id = str(uuid.uuid4())
    progress_store[task_id] = []
    os.makedirs("data/input", exist_ok=True)
    os.makedirs("data/output", exist_ok=True)

    video_path = f"data/input/{file.filename}"
    with open(video_path, "wb") as f:
        f.write(await file.read())

    # 后台启动任务
    asyncio.create_task(process_video(task_id, video_path))
    return JSONResponse({"task_id": task_id})

@app.get("/progress/{task_id}")
async def progress(task_id: str):
    async def event_stream():
        last_index = 0
        while True:
            await asyncio.sleep(1)
            progress = progress_store.get(task_id, [])
            if last_index < len(progress):
                for msg in progress[last_index:]:
                    yield f"data: {msg}\n\n"
                last_index = len(progress)
            # 检查任务完成标记
            if progress and json.loads(progress[-1]).get("done"):
                break
    return StreamingResponse(event_stream(), media_type="text/event-stream")

# ------------------------
# 后台处理逻辑
# ------------------------
async def process_video(task_id: str, video_path: str):
    def push(msg):
        progress_store[task_id].append(json.dumps(msg, ensure_ascii=False))

    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Step1: 视频转音频
        push({"type": "status", "step": "开始处理视频", "success": True})
        audio_file = video2audio(video_path)  # 返回带时间戳的路径
        push({"type": "status", "step": f"视频转音频完成: {os.path.basename(audio_file)}", "success": True})

        # Step2: 上传音频 OSS
        object_name = f"audio/audio_{timestamp}.mp3"
        oss_url = upload_audio(audio_file, object_name)
        push({"type": "status", "step": "音频上传 OSS 完成", "success": True})

        # Step3: 阿里云语音识别
        try:
            transcript = audio_rec(oss_url)
            result_file = os.path.join("data/output", f"result_{timestamp}.txt")
            save_result(transcript, result_file)

            # 流式推送转写文本
            for line in transcript.split("。"):
                if line.strip():
                    push({"type": "transcript", "text": line.strip() + "。"})
                    await asyncio.sleep(0.3)
            push({"type": "status", "step": "语音识别完成", "success": True})
        except Exception as e:
            push({"type": "status", "step": f"语音识别失败: {e}", "success": False, "done": True})
            return

        # Step4: 大模型总结
        push({"type": "status", "step": "开始生成总结", "success": True})
        summary_file = os.path.join("data/output", f"summary_{timestamp}.txt")
        summary_text = ai_summary(result_file, summary_file)
        if summary_text:
            for chunk in summary_text.split("。"):
                if chunk.strip():
                    push({"type": "summary", "text": chunk.strip() + "。"})
                    await asyncio.sleep(0.5)
            push({"type": "status", "step": "大模型总结完成", "success": True, "done": True})
        else:
            push({"type": "status", "step": "大模型总结失败", "success": False, "done": True})

    except Exception as e:
        push({"type": "status", "step": f"任务失败: {str(e)}", "success": False, "done": True})
