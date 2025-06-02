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
        <div>
            <form>
                <input type="text" value={link} onChange={(e) => setLink(e.target.value)} />
                <button type="submit" onClick={handleSubmit}>Суммаризировать</button>
            </form>
            <div>
                <p>{answer}</p>
            </div>
        </div>
    );
}

export default LinkForm;