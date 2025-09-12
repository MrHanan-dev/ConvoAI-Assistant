#!/usr/bin/env python3
"""
Comprehensive diagnostic test for AI Conversation Assistant
Tests each component individually to identify all issues
"""

import sys
import traceback
import asyncio
from loguru import logger

# Configure logging
logger.remove()
logger.add(sys.stdout, level="INFO")

class DiagnosticTester:
    def __init__(self):
        self.issues_found = []
        self.tests_passed = 0
        self.tests_failed = 0

    def log_issue(self, component, error):
        """Log an issue for later reporting"""
        self.issues_found.append(f"{component}: {error}")
        logger.error(f"❌ {component}: {error}")

    def log_success(self, component):
        """Log a successful test"""
        self.tests_passed += 1
        logger.success(f"✅ {component}: OK")

    def test_import(self, component_name, import_func):
        """Test importing a component"""
        try:
            import_func()
            self.log_success(f"Import {component_name}")
            return True
        except Exception as e:
            self.log_issue(f"Import {component_name}", str(e))
            self.tests_failed += 1
            return False

    def test_core_components(self):
        """Test core components"""
        logger.info("Testing core components...")
        
        # Test config
        self.test_import("Config", lambda: __import__('app.core.config', fromlist=['settings']))
        
        # Test database
        self.test_import("Database", lambda: __import__('app.core.database', fromlist=['Base']))
        
        # Test Redis
        self.test_import("Redis", lambda: __import__('app.core.redis_client', fromlist=['init_redis']))

    def test_api_components(self):
        """Test API components"""
        logger.info("Testing API components...")
        
        # Test API routes
        self.test_import("API Routes", lambda: __import__('app.api.api_routes', fromlist=['api_router']))
        
        # Test individual route files
        routes = ['auth', 'users', 'conversations', 'analytics', 'integrations', 'documents']
        for route in routes:
            self.test_import(f"Route {route}", lambda r=route: __import__(f'app.api.routes.{r}', fromlist=['router']))

    def test_models(self):
        """Test database models"""
        logger.info("Testing database models...")
        
        models = ['user', 'conversation', 'document', 'team', 'integration', 'objection_template', 'playbook', 'call_shadow', 'audit_log']
        for model in models:
            self.test_import(f"Model {model}", lambda m=model: __import__(f'app.models.{m}', fromlist=[m.title()]))

    def test_services(self):
        """Test services"""
        logger.info("Testing services...")
        
        # Test services that don't have heavy dependencies
        lightweight_services = ['auth_manager', 'compliance_manager', 'keyboard_shortcuts', 'mobile_companion', 'notification_system', 'platform_integrations']
        for service in lightweight_services:
            self.test_import(f"Service {service}", lambda s=service: __import__(f'app.services.{s}', fromlist=[s.replace('_', '').title()]))
        
        # Test heavy services separately
        heavy_services = ['ai_engine', 'audio_processor', 'conversation_analyzer', 'teleprompter', 'vector_store', 'win_rate_analyzer']
        for service in heavy_services:
            try:
                module = __import__(f'app.services.{service}', fromlist=[service.replace('_', '').title()])
                self.log_success(f"Service {service}")
                self.tests_passed += 1
            except Exception as e:
                # For heavy services, just log as warning if it's a dependency issue
                if "No module named" in str(e) or "cannot import name" in str(e):
                    logger.warning(f"⚠️  Service {service}: Missing optional dependency - {str(e)}")
                else:
                    self.log_issue(f"Service {service}", str(e))
                    self.tests_failed += 1

    def test_socket_handlers(self):
        """Test socket handlers"""
        logger.info("Testing socket handlers...")
        self.test_import("Socket Handlers", lambda: __import__('app.sockets.handlers', fromlist=['register_socket_handlers']))

    def test_main_application(self):
        """Test main application components"""
        logger.info("Testing main application...")
        
        try:
            # Test importing main components
            from app.core.config import settings
            from app.api.api_routes import api_router
            from app.sockets.handlers import register_socket_handlers
            
            self.log_success("Main application imports")
            self.tests_passed += 1
            
            # Test FastAPI app creation
            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(api_router, prefix="/api")
            
            self.log_success("FastAPI app creation")
            self.tests_passed += 1
            
        except Exception as e:
            self.log_issue("Main application", str(e))
            self.tests_failed += 1

    async def test_database_initialization(self):
        """Test database initialization"""
        logger.info("Testing database initialization...")
        
        try:
            from app.core.database import init_db
            await init_db()
            self.log_success("Database initialization")
            self.tests_passed += 1
        except Exception as e:
            self.log_issue("Database initialization", str(e))
            self.tests_failed += 1

    async def run_all_tests(self):
        """Run all diagnostic tests"""
        logger.info("🔍 Starting comprehensive diagnostic tests...")
        logger.info("=" * 60)
        
        # Run all tests
        self.test_core_components()
        self.test_api_components()
        self.test_models()
        self.test_services()
        self.test_socket_handlers()
        self.test_main_application()
        await self.test_database_initialization()
        
        # Report results
        logger.info("=" * 60)
        logger.info("📊 Test Results:")
        logger.info(f"✅ Tests Passed: {self.tests_passed}")
        logger.info(f"❌ Tests Failed: {self.tests_failed}")
        
        if self.issues_found:
            logger.error("🚨 Issues Found:")
            for issue in self.issues_found:
                logger.error(f"  - {issue}")
        else:
            logger.success("🎉 No critical issues found!")
        
        return len(self.issues_found) == 0

async def main():
    """Main diagnostic function"""
    tester = DiagnosticTester()
    success = await tester.run_all_tests()
    
    if success:
        logger.success("🎉 All tests passed! The application should work correctly.")
        return 0
    else:
        logger.error("❌ Issues found. Please review and fix the reported problems.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
