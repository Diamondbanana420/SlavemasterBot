"""Site Performance & SEO Monitor"""
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, Any, List
import re

class SiteMonitor:
    def __init__(self, store_url: str, frontend_url: str):
        self.store_url = store_url
        self.frontend_url = frontend_url
        self.results = {}
        
    async def check_page_speed(self, url: str) -> Dict[str, Any]:
        """Check page load time and performance"""
        try:
            start = datetime.utcnow()
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://{url}', timeout=30) as resp:
                    content = await resp.text()
                    end = datetime.utcnow()
                    load_time = (end - start).total_seconds()
                    
                    return {
                        'url': url,
                        'status_code': resp.status,
                        'load_time_seconds': round(load_time, 2),
                        'content_length': len(content),
                        'performance': 'good' if load_time < 3 else 'needs_improvement' if load_time < 5 else 'poor',
                        'checked_at': datetime.utcnow().isoformat()
                    }
        except Exception as e:
            return {'url': url, 'error': str(e)}
    
    async def check_seo_elements(self, url: str) -> Dict[str, Any]:
        """Check SEO elements on page"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://{url}', timeout=30) as resp:
                    content = await resp.text()
                    
                    # Check for SEO elements
                    has_title = '<title>' in content.lower()
                    has_meta_desc = 'meta name="description"' in content.lower()
                    has_h1 = '<h1' in content.lower()
                    has_canonical = 'rel="canonical"' in content.lower()
                    has_og_tags = 'og:' in content.lower()
                    has_schema = 'application/ld+json' in content.lower()
                    
                    # Count images without alt
                    img_count = content.lower().count('<img')
                    img_with_alt = len(re.findall(r'<img[^>]+alt=["\'][^"\']+["\']', content, re.I))
                    
                    issues = []
                    if not has_title:
                        issues.append('Missing title tag')
                    if not has_meta_desc:
                        issues.append('Missing meta description')
                    if not has_h1:
                        issues.append('Missing H1 tag')
                    if not has_canonical:
                        issues.append('Missing canonical URL')
                    if not has_schema:
                        issues.append('Missing structured data')
                    if img_count > img_with_alt:
                        issues.append(f'{img_count - img_with_alt} images missing alt text')
                    
                    score = sum([has_title, has_meta_desc, has_h1, has_canonical, has_og_tags, has_schema]) / 6 * 100
                    
                    return {
                        'url': url,
                        'seo_score': round(score, 1),
                        'has_title': has_title,
                        'has_meta_description': has_meta_desc,
                        'has_h1': has_h1,
                        'has_canonical': has_canonical,
                        'has_og_tags': has_og_tags,
                        'has_structured_data': has_schema,
                        'images_total': img_count,
                        'images_with_alt': img_with_alt,
                        'issues': issues,
                        'checked_at': datetime.utcnow().isoformat()
                    }
        except Exception as e:
            return {'url': url, 'error': str(e)}
    
    async def check_mobile_friendly(self, url: str) -> Dict[str, Any]:
        """Check mobile responsiveness indicators"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://{url}', timeout=30) as resp:
                    content = await resp.text()
                    
                    has_viewport = 'viewport' in content.lower()
                    has_responsive_meta = 'width=device-width' in content.lower()
                    
                    return {
                        'url': url,
                        'has_viewport_meta': has_viewport,
                        'has_responsive_meta': has_responsive_meta,
                        'mobile_ready': has_viewport and has_responsive_meta,
                        'checked_at': datetime.utcnow().isoformat()
                    }
        except Exception as e:
            return {'url': url, 'error': str(e)}
    
    async def check_trust_signals(self, url: str) -> Dict[str, Any]:
        """Check for trust signals on the site"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://{url}', timeout=30) as resp:
                    content = await resp.text().lower()
                    
                    signals = {
                        'has_ssl': url.startswith('https') or resp.url.scheme == 'https',
                        'has_reviews': any(x in content for x in ['review', 'testimonial', 'rating']),
                        'has_trust_badges': any(x in content for x in ['secure', 'guarantee', 'certified', 'verified']),
                        'has_contact_info': any(x in content for x in ['contact', 'email', 'phone', 'address']),
                        'has_return_policy': 'return' in content or 'refund' in content,
                        'has_privacy_policy': 'privacy' in content,
                        'has_terms': 'terms' in content,
                        'has_social_proof': any(x in content for x in ['facebook', 'instagram', 'twitter', 'tiktok']),
                    }
                    
                    score = sum(signals.values()) / len(signals) * 100
                    
                    return {
                        'url': url,
                        'trust_score': round(score, 1),
                        **signals,
                        'checked_at': datetime.utcnow().isoformat()
                    }
        except Exception as e:
            return {'url': url, 'error': str(e)}
    
    async def full_audit(self) -> Dict[str, Any]:
        """Run complete site audit"""
        tasks = [
            self.check_page_speed(self.frontend_url),
            self.check_seo_elements(self.frontend_url),
            self.check_mobile_friendly(self.frontend_url),
            self.check_trust_signals(self.frontend_url),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            'store': self.store_url,
            'frontend': self.frontend_url,
            'performance': results[0] if not isinstance(results[0], Exception) else {'error': str(results[0])},
            'seo': results[1] if not isinstance(results[1], Exception) else {'error': str(results[1])},
            'mobile': results[2] if not isinstance(results[2], Exception) else {'error': str(results[2])},
            'trust': results[3] if not isinstance(results[3], Exception) else {'error': str(results[3])},
            'audit_timestamp': datetime.utcnow().isoformat()
        }
