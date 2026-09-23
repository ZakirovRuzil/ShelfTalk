import type en from './locales/en'

// Формы множественного числа. Нужную выбирает Intl.PluralRules: в английском
// one/other, в русском one/few/many (1 отзыв, 2 отзыва, 5 отзывов).
export type Plural = Partial<Record<Intl.LDMLPluralRule, string>> & { other: string }

// Структура английского словаря — эталон, остальные языки обязаны ей соответствовать.
export type Messages = typeof en

// Все пути к переводам через точку: 'nav.login' | 'book.reviews' | ...
// Рекурсивно обходит словарь: строка или Plural — конец пути, объект — идём глубже
type Paths<T> = {
    [K in keyof T & string]: T[K] extends string | Plural ? K : `${K}.${Paths<T[K]>}`
}[keyof T & string]

export type MessageKey = Paths<Messages>
