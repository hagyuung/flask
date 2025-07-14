<template>
  <div class="container">
    <!-- 좌측 메뉴 -->
    <aside class="sidebar">
      <h2 class="logo">🚇 서울 지하철 관제</h2>
      <ul>
        <li
          v-for="item in menuItems"
          :key="item.name"
          :class="{ active: category === item.name }"
          @click="setCategory(item.name)"
        >
          {{ item.label }}
        </li>
      </ul>
    </aside>

    <!-- 메인 -->
    <main class="main">
      <header class="topbar">
        <h1>{{ topbarTitle }}</h1>
        <button @click="logout">로그아웃</button>
      </header>

      <!-- 실시간 알림 -->
      <section class="alerts" v-if="!category">
        <h3>🚨 실시간 경고 알림</h3>
        <ul>
          <!-- 이제 filteredAlerts를 사용해 필터링된 알림만 보여줍니다 -->
          <li v-for="(alert, idx) in filteredAlerts" :key="idx">
            <span class="time">{{ formatTime(alert.alarm["@timestamp"]) }}</span>
            <span class="status">{{ alert.alarm["상태"] }}</span>
            <span class="location">{{ alert.alarm["위치"] }}</span>
            <span class="desc">
              [{{ alert.alarm["equipment_id"] }}]
              {{ alert.alarm["시설"] }} - {{ alert.alarm["이벤트"] }}
            </span>
          </li>
        </ul>
      </section>

      <!-- Kibana 대시보드 -->
      <section class="dashboard" v-else>
        <iframe
          :src="dashboardUrl"
          frameborder="0"
          width="100%"
          height="100%"
        ></iframe>
      </section>
    </main>
  </div>
</template>

<script>
export default {
  data() {
    return {
      userDepartment: null,
      category: null,
      alerts: [], // 웹소켓에서 오는 모든 알림을 저장
      socket: null,
      departmentMap: {
        // 'control' 항목은 로직 처리를 위해 반드시 필요합니다.
        'control': { label: '종합', url: 'http://192.168.56.1:5601/goto/OVERALL_DASHBOARD_ID', team: null },
        'fire': { label: '소방', url: 'http://192.168.56.1:5601/goto/2b6e15b0-5e1e-11f0-b853-af82cbb5aa36', team: 'fire_safety_team' },
        'electrical': { label: '전기', url: 'http://192.168.56.1:5601/goto/3a5ba600-5e1e-11f0-b853-af82cbb5aa36', team: 'electrical_team' },
        'telecom': { label: '통신', url: 'http://192.168.56.1:5601/goto/40bf6400-5e1e-11f0-b853-af82cbb5aa36', team: 'communication_team' },
      }
    };
  },
  computed: {
    // 로그인한 사용자의 부서에 따라 메뉴를 동적으로 생성
    menuItems() {
      const items = [{ name: null, label: "실시간 알림" }];
      
      if (this.userDepartment === 'control') {
        // 'control' 사용자는 '종합 관제'를 제외한 모든 부서의 대시보드 메뉴를 봅니다.
        Object.keys(this.departmentMap).forEach(deptKey => {
           if (deptKey !== 'control') { // 'control' 메뉴는 건너뜁니다.
             items.push({ name: deptKey, label: this.departmentMap[deptKey].label });
           }
        });
      } else if (this.departmentMap[this.userDepartment]) {
        // 다른 부서 사용자는 자신의 대시보드 메뉴만 봅니다.
        const deptInfo = this.departmentMap[this.userDepartment];
        items.push({ name: this.userDepartment, label: deptInfo.label });
      }
      return items;
    },
    // 부서에 따라 실시간 알림을 필터링
    filteredAlerts() {
      if (this.userDepartment === 'control') {
        return this.alerts;
      }
      const userTeam = this.departmentMap[this.userDepartment]?.team;
      if (userTeam) {
        return this.alerts.filter(alert => alert.alarm.team === userTeam);
      }
      return [];
    },
    topbarTitle() {
      if (this.category) {
        return this.departmentMap[this.category]?.label || "대시보드";
      }
      return "실시간 경고 알림";
    },
    dashboardUrl() {
      return this.departmentMap[this.category]?.url;
    },
  },
  created() {
    // localStorage에서 부서 정보를 가져올 때 공백을 제거합니다.
    const department = localStorage.getItem('user_department')?.trim();
    
    // departmentMap에 해당 부서 정보가 있는지 확인합니다.
    if (department && this.departmentMap[department]) {
      this.userDepartment = department;
      // 'control' 팀은 로그인 후 기본으로 '실시간 알림'을 보여줍니다.
      // category를 null로 유지합니다.
    } else {
      alert("부서 정보가 유효하지 않습니다. 다시 로그인해주세요.");
      this.$router.push('/');
    }
  },
  mounted() {
    const socket = new WebSocket('ws://192.168.56.1:8001/ws');
    socket.onopen = () => console.log('✅ WebSocket 연결됨');
    socket.onmessage = (event) => {
      const parsed = JSON.parse(event.data);
      if (parsed["상태"] !== "심각" && parsed["상태"] !== "경고") return;
      this.alerts.unshift({ alarm: parsed });
      if (this.alerts.length > 10) this.alerts.pop();
    };
    socket.onerror = (error) => console.error('❌ WebSocket 에러:', error);
    socket.onclose = () => console.log('❌ WebSocket 닫힘');
  },
  methods: {
    setCategory(cat) {
      this.category = cat;
    },
    formatTime(timestamp) {
      const date = new Date(timestamp);
      return date.toLocaleString("ko-KR", { hour12: false });
    },
    logout() {
      localStorage.removeItem('user_department');
      this.$router.push('/');
    },
  },
};
</script>

<style scoped>
/* 스타일은 이전과 동일합니다. */
.container { display: flex; height: 100vh; background-color: #f0f2f5; color: #222; }
.sidebar { width: 220px; background: #003366; color: #fff; padding: 1.5rem; }
.logo { font-size: 1.2rem; margin-bottom: 2rem; }
.sidebar ul { list-style: none; padding: 0; }
.sidebar li { padding: 0.75rem; margin-bottom: 0.3rem; cursor: pointer; border-radius: 4px; transition: background 0.2s; }
.sidebar li.active, .sidebar li:hover { background: #005599; }
.main { flex: 1; display: flex; flex-direction: column; }
.topbar { background: #fff; border-bottom: 2px solid #003366; padding: 1rem 1.5rem; display: flex; justify-content: space-between; align-items: center; }
.topbar h1 { font-size: 1.2rem; }
.topbar button { padding: 0.4rem 1rem; border: none; background: #005599; color: #fff; border-radius: 4px; cursor: pointer; }
.alerts { padding: 1.2rem 1.5rem; background: #fefefe; }
.alerts h3 { margin-bottom: 1rem; font-weight: bold; color: #c80000; }
.alerts ul { list-style: none; padding: 0; margin: 0; }
.alerts li { background: #ffeeee; margin-bottom: 8px; padding: 0.8rem; border-left: 4px solid #cc0000; border-radius: 4px; font-size: 0.92rem; display: flex; gap: 10px; align-items: center; }
.time { font-weight: bold; color: #555; width: 160px; }
.status { font-weight: bold; color: #c80000; width: 60px; }
.location { flex: 1; }
.desc { font-weight: 500; color: #222; }
.dashboard { flex: 1; background: #fff; padding: 1rem 1.5rem; }
</style>
