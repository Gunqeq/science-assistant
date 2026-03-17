import requests
from bs4 import BeautifulSoup
import time

def scrape_page(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # เพิ่ม timeout เป็น 20 วินาที และเพิ่ม retries
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        return soup.get_text(separator=" ", strip=True)
    except requests.exceptions.Timeout:
        print(f"Timeout scraping {url}: Request took too long")
        return ""
    except requests.exceptions.ConnectionError:
        print(f"Connection error scraping {url}: Cannot connect to server")
        return ""
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""

def get_kusrc_data():
    pages = {
        "about": "https://sci.src.ku.ac.th/", #หน้าหลักคณะวิทยาศาสตร์
        "curriculum": "https://sci.src.ku.ac.th/en/program/", #หลักสูตร
        "faq": "https://sci.src.ku.ac.th/qa/", #คำถามที่พบบ่อย
        "cs_tuition": "https://sci.src.ku.ac.th/program/computer-science/", #วิทยาการคอมพิวเตอร์ ค่าเทอม
        "general_info": "https://sci.src.ku.ac.th/%e0%b8%82%e0%b9%89%e0%b8%ad%e0%b8%a1%e0%b8%b9%e0%b8%a5%e0%b8%97%e0%b8%b1%e0%b9%88%e0%b8%a7%e0%b9%84%e0%b8%9b%e0%b8%82%e0%b8%ad%e0%b8%87%e0%b8%84%e0%b8%93%e0%b8%b0/", #ข้อมูลทั่วไปของคณะ
        "dean_directory": "https://sci.src.ku.ac.th/%e0%b8%82%e0%b9%89%e0%b8%ad%e0%b8%a1%e0%b8%b9%e0%b8%a5%e0%b8%97%e0%b8%b1%e0%b9%88%e0%b8%a7%e0%b9%84%e0%b8%9b%e0%b8%82%e0%b8%ad%e0%b8%87%e0%b8%84%e0%b8%93%e0%b8%b0/%e0%b8%97%e0%b8%b3%e0%b9%80%e0%b8%99%e0%b8%b5%e0%b8%a2%e0%b8%9a%e0%b8%84%e0%b8%93%e0%b8%9a%e0%b8%94%e0%b8%b5/", #ทำเนียบคณบดี
        "manufacturers": "https://sci.src.ku.ac.th/%e0%b8%82%e0%b9%89%e0%b8%ad%e0%b8%a1%e0%b8%b9%e0%b8%a5%e0%b8%97%e0%b8%b1%e0%b9%88%e0%b8%a7%e0%b9%84%e0%b8%9b%e0%b8%82%e0%b8%ad%e0%b8%87%e0%b8%84%e0%b8%93%e0%b8%b0/%e0%b8%84%e0%b8%93%e0%b8%9a%e0%b8%94%e0%b8%b5%e0%b9%81%e0%b8%a5%e0%b8%b0%e0%b8%9c%e0%b8%b9%e0%b9%89%e0%b8%9a%e0%b8%a3%e0%b8%b4%e0%b8%ab%e0%b8%b2%e0%b8%a3/", #คณบดีและผู้บริหาร
        "support_staff": "https://sci.src.ku.ac.th/%e0%b8%82%e0%b9%89%e0%b8%ad%e0%b8%a1%e0%b8%b9%e0%b8%a5%e0%b8%97%e0%b8%b1%e0%b9%88%e0%b8%a7%e0%b9%84%e0%b8%9b%e0%b8%82%e0%b8%ad%e0%b8%87%e0%b8%84%e0%b8%93%e0%b8%b0/%e0%b8%9a%e0%b8%b8%e0%b8%84%e0%b8%a5%e0%b8%b2%e0%b8%81%e0%b8%a3%e0%b8%aa%e0%b8%99%e0%b8%b1%e0%b8%9a%e0%b8%aa%e0%b8%99%e0%b8%b8%e0%b8%99/", #บุคลากรสนับสนุน
        "award": "https://sci.src.ku.ac.th/%e0%b8%82%e0%b9%89%e0%b8%ad%e0%b8%a1%e0%b8%b9%e0%b8%a5%e0%b8%97%e0%b8%b1%e0%b9%88%e0%b8%a7%e0%b9%84%e0%b8%9b%e0%b8%82%e0%b8%ad%e0%b8%87%e0%b8%84%e0%b8%93%e0%b8%b0/award/", #รางวัล
        "km": "https://sci.src.ku.ac.th/knowledgemanagement/", #การจัดการความรู้
        "academic_staff": "https://sci.src.ku.ac.th/%e0%b8%82%e0%b9%89%e0%b8%ad%e0%b8%a1%e0%b8%b9%e0%b8%a5%e0%b8%97%e0%b8%b1%e0%b9%88%e0%b8%a7%e0%b9%84%e0%b8%9b%e0%b8%82%e0%b8%ad%e0%b8%87%e0%b8%84%e0%b8%93%e0%b8%b0/%e0%b8%9a%e0%b8%b8%e0%b8%84%e0%b8%a5%e0%b8%b2%e0%b8%81%e0%b8%a3%e0%b8%a7%e0%b8%b4%e0%b8%8a%e0%b8%b2%e0%b8%81%e0%b8%b2%e0%b8%a3-2/", #บุคลากรวิชาการ
        "cs_staff": "https://sci.src.ku.ac.th/department/computer-science/", #บุคลากร ComSci
        "it_staff": "https://sci.src.ku.ac.th/department/digital-science-and-technology/", #บุคลากร IT
        "env_sci_staff": "https://sci.src.ku.ac.th/department/natural-product-science-technology/", #บุคลากรวิทยาศาสตร์และเทคโนโลยีสิ่งแวดล้อม
        "env_sci_master": "http://sci.src.ku.ac.th/department/natural-product-science-technology-master/", #บุคลากรวิทยาศาสตร์และเทคโนโลยีผลิตภัณฑ์ธรรมชาติ (ป.โท)
        "special_cs": "https://sci.src.ku.ac.th/program/special-computer-science/", #หลักสูตรวิทยาการคอมพิวเตอร์ (หลักสูตรพิเศษ)
        "special_it": "https://sci.src.ku.ac.th/program/special-information-technology/", #หลักสูตรเทคโนโลยีสารสนเทศ (หลักสูตรพิเศษ)
        "special_digital": "https://sci.src.ku.ac.th/program/special-digital-science-and-technology/", #หลักสูตรดิจิทัลไซน์และเทคโนโลยี (หลักสูตรพิเศษ)
    }
    
    documents = []
    
    for category, url in pages.items():
        # ลอง scrape พร้อมกับ retry ถ้า fail
        text = None
        for attempt in range(2):  # ลอง 2 ครั้ง
            text = scrape_page(url)
            if text:
                break
            if attempt < 1:  # ถ้าลองครั้ง 1 ล้มเหลว ลองใหม่
                time.sleep(2)
        
        if text:
            documents.append({
                "content": text[:10000], # Limit content length potentially
                "category": category,
                "source": url
            })
        time.sleep(1) # Delay between requests to be polite
            
    return documents