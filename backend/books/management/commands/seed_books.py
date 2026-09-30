"""Management-команда `python manage.py seed_books` — демо-данные каталога."""

from django.core.management.base import BaseCommand

from books.models import Book

BOOKS = [
    (
        "1984",
        "George Orwell",
        1949,
        "In a society where every thought is watched, Winston Smith begins to "
        "question the truth. A chilling story of power, memory, and individual "
        "freedom.",
    ),
    (
        "Animal Farm",
        "George Orwell",
        1945,
        "The animals of Manor Farm overthrow their farmer in search of a fairer "
        "life. Their revolution becomes a sharp fable about power and its "
        "promises.",
    ),
    (
        "The Hobbit",
        "J. R. R. Tolkien",
        1937,
        "Bilbo Baggins leaves the comfort of his home for a journey with "
        "thirteen dwarves. Along the way, an unlikely adventurer discovers "
        "courage, friendship, and a mysterious ring.",
    ),
    (
        "The Great Gatsby",
        "F. Scott Fitzgerald",
        1925,
        "On Long Island, Nick Carraway enters the glittering world of his "
        "enigmatic neighbor Jay Gatsby. Behind the parties lies a story of "
        "longing and the American dream.",
    ),
    (
        "Pride and Prejudice",
        "Jane Austen",
        1813,
        "Elizabeth Bennet and Mr. Darcy must look beyond their first "
        "impressions. A witty novel of family, social expectations, and the "
        "courage to change one's mind.",
    ),
    (
        "Crime and Punishment",
        "Fyodor Dostoevsky",
        1866,
        "A young former student in Saint Petersburg commits a crime to test his "
        "own theory of morality. His struggle with guilt becomes a profound "
        "exploration of conscience and redemption.",
    ),
    (
        "Fahrenheit 451",
        "Ray Bradbury",
        1953,
        "Guy Montag is a fireman whose job is to burn books. An unexpected "
        "encounter makes him question a world that has traded difficult ideas "
        "for constant entertainment.",
    ),
    (
        "Brave New World",
        "Aldous Huxley",
        1932,
        "In a carefully engineered society, comfort and stability come at the "
        "cost of freedom. An outsider's arrival reveals what has been lost in "
        "the pursuit of perfect happiness.",
    ),
]


class Command(BaseCommand):
    """Добавляет восемь демо-книг, безопасно повторяемая (идемпотентная).

    Использует get_or_create по (title, author): существующие книги не
    дублируются и не перезаписываются, даже если их описание было
    отредактировано в Django Admin (см. тест
    test_seed_is_repeatable_and_preserves_edits в books/tests.py).
    """

    help = "Add eight demo books without duplicating or overwriting existing books."

    def handle(self, *args, **options):
        created_count = 0
        for title, author, year, description in BOOKS:
            _, created = Book.objects.get_or_create(
                title=title,
                author=author,
                defaults={"publication_year": year, "description": description},
            )
            created_count += created
        self.stdout.write(self.style.SUCCESS(f"Added {created_count} books."))
