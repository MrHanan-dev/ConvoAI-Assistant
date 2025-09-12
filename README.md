# 🧠 Convo AI - Intelligent Screen Analysis Assistant

<div align="center">
  <img src="https://img.shields.io/badge/React-19.1.1-blue?style=for-the-badge&logo=react" alt="React Version">
  <img src="https://img.shields.io/badge/Python-3.13-green?style=for-the-badge&logo=python" alt="Python Version">
  <img src="https://img.shields.io/badge/FastAPI-Latest-red?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Cohere-AI-orange?style=for-the-badge&logo=cohere" alt="Cohere AI">
  <img src="https://img.shields.io/badge/Socket.IO-Real--time-black?style=for-the-badge&logo=socket.io" alt="Socket.IO">
</div>

## 🌟 Overview

**Convo AI** is a cutting-edge intelligent assistant that combines real-time screen analysis, advanced AI conversation capabilities, and modern web technologies to provide an extraordinary user experience. Built with React, FastAPI, and powered by Cohere AI, it offers seamless interaction through voice, text, and visual analysis.

## ✨ Key Features

### 🤖 **AI-Powered Conversations**
- **Cohere AI Integration**: Real-time responses powered by advanced language models
- **Context-Aware Responses**: Smart detection of screen-related vs. general questions
- **Fast Response Times**: Optimized for 1-2 second response delivery
- **Natural Language Processing**: Advanced sentiment analysis and conversation flow

### 🎨 **Modern React Frontend**
- **Extraordinary Animations**: Floating particles, gradient text, smooth transitions
- **Glass Morphism Design**: Modern UI with backdrop blur effects
- **Responsive Layout**: Perfect on desktop, tablet, and mobile devices
- **Real-time Chat Interface**: Live messaging with typing indicators
- **Interactive Controls**: Voice input, screen capture, and status monitoring

### 🎤 **Advanced Voice Recognition**
- **Browser Speech API**: Native voice-to-text conversion
- **Real-time Processing**: Instant speech recognition and transcription
- **Noise Cancellation**: Advanced audio processing capabilities
- **Multi-language Support**: Configurable language settings

### 📺 **Real-time Screen Analysis**
- **Live Screen Capture**: Continuous screen monitoring and analysis
- **Computer Vision**: UI element detection, text regions, and activity analysis
- **Visual Intelligence**: Dominant color detection and screen composition analysis
- **Context Integration**: Screen data incorporated into AI responses

### 🔧 **Technical Excellence**
- **WebSocket Communication**: Real-time bidirectional data flow
- **RESTful API**: Comprehensive backend services
- **Error Handling**: Graceful fallbacks and robust error management
- **Performance Optimized**: Efficient resource usage and fast loading

## 🚀 Quick Start

### Prerequisites

- **Node.js** (v16 or higher)
- **Python** (v3.8 or higher)
- **Cohere API Key** (Get yours at [cohere.ai](https://cohere.ai))

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/convo-ai.git
   cd convo-ai
   ```

2. **Backend Setup**
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Set up Cohere API key
   python setup_cohere.py
   ```

3. **Frontend Setup**
   ```bash
   # Navigate to React frontend
   cd convo-ai-frontend
   
   # Install dependencies
   npm install
   ```

### Running the Application

1. **Start the Backend**
   ```bash
   python working_app_with_cohere.py
   ```
   Backend will be available at `http://localhost:8000`

2. **Start the Frontend**
   ```bash
   cd convo-ai-frontend
   npm start
   ```
   Frontend will be available at `http://localhost:3000`

3. **Access the Application**
   Open your browser and navigate to `http://localhost:3000`

## 🏗️ Architecture

### Backend (FastAPI + Python)
```
├── working_app_with_cohere.py    # Main application server
├── app/
│   ├── core/
│   │   ├── config.py            # Configuration management
│   │   ├── database.py          # Database initialization
│   │   └── redis_client.py      # Redis client setup
│   ├── services/
│   │   ├── ai_engine.py         # Cohere AI integration
│   │   ├── screen_capture.py    # Screen analysis service
│   │   └── conversation_analyzer.py # Chat analysis
│   └── models/                  # Database models
├── requirements.txt             # Python dependencies
└── setup_cohere.py             # Cohere API setup script
```

### Frontend (React + TypeScript)
```
convo-ai-frontend/
├── src/
│   ├── App.tsx                  # Main React component
│   ├── App.css                  # Custom styles and animations
│   └── index.css                # Global styles and Tailwind
├── public/                      # Static assets
├── package.json                 # Dependencies and scripts
└── tailwind.config.js          # Tailwind CSS configuration
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Cohere AI Configuration
COHERE_API_KEY=your_cohere_api_key_here

# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./ai_assistant.db

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379

# Server Configuration
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### Cohere API Setup

1. Visit [cohere.ai](https://cohere.ai) and create an account
2. Generate your API key from the dashboard
3. Run the setup script:
   ```bash
   python setup_cohere.py
   ```
4. Enter your API key when prompted

## 📡 API Endpoints

### Chat Endpoints
- `POST /api/chat` - Send message to AI
- `POST /api/speech/listen` - Voice input processing
- `POST /api/speech/test` - Test microphone functionality

### Screen Analysis Endpoints
- `POST /api/screen/start` - Start screen capture
- `POST /api/screen/stop` - Stop screen capture
- `GET /api/screen/image` - Get current screen image
- `GET /api/screen/analysis` - Get screen analysis data
- `POST /api/screen/chat` - Chat with screen context

### System Endpoints
- `GET /health` - Health check
- `GET /` - API documentation

## 🎨 Frontend Features

### Modern UI Components
- **Animated Header**: Rotating brain icon with gradient text
- **Floating Particles**: Background animation effects
- **Glass Morphism Cards**: Translucent UI elements with blur effects
- **Gradient Backgrounds**: Dynamic color transitions
- **Custom Scrollbars**: Styled scrollbars with gradient effects

### Interactive Elements
- **Voice Input Button**: Speech recognition with visual feedback
- **Screen Capture Toggle**: Start/stop screen monitoring
- **Real-time Status**: Connection, voice, and screen status indicators
- **Message Animations**: Smooth message appearance and transitions
- **Typing Indicators**: Animated dots during AI response generation

### Responsive Design
- **Mobile-First**: Optimized for all screen sizes
- **Touch-Friendly**: Large buttons and intuitive gestures
- **Adaptive Layout**: Grid system that adjusts to viewport
- **Performance Optimized**: Efficient rendering and minimal re-renders

## 🔌 WebSocket Events

### Client to Server
- `user_message` - Send chat message
- `connect` - Establish connection
- `disconnect` - Close connection

### Server to Client
- `connected` - Connection established
- `ai_response` - AI response received
- `message_analysis` - Message sentiment analysis
- `screen_update` - Screen capture data

## 🛠️ Development

### Backend Development
```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn working_app_with_cohere:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest tests/
```

### Frontend Development
```bash
cd convo-ai-frontend

# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

## 📦 Dependencies

### Backend Dependencies
```
fastapi==0.104.1
uvicorn==0.24.0
socketio==5.10.0
cohere==4.37
pydantic==2.5.0
pydantic-settings==2.1.0
sqlalchemy==2.0.23
alembic==1.13.1
aiosqlite==0.19.0
redis==5.0.1
loguru==0.7.2
mss==9.0.1
opencv-python==4.8.1.78
Pillow==10.1.0
```

### Frontend Dependencies
```
react==19.1.1
react-dom==19.1.1
typescript==4.9.5
socket.io-client==4.7.4
framer-motion==10.16.16
lucide-react==0.294.0
tailwindcss==3.3.6
```

## 🚀 Deployment

### Production Build
```bash
# Build React frontend
cd convo-ai-frontend
npm run build

# Serve with production server
python working_app_with_cohere.py
```

### Docker Deployment
```dockerfile
# Dockerfile example
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "working_app_with_cohere.py"]
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for React components
- Write tests for new features
- Update documentation for API changes
- Ensure responsive design for UI changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Cohere AI** for providing advanced language model capabilities
- **React Team** for the amazing frontend framework
- **FastAPI** for the high-performance backend framework
- **Framer Motion** for smooth animations
- **Tailwind CSS** for utility-first styling

## 📞 Support

- **Documentation**: [Wiki](https://github.com/yourusername/convo-ai/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/convo-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/convo-ai/discussions)
- **Email**: muhammadhanan23230@gmail.com

## 🔮 Roadmap

### Upcoming Features
- [ ] **Multi-language Support**: Support for multiple languages
- [ ] **Advanced Analytics**: Detailed conversation analytics
- [ ] **Mobile App**: Native iOS and Android applications
- [ ] **Plugin System**: Extensible plugin architecture
- [ ] **Team Collaboration**: Multi-user support and sharing
- [ ] **API Rate Limiting**: Advanced rate limiting and quotas
- [ ] **Custom Models**: Support for custom AI models
- [ ] **Voice Cloning**: Personalized voice responses

### Performance Improvements
- [ ] **Caching Layer**: Redis-based response caching
- [ ] **CDN Integration**: Global content delivery
- [ ] **Database Optimization**: Query optimization and indexing
- [ ] **Bundle Optimization**: Frontend bundle size reduction

---

<div align="center">
  <p>Made with ❤️ by the Convo AI Team</p>
  <p>

  </p>
</div>
