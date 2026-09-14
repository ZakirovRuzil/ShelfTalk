<script setup lang="ts">
import type { Review } from '../types'
defineProps<{ review: Review; owned: boolean; busy: boolean }>()
defineEmits<{ edit: []; delete: [] }>()
</script>

<template>
  <article class="review-item">
    <div class="review-heading"><div><strong>{{ review.author.display_name || 'Reader' }}</strong><span v-if="owned" class="you-badge">You</span><p class="review-date">{{ new Date(review.created_at).toLocaleDateString('en', { year: 'numeric', month: 'short', day: 'numeric' }) }}<span v-if="review.updated_at !== review.created_at"> · Edited</span></p></div><span class="rating-badge">★ {{ review.rating }} <small>/ 10</small></span></div>
    <p class="review-text">{{ review.text }}</p>
    <div v-if="owned" class="review-actions"><button class="text-button" :disabled="busy" @click="$emit('edit')">Edit review</button><button class="text-button danger" :disabled="busy" @click="$emit('delete')">Delete</button></div>
  </article>
</template>
