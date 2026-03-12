import './_group.css';
import { useState, useRef, useEffect } from 'react';

interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  sources?: { title: string; section: string; page: number }[];
  time: string;
}

const MOCK_MESSAGES: Message[] = [
  {
    id: 1,
    role: 'assistant',
    content: 'Привет! Я AI-ассистент технической поддержки. Задайте любой вопрос по услугам и тарифам.',
    time: '10:01',
  },
  {
    id: 2,
    role: 'user',
    content: 'Как подключить мобильный интернет?',
    time: '10:02',
  },
  {
    id: 3,
    role: 'assistant',
    content: 'Услуга «Мобильный интернет» уже подключена всем абонентам по умолчанию. Вам нужно только выполнить настройки устройства.\n\n**Способы активации:**\n- USSD: *104*18# вызов\n- SMS: ON на номер 1036\n- Личный кабинет или мобильное приложение\n- Офис продаж',
    sources: [{ title: 'Мобильный Интернет', section: 'Общая информация', page: 1 }],
    time: '10:02',
  },
  {
    id: 4,
    role: 'user',
    content: 'Где офис в Качканаре?',
    time: '10:05',
  },
  {
    id: 5,
    role: 'assistant',
    content: 'В Качканаре офисы расположены по следующим адресам:\n\n1. ул. Свердлова, 22А\n2. ул. Строителей, 8',
    sources: [{ title: 'Офисы продаж', section: 'Качканар', page: 3 }],
    time: '10:05',
  },
];

function formatContent(text: string) {
  const lines = text.split('\n');
  return lines.map((line, i) => {
    const bold = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    return <p key={i} style={{ margin: '2px 0' }} dangerouslySetInnerHTML={{ __html: bold }} />;
  });
}

export function AppleChat() {
  const [messages, setMessages] = useState<Message[]>(MOCK_MESSAGES);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const userMsg: Message = {
      id: Date.now(),
      role: 'user',
      content: input,
      time: new Date().toLocaleTimeString('ru', { hour: '2-digit', minute: '2-digit' }),
    };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    await new Promise(r => setTimeout(r, 1500));

    const aiMsg: Message = {
      id: Date.now() + 1,
      role: 'assistant',
      content: 'Информация отсутствует в базе знаний.',
      time: new Date().toLocaleTimeString('ru', { hour: '2-digit', minute: '2-digit' }),
    };
    setMessages(prev => [...prev, aiMsg]);
    setLoading(false);
  };

  const copy = (msg: Message) => {
    navigator.clipboard.writeText(msg.content).catch(() => {});
    setCopiedId(msg.id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const clear = () => setMessages([]);

  return (
    <div style={{
      minHeight: '100vh',
      background: 'var(--bg-primary)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'flex-start',
      fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", sans-serif',
    }}>
      <div style={{
        width: 390,
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        background: 'var(--bg-primary)',
        position: 'relative',
      }}>

        {/* Header */}
        <div style={{
          background: 'rgba(246,247,249,0.85)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          borderBottom: '0.5px solid var(--border)',
          padding: '12px 20px 10px',
          position: 'sticky',
          top: 0,
          zIndex: 10,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{
              width: 40, height: 40, borderRadius: '50%',
              background: 'linear-gradient(135deg, var(--brand-orange) 0%, #ff8c42 100%)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              flexShrink: 0,
              boxShadow: '0 2px 8px rgba(243,112,33,0.35)',
            }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 14.5v-9l6 4.5-6 4.5z" fill="white"/>
              </svg>
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 600, fontSize: 16, color: 'var(--text-primary)', lineHeight: 1.2 }}>
                AI-Инженер
              </div>
              <div style={{ fontSize: 12, color: 'var(--accent-green)', fontWeight: 500 }}>
                ● Онлайн
              </div>
            </div>
            <button
              onClick={clear}
              style={{
                background: 'none', border: 'none', cursor: 'pointer',
                color: 'var(--text-muted)', padding: 6, borderRadius: 8,
                display: 'flex', alignItems: 'center',
              }}
              title="Очистить чат"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/>
              </svg>
            </button>
          </div>
        </div>

        {/* Messages */}
        <div style={{
          flex: 1, overflowY: 'auto', padding: '16px 12px',
          display: 'flex', flexDirection: 'column', gap: 4,
        }}>
          {messages.length === 0 && (
            <div style={{
              textAlign: 'center', color: 'var(--text-muted)',
              fontSize: 14, marginTop: 48,
              display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12,
            }}>
              <div style={{
                width: 64, height: 64, borderRadius: '50%',
                background: 'linear-gradient(135deg, var(--brand-orange), #ff8c42)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                opacity: 0.5,
              }}>
                <svg width="30" height="30" viewBox="0 0 24 24" fill="white">
                  <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
                </svg>
              </div>
              <div>Начните диалог — задайте вопрос<br/>по услугам или тарифам</div>
            </div>
          )}

          {messages.map((msg, idx) => {
            const isUser = msg.role === 'user';
            const showDate = idx === 0 || messages[idx - 1]?.time !== msg.time;

            return (
              <div key={msg.id}>
                {showDate && idx > 0 && (
                  <div style={{
                    textAlign: 'center', fontSize: 11, color: 'var(--text-muted)',
                    margin: '8px 0 4px', fontWeight: 500,
                  }}>
                    {msg.time}
                  </div>
                )}
                {idx === 0 && (
                  <div style={{
                    textAlign: 'center', fontSize: 11, color: 'var(--text-muted)',
                    margin: '0 0 8px', fontWeight: 500,
                  }}>
                    {msg.time}
                  </div>
                )}

                <div style={{
                  display: 'flex',
                  justifyContent: isUser ? 'flex-end' : 'flex-start',
                  alignItems: 'flex-end',
                  gap: 6,
                  marginBottom: 2,
                }}>
                  {!isUser && (
                    <div style={{
                      width: 28, height: 28, borderRadius: '50%', flexShrink: 0,
                      background: 'linear-gradient(135deg, var(--brand-orange), #ff8c42)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      boxShadow: '0 1px 4px rgba(243,112,33,0.3)',
                    }}>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="white">
                        <path d="M12 2a5 5 0 100 10A5 5 0 0012 2zM2 20c0-4 4.5-7 10-7s10 3 10 7"/>
                      </svg>
                    </div>
                  )}

                  <div style={{ maxWidth: '78%', position: 'relative' }}>
                    <div style={{
                      background: isUser
                        ? 'var(--brand-orange)'
                        : 'var(--bg-white)',
                      color: isUser ? 'white' : 'var(--text-primary)',
                      padding: '10px 14px',
                      borderRadius: isUser
                        ? '20px 20px 4px 20px'
                        : '20px 20px 20px 4px',
                      fontSize: 15,
                      lineHeight: 1.45,
                      boxShadow: isUser
                        ? '0 2px 8px rgba(243,112,33,0.30)'
                        : 'var(--shadow-sm)',
                      position: 'relative',
                    }}>
                      <div>{formatContent(msg.content)}</div>

                      {msg.sources && msg.sources.length > 0 && (
                        <div style={{
                          marginTop: 8, paddingTop: 8,
                          borderTop: '0.5px solid rgba(0,0,0,0.08)',
                          fontSize: 12, color: 'var(--text-secondary)',
                          display: 'flex', flexDirection: 'column', gap: 2,
                        }}>
                          {msg.sources.map((s, i) => (
                            <div key={i} style={{
                              display: 'flex', alignItems: 'center', gap: 4,
                            }}>
                              <span style={{
                                background: 'var(--brand-orange-light)',
                                color: 'var(--brand-orange)',
                                borderRadius: 6, padding: '1px 6px',
                                fontWeight: 600, fontSize: 11,
                              }}>
                                {s.title}
                              </span>
                              <span style={{ color: 'var(--text-muted)' }}>
                                {s.section} · стр. {s.page}
                              </span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    {!isUser && (
                      <div style={{
                        display: 'flex', gap: 4, marginTop: 4,
                        paddingLeft: 2,
                      }}>
                        <button
                          onClick={() => copy(msg)}
                          style={{
                            background: 'none', border: 'none', cursor: 'pointer',
                            color: copiedId === msg.id ? 'var(--accent-green)' : 'var(--text-muted)',
                            padding: '3px 8px', borderRadius: 8, fontSize: 12,
                            display: 'flex', alignItems: 'center', gap: 3,
                            transition: 'color 0.2s',
                          }}
                        >
                          {copiedId === msg.id ? (
                            <>
                              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                                <polyline points="20 6 9 17 4 12"/>
                              </svg>
                              Скопировано
                            </>
                          ) : (
                            <>
                              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                                <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
                              </svg>
                              Копировать
                            </>
                          )}
                        </button>
                        <button style={{
                          background: 'none', border: 'none', cursor: 'pointer',
                          color: 'var(--text-muted)', padding: '3px 6px', borderRadius: 8,
                          fontSize: 14,
                        }}>👍</button>
                        <button style={{
                          background: 'none', border: 'none', cursor: 'pointer',
                          color: 'var(--text-muted)', padding: '3px 6px', borderRadius: 8,
                          fontSize: 14,
                        }}>👎</button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}

          {loading && (
            <div style={{ display: 'flex', alignItems: 'flex-end', gap: 6, marginBottom: 2 }}>
              <div style={{
                width: 28, height: 28, borderRadius: '50%', flexShrink: 0,
                background: 'linear-gradient(135deg, var(--brand-orange), #ff8c42)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="white">
                  <path d="M12 2a5 5 0 100 10A5 5 0 0012 2zM2 20c0-4 4.5-7 10-7s10 3 10 7"/>
                </svg>
              </div>
              <div style={{
                background: 'var(--bg-white)', borderRadius: '20px 20px 20px 4px',
                padding: '12px 18px', boxShadow: 'var(--shadow-sm)',
                display: 'flex', gap: 5, alignItems: 'center',
              }}>
                {[0, 1, 2].map(i => (
                  <div key={i} style={{
                    width: 7, height: 7, borderRadius: '50%',
                    background: 'var(--brand-orange)',
                    animation: 'bounce 1.4s ease-in-out infinite',
                    animationDelay: `${i * 0.2}s`,
                    opacity: 0.7,
                  }}/>
                ))}
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <div style={{
          background: 'rgba(246,247,249,0.92)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          borderTop: '0.5px solid var(--border)',
          padding: '10px 12px 16px',
          position: 'sticky', bottom: 0,
        }}>
          <div style={{
            display: 'flex', gap: 8, alignItems: 'flex-end',
          }}>
            <div style={{
              flex: 1,
              background: 'var(--bg-white)',
              borderRadius: 22,
              border: '1px solid var(--border)',
              boxShadow: 'var(--shadow-sm)',
              display: 'flex', alignItems: 'center',
              padding: '2px 4px 2px 14px',
              minHeight: 44,
            }}>
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSend()}
                placeholder="Спросите технический вопрос..."
                style={{
                  flex: 1, border: 'none', outline: 'none',
                  background: 'transparent', fontSize: 15,
                  color: 'var(--text-primary)',
                  fontFamily: 'inherit', padding: '8px 0',
                }}
              />
            </div>
            <button
              onClick={handleSend}
              disabled={!input.trim() || loading}
              style={{
                width: 44, height: 44, borderRadius: '50%', flexShrink: 0,
                background: input.trim() && !loading
                  ? 'var(--brand-orange)'
                  : 'var(--border)',
                border: 'none', cursor: input.trim() && !loading ? 'pointer' : 'default',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                transition: 'background 0.2s, transform 0.1s',
                boxShadow: input.trim() && !loading
                  ? '0 2px 8px rgba(243,112,33,0.35)'
                  : 'none',
              }}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M22 2L11 13M22 2L15 22 11 13 2 9l20-7z"
                  stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          </div>
          <div style={{
            textAlign: 'center', marginTop: 8, fontSize: 11,
            color: 'var(--text-muted)',
          }}>
            Telecom AI · Корпоративная база знаний
          </div>
        </div>
      </div>

      <style>{`
        @keyframes bounce {
          0%, 60%, 100% { transform: translateY(0); }
          30% { transform: translateY(-6px); }
        }
      `}</style>
    </div>
  );
}
