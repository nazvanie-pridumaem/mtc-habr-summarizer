import { useState, useEffect } from 'react';

interface CommentExample {
    author: string;
    text: string;
}

interface SentimentStat {
    count: number;
    percentage: number;
}

interface CommentsAnalysisData {
    total_comments: number;
    sentiment_stats: Record<string, SentimentStat>;
    examples: Record<string, CommentExample[]>;
    success: boolean;
    error?: string;
}

interface CommentsAnalysisProps {
    analysisData: CommentsAnalysisData | null;
    isLoading?: boolean;
}

function CommentsAnalysis({ analysisData, isLoading }: CommentsAnalysisProps) {
    const [selectedSentiment, setSelectedSentiment] = useState<string | null>(null);

    // Сброс выбранной тональности при смене данных
    useEffect(() => {
        setSelectedSentiment(null);
    }, [analysisData]);

    // Функция для получения цвета тональности
    const getSentimentColor = (sentiment: string) => {
        switch (sentiment) {
            case 'позитивная':
                return {
                    bg: 'bg-green-100',
                    text: 'text-green-800',
                    border: 'border-green-200',
                    accent: 'bg-green-500'
                };
            case 'негативная':
                return {
                    bg: 'bg-red-100',
                    text: 'text-red-800',
                    border: 'border-red-200',
                    accent: 'bg-red-500'
                };
            case 'нейтральная':
                return {
                    bg: 'bg-gray-100',
                    text: 'text-gray-800',
                    border: 'border-gray-200',
                    accent: 'bg-gray-500'
                };
            default:
                return {
                    bg: 'bg-blue-100',
                    text: 'text-blue-800',
                    border: 'border-blue-200',
                    accent: 'bg-blue-500'
                };
        }
    };

    // Функция для получения иконки тональности
    const getSentimentIcon = (sentiment: string) => {
        switch (sentiment) {
            case 'позитивная':
                return (
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM7 9a1 1 0 100-2 1 1 0 000 2zm7-1a1 1 0 11-2 0 1 1 0 012 0zm-.464 5.535a1 1 0 10-1.415-1.414 3 3 0 01-4.242 0 1 1 0 00-1.415 1.414 5 5 0 007.072 0z" clipRule="evenodd" />
                    </svg>
                );
            case 'негативная':
                return (
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM7 9a1 1 0 100-2 1 1 0 000 2zm7-1a1 1 0 11-2 0 1 1 0 012 0zm-7.536 5.879a1 1 0 001.415 1.414 3 3 0 004.242 0 1 1 0 001.415-1.414 5 5 0 00-7.072 0z" clipRule="evenodd" />
                    </svg>
                );
            case 'нейтральная':
                return (
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM7 9a1 1 0 100-2 1 1 0 000 2zm7-1a1 1 0 11-2 0 1 1 0 012 0zm-5 6a1 1 0 011-1h4a1 1 0 110 2H8a1 1 0 01-1-1z" clipRule="evenodd" />
                    </svg>
                );
            default:
                return null;
        }
    };

    if (isLoading) {
        return (
            <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mr-3"></div>
                    <span className="text-lg font-semibold text-gray-700">Анализируем комментарии...</span>
                </div>
            </div>
        );
    }

    if (!analysisData) {
        return null;
    }

    if (!analysisData.success) {
        return (
            <div className="bg-orange-50 border border-orange-200 rounded-xl p-6">
                <div className="flex items-center">
                    <svg className="w-6 h-6 text-orange-500 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 18.5c-.77.833.192 2.5 1.732 2.5z" />
                    </svg>
                    <div>
                        <h3 className="text-lg font-semibold text-orange-800">Анализ комментариев недоступен</h3>
                        <p className="text-orange-700 mt-1">{analysisData.error || 'Не удалось проанализировать комментарии'}</p>
                    </div>
                </div>
            </div>
        );
    }

    const sentiments = Object.keys(analysisData.sentiment_stats);

    return (
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <div className="bg-gradient-to-r from-purple-500 to-pink-600 px-6 py-4">
                <h2 className="text-2xl font-bold text-white flex items-center">
                    <svg className="w-8 h-8 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                    Анализ комментариев
                </h2>
            </div>

            <div className="p-6">
                {/* Статистика тональностей */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 md:gap-4 mb-6">
                    {sentiments.map((sentiment) => {
                        const stats = analysisData.sentiment_stats[sentiment];
                        const colors = getSentimentColor(sentiment);
                        const isSelected = selectedSentiment === sentiment;
                        
                        return (
                            <button
                                key={sentiment}
                                onClick={() => setSelectedSentiment(isSelected ? null : sentiment)}
                                className={`${colors.bg} ${colors.border} border rounded-lg p-4 text-left transition-all duration-200 hover:shadow-md ${isSelected ? 'ring-2 ring-purple-500' : ''}`}
                            >
                                <div className="flex items-center justify-between mb-3">
                                    <div className="flex items-center min-w-0 flex-1">
                                        <div className={`${colors.text} mr-2 flex-shrink-0`}>
                                            {getSentimentIcon(sentiment)}
                                        </div>
                                        <span className={`font-semibold ${colors.text} text-sm md:text-base truncate`}>
                                            {sentiment === 'позитивная' ? 'Позитивные' : 
                                             sentiment === 'негативная' ? 'Негативные' : 
                                             sentiment === 'нейтральная' ? 'Нейтральные' : sentiment}
                                        </span>
                                    </div>
                                    <span className={`text-xl md:text-2xl font-bold ${colors.text} ml-2 flex-shrink-0`}>
                                        {stats.count}
                                    </span>
                                </div>
                                
                                {/* Progress bar */}
                                <div className="w-full bg-white rounded-full h-2 mb-3">
                                    <div 
                                        className={`${colors.accent} h-2 rounded-full transition-all duration-300`}
                                        style={{ width: `${stats.percentage}%` }}
                                    ></div>
                                </div>
                                
                                <div className={`text-xs md:text-sm ${colors.text} leading-tight`}>
                                    {stats.percentage}% от всех комментариев
                                </div>
                            </button>
                        );
                    })}
                </div>

                {/* Примеры комментариев */}
                {selectedSentiment && analysisData.examples[selectedSentiment] && (
                    <div className="animate-fadeIn">
                        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                            <span>
                                {selectedSentiment === 'позитивная' ? 'Позитивные' : 
                                 selectedSentiment === 'негативная' ? 'Негативные' : 
                                 selectedSentiment === 'нейтральная' ? 'Нейтральные' : selectedSentiment} комментарии
                            </span>
                            <span className="ml-2 text-sm text-gray-500">
                                (показаны примеры)
                            </span>
                        </h3>
                        
                        <div className="space-y-3">
                            {analysisData.examples[selectedSentiment].map((example, index) => {
                                const colors = getSentimentColor(selectedSentiment);
                                
                                return (
                                    <div 
                                        key={index}
                                        className={`${colors.bg} ${colors.border} border rounded-lg p-4`}
                                    >
                                        <div className="flex items-start space-x-3">
                                            <div className={`${colors.text} mt-1`}>
                                                {getSentimentIcon(selectedSentiment)}
                                            </div>
                                            <div className="flex-1">
                                                <div className={`font-medium ${colors.text} text-sm mb-1`}>
                                                    {example.author}
                                                </div>
                                                <div className="text-gray-700 leading-relaxed">
                                                    "{example.text}"
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                )}

                {/* Инструкция если ничего не выбрано */}
                {!selectedSentiment && (
                    <div className="text-center py-8 text-gray-500">
                        <svg className="mx-auto w-12 h-12 mb-3 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-1l-4 4z" />
                        </svg>
                        <p>Нажмите на карточку тональности, чтобы увидеть примеры комментариев</p>
                    </div>
                )}
            </div>

            {/* Footer со статистикой */}
            <div className="bg-gray-50 px-6 py-4 border-t">
                <div className="flex items-center justify-between text-sm text-gray-600">
                    <span>
                        Проанализировано комментариев: {analysisData.total_comments}
                    </span>
                </div>
            </div>
        </div>
    );
}

export default CommentsAnalysis;