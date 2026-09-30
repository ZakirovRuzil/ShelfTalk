import { ref, watchEffect } from 'vue'
import en from './locales/en'
import ru from './locales/ru'
import type { MessageKey, Messages, Plural } from './types'

/**
 * Собственная (без библиотек) реализация i18n для проекта. Чтобы добавить
 * язык: создать locales/xx.ts с типом Messages, импортировать и дописать
 * сюда — переключатель в AppNavbar.vue подхватит его сам через `locales`.
 */
const messages = { en, ru } satisfies Record<string, Messages>

export type Locale = keyof typeof messages
export const locales = Object.keys(messages) as Locale[]

const STORAGE_KEY = 'locale'

function isLocale(value: unknown): value is Locale {
    return typeof value === 'string' && value in messages
}

/**
 * Язык при первой загрузке: сохранённый выбор в localStorage, иначе язык
 * браузера (если он поддерживается), иначе английский.
 */
function detectLocale(): Locale {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (isLocale(saved)) {
        return saved
    }
    const browser = navigator.language.slice(0, 2)
    return isLocale(browser) ? browser : 'en'
}

/**
 * Текущий язык интерфейса. Реактивная ссылка Vue: любой шаблон, читающий
 * её (напрямую или через {@link t}), автоматически перерисовывается при
 * смене языка — отдельной подписки не требуется.
 */
export const locale = ref<Locale>(detectLocale())

/** Меняет текущий язык и запоминает выбор в localStorage. */
export function setLocale(value: Locale) {
    locale.value = value
    localStorage.setItem(STORAGE_KEY, value)
}

watchEffect(() => {
    document.documentElement.lang = locale.value
    document.title = t('app.title')
})

// 'nav.login' -> messages[locale].nav.login
function lookup(key: string): string | Plural | undefined {
    let node: unknown = messages[locale.value]
    for (const part of key.split('.')) {
        node = (node as Record<string, unknown> | undefined)?.[part]
    }
    return node as string | Plural | undefined
}

/**
 * Проверяет, существует ли ключ в словаре текущего языка. Нужна для
 * ключей, собранных динамически во время работы (например,
 * `fields.${имяПоля}` из ответа API в api/client.ts), для которых
 * TypeScript не может проверить существование на этапе компиляции.
 */
export function hasKey(key: string): key is MessageKey {
    return lookup(key) !== undefined
}

/**
 * Переводит ключ в строку на текущем языке с подстановкой параметров.
 *
 * @param key - путь в словаре через точку, например `'nav.login'`.
 *   Проверяется TypeScript'ом: опечатка или несуществующий ключ — ошибка
 *   компиляции.
 * @param params - значения для `{имя}` в строке; `params.count` также
 *   используется для выбора формы множественного числа
 * @returns готовая строка. Если ключ не найден в словаре (в рантайме, в
 *   обход проверки типов), возвращается сам ключ — это заметно на экране
 *   и облегчает поиск пропущенного перевода
 */
export function t(
    key: MessageKey,
    params: Record<string, string | number> = {},
): string {
    let message = lookup(key) ?? key
    if (typeof message === 'object') {
        // Intl.PluralRules('ru').select(5) === 'many' -> '{count} отзывов'
        const count = Number(params.count ?? 0)
        const form = new Intl.PluralRules(locale.value).select(count)
        message = message[form] ?? message.other
    }
    // 'by {author}' + { author: 'Orwell' } -> 'by Orwell'
    return message.replace(/\{(\w+)\}/g, (match, name: string) =>
        name in params ? String(params[name]) : match,
    )
}

/** Форматирует дату под текущий язык, например «15 сент. 2026 г.» для ru. */
export function formatDate(value: string | Date): string {
    return new Date(value).toLocaleDateString(locale.value, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
    })
}
