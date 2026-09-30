<template>
    <header class="site-header">
        <nav
            class="container navbar"
            :aria-label="t('nav.label')"
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
                {{ t('nav.books') }}
            </RouterLink>
            <div class="nav-account">
                <div
                    class="lang-switch"
                    role="group"
                    :aria-label="t('nav.language')"
                >
                    <button
                        v-for="code in locales"
                        :key="code"
                        type="button"
                        :lang="code"
                        :aria-pressed="code === locale"
                        @click="setLocale(code)"
                    >
                        {{ code.toUpperCase() }}
                    </button>
                </div>
                <template v-if="auth.isAuthenticated">
                    <span class="user-name">{{ auth.user?.display_name }}</span>
                    <button
                        class="button secondary small"
                        @click="auth.logout"
                    >
                        {{ t('nav.logout') }}
                    </button>
                </template>
                <template v-else>
                    <RouterLink
                        to="/login"
                        class="nav-login"
                    >
                        {{ t('nav.login') }}
                    </RouterLink>
                    <RouterLink
                        to="/register"
                        class="button small"
                    >
                        {{ t('nav.join') }}
                        <span aria-hidden="true">↗</span>
                    </RouterLink>
                </template>
            </div>
        </nav>
    </header>
</template>

<!-- Шапка сайта: бренд, ссылка на каталог, переключатель языка и блок входа/аккаунта. -->
<script setup lang="ts">
import { useAuthStore } from '../stores/auth'
import { locale, locales, setLocale, t } from '../i18n'
const auth = useAuthStore()
</script>
