"""
Overlay window for real-time AI suggestions and conversation display
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import Dict, List, Any, Callable, Optional
from datetime import datetime
import threading
from loguru import logger

from desktop.ui.teleprompter_widget import TeleprompterWidget


class OverlayWindow:
    """Translucent overlay window for AI suggestions"""
    
    def __init__(
        self,
        settings,
        on_suggestion_click: Callable,
        on_toggle_recording: Callable,
        on_open_settings: Callable,
        on_open_dashboard: Callable
    ):
        self.settings = settings
        self.on_suggestion_click = on_suggestion_click
        self.on_toggle_recording = on_toggle_recording
        self.on_open_settings = on_open_settings
        self.on_open_dashboard = on_open_dashboard
        
        # Window state
        self.is_visible = True
        self.is_pinned = False
        self.is_recording = False
        
        # UI components
        self.root = None
        self.main_frame = None
        self.header_frame = None
        self.content_frame = None
        self.suggestions_frame = None
        self.conversation_frame = None
        self.controls_frame = None
        
        # Data
        self.current_suggestions = []
        self.conversation_history = []
        
        self._create_window()
        self._setup_ui()
        self._setup_bindings()
    
    def _create_window(self):
        """Create the overlay window"""
        try:
            self.root = ctk.CTkToplevel()
            self.root.title("AI Assistant")
            self.root.geometry(f"{self.settings.OVERLAY_WIDTH}x{self.settings.OVERLAY_HEIGHT}")
            
            # Position window
            x = self.settings.OVERLAY_X
            y = self.settings.OVERLAY_Y
            self.root.geometry(f"+{x}+{y}")
            
            # Window properties
            self.root.attributes('-topmost', True)
            self.root.attributes('-alpha', self.settings.OVERLAY_OPACITY)
            self.root.resizable(True, True)
            
            # Make window stay on top but not steal focus
            self.root.focus_set()
            self.root.lift()
            
            # Handle window close
            self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
            
        except Exception as e:
            logger.error(f"Error creating overlay window: {e}")
            raise
    
    def _setup_ui(self):
        """Set up the user interface"""
        try:
            # Main container
            self.main_frame = ctk.CTkFrame(self.root)
            self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Header with controls
            self._create_header()
            
            # Content area with tabs
            self._create_content_area()
            
            # Status bar
            self._create_status_bar()
            
        except Exception as e:
            logger.error(f"Error setting up UI: {e}")
            raise
    
    def _create_header(self):
        """Create header with controls"""
        self.header_frame = ctk.CTkFrame(self.main_frame)
        self.header_frame.pack(fill="x", padx=5, pady=(5, 0))
        
        # Title
        title_label = ctk.CTkLabel(
            self.header_frame,
            text="🤖 AI Assistant",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(side="left", padx=10, pady=5)
        
        # Controls
        controls_frame = ctk.CTkFrame(self.header_frame)
        controls_frame.pack(side="right", padx=5, pady=2)
        
        # Record button
        self.record_button = ctk.CTkButton(
            controls_frame,
            text="🎙️ Record",
            width=80,
            height=30,
            command=self._toggle_recording,
            fg_color="red" if not self.is_recording else "green"
        )
        self.record_button.pack(side="left", padx=2)
        
        # Pin button
        self.pin_button = ctk.CTkButton(
            controls_frame,
            text="📌",
            width=30,
            height=30,
            command=self._toggle_pin
        )
        self.pin_button.pack(side="left", padx=2)
        
        # Settings button
        settings_button = ctk.CTkButton(
            controls_frame,
            text="⚙️",
            width=30,
            height=30,
            command=self.on_open_settings
        )
        settings_button.pack(side="left", padx=2)
        
        # Dashboard button
        dashboard_button = ctk.CTkButton(
            controls_frame,
            text="📊",
            width=30,
            height=30,
            command=self.on_open_dashboard
        )
        dashboard_button.pack(side="left", padx=2)
        
        # Minimize button
        minimize_button = ctk.CTkButton(
            controls_frame,
            text="−",
            width=30,
            height=30,
            command=self._minimize_window
        )
        minimize_button.pack(side="left", padx=2)
    
    def _create_content_area(self):
        """Create main content area with tabs"""
        # Tab view
        self.tab_view = ctk.CTkTabview(self.main_frame, width=400, height=300)
        self.tab_view.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Teleprompter tab (Cluely.ai's main feature)
        self.teleprompter_tab = self.tab_view.add("🎯 Teleprompter")
        self._create_teleprompter_panel()
        
        # Suggestions tab
        self.suggestions_tab = self.tab_view.add("💡 Suggestions")
        self._create_suggestions_panel()
        
        # Conversation tab
        self.conversation_tab = self.tab_view.add("💬 Conversation")
        self._create_conversation_panel()
        
        # Analytics tab
        self.analytics_tab = self.tab_view.add("📈 Analytics")
        self._create_analytics_panel()
    
    def _create_teleprompter_panel(self):
        """Create adaptive teleprompter panel - Cluely.ai's signature feature"""
        self.teleprompter_widget = TeleprompterWidget(self.teleprompter_tab)
        self.teleprompter_widget.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _create_suggestions_panel(self):
        """Create suggestions panel"""
        # Suggestions scrollable frame
        self.suggestions_scroll = ctk.CTkScrollableFrame(self.suggestions_tab)
        self.suggestions_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # No suggestions message
        self.no_suggestions_label = ctk.CTkLabel(
            self.suggestions_scroll,
            text="🤖 AI suggestions will appear here during conversations",
            text_color="gray"
        )
        self.no_suggestions_label.pack(pady=20)
    
    def _create_conversation_panel(self):
        """Create conversation panel"""
        # Conversation display
        self.conversation_text = ctk.CTkTextbox(
            self.conversation_tab,
            wrap="word",
            height=200
        )
        self.conversation_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Input frame
        input_frame = ctk.CTkFrame(self.conversation_tab)
        input_frame.pack(fill="x", padx=5, pady=(0, 5))
        
        # Quick notes entry
        self.notes_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Add quick notes..."
        )
        self.notes_entry.pack(side="left", fill="x", expand=True, padx=(5, 2), pady=5)
        
        # Add note button
        add_note_button = ctk.CTkButton(
            input_frame,
            text="Add",
            width=60,
            command=self._add_note
        )
        add_note_button.pack(side="right", padx=(2, 5), pady=5)
    
    def _create_analytics_panel(self):
        """Create analytics panel"""
        # Analytics display
        analytics_frame = ctk.CTkScrollableFrame(self.analytics_tab)
        analytics_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Sentiment indicator
        sentiment_frame = ctk.CTkFrame(analytics_frame)
        sentiment_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(sentiment_frame, text="😊 Sentiment:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        self.sentiment_label = ctk.CTkLabel(sentiment_frame, text="Neutral")
        self.sentiment_label.pack(side="left", padx=5)
        
        # Engagement meter
        engagement_frame = ctk.CTkFrame(analytics_frame)
        engagement_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(engagement_frame, text="🎯 Engagement:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        self.engagement_progress = ctk.CTkProgressBar(engagement_frame, width=100)
        self.engagement_progress.pack(side="left", padx=5, pady=10)
        self.engagement_progress.set(0.5)
        
        # Speaking time
        speaking_frame = ctk.CTkFrame(analytics_frame)
        speaking_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(speaking_frame, text="⏱️ Talk Time:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        self.talk_time_label = ctk.CTkLabel(speaking_frame, text="You: 45% | Them: 55%")
        self.talk_time_label.pack(side="left", padx=5)
        
        # Objections detected
        objections_frame = ctk.CTkFrame(analytics_frame)
        objections_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(objections_frame, text="⚠️ Objections:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        self.objections_label = ctk.CTkLabel(objections_frame, text="None detected")
        self.objections_label.pack(side="left", padx=5)
    
    def _create_status_bar(self):
        """Create status bar"""
        self.status_frame = ctk.CTkFrame(self.main_frame, height=30)
        self.status_frame.pack(fill="x", padx=5, pady=(0, 5))
        self.status_frame.pack_propagate(False)
        
        # Status indicators
        self.connection_status = ctk.CTkLabel(
            self.status_frame,
            text="🟢 Connected",
            font=ctk.CTkFont(size=12)
        )
        self.connection_status.pack(side="left", padx=5, pady=5)
        
        self.recording_status = ctk.CTkLabel(
            self.status_frame,
            text="⏹️ Not Recording",
            font=ctk.CTkFont(size=12)
        )
        self.recording_status.pack(side="right", padx=5, pady=5)
    
    def _setup_bindings(self):
        """Set up keyboard and mouse bindings"""
        try:
            # Keyboard shortcuts
            self.root.bind("<Control-r>", lambda e: self._toggle_recording())
            self.root.bind("<Control-s>", lambda e: self.on_open_settings())
            self.root.bind("<Control-d>", lambda e: self.on_open_dashboard())
            self.root.bind("<Control-h>", lambda e: self._toggle_visibility())
            self.root.bind("<Escape>", lambda e: self._minimize_window())
            
            # Mouse bindings for dragging
            self.header_frame.bind("<Button-1>", self._start_drag)
            self.header_frame.bind("<B1-Motion>", self._drag_window)
            
        except Exception as e:
            logger.error(f"Error setting up bindings: {e}")
    
    def show_suggestions(self, suggestions: List[Dict[str, Any]]):
        """Display AI suggestions"""
        try:
            self.current_suggestions = suggestions
            
            # Clear existing suggestions
            for widget in self.suggestions_scroll.winfo_children():
                widget.destroy()
            
            if not suggestions:
                # Show no suggestions message
                self.no_suggestions_label = ctk.CTkLabel(
                    self.suggestions_scroll,
                    text="🤖 No suggestions at the moment",
                    text_color="gray"
                )
                self.no_suggestions_label.pack(pady=20)
                return
            
            # Display suggestions
            for i, suggestion in enumerate(suggestions):
                self._create_suggestion_widget(suggestion, i)
            
            # Switch to suggestions tab
            self.tab_view.set("💡 Suggestions")
            
        except Exception as e:
            logger.error(f"Error showing suggestions: {e}")
    
    def update_teleprompter(self, teleprompter_data: Dict[str, Any]):
        """Update teleprompter with new prompts and stage info"""
        try:
            if hasattr(self, 'teleprompter_widget'):
                self.teleprompter_widget.update_prompts(teleprompter_data)
                
                # Switch to teleprompter tab if active
                if teleprompter_data.get("prompts") and self.teleprompter_widget.get_is_active():
                    self.tab_view.set("🎯 Teleprompter")
                    
        except Exception as e:
            logger.error(f"Error updating teleprompter: {e}")
    
    def show_win_rate_prediction(self, prediction_data: Dict[str, Any]):
        """Show win rate prediction in teleprompter"""
        try:
            if hasattr(self, 'teleprompter_widget'):
                self.teleprompter_widget.show_win_rate_prediction(prediction_data)
                
        except Exception as e:
            logger.error(f"Error showing win rate prediction: {e}")
    
    def _create_suggestion_widget(self, suggestion: Dict[str, Any], index: int):
        """Create a widget for a single suggestion"""
        try:
            # Suggestion frame
            suggestion_frame = ctk.CTkFrame(self.suggestions_scroll)
            suggestion_frame.pack(fill="x", padx=5, pady=5)
            
            # Suggestion type icon
            type_icons = {
                "response": "💬",
                "question": "❓",
                "objection_response": "🛡️",
                "closing": "🎯",
                "follow_up": "📧"
            }
            icon = type_icons.get(suggestion.get("type", "response"), "💡")
            
            # Header with icon and confidence
            header_frame = ctk.CTkFrame(suggestion_frame)
            header_frame.pack(fill="x", padx=5, pady=(5, 0))
            
            icon_label = ctk.CTkLabel(header_frame, text=icon, font=ctk.CTkFont(size=16))
            icon_label.pack(side="left", padx=5)
            
            confidence = suggestion.get("confidence", 0)
            confidence_label = ctk.CTkLabel(
                header_frame,
                text=f"{confidence:.0%}",
                font=ctk.CTkFont(size=12),
                text_color="green" if confidence > 0.7 else "orange" if confidence > 0.4 else "red"
            )
            confidence_label.pack(side="right", padx=5)
            
            # Suggestion text
            text_label = ctk.CTkLabel(
                suggestion_frame,
                text=suggestion.get("text", ""),
                wraplength=350,
                justify="left"
            )
            text_label.pack(fill="x", padx=10, pady=5)
            
            # Action buttons
            buttons_frame = ctk.CTkFrame(suggestion_frame)
            buttons_frame.pack(fill="x", padx=5, pady=(0, 5))
            
            # Copy button
            copy_button = ctk.CTkButton(
                buttons_frame,
                text="📋 Copy",
                width=80,
                height=25,
                command=lambda s=suggestion: self._copy_suggestion(s)
            )
            copy_button.pack(side="left", padx=5, pady=2)
            
            # Use button
            use_button = ctk.CTkButton(
                buttons_frame,
                text="✅ Use",
                width=80,
                height=25,
                command=lambda s=suggestion: self._use_suggestion(s)
            )
            use_button.pack(side="left", padx=2, pady=2)
            
            # Feedback buttons
            thumbs_up = ctk.CTkButton(
                buttons_frame,
                text="👍",
                width=30,
                height=25,
                command=lambda s=suggestion: self._rate_suggestion(s, True)
            )
            thumbs_up.pack(side="right", padx=2, pady=2)
            
            thumbs_down = ctk.CTkButton(
                buttons_frame,
                text="👎",
                width=30,
                height=25,
                command=lambda s=suggestion: self._rate_suggestion(s, False)
            )
            thumbs_down.pack(side="right", padx=2, pady=2)
            
        except Exception as e:
            logger.error(f"Error creating suggestion widget: {e}")
    
    def add_speech(self, text: str, speaker: str, timestamp: datetime):
        """Add speech to conversation display"""
        try:
            # Format timestamp
            time_str = timestamp.strftime("%H:%M:%S")
            
            # Speaker emoji
            speaker_emoji = "👤" if speaker == "user" else "🗣️"
            
            # Add to conversation text
            entry = f"[{time_str}] {speaker_emoji} {speaker}: {text}\n"
            
            self.conversation_text.insert("end", entry)
            self.conversation_text.see("end")
            
            # Store in history
            self.conversation_history.append({
                "text": text,
                "speaker": speaker,
                "timestamp": timestamp
            })
            
        except Exception as e:
            logger.error(f"Error adding speech: {e}")
    
    def highlight_objection(self, objection: Dict[str, Any], responses: List[str]):
        """Highlight detected objection"""
        try:
            # Create objection notification
            objection_window = ctk.CTkToplevel(self.root)
            objection_window.title("Objection Detected!")
            objection_window.geometry("400x300")
            objection_window.attributes('-topmost', True)
            
            # Objection details
            ctk.CTkLabel(
                objection_window,
                text="🚨 Objection Detected",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="red"
            ).pack(pady=10)
            
            ctk.CTkLabel(
                objection_window,
                text=f"Type: {objection.get('type', 'Unknown')}",
                font=ctk.CTkFont(size=14)
            ).pack(pady=5)
            
            ctk.CTkLabel(
                objection_window,
                text=f"Urgency: {objection.get('urgency', 'Medium')}",
                font=ctk.CTkFont(size=14)
            ).pack(pady=5)
            
            # Suggested responses
            ctk.CTkLabel(
                objection_window,
                text="Suggested Responses:",
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(pady=(10, 5))
            
            responses_frame = ctk.CTkScrollableFrame(objection_window, height=150)
            responses_frame.pack(fill="both", expand=True, padx=10, pady=5)
            
            for i, response in enumerate(responses[:3]):  # Show top 3 responses
                response_button = ctk.CTkButton(
                    responses_frame,
                    text=response,
                    wraplength=350,
                    command=lambda r=response: self._use_objection_response(r, objection_window)
                )
                response_button.pack(fill="x", padx=5, pady=2)
            
            # Auto-close after 30 seconds
            objection_window.after(30000, objection_window.destroy)
            
        except Exception as e:
            logger.error(f"Error highlighting objection: {e}")
    
    def update_analysis(self, analysis: Dict[str, Any]):
        """Update conversation analysis display"""
        try:
            # Update sentiment
            sentiment = analysis.get("sentiment", {})
            if sentiment:
                overall = sentiment.get("overall", "neutral")
                confidence = sentiment.get("confidence", 0)
                self.sentiment_label.configure(text=f"{overall.title()} ({confidence:.0%})")
            
            # Update engagement
            engagement = analysis.get("engagement", {})
            if engagement:
                score = engagement.get("score", 0.5)
                self.engagement_progress.set(score)
            
            # Update objections
            objections = analysis.get("objections", [])
            if objections:
                count = len(objections)
                latest = objections[-1].get("type", "Unknown") if objections else "None"
                self.objections_label.configure(text=f"{count} detected (Latest: {latest})")
            
        except Exception as e:
            logger.error(f"Error updating analysis: {e}")
    
    def set_recording_status(self, is_recording: bool):
        """Update recording status"""
        self.is_recording = is_recording
        
        if is_recording:
            self.record_button.configure(text="⏹️ Stop", fg_color="green")
            self.recording_status.configure(text="🔴 Recording")
        else:
            self.record_button.configure(text="🎙️ Record", fg_color="red")
            self.recording_status.configure(text="⏹️ Not Recording")
    
    def _toggle_recording(self):
        """Toggle recording"""
        self.on_toggle_recording()
    
    def _toggle_pin(self):
        """Toggle window pin state"""
        self.is_pinned = not self.is_pinned
        if self.is_pinned:
            self.pin_button.configure(text="📍", fg_color="orange")
            self.root.attributes('-topmost', True)
        else:
            self.pin_button.configure(text="📌", fg_color=None)
            self.root.attributes('-topmost', False)
    
    def _toggle_visibility(self):
        """Toggle window visibility"""
        if self.is_visible:
            self.root.withdraw()
            self.is_visible = False
        else:
            self.root.deiconify()
            self.is_visible = True
    
    def _minimize_window(self):
        """Minimize window"""
        self.root.iconify()
    
    def _copy_suggestion(self, suggestion: Dict[str, Any]):
        """Copy suggestion to clipboard"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(suggestion.get("text", ""))
            logger.info("Suggestion copied to clipboard")
        except Exception as e:
            logger.error(f"Error copying suggestion: {e}")
    
    def _use_suggestion(self, suggestion: Dict[str, Any]):
        """Use suggestion (copy and mark as used)"""
        self._copy_suggestion(suggestion)
        self.on_suggestion_click(suggestion)
    
    def _use_objection_response(self, response: str, window):
        """Use objection response"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(response)
            window.destroy()
            logger.info("Objection response copied to clipboard")
        except Exception as e:
            logger.error(f"Error using objection response: {e}")
    
    def _rate_suggestion(self, suggestion: Dict[str, Any], is_positive: bool):
        """Rate suggestion"""
        try:
            # TODO: Send rating to API
            rating = "positive" if is_positive else "negative"
            logger.info(f"Suggestion rated: {rating}")
        except Exception as e:
            logger.error(f"Error rating suggestion: {e}")
    
    def _add_note(self):
        """Add quick note"""
        try:
            note_text = self.notes_entry.get().strip()
            if note_text:
                timestamp = datetime.now().strftime("%H:%M:%S")
                entry = f"[{timestamp}] 📝 Note: {note_text}\n"
                self.conversation_text.insert("end", entry)
                self.conversation_text.see("end")
                self.notes_entry.delete(0, "end")
        except Exception as e:
            logger.error(f"Error adding note: {e}")
    
    def _start_drag(self, event):
        """Start window dragging"""
        self._drag_start_x = event.x
        self._drag_start_y = event.y
    
    def _drag_window(self, event):
        """Drag window"""
        try:
            x = self.root.winfo_x() + (event.x - self._drag_start_x)
            y = self.root.winfo_y() + (event.y - self._drag_start_y)
            self.root.geometry(f"+{x}+{y}")
        except Exception as e:
            logger.error(f"Error dragging window: {e}")
    
    def _on_window_close(self):
        """Handle window close"""
        self._minimize_window()  # Minimize instead of closing
    
    def show(self):
        """Show window"""
        self.root.deiconify()
        self.root.lift()
        self.is_visible = True
    
    def hide(self):
        """Hide window"""
        self.root.withdraw()
        self.is_visible = False
    
    def load_conversation(self, conversation: Dict[str, Any]):
        """Load conversation data"""
        try:
            # Clear current conversation
            self.conversation_text.delete("1.0", "end")
            
            # Load conversation history
            transcript = conversation.get("transcript", "")
            if transcript:
                self.conversation_text.insert("end", transcript)
            
            # Update analytics
            analytics = conversation.get("analytics", {})
            if analytics:
                self.update_analysis(analytics)
                
        except Exception as e:
            logger.error(f"Error loading conversation: {e}")
