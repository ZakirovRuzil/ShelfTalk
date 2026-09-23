<template>
    <article class="review-item">
        <div class="review-heading">
            <div>
                <strong>
                    {{ review.author.display_name || t('review.anonymous') }}
                </strong>
                <span
                    v-if="owned"
                    class="you-badge"
                >
                    {{ t('review.you') }}
                </span>
                <p class="review-date">
                    {{ formatDate(review.created_at) }}
                    <span v-if="review.updated_at !== review.created_at">
                        · {{ t('review.edited') }}
                    </span>
                </p>
            </div>
            <span class="rating-badge">
                ★ {{ review.rating }}
                <small>/ 10</small>
            </span>
        </div>
        <p class="review-text">{{ review.text }}</p>
        <div
            v-if="owned"
            class="review-actions"
        >
            <button
                class="text-button"
                :disabled="busy"
                @click="$emit('edit')"
            >
                {{ t('review.edit') }}
            </button>
            <button
                class="text-button danger"
                :disabled="busy"
                @click="$emit('delete')"
            >
                {{ t('review.delete') }}
            </button>
        </div>
    </article>
</template>

<script setup lang="ts">
import type { Review } from '../types'
import { formatDate, t } from '../i18n'
defineProps<{ review: Review; owned: boolean; busy: boolean }>()
defineEmits<{ edit: []; delete: [] }>()
</script>
