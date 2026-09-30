import { createRouter, createWebHistory } from 'vue-router'
import BooksView from '../views/BooksView.vue'
import BookDetailView from '../views/BookDetailView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'

/**
 * Роутер приложения. Маршруты не защищены на этом уровне: страницы, которым
 * нужен вход (например, форма отзыва в BookDetailView), сами проверяют
 * `auth.isAuthenticated` и показывают гостю приглашение войти вместо формы.
 * Неизвестные пути редиректятся на каталог.
 */
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
