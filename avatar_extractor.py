
# -*- coding: utf-8 -*-
"""
Avatar Extractor - مستخرج الصور
"""

import requests
from bs4 import BeautifulSoup
import re
import json
from urllib.parse import urlparse
import time
import random
import base64
import io
from PIL import Image
import os
from typing import Dict, List

class AvatarExtractor:
    def __init__(self):
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/avif,image/*,*/*;q=0.8',
        })
    
    def extract_avatar(self, url: str) -> Dict:
        """استخراج الصورة من الرابط"""
        try:
            print(f"🔍 جاري استخراج الصورة من: {url}")
            
            # تنظيف الرابط
            clean_url = self._clean_url(url)
            
            # جلب الصفحة
            response = self.session.get(clean_url, timeout=15)
            html = response.text
            final_url = response.url
            
            # استخراج الصور
            avatars = self._extract_avatars(html, final_url)
            
            if not avatars:
                return {'success': False, 'error': 'لم يتم العثور على صور', 'input_url': url}
            
            # اختيار أفضل صورة
            best_avatar = self._select_best_avatar(avatars)
            
            if not best_avatar:
                return {'success': False, 'error': 'لا توجد صور بجودة مناسبة', 'input_url': url}
            
            # تحميل الصورة
            download_result = self._download_image(best_avatar['url'])
            
            if download_result['success']:
                result = {
                    'success': True,
                    'input_url': url,
                    'platform': best_avatar.get('platform', 'unknown'),
                    'avatar_url': best_avatar['url'],
                    'base64_data': download_result['base64_data'],
                    'resolution': download_result['resolution'],
                    'file_size': download_result['file_size'],
                    'format': download_result['format']
                }
                print(f"✅ تم استخراج الصورة بنجاح من {url}")
                return result
            else:
                return {'success': False, 'error': download_result['error'], 'input_url': url}
                
        except Exception as e:
            return {'success': False, 'error': f'خطأ في الاستخراج: {str(e)}', 'input_url': url}
    
    def _clean_url(self, url: str) -> str:
        """تنظيف الرابط"""
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    def _extract_avatars(self, html: str, url: str) -> List[Dict]:
        """استخراج جميع الصور المتاحة"""
        hostname = urlparse(url).netloc.lower()
        
        if 'youtube' in hostname:
            return self._extract_youtube_avatars(html, url)
        elif 'instagram' in hostname:
            return self._extract_instagram_avatars(html)
        elif 'tiktok' in hostname:
            return self._extract_tiktok_avatars(html)
        elif 'twitter' in hostname or 'x.com' in hostname:
            return self._extract_twitter_avatars(html)
        else:
            return self._extract_generic_avatars(html, url)
    
    def _extract_youtube_avatars(self, html: str, url: str) -> List[Dict]:
        """استخراج صور YouTube"""
        avatars = []
        
        try:
            # من ytInitialData
            yt_data_match = re.search(r'var ytInitialData\s*=\s*({.+?});', html)
            if yt_data_match:
                yt_data = json.loads(yt_data_match.group(1))
                
                thumbnail_paths = [
                    'metadata.channelMetadataRenderer.avatar.thumbnails',
                    'microformat.channelMicroformatRenderer.thumbnail.thumbnails',
                ]
                
                for path in thumbnail_paths:
                    thumbnails = self._get_nested_value(yt_data, path)
                    if thumbnails:
                        for thumb in thumbnails:
                            if thumb.get('url'):
                                enhanced_url = self._enhance_youtube_url(thumb['url'])
                                avatars.append({
                                    'url': enhanced_url,
                                    'width': thumb.get('width', 0),
                                    'height': thumb.get('height', 0),
                                    'platform': 'youtube',
                                    'quality': max(thumb.get('width', 0), thumb.get('height', 0))
                                })
            
            # من meta tags
            soup = BeautifulSoup(html, 'html.parser')
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                meta_url = og_image['content']
                enhanced_url = self._enhance_youtube_url(meta_url)
                avatars.append({
                    'url': enhanced_url,
                    'width': 300,
                    'height': 300,
                    'platform': 'youtube',
                    'quality': 300
                })
            
        except Exception as e:
            print(f"⚠️ خطأ في استخراج YouTube: {e}")
        
        return avatars
    
    def _extract_instagram_avatars(self, html: str) -> List[Dict]:
        """استخراج صور Instagram"""
        avatars = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # من JSON المضمن
            json_patterns = [
                r'"profile_pic_url_hd"\s*:\s*"([^"]+)"',
                r'"profile_pic_url"\s*:\s*"([^"]+)"',
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, html)
                for match in matches:
                    if 'http' in match:
                        clean_url = match.replace('\\u0026', '&')
                        avatars.append({
                            'url': clean_url,
                            'width': 1080,
                            'height': 1080,
                            'platform': 'instagram',
                            'quality': 1080
                        })
            
            # من meta tags
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                meta_url = og_image['content']
                hd_url = meta_url.replace('150x150', '1080x1080')
                avatars.append({
                    'url': hd_url,
                    'width': 1080,
                    'height': 1080,
                    'platform': 'instagram',
                    'quality': 1080
                })
            
        except Exception as e:
            print(f"⚠️ خطأ في استخراج Instagram: {e}")
        
        return avatars
    
    def _extract_tiktok_avatars(self, html: str) -> List[Dict]:
        """استخراج صور TikTok"""
        avatars = []
        
        try:
            # البحث في JSON المضمن
            json_patterns = [
                r'"avatarLarger"\s*:\s*"([^"]+)"',
                r'"avatarMedium"\s*:\s*"([^"]+)"',
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, html)
                for match_url in matches:
                    if 'http' in match_url:
                        clean_url = match_url.replace('\\u0026', '&')
                        quality = 1000 if 'Larger' in pattern else 300
                        avatars.append({
                            'url': clean_url,
                            'width': quality,
                            'height': quality,
                            'platform': 'tiktok',
                            'quality': quality
                        })
            
        except Exception as e:
            print(f"⚠️ خطأ في استخراج TikTok: {e}")
        
        return avatars
    
    def _extract_twitter_avatars(self, html: str) -> List[Dict]:
        """استخراج صور Twitter/X"""
        avatars = []
        
        try:
            patterns = [
                r'"profile_image_url_https":"([^"]+)"',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html)
                for match_url in matches:
                    if 'http' in match_url:
                        clean_url = match_url.replace('\\u0026', '&')
                        hd_url = clean_url.replace('_normal', '').replace('_bigger', '')
                        avatars.append({
                            'url': hd_url,
                            'width': 400,
                            'height': 400,
                            'platform': 'twitter',
                            'quality': 400
                        })
            
        except Exception as e:
            print(f"⚠️ خطأ في استخراج Twitter: {e}")
        
        return avatars
    
    def _extract_generic_avatars(self, html: str, url: str) -> List[Dict]:
        """استخراج صور عامة"""
        avatars = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # من meta tags
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                avatars.append({
                    'url': og_image['content'],
                    'width': 500,
                    'height': 500,
                    'platform': 'generic',
                    'quality': 500
                })
            
        except Exception as e:
            print(f"⚠️ خطأ في استخراج الصور العامة: {e}")
        
        return avatars
    
    def _enhance_youtube_url(self, url: str) -> str:
        """تحسين رابط YouTube"""
        if not url or 'ytimg.com' not in url:
            return url
        
        enhancements = [
            ('s88-c-k', 's800-c-k'),
            ('s100-c-k', 's800-c-k'),
            ('s176-c-k', 's800-c-k'),
        ]
        
        enhanced_url = url
        for old, new in enhancements:
            if old in enhanced_url:
                enhanced_url = enhanced_url.replace(old, new)
                break
        
        return enhanced_url
    
    def _get_nested_value(self, obj, path: str):
        """الحصول على قيمة من JSON متداخل"""
        keys = path.split('.')
        current = obj
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            elif isinstance(current, list) and key.isdigit():
                index = int(key)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    return None
            else:
                return None
        return current
    
    def _select_best_avatar(self, avatars: List[Dict]) -> Dict:
        """اختيار أفضل صورة"""
        if not avatars:
            return None
        
        sorted_avatars = sorted(avatars, key=lambda x: x.get('quality', 0), reverse=True)
        return sorted_avatars[0] if sorted_avatars else None
    
    def _download_image(self, url: str) -> Dict:
        """تحميل الصورة"""
        try:
            response = self.session.get(url, timeout=15, stream=True)
            if response.status_code != 200:
                return {'success': False, 'error': f'فشل التحميل: {response.status_code}'}
            
            image_data = response.content
            img = Image.open(io.BytesIO(image_data))
            
            # تحسين الجودة إذا كانت صغيرة
            if max(img.size) < 400:
                img = img.resize((800, 800), Image.Resampling.LANCZOS)
            
            # تحويل إلى JPEG
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            
            buffered = io.BytesIO()
            img.save(buffered, format='JPEG', quality=95)
            final_image_data = buffered.getvalue()
            
            img_base64 = base64.b64encode(final_image_data).decode()
            
            return {
                'success': True,
                'base64_data': f"data:image/jpeg;base64,{img_base64}",
                'resolution': img.size,
                'file_size': len(final_image_data),
                'format': 'JPEG'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'خطأ في تحميل الصورة: {str(e)}'}

# للاستخدام المباشر
if __name__ == "__main__":
    extractor = AvatarExtractor()
    result = extractor.extract_avatar("https://youtube.com/@mivo1-l")
    print(json.dumps(result, indent=2, ensure_ascii=False))
