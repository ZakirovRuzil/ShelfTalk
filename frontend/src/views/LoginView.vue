<template>
    <section class="auth-layout">
        <div class="auth-intro">
            <p class="eyebrow">{{ t('login.eyebrow') }}</p>
            <h1>
                {{ t('login.titleLine1') }}
                <br />
                {{ t('login.titleLine2') }}
            </h1>
            <p>{{ t('login.intro') }}</p>
            <span
                class="auth-decoration"
                aria-hidden="true"
            >
                “
            </span>
        </div>
        <form
            class="panel auth-form"
            @submit.prevent="submit"
        >
            <h2>{{ t('login.formTitle') }}</h2>
            <p class="muted">{{ t('login.formSubtitle') }}</p>
            <p
                v-if="route.query.registered"
                class="message success"
                role="status"
            >
                {{ t('login.registered') }}
            </p>
            <p
                v-if="error"
                class="message error"
                role="alert"
            >
                {{ error }}
            </p>
            <label for="email">{{ t('common.email') }}</label>
            <input
                id="email"
                v-model="email"
                type="email"
                autocomplete="email"
                required
                maxlength="254"
            />
            <label for="password">{{ t('common.password') }}</label>
            <input
                id="password"
                v-model="password"
                type="password"
                autocomplete="current-password"
                required
            />
            <button
                class="button"
                :disabled="busy"
            >
                {{ busy ? t('login.submitting') : t('login.submit') }}
                <span aria-hidden="true">→</span>
            </button>
            <p class="form-foot">
                {{ t('common.newHere') }}
                <RouterLink to="/register">{{ t('login.createAccount') }}</RouterLink>
            </p>
        </form>
    </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { errorMessage } from '../api/client'
import { t } from '../i18n'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const email = ref('')
const password = ref('')
const busy = ref(false)
const error = ref('')
async function submit() {
    busy.value = true
    error.value = ''
    try {
        await auth.login({ email: email.value, password: password.value })
        await router.push('/')
    } catch (cause) {
        error.value = errorMessage(cause)
    } finally {
        busy.value = false
    }
}
</script>
