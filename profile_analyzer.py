# -*- coding: utf-8 -*-
"""
Profile Analyzer - محلل الملفات الشخصية
"""

import re
from urllib.parse import urlparse
from typing import Dict, List
from bs4 import BeautifulSoup
import json

class ProfileAnalyzer:
    def __init__(self):
        self.platform_patterns = {
            'youtube': r'@([A-Za-z0-9_.-]+)',
            'instagram': r'instagram\.com/([^/?]+)',
            'tiktok': r'/@([^/?]+)',
            'twitter': r'twitter\.com/([^/?]+)',
        }
    
    def analyze_profile(self, html: str, url: str) -> Dict:
        """تحليل بيانات الملف الشخصي"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            hostname = urlparse(url).netloc.lower()
            platform = self._detect_platform(hostname)
            
            profile_data = {
                'platform': platform,
                'url': url,
                'username': self._extract_username(url, platform),
                'display_name': None,
                'description': None,
                'page_title': None,
            }
            
            # استخراج من meta tags
            meta_data = self._extract_meta_data(soup)
            profile_data.update(meta_data)
            
            # استخراج من عنوان الصفحة
            title = soup.title
            if title and title.string:
                profile_data['page_title'] = title.string.strip()
            
            return profile_data
            
        except Exception as e:
            return {
                'platform': 'unknown',
                'url': url,
                'error': f'خطأ في التحليل: {str(e)}'
            }
    
    def _detect_platform(self, hostname: str) -> str:
        """كشف المنصة"""
        if 'youtube' in hostname or 'youtu.be' in hostname:
            return 'youtube'
        elif 'instagram' in hostname:
            return 'instagram'
        elif 'tiktok' in hostname:
            return 'tiktok'
        elif 'twitter' in hostname or 'x.com' in hostname:
            return 'twitter'
        else:
            return 'generic'
    
    def _extract_username(self, url: str, platform: str) -> str:
        """استخراج اسم المستخدم"""
        if platform in self.platform_patterns:
            pattern = self.platform_patterns[platform]
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # استخراج عام من المسار
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        if path_parts and path_parts[0]:
            return path_parts[0]
        
        return None
    
    def _extract_meta_data(self, soup: BeautifulSoup) -> Dict:
        """استخراج البيانات من meta tags"""
        meta_data = {
            'display_name': None,
            'description': None,
        }
        
        # og:title و og:description
        og_title = soup.find('meta', property='og:title')
        og_description = soup.find('meta', property='og:description')
        
        if og_title and og_title.get('content'):
            meta_data['display_name'] = og_title['content']
        
        if og_description and og_description.get('content'):
            meta_data['description'] = og_description['content']
        
        return meta_data

class ReportGenerator:
    """مولد التقارير"""
    
    @staticmethod
    def generate_summary(results: List[Dict]) -> Dict:
        """توليد ملخص للنتائج"""
        total = len(results)
        successful = sum(1 for r in results if r.get('success'))
        failed = total - successful
        success_rate = (successful / total * 100) if total > 0 else 0
        
        platforms = {}
        for result in results:
            if result.get('success'):
                platform = result.get('platform', 'unknown')
                platforms[platform] = platforms.get(platform, 0) + 1
        
        return {
            'total_urls': total,
            'successful': successful,
            'failed': failed,
            'success_rate': success_rate,
            'platforms': platforms
        }
    
    @staticmethod
    def generate_detailed_report(results: List[Dict]) -> str:
        """توليد تقرير مفصل"""
        summary = ReportGenerator.generate_summary(results)
        
        report = "📊 تقرير مفصل لاستخراج الصور\n"
        report += "=" * 50 + "\n\n"
        
        report += f"📋 الإجمالي: {summary['total_urls']} رابط\n"
        report += f"✅ الناجحة: {summary['successful']}\n"
        report += f"❌ الفاشلة: {summary['failed']}\n"
        report += f"🎯 نسبة النجاح: {summary['success_rate']:.1f}%\n\n"
        
        if summary['platforms']:
            report += "📺 التوزيع حسب المنصة:\n"
            for platform, count in summary['platforms'].items():
                report += f"   - {platform}: {count}\n"
        
        return report

# للاستخدام المباشر
if __name__ == "__main__":
    analyzer = ProfileAnalyzer()
    # يمكن اختباره مع HTML حقيقي
    print("Profile Analyzer جاهز للاستخدام")
