import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const { data } = await axios.post('/chat', { question: userMsg.content });
      setMessages(prev => [...prev, { role: 'assistant', content: data.answer, sources: data.sources }]);
    } catch (e) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Ошибка сервера' }]);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('Ответ скопирован!');
  };

  return (
    <div className="chat-container">
      <header className="chat-header">
        <h2>Telecom AI Agent</h2>
      </header>
      <div className="chat-messages">
        {messages.map((m, i) => (
          <div key={i} className={`message ${m.role}`}>
            <div className="message-content">
              <strong>{m.role === 'user' ? 'Вы' : 'AI-Инженер'}:</strong>
              <div dangerouslySetInnerHTML={{ __html: m.content.replace(/\n/g, '<br/>') }} />
              {m.sources && m.sources.length > 0 && (
                <div className="sources">
                  <br /><strong>Источники:</strong>
                  <ul>
                    {m.sources.map((s, idx) => (
                      <li key={idx}>[{s.title}] Раздел: {s.section}, Стр: {s.page}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
            {m.role === 'assistant' && (
              <div className="message-actions">
                <button onClick={() => copyToClipboard(m.content)}>📋 Copy</button>
                <button onClick={() => alert('Оценка отправлена')}>👍</button>
                <button onClick={() => alert('Оценка отправлена')}>👎</button>
              </div>
            )}
          </div>
        ))}
        {loading && <div className="message assistant"><div className="loader">Анализ базы знаний...</div></div>}
      </div>
      <div className="chat-input-area">
        <input 
          type="text" 
          value={input} 
          onChange={e => setInput(e.target.value)} 
          onKeyPress={e => e.key === 'Enter' && sendMessage()}
          placeholder="Спросите технический вопрос..." 
        />
        <button onClick={sendMessage}>Отправить</button>
      </div>
    </div>
  );
}

export default App;
