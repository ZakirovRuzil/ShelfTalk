<script setup lang="ts">
import { onMounted, ref } from 'vue'
import AppNavbar from './components/AppNavbar.vue'
import { useAuthStore } from './stores/auth'
import { errorMessage } from './api/client'

const auth = useAuthStore()
const ready = ref(false)
const error = ref('')
onMounted(async () => {
  try { await auth.fetchCurrentUser() }
  catch (cause) { error.value = errorMessage(cause) }
  finally { ready.value = true }
})
</script>

<template>
  <a class="skip-link" href="#main">Skip to content</a>
  <AppNavbar />
  <main id="main" class="container">
    <p v-if="error" role="alert" class="message error">{{ error }} <button class="text-button" @click="error = ''">Dismiss</button></p>
    <RouterView v-if="ready" :key="$route.path" />
    <p v-else class="state" role="status">Opening your shelf…</p>
  </main>
  <footer class="container footer"><span>ShelfTalk</span><p>A little shelf. A lot to say.</p><span>Made for the love of reading.</span></footer>
</template>
