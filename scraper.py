import requests
from bs4 import BeautifulSoup
import time

def scrape_page(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
            tag.extract()
        main = soup.find("main") or soup.find("article") or soup.find(class_="entry-content") or soup.body
        return main.get_text(separator=" ", strip=True) if main else ""
    except requests.exceptions.Timeout:
        print(f"Timeout: {url}")
        return ""
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""


def get_kusrc_data():
    # หน้าสำคัญทั้งหมดของคณะ แบ่งตาม category ชัดเจน
    pages = {
        # ข้อมูลทั่วไป
        "home":             "https://sci.src.ku.ac.th/",
        "general_info":     "https://sci.src.ku.ac.th/%e0%b8%82%e0%b9%89%e0%b8%ad%e0%b8%a1%e0%b8%b9%e0%b8%a5%e0%b8%97%e0%b8%b1%e0%b9%88%e0%b8%a7%e0%b9%84%e0%b8%9b%e0%b8%82%e0%b8%ad%e0%b8%87%e0%b8%84%e0%b8%93%e0%b8%b0/",
        "faq":              "https://sci.src.ku.ac.th/qa/",

        # หลักสูตร
        "curriculum":       "https://sci.src.ku.ac.th/en/program/",
        "cs_program":       "https://sci.src.ku.ac.th/program/computer-science/",
        "it_program":       "https://sci.src.ku.ac.th/program/information-technology/",
        "special_cs":       "https://sci.src.ku.ac.th/program/special-computer-science/",
        "special_it":       "https://sci.src.ku.ac.th/program/special-information-technology/",
        "special_digital":  "https://sci.src.ku.ac.th/program/special-digital-science-and-technology/",
        "env_program":      "https://sci.src.ku.ac.th/program/environmental-science/",

        # บุคลากร
        "dean":             "https://sci.src.ku.ac.th/%e0%b8%82%e0%b9%89%e0%b8%ad%e0%b8%a1%e0%b8%b9%e0%b8%a5%e0%b8%97%e0%b8%b1%e0%b9%88%e0%b8%a7%e0%b9%84%e0%b8%9b%e0%b8%82%e0%b8%ad%e0%b8%87%e0%b8%84%e0%b8%93%e0%b8%b0/%e0%b8%84%e0%b8%93%e0%b8%9a%e0%b8%94%e0%b8%b5%e0%b9%81%e0%b8%a5%e0%b8%b0%e0%b8%9c%e0%b8%b9%e0%b9%89%e0%b8%9a%e0%b8%a3%e0%b8%b4%e0%b8%ab%e0%b8%b2%e0%b8%a3/",
        "academic_staff":   "https://sci.src.ku.ac.th/%e0%b8%82%e0%b9%89%e0%b8%ad%e0%b8%a1%e0%b8%b9%e0%b8%a5%e0%b8%97%e0%b8%b1%e0%b9%88%e0%b8%a7%e0%b9%84%e0%b8%9b%e0%b8%82%e0%b8%ad%e0%b8%87%e0%b8%84%e0%b8%93%e0%b8%b0/%e0%b8%9a%e0%b8%b8%e0%b8%84%e0%b8%a5%e0%b8%b2%e0%b8%81%e0%b8%a3%e0%b8%a7%e0%b8%b4%e0%b8%8a%e0%b8%b2%e0%b8%81%e0%b8%b2%e0%b8%a3-2/",
        "support_staff":    "https://sci.src.ku.ac.th/%e0%b8%82%e0%b9%89%e0%b8%ad%e0%b8%a1%e0%b8%b9%e0%b8%a5%e0%b8%97%e0%b8%b1%e0%b9%88%e0%b8%a7%e0%b9%84%e0%b8%9b%e0%b8%82%e0%b8%ad%e0%b8%87%e0%b8%84%e0%b8%93%e0%b8%b0/%e0%b8%9a%e0%b8%b8%e0%b8%84%e0%b8%a5%e0%b8%b2%e0%b8%81%e0%b8%a3%e0%b8%aa%e0%b8%99%e0%b8%b1%e0%b8%9a%e0%b8%aa%e0%b8%99%e0%b8%b8%e0%b8%99/",
        "cs_staff":         "https://sci.src.ku.ac.th/department/computer-science/",
        "it_staff":         "https://sci.src.ku.ac.th/department/digital-science-and-technology/",
        "env_staff":        "https://sci.src.ku.ac.th/department/natural-product-science-technology/",
        "env_master_staff": "http://sci.src.ku.ac.th/department/natural-product-science-technology-master/",
        "digital_staff":    "https://sci.src.ku.ac.th/department/special-digital-science-and-technology/",

        # ค่าเทอม
        "cs_tuition":       "https://sci.src.ku.ac.th/program/computer-science/",
        "it_tuition":       "https://sci.src.ku.ac.th/program/information-technology/",
        "digital_tuition":  "https://sci.src.ku.ac.th/program/special-digital-science-and-technology/",

        # รางวัลและการจัดการความรู้
        "award":            "https://sci.src.ku.ac.th/%e0%b8%82%e0%b9%89%e0%b8%ad%e0%b8%a1%e0%b8%b9%e0%b8%a5%e0%b8%97%e0%b8%b1%e0%b9%88%e0%b8%a7%e0%b9%84%e0%b8%9b%e0%b8%82%e0%b8%ad%e0%b8%87%e0%b8%84%e0%b8%93%e0%b8%b0/award/",
        "km":               "https://sci.src.ku.ac.th/knowledgemanagement/",
        "dean_history":     "https://sci.src.ku.ac.th/%e0%b8%82%e0%b9%89%e0%b8%ad%e0%b8%a1%e0%b8%b9%e0%b8%a5%e0%b8%97%e0%b8%b1%e0%b9%88%e0%b8%a7%e0%b9%84%e0%b8%9b%e0%b8%82%e0%b8%ad%e0%b8%87%e0%b8%84%e0%b8%93%e0%b8%b0/%e0%b8%97%e0%b8%b3%e0%b9%80%e0%b8%99%e0%b8%b5%e0%b8%a2%e0%b8%9a%e0%b8%84%e0%b8%93%e0%b8%9a%e0%b8%94%e0%b8%b5/",
    }

    documents = []

    for category, url in pages.items():
        print(f"Scraping [{category}]: {url}")
        text = None

        for attempt in range(2):
            text = scrape_page(url)
            if text:
                break
            if attempt < 1:
                time.sleep(2)

        if text:
            documents.append({
                "content": text[:10000],
                "category": category,
                "source": url
            })
            print(f"  OK ({len(text)} chars)")
        else:
            print(f"  FAILED")

        time.sleep(1)

    print(f"\nTotal scraped: {len(documents)} pages")
    return documents


if __name__ == "__main__":
    data = get_kusrc_data()
    print(f"Done: {len(data)} documents")