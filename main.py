import os
import random
from google import genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# 1. جلب الأسرار من بيئة التشغيل
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN")
BLOG_ID = os.environ.get("BLOG_ID")

def generate_article():
    """توليد مقال متنوع وغني بالمعلومات النافعة يغطي الجوانب الإسلامية، الثقافية، الفكرية، والعامة"""
    print("جاري تهيئة نموذج Gemini وتحديد موضوع المقال...")
    
    # تهيئة العميل باستخدام الحزمة الحديثة google-genai
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # قائمة المواضيع والتصنيفات الشاملة
    topics = [
        "العقيدة والتوحيد",
        "السيرة النبوية العطرة",
        "الفقه الإسلامي والأحكام اليومية",
        "الثقافة العامة والفكر الإنساني",
        "الأدب والبلاغة واللغة العربية",
        "التاريخ الإسلامي والحضاري",
        "قصص وعبر تاريخية وإسلامية",
        "الصحة العامة والطب الوقائي",
        "علم النفس وتطوير الذات",
        "تربية الأطفال وبناء الأسرة",
        "حكم ودرر ومواعظ نافعة",
        "محطات ثقافية ومعارف منوعة"
    ]
    
    selected_topic = random.choice(topics)
    
    prompt = (
        f"اكتب مقالاً قيماً وعميقاً باللغة العربية لصالح مدونة 'غراس المعرفة'. "
        f"موضوع المقال الأساسي يجب أن يكون في مجال: ({selected_topic}). "
        "اجعل المقال هادفاً، مكتوباً بأسلوب بليغ وموثوق، ومثرياً للقارئ بالعلم النافع والمعرفة الرصينة. "
        "اكتب المقال منسقاً بصيغة HTML متكاملة (يحتوي على عنوان رئيسي H1 معبر، وعناوين فرعية H2، و فقرات مرتبة ومنسقة بدقة)."
    )
    
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=prompt,
    )
    
    article_title = f"{selected_topic} - غراس المعرفة"
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
