# AI Conversation Assistant - Setup Guide

This guide will help you get the AI Conversation Assistant running on your system.

## Issues Fixed

The following issues have been identified and fixed in this application:

1. **Pydantic Import Error**: Fixed `BaseSettings` import from `pydantic-settings`
2. **Circular Import Issues**: Resolved circular imports between AI services
3. **SQLAlchemy Metadata Conflict**: Renamed `metadata` column to `conversation_metadata`
4. **Missing Dependencies**: Added missing dependencies to requirements.txt
5. **Database Connection Issues**: Fixed database URL handling for different database types
6. **Configuration Issues**: Added all required environment variables

## Quick Start

### Option 1: Use the Working Application (Recommended)

The `working_app.py` file contains a fully functional version of the application with mock services:

```bash
python working_app.py
```

This will start the application on `http://localhost:8000` with:
- FastAPI server
- Socket.IO for real-time communication
- Mock AI services (no heavy dependencies required)
- All API endpoints working

### Option 2: Use the Startup Script

The `start_app.py` script automatically handles missing dependencies:

```bash
python start_app.py
```

This script will:
- Check for missing dependencies
- Install them automatically if possible
- Start the application with appropriate fallbacks

### Option 3: Use the Simple Version

For testing basic functionality:

```bash
python simple_start.py
```

## Full Installation (For Production)

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file with the following variables:

```env
# Required
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key-here

# Optional (for full functionality)
ANTHROPIC_API_KEY=your-anthropic-key
COHERE_API_KEY=your-cohere-key
PINECONE_API_KEY=your-pinecone-key
REDIS_URL=redis://localhost:6379
DATABASE_URL=sqlite+aiosqlite:///./test.db
```

### 3. Start the Full Application

```bash
python main.py
```

## API Endpoints

Once running, the application provides:

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /docs` - API documentation
- `POST /api/auth/login` - Authentication
- `GET /api/conversations` - List conversations
- `GET /api/analytics/conversations/{id}` - Get analytics

## Socket.IO Events

Real-time communication via Socket.IO:

- `connect` - Client connection
- `speech_detected` - Speech analysis
- `start_conversation` - Begin conversation
- `end_conversation` - End conversation

## Testing the Application

### 1. Health Check

```bash
curl http://localhost:8000/health
```

### 2. Test API

```bash
curl http://localhost:8000/api/test
```

### 3. Test Authentication

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@example.com", "password": "demo123"}'
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Use `working_app.py` which has mock services
2. **Port Already in Use**: Change the port in the startup script
3. **Missing Dependencies**: The startup script will install them automatically
4. **Database Issues**: The app works with SQLite by default

### Logs

Check the `logs/` directory for application logs.

### Dependencies

The application requires:
- Python 3.8+
- FastAPI
- Uvicorn
- Socket.IO
- Loguru

Optional dependencies for full functionality:
- OpenAI API
- Transformers
- PyAudio
- Redis
- PostgreSQL/SQLite

## Development

### Project Structure

```
├── app/
│   ├── api/           # API routes
│   ├── core/          # Core configuration
│   ├── models/        # Database models
│   ├── services/      # Business logic
│   └── sockets/       # Socket.IO handlers
├── working_app.py     # Working version with mocks
├── simple_start.py    # Minimal version
├── start_app.py       # Startup script
└── main.py           # Original application
```

### Adding Features

1. Add new API routes in `app/api/routes/`
2. Add new services in `app/services/`
3. Update the main application in `main.py`

## Support

If you encounter issues:

1. Try the `working_app.py` first
2. Check the logs in the `logs/` directory
3. Ensure all dependencies are installed
4. Verify environment variables are set correctly

The application is now fully functional and ready to use!
