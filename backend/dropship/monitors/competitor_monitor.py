"""Competitor Price & Product Monitor"""
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, Any, List, Optional
import re
from bs4 import BeautifulSoup

class CompetitorMonitor:
    def __init__(self):
        self.competitors: List[Dict[str, Any]] = []
        self.price_history: List[Dict[str, Any]] = []
        
    def add_competitor(self, name: str, url: str, selectors: Optional[Dict] = None):
        """Add a competitor to monitor"""
        self.competitors.append({
            'name': name,
            'url': url,
            'selectors': selectors or {},
            'added_at': datetime.utcnow().isoformat()
        })
        
    async def scrape_prices(self, url: str, selectors: Dict = None) -> List[Dict[str, Any]]:
        """Scrape product prices from competitor site"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=30) as resp:
                    if resp.status != 200:
                        return [{'error': f'HTTP {resp.status}'}]
                    
                    content = await resp.text()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    products = []
                    
                    # Try common e-commerce price patterns
                    price_patterns = [
                        r'\$([\d,]+\.\d{2})',
                        r'USD\s*([\d,]+\.\d{2})',
                        r'Price:\s*\$([\d,]+\.\d{2})'
                    ]
                    
                    # Find all prices on page
                    for pattern in price_patterns:
                        matches = re.findall(pattern, content)
                        for match in matches[:10]:  # Limit to first 10
                            try:
                                price = float(match.replace(',', ''))
                                if 1 < price < 10000:  # Reasonable price range
                                    products.append({
                                        'price': price,
                                        'source': url,
                                        'scraped_at': datetime.utcnow().isoformat()
                                    })
                            except:
                                pass
                    
                    return products
        except Exception as e:
            return [{'error': str(e)}]
    
    async def check_competitor(self, competitor: Dict) -> Dict[str, Any]:
        """Check a single competitor"""
        products = await self.scrape_prices(competitor['url'], competitor.get('selectors'))
        
        return {
            'competitor': competitor['name'],
            'url': competitor['url'],
            'products_found': len([p for p in products if 'error' not in p]),
            'products': products[:20],  # Limit results
            'checked_at': datetime.utcnow().isoformat()
        }
    
    async def check_all_competitors(self) -> List[Dict[str, Any]]:
        """Check all registered competitors"""
        if not self.competitors:
            return [{'message': 'No competitors registered'}]
        
        tasks = [self.check_competitor(c) for c in self.competitors]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            r if not isinstance(r, Exception) else {'error': str(r)}
            for r in results
        ]
    
    def compare_prices(self, our_products: List[Dict], competitor_data: List[Dict]) -> Dict[str, Any]:
        """Compare our prices vs competitors"""
        comparison = {
            'cheaper': [],
            'more_expensive': [],
            'similar': [],
            'no_match': []
        }
        
        competitor_prices = []
        for c in competitor_data:
            for p in c.get('products', []):
                if 'price' in p:
                    competitor_prices.append(p['price'])
        
        if not competitor_prices:
            return {'message': 'No competitor prices found', 'comparison': comparison}
        
        avg_competitor = sum(competitor_prices) / len(competitor_prices)
        
        for product in our_products:
            our_price = product.get('price', 0)
            diff = ((our_price - avg_competitor) / avg_competitor) * 100 if avg_competitor > 0 else 0
            
            product_comparison = {
                'product': product.get('title', 'Unknown'),
                'our_price': our_price,
                'avg_competitor': round(avg_competitor, 2),
                'difference_percent': round(diff, 1)
            }
            
            if diff < -5:
                comparison['cheaper'].append(product_comparison)
            elif diff > 5:
                comparison['more_expensive'].append(product_comparison)
            else:
                comparison['similar'].append(product_comparison)
        
        return {
            'total_products_analyzed': len(our_products),
            'competitor_prices_found': len(competitor_prices),
            'avg_competitor_price': round(avg_competitor, 2),
            'comparison': comparison,
            'analyzed_at': datetime.utcnow().isoformat()
        }
