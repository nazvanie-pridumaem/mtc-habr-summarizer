import { useState } from 'react';

interface RateArticleProps {
    articleUrl: string;
    summarizedText: string;
    onRatingSubmitted?: () => void;
}

export default function RateArticle({ articleUrl, summarizedText, onRatingSubmitted }: RateArticleProps) {
    const [rating, setRating] = useState(0);
    const [hoveredRating, setHoveredRating] = useState(0);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isSubmitted, setIsSubmitted] = useState(false);
    const [error, setError] = useState('');

    const handleSubmitRating = async () => {
        if (rating === 0) {
            setError('Пожалуйста, выберите оценку');
            return;
        }

        setIsSubmitting(true);
        setError('');

        try {
            // Преобразуем текст резюме в строку для отправки
            const summaryText = typeof summarizedText === 'string' 
                ? summarizedText 
                : JSON.stringify(summarizedText);

            const response = await fetch('http://localhost:8000/rate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    article_url: articleUrl,
                    summarized_text: summaryText,
                    rating: rating
                })
            });

            if (!response.ok) {
                throw new Error('Ошибка при отправке оценки');
            }

            const result = await response.json();
            
            if (result.success) {
                setIsSubmitted(true);
                if (onRatingSubmitted) {
                    onRatingSubmitted();
                }
            }
        } catch (err) {
            setError('Произошла ошибка при отправке оценки. Попробуйте позже.');
            console.error('Rating submission error:', err);
        } finally {
            setIsSubmitting(false);
        }
    };

    if (isSubmitted) {
        return (
            <div className="bg-green-50 rounded-xl p-6 text-center">
                <div className="mb-4">
                    <svg className="w-16 h-16 text-green-500 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-800 mb-2">
                    Спасибо за вашу оценку!
                </h3>
                <p className="text-gray-600">
                    Ваш отзыв поможет нам улучшить качество суммаризации
                </p>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-xl font-semibold text-gray-800 mb-4 text-center">
                Оцените качество суммаризации
            </h3>
            
            <div className="flex justify-center mb-6">
                {[1, 2, 3, 4, 5].map((star) => (
                    <button
                        key={star}
                        onClick={() => setRating(star)}
                        onMouseEnter={() => setHoveredRating(star)}
                        onMouseLeave={() => setHoveredRating(0)}
                        className="mx-1 transition-all duration-200 transform hover:scale-110"
                        disabled={isSubmitting}
                    >
                        <svg
                            className={`w-10 h-10 ${
                                star <= (hoveredRating || rating)
                                    ? 'text-yellow-400 fill-current'
                                    : 'text-gray-300'
                            }`}
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                            strokeWidth={1}
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
                            />
                        </svg>
                    </button>
                ))}
            </div>

            {error && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-red-700 text-sm text-center">{error}</p>
                </div>
            )}

            <div className="text-center">
                <button
                    onClick={handleSubmitRating}
                    disabled={isSubmitting || rating === 0}
                    className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-6 py-2 rounded-lg font-medium shadow-md hover:from-blue-600 hover:to-indigo-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {isSubmitting ? (
                        <div className="flex items-center">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                            Отправляем...
                        </div>
                    ) : (
                        'Отправить оценку'
                    )}
                </button>
            </div>

            <p className="text-center text-sm text-gray-500 mt-4">
                Ваша оценка поможет нам улучшить качество суммаризации
            </p>
        </div>
    );
}