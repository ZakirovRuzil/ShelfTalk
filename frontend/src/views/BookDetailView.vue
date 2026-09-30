<template>
    <RouterLink
        class="back-link"
        to="/"
    >
        ← {{ t('detail.back') }}
    </RouterLink>
    <p
        v-if="loading"
        class="state"
        role="status"
    >
        {{ t('detail.loading') }}
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
    <template v-else-if="book">
        <section class="book-detail">
            <div
                class="book-cover detail-cover"
                :class="`cover-${book.id % 4}`"
                aria-hidden="true"
            >
                <span class="cover-edition">{{ t('book.edition') }}</span>
                <span class="cover-title">{{ book.title }}</span>
                <span class="cover-ornament">✳</span>
                <span class="cover-author">{{ book.author }}</span>
            </div>
            <div class="detail-copy">
                <p class="eyebrow">
                    {{
                        t('detail.eyebrow', {
                            year: book.publication_year ?? t('detail.yearUnknown'),
                        })
                    }}
                </p>
                <h1>{{ book.title }}</h1>
                <p class="detail-author">
                    {{ t('detail.byAuthor', { author: book.author }) }}
                </p>
                <div class="detail-rating">
                    <span class="rating-badge">
                        ★
                        {{
                            book.average_rating === null
                                ? t('book.notRated')
                                : t('common.outOfTen', {
                                      value: book.average_rating.toFixed(1),
                                  })
                        }}
                    </span>
                    <span class="muted">
                        {{ t('detail.readerReviews', { count: book.reviews_count }) }}
                    </span>
                </div>
                <h2>{{ t('detail.about') }}</h2>
                <p class="description">
                    {{ book.description || t('detail.noDescription') }}
                </p>
            </div>
        </section>
        <section class="reviews-section">
            <div class="section-heading">
                <div>
                    <p class="eyebrow">{{ t('detail.reviewsEyebrow') }}</p>
                    <h2>
                        {{ t('detail.reviewsTitle') }}
                        <span class="count">{{ reviews.length }}</span>
                    </h2>
                </div>
            </div>
            <p
                v-if="notice"
                class="message success"
                role="status"
            >
                {{ notice }}
            </p>
            <p
                v-if="actionError"
                class="message error"
                role="alert"
            >
                {{ actionError }}
            </p>
            <div class="reviews-layout">
                <div>
                    <p
                        v-if="!reviews.length"
                        class="panel empty-review"
                    >
                        {{ t('detail.noReviews') }}
                    </p>
                    <ReviewItem
                        v-for="review in reviews"
                        :key="review.id"
                        :review="review"
                        :owned="review.author.id === auth.user?.id"
                        :busy="busy"
                        @edit="startEdit"
                        @delete="removeReview"
                    />
                </div>
                <aside>
                    <form
                        v-if="auth.isAuthenticated && (!myReview || editing)"
                        class="panel review-form"
                        @submit.prevent="submit"
                    >
                        <h3>
                            {{
                                editing
                                    ? t('detail.formTitleEdit')
                                    : t('detail.formTitleNew')
                            }}
                        </h3>
                        <p class="muted">{{ t('detail.formSubtitle') }}</p>
                        <label for="rating">
                            {{ t('detail.yourRating') }}
                            <span class="muted">/ 10</span>
                        </label>
                        <select
                            id="rating"
                            v-model.number="rating"
                            :disabled="busy"
                        >
                            <option
                                v-for="value in 10"
                                :key="value"
                                :value="value"
                            >
                                {{ t('common.outOfTen', { value }) }}
                            </option>
                        </select>
                        <label for="review-text">{{ t('detail.yourReview') }}</label>
                        <textarea
                            id="review-text"
                            ref="textInput"
                            v-model="text"
                            rows="6"
                            required
                            :disabled="busy"
                            :placeholder="t('detail.reviewPlaceholder')"
                        ></textarea>
                        <button
                            class="button"
                            :disabled="busy"
                        >
                            {{
                                busy
                                    ? t('detail.saving')
                                    : editing
                                      ? t('detail.saveChanges')
                                      : t('detail.publish')
                            }}
                        </button>
                        <button
                            v-if="editing"
                            type="button"
                            class="text-button"
                            :disabled="busy"
                            @click="resetForm"
                        >
                            {{ t('common.cancel') }}
                        </button>
                    </form>
                    <div
                        v-else-if="auth.isAuthenticated"
                        class="panel"
                    >
                        <p class="eyebrow">{{ t('detail.doneEyebrow') }}</p>
                        <h3>{{ t('detail.doneTitle') }}</h3>
                        <p class="muted">
                            {{ t('detail.doneText') }}
                        </p>
                        <button
                            class="button secondary"
                            :disabled="busy"
                            @click="startEdit"
                        >
                            {{ t('detail.editReview') }}
                        </button>
                    </div>
                    <div
                        v-else
                        class="panel"
                    >
                        <p class="eyebrow">{{ t('detail.guestEyebrow') }}</p>
                        <h3>{{ t('detail.guestTitle') }}</h3>
                        <p class="muted">
                            {{ t('detail.guestText') }}
                        </p>
                        <RouterLink
                            to="/login"
                            class="button"
                        >
                            {{ t('detail.guestLogin') }} →
                        </RouterLink>
                        <p class="form-foot">
                            {{ t('common.newHere') }}
                            <RouterLink to="/register">{{ t('nav.join') }}</RouterLink>
                        </p>
                    </div>
                </aside>
            </div>
        </section>
    </template>
</template>

<!--
    Страница книги: данные книги, список отзывов и форма отзыва текущего
    пользователя. Форма показывает один из трёх видов в зависимости от
    состояния: гость → приглашение войти, автор без отзыва (или в режиме
    editing) → форма, автор с готовым отзывом → карточка «Спасибо».
-->
<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getBook } from '../api/books'
import { createReview, deleteReview, getReviews, updateReview } from '../api/reviews'
import { errorMessage } from '../api/client'
import { useAuthStore } from '../stores/auth'
import ReviewItem from '../components/ReviewItem.vue'
import { t } from '../i18n'
import type { Book, Review } from '../types'

const route = useRoute()
const auth = useAuthStore()
const bookId = Number(route.params.id)
const book = ref<Book | null>(null)
const reviews = ref<Review[]>([])
const loading = ref(true)
const error = ref('')
const actionError = ref('')
const notice = ref('')
const busy = ref(false)
const editing = ref(false)
const rating = ref(8)
const text = ref('')
const textInput = ref<HTMLTextAreaElement | null>(null)
/** Отзыв текущего пользователя на эту книгу, если он уже есть. */
const myReview = computed(() =>
    reviews.value.find((review) => review.author.id === auth.user?.id),
)

/** Перезагружает книгу и отзывы параллельно (используется после load и после submit/удаления). */
async function refresh() {
    const [bookData, reviewData] = await Promise.all([
        getBook(bookId),
        getReviews(bookId),
    ])
    book.value = bookData
    reviews.value = reviewData
}
async function load() {
    loading.value = true
    error.value = ''
    try {
        await refresh()
    } catch (cause) {
        error.value = errorMessage(cause)
    } finally {
        loading.value = false
    }
}
/** Сбрасывает форму отзыва к значениям по умолчанию и выходит из режима редактирования. */
function resetForm() {
    editing.value = false
    rating.value = 8
    text.value = ''
}
/** Заполняет форму текущим отзывом пользователя и переводит фокус в textarea. */
async function startEdit() {
    if (!myReview.value) {
        return
    }
    rating.value = myReview.value.rating
    text.value = myReview.value.text
    editing.value = true
    actionError.value = ''
    notice.value = ''
    await nextTick()
    textInput.value?.focus()
}
/**
 * Валидирует форму на клиенте и создаёт или обновляет отзыв (в зависимости
 * от editing). Клиентская проверка дублирует ограничения бэкенда
 * (books/models.py: rating 1–10, text не пустой) только ради мгновенной
 * обратной связи — финальную проверку всё равно делает сервер.
 */
async function submit() {
    if (
        !Number.isInteger(rating.value) ||
        rating.value < 1 ||
        rating.value > 10 ||
        !text.value.trim()
    ) {
        actionError.value = t('detail.invalidForm')
        return
    }
    busy.value = true
    actionError.value = ''
    notice.value = ''
    try {
        const payload = { rating: rating.value, text: text.value.trim() }
        if (editing.value && myReview.value) {
            await updateReview(myReview.value.id, payload)
        } else {
            await createReview(bookId, payload)
        }
        notice.value = editing.value ? t('detail.updated') : t('detail.published')
        resetForm()
        await refresh()
    } catch (cause) {
        actionError.value = errorMessage(cause)
    } finally {
        busy.value = false
    }
}
/** Удаляет отзыв пользователя после подтверждения через window.confirm. */
async function removeReview() {
    if (!myReview.value || !window.confirm(t('detail.confirmDelete'))) {
        return
    }
    busy.value = true
    actionError.value = ''
    notice.value = ''
    try {
        await deleteReview(myReview.value.id)
        resetForm()
        notice.value = t('detail.deleted')
        await refresh()
    } catch (cause) {
        actionError.value = errorMessage(cause)
    } finally {
        busy.value = false
    }
}
watch(
    () => auth.user?.id,
    () => {
        resetForm()
        actionError.value = ''
        notice.value = ''
    },
)
onMounted(load)
</script>
