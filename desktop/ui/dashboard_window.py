"""
Dashboard Window for analytics and conversation management
"""

import tkinter as tk
import customtkinter as ctk
from typing import Dict, List, Any, Callable
from datetime import datetime
from loguru import logger


class DashboardWindow:
    """Analytics dashboard window"""
    
    def __init__(self, api_client, on_conversation_selected: Callable):
        self.api_client = api_client
        self.on_conversation_selected = on_conversation_selected
        self.window = None
        self.is_visible = False
    
    def show(self):
        """Show dashboard window"""
        try:
            if self.window and self.is_visible:
                self.window.lift()
                return
            
            self._create_window()
            self.is_visible = True
            
        except Exception as e:
            logger.error(f"Error showing dashboard: {e}")
    
    def _create_window(self):
        """Create dashboard window"""
        self.window = ctk.CTkToplevel()
        self.window.title("📊 Analytics Dashboard")
        self.window.geometry("800x600")
        
        # Dashboard content
        ctk.CTkLabel(
            self.window,
            text="📊 Analytics Dashboard",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)
        
        # Mock analytics data
        ctk.CTkLabel(
            self.window,
            text="📈 Win Rate: 78%\n💬 Conversations: 45\n🎯 Objections Handled: 23",
            font=ctk.CTkFont(size=14)
        ).pack(pady=20)
