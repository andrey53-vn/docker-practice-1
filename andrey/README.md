# Метаданные картинок

Простое HTTP API для хранения метаданных изображений: url, width, height, tags.

## Эндпоинты

- `POST /images` — добавить изображение
- `GET /images` — получить список всех изображений
- `GET /images?tag=landscape` — получить список изображений по тегу
- `GET /images/{id}` — получить изображение по id

## Запуск

```bash
docker compose up --build
