#!/usr/bin/env python3
"""
Test Screen Capture Functionality
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def test_screen_capture():
    """Test screen capture service"""
    try:
        from app.services.screen_capture import ScreenCaptureService
        
        print("✅ Screen capture service imported successfully")
        
        # Initialize service
        screen_capture = ScreenCaptureService()
        success = await screen_capture.initialize()
        
        if success:
            print("✅ Screen capture service initialized successfully")
            
            # Test screen capture
            await screen_capture.start_capture(interval=1.0)
            print("✅ Screen capture started")
            
            # Wait a bit for capture
            await asyncio.sleep(3)
            
            # Get analysis
            analysis = screen_capture.get_screen_analysis()
            summary = screen_capture.get_screen_summary()
            
            print(f"✅ Screen analysis: {summary}")
            print(f"✅ Analysis data: {analysis}")
            
            # Get image
            image_base64 = screen_capture.get_screen_image_base64()
            if image_base64:
                print("✅ Screen image captured successfully")
            else:
                print("❌ Failed to capture screen image")
            
            # Stop capture
            await screen_capture.stop_capture()
            print("✅ Screen capture stopped")
            
            # Cleanup
            await screen_capture.cleanup()
            print("✅ Screen capture service cleaned up")
            
        else:
            print("❌ Failed to initialize screen capture service")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_screen_capture())
