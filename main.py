import os
import google.generativeai as genai

# استدعاء مفتاح الـ API من متغيرات النظام بأمان
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise ValueError("مفتاح API غير متوفر في متغيرات البيئة!")

# تهيئة مكتبة جيميني
genai.configure(api_key=api_key)

# اختيار النموذج الأحدث والأسرع
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_article():
    prompt = """
    اكتب مقالاً حصرياً ومميزاً لمدونة "غراس المعرفة" في أحد المواضيع النافعة (تاريخ إسلامي، أدب رفيع، أو قيم إسلامية).
    الشروط:
    1. أن يكون المقال خالياً تماماً من الأخطاء الإملائية والنحوية.
    2. يتضمن عنواناً جذاباً ومحسناً لمحركات البحث (SEO).
    3. مقسم إلى فقرات منظمة مع مقدمة وخاتمة.
    """
    
    response = model.generate_content(prompt)
    print("--- تم توليد المقال بنجاح ---")
    print(response.text)

if __name__ == "__main__":
    generate_article()
