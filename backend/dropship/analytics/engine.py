"""Analytics Engine for Dropshipping Store"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import random

class AnalyticsEngine:
    """Calculate and track store analytics"""
    
    def __init__(self, db=None):
        self.db = db
        self._cache = {}
        
    async def get_daily_metrics(self, date: str = None) -> Dict[str, Any]:
        """Get metrics for a specific date"""
        if date is None:
            date = datetime.utcnow().strftime('%Y-%m-%d')
        
        # Try to get from DB, otherwise return placeholder
        if self.db:
            metrics = await self.db.daily_metrics.find_one({'date': date})
            if metrics:
                return metrics
        
        # Return structure (will be populated when Shopify connected)
        return {
            'date': date,
            'revenue': 0,
            'orders': 0,
            'visitors': 0,
            'conversion_rate': 0,
            'avg_order_value': 0,
            'cart_abandonment_rate': 0,
            'profit': 0,
            'ad_spend': 0,
            'roas': 0,
            'data_source': 'pending_shopify_connection'
        }
    
    async def get_metrics_range(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get metrics for date range"""
        metrics = []
        for i in range(days):
            date = (datetime.utcnow() - timedelta(days=i)).strftime('%Y-%m-%d')
            daily = await self.get_daily_metrics(date)
            metrics.append(daily)
        return metrics
    
    def calculate_kpis(self, metrics: List[Dict]) -> Dict[str, Any]:
        """Calculate KPIs from metrics"""
        if not metrics:
            return {'error': 'No metrics available'}
        
        total_revenue = sum(m.get('revenue', 0) for m in metrics)
        total_orders = sum(m.get('orders', 0) for m in metrics)
        total_visitors = sum(m.get('visitors', 0) for m in metrics)
        total_profit = sum(m.get('profit', 0) for m in metrics)
        total_ad_spend = sum(m.get('ad_spend', 0) for m in metrics)
        
        return {
            'period_days': len(metrics),
            'total_revenue': round(total_revenue, 2),
            'total_orders': total_orders,
            'total_visitors': total_visitors,
            'total_profit': round(total_profit, 2),
            'total_ad_spend': round(total_ad_spend, 2),
            'avg_order_value': round(total_revenue / total_orders, 2) if total_orders > 0 else 0,
            'conversion_rate': round((total_orders / total_visitors) * 100, 2) if total_visitors > 0 else 0,
            'profit_margin': round((total_profit / total_revenue) * 100, 2) if total_revenue > 0 else 0,
            'roas': round(total_revenue / total_ad_spend, 2) if total_ad_spend > 0 else 0,
            'cac': round(total_ad_spend / total_orders, 2) if total_orders > 0 else 0,
            'calculated_at': datetime.utcnow().isoformat()
        }
    
    def calculate_profit_margin(self, product: Dict) -> Dict[str, Any]:
        """Calculate detailed profit margin for a product"""
        price = product.get('price', 0)
        cost = product.get('cost', 0)
        
        # Estimated fees
        payment_fee = price * 0.029 + 0.30  # Stripe/PayPal ~2.9% + $0.30
        shopify_fee = price * 0.02  # Shopify payments
        shipping_cost = product.get('shipping_cost', 5)  # Default $5
        ad_cost_per_sale = product.get('ad_cost_per_sale', 10)  # Default $10 CPA
        
        total_cost = cost + payment_fee + shopify_fee + shipping_cost + ad_cost_per_sale
        profit = price - total_cost
        margin = (profit / price) * 100 if price > 0 else 0
        
        return {
            'product': product.get('title', 'Unknown'),
            'price': round(price, 2),
            'product_cost': round(cost, 2),
            'payment_fees': round(payment_fee, 2),
            'platform_fees': round(shopify_fee, 2),
            'shipping_cost': round(shipping_cost, 2),
            'ad_cost_per_sale': round(ad_cost_per_sale, 2),
            'total_cost': round(total_cost, 2),
            'net_profit': round(profit, 2),
            'profit_margin_percent': round(margin, 1),
            'break_even_price': round(total_cost, 2),
            'recommended_min_price': round(total_cost * 1.3, 2),  # 30% margin
        }
    
    def analyze_funnel(self, funnel_data: Dict) -> Dict[str, Any]:
        """Analyze conversion funnel and identify drop-off points"""
        stages = [
            ('visitors', 'Visitors'),
            ('product_views', 'Product Views'),
            ('add_to_cart', 'Add to Cart'),
            ('checkout_started', 'Checkout Started'),
            ('payment_entered', 'Payment Entered'),
            ('orders', 'Orders Completed')
        ]
        
        analysis = []
        prev_count = None
        
        for key, label in stages:
            count = funnel_data.get(key, 0)
            if prev_count is not None and prev_count > 0:
                drop_off = ((prev_count - count) / prev_count) * 100
                conversion = (count / prev_count) * 100
            else:
                drop_off = 0
                conversion = 100
            
            stage_analysis = {
                'stage': label,
                'count': count,
                'drop_off_percent': round(drop_off, 1),
                'conversion_to_next': round(conversion, 1)
            }
            
            # Add recommendations for high drop-off
            if drop_off > 50:
                stage_analysis['severity'] = 'critical'
                stage_analysis['recommendation'] = self._get_funnel_recommendation(key, drop_off)
            elif drop_off > 30:
                stage_analysis['severity'] = 'warning'
                stage_analysis['recommendation'] = self._get_funnel_recommendation(key, drop_off)
            else:
                stage_analysis['severity'] = 'ok'
            
            analysis.append(stage_analysis)
            prev_count = count
        
        overall_conversion = (funnel_data.get('orders', 0) / funnel_data.get('visitors', 1)) * 100
        
        return {
            'funnel_analysis': analysis,
            'overall_conversion': round(overall_conversion, 2),
            'biggest_drop_off': max(analysis, key=lambda x: x['drop_off_percent']),
            'analyzed_at': datetime.utcnow().isoformat()
        }
    
    def _get_funnel_recommendation(self, stage: str, drop_off: float) -> str:
        recommendations = {
            'product_views': 'Improve homepage CTAs, add featured products, optimize site navigation',
            'add_to_cart': 'Add trust badges, improve product images, show reviews, add urgency elements',
            'checkout_started': 'Simplify add-to-cart flow, show cart summary, offer guest checkout',
            'payment_entered': 'Reduce checkout fields, add progress indicator, show security badges',
            'orders': 'Add more payment options, show clear shipping costs, offer guarantees'
        }
        return recommendations.get(stage, 'Review user experience at this stage')
