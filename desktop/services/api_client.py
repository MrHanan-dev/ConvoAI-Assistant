"""
API client for desktop application
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional
from loguru import logger


class APIClient:
    """API client for communicating with backend"""
    
    def __init__(self, base_url: str, api_key: str = ""):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = None
    
    async def _get_session(self):
        """Get or create HTTP session"""
        if not self.session:
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self.session
    
    async def test_connection(self) -> bool:
        """Test connection to API server"""
        try:
            session = await self._get_session()
            async with session.get(f'{self.base_url}/health') as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('status') == 'healthy'
                return False
                
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    async def start_conversation(self, data: Dict[str, Any]) -> str:
        """Start a new conversation"""
        try:
            session = await self._get_session()
            async with session.post(f'{self.base_url}/api/conversations/', json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('id')
                else:
                    logger.error(f"Failed to start conversation: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error starting conversation: {e}")
            return None
    
    async def end_conversation(self, conversation_id: str, data: Dict[str, Any]) -> bool:
        """End a conversation"""
        try:
            session = await self._get_session()
            async with session.put(f'{self.base_url}/api/conversations/{conversation_id}', json=data) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"Error ending conversation: {e}")
            return False
    
    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation data"""
        try:
            session = await self._get_session()
            async with session.get(f'{self.base_url}/api/conversations/{conversation_id}') as response:
                if response.status == 200:
                    return await response.json()
                return None
                
        except Exception as e:
            logger.error(f"Error getting conversation: {e}")
            return None
    
    async def upload_document(self, file_path: str, metadata: Dict[str, Any] = None) -> bool:
        """Upload document for processing"""
        try:
            session = await self._get_session()
            
            with open(file_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('file', f, filename=file_path)
                if metadata:
                    data.add_field('metadata', str(metadata))
                
                async with session.post(f'{self.base_url}/api/documents/', data=data) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            return False
    
    async def get_analytics(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation analytics"""
        try:
            session = await self._get_session()
            async with session.get(f'{self.base_url}/api/analytics/conversations/{conversation_id}') as response:
                if response.status == 200:
                    return await response.json()
                return None
                
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return None
    
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
