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
              <img :src="item.src" class="shrinked-banner-img" :alt="item.alt || `banner-${index}`" />
            </div>
          </el-carousel-item>
        </el-carousel>
      </div>
    </div>

    <div class="auth-section right-section">
      <div class="form-content-wrapper">
        <slot>
          <div class="default-form">
            <h3>登录表单插槽</h3>
            <p>屏幕变窄时，这里的宽度会随布局自动收紧。</p>
            <el-input placeholder="请输入账号" style="margin-bottom: 15px;" />
            <el-input placeholder="请输入密码" type="password" style="margin-bottom: 15px;" />
            <el-button type="primary" class="default-btn">登录</el-button>
          </div>
        </slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const bannerItems = ref([
  { src: 'https://via.placeholder.com/600x400/8aba35/ffffff?text=Illustration+1', alt: 'Image 1' },
  { src: 'https://via.placeholder.com/600x400/8aba35/ffffff?text=Illustration+2', alt: 'Image 2' },
  { src: 'https://via.placeholder.com/600x400/8aba35/ffffff?text=Illustration+3', alt: 'Image 3' }
])
</script>

<style scoped>
.auth-container {
  display: flex;
  width: 100%;
  min-height: 100vh;
  background-color: #fff;
  overflow: hidden;
  font-family: Arial, sans-serif;
  position: relative;
  padding-inline: 20px;
}

.auth-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 0;
}

.left-section {
  flex: 4.2;
  justify-content: center;
  background-color: #fff;
  padding: 28px;
}

.banner-box {
  width: 100%;
  max-width: 680px;
  aspect-ratio: 4 / 3;
  background: #f2f2f2;
  border-radius: 12px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
}

.right-section {
  flex: 5.8;
  justify-content: center;
  border-left: 1px solid #f0f0f0;
  min-width: 0;
  background-color: #fcfcfc;
  padding-block: 24px;
}

.form-content-wrapper {
  width: min(68%, 620px);
  max-width: 680px;
  transition: width 0.3s ease;
}

.auth-logo {
  position: absolute;
  top: 32px;
  left: 32px;
  width: 136px;
  z-index: 100;
  transition: all 0.3s ease;
}

.default-form {
  padding: 20px;
  background: #fafafa;
  border: 1px dashed #ccc;
}

.default-btn {
  width: 100%;
  background-color: #8aba35;
  border-color: #8aba35;
}

:deep(.el-carousel) {
  height: 100%;
  width: 100%;
}

:deep(.el-carousel__container) {
  height: 100% !important;
  width: 100%;
}

:deep(.el-carousel__arrow) {
  display: none;
}

.carousel-img-container {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10%;
}

.shrinked-banner-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

:deep(.el-carousel__indicators) {
  bottom: 15px;
}

:deep(.el-carousel__button) {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #d9d9d9;
  opacity: 1;
}

:deep(.el-carousel__indicator.is-active button) {
  background-color: #8aba35;
}

@media (max-width: 1024px) {
  .auth-container {
    flex-direction: column;
    overflow-y: auto;
    min-height: 100vh;
    padding-inline: 0;
  }

  .auth-logo {
    position: relative;
    top: 0;
    left: 0;
    margin: 24px auto 8px;
    width: 116px;
    display: block;
  }

  .left-section {
    flex: none;
    width: 100%;
    padding: 18px 20px;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .banner-box {
    width: 100%;
    max-width: 500px;
    box-shadow: none;
    border: 1px solid #f0f0f0;
  }

  .right-section {
    flex: none;
    width: 100%;
    border-left: none;
    justify-content: flex-start;
    padding: 16px 0 40px;
  }

  .form-content-wrapper {
    width: min(94%, 420px);
    margin: 0 auto;
  }
}

@media (max-width: 480px) {
  .left-section {
    padding: 14px 16px;
  }

  .form-content-wrapper {
    width: calc(100% - 28px);
  }

  .auth-logo {
    width: 100px;
    margin-top: 18px;
  }
}
</style>
