import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { createPinia } from 'pinia'


const app = createApp(App) // 1. 先创建实例

// 2. 循环注册图标 (这一步必须在 createApp 之后，mount 之前)
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(router)
app.use(ElementPlus) // 3. 别忘了安装 ElementPlus
app.use(createPinia())
app.mount('#app')     // 4. 最后再挂载