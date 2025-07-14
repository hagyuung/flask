import Vue from 'vue'
import App from './App.vue'
import router from './router'
import VueRouter from 'vue-router'

Vue.config.productionTip = false

// 라우터 플러그인을 사용하겠다고 Vue에 알려줍니다.
Vue.use(VueRouter)

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')
