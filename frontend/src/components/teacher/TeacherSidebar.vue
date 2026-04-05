<template>
  <aside class="teacher-sidebar" :class="{ collapsed }">
    <template v-if="!collapsed">
      <div class="sidebar-header">
        <span>管理员查看菜单</span>
      </div>

      <div class="sidebar-group">
        <div class="group-title">老师列表</div>
        <div
          v-for="item in teacherList"
          :key="item.id"
          class="sidebar-item"
          :class="{ active: selectedUser?.id === item.id }"
          @click="$emit('select-user', item)"
        >
          {{ item.label }}
        </div>
      </div>

      <div class="sidebar-group">
        <div class="group-title">学生列表</div>
        <div
          v-for="item in studentList"
          :key="item.id"
          class="sidebar-item"
          :class="{ active: selectedUser?.id === item.id }"
          @click="$emit('select-user', item)"
        >
          {{ item.label }}
        </div>
      </div>
    </template>

    <template v-else>
      <div class="collapsed-content">
        <span class="vertical-text">用户菜单栏</span>
      </div>
    </template>

    <div class="toggle-btn" @click="$emit('toggle')">
      {{ collapsed ? '▶' : '◀' }}
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useTeacherViewStore } from '@/stores/teacherView'

const router = useRouter()
const teacherViewStore = useTeacherViewStore()

const teacherUser = computed(() => teacherViewStore.teacherUser)
const selectedUser = computed(() => teacherViewStore.selectedUser)
const userList = computed(() => teacherViewStore.userList || [])

const props = defineProps({
  collapsed: Boolean,
  selectedUser: Object,
  userList: {
    type: Array,
    default: () => []
  }
})

defineEmits(['toggle', 'select-user'])

const teacherList = computed(() =>
  props.userList.filter(item => item.role === 'teacher')
)

const studentList = computed(() =>
  props.userList.filter(item => item.role === 'student')
)
</script>

<style scoped>
.teacher-sidebar {
  position: fixed;
  left: 0;
  top: 64px; /* 避开 AppHeader 的高度 */
  bottom: 0;
  z-index: 2000; /* 确保在最上层 */

  width: 260px;
  background: #fff;
  border-right: 1px solid #b3b3b3;
  border-top: 1px solid #b3b3b3;
  border-bottom: 1px solid #b3b3b3;
  box-shadow: 4px 0 12px rgba(0,0,0,0.05); /* 添加阴影增加悬浮感 */
  transition: transform 0.5s ease, width 0.5s ease;

  display: flex;
  flex-direction: column;
}

.teacher-sidebar.collapsed {
  /*transform: translateX(-220px);*/
  background: #bbbbbb;
  border-right: 1px solid #999999;
  border-top: 1px solid #999999;
  border-bottom: 1px solid #999999;
  width: 40px; 
}

.sidebar-header {
  padding: 18px;
  font-size: 20px;
  font-weight: 600;
  border-bottom: 1px solid #eee;
  white-space: nowrap;
}

/* 缩进后的垂直文字容器 */
.collapsed-content {
  flex: 1;
  display: flex;
  align-items: center; /* 垂直居中 */
  justify-content: center; /* 水平居中 */
}

/* 垂直文字样式 [对应图片：老师端侧边栏缩小--主页.jpg] */
.vertical-text {
  writing-mode: vertical-rl;
  text-orientation: mixed;
  letter-spacing: 30px;
  font-size: 20px;
  color: #333;
}

.sidebar-group {
  padding: 12px 0;
}

.group-title {
  padding: 8px 18px;
  color: #666;
  font-size: 18px;
}

.sidebar-item {
  padding: 12px 18px;
  cursor: pointer;
  font-size: 16px;
}

.sidebar-item:hover {
  background: #f5f7fa;
}

.sidebar-item.active {
  background: #4f78ff;
  color: #fff;
}

.toggle-btn {
  position: absolute;
  right: -19px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 120px;
  background: #fff;
  border-radius: 0 25px 25px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: rgb(226, 226, 226) solid 1px;
  box-shadow: 3px 0 4px rgba(0,0,0,0.25);
}
</style>