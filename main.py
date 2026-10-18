import os
import random
import sys

from google import genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


# =========================================================
# 1. الإعدادات والمتغيرات السرية
# =========================================================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN")
BLOG_ID = os.environ.get("BLOG_ID")

# استخدام النموذج المعتمد والمستقر للاتصال السريع
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
# 4. النشر على Blogger
# =========================================================

def publish_to_blogger(title, content):
    """
    نشر المقال على مدونة بلوجر باستخدام OAuth 2.0.
    """

    print("جاري تهيئة اتصال Blogger API...")

    credentials = Credentials(
        token=None,
        refresh_token=REFRESH_TOKEN,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_uri="[https://oauth2.googleapis.com/token](https://oauth2.googleapis.com/token)",
    )

    service = build(
        "blogger",
        "v3",
        credentials=credentials,
        cache_discovery=False,
    )

    post_body = {
        "kind": "blogger#post",
        "title": title,
        "content": content,
    }

    print("جاري إرسال المقال إلى بلوجر...")

    result = service.posts().insert(
        blogId=BLOG_ID,
        body=post_body,
        isDraft=False,
    ).execute()

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
            f"فشل تنفيذ البرنامج: "
            f"{type(error).__name__}: {error}",
            file=sys.stderr,
        )
        raise


if __name__ == "__main__":
    main()
