<template>
    <div class="auth-page">
        <div class="auth-page__left">
        <img class="auth-page__logo" src="@/assets/images/logo.png" alt="logo" />

        <div class="auth-page__banner">
            <img
                class="auth-page__banner-image"
                src="@/assets/images/auth-banner.png"
                alt="banner"
            />

            <div class="auth-page__dots">
                <span class="dot active"></span>
                <span class="dot"></span>
            </div>
        </div>
        </div>

        <div class="auth-page__right">
            <div class="auth-card">
                <slot />
            </div>
        </div>
    </div>
</template>

<style scoped>
.auth-page {
    min-height: 100vh;
    display: flex;
    background-color: #fff; /* 根据原图背景为白色 */
    overflow: hidden;
}

.auth-page__left {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    position: relative;


}
.auth-page__right {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
}

.auth-page__left {
  position: relative;
  flex-direction: column;
}

.auth-page__logo {
  position: absolute;
  top: 60px;
  left: 80px;
  width: 160px;
  object-fit: contain;
}

.auth-page__banner {
  width: 80%;           
  height: 70%;
  background: #f2f2f2;
  display: flex;
  align-items: center;
  justify-content: center;
}

.auth-page__banner-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.auth-page__dots {
  position: absolute;
  bottom: 12px;
  display: flex;
  gap: 10px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #cfcfcf;
}

.dot.active {
  background: #333;
}

.auth-card {
  width: 80%;
  min-height: 720px;
  background: #fff;
  border: 1px solid #d9d9d9;
  padding: 40px 100px;  /* 增加内边距 */
  box-sizing: border-box;
}

@media (max-width: 1200px) {
  .auth-page {
    flex-direction: column;
  }

  .auth-page__left,
  .auth-page__right {
    width: 100%;
  }

  .auth-page__left {
    padding-top: 100px;
    padding-bottom: 30px;
  }

  .auth-page__logo {
    left: 24px;
  }

  .auth-card {
    width: min(92vw, 660px);
    padding: 24px;
  }

  .auth-page__banner {
    width: min(92vw, 430px);
  }
}
</style>