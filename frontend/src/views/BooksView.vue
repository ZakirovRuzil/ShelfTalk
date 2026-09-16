<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { getBooks } from '../api/books'
import { errorMessage } from '../api/client'
import BookCard from '../components/BookCard.vue'
import type { Book } from '../types'

const books = ref<Book[]>([])
const search = ref('')
const loading = ref(true)
const error = ref('')
const filteredBooks = computed(() => {
  const query = search.value.trim().toLowerCase()
  return books.value.filter((book) =>
    `${book.title} ${book.author}`.toLowerCase().includes(query),
  )
})
async function load() {
  loading.value = true
  error.value = ''
  try {
    books.value = await getBooks()
  } catch (cause) {
    error.value = errorMessage(cause)
  } finally {
    loading.value = false
  }
}
onMounted(load)
</script>

<template>
  <section class="hero">
    <div>
      <p class="eyebrow">A HOME FOR YOUR NEXT GREAT READ</p>
      <h1>
        A little shelf.
        <br />
        <em>A lot to say.</em>
      </h1>
      <p class="hero-description">
        Explore timeless stories, find a new perspective,
        <br class="desktop-break" />
        and share the books that stay with you.
      </p>
      <a
        href="#catalog"
        class="browse-link"
      >
        Explore the collection
        <span aria-hidden="true">↓</span>
      </a>
    </div>
    <div
      class="hero-art"
      aria-hidden="true"
    >
      <div class="sun"></div>
      <div class="illustrated-book book-one">
        <span>
          Stories
          <br />
          that stay.
        </span>
        <i>the ShelfTalk collection</i>
      </div>
      <div class="illustrated-book book-two">
        <span>
          ONE
          <br />
          MORE
          <br />
          CHAPTER
        </span>
      </div>
      <div class="shelf-line"></div>
      <span class="art-caption">OPEN A BOOK. START A CONVERSATION.</span>
    </div>
  </section>
  <section
    id="catalog"
    class="catalog"
  >
    <div class="section-heading">
      <div>
        <p class="eyebrow">THE COLLECTION</p>
        <h2>
          Find your next chapter
          <span
            v-if="!loading && !error"
            class="count"
          >
            {{ books.length }}
          </span>
        </h2>
      </div>
      <div class="search">
        <span aria-hidden="true">⌕</span>
        <label
          class="sr-only"
          for="search"
        >
          Search by title or author
        </label>
        <input
          id="search"
          v-model="search"
          type="search"
          placeholder="Search by title or author…"
        />
      </div>
    </div>
    <p
      v-if="loading"
      class="state"
      role="status"
    >
      Gathering the books…
    </p>
    <div
      v-else-if="error"
      class="state"
    >
      <p
        class="message error"
        role="alert"
      >
        {{ error }}
      </p>
      <button
        class="button secondary"
        @click="load"
      >
        Try again
      </button>
    </div>
    <div
      v-else-if="!books.length"
      class="state"
    >
      <h3>The shelf is waiting.</h3>
      <p>There are no books in the collection yet. Check back soon.</p>
    </div>
    <div
      v-else-if="!filteredBooks.length"
      class="state"
    >
      <h3>No books found.</h3>
      <p>Try another title or author.</p>
      <button
        class="text-button"
        @click="search = ''"
      >
        Clear search
      </button>
    </div>
    <div
      v-else
      class="book-grid"
    >
      <BookCard
        v-for="book in filteredBooks"
        :key="book.id"
        :book="book"
      />
    </div>
  </section>
</template>
