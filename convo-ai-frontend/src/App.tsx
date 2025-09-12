import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Mic, 
  MicOff, 
  Send, 
  Eye, 
  EyeOff, 
  Copy, 
  Settings,
  Brain,
  Camera,
  Zap,
  Sparkles
} from 'lucide-react';
import io, { Socket } from 'socket.io-client';
import './App.css';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

interface ScreenData {
  image: string;
  analysis: string;
  summary: string;
}

const App: React.FC = () => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isScreenCapture, setIsScreenCapture] = useState(false);
  const [screenData, setScreenData] = useState<ScreenData | null>(null);
  const [isTyping, setIsTyping] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';
      
      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInputMessage(transcript);
        setIsListening(false);
      };
      
      recognitionRef.current.onerror = () => {
        setIsListening(false);
      };
      
      setSpeechSupported(true);
    }
  }, []);

  // Initialize socket connection
  useEffect(() => {
    const newSocket = io('http://localhost:8000');
    
    newSocket.on('connect', () => {
      setIsConnected(true);
      console.log('Connected to server');
    });
    
    newSocket.on('disconnect', () => {
      setIsConnected(false);
      console.log('Disconnected from server');
    });
    
    newSocket.on('ai_response', (data: { response: string }) => {
      setIsTyping(false);
      addMessage(data.response, 'ai');
    });
    
    setSocket(newSocket);
    
    return () => {
      newSocket.close();
    };
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const addMessage = (text: string, sender: 'user' | 'ai') => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text,
      sender,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !socket) return;
    
    addMessage(inputMessage, 'user');
    setIsTyping(true);
    
    socket.emit('user_message', {
      message: inputMessage,
      timestamp: new Date().toISOString()
    });
    
    setInputMessage('');
  };

  const toggleSpeechRecognition = () => {
    if (!recognitionRef.current) return;
    
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const toggleScreenCapture = async () => {
    try {
      if (isScreenCapture) {
        await fetch('http://localhost:8000/api/screen/stop', { method: 'POST' });
        setIsScreenCapture(false);
        setScreenData(null);
      } else {
        const response = await fetch('http://localhost:8000/api/screen/start', { method: 'POST' });
        if (response.ok) {
          setIsScreenCapture(true);
          startScreenUpdate();
        }
      }
    } catch (error) {
      console.error('Screen capture error:', error);
    }
  };

  const startScreenUpdate = () => {
    const interval = setInterval(async () => {
      if (!isScreenCapture) {
        clearInterval(interval);
        return;
      }
      
      try {
        const response = await fetch('http://localhost:8000/api/screen/image');
        if (response.ok) {
          const data = await response.json();
          setScreenData(prev => ({
            ...prev,
            image: data.image,
            analysis: data.analysis || prev?.analysis,
            summary: data.summary || prev?.summary
          }));
        }
      } catch (error) {
        console.error('Screen update error:', error);
      }
    }, 1000);
  };

  const copyLastMessage = () => {
    const lastMessage = messages[messages.length - 1];
    if (lastMessage && lastMessage.sender === 'ai') {
      navigator.clipboard.writeText(lastMessage.text);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 relative overflow-hidden">
      {/* Floating particles */}
      <div className="absolute inset-0 pointer-events-none">
        {[...Array(5)].map((_, i) => (
          <motion.div
            key={i}
            className="particle w-2 h-2 bg-white opacity-20 rounded-full"
            animate={{
              y: [0, -20, 0],
              x: [0, 10, 0],
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: 6,
              repeat: Infinity,
              delay: i * 1.2,
            }}
          />
        ))}
      </div>

      {/* Header */}
      <motion.header 
        className="glass p-4 mb-6"
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      >
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <motion.div 
            className="flex items-center space-x-3"
            whileHover={{ scale: 1.05 }}
          >
            <motion.div
              className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center"
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            >
              <Brain className="w-6 h-6 text-white" />
            </motion.div>
            <div>
              <h1 className="text-2xl font-bold gradient-text">Convo AI</h1>
              <p className="text-sm text-gray-300">Intelligent Screen Analysis Assistant</p>
            </div>
          </motion.div>
          
          <div className="flex items-center space-x-4">
            <motion.div
              className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}
              animate={{ scale: isConnected ? [1, 1.2, 1] : 1 }}
              transition={{ duration: 2, repeat: Infinity }}
            />
            <span className="text-sm text-gray-300">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-4">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chat Area */}
          <motion.div 
            className="lg:col-span-2"
            initial={{ x: -100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <div className="glass rounded-2xl p-6 h-[600px] flex flex-col">
              {/* Messages */}
              <div className="flex-1 overflow-y-auto space-y-4 mb-4">
                <AnimatePresence>
                  {messages.map((message) => (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 20, scale: 0.9 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: -20, scale: 0.9 }}
                      transition={{ duration: 0.3 }}
                      className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl ${
                        message.sender === 'user' 
                          ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white' 
                          : 'glass text-white'
                      }`}>
                        <p className="text-sm">{message.text}</p>
                        <p className="text-xs opacity-70 mt-1">
                          {message.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
                
                {isTyping && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex justify-start"
                  >
                    <div className="glass px-4 py-3 rounded-2xl">
                      <div className="flex space-x-1">
                        <div className="typing-indicator"></div>
                        <div className="typing-indicator"></div>
                        <div className="typing-indicator"></div>
                      </div>
                    </div>
                  </motion.div>
                )}
                
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <motion.div 
                className="flex items-center space-x-3"
                initial={{ y: 100, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.8, delay: 0.4 }}
              >
                <div className="flex-1 relative">
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask me anything..."
                    className="w-full px-4 py-3 glass rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
                
                <motion.button
                  onClick={sendMessage}
                  disabled={!inputMessage.trim()}
                  className="p-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl text-white disabled:opacity-50 disabled:cursor-not-allowed glow"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Send className="w-5 h-5" />
                </motion.button>
              </motion.div>
            </div>
          </motion.div>

          {/* Sidebar */}
          <motion.div 
            className="space-y-6"
            initial={{ x: 100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.3 }}
          >
            {/* Controls */}
            <div className="glass rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                <Zap className="w-5 h-5 mr-2 text-yellow-400" />
                Quick Actions
              </h3>
              
              <div className="space-y-3">
                <motion.button
                  onClick={toggleSpeechRecognition}
                  disabled={!speechSupported}
                  className={`w-full flex items-center justify-center space-x-2 p-3 rounded-xl transition-all ${
                    isListening 
                      ? 'bg-red-500 text-white' 
                      : 'glass text-white hover:bg-white/20'
                  }`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                  <span>{isListening ? 'Stop Listening' : 'Voice Input'}</span>
                </motion.button>

                <motion.button
                  onClick={toggleScreenCapture}
                  className={`w-full flex items-center justify-center space-x-2 p-3 rounded-xl transition-all ${
                    isScreenCapture 
                      ? 'bg-green-500 text-white' 
                      : 'glass text-white hover:bg-white/20'
                  }`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {isScreenCapture ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  <span>{isScreenCapture ? 'Stop Screen View' : 'Start Screen View'}</span>
                </motion.button>

                <motion.button
                  onClick={copyLastMessage}
                  className="w-full flex items-center justify-center space-x-2 p-3 glass text-white hover:bg-white/20 rounded-xl transition-all"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Copy className="w-5 h-5" />
                  <span>Copy Last Response</span>
                </motion.button>
              </div>
            </div>

            {/* Screen Analysis */}
            {isScreenCapture && screenData && (
              <motion.div 
                className="glass rounded-2xl p-6"
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.5 }}
              >
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                  <Camera className="w-5 h-5 mr-2 text-blue-400" />
                  Screen Analysis
                </h3>
                
                {screenData.image && (
                  <div className="mb-4">
                    <img 
                      src={`data:image/png;base64,${screenData.image}`} 
                      alt="Screen capture"
                      className="w-full rounded-lg border border-white/20"
                    />
                  </div>
                )}
                
                {screenData.analysis && (
                  <div className="text-sm text-gray-300">
                    <p className="mb-2 font-medium text-white">Analysis:</p>
                    <p>{screenData.analysis}</p>
                  </div>
                )}
              </motion.div>
            )}

            {/* Status */}
            <motion.div 
              className="glass rounded-2xl p-6"
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.5 }}
            >
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                <Sparkles className="w-5 h-5 mr-2 text-purple-400" />
                Status
              </h3>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-300">Connection:</span>
                  <span className={isConnected ? 'text-green-400' : 'text-red-400'}>
                    {isConnected ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Voice:</span>
                  <span className={speechSupported ? 'text-green-400' : 'text-red-400'}>
                    {speechSupported ? 'Available' : 'Unavailable'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Screen:</span>
                  <span className={isScreenCapture ? 'text-green-400' : 'text-gray-400'}>
                    {isScreenCapture ? 'Capturing' : 'Inactive'}
                  </span>
                </div>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default App;