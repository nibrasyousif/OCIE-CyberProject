import json
import random
import os

# 1. تحديد المسارات (تأكد من تشغيل الكود داخل مجلد المشروع)
input_file = 'cyber_data.json'
train_output = 'train_cyber.json'
test_output = 'test_cyber.json'

def split_cyber_data(file_path, train_ratio=0.8):
    # التأكد من وجود الملف
    if not os.path.exists(file_path):
        print(f"خطأ: الملف {file_path} غير موجود في هذا المجلد.")
        return

    # 2. تحميل البيانات من ملف JSON
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"تم تحميل {len(data)} تقرير سيبراني بنجاح.")

    # 3. خلط البيانات عشوائياً لضمان النزاهة في التدريب (كما في منهجية البحث [1])
    random.seed(42) # لتثبيت النتائج عند إعادة التشغيل
    random.shuffle(data)

    # 4. حساب نقطة التقسيم (80% تدريب، 20% اختبار)
    split_index = int(len(data) * train_ratio)
    train_data = data[:split_index]
    test_data = data[split_index:]

    # 5. حفظ مجموعة التدريب
    with open(train_output, 'w', encoding='utf-8') as f:
        json.dump(train_data, f, ensure_ascii=False, indent=4)

    # 6. حفظ مجموعة الاختبار
    with open(test_output, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=4)

    print(f"تم التقسيم بنجاح:")
    print(f" - ملف التدريب ({len(train_data)} عينة): {train_output}")
    print(f" - ملف الاختبار ({len(test_data)} عينة): {test_output}")

# تنفيذ الدالة
split_cyber_data(input_file)