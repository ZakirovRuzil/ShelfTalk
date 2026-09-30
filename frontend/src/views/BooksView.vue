<template>
    <section class="hero">
        <div>
            <p class="eyebrow">{{ t('books.eyebrow') }}</p>
            <h1>
                {{ t('books.titleLine1') }}
                <br />
                <em>{{ t('books.titleLine2') }}</em>
            </h1>
            <p class="hero-description">
                {{ t('books.descriptionLine1') }}
                <br class="desktop-break" />
                {{ t('books.descriptionLine2') }}
            </p>
            <a
                href="#catalog"
                class="browse-link"
            >
                {{ t('books.explore') }}
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
                    {{ t('books.artBookOneLine1') }}
                    <br />
                    {{ t('books.artBookOneLine2') }}
                </span>
                <i>{{ t('books.artBookOneCaption') }}</i>
            </div>
            <div class="illustrated-book book-two">
                <span>
                    <template
                        v-for="(word, index) in t('books.artBookTwo').split(' ')"
                        :key="index"
                    >
                        <br v-if="index" />
                        {{ word }}
                    </template>
                </span>
            </div>
            <div class="shelf-line"></div>
            <span class="art-caption">{{ t('books.artCaption') }}</span>
        </div>
    </section>
    <section
        id="catalog"
        class="catalog"
    >
        <div class="section-heading">
            <div>
                <p class="eyebrow">{{ t('books.collectionEyebrow') }}</p>
                <h2>
                    {{ t('books.collectionTitle') }}
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
                    {{ t('books.searchLabel') }}
                </label>
                <input
                    id="search"
                    v-model="search"
                    type="search"
                    :placeholder="t('books.searchPlaceholder')"
                />
            </div>
        </div>
        <p
            v-if="loading"
            class="state"
            role="status"
        >
            {{ t('books.loading') }}
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
                {{ t('common.tryAgain') }}
            </button>
        </div>
        <div
            v-else-if="!books.length"
            class="state"
        >
            <h3>{{ t('books.emptyTitle') }}</h3>
            <p>{{ t('books.emptyText') }}</p>
        </div>
        <div
            v-else-if="!filteredBooks.length"
            class="state"
        >
            <h3>{{ t('books.notFoundTitle') }}</h3>
            <p>{{ t('books.notFoundText') }}</p>
            <button
                class="text-button"
                @click="search = ''"
            >
                {{ t('books.clearSearch') }}
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

<!-- Главная страница: список книг с клиентским поиском по названию/автору. -->
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { getBooks } from '../api/books'
import { errorMessage } from '../api/client'
import BookCard from '../components/BookCard.vue'
import { t } from '../i18n'
import type { Book } from '../types'

const books = ref<Book[]>([])
const search = ref('')
const loading = ref(true)
const error = ref('')
// Поиск выполняется на клиенте по уже загрученному списку (API его не
// поддерживает и не пагинирует — см. docs/API.md), поэтому годится только
// для небольшого каталога.
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
