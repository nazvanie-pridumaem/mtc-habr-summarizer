""" download_nltk_resources.py - скрипт для установки необходимых NLTK ресурсов.

Запустите данный скрипт один раз после установки зависимостей из requirements.txt.

Для запуска скрипта введите в терминал следующую команду:
    `python download_nltk_resources.py`

Данный скрипт загружает:
    - "punkt"                      - токенизатор предложений;
    - "stopwords"                  - список стоп-слов;
    - "averaged_perceptron_tagger" - теггер частей речи.
"""

import os
import ssl

import nltk


def setup_nltk():
    """Настройка и загрузка NLTK ресурсов"""

    # Настройка SSL для загрузки
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    # Создаем директорию для данных NLTK
    nltk_data_dir = os.path.join(os.path.expanduser("~"), "nltk_data")
    if not os.path.exists(nltk_data_dir):
        os.makedirs(nltk_data_dir)

    print(f"NLTK данные будут сохранены в: {nltk_data_dir}")

    # Список необходимых ресурсов
    resources = [
        "punkt",
        "stopwords",
        "averaged_perceptron_tagger",  
        "punkt_tab",
    ]

    # Загружаем каждый ресурс
    for resource in resources:
        print(f"Загружаем {resource}...")
        try:
            nltk.download(resource, download_dir=nltk_data_dir, quiet=False)
            print(f"✓ {resource} успешно загружен")
        except Exception as e:
            print(f"✗ Ошибка при загрузке {resource}: {e}")

    # Проверяем установку
    print("\nПроверка установленных ресурсов:")
    try:
        from nltk.corpus import stopwords
        from nltk.tokenize import sent_tokenize, word_tokenize

        # Тест токенизации
        test_text = "Это тестовое предложение. А это второе!"
        sentences = sent_tokenize(test_text, language="russian")
        print(f"✓ Токенизация предложений работает: {len(sentences)} предложения")

        # Тест стоп-слов
        russian_stops = stopwords.words("russian")
        print(f"✓ Русские стоп-слова загружены: {len(russian_stops)} слов")

        print("\nВсе необходимые NLTK ресурсы успешно установлены!")

    except Exception as e:
        print(f"\n✗ Ошибка при проверке: {e}")
        print("Некоторые ресурсы могут быть недоступны")


if __name__ == "__main__":
    setup_nltk()
