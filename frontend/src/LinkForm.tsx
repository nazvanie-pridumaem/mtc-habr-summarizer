import { useState } from "react";

interface Section {
    header?: string;
    content: string | string[];
}

interface StreamData {
    type: 'start' | 'processing' | 'section_complete' | 'complete' | 'error' | 'metadata';
    total_sections?: number;
    header?: string;
    section_index?: number;
    section?: Section;
    result?: Section[];
    message?: string;
    title?: string;
}

function LinkForm() {
    const [link, setLink] = useState('');
    const [summary, setSummary] = useState<Section[] | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [streamingStatus, setStreamingStatus] = useState<string | null>(null);
    const [processedSections, setProcessedSections] = useState<(Section | null)[]>([]);
    const [totalSections, setTotalSections] = useState(0);
    const [articleTitle, setArticleTitle] = useState<string | null>(null);

    const handleSubmit = async () => {
        if (!link.trim()) return;

        console.log('Starting submission with link:', link);

        setLoading(true);
        setError('');
        setSummary(null);
        setProcessedSections([]);
        setStreamingStatus(null);
        setTotalSections(0);
        setArticleTitle(null);

        try {
            console.log('Sending request to:', 'http://localhost:8000/summarize');

            const response = await fetch('http://localhost:8000/summarize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ link: link })
            });

            console.log('Response status:', response.status);
            console.log('Response ok:', response.ok);

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Response error:', errorText);
                throw new Error(`Network response was not ok: ${response.status} ${errorText}`);
            }

            if (!response.body) {
                throw new Error('Response body is null');
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();

                if (done) {
                    console.log('Stream completed');
                    break;
                }

                // Декодируем chunk и добавляем к буферу
                buffer += decoder.decode(value, { stream: true });

                // Разбиваем по строкам
                const lines = buffer.split('\n');

                // Оставляем последнюю (возможно неполную) строку в буфере
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (line.trim() === '') continue;

                    if (line.startsWith('data: ')) {
                        try {
                            const jsonStr = line.substring(6);

                            // Пропускаем служебное сообщение [DONE]
                            if (jsonStr === '[DONE]') {
                                console.log('Received [DONE] signal');
                                continue;
                            }

                            const data: StreamData = JSON.parse(jsonStr);
                            console.log('Received event:', data.type, data);

                            switch (data.type) {
                                case 'metadata':
                                    if (data.title) {
                                        setArticleTitle(data.title);
                                    }
                                    break;

                                case 'start':
                                    if (data.total_sections !== undefined) {
                                        setTotalSections(data.total_sections);
                                    }
                                    setStreamingStatus('Начинаем обработку...');
                                    break;

                                case 'processing':
                                    setStreamingStatus(`Обрабатываем: ${data.header || ''}`);
                                    break;

                                case 'section_complete':
                                    if (data.section_index !== undefined && data.section) {
                                        setProcessedSections(prev => {
                                            const newSections = [...prev];
                                            newSections[data.section_index!] = data.section!;
                                            console.log(`Section ${data.section_index} complete, total processed: ${newSections.filter(s => s).length}`);
                                            return newSections;
                                        });
                                    }
                                    break;

                                case 'complete':
                                    console.log('Processing complete, setting summary');
                                    if (data.result) {
                                        setSummary(data.result);
                                    }
                                    setStreamingStatus('Готово!');
                                    setLoading(false);
                                    break;

                                case 'error':
                                    console.error('Received error:', data.message);
                                    setError(data.message || 'Произошла ошибка');
                                    setLoading(false);
                                    break;

                                default:
                                    console.warn('Unknown event type:', data.type);
                            }
                        } catch (e) {
                            console.error('Error parsing SSE data:', e, 'Line:', line);
                        }
                    }
                }
            }

            // Обработка оставшихся данных в буфере
            if (buffer.trim() && buffer.startsWith('data: ')) {
                try {
                    const jsonStr = buffer.substring(6);
                    if (jsonStr !== '[DONE]') {
                        const data: StreamData = JSON.parse(jsonStr);
                        console.log('Processing buffered data:', data);

                        if (data.type === 'complete' && data.result) {
                            setSummary(data.result);
                            setStreamingStatus('Готово!');
                            setLoading(false);
                        }
                    }
                } catch (e) {
                    console.error('Error processing buffered data:', e);
                }
            }

            // Если поток завершился, но loading всё ещё true, сбрасываем его
            if (loading) {
                console.log('Stream ended but loading still true, resetting...');
                setLoading(false);
            }
        } catch (err) {
            console.error('Fetch error:', err);
            setError('Ошибка при обработке ссылки. Проверьте URL и попробуйте снова.');
            console.error('Error:', err);
            setLoading(false);
        }
    }

    const renderContent = (content: string | string[]) => {
        if (Array.isArray(content)) {
            return content.map((paragraph, index) => (
                <p key={index} className="mb-3 leading-relaxed">
                    {paragraph}
                </p>
            ));
        }
        return <p className="leading-relaxed">{content}</p>;
    };

    // Функция для подсчета символов в резюме
    const countCharacters = (sections: Section[]) => {
        return sections.reduce((total, section) => {
            let sectionChars = 0;
            if (section.header) {
                sectionChars += section.header.length;
            }
            if (Array.isArray(section.content)) {
                sectionChars += section.content.join('').length;
            } else if (typeof section.content === 'string') {
                sectionChars += section.content.length;
            }
            return total + sectionChars;
        }, 0);
    };

    // Функция для расчета времени чтения
    // Средняя скорость чтения: 200-250 слов в минуту
    // Среднее количество символов в слове в русском языке: ~6-7
    const calculateReadingTime = (characters: number) => {
        const averageCharsPerWord = 6.5;
        const wordsPerMinute = 225;
        const words = characters / averageCharsPerWord;
        const minutes = Math.ceil(words / wordsPerMinute);

        if (minutes === 1) {
            return '1 минута';
        } else if (minutes < 5) {
            return `${minutes} минуты`;
        } else {
            return `${minutes} минут`;
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8 px-4">
            <style>{`
                @keyframes fadeIn {
                    from {
                        opacity: 0;
                        transform: translateY(20px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                
                .animate-fadeIn {
                    animation: fadeIn 0.5s ease-out forwards;
                }
            `}</style>

            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <div className="text-center mb-8">
                </div>

                {/* Form */}
                <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
                    <div className="space-y-4">
                        <div>
                            <label htmlFor="link" className="block text-sm font-medium text-gray-700 mb-2">
                                URL статьи
                            </label>
                            <input
                                id="link"
                                type="url"
                                value={link}
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                                placeholder="https://habr.com/"
                                onChange={(e) => setLink(e.target.value)}
                                onKeyPress={(e) => {
                                    if (e.key === 'Enter' && !loading && link.trim()) {
                                        handleSubmit();
                                    }
                                }}
                                disabled={loading}
                            />
                        </div>
                        <button
                            onClick={handleSubmit}
                            disabled={loading || !link.trim()}
                            className="w-full bg-gradient-to-r from-blue-400 to-indigo-400 text-white px-6 py-3 rounded-lg font-medium shadow-md hover:from-blue-600 hover:to-indigo-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? (
                                <div className="flex items-center justify-center">
                                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                                    Обрабатываем...
                                </div>
                            ) : (
                                'Суммаризировать'
                            )}
                        </button>
                    </div>

                    {error && (
                        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                            <p className="text-red-700 text-sm">{error}</p>
                        </div>
                    )}
                </div>

                {/* Article Metadata */}
                {(articleTitle || summary) && (
                    <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
                        <div className="space-y-3">
                            {articleTitle && (
                                <h2 className="text-2xl font-bold text-gray-800">
                                    {articleTitle}
                                </h2>
                            )}
                            {summary && (
                                <div className="flex items-center text-gray-600">
                                    <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                    <span>Время чтения: {calculateReadingTime(countCharacters(summary))}</span>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Streaming Status */}
                {loading && (
                    <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-gray-800">Обработка статьи</h3>
                            <div className="text-sm text-gray-500">
                                {processedSections.filter(s => s).length} / {totalSections} разделов
                            </div>
                        </div>

                        {totalSections > 0 && (
                            <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
                                <div
                                    className="bg-gradient-to-r from-blue-500 to-indigo-600 h-2 rounded-full transition-all duration-300"
                                    style={{ width: `${(processedSections.filter(s => s).length / totalSections) * 100}%` }}
                                ></div>
                            </div>
                        )}

                        <div className="flex items-center">
                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500 mr-3"></div>
                            <span className="text-gray-700">{streamingStatus || 'Загрузка...'}</span>
                        </div>
                    </div>
                )}

                {/* Real-time Results */}
                {processedSections.length > 0 && !summary && (
                    <div className="bg-white rounded-xl shadow-lg overflow-hidden mb-8">
                        <div className="bg-gradient-to-r from-blue-500 to-indigo-600 px-6 py-4">
                            <h2 className="text-2xl font-bold text-white">
                                Результаты (в процессе)
                            </h2>
                        </div>

                        <div className="p-6">
                            {processedSections.map((section, index) => (
                                section && (
                                    <div key={index} className="mb-6 last:mb-0 animate-fadeIn">
                                        {section.header ? (
                                            <div className="border-l-4 border-green-500 pl-4 mb-4">
                                                <h3 className="text-xl font-semibold text-gray-800 mb-3 flex items-center">
                                                    {section.header}
                                                    <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                                                        Готово
                                                    </span>
                                                </h3>
                                                <div className="text-gray-700 space-y-3">
                                                    {renderContent(section.content)}
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="bg-green-50 rounded-lg p-4 mb-4">
                                                <div className="text-gray-700 space-y-3">
                                                    {renderContent(section.content)}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )
                            ))}
                        </div>
                    </div>
                )}

                {/* Final Summary Display */}
                {summary && (
                    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
                        <div className="bg-gradient-to-r from-green-500 to-emerald-500 px-6 py-4">
                            <h2 className="text-2xl font-bold text-white flex items-center">
                                Резюме статьи
                                <span className="ml-2 px-3 py-1 bg-white bg-opacity-20 text-gray-800 text-sm rounded-full">
                                    Завершено
                                </span>
                            </h2>
                        </div>

                        <div className="p-6">
                            {summary.map((section, index) => (
                                <div key={index} className="mb-8 last:mb-0">
                                    {section.header ? (
                                        <div className="border-l-4 border-green-500 pl-4 mb-4">
                                            <h3 className="text-xl font-semibold text-gray-800 mb-3">
                                                {section.header}
                                            </h3>
                                            <div className="text-gray-700 space-y-3">
                                                {renderContent(section.content)}
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="bg-green-50 rounded-lg p-4 mb-4">
                                            <div className="text-gray-700 space-y-3">
                                                {renderContent(section.content)}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>

                        {/* Footer with summary stats */}
                        <div className="bg-gray-50 px-6 py-4 border-t">
                            <div className="flex items-center justify-between text-sm text-gray-600">
                                <span>
                                    Количество символов: {countCharacters(summary).toLocaleString('ru-RU')}
                                </span>
                                <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">
                                    ✓ Обработка завершена
                                </span>
                            </div>
                        </div>
                    </div>
                )}

                {/* Empty state */}
                {!summary && !loading && processedSections.length === 0 && (
                    <div className="text-center py-12">
                        <div className="text-gray-400 mb-4">
                            <svg className="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                            </svg>
                        </div>
                        <p className="text-gray-500">
                            Введите ссылку на статью, чтобы получить структурированное резюме
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}

export default LinkForm;