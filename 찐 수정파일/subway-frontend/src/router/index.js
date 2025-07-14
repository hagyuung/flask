import Vue from 'vue'
import VueRouter from 'vue-router'
import LoginView from '@/LoginView.vue'
import Dashboard from '@/Dashboard.vue'

// Vue.use(VueRouter)는 main.js에서 처리하므로 여기엔 없어야 합니다.

const routes = [
  {
    path: '/',
    name: 'login',
    component: LoginView
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: Dashboard
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
