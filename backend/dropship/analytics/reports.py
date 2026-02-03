"""Report Generator for Dropshipping Analytics"""
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json

class ReportGenerator:
    """Generate automated reports"""
    
    def __init__(self, analytics_engine, db=None):
        self.analytics = analytics_engine
        self.db = db
        
    async def generate_daily_report(self) -> Dict[str, Any]:
        """Generate daily performance report"""
        today = datetime.utcnow().strftime('%Y-%m-%d')
        yesterday = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        today_metrics = await self.analytics.get_daily_metrics(today)
        yesterday_metrics = await self.analytics.get_daily_metrics(yesterday)
        
        # Calculate changes
        changes = {}
        for key in ['revenue', 'orders', 'visitors', 'conversion_rate']:
            today_val = today_metrics.get(key, 0)
            yesterday_val = yesterday_metrics.get(key, 0)
            if yesterday_val > 0:
                change = ((today_val - yesterday_val) / yesterday_val) * 100
            else:
                change = 0
            changes[f'{key}_change'] = round(change, 1)
        
        return {
            'report_type': 'daily',
            'date': today,
            'metrics': today_metrics,
            'vs_yesterday': changes,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    async def generate_weekly_report(self) -> Dict[str, Any]:
        """Generate weekly performance report"""
        metrics = await self.analytics.get_metrics_range(7)
        kpis = self.analytics.calculate_kpis(metrics)
        
        # Get previous week for comparison
        prev_metrics = await self.analytics.get_metrics_range(14)
        prev_week = prev_metrics[7:14] if len(prev_metrics) >= 14 else []
        prev_kpis = self.analytics.calculate_kpis(prev_week) if prev_week else {}
        
        return {
            'report_type': 'weekly',
            'period': f"{metrics[-1]['date']} to {metrics[0]['date']}",
            'kpis': kpis,
            'vs_previous_week': prev_kpis,
            'daily_breakdown': metrics,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    async def generate_product_performance_report(self, products: List[Dict]) -> Dict[str, Any]:
        """Generate product performance report"""
        product_analysis = []
        
        for product in products:
            margin = self.analytics.calculate_profit_margin(product)
            product_analysis.append({
                'product': product.get('title', 'Unknown'),
                'sku': product.get('sku', ''),
                'price': product.get('price', 0),
                'sales': product.get('sales_count', 0),
                'revenue': product.get('revenue', 0),
                'profit_margin': margin['profit_margin_percent'],
                'stock': product.get('inventory_qty', 0),
                'status': 'low_stock' if product.get('inventory_qty', 0) < 10 else 'ok'
            })
        
        # Sort by revenue
        product_analysis.sort(key=lambda x: x['revenue'], reverse=True)
        
        return {
            'report_type': 'product_performance',
            'total_products': len(products),
            'top_performers': product_analysis[:10],
            'low_stock_products': [p for p in product_analysis if p['status'] == 'low_stock'],
            'low_margin_products': [p for p in product_analysis if p['profit_margin'] < 20],
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def format_report_text(self, report: Dict) -> str:
        """Format report as readable text"""
        lines = []
        lines.append(f"=" * 50)
        lines.append(f"📊 {report.get('report_type', 'Report').upper()} REPORT")
        lines.append(f"Generated: {report.get('generated_at', 'Unknown')}")
        lines.append(f"=" * 50)
        
        if 'kpis' in report:
            kpis = report['kpis']
            lines.append(f"\n💰 Revenue: ${kpis.get('total_revenue', 0):,.2f}")
            lines.append(f"📦 Orders: {kpis.get('total_orders', 0)}")
            lines.append(f"👥 Visitors: {kpis.get('total_visitors', 0)}")
            lines.append(f"📈 Conversion: {kpis.get('conversion_rate', 0)}%")
            lines.append(f"💵 AOV: ${kpis.get('avg_order_value', 0):.2f}")
            lines.append(f"📊 ROAS: {kpis.get('roas', 0)}x")
        
        if 'metrics' in report:
            m = report['metrics']
            lines.append(f"\n💰 Revenue: ${m.get('revenue', 0):,.2f}")
            lines.append(f"📦 Orders: {m.get('orders', 0)}")
        
        return "\n".join(lines)
