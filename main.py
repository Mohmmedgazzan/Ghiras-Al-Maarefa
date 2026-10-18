import os
import google.generativeai as genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# 1. جلب الأسرار من بيئة التشغيل
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN")
BLOG_ID = os.environ.get("BLOG_ID")

def generate_article():
    """توليد مقال جديد باستخدام مكتبة Gemini المستقرة"""
    print("جاري تهيئة نموذج Gemini وتوليد المقال...")
    genai.configure(api_key=GEMINI_API_KEY)
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = (
        "اكتب مقالاً تقنياً أو تعليمياً غنياً بالمعلومات باللغة العربية لصالح مدونة 'غراس المعرفة'. "
        "اختر موضوعاً مفيداً (مثل: أحدث تقنيات الذكاء الاصطناعي، أو نصائح برمجية، أو أدوات الإنتاجية الرقمية). "
        "اكتب المقال منسقاً بصيغة HTML (يحتوي على عنوان رئيسي H1، وعناوين فرعية H2، وفقات مرتبة ومفصلة)."
    )
    
    response = model.generate_content(prompt)
    article_title = "مقال تقني جديد من غراس المعرفة"
    return article_title, response.text

def publish_to_blogger(title, content):
    """نشر المقال على مدونة بلوجر"""
    if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, BLOG_ID]):
        raise ValueError("خطأ: بعض المتغيرات السرية لنشر بلوجر غير متوفرة!")

    creds = Credentials(
        None,
        refresh_token=REFRESH_TOKEN,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token"
    )
    
    service = build('blogger', 'v3', credentials=creds)
    
    post_body = {
        'title': title,
        'content': content
    }
    
    print("جاري إرسال المقال ونشره على مدونة بلوجر...")
    result = service.posts().insert(blogId=BLOG_ID, body=post_body).execute()
    print(f"تم النشر بنجاح تام! رابط المقال: {result.get('url')}")

if __name__ == "__main__":
    try:
        title, content = generate_article()
        publish_to_blogger(title, content)
    except Exception as e:
        print(f"حدث خطأ أثناء التنفيذ: {e}")
        exit(1)
