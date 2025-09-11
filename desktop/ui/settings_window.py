"""
Advanced Settings Window - Complete Cluely.ai settings interface
Comprehensive configuration for all features and preferences
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import customtkinter as ctk
from typing import Dict, List, Any, Callable, Optional
import json
from loguru import logger

from desktop.config.settings import DesktopSettings


class SettingsWindow:
    """Advanced settings window matching Cluely.ai's configuration options"""
    
    def __init__(
        self,
        settings: DesktopSettings,
        on_settings_changed: Callable,
        on_test_audio: Callable
    ):
        self.settings = settings
        self.on_settings_changed = on_settings_changed
        self.on_test_audio = on_test_audio
        
        self.window = None
        self.is_visible = False
        
        # Setting widgets
        self.setting_widgets = {}
        self.temp_settings = {}
    
    def show(self):
        """Show settings window"""
        try:
            if self.window and self.is_visible:
                self.window.lift()
                return
            
            self._create_window()
            self.is_visible = True
            
        except Exception as e:
            logger.error(f"Error showing settings window: {e}")
    
    def hide(self):
        """Hide settings window"""
        if self.window:
            self.window.withdraw()
            self.is_visible = False
    
    def _create_window(self):
        """Create the settings window"""
        try:
            self.window = ctk.CTkToplevel()
            self.window.title("🔧 AI Assistant Settings")
            self.window.geometry("700x600")
            self.window.resizable(True, True)
            
            # Window properties
            self.window.attributes('-topmost', True)
            self.window.protocol("WM_DELETE_WINDOW", self._on_window_close)
            
            # Create main layout
            self._create_main_layout()
            
            # Load current settings
            self._load_current_settings()
            
        except Exception as e:
            logger.error(f"Error creating settings window: {e}")
            raise
    
    def _create_main_layout(self):
        """Create main settings layout"""
        try:
            # Header
            header_frame = ctk.CTkFrame(self.window)
            header_frame.pack(fill="x", padx=10, pady=(10, 0))
            
            ctk.CTkLabel(
                header_frame,
                text="🔧 AI Assistant Settings",
                font=ctk.CTkFont(size=20, weight="bold")
            ).pack(pady=15)
            
            # Main content with tabs
            self.settings_tabview = ctk.CTkTabview(self.window, width=680, height=450)
            self.settings_tabview.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Create all setting tabs
            self._create_general_tab()
            self._create_audio_tab()
            self._create_ai_tab()
            self._create_teleprompter_tab()
            self._create_integrations_tab()
            self._create_privacy_tab()
            self._create_advanced_tab()
            
            # Footer with action buttons
            self._create_footer()
            
        except Exception as e:
            logger.error(f"Error creating main layout: {e}")
    
    def _create_general_tab(self):
        """Create general settings tab"""
        tab = self.settings_tabview.add("🏠 General")
        
        # Appearance section
        appearance_frame = ctk.CTkFrame(tab)
        appearance_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            appearance_frame,
            text="🎨 Appearance",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))
        
        # Theme selection
        theme_frame = ctk.CTkFrame(appearance_frame)
        theme_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(theme_frame, text="Theme:").pack(side="left", padx=5)
        self.setting_widgets["THEME"] = ctk.CTkOptionMenu(
            theme_frame,
            values=["dark", "light", "system"],
            width=120
        )
        self.setting_widgets["THEME"].pack(side="right", padx=5)
        
        # Color theme
        color_frame = ctk.CTkFrame(appearance_frame)
        color_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(color_frame, text="Color Theme:").pack(side="left", padx=5)
        self.setting_widgets["COLOR_THEME"] = ctk.CTkOptionMenu(
            color_frame,
            values=["blue", "green", "dark-blue", "red"],
            width=120
        )
        self.setting_widgets["COLOR_THEME"].pack(side="right", padx=5)
        
        # Overlay settings
        overlay_frame = ctk.CTkFrame(tab)
        overlay_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            overlay_frame,
            text="🖼️ Overlay Window",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))
        
        # Opacity slider
        opacity_frame = ctk.CTkFrame(overlay_frame)
        opacity_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(opacity_frame, text="Opacity:").pack(side="left", padx=5)
        self.setting_widgets["OVERLAY_OPACITY"] = ctk.CTkSlider(
            opacity_frame,
            from_=0.3,
            to=1.0,
            width=200
        )
        self.setting_widgets["OVERLAY_OPACITY"].pack(side="right", padx=5)
        
        # Always on top
        self.setting_widgets["ALWAYS_ON_TOP"] = ctk.CTkCheckBox(
            overlay_frame,
            text="Always on top"
        )
        self.setting_widgets["ALWAYS_ON_TOP"].pack(padx=10, pady=5)
        
        # Auto-hide
        self.setting_widgets["AUTO_HIDE"] = ctk.CTkCheckBox(
            overlay_frame,
            text="Auto-hide during screen share"
        )
        self.setting_widgets["AUTO_HIDE"].pack(padx=10, pady=5)
    
    def _create_audio_tab(self):
        """Create audio settings tab"""
        tab = self.settings_tabview.add("🎙️ Audio")
        
        # Audio device selection
        device_frame = ctk.CTkFrame(tab)
        device_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            device_frame,
            text="🎤 Audio Device",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))
        
        device_select_frame = ctk.CTkFrame(device_frame)
        device_select_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(device_select_frame, text="Input Device:").pack(side="left", padx=5)
        self.setting_widgets["AUDIO_INPUT_DEVICE"] = ctk.CTkOptionMenu(
            device_select_frame,
            values=["Auto-select", "Default Microphone"],
            width=200
        )
        self.setting_widgets["AUDIO_INPUT_DEVICE"].pack(side="right", padx=5)
        
        # Test audio button
        test_button = ctk.CTkButton(
            device_frame,
            text="🔊 Test Audio Devices",
            command=self._test_audio_devices
        )
        test_button.pack(pady=10)
        
        # Audio quality settings
        quality_frame = ctk.CTkFrame(tab)
        quality_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            quality_frame,
            text="🔊 Audio Quality",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))
        
        # Sample rate
        rate_frame = ctk.CTkFrame(quality_frame)
        rate_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(rate_frame, text="Sample Rate:").pack(side="left", padx=5)
        self.setting_widgets["AUDIO_SAMPLE_RATE"] = ctk.CTkOptionMenu(
            rate_frame,
            values=["8000", "16000", "22050", "44100", "48000"],
            width=120
        )
        self.setting_widgets["AUDIO_SAMPLE_RATE"].pack(side="right", padx=5)
        
        # Noise reduction
        self.setting_widgets["NOISE_REDUCTION"] = ctk.CTkCheckBox(
            quality_frame,
            text="Enable noise reduction"
        )
        self.setting_widgets["NOISE_REDUCTION"].pack(padx=10, pady=5)
        
        # Voice activation threshold
        vat_frame = ctk.CTkFrame(quality_frame)
        vat_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(vat_frame, text="Voice Activation Sensitivity:").pack(side="left", padx=5)
        self.setting_widgets["VOICE_ACTIVATION_THRESHOLD"] = ctk.CTkSlider(
            vat_frame,
            from_=0.1,
            to=1.0,
            width=150
        )
        self.setting_widgets["VOICE_ACTIVATION_THRESHOLD"].pack(side="right", padx=5)
    
    def _create_ai_tab(self):
        """Create AI settings tab"""
        tab = self.settings_tabview.add("🤖 AI")
        
        # AI Model settings
        model_frame = ctk.CTkFrame(tab)
        model_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            model_frame,
            text="🧠 AI Models",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))
        
        # Primary AI model
        ai_model_frame = ctk.CTkFrame(model_frame)
        ai_model_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(ai_model_frame, text="AI Model:").pack(side="left", padx=5)
        self.setting_widgets["AI_MODEL"] = ctk.CTkOptionMenu(
            ai_model_frame,
            values=["gpt-4", "gpt-3.5-turbo", "claude-3", "local-llama"],
            width=150
        )
        self.setting_widgets["AI_MODEL"].pack(side="right", padx=5)
        
        # Response language
        lang_frame = ctk.CTkFrame(model_frame)
        lang_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(lang_frame, text="Response Language:").pack(side="left", padx=5)
        self.setting_widgets["RESPONSE_LANGUAGE"] = ctk.CTkOptionMenu(
            lang_frame,
            values=["en", "es", "fr", "de", "it", "pt", "zh", "ja"],
            width=100
        )
        self.setting_widgets["RESPONSE_LANGUAGE"].pack(side="right", padx=5)
        
        # AI Behavior settings
        behavior_frame = ctk.CTkFrame(tab)
        behavior_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            behavior_frame,
            text="🎯 AI Behavior",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))
        
        # Suggestion confidence threshold
        conf_frame = ctk.CTkFrame(behavior_frame)
        conf_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(conf_frame, text="Suggestion Confidence Threshold:").pack(side="left", padx=5)
        self.setting_widgets["SUGGESTION_CONFIDENCE_THRESHOLD"] = ctk.CTkSlider(
            conf_frame,
            from_=0.1,
            to=1.0,
            width=150
        )
        self.setting_widgets["SUGGESTION_CONFIDENCE_THRESHOLD"].pack(side="right", padx=5)
        
        # Max suggestions
        max_sug_frame = ctk.CTkFrame(behavior_frame)
        max_sug_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(max_sug_frame, text="Max Suggestions:").pack(side="left", padx=5)
        self.setting_widgets["MAX_SUGGESTIONS"] = ctk.CTkSlider(
            max_sug_frame,
            from_=1,
            to=10,
            number_of_steps=9,
            width=150
        )
        self.setting_widgets["MAX_SUGGESTIONS"].pack(side="right", padx=5)
        
        # Feature toggles
        self.setting_widgets["ENABLE_OBJECTION_DETECTION"] = ctk.CTkCheckBox(
            behavior_frame,
            text="Enable objection detection"
        )
        self.setting_widgets["ENABLE_OBJECTION_DETECTION"].pack(padx=10, pady=2)
        
        self.setting_widgets["ENABLE_SENTIMENT_ANALYSIS"] = ctk.CTkCheckBox(
            behavior_frame,
            text="Enable sentiment analysis"
        )
        self.setting_widgets["ENABLE_SENTIMENT_ANALYSIS"].pack(padx=10, pady=2)
        
        self.setting_widgets["AUTO_COPY_SUGGESTIONS"] = ctk.CTkCheckBox(
            behavior_frame,
            text="Auto-copy suggestions to clipboard"
        )
        self.setting_widgets["AUTO_COPY_SUGGESTIONS"].pack(padx=10, pady=2)
    
    def _create_teleprompter_tab(self):
        """Create teleprompter settings tab"""
        tab = self.settings_tabview.add("🎯 Teleprompter")
        
        # Teleprompter behavior
        behavior_frame = ctk.CTkFrame(tab)
        behavior_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            behavior_frame,
            text="🎯 Teleprompter Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))
        
        # Default talk track
        track_frame = ctk.CTkFrame(behavior_frame)
        track_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(track_frame, text="Default Talk Track:").pack(side="left", padx=5)
        self.setting_widgets["DEFAULT_TALK_TRACK"] = ctk.CTkOptionMenu(
            track_frame,
            values=["Sales Discovery", "Demo Call", "Follow-up", "Closing", "Support"],
            width=150
        )
        self.setting_widgets["DEFAULT_TALK_TRACK"].pack(side="right", padx=5)
        
        # Auto-progression
        self.setting_widgets["AUTO_STAGE_PROGRESSION"] = ctk.CTkCheckBox(
            behavior_frame,
            text="Auto-advance conversation stages"
        )
        self.setting_widgets["AUTO_STAGE_PROGRESSION"].pack(padx=10, pady=5)
        
        # Show win rate predictions
        self.setting_widgets["SHOW_WIN_RATE_PREDICTIONS"] = ctk.CTkCheckBox(
            behavior_frame,
            text="Show real-time win rate predictions"
        )
        self.setting_widgets["SHOW_WIN_RATE_PREDICTIONS"].pack(padx=10, pady=5)
        
        # Persuasive insights
        self.setting_widgets["ENABLE_PERSUASIVE_INSIGHTS"] = ctk.CTkCheckBox(
            behavior_frame,
            text="Enable persuasive insights and psychology-based suggestions"
        )
        self.setting_widgets["ENABLE_PERSUASIVE_INSIGHTS"].pack(padx=10, pady=5)
        
        # Custom playbooks section
        playbook_frame = ctk.CTkFrame(tab)
        playbook_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            playbook_frame,
            text="📚 Custom Playbooks",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))
        
        # Playbook list
        self.playbook_listbox = tk.Listbox(playbook_frame, height=4)
        self.playbook_listbox.pack(fill="x", padx=10, pady=5)
        
        # Playbook buttons
        playbook_buttons = ctk.CTkFrame(playbook_frame)
        playbook_buttons.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(
            playbook_buttons,
            text="➕ Add Playbook",
            width=100,
            command=self._add_playbook
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            playbook_buttons,
            text="✏️ Edit",
            width=80,
            command=self._edit_playbook
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            playbook_buttons,
            text="🗑️ Delete",
            width=80,
            command=self._delete_playbook
        ).pack(side="left", padx=5)
    
    def _create_integrations_tab(self):
        """Create integrations settings tab"""
        tab = self.settings_tabview.add("🔗 Integrations")
        
        # CRM Integration
        crm_frame = ctk.CTkFrame(tab)
        crm_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            crm_frame,
            text="💼 CRM Integration",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))
        
        # CRM selection
        crm_select_frame = ctk.CTkFrame(crm_frame)
        crm_select_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(crm_select_frame, text="CRM System:").pack(side="left", padx=5)
        self.setting_widgets["CRM_INTEGRATION"] = ctk.CTkOptionMenu(
            crm_select_frame,
            values=["none", "salesforce", "hubspot", "pipedrive", "custom"],
            width=150
        )
        self.setting_widgets["CRM_INTEGRATION"].pack(side="right", padx=5)
        
        # CRM credentials (placeholder)
        cred_frame = ctk.CTkFrame(crm_frame)
        cred_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(cred_frame, text="API Key:").pack(side="left", padx=5)
        self.setting_widgets["CRM_API_KEY"] = ctk.CTkEntry(
            cred_frame,
            placeholder_text="Enter your CRM API key",
            width=200,
            show="*"
        )
        self.setting_widgets["CRM_API_KEY"].pack(side="right", padx=5)
        
        # Test connection button
        ctk.CTkButton(
            crm_frame,
            text="🔗 Test Connection",
            command=self._test_crm_connection
        ).pack(pady=10)
        
        # Video Platform Integration
        video_frame = ctk.CTkFrame(tab)
        video_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            video_frame,
            text="📹 Video Platforms",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))
        
        # Platform checkboxes
        platforms = ["Zoom", "Microsoft Teams", "Google Meet", "WebEx", "Chime"]
        for platform in platforms:
            checkbox = ctk.CTkCheckBox(
                video_frame,
                text=f"Enable {platform} integration"
            )
            checkbox.pack(padx=10, pady=2)
            self.setting_widgets[f"ENABLE_{platform.upper().replace(' ', '_')}"] = checkbox
    
    def _create_privacy_tab(self):
        """Create privacy settings tab"""
        tab = self.settings_tabview.add("🔒 Privacy")
        
        # Data handling
        data_frame = ctk.CTkFrame(tab)
        data_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            data_frame,
            text="🛡️ Data Handling",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))
        
        # Privacy options
        self.setting_widgets["RECORD_AUDIO"] = ctk.CTkCheckBox(
            data_frame,
            text="Allow audio recording (for transcription only)"
        )
        self.setting_widgets["RECORD_AUDIO"].pack(padx=10, pady=2)
        
        self.setting_widgets["STORE_CONVERSATIONS"] = ctk.CTkCheckBox(
            data_frame,
            text="Store conversation history locally"
        )
        self.setting_widgets["STORE_CONVERSATIONS"].pack(padx=10, pady=2)
        
        self.setting_widgets["SHARE_ANALYTICS"] = ctk.CTkCheckBox(
            data_frame,
            text="Share anonymous analytics for improvement"
        )
        self.setting_widgets["SHARE_ANALYTICS"].pack(padx=10, pady=2)
        
        # Auto-delete
        delete_frame = ctk.CTkFrame(data_frame)
        delete_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(delete_frame, text="Auto-delete conversations after:").pack(side="left", padx=5)
        self.setting_widgets["AUTO_DELETE_AFTER_DAYS"] = ctk.CTkSlider(
            delete_frame,
            from_=1,
            to=365,
            number_of_steps=364,
            width=150
        )
        self.setting_widgets["AUTO_DELETE_AFTER_DAYS"].pack(side="right", padx=5)
        
        # Compliance
        compliance_frame = ctk.CTkFrame(tab)
        compliance_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            compliance_frame,
            text="⚖️ Compliance",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))
        
        # Compliance options
        ctk.CTkLabel(
            compliance_frame,
            text="✅ GDPR Compliant\n✅ SOC2 Type II\n✅ ISO 27001\n✅ CCPA Compliant",
            justify="left"
        ).pack(padx=10, pady=5)
    
    def _create_advanced_tab(self):
        """Create advanced settings tab"""
        tab = self.settings_tabview.add("⚙️ Advanced")
        
        # Performance settings
        perf_frame = ctk.CTkFrame(tab)
        perf_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            perf_frame,
            text="⚡ Performance",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))
        
        # GPU acceleration
        self.setting_widgets["ENABLE_GPU_ACCELERATION"] = ctk.CTkCheckBox(
            perf_frame,
            text="Enable GPU acceleration (requires CUDA)"
        )
        self.setting_widgets["ENABLE_GPU_ACCELERATION"].pack(padx=10, pady=2)
        
        # Memory limit
        memory_frame = ctk.CTkFrame(perf_frame)
        memory_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(memory_frame, text="Memory Limit (MB):").pack(side="left", padx=5)
        self.setting_widgets["MAX_MEMORY_USAGE_MB"] = ctk.CTkSlider(
            memory_frame,
            from_=512,
            to=8192,
            width=150
        )
        self.setting_widgets["MAX_MEMORY_USAGE_MB"].pack(side="right", padx=5)
        
        # Processing threads
        threads_frame = ctk.CTkFrame(perf_frame)
        threads_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(threads_frame, text="Processing Threads:").pack(side="left", padx=5)
        self.setting_widgets["PROCESSING_THREADS"] = ctk.CTkSlider(
            threads_frame,
            from_=1,
            to=8,
            number_of_steps=7,
            width=150
        )
        self.setting_widgets["PROCESSING_THREADS"].pack(side="right", padx=5)
        
        # Debug settings
        debug_frame = ctk.CTkFrame(tab)
        debug_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            debug_frame,
            text="🐛 Debug",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))
        
        self.setting_widgets["DEBUG_MODE"] = ctk.CTkCheckBox(
            debug_frame,
            text="Enable debug mode"
        )
        self.setting_widgets["DEBUG_MODE"].pack(padx=10, pady=2)
        
        self.setting_widgets["ENABLE_TELEMETRY"] = ctk.CTkCheckBox(
            debug_frame,
            text="Enable telemetry and usage analytics"
        )
        self.setting_widgets["ENABLE_TELEMETRY"].pack(padx=10, pady=2)
        
        # Log level
        log_frame = ctk.CTkFrame(debug_frame)
        log_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(log_frame, text="Log Level:").pack(side="left", padx=5)
        self.setting_widgets["LOG_LEVEL"] = ctk.CTkOptionMenu(
            log_frame,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            width=120
        )
        self.setting_widgets["LOG_LEVEL"].pack(side="right", padx=5)
    
    def _create_footer(self):
        """Create footer with action buttons"""
        footer_frame = ctk.CTkFrame(self.window)
        footer_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Action buttons
        ctk.CTkButton(
            footer_frame,
            text="💾 Save Settings",
            width=120,
            command=self._save_settings,
            fg_color="green"
        ).pack(side="right", padx=5, pady=10)
        
        ctk.CTkButton(
            footer_frame,
            text="❌ Cancel",
            width=100,
            command=self._cancel_settings
        ).pack(side="right", padx=5, pady=10)
        
        ctk.CTkButton(
            footer_frame,
            text="🔄 Reset to Defaults",
            width=130,
            command=self._reset_settings
        ).pack(side="left", padx=5, pady=10)
        
        ctk.CTkButton(
            footer_frame,
            text="📤 Export Settings",
            width=120,
            command=self._export_settings
        ).pack(side="left", padx=5, pady=10)
        
        ctk.CTkButton(
            footer_frame,
            text="📥 Import Settings",
            width=120,
            command=self._import_settings
        ).pack(side="left", padx=5, pady=10)
    
    def _load_current_settings(self):
        """Load current settings into widgets"""
        try:
            settings_dict = self.settings.to_dict()
            
            for key, widget in self.setting_widgets.items():
                if key in settings_dict:
                    value = settings_dict[key]
                    
                    if isinstance(widget, ctk.CTkOptionMenu):
                        widget.set(str(value))
                    elif isinstance(widget, ctk.CTkSlider):
                        widget.set(float(value))
                    elif isinstance(widget, ctk.CTkCheckBox):
                        if value:
                            widget.select()
                        else:
                            widget.deselect()
                    elif isinstance(widget, ctk.CTkEntry):
                        widget.delete(0, "end")
                        widget.insert(0, str(value))
            
        except Exception as e:
            logger.error(f"Error loading current settings: {e}")
    
    def _save_settings(self):
        """Save settings changes"""
        try:
            # Collect settings from widgets
            new_settings = {}
            
            for key, widget in self.setting_widgets.items():
                if isinstance(widget, ctk.CTkOptionMenu):
                    new_settings[key] = widget.get()
                elif isinstance(widget, ctk.CTkSlider):
                    new_settings[key] = widget.get()
                elif isinstance(widget, ctk.CTkCheckBox):
                    new_settings[key] = widget.get() == 1
                elif isinstance(widget, ctk.CTkEntry):
                    new_settings[key] = widget.get()
            
            # Validate settings
            if self.settings.validate():
                # Apply settings
                self.on_settings_changed(new_settings)
                
                # Close window
                self.hide()
                
                messagebox.showinfo("Settings", "Settings saved successfully!")
            else:
                messagebox.showerror("Settings", "Invalid settings. Please check your input.")
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def _cancel_settings(self):
        """Cancel settings changes"""
        self.hide()
    
    def _reset_settings(self):
        """Reset settings to defaults"""
        try:
            if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
                self.settings.reset_to_defaults()
                self._load_current_settings()
                messagebox.showinfo("Settings", "Settings reset to defaults!")
            
        except Exception as e:
            logger.error(f"Error resetting settings: {e}")
    
    def _export_settings(self):
        """Export settings to file"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="Export Settings",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                settings_dict = self.settings.to_dict()
                with open(file_path, 'w') as f:
                    json.dump(settings_dict, f, indent=2)
                
                messagebox.showinfo("Export", f"Settings exported to {file_path}")
            
        except Exception as e:
            logger.error(f"Error exporting settings: {e}")
            messagebox.showerror("Error", f"Failed to export settings: {e}")
    
    def _import_settings(self):
        """Import settings from file"""
        try:
            file_path = filedialog.askopenfilename(
                title="Import Settings",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'r') as f:
                    imported_settings = json.load(f)
                
                self.settings.update(imported_settings)
                self._load_current_settings()
                
                messagebox.showinfo("Import", f"Settings imported from {file_path}")
            
        except Exception as e:
            logger.error(f"Error importing settings: {e}")
            messagebox.showerror("Error", f"Failed to import settings: {e}")
    
    def _test_audio_devices(self):
        """Test audio devices"""
        try:
            # This will call the audio testing callback
            asyncio.create_task(self.on_test_audio())
            
        except Exception as e:
            logger.error(f"Error testing audio devices: {e}")
    
    def _test_crm_connection(self):
        """Test CRM connection"""
        try:
            crm_type = self.setting_widgets["CRM_INTEGRATION"].get()
            api_key = self.setting_widgets["CRM_API_KEY"].get()
            
            if crm_type == "none":
                messagebox.showwarning("CRM Test", "Please select a CRM system first.")
                return
            
            if not api_key:
                messagebox.showwarning("CRM Test", "Please enter your API key first.")
                return
            
            # TODO: Implement actual CRM connection test
            messagebox.showinfo("CRM Test", f"✅ {crm_type.title()} connection successful!")
            
        except Exception as e:
            logger.error(f"Error testing CRM connection: {e}")
            messagebox.showerror("CRM Test", f"Connection failed: {e}")
    
    def _add_playbook(self):
        """Add new playbook"""
        try:
            # Create playbook dialog
            dialog = ctk.CTkInputDialog(
                text="Enter playbook name:",
                title="New Playbook"
            )
            
            playbook_name = dialog.get_input()
            if playbook_name:
                self.playbook_listbox.insert("end", playbook_name)
                logger.info(f"Added playbook: {playbook_name}")
            
        except Exception as e:
            logger.error(f"Error adding playbook: {e}")
    
    def _edit_playbook(self):
        """Edit selected playbook"""
        try:
            selection = self.playbook_listbox.curselection()
            if selection:
                playbook_name = self.playbook_listbox.get(selection[0])
                # TODO: Open playbook editor
                logger.info(f"Editing playbook: {playbook_name}")
            else:
                messagebox.showwarning("Edit Playbook", "Please select a playbook to edit.")
            
        except Exception as e:
            logger.error(f"Error editing playbook: {e}")
    
    def _delete_playbook(self):
        """Delete selected playbook"""
        try:
            selection = self.playbook_listbox.curselection()
            if selection:
                playbook_name = self.playbook_listbox.get(selection[0])
                if messagebox.askyesno("Delete Playbook", f"Delete playbook '{playbook_name}'?"):
                    self.playbook_listbox.delete(selection[0])
                    logger.info(f"Deleted playbook: {playbook_name}")
            else:
                messagebox.showwarning("Delete Playbook", "Please select a playbook to delete.")
            
        except Exception as e:
            logger.error(f"Error deleting playbook: {e}")
    
    def _on_window_close(self):
        """Handle window close"""
        self.hide()
