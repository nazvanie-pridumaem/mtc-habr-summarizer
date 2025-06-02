import { useState } from "react";
import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000'
})

function LinkForm() {
    const [link, setLink] = useState('');
    const [answer, setAnswer] = useState('');

    const handleSubmit = async (e: { preventDefault: () => void; }) => {
        e.preventDefault();
        const response = await api.post('/summarize', { link: link });
        setAnswer(JSON.stringify(response.data));
    }

    return (
        <div className="w-full max-w-md mx-auto">
            <form>
                <input type="text" value={link}
                       className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                       placeholder="https://habr.com"
                       onChange={(e) => setLink(e.target.value)} />
                <button type="submit"
                        className="cursor-pointer transition-all bg-blue-500 text-white px-6 py-2 rounded-lg border-blue-600 border-b-[4px] hover:brightness-110 hover:-translate-y-[1px] hover:border-b-[6px] active:border-b-[2px] active:brightness-90 active:translate-y-[2px] mx-auto block mt-4"
                        onClick={handleSubmit}>Суммаризировать</button>
            </form>
            <div>
                {answer && (
                    <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                        <p className="text-gray-700">{answer}</p>
                    </div>
                )}
            </div>
        </div>
    );
}

export default LinkForm;