"""Configuration for Dropshipping Automation System"""
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class ShopifyConfig:
    store_url: str = os.getenv('SHOPIFY_STORE_URL', 'xeria-378.myshopify.com')
    access_token: Optional[str] = os.getenv('SHOPIFY_ACCESS_TOKEN')
    api_key: Optional[str] = os.getenv('SHOPIFY_API_KEY')
    api_secret: Optional[str] = os.getenv('SHOPIFY_API_SECRET')
    api_version: str = '2024-01'
    
    @property
    def is_configured(self) -> bool:
        return bool(self.access_token)
    
    @property
    def admin_url(self) -> str:
        return f"https://{self.store_url}/admin/api/{self.api_version}"

@dataclass
class StoreConfig:
    name: str = 'XeriaCo'
    shopify_url: str = 'xeria-378.myshopify.com'
    frontend_url: str = 'xeriacofinal.vercel.app'
    currency: str = 'USD'
    
@dataclass
class AlertConfig:
    low_stock_threshold: int = 10
    price_change_threshold: float = 0.05  # 5%
    conversion_drop_threshold: float = 0.10  # 10%
    
@dataclass
class AutomationConfig:
    enable_auto_pricing: bool = True
    enable_auto_restock: bool = True
    enable_competitor_monitoring: bool = True
    price_update_interval_hours: int = 6
    competitor_check_interval_hours: int = 12

# Global configs
shopify = ShopifyConfig()
store = StoreConfig()
alerts = AlertConfig()
automation = AutomationConfig()
