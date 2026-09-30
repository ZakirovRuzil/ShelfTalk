<template>
    <RouterLink
        :to="`/books/${book.id}`"
        class="book-card"
    >
        <div
            class="book-cover"
            :class="`cover-${book.id % 4}`"
            aria-hidden="true"
        >
            <span class="cover-edition">{{ t('book.edition') }}</span>
            <span class="cover-title">{{ book.title }}</span>
            <span class="cover-ornament">✳</span>
            <span class="cover-author">{{ book.author }}</span>
        </div>
        <div class="book-info">
            <p class="book-year">
                {{ book.publication_year ?? t('book.yearUnknown') }}
            </p>
            <h3>{{ book.title }}</h3>
            <p class="muted">{{ book.author }}</p>
            <div class="book-rating">
                <span>
                    <span
                        class="star"
                        aria-hidden="true"
                    >
                        ★
                    </span>
                    {{
                        book.average_rating === null
                            ? t('book.notRated')
                            : t('common.outOfTen', {
                                  value: book.average_rating.toFixed(1),
                              })
                    }}
                </span>
                <span>
                    {{ t('book.reviews', { count: book.reviews_count }) }}
                </span>
            </div>
        </div>
    </RouterLink>
</template>

<!-- Карточка книги в сетке каталога (см. BooksView.vue). -->
<script setup lang="ts">
import type { Book } from '../types'
import { t } from '../i18n'
defineProps<{ book: Book }>()
</script>
