import json
import collections
import os

# اسم الملف الأصلي الذي صدرتيه من ليبل ستوديو
file_name = 'cyber_data.json'

if not os.path.exists(file_name):
    print(f"خطأ: الملف {file_name} غير موجود في المجلد الحالي!")
else:
    all_labels = []
    
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # المرور على كل وثيقة تم توسيمها
            for entry in data:
                # هيكلية ليبل ستوديو المعتادة للأوسمة
                if 'annotations' in entry:
                    for ann in entry['annotations']:
                        if 'result' in ann:
                            for res in ann['result']:
                                if 'value' in res and 'labels' in res['value']:
                                    for label in res['value']['labels']:
                                        all_labels.append(label)
                # في حال كانت الهيكلية مبسطة (JSON_MIN)
                elif 'label' in entry:
                    for label_item in entry['label']:
                        if isinstance(label_item, dict) and 'labels' in label_item:
                            all_labels.extend(label_item['labels'])
                        else:
                            all_labels.append(label_item)

        # حساب التكرارات لكل فئة
        counts = collections.Counter(all_labels)
        total_annotations = len(all_labels)

        print(f"\n--- إحصائيات المجهود اليدوي الكلي (قبل الفصل) ---")
        print(f"اسم الملف المعالج: {file_name}")
        print(f"إجمالي عدد الأوسمة الفرعية (Sub-annotations): {total_annotations}")
        print(f"توزيع الأوسمة على الكيانات السيبرانية:")
        
        # ترتيب النتائج حسب الأكثر تكراراً
        for label, count in counts.most_common():
            print(f"- {label}: {count}")

    except Exception as e:
        print(f"حدث خطأ أثناء قراءة الملف: {e}")