import { useEffect, useState } from 'react';

function App() {
  const [message, setMessage] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Отправляем запрос к бэкенду
    fetch("http://localhost:8000/") // адрес бэкенда на порту 8000
      .then(response => {
        if (!response.ok) {
          throw new Error("Не удалось получить данные с сервера");
        }
        return response.json();
      })
      .then(data => setMessage(data.message)) // получаем данные и выводим сообщение
      .catch(error => {
        console.error("Ошибка при запросе:", error);
        setError(error.message);
      });
  }, []);

  return (
    <div>
      {error ? <h2 style={{ color: 'red' }}>{error}</h2> : <h1>{message}</h1>}
    </div>
  );
}

export default App;
