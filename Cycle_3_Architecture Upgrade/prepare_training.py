import spacy
from spacy.tokens import DocBin
import json
import os

# إعداد المحرك اللغوي مع تقسيم الجمل
nlp = spacy.blank("en")
nlp.add_pipe("sentencizer") 

# --- بداية كود القاموس المدمج (Dictionary-Infused Approach) للدورة الثالثة ---
ruler = nlp.add_pipe("entity_ruler")

# قاموس المصطلحات الصريحة لجهات التهديد وأساليب التخفيف
patterns = [
    {"label": "THREAT_ACTOR", "pattern": "APT29"},
    {"label": "THREAT_ACTOR", "pattern": "CyberAv3ngers"},
    {"label": "THREAT_ACTOR", "pattern": "Volt Typhoon"},
    {"label": "THREAT_ACTOR", "pattern": "LockBit 3.0"},
    {"label": "THREAT_ACTOR", "pattern": "Snatch"},
    {"label": "THREAT_ACTOR", "pattern": "Soldiers of Solomon"},
    {"label": "THREAT_ACTOR", "pattern": "ALPHV"},
    {"label": "THREAT_ACTOR", "pattern": "Scattered Spider"},

    {"label": "MITIGATION", "pattern": "multifactor authentication"},
    {"label": "MITIGATION", "pattern": "MFA"},
    {"label": "MITIGATION", "pattern": "patch systems"},
    {"label": "MITIGATION", "pattern": "disconnect the PLC"},
    {"label": "MITIGATION", "pattern": "upgrade devices"},
    {"label": "MITIGATION", "pattern": "password reset"},
    {"label": "MITIGATION", "pattern": "network segmentation"}
]
ruler.add_patterns(patterns)
# --- نهاية كود القاموس ---

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
            
        # استخدمنا nlp(text) بدلاً من make_doc لتفعيل القاموس واستخراج الكيانات برمجياً
        full_doc = nlp(text)
        
        # 1. استخراج الكيانات التي وجدها القاموس المدمج
        dict_ents = list(full_doc.ents)
        
        # 2. استخراج الكيانات اليدوية من ملف JSON
        json_ents = []
        for annotation in entry['annotations']:
            for res in annotation['result']:
                if 'value' in res:
                    val = res['value']
                    start, end = val.get('start'), val.get('end')
                    labels = val.get('labels')
                    
                    if start is not None and end is not None and labels:
                        label_name = "".join(labels) if isinstance(labels, list) and len(labels) > 0 else str(labels)
                        span = full_doc.char_span(start, end, label=label_name, alignment_mode="contract")
                        if span is not None:
                            json_ents.append(span)
        
        # 3. الدمج الذكي بين القاموس والبيانات الأصلية (مع إزالة التداخل)
        try:
            combined_ents = dict_ents + json_ents
            full_doc.ents = spacy.util.filter_spans(combined_ents)
        except Exception:
            continue

        # تطبيق استراتيجية التقسيم (Cascade Splitting) بـ 25 كلمة
        max_tokens = 25
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
    print("--- بدء هندسة البيانات للأمن السيبراني (الدورة الثالثة - القاموس المدمج) ---")
    convert_to_spacy_format('train_cyber.json', 'train.spacy')
    convert_to_spacy_format('test_cyber.json', 'test.spacy')