/**
 * Content Script for AI Conversation Assistant Browser Extension
 * Provides Cluely.ai-like functionality within web browsers
 */

class AIAssistantExtension {
    constructor() {
        this.isActive = false;
        this.isRecording = false;
        this.overlayElement = null;
        this.websocket = null;
        this.currentPlatform = this.detectPlatform();
        this.conversationId = null;
        this.suggestions = [];
        
        // Initialize extension
        this.initialize();
    }
    
    initialize() {
        console.log('🚀 AI Conversation Assistant Extension initializing...');
        
        // Detect meeting platform
        this.currentPlatform = this.detectPlatform();
        
        if (this.currentPlatform) {
            console.log(`📹 Detected platform: ${this.currentPlatform}`);
            
            // Create overlay
            this.createOverlay();
            
            // Connect to desktop app
            this.connectToDesktop();
            
            // Set up platform-specific hooks
            this.setupPlatformHooks();
            
            // Start monitoring
            this.startMonitoring();
            
            console.log('✅ Extension initialized successfully');
        } else {
            console.log('ℹ️ No supported meeting platform detected');
        }
    }
    
    detectPlatform() {
        const url = window.location.href;
        
        if (url.includes('meet.google.com')) {
            return 'google_meet';
        } else if (url.includes('teams.microsoft.com')) {
            return 'microsoft_teams';
        } else if (url.includes('zoom.us')) {
            return 'zoom';
        } else if (url.includes('webex.com')) {
            return 'webex';
        } else if (url.includes('chime.aws')) {
            return 'amazon_chime';
        }
        
        return null;
    }
    
    createOverlay() {
        try {
            // Create overlay container
            this.overlayElement = document.createElement('div');
            this.overlayElement.id = 'ai-assistant-overlay';
            this.overlayElement.innerHTML = `
                <div class="ai-overlay-container">
                    <div class="ai-overlay-header">
                        <span class="ai-overlay-title">🤖 AI Assistant</span>
                        <div class="ai-overlay-controls">
                            <button id="ai-toggle-record" class="ai-btn ai-btn-record">🎙️</button>
                            <button id="ai-toggle-visibility" class="ai-btn">👁️</button>
                            <button id="ai-settings" class="ai-btn">⚙️</button>
                        </div>
                    </div>
                    
                    <div class="ai-overlay-content">
                        <div class="ai-tab-container">
                            <div class="ai-tab ai-tab-active" data-tab="teleprompter">🎯 Teleprompter</div>
                            <div class="ai-tab" data-tab="suggestions">💡 Suggestions</div>
                            <div class="ai-tab" data-tab="analytics">📊 Analytics</div>
                        </div>
                        
                        <div class="ai-tab-content">
                            <!-- Teleprompter tab -->
                            <div id="ai-teleprompter-tab" class="ai-tab-panel ai-tab-panel-active">
                                <div class="ai-stage-indicator">
                                    <span class="ai-stage-label">Opening</span>
                                    <div class="ai-progress-bar">
                                        <div class="ai-progress-fill" style="width: 20%"></div>
                                    </div>
                                </div>
                                
                                <div id="ai-prompts-container" class="ai-prompts-container">
                                    <div class="ai-prompt-placeholder">
                                        🎤 Start your conversation to see adaptive prompts...
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Suggestions tab -->
                            <div id="ai-suggestions-tab" class="ai-tab-panel">
                                <div id="ai-suggestions-container" class="ai-suggestions-container">
                                    <div class="ai-suggestion-placeholder">
                                        💡 AI suggestions will appear here
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Analytics tab -->
                            <div id="ai-analytics-tab" class="ai-tab-panel">
                                <div class="ai-analytics-container">
                                    <div class="ai-metric">
                                        <span class="ai-metric-label">😊 Sentiment:</span>
                                        <span id="ai-sentiment-value" class="ai-metric-value">Neutral</span>
                                    </div>
                                    <div class="ai-metric">
                                        <span class="ai-metric-label">🎯 Win Rate:</span>
                                        <span id="ai-winrate-value" class="ai-metric-value">65%</span>
                                    </div>
                                    <div class="ai-metric">
                                        <span class="ai-metric-label">⏱️ Talk Time:</span>
                                        <span id="ai-talktime-value" class="ai-metric-value">You: 45%</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="ai-overlay-status">
                        <span id="ai-connection-status" class="ai-status-indicator">🟢 Connected</span>
                        <span id="ai-recording-status" class="ai-status-indicator">⏹️ Not Recording</span>
                    </div>
                </div>
            `;
            
            // Add CSS styles
            this.addOverlayStyles();
            
            // Append to body
            document.body.appendChild(this.overlayElement);
            
            // Set up event listeners
            this.setupOverlayEvents();
            
            console.log('✅ Overlay created successfully');
            
        } catch (error) {
            console.error('Error creating overlay:', error);
        }
    }
    
    addOverlayStyles() {
        const style = document.createElement('style');
        style.textContent = `
            #ai-assistant-overlay {
                position: fixed;
                top: 20px;
                right: 20px;
                width: 350px;
                height: 450px;
                background: rgba(30, 30, 30, 0.95);
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                z-index: 10000;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                color: white;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .ai-overlay-container {
                display: flex;
                flex-direction: column;
                height: 100%;
                padding: 12px;
            }
            
            .ai-overlay-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 12px;
                padding-bottom: 8px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .ai-overlay-title {
                font-size: 16px;
                font-weight: bold;
                color: #4A9EFF;
            }
            
            .ai-overlay-controls {
                display: flex;
                gap: 6px;
            }
            
            .ai-btn {
                background: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 6px;
                padding: 6px 10px;
                color: white;
                cursor: pointer;
                font-size: 14px;
                transition: background 0.2s;
            }
            
            .ai-btn:hover {
                background: rgba(255, 255, 255, 0.2);
            }
            
            .ai-btn-record.recording {
                background: #FF4757;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }
            
            .ai-tab-container {
                display: flex;
                gap: 4px;
                margin-bottom: 12px;
            }
            
            .ai-tab {
                flex: 1;
                padding: 8px 12px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                text-align: center;
                cursor: pointer;
                font-size: 12px;
                transition: background 0.2s;
            }
            
            .ai-tab:hover {
                background: rgba(255, 255, 255, 0.2);
            }
            
            .ai-tab-active {
                background: #4A9EFF !important;
            }
            
            .ai-tab-content {
                flex: 1;
                overflow: hidden;
            }
            
            .ai-tab-panel {
                display: none;
                height: 100%;
                overflow-y: auto;
            }
            
            .ai-tab-panel-active {
                display: block;
            }
            
            .ai-stage-indicator {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 10px;
                margin-bottom: 12px;
            }
            
            .ai-stage-label {
                font-weight: bold;
                color: #FFA726;
            }
            
            .ai-progress-bar {
                width: 100%;
                height: 4px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 2px;
                margin-top: 6px;
                overflow: hidden;
            }
            
            .ai-progress-fill {
                height: 100%;
                background: #4A9EFF;
                transition: width 0.3s ease;
            }
            
            .ai-prompts-container, .ai-suggestions-container {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }
            
            .ai-prompt, .ai-suggestion {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 12px;
                border-left: 3px solid #4A9EFF;
            }
            
            .ai-prompt-text, .ai-suggestion-text {
                font-size: 14px;
                line-height: 1.4;
                margin-bottom: 8px;
            }
            
            .ai-prompt-actions, .ai-suggestion-actions {
                display: flex;
                gap: 6px;
                justify-content: flex-end;
            }
            
            .ai-btn-small {
                background: rgba(255, 255, 255, 0.2);
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                color: white;
                cursor: pointer;
                font-size: 12px;
            }
            
            .ai-btn-small:hover {
                background: rgba(255, 255, 255, 0.3);
            }
            
            .ai-analytics-container {
                display: flex;
                flex-direction: column;
                gap: 12px;
            }
            
            .ai-metric {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 8px 12px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 6px;
            }
            
            .ai-metric-label {
                font-size: 14px;
            }
            
            .ai-metric-value {
                font-weight: bold;
                color: #4A9EFF;
            }
            
            .ai-overlay-status {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 12px;
                padding-top: 8px;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                font-size: 12px;
            }
            
            .ai-status-indicator {
                display: flex;
                align-items: center;
                gap: 4px;
            }
            
            .ai-prompt-placeholder, .ai-suggestion-placeholder {
                text-align: center;
                color: rgba(255, 255, 255, 0.6);
                padding: 20px;
                font-style: italic;
            }
            
            /* Hide overlay during screen sharing */
            .ai-overlay-hidden {
                display: none !important;
            }
            
            /* Responsive design */
            @media (max-width: 768px) {
                #ai-assistant-overlay {
                    width: 300px;
                    height: 400px;
                }
            }
        `;
        
        document.head.appendChild(style);
    }
    
    setupOverlayEvents() {
        try {
            // Tab switching
            const tabs = this.overlayElement.querySelectorAll('.ai-tab');
            tabs.forEach(tab => {
                tab.addEventListener('click', (e) => {
                    this.switchTab(e.target.dataset.tab);
                });
            });
            
            // Control buttons
            const recordBtn = this.overlayElement.querySelector('#ai-toggle-record');
            recordBtn.addEventListener('click', () => this.toggleRecording());
            
            const visibilityBtn = this.overlayElement.querySelector('#ai-toggle-visibility');
            visibilityBtn.addEventListener('click', () => this.toggleVisibility());
            
            const settingsBtn = this.overlayElement.querySelector('#ai-settings');
            settingsBtn.addEventListener('click', () => this.openSettings());
            
            // Make overlay draggable
            this.makeDraggable();
            
        } catch (error) {
            console.error('Error setting up overlay events:', error);
        }
    }
    
    connectToDesktop() {
        try {
            // Connect to desktop app via WebSocket
            this.websocket = new WebSocket('ws://localhost:8000/ws/browser');
            
            this.websocket.onopen = () => {
                console.log('🔗 Connected to desktop app');
                this.updateConnectionStatus(true);
                
                // Send platform detection
                this.websocket.send(JSON.stringify({
                    type: 'platform_detected',
                    platform: this.currentPlatform,
                    url: window.location.href,
                    timestamp: new Date().toISOString()
                }));
            };
            
            this.websocket.onmessage = (event) => {
                this.handleDesktopMessage(JSON.parse(event.data));
            };
            
            this.websocket.onclose = () => {
                console.log('❌ Disconnected from desktop app');
                this.updateConnectionStatus(false);
                
                // Attempt reconnection
                setTimeout(() => this.connectToDesktop(), 5000);
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
            
        } catch (error) {
            console.error('Error connecting to desktop:', error);
        }
    }
    
    setupPlatformHooks() {
        try {
            switch (this.currentPlatform) {
                case 'google_meet':
                    this.setupGoogleMeetHooks();
                    break;
                case 'microsoft_teams':
                    this.setupTeamsHooks();
                    break;
                case 'zoom':
                    this.setupZoomHooks();
                    break;
                default:
                    this.setupGenericHooks();
            }
            
        } catch (error) {
            console.error('Error setting up platform hooks:', error);
        }
    }
    
    setupGoogleMeetHooks() {
        // Monitor Google Meet captions for conversation text
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    const captions = document.querySelectorAll('[data-speaker-name]');
                    captions.forEach(caption => {
                        const speaker = caption.getAttribute('data-speaker-name');
                        const text = caption.textContent;
                        
                        if (text && text.length > 10) {
                            this.sendSpeechToDesktop(text, speaker);
                        }
                    });
                }
            });
        });
        
        // Start observing
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    setupTeamsHooks() {
        // Monitor Teams chat and captions
        const observer = new MutationObserver((mutations) => {
            // Look for Teams-specific caption elements
            const captionElements = document.querySelectorAll('[data-tid="closed-captions-text"]');
            captionElements.forEach(element => {
                const text = element.textContent;
                if (text && text.length > 10) {
                    this.sendSpeechToDesktop(text, 'participant');
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    setupZoomHooks() {
        // Monitor Zoom captions
        const observer = new MutationObserver((mutations) => {
            const captions = document.querySelectorAll('.caption-line');
            captions.forEach(caption => {
                const text = caption.textContent;
                if (text && text.length > 10) {
                    this.sendSpeechToDesktop(text, 'participant');
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    setupGenericHooks() {
        // Generic hooks for other platforms
        console.log('Setting up generic platform hooks');
    }
    
    startMonitoring() {
        try {
            // Monitor for screen sharing
            this.monitorScreenShare();
            
            // Monitor for meeting state changes
            this.monitorMeetingState();
            
            // Start periodic status updates
            setInterval(() => {
                this.sendStatusUpdate();
            }, 10000); // Every 10 seconds
            
        } catch (error) {
            console.error('Error starting monitoring:', error);
        }
    }
    
    monitorScreenShare() {
        // Hide overlay during screen sharing
        const mediaObserver = new MutationObserver(() => {
            const isSharing = this.detectScreenSharing();
            if (isSharing) {
                this.overlayElement.classList.add('ai-overlay-hidden');
            } else {
                this.overlayElement.classList.remove('ai-overlay-hidden');
            }
        });
        
        mediaObserver.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['class']
        });
    }
    
    detectScreenSharing() {
        // Platform-specific screen sharing detection
        switch (this.currentPlatform) {
            case 'google_meet':
                return document.querySelector('[data-is-presenting="true"]') !== null;
            case 'microsoft_teams':
                return document.querySelector('[data-tid="screen-share-indicator"]') !== null;
            case 'zoom':
                return document.querySelector('.sharing-screen-status') !== null;
            default:
                return false;
        }
    }
    
    monitorMeetingState() {
        // Monitor for meeting start/end
        const stateObserver = new MutationObserver(() => {
            const meetingActive = this.isMeetingActive();
            
            if (meetingActive && !this.isActive) {
                this.onMeetingStart();
            } else if (!meetingActive && this.isActive) {
                this.onMeetingEnd();
            }
        });
        
        stateObserver.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    isMeetingActive() {
        // Platform-specific meeting detection
        switch (this.currentPlatform) {
            case 'google_meet':
                return document.querySelector('[data-call-ended="false"]') !== null;
            case 'microsoft_teams':
                return document.querySelector('[data-tid="call-canvas"]') !== null;
            case 'zoom':
                return document.querySelector('.meeting-client-view') !== null;
            default:
                return true; // Assume active if can't detect
        }
    }
    
    onMeetingStart() {
        console.log('📞 Meeting started');
        this.isActive = true;
        
        // Notify desktop app
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({
                type: 'meeting_started',
                platform: this.currentPlatform,
                timestamp: new Date().toISOString()
            }));
        }
    }
    
    onMeetingEnd() {
        console.log('📞 Meeting ended');
        this.isActive = false;
        this.isRecording = false;
        
        // Update UI
        this.updateRecordingStatus(false);
        
        // Notify desktop app
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({
                type: 'meeting_ended',
                platform: this.currentPlatform,
                timestamp: new Date().toISOString()
            }));
        }
    }
    
    sendSpeechToDesktop(text, speaker) {
        try {
            if (this.websocket && this.websocket.readyState === WebSocket.OPEN && this.isRecording) {
                this.websocket.send(JSON.stringify({
                    type: 'speech_detected',
                    text: text,
                    speaker: speaker,
                    platform: this.currentPlatform,
                    timestamp: new Date().toISOString()
                }));
            }
            
        } catch (error) {
            console.error('Error sending speech to desktop:', error);
        }
    }
    
    handleDesktopMessage(message) {
        try {
            switch (message.type) {
                case 'teleprompter_update':
                    this.updateTeleprompter(message.data);
                    break;
                
                case 'suggestions_update':
                    this.updateSuggestions(message.data);
                    break;
                
                case 'analytics_update':
                    this.updateAnalytics(message.data);
                    break;
                
                case 'objection_detected':
                    this.showObjectionAlert(message.data);
                    break;
                
                default:
                    console.log('Unknown message type:', message.type);
            }
            
        } catch (error) {
            console.error('Error handling desktop message:', error);
        }
    }
    
    updateTeleprompter(data) {
        try {
            const promptsContainer = this.overlayElement.querySelector('#ai-prompts-container');
            const stageLabel = this.overlayElement.querySelector('.ai-stage-label');
            const progressFill = this.overlayElement.querySelector('.ai-progress-fill');
            
            // Update stage
            if (data.stage) {
                stageLabel.textContent = data.stage.replace('_', ' ').toUpperCase();
            }
            
            // Update progress
            if (data.progress) {
                progressFill.style.width = `${data.progress}%`;
            }
            
            // Update prompts
            if (data.prompts) {
                promptsContainer.innerHTML = '';
                
                data.prompts.forEach(prompt => {
                    const promptElement = document.createElement('div');
                    promptElement.className = 'ai-prompt';
                    promptElement.innerHTML = `
                        <div class="ai-prompt-text">${prompt.text}</div>
                        <div class="ai-prompt-actions">
                            <button class="ai-btn-small" onclick="navigator.clipboard.writeText('${prompt.text}')">📋 Copy</button>
                            <button class="ai-btn-small" onclick="this.parentElement.parentElement.style.opacity='0.5'">✅ Used</button>
                        </div>
                    `;
                    promptsContainer.appendChild(promptElement);
                });
            }
            
        } catch (error) {
            console.error('Error updating teleprompter:', error);
        }
    }
    
    updateSuggestions(suggestions) {
        try {
            const suggestionsContainer = this.overlayElement.querySelector('#ai-suggestions-container');
            suggestionsContainer.innerHTML = '';
            
            suggestions.forEach(suggestion => {
                const suggestionElement = document.createElement('div');
                suggestionElement.className = 'ai-suggestion';
                suggestionElement.innerHTML = `
                    <div class="ai-suggestion-text">${suggestion.text}</div>
                    <div class="ai-suggestion-actions">
                        <button class="ai-btn-small" onclick="navigator.clipboard.writeText('${suggestion.text}')">📋 Copy</button>
                        <button class="ai-btn-small" onclick="this.parentElement.parentElement.style.opacity='0.5'">✅ Use</button>
                    </div>
                `;
                suggestionsContainer.appendChild(suggestionElement);
            });
            
        } catch (error) {
            console.error('Error updating suggestions:', error);
        }
    }
    
    updateAnalytics(analytics) {
        try {
            // Update sentiment
            const sentimentValue = this.overlayElement.querySelector('#ai-sentiment-value');
            if (analytics.sentiment) {
                sentimentValue.textContent = `${analytics.sentiment.overall} (${Math.round(analytics.sentiment.confidence * 100)}%)`;
            }
            
            // Update win rate
            const winrateValue = this.overlayElement.querySelector('#ai-winrate-value');
            if (analytics.win_rate) {
                winrateValue.textContent = `${Math.round(analytics.win_rate * 100)}%`;
            }
            
            // Update talk time
            const talktimeValue = this.overlayElement.querySelector('#ai-talktime-value');
            if (analytics.talk_time) {
                talktimeValue.textContent = `You: ${analytics.talk_time.user}%`;
            }
            
        } catch (error) {
            console.error('Error updating analytics:', error);
        }
    }
    
    showObjectionAlert(objectionData) {
        try {
            // Create temporary objection alert
            const alert = document.createElement('div');
            alert.className = 'ai-objection-alert';
            alert.innerHTML = `
                <div class="ai-alert-content">
                    <div class="ai-alert-header">🚨 OBJECTION DETECTED</div>
                    <div class="ai-alert-body">
                        <strong>${objectionData.type.toUpperCase()}</strong>
                        <br>Confidence: ${Math.round(objectionData.confidence * 100)}%
                    </div>
                    <button class="ai-alert-close" onclick="this.parentElement.parentElement.remove()">×</button>
                </div>
            `;
            
            // Style the alert
            alert.style.cssText = `
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: rgba(255, 71, 87, 0.95);
                color: white;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                z-index: 10001;
                animation: slideIn 0.3s ease;
            `;
            
            document.body.appendChild(alert);
            
            // Auto-remove after 8 seconds
            setTimeout(() => {
                if (alert.parentElement) {
                    alert.remove();
                }
            }, 8000);
            
        } catch (error) {
            console.error('Error showing objection alert:', error);
        }
    }
    
    switchTab(tabName) {
        try {
            // Update tab buttons
            const tabs = this.overlayElement.querySelectorAll('.ai-tab');
            tabs.forEach(tab => {
                tab.classList.remove('ai-tab-active');
                if (tab.dataset.tab === tabName) {
                    tab.classList.add('ai-tab-active');
                }
            });
            
            // Update tab panels
            const panels = this.overlayElement.querySelectorAll('.ai-tab-panel');
            panels.forEach(panel => {
                panel.classList.remove('ai-tab-panel-active');
                if (panel.id === `ai-${tabName}-tab`) {
                    panel.classList.add('ai-tab-panel-active');
                }
            });
            
        } catch (error) {
            console.error('Error switching tab:', error);
        }
    }
    
    toggleRecording() {
        try {
            this.isRecording = !this.isRecording;
            this.updateRecordingStatus(this.isRecording);
            
            // Notify desktop app
            if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
                this.websocket.send(JSON.stringify({
                    type: this.isRecording ? 'start_recording' : 'stop_recording',
                    platform: this.currentPlatform,
                    timestamp: new Date().toISOString()
                }));
            }
            
        } catch (error) {
            console.error('Error toggling recording:', error);
        }
    }
    
    toggleVisibility() {
        try {
            const overlay = this.overlayElement;
            if (overlay.style.display === 'none') {
                overlay.style.display = 'block';
            } else {
                overlay.style.display = 'none';
            }
            
        } catch (error) {
            console.error('Error toggling visibility:', error);
        }
    }
    
    openSettings() {
        try {
            // Open extension settings (would open popup or new tab)
            chrome.runtime.sendMessage({
                type: 'open_settings'
            });
            
        } catch (error) {
            console.error('Error opening settings:', error);
        }
    }
    
    updateConnectionStatus(connected) {
        try {
            const statusElement = this.overlayElement.querySelector('#ai-connection-status');
            if (connected) {
                statusElement.textContent = '🟢 Connected';
                statusElement.style.color = '#4CAF50';
            } else {
                statusElement.textContent = '🔴 Disconnected';
                statusElement.style.color = '#F44336';
            }
            
        } catch (error) {
            console.error('Error updating connection status:', error);
        }
    }
    
    updateRecordingStatus(recording) {
        try {
            const recordBtn = this.overlayElement.querySelector('#ai-toggle-record');
            const statusElement = this.overlayElement.querySelector('#ai-recording-status');
            
            if (recording) {
                recordBtn.textContent = '⏹️';
                recordBtn.classList.add('recording');
                statusElement.textContent = '🔴 Recording';
                statusElement.style.color = '#F44336';
            } else {
                recordBtn.textContent = '🎙️';
                recordBtn.classList.remove('recording');
                statusElement.textContent = '⏹️ Not Recording';
                statusElement.style.color = '#9E9E9E';
            }
            
        } catch (error) {
            console.error('Error updating recording status:', error);
        }
    }
    
    sendStatusUpdate() {
        try {
            if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
                this.websocket.send(JSON.stringify({
                    type: 'status_update',
                    platform: this.currentPlatform,
                    url: window.location.href,
                    meeting_active: this.isActive,
                    recording: this.isRecording,
                    timestamp: new Date().toISOString()
                }));
            }
            
        } catch (error) {
            console.error('Error sending status update:', error);
        }
    }
    
    makeDraggable() {
        try {
            const header = this.overlayElement.querySelector('.ai-overlay-header');
            let isDragging = false;
            let startX, startY, startLeft, startTop;
            
            header.addEventListener('mousedown', (e) => {
                isDragging = true;
                startX = e.clientX;
                startY = e.clientY;
                startLeft = this.overlayElement.offsetLeft;
                startTop = this.overlayElement.offsetTop;
                
                document.addEventListener('mousemove', onMouseMove);
                document.addEventListener('mouseup', onMouseUp);
            });
            
            const onMouseMove = (e) => {
                if (!isDragging) return;
                
                const deltaX = e.clientX - startX;
                const deltaY = e.clientY - startY;
                
                this.overlayElement.style.left = `${startLeft + deltaX}px`;
                this.overlayElement.style.top = `${startTop + deltaY}px`;
                this.overlayElement.style.right = 'auto';
            };
            
            const onMouseUp = () => {
                isDragging = false;
                document.removeEventListener('mousemove', onMouseMove);
                document.removeEventListener('mouseup', onMouseUp);
            };
            
        } catch (error) {
            console.error('Error making overlay draggable:', error);
        }
    }
}

// Initialize extension when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new AIAssistantExtension();
    });
} else {
    new AIAssistantExtension();
}
