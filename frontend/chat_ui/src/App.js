import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const SUGGESTED = [
  'Как подключить роуминг?',
  'Тарифы на безлимитный интернет',
  'Перенести номер к Мотив',
  'Блокировка SIM-карты',
];

function extractQuickReplies(text) {
  if (!text.includes('?')) return [];
  const lines = text.split('\n').map((l) => l.trim()).filter(Boolean);
  const options = [];
  for (const line of lines) {
    const match = line.match(/^(?:\d+[.)]\s*|-\s*|•\s*)(.+)/);
    if (match) {
      const option = match[1].replace(/\*\*/g, '').trim();
      if (option.length > 0 && option.length < 80) options.push(option);
    }
  }
  return options;
}

function formatContent(text) {
  const lines = text.split('\n');
  return lines.map((line, i) => {
    const bold = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    return (
      <p
        key={i}
        style={{ margin: '2px 0', lineHeight: 1.5 }}
        dangerouslySetInnerHTML={{ __html: bold }}
      />
    );
  });
}

function SendIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
      <path
        d="M22 2L11 13M22 2L15 22 11 13 2 9l20-7z"
        stroke="white"
        strokeWidth="2.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function CopyIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="9" y="9" width="13" height="13" rx="2" />
      <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [copiedId, setCopiedId] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const now = () =>
    new Date().toLocaleTimeString('ru', { hour: '2-digit', minute: '2-digit' });

  const handleSend = async (text) => {
    const msg = text !== undefined ? text : input;
    if (!msg.trim() || loading) return;

    const userMsg = { id: Date.now(), role: 'user', content: msg, time: now() };
    const historyToSend = messages.map((m) => ({ role: m.role, content: m.content }));

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const { data } = await axios.post('/chat', {
        question: msg,
        history: historyToSend,
      });
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content: data.answer,
          sources: data.sources,
          time: now(),
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content: 'Ошибка сервера. Попробуйте ещё раз.',
          time: now(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const copy = (msg) => {
    navigator.clipboard.writeText(msg.content).catch(() => {});
    setCopiedId(msg.id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div
      style={{
        width: '100vw',
        height: '100vh',
        display: 'flex',
        background: 'var(--bg-primary)',
        fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", sans-serif',
        overflow: 'hidden',
      }}
    >
      {/* Main chat area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

        {/* Top bar */}
        <div
          style={{
            height: 56,
            background: 'rgba(246,247,249,0.9)',
            backdropFilter: 'blur(20px)',
            borderBottom: '0.5px solid var(--border)',
            display: 'flex',
            alignItems: 'center',
            padding: '0 24px',
            gap: 12,
            flexShrink: 0,
          }}
        >
          <div
            style={{
              width: 36, height: 36, borderRadius: '50%',
              background: 'linear-gradient(135deg, var(--brand-orange), #ff8c42)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '0 2px 6px rgba(243,112,33,0.3)',
            }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="white">
              <path d="M12 2a5 5 0 100 10A5 5 0 0012 2zM2 20c0-4 4.5-7 10-7s10 3 10 7" />
            </svg>
          </div>
          <div>
            <div style={{ fontWeight: 600, fontSize: 15, color: 'var(--text-primary)' }}>Мотив AI</div>
            <div style={{ fontSize: 12, color: 'var(--accent-green)', fontWeight: 500 }}>
              ● Онлайн · Корпоративная база знаний
            </div>
          </div>
          <div style={{ flex: 1 }} />
          <button
            onClick={() => setMessages([])}
            style={{
              display: 'flex', alignItems: 'center', gap: 6,
              background: 'none', border: '1px solid var(--border)',
              borderRadius: 8, padding: '5px 12px', cursor: 'pointer',
              color: 'var(--text-secondary)', fontSize: 13,
            }}
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="3 6 5 6 21 6" />
              <path d="M19 6l-1 14H6L5 6" />
            </svg>
            Очистить чат
          </button>
        </div>

        {/* Messages */}
        <div
          style={{
            flex: 1, overflowY: 'auto',
            padding: '24px 0',
            display: 'flex', flexDirection: 'column',
          }}
        >
          <div style={{ maxWidth: 780, width: '100%', margin: '0 auto', padding: '0 32px' }}>

            {/* Empty state */}
            {messages.length === 0 && (
              <div
                style={{
                  textAlign: 'center', paddingTop: 80,
                  display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16,
                }}
              >
                <div
                  style={{
                    width: 72, height: 72, borderRadius: 20,
                    background: 'linear-gradient(135deg, var(--brand-orange), #ff8c42)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    boxShadow: '0 4px 16px rgba(243,112,33,0.3)',
                  }}
                >
                  <svg width="34" height="34" viewBox="0 0 24 24" fill="white">
                    <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z" />
                  </svg>
                </div>
                <div>
                  <div style={{ fontSize: 20, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 6 }}>
                    Мотив AI готов к работе
                  </div>
                  <div style={{ fontSize: 14, color: 'var(--text-muted)' }}>
                    Задайте вопрос по услугам, тарифам или работе оборудования
                  </div>
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center', marginTop: 8 }}>
                  {SUGGESTED.map((s) => (
                    <button
                      key={s}
                      onClick={() => handleSend(s)}
                      style={{
                        background: 'var(--bg-white)', border: '1px solid var(--border)',
                        borderRadius: 20, padding: '8px 16px',
                        color: 'var(--text-primary)', fontSize: 13, cursor: 'pointer',
                        boxShadow: 'var(--shadow-sm)', transition: 'box-shadow 0.15s',
                      }}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Message list */}
            {messages.map((msg, idx) => {
              const isUser = msg.role === 'user';
              const prevMsg = messages[idx - 1];
              const showTime = !prevMsg || prevMsg.time !== msg.time || prevMsg.role !== msg.role;
              const isLastMsg = idx === messages.length - 1;
              const quickReplies = !isUser && isLastMsg && !loading
                ? extractQuickReplies(msg.content)
                : [];

              return (
                <div key={msg.id} style={{ marginBottom: 16 }}>
                  {idx === 0 && (
                    <div
                      style={{
                        textAlign: 'center', fontSize: 11,
                        color: 'var(--text-muted)', marginBottom: 12, fontWeight: 500,
                      }}
                    >
                      {msg.time}
                    </div>
                  )}
                  {showTime && idx > 0 && (
                    <div
                      style={{
                        textAlign: 'center', fontSize: 11,
                        color: 'var(--text-muted)', margin: '16px 0 12px', fontWeight: 500,
                      }}
                    >
                      {msg.time}
                    </div>
                  )}

                  <div
                    style={{
                      display: 'flex',
                      flexDirection: isUser ? 'row-reverse' : 'row',
                      gap: 10,
                      alignItems: 'flex-start',
                    }}
                  >
                    {/* AI avatar */}
                    {!isUser && (
                      <div
                        style={{
                          width: 32, height: 32, borderRadius: '50%', flexShrink: 0, marginTop: 2,
                          background: 'linear-gradient(135deg, var(--brand-orange), #ff8c42)',
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                          boxShadow: '0 2px 6px rgba(243,112,33,0.3)',
                        }}
                      >
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="white">
                          <path d="M12 2a5 5 0 100 10A5 5 0 0012 2zM2 20c0-4 4.5-7 10-7s10 3 10 7" />
                        </svg>
                      </div>
                    )}

                    <div style={{ maxWidth: '68%' }}>
                      {/* Bubble */}
                      <div
                        style={{
                          background: isUser ? '#e8734a' : 'var(--bg-white)',
                          color: isUser ? 'white' : 'var(--text-primary)',
                          padding: '12px 16px',
                          borderRadius: isUser ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
                          fontSize: 14,
                          lineHeight: 1.55,
                          boxShadow: isUser
                            ? '0 2px 8px rgba(180,80,40,0.18)'
                            : 'var(--shadow-sm)',
                        }}
                      >
                        {formatContent(msg.content)}

                        {msg.sources && msg.sources.length > 0 && (
                          <div
                            style={{
                              marginTop: 10, paddingTop: 10,
                              borderTop: '0.5px solid rgba(0,0,0,0.07)',
                              display: 'flex', flexWrap: 'wrap', gap: 6,
                            }}
                          >
                            {msg.sources.map((s, i) => (
                              <div
                                key={i}
                                style={{
                                  display: 'flex', alignItems: 'center', gap: 5,
                                  background: 'var(--brand-orange-light)',
                                  borderRadius: 8, padding: '3px 8px',
                                }}
                              >
                                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="var(--brand-orange)" strokeWidth="2.5">
                                  <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                                  <polyline points="14 2 14 8 20 8" />
                                </svg>
                                <span style={{ fontSize: 11, color: 'var(--brand-orange)', fontWeight: 600 }}>
                                  {s.title}
                                </span>
                                <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                                  {s.section} · стр. {s.page}
                                </span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>

                      {/* Actions */}
                      {!isUser && (
                        <div>
                          <div style={{ display: 'flex', gap: 4, marginTop: 6, paddingLeft: 2 }}>
                            <button
                              onClick={() => copy(msg)}
                              style={{
                                display: 'flex', alignItems: 'center', gap: 4,
                                background: 'none', border: 'none', cursor: 'pointer',
                                color: copiedId === msg.id ? 'var(--accent-green)' : 'var(--text-muted)',
                                padding: '3px 8px', borderRadius: 6, fontSize: 12,
                                transition: 'color 0.2s',
                              }}
                            >
                              {copiedId === msg.id ? <CheckIcon /> : <CopyIcon />}
                              {copiedId === msg.id ? 'Скопировано' : 'Копировать'}
                            </button>
                            <button
                              style={{
                                background: 'none', border: 'none', cursor: 'pointer',
                                color: 'var(--text-muted)', padding: '3px 6px', borderRadius: 6, fontSize: 14,
                              }}
                            >
                              👍
                            </button>
                            <button
                              style={{
                                background: 'none', border: 'none', cursor: 'pointer',
                                color: 'var(--text-muted)', padding: '3px 6px', borderRadius: 6, fontSize: 14,
                              }}
                            >
                              👎
                            </button>
                          </div>

                          {/* Quick reply chips */}
                          {quickReplies.length > 0 && (
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 10, paddingLeft: 2 }}>
                              {quickReplies.map((reply) => (
                                <button
                                  key={reply}
                                  onClick={() => handleSend(reply)}
                                  style={{
                                    background: 'var(--bg-white)',
                                    border: '1.5px solid var(--brand-orange)',
                                    borderRadius: 20,
                                    padding: '6px 14px',
                                    color: 'var(--brand-orange)',
                                    fontSize: 13,
                                    fontWeight: 500,
                                    cursor: 'pointer',
                                    transition: 'background 0.15s, color 0.15s',
                                    fontFamily: 'inherit',
                                  }}
                                  onMouseEnter={(e) => {
                                    e.currentTarget.style.background = 'var(--brand-orange)';
                                    e.currentTarget.style.color = 'white';
                                  }}
                                  onMouseLeave={(e) => {
                                    e.currentTarget.style.background = 'var(--bg-white)';
                                    e.currentTarget.style.color = 'var(--brand-orange)';
                                  }}
                                >
                                  {reply}
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}

            {/* Loading indicator */}
            {loading && (
              <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start', marginBottom: 16 }}>
                <div
                  style={{
                    width: 32, height: 32, borderRadius: '50%', flexShrink: 0,
                    background: 'linear-gradient(135deg, var(--brand-orange), #ff8c42)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                  }}
                >
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="white">
                    <path d="M12 2a5 5 0 100 10A5 5 0 0012 2zM2 20c0-4 4.5-7 10-7s10 3 10 7" />
                  </svg>
                </div>
                <div
                  style={{
                    background: 'var(--bg-white)', borderRadius: '18px 18px 18px 4px',
                    padding: '14px 20px', boxShadow: 'var(--shadow-sm)',
                    display: 'flex', gap: 5, alignItems: 'center',
                  }}
                >
                  {[0, 1, 2].map((i) => (
                    <div
                      key={i}
                      style={{
                        width: 7, height: 7, borderRadius: '50%',
                        background: 'var(--brand-orange)',
                        animation: 'bounce 1.4s ease-in-out infinite',
                        animationDelay: `${i * 0.2}s`,
                        opacity: 0.7,
                      }}
                    />
                  ))}
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input area */}
        <div
          style={{
            background: 'rgba(246,247,249,0.95)',
            backdropFilter: 'blur(20px)',
            borderTop: '0.5px solid var(--border)',
            padding: '14px 32px 16px',
            flexShrink: 0,
          }}
        >
          <div style={{ maxWidth: 780, margin: '0 auto' }}>
            {/* Suggested chips (shown when there are messages) */}
            {messages.length > 0 && (
              <div style={{ display: 'flex', gap: 6, marginBottom: 10, flexWrap: 'wrap' }}>
                {SUGGESTED.slice(0, 3).map((s) => (
                  <button
                    key={s}
                    onClick={() => handleSend(s)}
                    style={{
                      background: 'var(--bg-white)', border: '1px solid var(--border)',
                      borderRadius: 14, padding: '5px 12px',
                      color: 'var(--text-secondary)', fontSize: 12, cursor: 'pointer',
                    }}
                  >
                    {s}
                  </button>
                ))}
              </div>
            )}

            <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
              <div
                style={{
                  flex: 1,
                  background: 'var(--bg-white)',
                  borderRadius: 14,
                  border: '1px solid var(--border)',
                  boxShadow: 'var(--shadow-sm)',
                  display: 'flex', alignItems: 'center',
                  padding: '0 16px',
                  height: 48,
                }}
              >
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                  placeholder="Задайте свой вопрос"
                  style={{
                    flex: 1, border: 'none', outline: 'none',
                    background: 'transparent', fontSize: 15,
                    color: 'var(--text-primary)', fontFamily: 'inherit',
                  }}
                />
              </div>
              <button
                onClick={() => handleSend()}
                disabled={!input.trim() || loading}
                style={{
                  height: 48, paddingLeft: 20, paddingRight: 20,
                  borderRadius: 14, border: 'none',
                  background: input.trim() && !loading ? 'var(--brand-orange)' : 'var(--border)',
                  cursor: input.trim() && !loading ? 'pointer' : 'default',
                  display: 'flex', alignItems: 'center', gap: 8,
                  color: 'white', fontSize: 14, fontWeight: 600,
                  boxShadow: input.trim() && !loading ? '0 2px 10px rgba(243,112,33,0.35)' : 'none',
                  transition: 'all 0.2s',
                  fontFamily: 'inherit',
                }}
              >
                <SendIcon />
                Отправить
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
