<template> <!-- 模板开始：定义页面结构 -->
    <!-- 外层背景容器：渐变背景和波浪装饰 -->
    <div class="login-background">
      <!-- 波浪装饰元素 -->
      <div class="wave wave-1"></div>
      <div class="wave wave-2"></div>
      <div class="wave wave-3"></div>
      
      <!-- 登录卡片：居中显示 -->
      <div class="login-page">
        <!-- Logo区域：圆形图标 -->
        <div class="logo-container">
          <div class="logo-circle">
            <span class="logo-text">Logo</span>
          </div>
        </div>
        
        <!-- 欢迎标题 -->
        <h1 class="welcome-title">Welcome back!</h1>
        
        <!-- 表单容器 -->
        <el-form class="login-form">
          <!-- 表单项：邮箱输入（无标签，简洁设计） -->
          <div class="input-wrapper">
            <span class="input-label">邮箱</span>
            <el-input 
              v-model="email" 
              placeholder="" 
              @keyup.enter="login"
              :class="['custom-input', email ? 'has-value' : '']"
            ></el-input>
          </div>
          
          <!-- 表单项：密码输入（无标签，简洁设计） -->
          <div class="input-wrapper">
            <span class="input-label">密码</span>
            <el-input 
              v-model="password" 
              type="password" 
              placeholder="" 
              @keyup.enter="login"
              :class="['custom-input', password ? 'has-value' : '']"
            ></el-input>
          </div>
          
          <!-- 按钮容器：使用相对定位，方便子按钮绝对定位 -->
          <div class="login-button-container">
            <!-- 主按钮：提交登录，加载中禁用并显示loading，渐变背景 -->
            <el-button 
              :loading="loading" 
              :disabled="loading" 
              @click="login" 
              class="main-login-btn gradient-btn"
            >登录</el-button>
            <!-- 次按钮：跳转找回密码页，放在左下角 -->
            <button 
              type="button" 
              @click="$router.push('/forgot')" 
              class="forgot-btn link-btn"
            >忘记密码？</button>
            <!-- 次按钮：跳转注册页，放在右下角 -->
            <button 
              type="button" 
              @click="$router.push('/register')" 
              class="register-btn link-btn"
            >注册</button>
          </div>
        </el-form>
      </div>
    </div>
  </template> <!-- 模板结束 -->
  
  <script setup> // 采用<script setup>语法糖，简化组件编写
  import { ref, onMounted, onBeforeUnmount } from 'vue'; // 从Vue中导入ref和生命周期钩子
  import axios from 'axios'; // 导入axios用于HTTP请求
  import { useRouter } from 'vue-router'; // 导入useRouter用于路由跳转
  import { ElMessage } from 'element-plus'; // 从Element Plus导入消息提示组件
  
  const router = useRouter(); // 获取路由实例
  const email = ref(''); // 定义响应式变量：邮箱
  const password = ref(''); // 定义响应式变量：密码
  const loading = ref(false); // 定义响应式变量：按钮加载状态
  
  const isValidEmail = (value) => { // 定义函数：校验邮箱格式
    const re = /\S+@\S+\.\S+/; // 简单邮箱正则
    return re.test(value); // 返回校验结果
  }; // 函数结束：邮箱校验
  
  const login = async () => { // 定义异步函数：执行登录
    // 基础表单校验开始
    if (!email.value) { // 如果邮箱为空
      ElMessage.error('请输入邮箱'); // 弹出错误提示
      return; // 终止后续逻辑
    } // 校验结束：邮箱非空
    if (!isValidEmail(email.value)) { // 如果邮箱格式不正确
      ElMessage.error('邮箱格式不正确'); // 弹出错误提示
      return; // 终止后续逻辑
    } // 校验结束：邮箱格式
    if (!password.value) { // 如果密码为空
      ElMessage.error('请输入密码'); // 弹出错误提示
      return; // 终止后续逻辑
    } // 校验结束：密码非空
    // 基础表单校验结束

    try { // 开始try捕获网络或接口错误
      loading.value = true; // 设置加载状态为true
      const res = await axios.post('http://127.0.0.1:8000/api/auth/login', { // 发送POST请求到登录接口
        email: email.value, // 请求体字段：邮箱
        password: password.value // 请求体字段：密码
      }); // 请求结束

      const data = res.data; // 读取响应数据体
      if (!data || !data.token) { // 如果未返回token
        ElMessage.error('登录响应异常，请稍后重试'); // 提示异常
        return; // 终止后续逻辑
      } // 校验结束：token存在

      localStorage.setItem('token', data.token); // 将token存入本地存储供后续请求使用
      ElMessage.success('登录成功'); // 弹出成功提示
      router.push('/generate'); // 登录成功后跳转到/generate页面
    } catch (err) { // 捕获错误分支
      // 处理HTTP错误与网络错误
      const status = err?.response?.status; // 获取HTTP状态码
      const detail = err?.response?.data?.detail; // 获取后端返回的错误信息
      if (status === 401) { // 如果是未授权错误
        ElMessage.error(detail || '邮箱或密码错误'); // 提示账号或密码错误
      } else { // 其他错误
        ElMessage.error(detail || '登录失败，请检查网络或稍后重试'); // 提示通用错误
      } // 分支结束
    } finally { // finally分支总会执行
      loading.value = false; // 恢复按钮加载状态为false
    } // finally结束
  }; // 登录函数结束

  // 组件挂载时：禁用页面滚动
  onMounted(() => {
    document.body.classList.add('login-page-active'); // 给body添加类名
    document.documentElement.classList.add('login-page-active'); // 给html添加类名
  });

  // 组件卸载前：恢复页面滚动
  onBeforeUnmount(() => {
    document.body.classList.remove('login-page-active'); // 移除body类名
    document.documentElement.classList.remove('login-page-active'); // 移除html类名
  });
  </script> // 脚本结束
  
  <style> /* 样式：登录页面需要全局控制body和html */
  /* 全局样式：禁用登录页面的滚动 */
  body.login-page-active {
    margin: 0;
    padding: 0;
    overflow: hidden;
    height: 100vh;
    width: 100vw;
  }

  html.login-page-active {
    overflow: hidden;
    height: 100vh;
    width: 100vw;
  }
  </style>

  <style scoped> /* 作用域样式：仅作用于当前组件 */
  /* 背景容器：全屏，渐变背景 */
  .login-background {
    height: 100vh; /* 固定高度100vh，占据整个视口 */
    width: 100vw; /* 固定宽度100vw，占据整个视口宽度 */
    position: fixed; /* 固定定位，避免滚动 */
    top: 0; /* 顶部对齐 */
    left: 0; /* 左侧对齐 */
    overflow: hidden; /* 隐藏溢出 */
    background: linear-gradient(135deg, #e8f0fe 0%, #f3e5f5 100%); /* 淡蓝到淡紫的渐变背景 */
    display: flex; /* flex布局 */
    align-items: center; /* 垂直居中 */
    justify-content: center; /* 水平居中 */
    padding: 20px; /* 内边距 */
    box-sizing: border-box; /* 边框盒模型 */
  }

  /* 波浪装饰元素 */
  .wave {
    position: absolute; /* 绝对定位 */
    border-radius: 50%; /* 圆形边框 */
    opacity: 0.3; /* 透明度 */
    filter: blur(40px); /* 模糊效果 */
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
      transform: translate(20px, -20px) scale(1.05); /* 中间位置，轻微移动和放大（减少移动范围） */
    }
  }

  /* 登录卡片：白色圆角卡片 */
  .login-page {
    width: 100%; /* 宽度100% */
    max-width: 420px; /* 最大宽度420像素 */
    background: #fff; /* 白色背景 */
    border-radius: 20px; /* 圆角20像素 */
    padding: 40px 35px; /* 内边距 */
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1); /* 阴影效果 */
    position: relative; /* 相对定位 */
    z-index: 10; /* z-index层级，确保在波浪之上 */
  }

  /* Logo容器 */
  .logo-container {
    display: flex; /* flex布局 */
    justify-content: center; /* 水平居中 */
    margin-bottom: 20px; /* 底部间距 */
  }

  /* Logo圆形图标 */
  .logo-circle {
    width: 80px; /* 宽度80像素 */
    height: 80px; /* 高度80像素 */
    border-radius: 50%; /* 圆形 */
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); /* 蓝紫色渐变背景 */
    display: flex; /* flex布局 */
    align-items: center; /* 垂直居中 */
    justify-content: center; /* 水平居中 */
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3); /* 阴影效果 */
  }

  .logo-text {
    color: #fff; /* 白色文字 */
    font-size: 14px; /* 字体大小 */
    font-weight: 500; /* 字重 */
  }

  /* 欢迎标题 */
  .welcome-title {
    text-align: center; /* 文本居中 */
    font-size: 28px; /* 字体大小 */
    font-weight: 700; /* 字重 */
    color: #4a5568; /* 深紫色文字 */
    margin: 0 0 8px 0; /* 外边距 */
    line-height: 1.2; /* 行高 */
  }

  /* 副标题 */
  .subtitle {
    text-align: center; /* 文本居中 */
    font-size: 14px; /* 字体大小 */
    color: #a0aec0; /* 浅灰色文字 */
    margin: 0 0 35px 0; /* 外边距 */
  }

  /* 表单样式 */
  .login-form {
    display: flex; /* flex布局 */
    flex-direction: column; /* 垂直排列 */
    gap: 25px; /* 表单项间距 */
  }

  /* 输入框包装器 */
  .input-wrapper {
    position: relative; /* 相对定位 */
  }

  /* 输入框标签 */
  .input-label {
    display: block; /* 块级元素 */
    font-size: 13px; /* 字体大小 */
    color: #a0aec0; /* 浅灰色 */
    margin-bottom: 8px; /* 底部间距 */
  }

  /* 自定义输入框 */
  .custom-input :deep(.el-input__wrapper) {
    border: none; /* 无边框 */
    border-bottom: 1px solid #e2e8f0; /* 底部边框 */
    border-radius: 0; /* 无圆角 */
    box-shadow: none; /* 无阴影 */
    padding: 0; /* 内边距为0 */
    background: transparent; /* 透明背景 */
    transition: border-color 0.3s; /* 边框颜色过渡动画 */
  }

  .custom-input.has-value :deep(.el-input__wrapper) {
    border-bottom-color: #667eea; /* 有值时边框颜色变为蓝紫色 */
  }

  .custom-input :deep(.el-input__wrapper:hover) {
    border-bottom-color: #667eea; /* 悬停时边框颜色 */
  }

  .custom-input :deep(.el-input__inner) {
    padding: 10px 0; /* 内边距 */
    font-size: 15px; /* 字体大小 */
  }

  /* 登录按钮容器 */
  .login-button-container {
    position: relative; /* 相对定位 */
    margin-top: 15px; /* 顶部间距 */
    margin-bottom: 42px; /* 底部间距（从35px调整为42px，为链接按钮留出更多空间） */
  }

  /* 主登录按钮：渐变背景 */
  .main-login-btn {
    width: 100%; /* 宽度100% */
    height: 45px; /* 高度 */
    border-radius: 8px; /* 圆角 */
    font-size: 16px; /* 字体大小 */
    font-weight: 600; /* 字重 */
    border: none; /* 无边框 */
  }

  /* 渐变按钮样式 */
  .gradient-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; /* 蓝紫色渐变背景 */
    color: #fff !important; /* 白色文字 */
  }

  .gradient-btn:hover {
    background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%) !important; /* 悬停时更深的渐变色 */
    opacity: 0.9; /* 透明度 */
  }

  .gradient-btn:disabled {
    opacity: 0.6; /* 禁用时透明度 */
  }

  /* 链接按钮：Forgot Password 和 Register */
  .link-btn {
    position: absolute; /* 绝对定位 */
    background: none; /* 无背景 */
    border: none; /* 无边框 */
    color: #a0aec0; /* 浅灰色文字 */
    font-size: 14px; /* 字体大小（从12px增大到14px） */
    cursor: pointer; /* 鼠标指针 */
    padding: 6px 8px; /* 内边距（从4px 0增大到6px 8px） */
    transition: color 0.3s; /* 颜色过渡动画 */
  }

  .link-btn:hover {
    color: #667eea; /* 悬停时蓝紫色 */
  }

  /* Forgot Password 按钮 */
  .forgot-btn {
    left: 0; /* 靠左 */
    bottom: -32px; /* 放在登录按钮下方（从-25px调整为-32px，距离更远） */
  }

  /* Register 按钮 */
  .register-btn {
    right: 0; /* 靠右 */
    bottom: -32px; /* 放在登录按钮下方（从-25px调整为-32px，距离更远） */
  }
  </style> /* 样式结束 */
  