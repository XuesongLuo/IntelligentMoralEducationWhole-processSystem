import { defineStore } from 'pinia'

export const useTeacherViewStore = defineStore('teacherView', {
  state: () => ({
    sidebarCollapsed: false,
    teacherUser: null,
    selectedUser: null,
    userList: []
  }),

  getters: {
    isViewingSelf(state) {
      if (!state.teacherUser || !state.selectedUser) return false
      return state.teacherUser.id === state.selectedUser.id
    }
  },

  actions: {
    persist() {
      localStorage.setItem(
        'teacherViewState',
        JSON.stringify({
          teacherUser: this.teacherUser,
          selectedUser: this.selectedUser,
          userList: this.userList,
          sidebarCollapsed: this.sidebarCollapsed
        })
      )
    },

    restore() {
      const cache = JSON.parse(localStorage.getItem('teacherViewState') || '{}')
      this.teacherUser = cache.teacherUser || null
      this.selectedUser = cache.selectedUser || null
      this.userList = cache.userList || []
      this.sidebarCollapsed = cache.sidebarCollapsed || false
    },

    init(teacherUser, userList = []) {
      this.teacherUser = teacherUser
      this.selectedUser = teacherUser
      this.userList = userList
      this.persist()
    },

    selectUser(user) {
      this.selectedUser = user
      this.persist()
    },

    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
      this.persist()
    },
    reset() {
      this.sidebarCollapsed = false
      this.teacherUser = null
      this.selectedUser = null
      this.userList = []
      localStorage.removeItem('teacherViewState')
    }
  }
})