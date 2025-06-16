from transformers import pipeline
from collections import Counter, defaultdict
from typing import List, Dict
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommentAnalyzer:
    def __init__(self):
        """Инициализация анализатора комментариев"""
        try:
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis", 
                model="blanchefort/rubert-base-cased-sentiment"
            )
            logger.info("Модель анализа тональности загружена успешно")
        except Exception as e:
            logger.error(f"Ошибка загрузки модели: {e}")
            self.sentiment_analyzer = None

    def analyze_sentiment(self, text: str) -> str:
        """Анализирует тональность текста"""
        if not self.sentiment_analyzer or not text or not text.strip():
            return 'нейтральная'
        
        try:
            result = self.sentiment_analyzer(text[:512])[0]  # Ограничиваем длину текста
            label = result['label']
            
            if label == 'POSITIVE':
                return 'позитивная'
            elif label == 'NEGATIVE':
                return 'негативная'
            else:
                return 'нейтральная'
        except Exception as e:
            logger.warning(f"Ошибка анализа тональности: {e}")
            return 'нейтральная'

    def process_comments(self, comments_list: List[Dict]) -> Dict:
        """
        Анализирует список комментариев и возвращает статистику
        
        Args:
            comments_list: список словарей с ключами 'author' и 'text'
        
        Returns:
            Dict с результатами анализа
        """
        if not comments_list:
            return {
                'total_comments': 0,
                'sentiment_stats': {},
                'examples': {},
                'success': False,
                'error': 'Комментарии отсутствуют'
            }

        try:
            # Фильтруем валидные комментарии
            valid_comments = []
            for comment in comments_list:
                if (isinstance(comment, dict) and 
                    'text' in comment and 
                    comment['text'] and 
                    str(comment['text']).strip()):
                    valid_comments.append({
                        'author': comment.get('author', 'Неизвестный автор'),
                        'text': str(comment['text']).strip()
                    })
            
            if not valid_comments:
                return {
                    'total_comments': 0,
                    'sentiment_stats': {},
                    'examples': {},
                    'success': False,
                    'error': 'Все комментарии пустые'
                }
            
            logger.info(f"Анализируем {len(valid_comments)} комментариев...")
            
            # Анализ тональности с группировкой
            sentiment_groups = defaultdict(list)
            sentiment_counts = Counter()
            
            for comment in valid_comments:
                sentiment = self.analyze_sentiment(comment['text'])
                sentiment_groups[sentiment].append(comment)
                sentiment_counts[sentiment] += 1
            
            total_comments = len(valid_comments)
            
            # Формируем статистику в процентах
            sentiment_stats = {}
            for sentiment, count in sentiment_counts.items():
                sentiment_stats[sentiment] = {
                    'count': count,
                    'percentage': round((count / total_comments) * 100, 1)
                }
            
            # Собираем примеры комментариев (до 3 для каждой тональности)
            examples = {}
            for sentiment, comments in sentiment_groups.items():
                examples[sentiment] = []
                
                # Сортируем по длине и берем самые информативные
                sorted_comments = sorted(comments, key=lambda x: len(x['text']), reverse=True)
                
                for comment in sorted_comments[:3]:
                    text = comment['text']
                    
                    # Обрезаем длинные комментарии
                    if len(text) > 150:
                        text = text[:150] + '...'
                    
                    examples[sentiment].append({
                        'author': comment['author'],
                        'text': text
                    })
            
            result = {
                'total_comments': total_comments,
                'sentiment_stats': sentiment_stats,
                'examples': examples,
                'success': True,
                'error': None
            }
            
            logger.info(f"Анализ завершен успешно: {total_comments} комментариев")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при анализе комментариев: {e}")
            return {
                'total_comments': 0,
                'sentiment_stats': {},
                'examples': {},
                'success': False,
                'error': f'Ошибка анализа: {str(e)}'
            }

    def get_top_words(self, comments_list: List[Dict], sentiment: str = None, top_n: int = 10) -> List[str]:
        """
        Возвращает топ слов из комментариев (опционально для конкретной тональности)
        """
        try:
            # Фильтруем валидные комментарии
            valid_comments = []
            for comment in comments_list:
                if (isinstance(comment, dict) and 
                    'text' in comment and 
                    comment['text'] and 
                    str(comment['text']).strip()):
                    valid_comments.append(comment)
            
            if not valid_comments:
                return []
            
            # Фильтруем по тональности если указана
            if sentiment:
                filtered_comments = []
                for comment in valid_comments:
                    comment_sentiment = self.analyze_sentiment(comment['text'])
                    if comment_sentiment == sentiment:
                        filtered_comments.append(comment)
                valid_comments = filtered_comments
            
            # Объединяем все тексты
            all_texts = [str(comment['text']) for comment in valid_comments]
            all_text = ' '.join(all_texts)
            
            # Простая токенизация и очистка
            words = self._extract_words(all_text)
            
            # Подсчитываем частоту
            word_counts = Counter(words)
            
            return [word for word, count in word_counts.most_common(top_n)]
            
        except Exception as e:
            logger.error(f"Ошибка получения топ слов: {e}")
            return []

    def _extract_words(self, text: str) -> List[str]:
        """Извлекает и очищает слова из текста"""
        import re
        
        # Удаляем HTML теги и специальные символы
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Разбиваем на слова и приводим к нижнему регистру
        words = text.lower().split()
        
        # Стоп-слова для русского языка
        stop_words = {
            'и', 'в', 'на', 'с', 'по', 'для', 'как', 'что', 'это', 'не', 'а', 'но', 
            'или', 'от', 'до', 'при', 'из', 'за', 'к', 'о', 'у', 'же', 'уже', 'еще',
            'так', 'вот', 'быть', 'мочь', 'весь', 'свой', 'наш', 'ваш', 'их', 'который',
            'тот', 'этот', 'один', 'два', 'три', 'там', 'тут', 'где', 'когда', 'если'
        }
        
        # Фильтруем короткие слова, числа и стоп-слова
        filtered_words = []
        for word in words:
            if (len(word) > 3 and 
                word not in stop_words and 
                not word.isdigit() and
                word.isalpha()):
                filtered_words.append(word)
        
        return filtered_words

    def get_sentiment_summary(self, comments_list: List[Dict]) -> str:
        """Возвращает краткое описание общего настроения комментариев"""
        try:
            analysis = self.process_comments(comments_list)
            
            if not analysis['success'] or not analysis['sentiment_stats']:
                return "Анализ комментариев недоступен"
            
            stats = analysis['sentiment_stats']
            total = analysis['total_comments']
            
            # Находим доминирующую тональность
            dominant_sentiment = max(stats.keys(), key=lambda x: stats[x]['count'])
            dominant_percentage = stats[dominant_sentiment]['percentage']
            
            # Формируем описание
            if dominant_percentage > 60:
                intensity = "преимущественно"
            elif dominant_percentage > 40:
                intensity = "в основном"
            else:
                intensity = "частично"
            
            sentiment_text = {
                'позитивная': 'позитивные',
                'негативная': 'негативные', 
                'нейтральная': 'нейтральные'
            }.get(dominant_sentiment, dominant_sentiment)
            
            return f"Комментарии {intensity} {sentiment_text} ({dominant_percentage}% из {total})"
            
        except Exception as e:
            logger.error(f"Ошибка создания сводки: {e}")
            return "Ошибка анализа комментариев"

# Глобальный экземпляр анализатора
comment_analyzer = CommentAnalyzer()