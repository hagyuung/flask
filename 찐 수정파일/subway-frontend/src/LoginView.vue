<template>
  <div class="login-page">
    <div class="login-box">
      <h2 class="logo">🚇 서울 지하철 관제</h2>
      <div class="form-group">
        <input v-model="username" type="text" placeholder="사번 (8자리)" @keyup.enter="login"/>
      </div>
      <div class="form-group">
        <input v-model="password" type="password" placeholder="비밀번호" @keyup.enter="login"/>
      </div>
      <p v-if="error" class="error-message">{{ error }}</p>
      <button @click="login">로그인</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'LoginView',
  data() {
    return {
      username: '',
      password: '',
      error: ''
    }
  },
  methods: {
    async login() {
      try {
        const res = await axios.post('http://192.168.56.1:5000/api/login', {
          username: this.username,
          password: this.password
        });

        // --- 여기를 수정하세요! ---
        // 로그인 성공 응답에 'department' 정보가 있는지 확인합니다.
        if (res.status === 200 && res.data.department) {
          // 부서 정보를 브라우저의 localStorage에 저장합니다.
          localStorage.setItem('user_department', res.data.department);
          
          // 대시보드 페이지로 이동합니다.
          this.$router.push('/dashboard');
        } else {
          // 부서 정보가 없는 경우 에러 처리
          this.error = "로그인에 성공했으나 부서 정보가 없습니다.";
        }
      } catch (err) {
        if (err.response && err.response.data && err.response.data.message) {
          this.error = err.response.data.message;
        } else {
          this.error = '로그인 실패. 서버 또는 네트워크 연결을 확인하세요.';
        }
      }
    }
  }
}
</script>

<style scoped>
/* 스타일은 이전과 동일합니다. */
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #003366;
  font-family: "Nanum Gothic", sans-serif;
}
.login-box {
  width: 400px;
  padding: 40px;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  text-align: center;
}
.logo {
  font-size: 1.8rem;
  margin-bottom: 30px;
}
input {
  width: 100%;
  padding: 12px 15px;
  margin-bottom: 20px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}
button {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 4px;
  background-color: #005599;
  color: white;
  font-weight: bold;
  cursor: pointer;
}
.error-message {
  color: #d93025;
  margin-top: -10px;
  margin-bottom: 15px;
  min-height: 1.2em;
}
</style>
