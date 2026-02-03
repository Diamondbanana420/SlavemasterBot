"""Inventory Management Automation"""
from datetime import datetime
from typing import Dict, Any, List
from ..config import alerts as alert_config

class InventoryManager:
    """Automated inventory management"""
    
    def __init__(self, shopify_client, db=None):
        self.shopify = shopify_client
        self.db = db
        self.suppliers = []
        
    def add_supplier(self, supplier: Dict):
        """Add supplier configuration"""
        self.suppliers.append({
            **supplier,
            'added_at': datetime.utcnow().isoformat()
        })
    
    def check_stock_levels(self, products: List[Dict]) -> Dict[str, Any]:
        """Check stock levels and generate alerts"""
        low_stock = []
        out_of_stock = []
        healthy = []
        
        for product in products:
            qty = product.get('inventory_qty', 0)
            
            if qty == 0:
                out_of_stock.append({
                    'product': product.get('title'),
                    'sku': product.get('sku'),
                    'quantity': qty,
                    'severity': 'critical'
                })
            elif qty < alert_config.low_stock_threshold:
                low_stock.append({
                    'product': product.get('title'),
                    'sku': product.get('sku'),
                    'quantity': qty,
                    'threshold': alert_config.low_stock_threshold,
                    'severity': 'warning'
                })
            else:
                healthy.append({
                    'product': product.get('title'),
                    'sku': product.get('sku'),
                    'quantity': qty
                })
        
        return {
            'total_products': len(products),
            'out_of_stock': len(out_of_stock),
            'low_stock': len(low_stock),
            'healthy': len(healthy),
            'out_of_stock_products': out_of_stock,
            'low_stock_products': low_stock,
            'checked_at': datetime.utcnow().isoformat()
        }
    
    def calculate_reorder_quantities(self, products: List[Dict], 
                                      avg_daily_sales: Dict[str, float] = None) -> List[Dict]:
        """Calculate reorder quantities based on sales velocity"""
        reorders = []
        avg_daily_sales = avg_daily_sales or {}
        
        for product in products:
            sku = product.get('sku', '')
            current_qty = product.get('inventory_qty', 0)
            daily_sales = avg_daily_sales.get(sku, 1)  # Default 1/day
            lead_time_days = product.get('lead_time_days', 14)  # Default 2 weeks
            
            # Safety stock = 7 days of sales
            safety_stock = daily_sales * 7
            
            # Reorder point = (lead time * daily sales) + safety stock
            reorder_point = (lead_time_days * daily_sales) + safety_stock
            
            # Reorder quantity = 30 days of stock
            reorder_qty = max(0, int((daily_sales * 30) - current_qty + safety_stock))
            
            if current_qty <= reorder_point:
                reorders.append({
                    'product': product.get('title'),
                    'sku': sku,
                    'current_qty': current_qty,
                    'reorder_point': int(reorder_point),
                    'recommended_order_qty': reorder_qty,
                    'supplier': product.get('supplier'),
                    'estimated_cost': reorder_qty * product.get('cost', 0),
                    'urgency': 'critical' if current_qty == 0 else 'normal'
                })
        
        return reorders
    
    async def sync_with_supplier(self, supplier_id: str) -> Dict[str, Any]:
        """Sync inventory with supplier (placeholder for supplier API)"""
        return {
            'supplier_id': supplier_id,
            'status': 'pending_supplier_integration',
            'message': 'Supplier API integration required',
            'checked_at': datetime.utcnow().isoformat()
        }
