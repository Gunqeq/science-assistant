"""
ตัวอย่างการใช้งานระบบทดสอบความแม่นยำ (Examples of Using Accuracy Test System)

ไฟล์นี้แสดงวิธีการใช้เครื่องมือต่างๆ ในการทดสอบและวัดความแม่นยำ
"""

from test_accuracy import (
    AccuracyTester, TestCase,
    calculate_similarity_score,
    check_keywords_in_response,
    detect_response_intent,
    calculate_response_quality
)


# ========================
# ตัวอย่างที่ 1: ทดสอบด้วยคำตอบจำลอง
# ========================

def example_1_mock_testing():
    """ทดสอบโดยใช้คำตอบจำลอง"""
    print("\n" + "="*80)
    print("ตัวอย่างที่ 1: ทดสอบด้วยคำตอบจำลอง")
    print("="*80)
    
    # สร้าง test case
    test_case = TestCase(
        test_id="TC_EX1",
        question="ค่าเทอมเท่าไหร่",
        expected_response="ค่าเทอมประมาณ 25,000 บาท/เทอม สามารถชำระเป็นงวดได้",
        required_keywords=["ค่าเทอม", "บาท", "เทอม"],
        category="Tuition & Fees"
    )
    
    # จำลองคำตอบจาก AI
    ai_response = "ค่าเทอมประมาณ 25,000 บาท ต่อเทอมครับ"
    
    # ประเมิน
    tester = AccuracyTester()
    result = tester.evaluate_response(test_case, ai_response)
    
    # แสดงผล
    print(f"\n📝 คำถาม: {result['question']}")
    print(f"🤖 คำตอบ: {result['actual_response']}")
    print(f"\n📊 ผลประเมิน:")
    print(f"  ├─ Similarity Score: {result['similarity_score']} ({result['similarity_score']*100:.1f}%)")
    print(f"  ├─ Keyword Match: {result['keyword_analysis']['match_percentage']}%")
    print(f"  ├─ Intent Score: {sum(result['intent_detection'].values())/len(result['intent_detection']):.2f}")
    print(f"  └─ Overall Accuracy: {result['overall_accuracy_percentage']}% ⭐")


# ========================
# ตัวอย่างที่ 2: ตรวจสอบคำสำคัญเท่านั้น
# ========================

def example_2_keyword_checking():
    """ตรวจสอบเฉพาะคำสำคัญ"""
    print("\n" + "="*80)
    print("ตัวอย่างที่ 2: ตรวจสอบคำสำคัญ")
    print("="*80)
    
    responses = [
        "ค่าเทอมประมาณ 25,000 บาท ต่อเทอม",
        "ค่าเทอมสั้นมากครับ",
        "ไม่ทราบข้อมูลเกี่ยวกับค่าเทอม",
    ]
    
    keywords = ["ค่าเทอม", "บาท", "เทอม"]
    
    for i, response in enumerate(responses, 1):
        result = check_keywords_in_response(response, keywords)
        print(f"\n📌 ตัวอย่างที่ {i}:")
        print(f"   คำตอบ: {response}")
        print(f"   ✓ คำสำคัญที่พบ: {result['found_keywords']}")
        print(f"   ✗ คำสำคัญที่ไม่พบ: {result['missing_keywords']}")
        print(f"   📊 ความสำเร็จ: {result['match_percentage']}%")


# ========================
# ตัวอย่างที่ 3: ตรวจสอบความเข้าใจประเด็น
# ========================

def example_3_intent_detection():
    """ตรวจสอบว่า AI เข้าใจคำถาม"""
    print("\n" + "="*80)
    print("ตัวอย่างที่ 3: ตรวจสอบความเข้าใจประเด็น")
    print("="*80)
    
    responses = [
        "ค่าเทอมประมาณ 25,000 บาท/เทอม สามารถชำระเป็นงวดได้",
        "ขออภัย ระบบไม่พบข้อมูลในส่วนนี้",
        "ฮ่ะ",
    ]
    
    labels = ["ตอบตรง", "ไม่มีข้อมูล", "ตอบไม่เหมาะสม"]
    
    for response, label in zip(responses, labels):
        intent = detect_response_intent(response)
        print(f"\n📌 {label}:")
        print(f"   คำตอบ: {response}")
        print(f"   ✓ มีเนื้อหา: {intent['provides_direct_answer']}")
        print(f"   ✓ ใช้ Bullet points: {intent['uses_bullet_points']}")
        print(f"   ✓ ใช้ภาษาไทย: {intent['uses_thai_language']}")
        print(f"   ✓ สุภาพ: {intent['is_polite']}")
        print(f"   ✓ ยอมรับไม่มีข้อมูล: {intent['acknowledges_no_data']}")


# ========================
# ตัวอย่างที่ 4: วัดคุณภาพการตอบ
# ========================

def example_4_quality_metrics():
    """วัดคุณภาพ"""
    print("\n" + "="*80)
    print("ตัวอย่างที่ 4: วัดคุณภาพการตอบ")
    print("="*80)
    
    responses = [
        "ใช่",  # สั้นเกินไป
        "ค่าเทอมประมาณ 25,000 บาท/เทอม",  # เหมาะสม
        " ".join(["ค่าเทอม"] * 300),  # ยาวเกินไป
    ]
    
    labels = ["สั้นเกินไป ❌", "เหมาะสม ✓", "ยาวเกินไป ❌"]
    
    for response, label in zip(responses, labels):
        quality = calculate_response_quality(response)
        print(f"\n📌 {label}")
        print(f"   Word count: {quality['word_count']}")
        print(f"   Character count: {quality['char_count']}")
        print(f"   Length score: {quality['length_score']}")
        print(f"   Is concise: {quality['is_concise']}")


# ========================
# ตัวอย่างที่ 5: เปรียบเทียบความเหมือน
# ========================

def example_5_similarity_comparison():
    """เปรียบเทียบความเหมือนระหว่างข้อความ"""
    print("\n" + "="*80)
    print("ตัวอย่างที่ 5: เปรียบเทียบความเหมือน")
    print("="*80)
    
    pairs = [
        ("ค่าเทอมประมาณ 25,000 บาท", "ค่าเทอมประมาณ 25,000 บาท"),  # เหมือน 100%
        ("ค่าเทอมประมาณ 25,000 บาท", "ค่าเทอมประมาณ 25,000 บาท/เทอม"),  # คล้ายกัน
        ("สวัสดี", "ค่าเทอมประมาณ 25,000 บาท"),  # ต่างกันโดยสิ้นเชิง
    ]
    
    for response, expected in pairs:
        score = calculate_similarity_score(response, expected)
        bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
        
        print(f"\n📌 คำตอบที่ได้: {response}")
        print(f"   ที่คาดหวัง:   {expected}")
        print(f"   คะแนน: {score:.2f} (100%)")
        print(f"   [{bar}] {score*100:.1f}%")


# ========================
# ตัวอย่างที่ 6: สร้างรายงานสรุป
# ========================

def example_6_generate_report():
    """สร้างรายงานสรุป"""
    print("\n" + "="*80)
    print("ตัวอย่างที่ 6: สร้างรายงานสรุป")
    print("="*80)
    
    # จำลองผลลัพธ์จากการทดสอบหลายๆ กรณี
    sample_results = [
        {'test_id': 'TC001', 'category': 'Tuition & Fees', 'overall_accuracy_percentage': 85},
        {'test_id': 'TC002', 'category': 'Scholarships', 'overall_accuracy_percentage': 92},
        {'test_id': 'TC003', 'category': 'Tuition & Fees', 'overall_accuracy_percentage': 78},
        {'test_id': 'TC004', 'category': 'Admission', 'overall_accuracy_percentage': 88},
        {'test_id': 'TC005', 'category': 'Scholarships', 'overall_accuracy_percentage': 95},
    ]
    
    tester = AccuracyTester()
    report = tester.generate_report(sample_results)
    
    print(f"\n📊 สรุปผลการทดสอบ:")
    print(f"  ├─ ทดสอบทั้งหมด: {report['total_tests']} กรณี")
    print(f"  ├─ ความแม่นยำเฉลี่ย: {report['overall_average_accuracy']}%")
    print(f"  ├─ ผ่านการทดสอบ: {report['passed_tests']}/{report['total_tests']} ({report['overall_pass_rate']}%)")
    print(f"  └─ ไม่ผ่าน: {report['failed_tests']}/{report['total_tests']}\n")
    
    print(f"📈 สถิติตามหมวดหมู่:")
    for category, stats in report['category_statistics'].items():
        print(f"  ├─ {category}:")
        print(f"  │  ├─ จำนวน: {stats['count']} กรณี")
        print(f"  │  ├─ ความแม่นยำเฉลี่ย: {stats['average_accuracy']}%")
        print(f"  │  └─ ผ่านการทดสอบ: {stats['pass_rate']}%")


# ========================
# ตัวอย่างที่ 7: ทดสอบหลายกรณีพร้อมกัน
# ========================

def example_7_batch_testing():
    """ทดสอบหลายกรณีพร้อมกัน"""
    print("\n" + "="*80)
    print("ตัวอย่างที่ 7: ทดสอบหลายกรณีพร้อมกัน")
    print("="*80)
    
    # สร้าง test cases
    test_cases = [
        TestCase(
            test_id="TC_EX7_1",
            question="ค่าเทอมเท่าไหร่",
            expected_response="ค่าเทอมประมาณ 25,000 บาท/เทอม",
            required_keywords=["ค่าเทอม", "บาท"],
            category="Tuition"
        ),
        TestCase(
            test_id="TC_EX7_2",
            question="มีทุนไหม",
            expected_response="มีทุนการศึกษาสำหรับนักศึกษา",
            required_keywords=["ทุน"],
            category="Scholarships"
        ),
        TestCase(
            test_id="TC_EX7_3",
            question="ลงทะเบียนเรียนยังไง",
            expected_response="ลงทะเบียนผ่านระบบมหาวิทยาลัย",
            required_keywords=["ลงทะเบียน", "ระบบ"],
            category="Study System"
        ),
    ]
    
    # จำลองคำตอบ
    mock_responses = [
        "ค่าเทอมประมาณ 25,000 บาท ต่อเทอมครับ",
        "ขออภัยไม่มีข้อมูล",
        "ลงทะเบียนผ่านระบบมหาวิทยาลัยในช่วงที่กำหนด",
    ]
    
    tester = AccuracyTester()
    
    print()
    results = []
    for test_case, response in zip(test_cases, mock_responses):
        result = tester.evaluate_response(test_case, response)
        results.append(result)
        
        # แสดงแต่ละผลลัพธ์
        status = "✓ ผ่าน" if result['overall_accuracy_percentage'] >= 80 else "✗ ไม่ผ่าน"
        print(f"[{result['test_id']}] {result['category']} - {status}")
        print(f"  คำถาม: {result['question']}")
        print(f"  ความแม่นยำ: {result['overall_accuracy_percentage']}%\n")
    
    # สร้างรายงาน
    report = tester.generate_report(results)
    print(f"\n📊 สรุป: ความแม่นยำเฉลี่ย {report['overall_average_accuracy']}% " +
          f"(ผ่าน {report['overall_pass_rate']}%)")


# ========================
# MAIN
# ========================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("= ตัวอย่างการใช้งานระบบทดสอบความแม่นยำ (Test Accuracy Examples)")
    print("="*80)
    
    # รันตัวอย่างทั้งหมด
    example_1_mock_testing()
    example_2_keyword_checking()
    example_3_intent_detection()
    example_4_quality_metrics()
    example_5_similarity_comparison()
    example_6_generate_report()
    example_7_batch_testing()
    
    print("\n" + "="*80)
    print("= เสร็จสิ้นการรันตัวอย่างทั้งหมด")
    print("="*80 + "\n")
