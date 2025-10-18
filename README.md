# README.md — Паспорт проекта

## Hatnchiks — асинхронный backend для игры «Шляпа»

**Техстек:** Python 3.12, FastAPI, Pydantic, SQLAlchemy, Redis, PostgreSQL, FastAPI Users, Uvicorn, Loguru

### Цель репозитория

Асинхронный REST API для игры «Шляпа»: управление пользователями, карточками, играми и игровыми раундами.

### Definition of Done (DoD)

* Изменения соответствуют правилам безопасности и качества (см. `Agents.md` и `docs/`).
* Все проверки `uv run pytest -q` зелёные локально и в CI.
* Тесты добавлены/обновлены; покрытие не снижается (или ≥ 80%).
* Документация и примеры кода актуализированы.



Generate secrets to UserManager:
```shell
python -c 'import secrets; print(secrets.token_hex())'
```