"""Alert System for Dropshipping Automation"""
from datetime import datetime
from typing import Dict, Any, List, Callable
import asyncio

class AlertManager:
    """Manage and dispatch alerts"""
    
    def __init__(self, db=None):
        self.db = db
        self.alerts: List[Dict] = []
        self.handlers: Dict[str, List[Callable]] = {}
        
    def create_alert(self, alert_type: str, severity: str, title: str, 
                     message: str, data: Dict = None) -> Dict[str, Any]:
        """Create a new alert"""
        alert = {
            'id': f"alert_{datetime.utcnow().timestamp()}",
            'type': alert_type,
            'severity': severity,
            'title': title,
            'message': message,
            'data': data or {},
            'acknowledged': False,
            'created_at': datetime.utcnow().isoformat()
        }
        self.alerts.append(alert)
        
        # Dispatch to handlers
        asyncio.create_task(self._dispatch_alert(alert))
        
        return alert
    
    def register_handler(self, alert_type: str, handler: Callable):
        """Register alert handler"""
        if alert_type not in self.handlers:
            self.handlers[alert_type] = []
        self.handlers[alert_type].append(handler)
    
    async def _dispatch_alert(self, alert: Dict):
        """Dispatch alert to registered handlers"""
        handlers = self.handlers.get(alert['type'], []) + self.handlers.get('*', [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert)
                else:
                    handler(alert)
            except Exception as e:
                print(f"Alert handler error: {e}")
    
    def get_alerts(self, unacknowledged_only: bool = False, 
                   severity: str = None, limit: int = 50) -> List[Dict]:
        """Get alerts with filters"""
        filtered = self.alerts
        
        if unacknowledged_only:
            filtered = [a for a in filtered if not a['acknowledged']]
        if severity:
            filtered = [a for a in filtered if a['severity'] == severity]
        
        return sorted(filtered, key=lambda x: x['created_at'], reverse=True)[:limit]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['acknowledged'] = True
                alert['acknowledged_at'] = datetime.utcnow().isoformat()
                return True
        return False
    
    # Convenience methods for common alerts
    def low_stock_alert(self, product: str, sku: str, quantity: int):
        return self.create_alert(
            'low_stock', 
            'warning' if quantity > 0 else 'critical',
            f"Low Stock: {product}",
            f"SKU {sku} has only {quantity} units remaining",
            {'product': product, 'sku': sku, 'quantity': quantity}
        )
    
    def price_change_alert(self, product: str, old_price: float, new_price: float, competitor: str):
        return self.create_alert(
            'price_change',
            'info',
            f"Competitor Price Change: {product}",
            f"{competitor} changed price from ${old_price:.2f} to ${new_price:.2f}",
            {'product': product, 'old_price': old_price, 'new_price': new_price, 'competitor': competitor}
        )
    
    def conversion_drop_alert(self, current_rate: float, previous_rate: float):
        drop = ((previous_rate - current_rate) / previous_rate) * 100
        return self.create_alert(
            'conversion_drop',
            'critical' if drop > 30 else 'warning',
            "Conversion Rate Drop Detected",
            f"Conversion dropped from {previous_rate:.2f}% to {current_rate:.2f}% ({drop:.1f}% decrease)",
            {'current_rate': current_rate, 'previous_rate': previous_rate, 'drop_percent': drop}
        )
    
    def order_alert(self, order_id: str, total: float, status: str):
        return self.create_alert(
            'new_order',
            'info',
            f"New Order: #{order_id}",
            f"Order total: ${total:.2f} - Status: {status}",
            {'order_id': order_id, 'total': total, 'status': status}
        )
