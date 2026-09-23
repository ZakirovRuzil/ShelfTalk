<template>
    <section class="auth-layout">
        <div class="auth-intro">
            <p class="eyebrow">{{ t('register.eyebrow') }}</p>
            <h1>
                {{ t('register.titleLine1') }}
                <br />
                {{ t('register.titleLine2') }}
            </h1>
            <p>{{ t('register.intro') }}</p>
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
            <h2>{{ t('register.formTitle') }}</h2>
            <p class="muted">{{ t('register.formSubtitle') }}</p>
            <p
                v-if="error"
                class="message error"
                role="alert"
            >
                {{ error }}
            </p>
            <label for="name">{{ t('register.displayName') }}</label>
            <input
                id="name"
                v-model="displayName"
                autocomplete="nickname"
                required
                maxlength="80"
            />
            <small>{{ t('register.displayNameHelp') }}</small>
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
                autocomplete="new-password"
                minlength="8"
                required
                aria-describedby="password-help"
            />
            <small id="password-help">{{ t('register.passwordHelp') }}</small>
            <button
                class="button"
                :disabled="busy"
            >
                {{ busy ? t('register.submitting') : t('register.submit') }}
                <span aria-hidden="true">→</span>
            </button>
            <p class="form-foot">
                {{ t('register.haveAccount') }}
                <RouterLink to="/login">{{ t('register.login') }}</RouterLink>
            </p>
        </form>
    </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { errorMessage } from '../api/client'
import { t } from '../i18n'

const auth = useAuthStore()
const router = useRouter()
const email = ref('')
const displayName = ref('')
const password = ref('')
const busy = ref(false)
const error = ref('')
async function submit() {
    busy.value = true
    error.value = ''
    try {
        await auth.register({
            email: email.value,
            display_name: displayName.value,
            password: password.value,
        })
        await router.push('/login?registered=1')
    } catch (cause) {
        error.value = errorMessage(cause)
    } finally {
        busy.value = false
    }
}
</script>
