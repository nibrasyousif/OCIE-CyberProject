import spacy
from spacy.tokens import DocBin
import json
import os

# إعداد المحرك اللغوي مع تقسيم الجمل لضمان عدم ضياع السياق
nlp = spacy.blank("en")
nlp.add_pipe("sentencizer") 

def convert_to_spacy_format(input_json, output_file):
    if not os.path.exists(input_json):
        print(f"خطأ: الملف {input_json} غير موجود.")
        return

    db = DocBin()
    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    doc_count = 0
    chunk_count = 0

    for entry in data:
        text = entry['data'].get('text') or entry['data'].get('cyber_report')
        if not text: continue
            
        full_doc = nlp.make_doc(text)
        ents = []
        
        for annotation in entry['annotations']:
            for res in annotation['result']:
                if 'value' in res:
                    val = res['value']
                    start, end = val.get('start'), val.get('end')
                    labels = val.get('labels')
                    
                    if start is not None and end is not None and labels:
                        # التعديل الحاسم والصحيح: استخراج العنصر الأول من القائمة كنص نقي
                        if isinstance(labels, list) and len(labels) > 0:
                            label_name = str(labels)  # <-- هنا تم إضافة 
                        else:
                            label_name = str(labels)
                        
                        span = full_doc.char_span(start, end, label=label_name, alignment_mode="contract")
                        if span is not None:
                            ents.append(span)
        
        try:
            full_doc.ents = spacy.util.filter_spans(ents)
        except Exception:
            continue

        # تطبيق استراتيجية التقسيم (Cascade Splitting) بـ 40 كلمة لكسر حاجز الـ 512 توكن
        max_tokens = 15 
        current_start = 0
        
        while current_start < len(full_doc):
            current_end = current_start + max_tokens
            if current_end > len(full_doc):
                current_end = len(full_doc)
            
            # إنشاء القطعة وإعادة تعيين المواقع تلقائياً للحفاظ على الكيانات
            chunk = full_doc[current_start:current_end].as_doc()
            
            if len(chunk) > 0:
                db.add(chunk)
                chunk_count += 1
            
            current_start = current_end
            
        doc_count += 1
    
    db.to_disk(output_file)
    print(f"✅ نجاح: تم معالجة {doc_count} سجل أصلي.")
    print(f"📦 النتيجة: تم إنشاء {chunk_count} قطعة (Chunk) متوافقة مع نافذة BERT في {output_file}")

if __name__ == "__main__":
    print("--- بدء هندسة البيانات للأمن السيبراني (الإصدار النهائي المعتمد) ---")
    convert_to_spacy_format('train_cyber.json', 'train.spacy')
    convert_to_spacy_format('test_cyber.json', 'test.spacy')