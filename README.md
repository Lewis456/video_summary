# 视频智能摘要系统

这是一个基于Web的视频智能摘要系统，可实现视频上传、音频提取、语音识别和AI摘要生成的完整流程。

## 功能特性

- 🎥 视频上传与处理
- 🔊 视频转音频
- 📄 音频文本识别
- 🧠 使用AI生成文本摘要
- 📊 实时处理进度显示

## 系统架构

```
├── app.py          # FastAPI后端服务
├── main.py         # 主处理流程
├── recognize.py    # 语音识别接口
├── summarize_qwen.py # AI摘要生成模块
└── templates/
    └── index.html  # 前端界面
```

## 使用方法

1. 启动服务后访问Web界面
2. 上传视频文件
3. 系统自动进行以下处理：
   - 提取视频音频
   - 将音频转为文本
   - 使用AI生成摘要
4. 查看处理进度和最终摘要结果

## 技术栈

- FastAPI: 后端API服务
- HTML/CSS: 前端界面
- 阿里云语音识别: 音频转文本
- Qwen: AI摘要生成

## 注意事项

- 系统需要配置阿里云语音识别的API密钥
- 需要安装FFmpeg进行视频音频处理
- AI摘要功能需要连接Qwen服务
- 一定一定要将相关API KEY配置到本地环境，具体可以上网搜索教程！！
- 需要用到阿里云OSS、阿里云智能音频系统相关，新用户三个月试用，每天2h！！！

## 结果展示
![result1](https://github.com/Lewis456/video_summary/blob/main/image/%E7%BB%93%E6%9E%9C3.png?raw=true)
![result2](https://github.com/Lewis456/video_summary/blob/main/image/%E7%BB%93%E6%9E%9C4.png?raw=true)

## 许可证

未在代码库中找到明确的许可证信息。请在使用前联系作者确认许可证类型。

## 贡献指南

未在代码库中找到具体的贡献指南信息。请查看项目文档或联系作者获取贡献方式。
