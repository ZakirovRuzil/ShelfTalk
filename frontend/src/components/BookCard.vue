<script setup lang="ts">
import type { Book } from '../types'
defineProps<{ book: Book }>()
</script>

<template>
  <RouterLink :to="`/books/${book.id}`" class="book-card">
    <div class="book-cover" :class="`cover-${book.id % 4}`" aria-hidden="true">
      <span class="cover-edition">THE SHELFTALK LIBRARY</span>
      <span class="cover-title">{{ book.title }}</span>
      <span class="cover-ornament">✳</span>
      <span class="cover-author">{{ book.author }}</span>
    </div>
    <div class="book-info"><p class="book-year">{{ book.publication_year ?? 'Year unknown' }}</p><h3>{{ book.title }}</h3><p class="muted">{{ book.author }}</p>
      <div class="book-rating"><span><span class="star" aria-hidden="true">★</span> {{ book.average_rating === null ? 'Not rated' : `${book.average_rating.toFixed(1)} / 10` }}</span><span>{{ book.reviews_count }} {{ book.reviews_count === 1 ? 'review' : 'reviews' }}</span></div>
    </div>
  </RouterLink>
</template>
