<template>
    <a
        class="skip-link"
        href="#main"
    >
        {{ t('app.skipLink') }}
    </a>
    <AppNavbar />
    <main
        id="main"
        class="container"
    >
        <p
            v-if="error"
            role="alert"
            class="message error"
        >
            {{ error }}
            <button
                class="text-button"
                @click="error = ''"
            >
                {{ t('app.dismiss') }}
            </button>
        </p>
        <RouterView
            v-if="ready"
            :key="$route.path"
        />
        <p
            v-else
            class="state"
            role="status"
        >
            {{ t('app.loading') }}
        </p>
    </main>
    <footer class="container footer">
        <span>ShelfTalk</span>
        <p>{{ t('app.footerTagline') }}</p>
        <span>{{ t('app.footerNote') }}</span>
    </footer>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import AppNavbar from './components/AppNavbar.vue'
import { useAuthStore } from './stores/auth'
import { errorMessage } from './api/client'
import { t } from './i18n'

const auth = useAuthStore()
const ready = ref(false)
const error = ref('')
onMounted(async () => {
    try {
        await auth.fetchCurrentUser()
    } catch (cause) {
        error.value = errorMessage(cause)
    } finally {
        ready.value = true
    }
})
</script>
