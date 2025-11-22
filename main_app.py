# -*- coding: utf-8 -*-
"""
Main Application - التطبيق الرئيسي
"""

import time
import random
from typing import List, Dict
from avatar_extractor import AvatarExtractor
from profile_analyzer import ProfileAnalyzer, ReportGenerator

class SocialMediaExtractorApp:
    """التطبيق الرئيسي"""
    
    def __init__(self):
        self.avatar_extractor = AvatarExtractor()
        self.profile_analyzer = ProfileAnalyzer()
        self.results = []
    
    def process_urls(self, urls: List[str]) -> List[Dict]:
        """معالجة قائمة الروابط"""
        print(f"🚀 بدء معالجة {len(urls)} روابط...")
        self.results = []
        
        for i, url in enumerate(urls, 1):
            print(f"\n📍 معالجة الرابط {i}/{len(urls)}: {url}")
            
            try:
                # استخراج الصورة
                result = self.avatar_extractor.extract_avatar(url)
                self.results.append(result)
                
                # عرض النتيجة
                if result['success']:
                    print(f"   ✅ نجح - {result.get('platform')} - {result.get('resolution', (0, 0))[0]}x{result.get('resolution', (0, 0))[1]}")
                else:
                    print(f"   ❌ فشل - {result.get('error')}")
                
            except Exception as e:
                error_result = {
                    'success': False, 
                    'error': f'خطأ غير متوقع: {str(e)}', 
                    'input_url': url
                }
                self.results.append(error_result)
                print(f"   💥 خطأ - {str(e)}")
            
            # تأخير بين الطلبات
            if i < len(urls):
                delay = random.uniform(1, 3)
                time.sleep(delay)
        
        print(f"\n🎊 اكتملت معالجة جميع الروابط!")
        return self.results
    
    def get_summary(self) -> Dict:
        """الحصول على ملخص النتائج"""
        return ReportGenerator.generate_summary(self.results)
    
    def get_successful_results(self) -> List[Dict]:
        """الحصول على النتائج الناجحة فقط"""
        return [r for r in self.results if r.get('success')]
    
    def get_failed_results(self) -> List[Dict]:
        """الحصول على النتائج الفاشلة فقط"""
        return [r for r in self.results if not r.get('success')]

# للاستخدام المباشر
if __name__ == "__main__":
    # مثال للاستخدام
    app = SocialMediaExtractorApp()
    
    test_urls = [
        "https://youtube.com/@mivo1-l",
        "https://www.youtube.com/@YouTube",
        "https://www.instagram.com/instagram/",
    ]
    
    results = app.process_urls(test_urls)
    summary = app.get_summary()
    
    print(f"\n📊 الملخص النهائي:")
    print(f"   الإجمالي: {summary['total_urls']}")
    print(f"   الناجحة: {summary['successful']}")
    print(f"   الفاشلة: {summary['failed']}")
    print(f"   النسبة: {summary['success_rate']:.1f}%")
