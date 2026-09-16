<template>
    <RouterLink
        class="back-link"
        to="/"
    >
        ← Back to the collection
    </RouterLink>
    <p
        v-if="loading"
        class="state"
        role="status"
    >
        Opening the book…
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
    <template v-else-if="book">
        <section class="book-detail">
            <div
                class="book-cover detail-cover"
                :class="`cover-${book.id % 4}`"
                aria-hidden="true"
            >
                <span class="cover-edition">THE SHELFTALK LIBRARY</span>
                <span class="cover-title">{{ book.title }}</span>
                <span class="cover-ornament">✳</span>
                <span class="cover-author">{{ book.author }}</span>
            </div>
            <div class="detail-copy">
                <p class="eyebrow">
                    FROM THE COLLECTION · {{ book.publication_year ?? 'YEAR UNKNOWN' }}
                </p>
                <h1>{{ book.title }}</h1>
                <p class="detail-author">by {{ book.author }}</p>
                <div class="detail-rating">
                    <span class="rating-badge">
                        ★
                        {{
                            book.average_rating === null
                                ? 'Not rated'
                                : `${book.average_rating.toFixed(1)} / 10`
                        }}
                    </span>
                    <span class="muted">
                        {{ book.reviews_count }}
                        {{
                            book.reviews_count === 1
                                ? 'reader review'
                                : 'reader reviews'
                        }}
                    </span>
                </div>
                <h2>About the book</h2>
                <p class="description">
                    {{
                        book.description ||
                        'No description has been added for this book yet.'
                    }}
                </p>
            </div>
        </section>
        <section class="reviews-section">
            <div class="section-heading">
                <div>
                    <p class="eyebrow">BETWEEN THE LINES</p>
                    <h2>
                        What readers are saying
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
                        Every conversation starts somewhere. Be the first to share your
                        thoughts.
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
                                    ? 'Edit your review'
                                    : 'Your reading, your words.'
                            }}
                        </h3>
                        <p class="muted">What stayed with you?</p>
                        <label for="rating">
                            Your rating
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
                                {{ value }} / 10
                            </option>
                        </select>
                        <label for="review-text">Your review</label>
                        <textarea
                            id="review-text"
                            ref="textInput"
                            v-model="text"
                            rows="6"
                            required
                            :disabled="busy"
                            placeholder="Tell other readers what you thought…"
                        ></textarea>
                        <button
                            class="button"
                            :disabled="busy"
                        >
                            {{
                                busy
                                    ? 'Saving…'
                                    : editing
                                      ? 'Save changes'
                                      : 'Publish review'
                            }}
                        </button>
                        <button
                            v-if="editing"
                            type="button"
                            class="text-button"
                            :disabled="busy"
                            @click="resetForm"
                        >
                            Cancel
                        </button>
                    </form>
                    <div
                        v-else-if="auth.isAuthenticated"
                        class="panel"
                    >
                        <p class="eyebrow">YOUR VOICE IS ON THE SHELF</p>
                        <h3>Thanks for sharing.</h3>
                        <p class="muted">
                            Changed your mind after a reread? You can edit your review
                            anytime.
                        </p>
                        <button
                            class="button secondary"
                            :disabled="busy"
                            @click="startEdit"
                        >
                            Edit your review
                        </button>
                    </div>
                    <div
                        v-else
                        class="panel"
                    >
                        <p class="eyebrow">ADD YOUR PERSPECTIVE</p>
                        <h3>Read it? Let’s talk.</h3>
                        <p class="muted">
                            Log in to rate this book and join the conversation.
                        </p>
                        <RouterLink
                            to="/login"
                            class="button"
                        >
                            Log in to review →
                        </RouterLink>
                        <p class="form-foot">
                            New here?
                            <RouterLink to="/register">Join ShelfTalk</RouterLink>
                        </p>
                    </div>
                </aside>
            </div>
        </section>
    </template>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getBook } from '../api/books'
import { createReview, deleteReview, getReviews, updateReview } from '../api/reviews'
import { errorMessage } from '../api/client'
import { useAuthStore } from '../stores/auth'
import ReviewItem from '../components/ReviewItem.vue'
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
const myReview = computed(() =>
    reviews.value.find((review) => review.author.id === auth.user?.id),
)

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
function resetForm() {
    editing.value = false
    rating.value = 8
    text.value = ''
}
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
async function submit() {
    if (
        !Number.isInteger(rating.value) ||
        rating.value < 1 ||
        rating.value > 10 ||
        !text.value.trim()
    ) {
        actionError.value =
            'Choose a whole-number rating from 1 to 10 and write your review.'
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
        notice.value = editing.value
            ? 'Your review has been updated.'
            : 'Your review is on the shelf. Thanks for sharing!'
        resetForm()
        await refresh()
    } catch (cause) {
        actionError.value = errorMessage(cause)
    } finally {
        busy.value = false
    }
}
async function removeReview() {
    if (
        !myReview.value ||
        !window.confirm('Delete your review? This cannot be undone.')
    ) {
        return
    }
    busy.value = true
    actionError.value = ''
    notice.value = ''
    try {
        await deleteReview(myReview.value.id)
        resetForm()
        notice.value = 'Your review has been deleted.'
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
