"""config.py - конфигурационный файл.

Содержит:
1. MODEL_CONFIG: настройка параметров для используемых моделей.

    - Описание параметров:
        - "model_name"        - название модели c HuggingFace Hub;
        - "max_input_length"  - макс. длина входного текста в токенах;
        - "max_output_length" - макс. длина суммаризации в токенах;
        - "min_output_length" - мин. длина суммаризации в токенах.

2. GENERATION_PRESETS: настройка параметров для генерации суммаризации.

    - Описание параметров:
        - "num_beams"            - количество лучей в beam search (оптимально: 3-5);
        - "length_penalty"       - коэф. длины (<1 - короче, >1 - длиннее);
        - "no_repeat_ngram_size" - запрет N-грамм (оптимально: 2-4);
        - "early_stopping"       - досрочная остановка генерации;
        - "do_sample"            - использовать стохастическую генерацию;
        - "temperature"          - уровень случайности (оптимально: 0.5-1.0);
        - "top_p"                - top-p sampling (оптимально: 0.7-0.95);
        - "repetition_penalty"   - штраф за повторы (оптимально: 1.0-1.5).
"""

MODEL_CONFIG = {
    "primary": {
        "model_name": "denisnaenko/t5_habr_summarizer", 
        "max_input_length": 600,
        "max_output_length": 200,
        "min_output_length": 30,
    },
    "fallback": {
        "model_name": "ghostbim21/ru_text_summary",
        "max_input_length": 512,
        "max_output_length": 150,
        "min_output_length": 30,
    },
}

GENERATION_PRESETS = {
    "general": {
        "num_beams": 3,
        "length_penalty": 0.9,
        "no_repeat_ngram_size": 3,
        "early_stopping": True,
        "do_sample": True,
        "temperature": 0.8,
        "top_p": 0.9,
        "repetition_penalty": 1.15,
    },
}
