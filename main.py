import os
import random
import sys
import json
import requests
from google import genai


# =========================================================
# دالة ذكية لتنظيف الأسرار واستخراج القيم تلقائياً حتى لو لُصق ملف JSON كامل
# =========================================================
def clean_secret(val, expected_key=None):
    if not val:
        return ""
    val_str = str(val).strip()
    
    # إذا كان المدخل عبارة عن JSON أو يحتوي على أقواس
    if val_str.startswith("{") and val_str.endswith("}"):
        try:
            data = json.loads(val_str)
            if "installed" in data:
                data = data["installed"]
            elif "web" in data:
                data = data["web"]
            
            if expected_key and expected_key in data:
                return str(data[expected_key]).strip()
            
            # البحث عن المفتاح المناسب تلقائياً
            for k in ["client_id", "client_secret", "refresh_token", "blog_id"]:
                if k in data:
                    return str(data[k]).strip()
                    
            if data:
                return str(list(data.values())[0]).strip()
        except Exception:
            pass
            
    return val_str.strip('{}\'""')


# =========================================================
# 1. الإعدادات والمتغيرات السرية
# =========================================================

CLIENT_ID = clean_secret(os.environ.get("CLIENT_ID"), "client_id")
CLIENT_SECRET = clean_secret(os.environ.get("CLIENT_SECRET"), "client_secret")
REFRESH_TOKEN = clean_secret(os.environ.get("REFRESH_TOKEN"), "refresh_token")
BLOG_ID = clean_secret(os.environ.get("BLOG_ID"), "blog_id")
GEMINI_API_KEY = clean_secret(os.environ.get("GEMINI_API_KEY"))

# استخدام النموذج المعتمد والمستقر
GEMINI_MODEL = os.environ.get(
    "GEMINI_MODEL",
    "gemini-flash-latest"
)


# =========================================================
# 2. التحقق من الإعدادات
# =========================================================

def validate_environment():
    required_variables = {
        "GEMINI_API_KEY": GEMINI_API_KEY,
        "CLIENT_ID": CLIENT_ID,
        "CLIENT_SECRET": CLIENT_SECRET,
        "REFRESH_TOKEN": REFRESH_TOKEN,
        "BLOG_ID": BLOG_ID,
    }

    missing = [
        name
        for name, value in required_variables.items()
        if not value
    ]

    if missing:
        raise ValueError(
            "المتغيرات السرية التالية غير متوفرة: "
            + ", ".join(missing)
        )


# =========================================================
# 3. توليد المقال
# =========================================================

def generate_article():
    """
    توليد مقال عربي منسق بصيغة HTML لمدونة غراس المعرفة.
    """

    print("بدء تجهيز نموذج Gemini...")

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

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
        "محطات ثقافية ومعارف منوعة",
    ]

    selected_topic = random.choice(topics)

    print(f"موضوع المقال المختار: {selected_topic}")
    print(f"النموذج المستخدم: {GEMINI_MODEL}")
    print("جاري توليد المقال...")

    prompt = f"""
أنت كاتب ومحرر محتوى عربي متخصص في إعداد المقالات
الموثوقة والنافعة لمدونة «غراس المعرفة».

المجال المطلوب: {selected_topic}

المطلوب:
1. اختر موضوعًا محددًا ومفيدًا داخل المجال المطلوب.
2. اكتب مقالًا عربيًا أصيلًا، واضحًا، غنيًا بالمعلومات.
3. استخدم عنوانًا رئيسيًا جذابًا ومعبّرًا.
4. قسّم المقال إلى مقدمة وعناوين فرعية وفقرات منظمة.
5. استخدم القوائم عند الحاجة لتسهيل القراءة.
6. اختم بخلاصة مفيدة للقارئ.
7. تجنب التكرار والحشو والادعاءات غير الموثقة.
8. لا تختلق آيات قرآنية أو أحاديث نبوية أو مراجع.
9. في المسائل الدينية، تحرَّ الدقة ولا تنسب قولًا إلى
   القرآن أو السنة دون التثبت.
10. في الموضوعات الطبية، تجنب التشخيص والعلاج الجازم
    دون سند موثوق.
11. أخرج المقال بصيغة HTML صالحة لوضعها في Blogger.
12. استخدم عناصر HTML المناسبة مثل:
    <h1> و <h2> و <h3> و <p> و <ul> و <li>.
13. لا تستخدم وسوم Markdown.
14. لا تضف أي شرح خارج المقال.
15. لا تضع المقال داخل كتلة Markdown مثل ```html.

أخرج HTML المقال فقط.
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )

    article_html = response.text

    if not article_html or not article_html.strip():
        raise RuntimeError(
            "لم يُرجع Gemini محتوى نصيًا للمقال."
        )

    article_html = article_html.strip()

    article_title = f"{selected_topic} - غراس المعرفة"

    print("اكتمل توليد المقال بنجاح.")

    return article_title, article_html


# =========================================================
# 4. النشر على Blogger (بشكل مباشر وآمن تماماً عبر requests)
# =========================================================

def publish_to_blogger(title, content):
    """
    نشر المقال على بلوجر باستخدام طلبات HTTP مباشرة وآمنة.
    """

    print("جاري طلب رمز الوصول (Access Token) مباشرة...")

    token_url = "[https://oauth2.googleapis.com/token](https://oauth2.googleapis.com/token)"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token",
    }

    token_response = requests.post(token_url, data=payload)

    if token_response.status_code != 200:
        raise RuntimeError(
            f"فشل تجديد الرمز ({token_response.status_code}): {token_response.text}"
        )

    token_data = token_response.json()
    access_token = token_data.get("access_token")

    if not access_token:
        raise RuntimeError(
            f"لم يتم العثور على access_token في الاستجابة: {token_response.text}"
        )

    url = f"[https://www.googleapis.com/blogger/v3/blogs/](https://www.googleapis.com/blogger/v3/blogs/){BLOG_ID}/posts"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    post_body = {
        "kind": "blogger#post",
        "title": title,
        "content": content,
        "isDraft": False,
    }

    print("جاري إرسال المقال إلى بلوجر...")

    response = requests.post(url, headers=headers, json=post_body)

    if response.status_code != 200 and response.status_code != 201:
        raise RuntimeError(
            f"فشل النشر على بلوجر ({response.status_code}): {response.text}"
        )

    result = response.json()
    post_url = result.get("url", "")

    print("تم نشر المقال بنجاح.")
    print(f"عنوان المقال: {result.get('title', title)}")
    print(f"رابط المقال: {post_url}")

    return result


# =========================================================
# 5. نقطة تشغيل البرنامج
# =========================================================

def main():
    try:
        validate_environment()

        title, content = generate_article()

        publish_to_blogger(
            title=title,
            content=content,
        )

    except Exception as error:
        print(
            f"فشل تنفيذ البرنامج: {type(error).__name__}: {error}",
            file=sys.stderr,
        )
        raise


if __name__ == "__main__":
    main()
