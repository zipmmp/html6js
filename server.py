# -*- coding: utf-8 -*-
"""
Server - خادم الويب للربط بين الواجهة والسكربتات
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os
from main_app import SocialMediaExtractorApp

app = Flask(__name__)
CORS(app)

# إنشاء instance من التطبيق
extractor_app = SocialMediaExtractorApp()

@app.route('/')
def index():
    """عرض الواجهة الرئيسية"""
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract_avatars():
    """استخراج الصور من الروابط"""
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        
        if not urls:
            return jsonify({'error': 'لم يتم تقديم أي روابط'}), 400
        
        print(f"📥 استلام طلب لمعالجة {len(urls)} روابط")
        
        # معالجة الروابط
        results = extractor_app.process_urls(urls)
        
        # توليد الملخص
        summary = extractor_app.get_summary()
        
        response = {
            'success': True,
            'summary': summary,
            'results': results,
            'total_processed': len(results)
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'خطأ في المعالجة: {str(e)}'}), 500

@app.route('/status')
def status():
    """حالة الخادم"""
    return jsonify({
        'status': 'يعمل',
        'message': 'خادم مستخرج الصور جاهز للاستخدام'
    })

@app.route('/examples')
def get_examples():
    """الحصول على أمثلة للروابط"""
    examples = {
        'youtube': [
            'https://youtube.com/@mivo1-l',
            'https://www.youtube.com/@YouTube'
        ],
        'instagram': [
            'https://www.instagram.com/instagram/',
            'https://www.instagram.com/cristiano/'
        ],
        'tiktok': [
            'https://www.tiktok.com/@tiktok',
            'https://www.tiktok.com/@khaby.lame'
        ],
        'twitter': [
            'https://twitter.com/elonmusk',
            'https://twitter.com/Twitter'
        ]
    }
    return jsonify(examples)

if __name__ == '__main__':
    print("🚀 بدء تشغيل خادم مستخرج الصور...")
    print("📧 Endpoints المتاحة:")
    print("   GET  /          - الواجهة الرئيسية")
    print("   POST /extract   - استخراج الصور")
    print("   GET  /status    - حالة الخادم")
    print("   GET  /examples  - أمثلة الروابط")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
