# 🚀 Quick Start: Real-time Screen Viewing

## ⚡ Get Started in 3 Steps

### 1. **Start the Application**
```bash
python working_app_with_cohere.py
```

### 2. **Open the Frontend**
- Go to `http://localhost:3000` (or your frontend URL)
- Click the **"📺 Screen View"** button

### 3. **Start Screen Capture**
- Click **"Start Screen Capture"**
- Wait for the screen image to appear
- Click **"Ask About Screen"** to interact with AI

## 🎯 Quick Demo

### **Test Screen Analysis**
1. Click **"Analyze Screen"** to see computer vision results
2. Click **"Ask About Screen"** and ask: *"What do you see?"*
3. Try: *"Are there any buttons visible?"*
4. Ask: *"What's the activity level on my screen?"*

### **Example Questions**
- *"What applications are open?"*
- *"Is my screen cluttered?"*
- *"Can you see any text on my screen?"*
- *"What UI elements are visible?"*
- *"Help me find a button"*

## 🔧 API Quick Test

### **Check Status**
```bash
curl http://localhost:8000/api/screen/status
```

### **Start Capture**
```bash
curl -X POST http://localhost:8000/api/screen/start
```

### **Ask About Screen**
```bash
curl -X POST http://localhost:8000/api/screen/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What do you see on my screen?"}'
```

### **Stop Capture**
```bash
curl -X POST http://localhost:8000/api/screen/stop
```

## 🎨 Frontend Features

### **Screen Viewing Panel**
- **📺 Screen View Button**: Toggle the screen viewing interface
- **Start/Stop Controls**: Control screen capture
- **Live Screen Display**: See your screen in real-time
- **Analysis Panel**: View computer vision results
- **Ask About Screen**: Interactive AI queries

### **Visual Interface**
- **Real-time Updates**: Screen refreshes every 2 seconds
- **Status Indicators**: Know when capture is active
- **Responsive Design**: Works on all screen sizes
- **Clean UI**: Easy to use interface

## 🚨 Troubleshooting

### **Screen Capture Not Working?**
1. Check if the server is running: `http://localhost:8000/health`
2. Verify dependencies: `pip install mss opencv-python pillow numpy`
3. Check browser console for errors
4. Try refreshing the page

### **No Screen Image?**
1. Make sure screen capture is started
2. Wait a few seconds for first capture
3. Check if screen capture service is available
4. Try stopping and starting again

### **AI Not Responding?**
1. Check if Cohere API key is set
2. Verify screen analysis is working
3. Try asking simpler questions
4. Check server logs for errors

## 🎯 Pro Tips

### **Best Practices**
- **Start Simple**: Begin with basic questions
- **Be Specific**: Ask about specific elements you see
- **Use Context**: Reference what you're working on
- **Experiment**: Try different types of questions

### **Example Workflows**
1. **Productivity Check**: *"What's on my screen right now?"*
2. **UI Help**: *"How do I find the save button?"*
3. **Screen Analysis**: *"Is my workspace organized?"*
4. **Real-time Help**: *"What should I do next?"*

## 🎉 You're Ready!

Your AI Assistant can now:
- ✅ **See your screen** in real-time
- ✅ **Analyze visual content** with computer vision
- ✅ **Provide context-aware help** based on what you're doing
- ✅ **Answer questions** about your screen content
- ✅ **Guide you** through visual tasks

**Start exploring and see how your AI Assistant can help with whatever you're working on!** 🚀✨
