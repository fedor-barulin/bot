import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const formatMessage = (text) => {
    let formatted = text.replace(/\n/g, '<br/>');
    formatted = formatted.replace(/\\\*/g, '*');
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    return formatted;
  };

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    const userMsg = { role: 'user', content: input };
    const historyToSend = messages.map(m => ({ role: m.role, content: m.content }));
    
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const { data } = await axios.post('/chat', { 
        question: userMsg.content,
        history: historyToSend
      });
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
  
  const clearChat = () => {
    if (window.confirm('Вы уверены, что хотите очистить историю сообщений?')) {
      setMessages([]);
    }
  };

  return (
    <div className="chat-container">
      <header className="chat-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Telecom AI Agent</h2>
        <button 
          onClick={clearChat} 
          style={{ background: '#ff4d4f', color: 'white', border: 'none', padding: '8px 16px', borderRadius: '4px', cursor: 'pointer' }}
        >
          🗑 Очистить
        </button>
      </header>
      <div className="chat-messages">
        {messages.map((m, i) => (
          <div key={i} className={`message ${m.role}`}>
            <div className="message-content">
              <strong>{m.role === 'user' ? 'Вы' : 'AI-Инженер'}:</strong>
              <div dangerouslySetInnerHTML={{ __html: formatMessage(m.content) }} />
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
                <button onClick={() => copyToClipboard(m.content)}>📋 Копировать</button>
                <button onClick={() => alert('Оценка отправлена')}>👍</button>
                <button onClick={() => alert('Оценка отправлена')}>👎</button>
              </div>
            )}
          </div>
        ))}
        {loading && <div className="message assistant"><div className="loader">Анализ базы знаний...</div></div>}
        <div ref={messagesEndRef} />
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
