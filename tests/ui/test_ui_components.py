"""
Tests for the UI components.
"""
import pytest
import tkinter as tk
from customtkinter import CTk, CTkButton, CTkLabel
from PIL import Image, ImageTk

from app.ui.main_window import MainWindow
from app.ui.system_tray import SystemTray
from app.ui.settings_dialog import SettingsDialog
from app.ui.call_controls import CallControls

pytestmark = pytest.mark.ui

@pytest.fixture
def root():
    """Create a root window for testing."""
    root = CTk()
    yield root
    root.destroy()

@pytest.fixture
def main_window(root):
    """Create a main window for testing."""
    window = MainWindow(root)
    yield window

@pytest.fixture
def system_tray():
    """Create a system tray for testing."""
    tray = SystemTray()
    yield tray
    tray.stop()

@pytest.fixture
def settings_dialog(root):
    """Create a settings dialog for testing."""
    dialog = SettingsDialog(root)
    yield dialog

@pytest.fixture
def call_controls(root):
    """Create call controls for testing."""
    controls = CallControls(root)
    yield controls

def test_main_window_initialization(main_window):
    """Test that the main window initializes correctly."""
    assert isinstance(main_window.root, CTk)
    assert main_window.title() == "AI Conversation Assistant"
    assert hasattr(main_window, 'call_controls')
    assert hasattr(main_window, 'settings_button')

def test_system_tray_initialization(system_tray):
    """Test that the system tray initializes correctly."""
    assert system_tray.icon is not None
    assert len(system_tray.menu_items) > 0
    assert "Settings" in [item.text for item in system_tray.menu_items]
    assert "Exit" in [item.text for item in system_tray.menu_items]

def test_settings_dialog(settings_dialog):
    """Test the settings dialog."""
    assert isinstance(settings_dialog, tk.Toplevel)
    assert settings_dialog.title() == "Settings"
    
    # Test API key settings
    assert hasattr(settings_dialog, 'cohere_api_key_entry')
    assert hasattr(settings_dialog, 'openai_api_key_entry')
    assert hasattr(settings_dialog, 'anthropic_api_key_entry')
    
    # Test audio settings
    assert hasattr(settings_dialog, 'input_device_combobox')
    assert hasattr(settings_dialog, 'output_device_combobox')
    
    # Test privacy settings
    assert hasattr(settings_dialog, 'data_retention_spinbox')
    assert hasattr(settings_dialog, 'local_processing_checkbox')

def test_call_controls(call_controls):
    """Test the call controls."""
    assert isinstance(call_controls, tk.Frame)
    
    # Test control buttons
    assert hasattr(call_controls, 'start_button')
    assert hasattr(call_controls, 'stop_button')
    assert hasattr(call_controls, 'mute_button')
    
    # Test status indicators
    assert hasattr(call_controls, 'status_label')
    assert hasattr(call_controls, 'timer_label')

def test_main_window_keyboard_shortcuts(main_window):
    """Test keyboard shortcuts."""
    # Create a mock event
    event = type('Event', (), {'char': 'm', 'keysym': 'M'})()
    
    # Test mute shortcut
    main_window.handle_keyboard_shortcut(event)
    assert main_window.call_controls.is_muted
    
    # Test unmute shortcut
    main_window.handle_keyboard_shortcut(event)
    assert not main_window.call_controls.is_muted

def test_system_tray_menu_actions(system_tray, root):
    """Test system tray menu actions."""
    # Test show/hide window
    system_tray.toggle_window(None)
    assert root.winfo_viewable()
    
    system_tray.toggle_window(None)
    assert not root.winfo_viewable()
    
    # Test settings dialog
    system_tray.show_settings(None)
    assert any(isinstance(w, SettingsDialog) for w in root.winfo_children())

def test_settings_save(settings_dialog):
    """Test saving settings."""
    # Set some test values
    settings_dialog.cohere_api_key_entry.insert(0, "test-key")
    settings_dialog.local_processing_checkbox.select()
    settings_dialog.data_retention_spinbox.set(30)
    
    # Save settings
    settings_dialog.save_settings()
    
    # Verify settings were saved
    assert settings_dialog.settings.get("cohere_api_key") == "test-key"
    assert settings_dialog.settings.get("local_processing")
    assert settings_dialog.settings.get("data_retention_days") == 30

def test_call_controls_state_management(call_controls):
    """Test call controls state management."""
    # Test start call
    call_controls.start_button.invoke()
    assert call_controls.is_active
    assert call_controls.start_button.cget("state") == "disabled"
    assert call_controls.stop_button.cget("state") == "normal"
    
    # Test stop call
    call_controls.stop_button.invoke()
    assert not call_controls.is_active
    assert call_controls.start_button.cget("state") == "normal"
    assert call_controls.stop_button.cget("state") == "disabled"
    
    # Test mute/unmute
    call_controls.mute_button.invoke()
    assert call_controls.is_muted
    assert "Unmute" in call_controls.mute_button.cget("text")
    
    call_controls.mute_button.invoke()
    assert not call_controls.is_muted
    assert "Mute" in call_controls.mute_button.cget("text")
