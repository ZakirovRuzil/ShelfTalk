<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { errorMessage } from '../api/client'

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
  try { await auth.login({ email: email.value, password: password.value }); await router.push('/') }
  catch (cause) { error.value = errorMessage(cause) }
  finally { busy.value = false }
}
</script>

<template>
  <section class="auth-layout">
    <div class="auth-intro"><p class="eyebrow">YOUR NEXT CHAPTER</p><h1>Good books.<br />Better conversations.</h1><p>Come back to your shelf and share what stayed with you.</p><span class="auth-decoration" aria-hidden="true">“</span></div>
    <form class="panel auth-form" @submit.prevent="submit">
      <h2>Welcome back</h2><p class="muted">Log in to share your thoughts.</p>
      <p v-if="route.query.registered" class="message success" role="status">Your account is ready. You can log in now.</p>
      <p v-if="error" class="message error" role="alert">{{ error }}</p>
      <label for="email">Email</label><input id="email" v-model="email" type="email" autocomplete="email" required maxlength="254" />
      <label for="password">Password</label><input id="password" v-model="password" type="password" autocomplete="current-password" required />
      <button class="button" :disabled="busy">{{ busy ? 'Logging in…' : 'Log in' }} <span aria-hidden="true">→</span></button>
      <p class="form-foot">New here? <RouterLink to="/register">Create an account</RouterLink></p>
    </form>
  </section>
</template>
