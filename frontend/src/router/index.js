import { createRouter, createWebHistory } from 'vue-router'; // 导入创建路由与历史模式的方法
import Login from '../views/Login.vue'; // 导入登录页组件
import Register from '../views/Register.vue'; // 导入注册页组件
import Main from '../views/Main.vue'; // 导入主要功能页（生成页）组件
import Profile from '../views/Profile.vue'; // 导入个人中心页组件
import Forgot from '../views/Forgot.vue'; // 新增：找回密码页组件

// 定义路由表
const routes = [ // 路由配置数组
  { path: '/', redirect: '/login' }, // 根路径重定向到登录页
  { path: '/login', component: Login, meta: { requiresAuth: false } }, // 登录页不需要鉴权
  { path: '/register', component: Register, meta: { requiresAuth: false } }, // 注册页不需要鉴权
  { path: '/forgot', component: Forgot, meta: { requiresAuth: false } }, // 新增：找回密码页
  { path: '/generate', component: Main, meta: { requiresAuth: true, keepAlive: true } }, // 生成页需要鉴权，需要缓存
  { path: '/profile', component: Profile, meta: { requiresAuth: true } }, // 个人中心页需要鉴权
]; // 路由配置结束

// 创建路由实例
const router = createRouter({ // 创建路由器
  history: createWebHistory(), // 使用HTML5历史模式
  routes, // 挂载路由表
}); // 路由器创建结束

// 全局前置守卫：在每次路由跳转前执行
router.beforeEach((to, from, next) => { // 注册全局前置守卫
  const requiresAuth = to.meta?.requiresAuth; // 读取目标路由的鉴权标记
  const token = localStorage.getItem('token'); // 从本地存储读取登录令牌

  if (requiresAuth && !token) { // 如果目标路由需要鉴权且没有令牌
    next({ path: '/login', query: { redirect: to.fullPath } }); // 重定向到登录页，并附带重定向回来的路径
  } else { // 其他情况放行
    next(); // 继续路由导航
  } // 条件分支结束
}); // 守卫注册结束

export default router; // 导出路由实例供应用使用
