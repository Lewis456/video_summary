<template>
  <!-- 使用keep-alive缓存组件，保持状态 -->
  <router-view v-slot="{ Component, route }">
    <keep-alive :include="['Main']">
      <component :is="Component" v-if="Component" />
    </keep-alive>
  </router-view>
</template>
