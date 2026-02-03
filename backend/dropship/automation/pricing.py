"""Dynamic Pricing Automation"""
from datetime import datetime
from typing import Dict, Any, List, Optional
from ..config import automation as auto_config, alerts as alert_config

class PricingEngine:
    """Automated pricing optimization"""
    
    def __init__(self, shopify_client, competitor_monitor, db=None):
        self.shopify = shopify_client
        self.competitors = competitor_monitor
        self.db = db
        self.rules = []
        
    def add_pricing_rule(self, rule: Dict):
        """Add a pricing rule"""
        self.rules.append({
            **rule,
            'created_at': datetime.utcnow().isoformat()
        })
    
    def calculate_optimal_price(self, product: Dict, competitor_prices: List[float], 
                                 min_margin: float = 0.20) -> Dict[str, Any]:
        """Calculate optimal price based on competition and margins"""
        cost = product.get('cost', 0)
        current_price = product.get('price', 0)
        
        if not competitor_prices:
            return {
                'product': product.get('title'),
                'current_price': current_price,
                'recommended_price': current_price,
                'reason': 'No competitor data available'
            }
        
        avg_competitor = sum(competitor_prices) / len(competitor_prices)
        min_competitor = min(competitor_prices)
        max_competitor = max(competitor_prices)
        
        # Calculate minimum viable price (with margin)
        min_price = cost / (1 - min_margin) if cost > 0 else current_price * 0.7
        
        # Pricing strategy
        if current_price > max_competitor * 1.15:  # 15% above highest competitor
            recommended = max_competitor * 1.05  # Price 5% above highest
            reason = 'Price too high vs competition'
        elif current_price < min_competitor * 0.85:  # 15% below lowest
            recommended = min_competitor * 0.95  # Price 5% below lowest (aggressive)
            reason = 'Opportunity to increase price'
        elif current_price < min_price:
            recommended = min_price
            reason = 'Price below minimum margin'
        else:
            recommended = current_price
            reason = 'Price is competitive'
        
        # Ensure we maintain minimum margin
        recommended = max(recommended, min_price)
        
        return {
            'product': product.get('title'),
            'sku': product.get('sku'),
            'current_price': round(current_price, 2),
            'recommended_price': round(recommended, 2),
            'min_competitor_price': round(min_competitor, 2),
            'avg_competitor_price': round(avg_competitor, 2),
            'max_competitor_price': round(max_competitor, 2),
            'min_viable_price': round(min_price, 2),
            'price_change': round(recommended - current_price, 2),
            'price_change_percent': round(((recommended - current_price) / current_price) * 100, 1) if current_price > 0 else 0,
            'reason': reason,
            'calculated_at': datetime.utcnow().isoformat()
        }
    
    async def analyze_all_products(self, products: List[Dict]) -> Dict[str, Any]:
        """Analyze pricing for all products"""
        # Get competitor prices
        competitor_data = await self.competitors.check_all_competitors()
        
        all_competitor_prices = []
        for c in competitor_data:
            for p in c.get('products', []):
                if 'price' in p:
                    all_competitor_prices.append(p['price'])
        
        analysis = []
        for product in products:
            result = self.calculate_optimal_price(product, all_competitor_prices)
            analysis.append(result)
        
        # Summary
        price_increases = [a for a in analysis if a['price_change'] > 0]
        price_decreases = [a for a in analysis if a['price_change'] < 0]
        
        return {
            'total_products': len(products),
            'recommended_increases': len(price_increases),
            'recommended_decreases': len(price_decreases),
            'potential_revenue_change': sum(a['price_change'] for a in analysis),
            'analysis': analysis,
            'analyzed_at': datetime.utcnow().isoformat()
        }
    
    async def auto_update_prices(self, products: List[Dict], dry_run: bool = True) -> Dict[str, Any]:
        """Automatically update prices (use dry_run=False to apply)"""
        if not self.shopify.is_configured:
            return {'error': 'Shopify not configured for price updates'}
        
        analysis = await self.analyze_all_products(products)
        updates = []
        
        for item in analysis['analysis']:
            if abs(item['price_change_percent']) >= alert_config.price_change_threshold * 100:
                update = {
                    'product': item['product'],
                    'sku': item['sku'],
                    'old_price': item['current_price'],
                    'new_price': item['recommended_price'],
                    'change': item['price_change'],
                    'reason': item['reason']
                }
                
                if not dry_run:
                    # Actually update in Shopify
                    # result = await self.shopify.update_price(variant_id, item['recommended_price'])
                    update['status'] = 'pending_shopify_connection'
                else:
                    update['status'] = 'dry_run'
                
                updates.append(update)
        
        return {
            'mode': 'dry_run' if dry_run else 'live',
            'updates_recommended': len(updates),
            'updates': updates,
            'executed_at': datetime.utcnow().isoformat()
        }
