<template>
    <header class="site-header">
        <nav
            class="container navbar"
            aria-label="Main navigation"
        >
            <RouterLink
                to="/"
                class="brand"
            >
                <span
                    class="brand-mark"
                    aria-hidden="true"
                >
                    st.
                </span>
                ShelfTalk
            </RouterLink>
            <RouterLink
                to="/"
                class="nav-books"
            >
                Books
            </RouterLink>
            <div class="nav-account">
                <template v-if="auth.isAuthenticated">
                    <span class="user-name">{{ auth.user?.display_name }}</span>
                    <button
                        class="button secondary small"
                        @click="auth.logout"
                    >
                        Log out
                    </button>
                </template>
                <template v-else>
                    <RouterLink
                        to="/login"
                        class="nav-login"
                    >
                        Log in
                    </RouterLink>
                    <RouterLink
                        to="/register"
                        class="button small"
                    >
                        Join ShelfTalk
                        <span aria-hidden="true">↗</span>
                    </RouterLink>
                </template>
            </div>
        </nav>
    </header>
</template>

<script setup lang="ts">
import { useAuthStore } from '../stores/auth'
const auth = useAuthStore()
</script>
