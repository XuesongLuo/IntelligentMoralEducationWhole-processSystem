<template>
  <div class="auth-container">
    <img class="auth-logo" src="@/assets/images/logo.png" alt="logo" />

    <div class="auth-section left-section">
      <div class="banner-box">
        <el-carousel
          trigger="click"
          arrow="never" 
          height="100%"
          :interval="5000"
        >
          <el-carousel-item v-for="(item, index) in bannerItems" :key="index">
            <div class="carousel-img-container">
              <img :src="item.src" class="shrinked-banner-img" :alt="'banner-' + index" />
            </div>
          </el-carousel-item>
        </el-carousel>
      </div>
    </div>

    <div class="auth-section right-section">
      <div class="form-content-wrapper">
        <slot>
          <div style="padding: 20px; background: #fafafa; border: 1px dashed #ccc;">
            <h3>登录表单插槽</h3>
            <p>屏幕变窄时，这里的宽度会从固定 70% 变为近乎占满。</p>
            <el-input placeholder="请输入账号" style="margin-bottom: 15px;"></el-input>
            <el-input placeholder="请输入密码" type="password" style="margin-bottom: 15px;"></el-input>
            <el-button type="primary" style="width: 100%; background-color: #8aba35; border-color: #8aba35;">登录</el-button>
          </div>
        </slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 示例数据，保持不变
const bannerItems = ref([
  { src: 'https://via.placeholder.com/600x400/8aba35/ffffff?text=Illustration+1', alt: 'Image 1' },
  { src: 'https://via.placeholder.com/600x400/8aba35/ffffff?text=Illustration+2', alt: 'Image 2' },
  { src: 'https://via.placeholder.com/600x400/8aba35/ffffff?text=Illustration+3', alt: 'Image 3' }
])
</script>

<style scoped>
/* ==============================
   1. 基础布局 (PC端, >1024px)
   ============================== */
.auth-container {
  display: flex;
  width: 100vw;
  height: 100vh;
  background-color: #fff;
  overflow: hidden; /* PC端防止滚动 */
  font-family: Arial, sans-serif;
  position: relative;
}

/* 共有 Section 样式 */
.auth-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* --- 左侧 Banner --- */
.left-section {
  flex: 4; /* 占据剩余空间 */
  justify-content: center; /* 垂直居中 banner-box */
  background-color: #ffffff; /* 淡淡的背景色区分 */
  padding: 40px; /* 增加内边距，防止 banner 贴边 */
}

/* 【核心】灰色背景框：实现等比例缩放的关键 */
.banner-box {
  width: 100%; /* 充满 left-section 的可用宽度 */
  max-width: 700px; /* 限制 PC 端最大宽度，防止变得太大 */
  
  /* 魔法属性：强制保持 4:3 的宽高比 */
  /* 当 flex 导致宽度缩小，高度会自动按比例缩小 */
  aspect-ratio: 4 / 3; 
  
  background: #f2f2f2;
  border-radius: 12px; /* 加点圆角更好看 */
  position: relative;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05); /* 加点阴影增强精致感 */
}

/* --- 右侧表单 --- */
.right-section {
  flex: 6; /* 左右对等 */
  justify-content: center; /* 表单垂直居中 */
  /* 移除原代码的 min-width: 800px，否则无法响应 */
  border-left: 1px solid #f0f0f0;
  min-width:720px;
  background-color: #fcfcfc;
}

/* 表单包裹容器 */
.form-content-wrapper {
  width: 70%; /* PC端表单在右侧区域占据 70% 宽度 */
  max-width: 680px; /* 限制最大宽度，防止输入框过长 */
  transition: width 0.3s ease; /* 宽度变化时加个过渡 */
}

/* --- Logo (PC端) --- */
.auth-logo {
  position: absolute;
  top: 40px;
  left: 40px;
  width: 140px; /* 稍微加大一点 Logo */
  z-index: 100;
  transition: all 0.3s ease;
}


/* ==============================
   2. 轮播图内部样式 (保持精致)
   ============================== */
:deep(.el-carousel) { height: 100%; width: 100%; }
:deep(.el-carousel__container) { height: 100% !important; width: 100%; }
:deep(.el-carousel__arrow) { display: none; } /* 隐藏箭头 */

.carousel-img-container {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10%; /* 使用百分比 padding，跟随缩放 */
}

.shrinked-banner-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain; /* 确保图片比例不失真且完整显示 */
}

/* 指示器样式，保持系统绿 */
:deep(.el-carousel__indicators) { bottom: 15px; }
:deep(.el-carousel__button) { width: 8px; height: 8px; border-radius: 50%; background-color: #d9d9d9; opacity: 1; }
:deep(.el-carousel__indicator.is-active button) { background-color: #8aba35; }


/* ==============================
   3. 【关键】响应式布局 (iPad Pro 以下, <=1024px)
   ============================== */
@media (max-width: 1024px) {
  .auth-container {
    flex-direction: column; /* 【核心】由左右排版变为上下排版 */
    overflow-y: auto; /* 允许纵向滚动 */
    height: auto;
    min-height: 100vh;
  }

  /* --- Logo 在移动端的调整 --- */
  .auth-logo {
    position: relative; /* 取消绝对定位 */
    top: 0;
    left: 0;
    margin: 30px auto 10px auto; /* 居中显示，调整间距 */
    width: 120px;
    display: block;
  }

  /* --- Banner (移动端在上) --- */
  .left-section {
    flex: none; /* 取消 flex:1 */
    width: 100%;
    padding: 20px 20px; /* 减少上下间距 */
    background-color: #fff; /* 取消背景色，保持整体白色 */
    box-sizing: border-box;
    display: flex;
    justify-content: center; /* 水平居中 */
    align-items: center;
  }

  .banner-box {
    /* 这里无需修改宽高，aspect-ratio 会自动根据此时 100% 的屏幕宽度计算高度 */
    width: 100%; 
    max-width: 500px; /* 在平板/手机上限制最大宽度，不要撑太满 */
    box-shadow: none; /* 移动端可以考虑去掉阴影，保持扁平 */
    border: 1px solid #f0f0f0;
  }

  /* --- 表单 (移动端在下) --- */
  .right-section {
    flex: none;
    width: 100%;
    min-width: 0 !important;
    border-left: none; /* 去掉中间分割线 */
    justify-content: flex-start; /* 顶部对齐，靠 banner 紧一点 */
    padding: 20px 0 50px 0; /* 底部留白，防止顶到屏幕边缘 */
  }

  .form-content-wrapper {
    /* 【核心】修改登录表单大小 */
    width: 95%; /* 在移动端，表单应该占据更宽的比例，方便手指点击 */
    max-width: 400px; /* 移动端不要宽于 400px，否则显得松散 */
    padding: 0;
    margin: 0 auto;
  }
}

/* 针对小屏幕手机的额外微调 */
@media (max-width: 480px) {
  .left-section { padding: 15px 20px; } /* 进一步减少 Banner 贴边 */
  .form-content-wrapper { width: 90%; } /* 几乎占满 */
  .auth-logo { width: 100px; margin-top: 20px; }
}
</style>