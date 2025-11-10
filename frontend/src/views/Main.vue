<template> <!-- 模板：生成页面UI -->
    <!-- 外层背景容器：渐变背景和波浪装饰 -->
    <div class="main-background">
      <!-- 波浪装饰元素 -->
      <div class="wave wave-1"></div>
      <div class="wave wave-2"></div>
      <div class="wave wave-3"></div>
      
      <div class="main-page"> <!-- 外层容器：页面居中宽布局 -->
      <div class="header-bar"> <!-- 顶部栏：标题与退出按钮 -->
        <h2 class="title">智能视频总结系统</h2> <!-- 页面标题 -->
        <div style="display:flex; gap:10px; align-items:center;"> <!-- 右侧按钮组 -->
          <el-avatar :size="36" :src="avatarUrl" @click="goProfile" style="cursor:pointer;" /> <!-- 头像按钮：点击进入profile -->
          <el-button type="danger" plain @click="logout">退出登录</el-button> <!-- 退出按钮 -->
        </div>
      </div> <!-- 顶部栏结束 -->

      <!-- 卡片容器：上传与操作区 -->
      <el-card class="card">
        <div class="card-title">请选择要总结的视频文件</div> <!-- 卡片标题说明 -->

        <!-- 上传组件开始：仅允许视频，手动提交，限制单文件 -->
        <el-upload
          class="upload-box"
          drag
          action=""
          :auto-upload="false"
          :on-change="handleFileChange"
          :show-file-list="true"
          :limit="1"
          accept="video/*"
        >
          <i class="el-icon-upload"></i>
          <div class="el-upload__text">拖拽视频到此处，或点击选择视频</div>
          <template #tip>
            <div class="el-upload__tip">仅支持视频格式：mp4、mov、avi、mkv、webm，单次仅限一个文件</div>
          </template>
        </el-upload>
        <!-- 上传组件结束 -->

        <div class="actions"> <!-- 操作按钮区域 -->
          <el-button
            type="primary"
            :loading="running"
            :disabled="running || (!selectedFile || !isVideoFile)"
            @click="startTask"
          >开始总结</el-button>
          <el-button @click="cancelTask" :disabled="!running">暂停/取消</el-button>
          <el-button @click="exportSummary" :disabled="!summaryText || summaryText.trim() === ''">一键导出</el-button>
          <el-button @click="clearSelection" :disabled="running && !selectedFile && !summaryText && !transcriptText">清空</el-button>
        </div> <!-- 操作按钮区域结束 -->

        <div v-if="running" style="margin-top:12px;"> <!-- 进度与阶段展示（任务进行中显示） -->
          <el-progress :percentage="progress" :stroke-width="12"></el-progress> <!-- 进度条 -->
          <div style="margin-top:6px;color:#666;">当前阶段：{{ stageLabel }}</div> <!-- 阶段文字 -->
        </div>
      </el-card> <!-- 卡片结束 -->

      <el-card v-if="transcriptText" class="result-card"> <!-- 转写结果卡片：有文本时显示 -->
        <div class="card-title">转写文本（视频转文字结果）</div> <!-- 标题 -->
        <el-input type="textarea" :rows="10" v-model="transcriptText" readonly></el-input> <!-- 展示转写文本 -->
      </el-card>

      <el-card v-if="summaryText" class="result-card"> <!-- 总结结果卡片：有文本时显示 -->
        <div class="card-title">总结文本（基于转写的总结）</div> <!-- 标题 -->
        <el-input type="textarea" :rows="12" v-model="summaryText" readonly></el-input> <!-- 展示总结文本 -->
        <div class="actions"> <!-- 结果操作按钮区域 -->
          <el-button @click="copySummary">复制总结</el-button> <!-- 复制按钮 -->
        </div> <!-- 结果操作区域结束 -->
      </el-card> <!-- 结果卡片结束 -->
      </div> <!-- 外层容器结束 -->
    </div> <!-- 背景容器结束 -->
  </template> <!-- 模板结束 -->

  <script setup>
  import { ref, computed, onBeforeUnmount, onMounted, onActivated, onDeactivated } from "vue"; // 引入ref/computed/生命周期（包括激活和失活钩子）
  import axios from "axios"; // 引入axios用于HTTP请求
  import { ElMessage, ElMessageBox } from "element-plus"; // 引入消息提示组件和确认对话框组件
  import { useRouter } from "vue-router"; // 引入路由钩子

  // 定义组件名称，用于keep-alive识别
  defineOptions({
    name: 'Main'
  });

  const router = useRouter(); // 获取路由实例
  const selectedFile = ref(null); // 已选择的原始文件对象（File对象无法被keep-alive保存，但响应式状态可以）
  const selectedFileName = ref(""); // 已选择的文件名（用于显示）
  const isVideoFile = ref(false); // 当前选择是否为视频文件
  const transcriptText = ref(""); // 转写文本展示（会被keep-alive保留）
  const summaryText = ref(""); // 总结结果文本（会被keep-alive保留）

  const running = ref(false); // 是否有任务在进行
  const taskId = ref(""); // 当前任务ID
  const progress = ref(0); // 进度百分比
  const stage = ref("idle"); // 当前阶段标识
  let pollTimer = null; // 轮询定时器ID

  const avatarUrl = ref(""); // 头像URL（可在profile保存后拉取并缓存）
  const isVip = ref(false); // 是否是VIP用户

  const stageLabel = computed(() => { // 阶段文字映射
    const map = { idle: "空闲", queued: "排队中", recognizing: "语音转写中", summarizing: "总结生成中", finished: "已完成", failed: "失败", cancelled: "已取消", running: "执行中" };
    return map[stage.value] || stage.value; // 返回映射文字
  }); // 结束

  const allowedExtensions = ["mp4", "mov", "avi", "mkv", "webm"]; // 允许的视频扩展名列表

  const goProfile = () => { // 跳转个人资料页
    router.push('/profile');
  };

  const logout = () => { // 退出登录
    localStorage.removeItem('token');
    router.push('/login');
  };


  const clearSelection = () => { // 清空选择与结果
    selectedFile.value = null;
    selectedFileName.value = ""; // 清空文件名
    isVideoFile.value = false;
    transcriptText.value = "";
    summaryText.value = "";
    progress.value = 0;
    stage.value = "idle";
    taskId.value = "";
    running.value = false; // 清空运行状态
    if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
  };

  const isVideoMime = (mime) => { return typeof mime === 'string' && mime.startsWith('video/'); }; // 校验MIME是否为视频
  const isAllowedExt = (name) => { // 校验扩展名是否允许
    if (!name) return false;
    const parts = name.split('.');
    const ext = parts.length > 1 ? parts.pop().toLowerCase() : '';
    return ["mp4","mov","avi","mkv","webm"].includes(ext);
  };

  const handleFileChange = (file) => { // 处理选择文件事件
    const raw = file && file.raw ? file.raw : null; // 安全读取原始文件
    if (!raw) { 
      selectedFile.value = null; 
      selectedFileName.value = ""; // 清空文件名
      isVideoFile.value = false; 
      return; 
    }
    const mimeOk = isVideoMime(raw.type);
    const extOk = isAllowedExt(raw.name);
    if (!mimeOk || !extOk) { 
      ElMessage.error("请选择有效的视频文件（mp4/mov/avi/mkv/webm）"); 
      selectedFile.value = null; 
      selectedFileName.value = ""; // 清空文件名
      isVideoFile.value = false; 
      return; 
    }
    selectedFile.value = raw; 
    selectedFileName.value = raw.name; // 保存文件名，即使File对象无法被keep-alive保存，文件名可以保留
    isVideoFile.value = true;
  };

  const startTask = async () => { // 发起异步任务
    if (!selectedFile.value || !isVideoFile.value) { ElMessage.warning("请选择一个视频文件"); return; }
    try {
      running.value = true; progress.value = 0; stage.value = "queued"; taskId.value = "";
      const form = new FormData();
      form.append('file', selectedFile.value); // 只支持文件上传
      const res = await axios.post("http://127.0.0.1:8000/api/summary/start", form, { headers: { 'Content-Type': 'multipart/form-data' } });
      const tid = res.data && res.data.task_id ? res.data.task_id : ""; // 兼容读取task_id
      if (!tid) { throw new Error('任务创建失败'); }
      taskId.value = tid; pollStatus();
    } catch (err) {
      running.value = false;
      const detail = (err && err.response && err.response.data && err.response.data.detail) ? err.response.data.detail : err.message; // 提取错误
      ElMessage.error("创建任务失败：" + detail);
    }
  };

  const pollStatus = () => { // 轮询任务状态
    if (pollTimer) { clearInterval(pollTimer); }
    const tick = async () => {
      try {
        const res = await axios.get("http://127.0.0.1:8000/api/summary/status", { params: { task_id: taskId.value } });
        const data = res.data || {}; // 读取数据
        progress.value = (typeof data.progress !== 'undefined') ? data.progress : progress.value; // 兼容无progress
        stage.value = data.stage ? data.stage : (data.status ? data.status : stage.value); // 兼容stage/status
        if (data.transcript) { transcriptText.value = data.transcript; } // 已产生转写
        if (data.summary) { summaryText.value = data.summary; } // 已产生总结
        if (data.status === 'done' || data.stage === 'finished') { // 完成
          running.value = false; clearInterval(pollTimer); pollTimer = null; ElMessage.success('处理完成');
        } else if (data.status === 'error' || data.stage === 'failed') { // 失败
          running.value = false; clearInterval(pollTimer); pollTimer = null;
          const errMsg = data.error ? data.error : '未知错误';
          ElMessage.error('处理失败：' + errMsg);
        } else if (data.status === 'cancelled' || data.cancelled) { // 取消
          running.value = false; clearInterval(pollTimer); pollTimer = null; ElMessage.info('任务已取消');
        }
      } catch (err) { // 轮询异常
        running.value = false; clearInterval(pollTimer); pollTimer = null;
        const detail = (err && err.response && err.response.data && err.response.data.detail) ? err.response.data.detail : err.message;
        ElMessage.error('查询任务失败：' + detail);
      }
    };
    tick(); pollTimer = setInterval(tick, 2000);
  };

  const cancelTask = async () => { // 取消当前任务
    if (!taskId.value) { return; }
    try {
      await axios.post("http://127.0.0.1:8000/api/summary/cancel", null, { params: { task_id: taskId.value } });
    } catch (err) {
      const detail = (err && err.response && err.response.data && err.response.data.detail) ? err.response.data.detail : err.message;
      ElMessage.error('取消失败：' + detail);
    }
  };

  const copySummary = async () => { // 复制总结文本到剪贴板
    if (!summaryText.value || summaryText.value.trim() === '') { // 如果总结文本为空
      ElMessage.warning('没有可复制的内容'); // 提示无内容
      return;
    }
    try {
      // 使用现代 Clipboard API 复制文本
      if (navigator.clipboard && navigator.clipboard.writeText) { // 检查浏览器支持
        await navigator.clipboard.writeText(summaryText.value); // 复制文本到剪贴板
        ElMessage.success('总结已复制到剪贴板'); // 显示成功提示
      } else {
        // 降级方案：使用传统的复制方法（兼容旧浏览器）
        const textArea = document.createElement('textarea'); // 创建临时文本域
        textArea.value = summaryText.value; // 设置文本内容
        textArea.style.position = 'fixed'; // 设置样式使其不可见
        textArea.style.left = '-9999px'; // 移出屏幕外
        document.body.appendChild(textArea); // 添加到DOM
        textArea.select(); // 选中文本
        try {
          document.execCommand('copy'); // 执行复制命令
          ElMessage.success('总结已复制到剪贴板'); // 显示成功提示
        } catch (err) {
          ElMessage.error('复制失败，请手动复制'); // 显示错误提示
        }
        document.body.removeChild(textArea); // 移除临时元素
      }
    } catch (err) {
      ElMessage.error('复制失败：' + err.message); // 显示错误提示
    }
  };

  const exportSummary = () => { // 导出总结为 .md 文件
    if (!summaryText.value || summaryText.value.trim() === '') { // 如果总结文本为空
      ElMessage.warning('没有可导出的内容'); // 提示无内容
      return;
    }
    try {
      // 生成文件名：使用当前时间戳
      const now = new Date(); // 获取当前时间
      const timestamp = now.toISOString().replace(/[:.]/g, '-').slice(0, -5); // 格式化时间戳（去掉冒号和点）
      const filename = `视频总结_${timestamp}.md`; // 生成文件名
      
      // 创建 Blob 对象，类型为 markdown
      const blob = new Blob([summaryText.value], { type: 'text/markdown;charset=utf-8' }); // 创建 Blob 对象
      
      // 创建下载链接
      const url = URL.createObjectURL(blob); // 创建对象 URL
      const link = document.createElement('a'); // 创建 <a> 元素
      link.href = url; // 设置链接地址
      link.download = filename; // 设置下载文件名
      link.style.display = 'none'; // 隐藏链接元素
      
      // 触发下载
      document.body.appendChild(link); // 添加到 DOM
      link.click(); // 模拟点击下载
      
      // 清理
      document.body.removeChild(link); // 移除链接元素
      URL.revokeObjectURL(url); // 释放对象 URL
      
      ElMessage.success('总结已导出为 ' + filename); // 显示成功提示
    } catch (err) {
      ElMessage.error('导出失败：' + err.message); // 显示错误提示
    }
  };

  onBeforeUnmount(() => { // 组件卸载前钩子
    if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
  });

  // 新增：加载并设置当前用户头像和会员信息
  const loadUserProfile = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;
      const res = await axios.get('http://127.0.0.1:8000/api/user/profile', {
        headers: { Token: token },
      });
      avatarUrl.value = res.data && res.data.avatar_url ? res.data.avatar_url : "";
      isVip.value = res.data && res.data.is_vip ? true : false; // 更新VIP状态
    } catch (err) {
      // 不提示错误，防止一直弹窗
    }
  };

  onMounted(() => { // 页面首次加载时自动拉取头像和会员信息
    loadUserProfile();
  });

  // 组件激活时（从其他页面返回时触发）
  onActivated(() => {
    // 刷新用户信息（头像可能已更新）
    loadUserProfile();
    
    // 如果任务还在进行中，恢复轮询
    // 注意：keep-alive会保留所有响应式状态，包括transcriptText和summaryText
    if (running.value && taskId.value) {
      pollStatus(); // 恢复轮询任务状态
    }
    // 即使任务已完成，transcriptText和summaryText也会被keep-alive自动保留
  });

  // 组件失活时（跳转到其他页面时触发）
  onDeactivated(() => {
    // 不清空数据，只停止轮询（避免在后台继续请求）
    // 注意：不清除pollTimer，因为在activated时会重新启动
    if (pollTimer) {
      clearInterval(pollTimer);
      pollTimer = null;
    }
  });
  </script>

  <style scoped>
  /* 背景容器：全屏，渐变背景 */
  .main-background {
    min-height: 100vh; /* 最小高度100vh，内容超出时可扩展 */
    width: 100%; /* 使用100%而不是100vw，避免滚动条宽度问题 */
    position: relative; /* 相对定位，允许页面自然滚动 */
    background: linear-gradient(135deg, #e8f0fe 0%, #f3e5f5 100%); /* 淡蓝到淡紫的渐变背景 */
    padding: 20px; /* 内边距 */
    box-sizing: border-box; /* 边框盒模型 */
    z-index: 0; /* 背景层级 */
  }

  /* 波浪装饰元素 */
  .wave {
    position: fixed; /* 固定定位，滚动时保持固定位置 */
    border-radius: 50%; /* 圆形边框 */
    opacity: 0.3; /* 透明度 */
    filter: blur(40px); /* 模糊效果 */
    z-index: 0; /* z-index层级，确保在内容之下 */
  }

  .wave-1 { /* 左下角波浪 */
    width: 600px; /* 宽度 */
    height: 600px; /* 高度 */
    background: linear-gradient(135deg, #6b73ff 0%, #9d50bb 100%); /* 蓝紫色渐变 */
    bottom: -300px; /* 底部位置 */
    left: -200px; /* 左侧位置 */
    animation: float 8s ease-in-out infinite; /* 浮动动画 */
  }

  .wave-2 { /* 右上角波浪 */
    width: 500px; /* 宽度 */
    height: 500px; /* 高度 */
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); /* 紫蓝色渐变 */
    top: -200px; /* 顶部位置 */
    right: -150px; /* 右侧位置 */
    animation: float 10s ease-in-out infinite reverse; /* 反向浮动动画 */
  }

  .wave-3 { /* 右下角小波浪 */
    width: 400px; /* 宽度 */
    height: 400px; /* 高度 */
    background: linear-gradient(135deg, #8b5cf6 0%, #6b46c1 100%); /* 紫色渐变 */
    bottom: -150px; /* 底部位置 */
    right: -100px; /* 右侧位置 */
    animation: float 12s ease-in-out infinite; /* 浮动动画 */
  }

  @keyframes float { /* 浮动动画关键帧 */
    0%, 100% {
      transform: translate(0, 0) scale(1); /* 初始和结束位置 */
    }
    50% {
      transform: translate(20px, -20px) scale(1.05); /* 中间位置，轻微移动和放大 */
    }
  }

  /* 主页面容器 */
  .main-page { 
    max-width: 900px; /* 最大宽度 */
    margin: 0 auto; /* 居中 */
    padding: 32px; /* 内边距 */
    position: relative; /* 相对定位 */
    z-index: 10; /* z-index层级，确保在波浪之上 */
    min-height: calc(100vh - 40px); /* 最小高度，内容可自然扩展 */
    overflow-x: hidden; /* 禁止横向滚动 */
    box-sizing: border-box; /* 边框盒模型 */
    padding-bottom: 40px; /* 底部内边距，确保内容底部有足够空间 */
  }
  
  .header-bar { 
    display: flex; /* flex布局 */
    align-items: center; /* 垂直居中 */
    justify-content: space-between; /* 两端对齐 */
    margin-bottom: 16px; /* 底部间距 */
  }
  
  .title { 
    margin: 0; /* 外边距为0 */
    font-weight: 600; /* 字重 */
    color: #4a5568; /* 深灰色文字 */
  }
  
  .card { 
    margin-top: 12px; /* 顶部间距 */
    background: #fff; /* 白色背景 */
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1); /* 阴影效果 */
  }
  
  .card-title { 
    font-size: 14px; /* 字体大小 */
    color: #666; /* 灰色文字 */
    margin-bottom: 12px; /* 底部间距 */
  }
  
  .upload-box { 
    width: 520px; /* 宽度 */
    margin: 0 auto; /* 居中 */
  }
  
  .actions { 
    display: flex; /* flex布局 */
    gap: 12px; /* 间距 */
    justify-content: center; /* 居中 */
    margin-top: 16px; /* 顶部间距 */
  }
  
  .result-card { 
    margin-top: 20px; /* 顶部间距 */
    background: #fff; /* 白色背景 */
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1); /* 阴影效果 */
  }
  </style>
  