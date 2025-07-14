module.exports = {
  // 이 설정이 Vue 2와 최신 개발 도구의 호환성 문제를 해결하는 핵심입니다.
  configureWebpack: {
    resolve: {
      alias: {
        'vue$': 'vue/dist/vue.esm.js'
      }
    }
  }
}
