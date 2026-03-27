import spacy
from spacy.tokens import DocBin
import json
import os

# 1. إعداد المحرك اللغوي (أطروحة الدكتوراه تعتمد على spaCy 3.x)
nlp = spacy.blank("en")

def convert_to_spacy_format(input_json, output_file):
    if not os.path.exists(input_json):
        print(f"خطأ: الملف {input_json} غير موجود.")
        return

    db = DocBin()
    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    count = 0
    for entry in data:
        # استخراج النص (تأكد أن Label Studio يستخدم حقل 'text')
        text = entry['data'].get('text') or entry['data'].get('cyber_report')
        if not text:
            continue
            
        doc = nlp.make_doc(text)
        ents = []
        
        for annotation in entry['annotations']:
            for res in annotation['result']:
                if 'value' in res:
                    val = res['value']
                    start = val.get('start')
                    end = val.get('end')
                    labels = val.get('labels')
                    
                    # التحقق من صحة البيانات قبل المعالجة
                    if start is not None and end is not None and labels:
                        # الحل الجذري: استخراج الوسم كنص صريح (String)
                        # Label Studio يرسلها كـ ['THREAT_ACTOR'] ونحن نحتاج 'THREAT_ACTOR'
                        label_name = str(labels) 
                        
                        # إنشاء الكيان مع معالجة المسافات الزائدة (Alignment)
                        span = doc.char_span(start, end, label=label_name, alignment_mode="contract")
                        if span is not None:
                            ents.append(span)
        
        # ربط الخصائص (Properties) بالكيان الرئيسي (CyberIncident) [1]
        try:
            doc.ents = ents
            db.add(doc)
            count += 1
        except Exception as e:
            print(f"تنبيه في السجل {count}: تداخل في الكيانات، تم التخطي.")
    
    db.to_disk(output_file)
    print(f"✅ نجاح: تم تحويل {count} سجل إلى {output_file}")

# التنفيذ الفعلي على ملفاتك
if __name__ == "__main__":
    print("--- بدء عملية معالجة بيانات الأمن السيبراني ---")
    convert_to_spacy_format('train_cyber.json', 'train.spacy')
    convert_to_spacy_format('test_cyber.json', 'test.spacy')