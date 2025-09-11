"""
Adaptive Teleprompter Widget - Cluely.ai's signature feature
Real-time prompts and talk tracks that adapt to conversation flow
"""

import tkinter as tk
import customtkinter as ctk
from typing import Dict, List, Any, Callable
from datetime import datetime
import threading
from loguru import logger


class TeleprompterWidget(ctk.CTkFrame):
    """Adaptive teleprompter widget matching Cluely.ai's design"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.current_prompts = []
        self.current_stage = "opening"
        self.talk_track_progress = 0
        self.is_active = False
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up teleprompter interface"""
        try:
            # Header
            header_frame = ctk.CTkFrame(self)
            header_frame.pack(fill="x", padx=5, pady=(5, 0))
            
            # Teleprompter icon and title
            title_frame = ctk.CTkFrame(header_frame)
            title_frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)
            
            ctk.CTkLabel(
                title_frame,
                text="🎯 AI Teleprompter",
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(side="left", padx=5)
            
            # Stage indicator
            self.stage_label = ctk.CTkLabel(
                title_frame,
                text="Opening",
                font=ctk.CTkFont(size=12),
                text_color="orange"
            )
            self.stage_label.pack(side="right", padx=5)
            
            # Progress bar
            progress_frame = ctk.CTkFrame(self)
            progress_frame.pack(fill="x", padx=5, pady=(2, 0))
            
            ctk.CTkLabel(
                progress_frame,
                text="Talk Track Progress:",
                font=ctk.CTkFont(size=10)
            ).pack(side="left", padx=5, pady=2)
            
            self.progress_bar = ctk.CTkProgressBar(progress_frame, width=100, height=8)
            self.progress_bar.pack(side="right", padx=5, pady=2)
            self.progress_bar.set(0.0)
            
            # Prompts container
            self.prompts_frame = ctk.CTkScrollableFrame(
                self,
                height=200,
                label_text="💡 Real-time Prompts"
            )
            self.prompts_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Default message
            self.default_message = ctk.CTkLabel(
                self.prompts_frame,
                text="🎤 Start speaking to see adaptive prompts...",
                font=ctk.CTkFont(size=12),
                text_color="gray"
            )
            self.default_message.pack(pady=20)
            
            # Controls
            controls_frame = ctk.CTkFrame(self)
            controls_frame.pack(fill="x", padx=5, pady=(0, 5))
            
            self.activate_button = ctk.CTkButton(
                controls_frame,
                text="🚀 Activate Teleprompter",
                width=150,
                height=30,
                command=self._toggle_teleprompter,
                fg_color="green"
            )
            self.activate_button.pack(side="left", padx=5, pady=5)
            
            # Settings button
            settings_button = ctk.CTkButton(
                controls_frame,
                text="⚙️",
                width=30,
                height=30,
                command=self._open_settings
            )
            settings_button.pack(side="right", padx=5, pady=5)
            
        except Exception as e:
            logger.error(f"Error setting up teleprompter UI: {e}")
    
    def update_prompts(self, prompts_data: Dict[str, Any]):
        """Update teleprompter with new prompts"""
        try:
            prompts = prompts_data.get("prompts", [])
            stage = prompts_data.get("stage", "unknown")
            progress = prompts_data.get("talk_track_progress", {})
            
            # Update stage
            self.current_stage = stage
            self.stage_label.configure(text=stage.replace("_", " ").title())
            
            # Update progress
            progress_pct = progress.get("progress_percentage", 0) / 100
            self.progress_bar.set(progress_pct)
            
            # Clear existing prompts
            for widget in self.prompts_frame.winfo_children():
                widget.destroy()
            
            # Add new prompts
            if not prompts:
                self.default_message = ctk.CTkLabel(
                    self.prompts_frame,
                    text="🤖 Listening for conversation cues...",
                    font=ctk.CTkFont(size=12),
                    text_color="gray"
                )
                self.default_message.pack(pady=20)
                return
            
            for i, prompt in enumerate(prompts):
                self._create_prompt_widget(prompt, i)
            
        except Exception as e:
            logger.error(f"Error updating prompts: {e}")
    
    def _create_prompt_widget(self, prompt: Dict[str, Any], index: int):
        """Create widget for individual prompt"""
        try:
            prompt_frame = ctk.CTkFrame(self.prompts_frame)
            prompt_frame.pack(fill="x", padx=5, pady=3)
            
            # Prompt type icon
            type_icons = {
                "adaptive_response": "💬",
                "stage_prompt": "🎯",
                "urgency_builder": "⚡",
                "social_proof": "👥",
                "risk_reversal": "🛡️"
            }
            
            prompt_type = prompt.get("type", "adaptive_response")
            icon = type_icons.get(prompt_type, "💡")
            
            # Header with icon and confidence
            header_frame = ctk.CTkFrame(prompt_frame)
            header_frame.pack(fill="x", padx=5, pady=(5, 0))
            
            icon_label = ctk.CTkLabel(
                header_frame,
                text=icon,
                font=ctk.CTkFont(size=16)
            )
            icon_label.pack(side="left", padx=5)
            
            # Confidence indicator
            confidence = prompt.get("confidence", 0.5)
            confidence_color = "green" if confidence > 0.7 else "orange" if confidence > 0.4 else "red"
            
            confidence_label = ctk.CTkLabel(
                header_frame,
                text=f"{confidence:.0%}",
                font=ctk.CTkFont(size=10),
                text_color=confidence_color
            )
            confidence_label.pack(side="right", padx=5)
            
            # Stage indicator
            stage = prompt.get("stage", self.current_stage)
            stage_badge = ctk.CTkLabel(
                header_frame,
                text=stage.replace("_", " ").title(),
                font=ctk.CTkFont(size=10),
                text_color="blue"
            )
            stage_badge.pack(side="right", padx=10)
            
            # Prompt text
            prompt_text = prompt.get("text", "")
            text_label = ctk.CTkLabel(
                prompt_frame,
                text=prompt_text,
                wraplength=320,
                justify="left",
                font=ctk.CTkFont(size=11)
            )
            text_label.pack(fill="x", padx=10, pady=(0, 5))
            
            # Action buttons
            buttons_frame = ctk.CTkFrame(prompt_frame)
            buttons_frame.pack(fill="x", padx=5, pady=(0, 5))
            
            # Copy button
            copy_button = ctk.CTkButton(
                buttons_frame,
                text="📋",
                width=30,
                height=25,
                command=lambda: self._copy_prompt(prompt_text)
            )
            copy_button.pack(side="left", padx=2, pady=2)
            
            # Use button
            use_button = ctk.CTkButton(
                buttons_frame,
                text="✅ Use",
                width=60,
                height=25,
                command=lambda: self._use_prompt(prompt)
            )
            use_button.pack(side="left", padx=2, pady=2)
            
            # Feedback buttons
            thumbs_up = ctk.CTkButton(
                buttons_frame,
                text="👍",
                width=25,
                height=25,
                command=lambda: self._rate_prompt(prompt, True)
            )
            thumbs_up.pack(side="right", padx=1, pady=2)
            
            thumbs_down = ctk.CTkButton(
                buttons_frame,
                text="👎", 
                width=25,
                height=25,
                command=lambda: self._rate_prompt(prompt, False)
            )
            thumbs_down.pack(side="right", padx=1, pady=2)
            
        except Exception as e:
            logger.error(f"Error creating prompt widget: {e}")
    
    def _toggle_teleprompter(self):
        """Toggle teleprompter activation"""
        try:
            self.is_active = not self.is_active
            
            if self.is_active:
                self.activate_button.configure(
                    text="⏹️ Stop Teleprompter",
                    fg_color="red"
                )
                logger.info("Teleprompter activated")
            else:
                self.activate_button.configure(
                    text="🚀 Activate Teleprompter", 
                    fg_color="green"
                )
                logger.info("Teleprompter deactivated")
            
        except Exception as e:
            logger.error(f"Error toggling teleprompter: {e}")
    
    def _copy_prompt(self, text: str):
        """Copy prompt to clipboard"""
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
            logger.info(f"Prompt copied: {text[:50]}...")
        except Exception as e:
            logger.error(f"Error copying prompt: {e}")
    
    def _use_prompt(self, prompt: Dict[str, Any]):
        """Mark prompt as used"""
        try:
            self._copy_prompt(prompt.get("text", ""))
            # TODO: Send usage analytics to backend
            logger.info(f"Prompt used: {prompt.get('type', 'unknown')}")
        except Exception as e:
            logger.error(f"Error using prompt: {e}")
    
    def _rate_prompt(self, prompt: Dict[str, Any], is_positive: bool):
        """Rate prompt quality"""
        try:
            rating = "positive" if is_positive else "negative"
            # TODO: Send rating to backend for ML improvement
            logger.info(f"Prompt rated {rating}: {prompt.get('type', 'unknown')}")
        except Exception as e:
            logger.error(f"Error rating prompt: {e}")
    
    def _open_settings(self):
        """Open teleprompter settings"""
        try:
            # Create settings popup
            settings_window = ctk.CTkToplevel(self)
            settings_window.title("Teleprompter Settings")
            settings_window.geometry("400x300")
            settings_window.attributes('-topmost', True)
            
            # Settings content
            ctk.CTkLabel(
                settings_window,
                text="🎯 Teleprompter Settings",
                font=ctk.CTkFont(size=16, weight="bold")
            ).pack(pady=10)
            
            # Talk track selection
            track_frame = ctk.CTkFrame(settings_window)
            track_frame.pack(fill="x", padx=20, pady=10)
            
            ctk.CTkLabel(
                track_frame,
                text="Talk Track Type:",
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(pady=5)
            
            track_options = ["Sales Discovery", "Demo Call", "Follow-up Call", "Closing Call"]
            track_menu = ctk.CTkOptionMenu(
                track_frame,
                values=track_options,
                width=200
            )
            track_menu.pack(pady=5)
            
            # Prompt frequency
            freq_frame = ctk.CTkFrame(settings_window)
            freq_frame.pack(fill="x", padx=20, pady=10)
            
            ctk.CTkLabel(
                freq_frame,
                text="Prompt Frequency:",
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(pady=5)
            
            freq_slider = ctk.CTkSlider(
                freq_frame,
                from_=1,
                to=10,
                number_of_steps=9,
                width=200
            )
            freq_slider.pack(pady=5)
            freq_slider.set(5)
            
            # Save button
            save_button = ctk.CTkButton(
                settings_window,
                text="💾 Save Settings",
                command=settings_window.destroy
            )
            save_button.pack(pady=20)
            
        except Exception as e:
            logger.error(f"Error opening teleprompter settings: {e}")
    
    def show_win_rate_prediction(self, prediction_data: Dict[str, Any]):
        """Show win rate prediction"""
        try:
            prediction = prediction_data.get("prediction", 0.5)
            confidence = prediction_data.get("confidence", 0.0)
            
            # Create win rate indicator
            win_rate_frame = ctk.CTkFrame(self.prompts_frame)
            win_rate_frame.pack(fill="x", padx=5, pady=5)
            
            # Win rate header
            header_frame = ctk.CTkFrame(win_rate_frame)
            header_frame.pack(fill="x", padx=5, pady=5)
            
            ctk.CTkLabel(
                header_frame,
                text="🎯 Win Rate Prediction",
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(side="left", padx=5)
            
            # Prediction percentage
            prediction_color = "green" if prediction > 0.7 else "orange" if prediction > 0.4 else "red"
            
            ctk.CTkLabel(
                header_frame,
                text=f"{prediction:.0%}",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=prediction_color
            ).pack(side="right", padx=5)
            
            # Confidence indicator
            ctk.CTkLabel(
                win_rate_frame,
                text=f"Confidence: {confidence:.0%}",
                font=ctk.CTkFont(size=10),
                text_color="gray"
            ).pack(padx=5, pady=(0, 5))
            
            # Recommendation
            recommendation = prediction_data.get("recommendation", "")
            if recommendation:
                ctk.CTkLabel(
                    win_rate_frame,
                    text=f"💡 {recommendation}",
                    font=ctk.CTkFont(size=10),
                    wraplength=300,
                    text_color="blue"
                ).pack(padx=5, pady=(0, 5))
            
        except Exception as e:
            logger.error(f"Error showing win rate prediction: {e}")
    
    def get_is_active(self) -> bool:
        """Check if teleprompter is active"""
        return self.is_active
