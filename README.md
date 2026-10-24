# codeowners-lint

Проверяет файл `CODEOWNERS` по дереву репозитория до того, как он сломает ревью: неверные владельцы, правила, которые ничего не покрывают, дубликаты и файлы без владельца. Работает офлайн и только читает файлы. Без зависимостей, Python 3.10+.

## Быстрый старт

Требуется Python 3.10+. Установите готовую версию из [последнего релиза](https://github.com/GhosTnever-lkm/codeowners-lint/releases/latest) или запустите из клона репозитория:

```bash
python -m pip install codeowners_lint-0.1.4-py3-none-any.whl
codeowners-lint . --require-full
```

```bash
python -m codeowners_lint               # текущая папка
python -m codeowners_lint . --require-full --strict
python -m codeowners_lint . --json
python -m codeowners_lint . --require-full --exclude "gen/*"   # сгенерированные файлы без владельца допустимы
```

Пример вывода для [examples/demo](examples/demo):

```text
CODEOWNERS: CODEOWNERS (3 rules)
OK: no findings
```

## Проверки

| Код | Уровень | Смысл |
| --- | --- | --- |
| `INVALID_OWNER` | error | владелец не `@user`, `@org/team` и не e-mail |
| `NO_OWNERS` | error | правило без владельцев |
| `NO_CODEOWNERS` | info (error с `--require-file`) | файла нет в `CODEOWNERS`, `.github/` или `docs/` |
| `UNMATCHED_PATTERN` | warning | шаблон не совпадает ни с одним файлом |
| `DUPLICATE_PATTERN` | warning | шаблон повторяется; действует последний |
| `UNOWNED_FILES` | error с `--require-full` | файлы без владельца |

Коды возврата: `0` — ок, `1` — есть ошибки (или предупреждения при `--strict`), `2` — путь не папка.

## Семантика

- Последнее совпавшее правило побеждает, как в GitHub.
- Шаблон без `/` совпадает с файлом в любой папке; `/docs/` — только в корне; `**` — любая вложенность.
- Папки `.git`, `node_modules`, `.venv`, `venv`, `__pycache__` пропускаются.

## Ограничения

- Не проверяет, существуют ли команды и пользователи в GitHub: проверка офлайн.
- Сопоставление шаблонов упрощённое; сложные случаи `[abc]` и экранирование не поддерживаются.

## Разработка

```bash
python -m unittest discover -s tests -t .
```

## Лицензия

MIT — см. [LICENSE](LICENSE).

## История изменений

См. [CHANGELOG.md](CHANGELOG.md). Политика безопасности — в [SECURITY.md](SECURITY.md).

## Использование в CI

Фрагмент для GitHub Actions (Python 3.10+, без зависимостей):

```yaml
- uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
- uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0
  with:
    python-version: "3.12"
- name: codeowners-lint
  run: python -m codeowners_lint . --require-full --strict
```
