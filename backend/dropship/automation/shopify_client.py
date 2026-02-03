"""Shopify Integration (requires API credentials)"""
import aiohttp
from datetime import datetime
from typing import Dict, Any, List, Optional
from ..config import shopify as shopify_config

class ShopifyClient:
    """Client for Shopify Admin API"""
    
    def __init__(self):
        self.config = shopify_config
        self.base_url = self.config.admin_url
        self.headers = {
            'Content-Type': 'application/json',
            'X-Shopify-Access-Token': self.config.access_token or ''
        }
        
    @property
    def is_configured(self) -> bool:
        return self.config.is_configured
    
    def _get_status(self) -> Dict[str, Any]:
        """Get connection status"""
        return {
            'configured': self.is_configured,
            'store_url': self.config.store_url,
            'api_version': self.config.api_version,
            'message': 'Ready' if self.is_configured else 'Shopify API credentials required'
        }
    
    async def _request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make API request to Shopify"""
        if not self.is_configured:
            return {'error': 'Shopify not configured', 'needs': ['SHOPIFY_ACCESS_TOKEN']}
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, headers=self.headers, json=data) as resp:
                    result = await resp.json()
                    if resp.status >= 400:
                        return {'error': result, 'status': resp.status}
                    return result
        except Exception as e:
            return {'error': str(e)}
    
    # Products
    async def get_products(self, limit: int = 50) -> Dict[str, Any]:
        """Get all products"""
        return await self._request('GET', f'products.json?limit={limit}')
    
    async def get_product(self, product_id: str) -> Dict[str, Any]:
        """Get single product"""
        return await self._request('GET', f'products/{product_id}.json')
    
    async def update_product(self, product_id: str, data: Dict) -> Dict[str, Any]:
        """Update product"""
        return await self._request('PUT', f'products/{product_id}.json', {'product': data})
    
    async def update_price(self, variant_id: str, new_price: float) -> Dict[str, Any]:
        """Update product variant price"""
        return await self._request('PUT', f'variants/{variant_id}.json', {
            'variant': {'price': str(new_price)}
        })
    
    # Inventory
    async def get_inventory_levels(self) -> Dict[str, Any]:
        """Get inventory levels"""
        return await self._request('GET', 'inventory_levels.json')
    
    async def adjust_inventory(self, inventory_item_id: str, adjustment: int) -> Dict[str, Any]:
        """Adjust inventory level"""
        return await self._request('POST', 'inventory_levels/adjust.json', {
            'inventory_item_id': inventory_item_id,
            'available_adjustment': adjustment
        })
    
    # Orders
    async def get_orders(self, status: str = 'any', limit: int = 50) -> Dict[str, Any]:
        """Get orders"""
        return await self._request('GET', f'orders.json?status={status}&limit={limit}')
    
    async def get_order(self, order_id: str) -> Dict[str, Any]:
        """Get single order"""
        return await self._request('GET', f'orders/{order_id}.json')
    
    async def fulfill_order(self, order_id: str, tracking: Dict = None) -> Dict[str, Any]:
        """Create fulfillment for order"""
        fulfillment_data = {'notify_customer': True}
        if tracking:
            fulfillment_data['tracking_info'] = tracking
        return await self._request('POST', f'orders/{order_id}/fulfillments.json', {
            'fulfillment': fulfillment_data
        })
    
    # Customers
    async def get_customers(self, limit: int = 50) -> Dict[str, Any]:
        """Get customers"""
        return await self._request('GET', f'customers.json?limit={limit}')
    
    async def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """Get single customer"""
        return await self._request('GET', f'customers/{customer_id}.json')
    
    # Analytics
    async def get_shop_info(self) -> Dict[str, Any]:
        """Get shop information"""
        return await self._request('GET', 'shop.json')
