<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { errorMessage } from '../api/client'

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

<template>
  <section class="auth-layout">
    <div class="auth-intro">
      <p class="eyebrow">THERE’S ROOM ON THE SHELF</p>
      <h1>
        Every reader
        <br />
        has a perspective.
      </h1>
      <p>Find a familiar favorite. Discover something new. Tell us what you think.</p>
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
      <h2>Join the conversation</h2>
      <p class="muted">A small community starts with your next review.</p>
      <p
        v-if="error"
        class="message error"
        role="alert"
      >
        {{ error }}
      </p>
      <label for="name">Display name</label>
      <input
        id="name"
        v-model="displayName"
        autocomplete="nickname"
        required
        maxlength="80"
      />
      <small>This name will appear beside your reviews.</small>
      <label for="email">Email</label>
      <input
        id="email"
        v-model="email"
        type="email"
        autocomplete="email"
        required
        maxlength="254"
      />
      <label for="password">Password</label>
      <input
        id="password"
        v-model="password"
        type="password"
        autocomplete="new-password"
        minlength="8"
        required
        aria-describedby="password-help"
      />
      <small id="password-help">
        At least 8 characters. Avoid common or entirely numeric passwords.
      </small>
      <button
        class="button"
        :disabled="busy"
      >
        {{ busy ? 'Creating account…' : 'Create account' }}
        <span aria-hidden="true">→</span>
      </button>
      <p class="form-foot">
        Already a reader here?
        <RouterLink to="/login">Log in</RouterLink>
      </p>
    </form>
  </section>
</template>
