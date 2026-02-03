"""Main Dropshipping Automation System"""
from datetime import datetime
from typing import Dict, Any, Optional
import asyncio

from .config import shopify, store, alerts, automation
from .monitors import SiteMonitor, CompetitorMonitor
from .analytics import AnalyticsEngine, ReportGenerator
from .automation import ShopifyClient, PricingEngine, InventoryManager, FulfillmentEngine
from .utils import AlertManager, TaskScheduler

class DropshipSystem:
    """Main dropshipping automation system"""
    
    def __init__(self, db=None):
        self.db = db
        self.initialized = False
        
        # Initialize components
        self.shopify = ShopifyClient()
        self.site_monitor = SiteMonitor(store.shopify_url, store.frontend_url)
        self.competitor_monitor = CompetitorMonitor()
        self.analytics = AnalyticsEngine(db)
        self.reports = ReportGenerator(self.analytics, db)
        self.pricing = PricingEngine(self.shopify, self.competitor_monitor, db)
        self.inventory = InventoryManager(self.shopify, db)
        self.fulfillment = FulfillmentEngine(self.shopify, db)
        self.alerts = AlertManager(db)
        self.scheduler = TaskScheduler()
        
    async def initialize(self):
        """Initialize the system and schedule tasks"""
        # Schedule automated tasks
        self.scheduler.schedule_task(
            'site_audit',
            self.site_monitor.full_audit,
            interval_hours=24,
            run_immediately=True
        )
        
        self.scheduler.schedule_task(
            'competitor_check',
            self.competitor_monitor.check_all_competitors,
            interval_hours=automation.competitor_check_interval_hours
        )
        
        self.scheduler.schedule_task(
            'daily_report',
            self.reports.generate_daily_report,
            interval_hours=24
        )
        
        self.initialized = True
        return {'status': 'initialized', 'timestamp': datetime.utcnow().isoformat()}
    
    def start_automation(self):
        """Start automated tasks"""
        self.scheduler.start()
        return {'status': 'automation_started'}
    
    def stop_automation(self):
        """Stop automated tasks"""
        self.scheduler.stop()
        return {'status': 'automation_stopped'}
    
    def get_status(self) -> Dict[str, Any]:
        """Get full system status"""
        return {
            'system': 'XeriaCo Dropship Automation',
            'version': '1.0.0',
            'initialized': self.initialized,
            'store': {
                'name': store.name,
                'shopify_url': store.shopify_url,
                'frontend_url': store.frontend_url
            },
            'integrations': {
                'shopify': {
                    'configured': self.shopify.is_configured,
                    'status': 'ready' if self.shopify.is_configured else 'needs_api_credentials'
                }
            },
            'scheduler': self.scheduler.get_status(),
            'alerts': {
                'unacknowledged': len(self.alerts.get_alerts(unacknowledged_only=True))
            },
            'timestamp': datetime.utcnow().isoformat()
        }
    
    # Quick action methods
    async def run_site_audit(self) -> Dict[str, Any]:
        """Run a full site audit"""
        return await self.site_monitor.full_audit()
    
    async def check_competitors(self) -> Dict[str, Any]:
        """Check all competitors"""
        return await self.competitor_monitor.check_all_competitors()
    
    async def get_daily_report(self) -> Dict[str, Any]:
        """Get daily report"""
        return await self.reports.generate_daily_report()
    
    async def get_weekly_report(self) -> Dict[str, Any]:
        """Get weekly report"""
        return await self.reports.generate_weekly_report()
    
    async def analyze_pricing(self, products: list) -> Dict[str, Any]:
        """Analyze pricing for products"""
        return await self.pricing.analyze_all_products(products)
    
    def check_inventory(self, products: list) -> Dict[str, Any]:
        """Check inventory levels"""
        return self.inventory.check_stock_levels(products)
    
    def calculate_profit(self, product: dict) -> Dict[str, Any]:
        """Calculate profit margin for a product"""
        return self.analytics.calculate_profit_margin(product)
    
    def analyze_funnel(self, funnel_data: dict) -> Dict[str, Any]:
        """Analyze conversion funnel"""
        return self.analytics.analyze_funnel(funnel_data)


# Global instance
_system_instance: Optional[DropshipSystem] = None

def get_system(db=None) -> DropshipSystem:
    """Get or create the dropship system instance"""
    global _system_instance
    if _system_instance is None:
        _system_instance = DropshipSystem(db)
    return _system_instance
