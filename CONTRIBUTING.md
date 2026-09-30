# Contributing

Учебный проект, но правила те же, что и в обычном репозитории.

## Перед началом

1. Настройте окружение по [docs/SETUP.md](docs/SETUP.md).
2. Создайте отдельную ветку от `main` (`feature/...`, `fix/...`, `docs/...`).

## Перед коммитом/PR

Прогоните проверки, описанные в
[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md#проверки-и-форматирование):

```sh
# backend/, с активированным virtualenv
ruff check .
ruff format --check .
python manage.py check
python manage.py test

# frontend/
npm run lint
npm run format:check
npm run build
```

## Коммиты

Формат [Conventional Commits](https://www.conventionalcommits.org/): `feat(scope): ...`,
`fix: ...`, `docs: ...`, `test: ...`, `refactor: ...`, `style: ...`, `chore: ...`.
Примеры — в [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md#git-процесс-и-коммиты).

## Pull Request

Опишите, что и зачем изменилось. Если менялся API — обновите [docs/API.md](docs/API.md);
если менялась модель данных — [docs/DATA_MODEL.md](docs/DATA_MODEL.md); если добавлялась
заметная фича — запись в [CHANGELOG.md](CHANGELOG.md) под `[Unreleased]`.
