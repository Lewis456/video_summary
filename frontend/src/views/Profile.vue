<template> <!-- 模板：个人资料页面 -->
  <!-- 外层背景容器：渐变背景和波浪装饰 -->
  <div class="profile-background">
    <!-- 波浪装饰元素 -->
    <div class="wave wave-1"></div>
    <div class="wave wave-2"></div>
    <div class="wave wave-3"></div>
    
    <div class="profile-page"> <!-- 外层容器 -->
    <h2>个人资料</h2> <!-- 标题 -->

    <el-card class="card"> <!-- 信息卡片 -->
      <div class="avatar-row"> <!-- 头像行 -->
        <el-avatar :size="84" :src="form.avatar_url"></el-avatar> <!-- 头像显示 -->
        <div style="margin-left:16px;"> <!-- 右侧上传区 -->
          <!-- 不直接上传，由代码控制 -->
          <el-upload
            action=""
            :auto-upload="false"
            :show-file-list="false"
            accept="image/*"
            :on-change="onAvatarSelected"
          >
            <el-button>选择本地头像</el-button> <!-- 选择按钮 -->
          </el-upload>
          <div style="color:#888; font-size:12px; margin-top:4px;">选择本地图片作为头像，保存后即生效</div> <!-- 提示文案 -->
        </div>
      </div>

      <el-form label-width="90px" style="margin-top:16px;"> <!-- 表单 -->
        <el-form-item label="会员状态"> <!-- 会员信息（只读） -->
          <el-tag :type="form.is_vip ? 'success' : 'info'" size="large">
            {{ form.is_vip ? 'VIP会员' : '普通用户' }}
          </el-tag>
        </el-form-item>
        <el-form-item label="用户名"> <!-- 用户名 -->
          <el-input v-model="form.username" placeholder="请输入用户名"></el-input> <!-- 可编辑用户名 -->
        </el-form-item>
        <el-form-item label="邮箱"> <!-- 邮箱 -->
          <el-input v-model="form.email" disabled></el-input> <!-- 邮箱禁用不可修改 -->
        </el-form-item>
        <el-form-item label="性别"> <!-- 性别 -->
          <!-- 下拉选择 -->
          <el-select v-model="form.gender" placeholder="请选择性别" style="width:100%">
            <el-option label="男" value="male" /> <!-- 选项：男 -->
            <el-option label="女" value="female" /> <!-- 选项：女 -->
            <el-option label="其他" value="other" /> <!-- 选项：其他 -->
          </el-select>
        </el-form-item>
        <el-form-item label="出生日期"> <!-- 生日 -->
          <!-- 日期选择器 -->
          <el-date-picker v-model="form.birth_date" type="date" placeholder="选择日期" style="width:100%" />
        </el-form-item>
      </el-form>

      <div class="actions"> <!-- 操作按钮区 -->
        <el-button type="primary" :loading="saving" @click="save">保存</el-button> <!-- 保存按钮 -->
        <el-button @click="$router.back()">返回</el-button> <!-- 返回按钮 -->
      </div>
    </el-card>
    </div> <!-- 外层容器结束 -->
  </div> <!-- 背景容器结束 -->
</template>

<script setup> // 使用<script setup>语法
import { ref, onMounted } from 'vue'; // 导入ref和生命周期
import axios from 'axios'; // 导入axios
import { ElMessage } from 'element-plus'; // 导入消息提示

const form = ref({ // 表单数据
  username: '', // 用户名
  email: '', // 邮箱（禁改）
  avatar_url: '', // 头像URL（由后端返回）
  gender: '', // 性别
  birth_date: null, // 出生日期（字符串或Date）
  is_vip: false, // 是否是VIP（只读）
});
const saving = ref(false); // 保存加载状态

const loadProfile = async () => { // 加载资料
  try {
    const token = localStorage.getItem('token');
    const res = await axios.get('http://127.0.0.1:8000/api/user/profile', { headers: { Token: token } });
    const data = res.data || {};
    form.value.username = data.username || '';
    form.value.email = data.email || '';
    form.value.avatar_url = data.avatar_url || '';
    form.value.gender = data.gender || '';
    form.value.birth_date = data.birth_date || null;
    form.value.is_vip = data.is_vip || false; // 加载VIP状态
  } catch (err) {
    const detail = (err && err.response && err.response.data && err.response.data.detail) ? err.response.data.detail : err.message; // 兼容读取错误
    ElMessage.error('加载资料失败：' + detail);
  }
};

const onAvatarSelected = async (file) => { // 选择本地头像文件
  try {
    const raw = file && file.raw ? file.raw : null; if (!raw) return; // 无原始文件直接返回
    const token = localStorage.getItem('token'); // 读取token
    const formData = new FormData(); // 创建表单
    formData.append('file', raw); // 附加文件
    const res = await axios.post('http://127.0.0.1:8000/api/user/profile/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data', Token: token },
    });
    const url = res.data && res.data.avatar_url ? res.data.avatar_url : ''; // 兼容读取
    if (url) { form.value.avatar_url = url; }
    ElMessage.success('头像已更新');
  } catch (err) {
    const detail = (err && err.response && err.response.data && err.response.data.detail) ? err.response.data.detail : err.message; // 兼容读取错误
    ElMessage.error('头像上传失败：' + detail);
  }
};

const save = async () => { // 保存资料（不包含邮箱）
  try {
    saving.value = true;
    const token = localStorage.getItem('token');
    let birth = form.value.birth_date;
    if (birth && typeof birth !== 'string') { const d = new Date(birth); const y = d.getFullYear(); const m = String(d.getMonth()+1).padStart(2, '0'); const day = String(d.getDate()).padStart(2, '0'); birth = `${y}-${m}-${day}`; }
    await axios.put('http://127.0.0.1:8000/api/user/profile', {
      username: form.value.username,
      avatar_url: form.value.avatar_url,
      gender: form.value.gender,
      birth_date: birth,
    }, { headers: { Token: token } });
    ElMessage.success('资料已保存');
  } catch (err) {
    const detail = (err && err.response && err.response.data && err.response.data.detail) ? err.response.data.detail : err.message;
    ElMessage.error('保存失败：' + detail);
  } finally { saving.value = false; }
};

onMounted(loadProfile);
</script>

<style scoped> /* 作用域样式 */
/* 背景容器：全屏，渐变背景 */
.profile-background {
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

.profile-page { 
  max-width: 720px; /* 最大宽度 */
  margin: 40px auto; /* 居中，上下间距 */
  padding: 0 16px; /* 内边距 */
  position: relative; /* 相对定位 */
  z-index: 10; /* z-index层级，确保在波浪之上 */
  min-height: calc(100vh - 120px); /* 最小高度，内容可自然扩展 */
  overflow-x: hidden; /* 禁止横向滚动 */
  box-sizing: border-box; /* 边框盒模型 */
  padding-bottom: 40px; /* 底部内边距，确保内容底部有足够空间 */
}

.card { 
  padding: 12px; /* 内边距 */
  background: #fff; /* 白色背景 */
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1); /* 阴影效果 */
  border-radius: 20px; /* 圆角 */
}

.avatar-row { 
  display: flex; /* flex布局 */
  align-items: center; /* 垂直居中 */
}

.actions { 
  display: flex; /* flex布局 */
  gap: 12px; /* 间距 */
  justify-content: flex-end; /* 右对齐 */
}

/* 标题样式 */
h2 {
  color: #4a5568; /* 深灰色文字 */
  margin-bottom: 24px; /* 底部间距 */
}
</style>
  