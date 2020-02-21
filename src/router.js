import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
import Api from './views/Api.vue'
import File from './views/File.vue'
import Theory from './views/Theory.vue'
import Config from './views/Config.vue'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/api',
      name: 'api',
      component: Api
    },
    {
      path: '/upload',
      name: 'uploadFile',
      component: File
    },
    {
      path: '/theory',
      name: 'theory',
      component: Theory
    },
    {
      path: '/config',
      name: 'config',
      component: Config
    }
  ]
})
