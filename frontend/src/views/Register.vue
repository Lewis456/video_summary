<template> <!-- 模板开始：定义页面结构 -->
    <!-- 外层背景容器：渐变背景和波浪装饰 -->
    <div class="register-background">
      <!-- 波浪装饰元素 -->
      <div class="wave wave-1"></div>
      <div class="wave wave-2"></div>
      <div class="wave wave-3"></div>
      
      <!-- 注册卡片：居中显示 -->
      <div class="register-page">
        <!-- Logo区域：圆形图标 -->
        <div class="logo-container">
          <div class="logo-circle">
            <span class="logo-text">Logo</span>
          </div>
        </div>
        
        <!-- 欢迎标题 -->
        <h1 class="welcome-title">创建账户</h1>
        
        <!-- 表单容器 -->
        <el-form class="register-form">
          <!-- 表单项：用户名输入（简洁设计） -->
          <div class="input-wrapper">
            <span class="input-label">用户名</span>
            <el-input 
              v-model="username" 
              placeholder="" 
              :class="['custom-input', username ? 'has-value' : '']"
            ></el-input>
          </div>
          
          <!-- 表单项：邮箱输入（简洁设计） -->
          <div class="input-wrapper">
            <span class="input-label">邮箱</span>
            <el-input 
              v-model="email" 
              placeholder="" 
              :class="['custom-input', email ? 'has-value' : '']"
            ></el-input>
          </div>
          
          <!-- 表单项：验证码输入 -->
          <div class="input-wrapper">
            <span class="input-label">验证码</span>
            <div class="code-input-container">
              <el-input 
                v-model="code" 
                placeholder="" 
                :class="['custom-input', 'code-input', code ? 'has-value' : '']"
              ></el-input>
              <el-button 
                :disabled="countdown > 0 || sending" 
                @click="sendCode"
                class="send-code-btn"
                size="small"
              >
                {{ countdown > 0 ? `${countdown}s` : (sending ? '发送中' : '发送验证码') }}
              </el-button>
            </div>
          </div>
          
          <!-- 表单项：密码输入（简洁设计） -->
          <div class="input-wrapper">
            <span class="input-label">密码</span>
            <el-input 
              v-model="password" 
              type="password" 
              placeholder="不少于6位，包含字母和数字"
              :class="['custom-input', password ? 'has-value' : '']"
            ></el-input>
          </div>
          
          <!-- 表单项：确认密码输入（简洁设计） -->
          <div class="input-wrapper">
            <span class="input-label">确认密码</span>
            <el-input 
              v-model="confirm" 
              type="password" 
              placeholder="" 
              :class="['custom-input', confirm ? 'has-value' : '']"
            ></el-input>
          </div>
          
          <!-- 按钮容器 -->
          <div class="register-button-container">
            <!-- 主按钮：提交注册，渐变背景 -->
            <el-button 
              type="primary" 
              :loading="submitting" 
              @click="register"
              class="main-register-btn gradient-btn"
            >注册</el-button>
            <!-- 返回登录按钮 -->
            <button 
              type="button" 
              @click="$router.push('/login')" 
              class="back-login-btn link-btn"
            >返回登录</button>
          </div>
        </el-form>
      </div>
    </div>
  </template> <!-- 模板结束 -->
  
  <script setup> // 使用<script setup>语法
  import { ref, onMounted, onBeforeUnmount } from "vue"; // 导入ref和生命周期钩子
  import axios from "axios"; // 导入axios
  import { ElMessage } from "element-plus"; // 导入消息提示
  import { useRouter } from "vue-router"; // 导入路由
  
  const router = useRouter(); // 获取路由实例
  const username = ref(""); // 用户名
  const email = ref(""); // 邮箱
  const code = ref(""); // 验证码
  const password = ref(""); // 密码
  const confirm = ref(""); // 确认密码
  const countdown = ref(0); // 倒计时秒数
  const sending = ref(false); // 是否正在发送验证码
  const submitting = ref(false); // 是否正在提交注册
  let timerId = null; // 定时器ID

  const isValidEmail = (value) => { // 校验邮箱格式函数
    const re = /\S+@\S+\.\S+/; // 简单正则
    return re.test(value); // 返回校验结果
  }; // 函数结束

  const isValidPassword = (pwd) => { // 校验密码格式函数
    if (!pwd || pwd.length < 6) { // 如果密码为空或长度小于6位
      return "密码长度不能少于6位"; // 返回错误信息
    }
    const hasLetter = /[a-zA-Z]/.test(pwd); // 检查是否包含字母（大小写不限）
    const hasNumber = /[0-9]/.test(pwd); // 检查是否包含数字
    if (!hasLetter) { // 如果没有字母
      return "密码必须包含至少一个字母"; // 返回错误信息
    }
    if (!hasNumber) { // 如果没有数字
      return "密码必须包含至少一个数字"; // 返回错误信息
    }
    return ""; // 验证通过，返回空字符串
  }; // 函数结束

  const startCountdown = () => { // 开始倒计时函数
    countdown.value = 60; // 设置60秒
    timerId && clearInterval(timerId); // 若已有定时器则清除
    timerId = setInterval(() => { // 每秒自减1
      countdown.value -= 1; // 自减
      if (countdown.value <= 0) { // 到0时
        clearInterval(timerId); // 清除定时器
        timerId = null; // 置空ID
      } // 结束
    }, 1000); // 时间间隔1秒
  }; // 函数结束

  const sendCode = async () => { // 点击发送验证码
    if (!email.value) { // 校验邮箱非空
      ElMessage.error("请输入邮箱"); // 提示
      return; // 结束
    } // 结束
    if (!isValidEmail(email.value)) { // 校验邮箱格式
      ElMessage.error("邮箱格式不正确"); // 提示
      return; // 结束
    } // 结束
    try { // 发送验证码
      sending.value = true; // 标记发送中
      await axios.post("http://127.0.0.1:8000/api/auth/send-code", { // 请求发送验证码
        email: email.value, // 邮箱
      }); // 请求结束
      ElMessage.success("验证码已发送，请检查邮箱"); // 成功提示
      startCountdown(); // 开始倒计时
    } catch (err) { // 失败处理
      const detail = err?.response?.data?.detail || err.message; // 提取错误信息
      ElMessage.error("发送失败：" + detail); // 提示失败
    } finally { // finally
      sending.value = false; // 重置发送状态
    } // 结束
  }; // 函数结束

  const register = async () => { // 提交注册
    // 校验密码格式
    const pwdError = isValidPassword(password.value); // 验证密码格式
    if (pwdError) { // 如果密码格式不正确
      ElMessage.error(pwdError); // 提示错误信息
      return; // 结束
    } // 结束
    if (password.value !== confirm.value) { // 校验两次密码一致
      ElMessage.error("两次密码不一致"); // 提示
      return; // 结束
    } // 结束
    if (!code.value) { // 校验验证码非空
      ElMessage.error("请输入验证码"); // 提示
      return; // 结束
    } // 结束
    try { // 请求注册
      submitting.value = true; // 标记提交中
      await axios.post("http://127.0.0.1:8000/api/auth/register", { // 调用注册接口
        username: username.value, // 用户名
        email: email.value, // 邮箱
        password: password.value, // 密码
        code: code.value, // 验证码
      }); // 请求结束
      ElMessage.success("注册成功，请登录"); // 成功提示
      router.push("/login"); // 跳转登录页
    } catch (err) { // 失败处理
      const detail = err?.response?.data?.detail || err.message; // 错误信息
      ElMessage.error("注册失败：" + detail); // 失败提示
    } finally { // finally
      submitting.value = false; // 重置提交状态
    } // 结束
  }; // 函数结束

  // 组件挂载时：禁用页面滚动
  onMounted(() => {
    document.body.classList.add('register-page-active'); // 给body添加类名
    document.documentElement.classList.add('register-page-active'); // 给html添加类名
  });

  // 组件卸载前：恢复页面滚动
  onBeforeUnmount(() => {
    if (timerId) { clearInterval(timerId); timerId = null; } // 清理定时器
    document.body.classList.remove('register-page-active'); // 移除body类名
    document.documentElement.classList.remove('register-page-active'); // 移除html类名
  });
  </script> <!-- 脚本结束 -->
  
  <style> /* 样式：注册页面需要全局控制body和html */
  /* 全局样式：禁用注册页面的滚动 */
  body.register-page-active {
    margin: 0;
    padding: 0;
    overflow: hidden;
    height: 100vh;
    width: 100vw;
  }

  html.register-page-active {
    overflow: hidden;
    height: 100vh;
    width: 100vw;
  }
  </style>

  <style scoped> /* 作用域样式 */
  /* 背景容器：全屏，渐变背景 */
  .register-background {
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

  /* 注册卡片：白色圆角卡片 */
  .register-page {
    width: 100%; /* 宽度100% */
    max-width: 450px; /* 最大宽度450像素（比登录页稍宽，因为有更多字段） */
    background: #fff; /* 白色背景 */
    border-radius: 20px; /* 圆角20像素 */
    padding: 40px 35px; /* 内边距 */
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1); /* 阴影效果 */
    position: relative; /* 相对定位 */
    z-index: 10; /* z-index层级，确保在波浪之上 */
    max-height: 90vh; /* 最大高度90vh */
    overflow-y: auto; /* 内容过多时允许垂直滚动 */
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
    margin: 0 0 35px 0; /* 外边距 */
    line-height: 1.2; /* 行高 */
  }

  /* 表单样式 */
  .register-form {
    display: flex; /* flex布局 */
    flex-direction: column; /* 垂直排列 */
    gap: 20px; /* 表单项间距 */
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

  /* 验证码输入容器 */
  .code-input-container {
    display: flex; /* flex布局 */
    gap: 10px; /* 间距 */
    align-items: center; /* 垂直对齐 */
  }

  .code-input {
    flex: 1; /* 占据剩余空间 */
  }

  .send-code-btn {
    flex-shrink: 0; /* 不收缩 */
    white-space: nowrap; /* 不换行 */
  }

  /* 注册按钮容器 */
  .register-button-container {
    position: relative; /* 相对定位 */
    margin-top: 15px; /* 顶部间距 */
    margin-bottom: 42px; /* 底部间距（从15px调整为42px，为链接按钮留出更多空间） */
  }

  /* 主注册按钮：渐变背景 */
  .main-register-btn {
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

  /* 返回登录链接按钮 */
  .back-login-btn {
    position: absolute; /* 绝对定位 */
    left: 0; /* 靠左 */
    bottom: -32px; /* 放在注册按钮下方（从-25px调整为-32px，距离更远） */
    background: none; /* 无背景 */
    border: none; /* 无边框 */
    color: #a0aec0; /* 浅灰色文字 */
    font-size: 14px; /* 字体大小（从12px增大到14px） */
    cursor: pointer; /* 鼠标指针 */
    padding: 6px 8px; /* 内边距（从4px 0增大到6px 8px） */
    transition: color 0.3s; /* 颜色过渡动画 */
  }

  .back-login-btn:hover {
    color: #667eea; /* 悬停时蓝紫色 */
  }
  </style> /* 样式结束 */
