# Как там Хабр?
[Как там Хабр?](https://kak-tam-habr.ru.tuna.am/) - веб-сервис, предоставляющий суммаризацию и аналитику для статей и комментариев с сайта [Habr](https://habr.com).

## Запуск Docker контейнеров

Для удобства поддержки и запуска проекта добавлена разделённая сборка для CPU и GPU.

### Требования

- Docker >= 20.10
- Docker Compose >= 1.29
- Для GPU-версии: установлен драйвер NVIDIA + [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

### Запуск GPU-версии (использует CUDA):

- через утилиту make:
```bash
make up-gpu
```
- либо вручную:
```bash
docker-compose up --build frontend backend-gpu
```

### Запуск CPU-версии:

- через утилиту make:
```bash
make up-cpu
```
- либо вручную:
```bash
docker-compose up --build frontend backend-cpu
```

### Проверка
После запуска frontend-контейнер будет доступен на `localhost:3000`, а backend-контейнер на `localhost:8000` (изменить порты можно в файле `docker-compose.yml`).
`


## Конфигурация моделей
Параметры конфигурации находятся в `config.py`:

### MODEL_CONFIG

Настройка используемых моделей суммаризации:

- `model_name` — название модели на HuggingFace;
- `max_input_length` — максимальная длина входного текста (в токенах);
- `max_output_length` — максимальная длина выходного текста;
- `min_output_length` — минимальная длина выходного текста.

Поддерживаются два режима:
- **primary** — основная модель;
- **fallback** — запасная модель (если primary не доступна).

### GENERATION_PRESETS

Параметры генерации текста:

- `num_beams` — количество лучей для beam search (3–5 оптимально);
- `length_penalty` — штраф за длину: >1 делает текст длиннее, <1 — короче;
- `no_repeat_ngram_size` — запрещённые повторения N-грамм (обычно 2–4);
- `early_stopping` — досрочная остановка генерации;
- `do_sample` — включает стохастическую генерацию;
- `temperature` — уровень случайности (0.7–1.0 разумно);
- `top_p` — top-p sampling (0.7–0.95);
- `repetition_penalty` — штраф за повторы слов/фраз (1.0–1.5).
