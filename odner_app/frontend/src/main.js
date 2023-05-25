import Vue from 'vue' // Importing Vue library
import App from './App.vue' // Importing the root component of the application

Vue.config.productionTip = false // Disable production tip in Vue

new Vue({
  render: h => h(App), // Rendering the root component
}).$mount('#app') // Mounting the Vue instance to the DOM element with the ID 'app'
