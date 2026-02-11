import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { io } from 'socket.io-client';
import {
  MessageCircle, Send, ArrowLeft, Users, Search, Circle
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import DashboardNav from '../components/DashboardNav';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Chat() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [store, setStore] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [socket, setSocket] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    const init = async () => {
      try {
        const [userRes, storeRes] = await Promise.all([
          axios.get(`${API}/auth/me`, { withCredentials: true }),
          axios.get(`${API}/stores/my-store`, { withCredentials: true })
        ]);
        setUser(userRes.data);
        setStore(storeRes.data);
      } catch {
        navigate('/demo-login');
      } finally {
        setLoading(false);
      }
    };
    init();
  }, [navigate]);

  // Connect socket when store is loaded
  useEffect(() => {
    if (!store) return;

    const sck = io(BACKEND_URL, {
      path: '/socket.io/',
      transports: ['websocket', 'polling']
    });

    sck.on('connect', () => {
      sck.emit('join_store', { store_id: store.store_id });
    });

    sck.on('new_message', (msg) => {
      setMessages(prev => {
        if (prev.some(m => m.message_id === msg.message_id)) return prev;
        return [...prev, msg];
      });
      // Refresh conversations list
      fetchConversations(store.store_id);
    });

    setSocket(sck);
    fetchConversations(store.store_id);

    return () => {
      sck.disconnect();
    };
  }, [store]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const fetchConversations = async (storeId) => {
    try {
      const res = await axios.get(`${API}/chat/conversations/${storeId}`, { withCredentials: true });
      setConversations(res.data);
    } catch (err) {
      console.error('Failed to fetch conversations:', err);
    }
  };

  const selectCustomer = async (customer) => {
    setSelectedCustomer(customer);
    try {
      const res = await axios.get(
        `${API}/chat/messages/${store.store_id}?customer_id=${customer.customer_id}`
      );
      setMessages(res.data);
      // Mark as read
      if (customer.unread_count > 0) {
        await axios.post(
          `${API}/chat/mark-read?store_id=${store.store_id}&customer_id=${customer.customer_id}`,
          {},
          { withCredentials: true }
        );
        fetchConversations(store.store_id);
      }
    } catch (err) {
      toast.error('Failed to load messages');
    }
  };

  const handleSend = async () => {
    if (!newMessage.trim() || !selectedCustomer) return;

    const payload = {
      store_id: store.store_id,
      customer_id: selectedCustomer.customer_id,
      customer_name: selectedCustomer.customer_name,
      message: newMessage.trim(),
      sender: 'retailer'
    };

    try {
      if (socket?.connected) {
        socket.emit('send_message', payload);
      } else {
        await axios.post(`${API}/chat/send`, payload);
      }
      setNewMessage('');
    } catch (err) {
      toast.error('Failed to send message');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const filteredConversations = conversations.filter(c =>
    c.customer_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const formatTime = (ts) => {
    if (!ts) return '';
    const d = new Date(ts);
    const now = new Date();
    const isToday = d.toDateString() === now.toDateString();
    if (isToday) return d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
    return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col" data-testid="chat-page">
      <DashboardNav user={user} />

      <div className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 flex flex-col" style={{ height: 'calc(100vh - 73px)' }}>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-secondary" data-testid="chat-heading">Customer Chat</h1>
            <p className="text-sm text-muted">Real-time messaging with your customers &mdash; zero transaction fees</p>
          </div>
        </div>

        <div className="flex-1 bg-white border border-slate-200 rounded-xl overflow-hidden flex min-h-0">
          {/* Conversations sidebar */}
          <div className={`w-full sm:w-80 border-r border-slate-200 flex flex-col ${selectedCustomer ? 'hidden sm:flex' : 'flex'}`} data-testid="conversations-sidebar">
            <div className="p-3 border-b border-slate-100">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                <Input
                  placeholder="Search customers..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-9 h-9 text-sm"
                  data-testid="chat-search-input"
                />
              </div>
            </div>

            <div className="flex-1 overflow-y-auto">
              {filteredConversations.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center p-6">
                  <Users className="h-12 w-12 text-slate-300 mb-3" />
                  <p className="text-sm font-medium text-slate-500">No conversations yet</p>
                  <p className="text-xs text-slate-400 mt-1">Customer messages will appear here</p>
                </div>
              ) : (
                filteredConversations.map((conv) => (
                  <button
                    key={conv.customer_id}
                    onClick={() => selectCustomer(conv)}
                    data-testid={`conversation-${conv.customer_id}`}
                    className={`w-full text-left px-4 py-3 border-b border-slate-50 hover:bg-slate-50 transition-colors ${
                      selectedCustomer?.customer_id === conv.customer_id ? 'bg-primary/5 border-l-2 border-l-primary' : ''
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                        <span className="text-sm font-semibold text-primary">
                          {conv.customer_name?.[0]?.toUpperCase() || '?'}
                        </span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-semibold text-secondary truncate">{conv.customer_name}</p>
                          <span className="text-xs text-slate-400 flex-shrink-0 ml-2">{formatTime(conv.last_timestamp)}</span>
                        </div>
                        <div className="flex items-center justify-between mt-0.5">
                          <p className="text-xs text-slate-500 truncate">{conv.last_message}</p>
                          {conv.unread_count > 0 && (
                            <span className="ml-2 flex-shrink-0 bg-primary text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-medium" data-testid={`unread-badge-${conv.customer_id}`}>
                              {conv.unread_count}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </button>
                ))
              )}
            </div>
          </div>

          {/* Chat area */}
          <div className={`flex-1 flex flex-col ${!selectedCustomer ? 'hidden sm:flex' : 'flex'}`} data-testid="chat-area">
            {selectedCustomer ? (
              <>
                {/* Chat header */}
                <div className="px-4 py-3 border-b border-slate-200 flex items-center gap-3 bg-white">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="sm:hidden p-1"
                    onClick={() => setSelectedCustomer(null)}
                    data-testid="chat-back-button"
                  >
                    <ArrowLeft className="h-5 w-5" />
                  </Button>
                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                    <span className="text-sm font-semibold text-primary">
                      {selectedCustomer.customer_name?.[0]?.toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-secondary" data-testid="chat-customer-name">{selectedCustomer.customer_name}</p>
                    <div className="flex items-center gap-1">
                      <Circle className="h-2 w-2 fill-green-500 text-green-500" />
                      <span className="text-xs text-slate-400">Customer</span>
                    </div>
                  </div>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50/50" data-testid="messages-container">
                  {messages.map((msg, idx) => (
                    <div
                      key={msg.message_id || idx}
                      className={`flex ${msg.sender === 'retailer' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[75%] px-3.5 py-2 rounded-2xl text-sm ${
                          msg.sender === 'retailer'
                            ? 'bg-primary text-white rounded-br-md'
                            : 'bg-white border border-slate-200 text-secondary rounded-bl-md'
                        }`}
                        data-testid={`message-${msg.message_id}`}
                      >
                        <p>{msg.message}</p>
                        <p className={`text-[10px] mt-1 ${msg.sender === 'retailer' ? 'text-white/60' : 'text-slate-400'}`}>
                          {formatTime(msg.timestamp)}
                        </p>
                      </div>
                    </div>
                  ))}
                  <div ref={messagesEndRef} />
                </div>

                {/* Input */}
                <div className="px-4 py-3 border-t border-slate-200 bg-white">
                  <div className="flex items-center gap-2">
                    <Input
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      onKeyDown={handleKeyPress}
                      placeholder="Type a message..."
                      className="flex-1 h-10"
                      data-testid="chat-message-input"
                    />
                    <Button
                      onClick={handleSend}
                      disabled={!newMessage.trim()}
                      className="h-10 w-10 p-0 bg-primary hover:bg-primary/90"
                      data-testid="chat-send-button"
                    >
                      <Send className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-center p-8">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                  <MessageCircle className="h-8 w-8 text-primary" />
                </div>
                <h3 className="text-lg font-semibold text-secondary mb-1">Select a conversation</h3>
                <p className="text-sm text-slate-400 max-w-xs">
                  Choose a customer from the sidebar to start chatting. All messages are free with zero transaction fees.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
