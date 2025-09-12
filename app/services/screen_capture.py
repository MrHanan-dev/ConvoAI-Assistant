"""
Screen Capture Service for Real-time Screen Analysis
"""
import asyncio
import base64
import io
import time
from typing import Optional, Dict, Any, List
import cv2
import numpy as np
from PIL import Image
import mss
from loguru import logger


class ScreenCaptureService:
    """Real-time screen capture and analysis service"""
    
    def __init__(self):
        self.is_capturing = False
        self.capture_interval = 0.5  # Capture every 500ms
        self.sct = None
        self.current_screen = None
        self.screen_analysis = {}
        self.last_capture_time = 0
        
    async def initialize(self):
        """Initialize screen capture service"""
        try:
            self.sct = mss.mss()
            logger.info("✅ Screen Capture Service initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize Screen Capture Service: {e}")
            return False
    
    async def start_capture(self, interval: float = 0.5):
        """Start real-time screen capture"""
        if self.is_capturing:
            logger.warning("⚠️ Screen capture already running")
            return
        
        self.capture_interval = interval
        self.is_capturing = True
        logger.info(f"🎥 Starting screen capture (interval: {interval}s)")
        
        # Start capture loop
        asyncio.create_task(self._capture_loop())
    
    async def stop_capture(self):
        """Stop screen capture"""
        self.is_capturing = False
        logger.info("🛑 Screen capture stopped")
    
    async def _capture_loop(self):
        """Main capture loop"""
        while self.is_capturing:
            try:
                await self._capture_screen()
                await asyncio.sleep(self.capture_interval)
            except Exception as e:
                logger.error(f"❌ Error in capture loop: {e}")
                await asyncio.sleep(1)
    
    async def _capture_screen(self):
        """Capture current screen"""
        try:
            # Capture screen using mss
            screenshot = self.sct.grab(self.sct.monitors[1])  # Primary monitor
            
            # Convert to PIL Image
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            
            # Convert to numpy array for OpenCV
            img_array = np.array(img)
            
            # Store current screen
            self.current_screen = img_array
            self.last_capture_time = time.time()
            
            # Analyze screen content
            await self._analyze_screen(img_array)
            
        except Exception as e:
            logger.error(f"❌ Error capturing screen: {e}")
    
    async def _analyze_screen(self, img_array: np.ndarray):
        """Analyze screen content using computer vision"""
        try:
            analysis = {
                'timestamp': time.time(),
                'resolution': img_array.shape[:2],
                'dominant_colors': await self._get_dominant_colors(img_array),
                'text_regions': await self._detect_text_regions(img_array),
                'ui_elements': await self._detect_ui_elements(img_array),
                'activity_level': await self._calculate_activity_level(img_array)
            }
            
            self.screen_analysis = analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing screen: {e}")
    
    async def _get_dominant_colors(self, img_array: np.ndarray) -> List[tuple]:
        """Extract dominant colors from screen"""
        try:
            # Resize image for faster processing
            small_img = cv2.resize(img_array, (150, 150))
            
            # Reshape image to be a list of pixels
            pixels = small_img.reshape(-1, 3)
            
            # Convert to float and normalize
            pixels = np.float32(pixels)
            
            # Define criteria and apply kmeans
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            k = 5  # Number of dominant colors
            
            _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Convert back to uint8
            centers = np.uint8(centers)
            
            # Get color counts
            unique, counts = np.unique(labels, return_counts=True)
            
            # Sort by frequency
            color_freq = list(zip(centers[unique], counts))
            color_freq.sort(key=lambda x: x[1], reverse=True)
            
            return [tuple(int(c) for c in color) for color, _ in color_freq[:3]]
            
        except Exception as e:
            logger.error(f"❌ Error getting dominant colors: {e}")
            return []
    
    async def _detect_text_regions(self, img_array: np.ndarray) -> List[Dict]:
        """Detect text regions on screen"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Apply threshold to get binary image
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            text_regions = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter by size (likely text regions)
                if w > 50 and h > 10 and w < 500 and h < 100:
                    text_regions.append({
                        'x': int(x),
                        'y': int(y),
                        'width': int(w),
                        'height': int(h),
                        'area': int(w * h)
                    })
            
            return text_regions[:10]  # Return top 10 text regions
            
        except Exception as e:
            logger.error(f"❌ Error detecting text regions: {e}")
            return []
    
    async def _detect_ui_elements(self, img_array: np.ndarray) -> List[Dict]:
        """Detect UI elements like buttons, windows, etc."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            ui_elements = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                area = cv2.contourArea(contour)
                
                # Filter by size and aspect ratio
                if area > 1000 and w > 30 and h > 30:
                    aspect_ratio = w / h
                    
                    # Classify UI element type based on aspect ratio and size
                    element_type = "unknown"
                    if 0.8 <= aspect_ratio <= 1.2 and 30 <= w <= 100:
                        element_type = "button"
                    elif aspect_ratio > 2 and h > 50:
                        element_type = "window"
                    elif aspect_ratio < 0.5 and w > 50:
                        element_type = "sidebar"
                    
                    ui_elements.append({
                        'type': element_type,
                        'x': int(x),
                        'y': int(y),
                        'width': int(w),
                        'height': int(h),
                        'area': int(area)
                    })
            
            return ui_elements[:15]  # Return top 15 UI elements
            
        except Exception as e:
            logger.error(f"❌ Error detecting UI elements: {e}")
            return []
    
    async def _calculate_activity_level(self, img_array: np.ndarray) -> float:
        """Calculate screen activity level (0-1)"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Calculate standard deviation (higher = more activity)
            activity = np.std(gray) / 255.0
            
            return float(activity)
            
        except Exception as e:
            logger.error(f"❌ Error calculating activity level: {e}")
            return 0.0
    
    def get_screen_image_base64(self) -> Optional[str]:
        """Get current screen as base64 encoded image"""
        if self.current_screen is None:
            return None
        
        try:
            # Convert numpy array to PIL Image
            img = Image.fromarray(self.current_screen)
            
            # Resize for efficiency (max 800px width)
            width, height = img.size
            if width > 800:
                ratio = 800 / width
                new_height = int(height * ratio)
                img = img.resize((800, new_height), Image.Resampling.LANCZOS)
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/jpeg;base64,{img_str}"
            
        except Exception as e:
            logger.error(f"❌ Error encoding screen image: {e}")
            return None
    
    def get_screen_analysis(self) -> Dict[str, Any]:
        """Get current screen analysis"""
        return self.screen_analysis.copy() if self.screen_analysis else {}
    
    def get_screen_summary(self) -> str:
        """Get a text summary of current screen"""
        if not self.screen_analysis:
            return "No screen analysis available"
        
        analysis = self.screen_analysis
        
        summary_parts = []
        
        # Resolution
        height, width = analysis.get('resolution', (0, 0))
        summary_parts.append(f"Screen resolution: {width}x{height}")
        
        # Activity level
        activity = analysis.get('activity_level', 0)
        if activity > 0.7:
            activity_desc = "high activity"
        elif activity > 0.4:
            activity_desc = "moderate activity"
        else:
            activity_desc = "low activity"
        summary_parts.append(f"Activity level: {activity_desc}")
        
        # UI elements
        ui_elements = analysis.get('ui_elements', [])
        if ui_elements:
            element_types = [elem['type'] for elem in ui_elements]
            type_counts = {}
            for elem_type in element_types:
                type_counts[elem_type] = type_counts.get(elem_type, 0) + 1
            
            element_summary = ", ".join([f"{count} {type}" for type, count in type_counts.items()])
            summary_parts.append(f"UI elements detected: {element_summary}")
        
        # Text regions
        text_regions = analysis.get('text_regions', [])
        if text_regions:
            summary_parts.append(f"Text regions: {len(text_regions)} detected")
        
        return ". ".join(summary_parts) + "."
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.stop_capture()
        if self.sct:
            self.sct.close()
        logger.info("✅ Screen Capture Service cleaned up")
