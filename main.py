import os
import google.generativeai as genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# 1. جلب الأسرار والمتغيرات من بيئة التشغيل (GitHub Secrets)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN")
BLOG_ID = os.environ.get("BLOG_ID")

def generate_article():
    """توليد مقال جديد ومفيد تلقائياً باستخدام نموذج Gemini"""
    genai.configure(api_key=GEMINI_API_KEY)
    
    # استخدام نموذج Gemini السريع والمستقر
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = (
        "اكتب مقالاً تقنياً أو تعليمياً غنياً بالمعلومات باللغة العربية لصالح مدونة 'غراس المعرفة'. "
        "اختر موضوعاً مفيداً (مثل: أحدث تقنيات الذكاء الاصطناعي، أو نصائح برمجية، أو أدوات الإنتاجية الرقمية). "
        "اكتب المقال منسقاً بصيغة HTML (يحتوي على عنوان رئيسي H1، وعناوين فرعية H2، وفقات مرتبة ومفصلة)."
    )
    
    print("جاري توليد المقال بواسطة ذكاء Gemini الاصطناعي...")
    response = model.generate_content(prompt)
    article_content = response.text
    
    # استخراج عنوان افتراضي أو عنوان مناسب من المقال
    article_title = "مقال تقني جديد من غراس المعرفة"
    
    return article_title, article_content

def publish_to_blogger(title, content):
    """نشر المقال تلقائياً على مدونة Blogger باستخدام مفاتيح الاعتماد"""
    if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, BLOG_ID]):
        raise ValueError("خطأ: بعض المتغيرات السرية المطلوبة لنشر بلوجر غير متوفرة في البيئة!")

    # إعداد بيانات المصادقة عبر OAuth2
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
    
    print("جاري إرسال ونشر المقال على مدونة بلوجر...")
    posts_resource = service.posts()
    request = posts_resource.insert(blogId=BLOG_ID, body=post_body)
    result = request.execute()
    
    print(f"تم النشر بنجاح تام! رابط المقال: {result.get('url')}")

if __name__ == "__main__":
    try:
        title, content = generate_article()
        publish_to_blogger(title, content)
    except Exception as e:
        print(f"حدث خطأ أثناء عملية التوليد أو النشر: {e}")
        exit(1)
