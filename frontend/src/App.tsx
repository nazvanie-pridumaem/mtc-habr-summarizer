import LinkForm from "./LinkForm.tsx";

function App() {

    return (
        <div className="min-h-screen flex flex-col items-center justify-center px-4 bg-gray-100">
            <header className="mb-8">
                <img
                    src="/mtc-icon.png"
                    alt="Логотип"
                    className="mx-auto mt-10 mb-4 w-24 h-24 object-contain"
                />
                <h1 className="text-4xl font-bold text-gray-800 text-center">
                    Как там Хабр?
                </h1>
            </header>
            <main className="w-full max-w-lg">
                <LinkForm />
            </main>
        </div>
    );
}

export default App;
