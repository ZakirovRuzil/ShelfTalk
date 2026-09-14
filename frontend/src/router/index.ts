import { createRouter, createWebHistory } from 'vue-router'
import BooksView from '../views/BooksView.vue'
import BookDetailView from '../views/BookDetailView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: BooksView },
    { path: '/books/:id', component: BookDetailView },
    { path: '/login', component: LoginView },
    { path: '/register', component: RegisterView },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
  scrollBehavior: () => ({ top: 0 }),
})
