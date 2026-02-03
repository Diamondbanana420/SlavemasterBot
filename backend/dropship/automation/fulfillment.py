"""Order Fulfillment Automation"""
from datetime import datetime
from typing import Dict, Any, List

class FulfillmentEngine:
    """Automated order fulfillment"""
    
    def __init__(self, shopify_client, db=None):
        self.shopify = shopify_client
        self.db = db
        self.supplier_mappings = {}  # SKU -> supplier info
        
    def add_supplier_mapping(self, sku: str, supplier_info: Dict):
        """Map SKU to supplier for auto-fulfillment"""
        self.supplier_mappings[sku] = supplier_info
    
    async def process_new_orders(self) -> Dict[str, Any]:
        """Process new unfulfilled orders"""
        if not self.shopify.is_configured:
            return {'error': 'Shopify not configured'}
        
        orders_response = await self.shopify.get_orders(status='open')
        
        if 'error' in orders_response:
            return orders_response
        
        orders = orders_response.get('orders', [])
        results = []
        
        for order in orders:
            if order.get('fulfillment_status') == 'fulfilled':
                continue
            
            order_result = {
                'order_id': order.get('id'),
                'order_number': order.get('order_number'),
                'customer': order.get('email'),
                'total': order.get('total_price'),
                'items': [],
                'status': 'pending'
            }
            
            for item in order.get('line_items', []):
                sku = item.get('sku', '')
                supplier = self.supplier_mappings.get(sku)
                
                order_result['items'].append({
                    'sku': sku,
                    'title': item.get('title'),
                    'quantity': item.get('quantity'),
                    'supplier': supplier.get('name') if supplier else 'Unknown',
                    'auto_fulfillable': bool(supplier)
                })
            
            results.append(order_result)
        
        return {
            'total_orders': len(results),
            'auto_fulfillable': len([o for o in results if all(i['auto_fulfillable'] for i in o['items'])]),
            'orders': results,
            'processed_at': datetime.utcnow().isoformat()
        }
    
    async def auto_fulfill_order(self, order_id: str, tracking: Dict = None) -> Dict[str, Any]:
        """Auto-fulfill an order (placeholder for supplier integration)"""
        return {
            'order_id': order_id,
            'status': 'pending_supplier_integration',
            'message': 'Supplier API required for auto-fulfillment',
            'tracking': tracking,
            'attempted_at': datetime.utcnow().isoformat()
        }
