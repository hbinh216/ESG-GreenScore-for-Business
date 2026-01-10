# esg_tools.py
import os
import re
import json
import requests
import yfinance as yf
import PyPDF2
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional

# --- (1) Tool: đọc PDF ---
import os
import glob
import PyPDF2

def extract_text_from_pdf(path: str) -> str:
    """
    Cho phép nhập:
    - đường dẫn file .pdf
    - hoặc thư mục chứa pdf (tự chọn file pdf mới nhất)
    """
    path = path.strip('"').strip()

    # Nếu là thư mục -> tìm pdf
    if os.path.isdir(path):
        pdfs = sorted(
            glob.glob(os.path.join(path, "*.pdf")),
            key=os.path.getmtime,
            reverse=True
        )
        if not pdfs:
            raise FileNotFoundError(f"Không tìm thấy file PDF trong thư mục: {path}")
        path = pdfs[0]  # lấy file mới nhất

    # Nếu không phải file tồn tại
    if not os.path.exists(path):
        raise FileNotFoundError(f"Không tìm thấy file: {path}")

    # Nếu không phải pdf
    if not path.lower().endswith(".pdf"):
        raise ValueError(f"File không phải PDF: {path}")

    text = ""
    with open(path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"
    return text

# --- (2) Tool: hard data từ yfinance ---
def get_basic_esg_data(ticker: str) -> str:
    """
    Lấy dữ liệu ESG cơ bản từ Yahoo Finance nếu có.
    """
    stock = yf.Ticker(ticker)
    try:
        esg_data = getattr(stock, "sustainability", None)
        if esg_data is None:
            return "Không tìm thấy dữ liệu ESG có sẵn trên Yahoo Finance."
        return esg_data.to_string()
    except Exception as e:
        return f"Lỗi yfinance: {str(e)}"


from typing import List, Dict
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json


def google_search_cse(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    """
    Tìm Google qua Custom Search JSON API.
    - Đã hardcode API key & CSE ID
    - Có debug lỗi 403 chi tiết
    - Có fallback để không làm crash pipeline
    """

    # 🔴 API KEY & CSE ID (đúng cái bạn đang dùng)
    api_key = "AIzaSyCfTpSXdC3LfX-CIlHscAL8NRzWyAaknlI"
    cse_id  = "f762af7348cde4afd"

    if not api_key or not cse_id:
        raise EnvironmentError("Thiếu GOOGLE_CSE_API_KEY hoặc GOOGLE_CSE_ID.")

    try:
        service = build(
            "customsearch",
            "v1",
            developerKey=api_key,
            cache_discovery=False  # tránh lỗi cache lặt vặt trên Windows
        )

        res = service.cse().list(
            q=query,
            cx=cse_id,
            num=min(num_results, 10)
        ).execute()

        items = res.get("items", [])
        return [
            {
                "title": it.get("title", ""),
                "link": it.get("link", ""),
                "snippet": it.get("snippet", "")
            }
            for it in items
        ]

    except HttpError as e:
        # 🔎 In lỗi CHI TIẾT từ Google (rất quan trọng)
        print("❌ Google CSE HttpError")
        try:
            error_detail = json.loads(e.content.decode("utf-8"))
            print(json.dumps(error_detail, indent=2, ensure_ascii=False))
        except Exception:
            print(str(e))

        # ⛑️ Fallback: không cho pipeline chết
        return []

    except Exception as e:
        print("❌ Lỗi không xác định khi gọi Google CSE:", str(e))
        return []





# --- (4) Tool: lấy nội dung bài báo (webpage -> text) ---
def fetch_url_text(url: str, timeout: int = 15) -> str:
    """
    Lấy text thô từ URL (tin tức/press release). (Có thể fail nếu trang chặn bot)
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    # bỏ script/style
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator=" ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


# --- (5) Tool: Soft data classifier (FinBERT-ESG) ---
class FinBertESGTool:
    """
    Load 1 lần để dùng lại (đỡ chậm).
    """
    def __init__(self, model_name: str = "yiyanghkust/finbert-esg"):
        from transformers import pipeline
        self.classifier = pipeline("text-classification", model=model_name)

    def analyze(self, text: str) -> Any:
        snippet = text[:512]
        return self.classifier(snippet)


# --- (6) Tool: gom soft data từ Google Search -> fetch -> FinBERT ---
def collect_esg_news_signals(
    company_name: str,
    finbert_tool: FinBertESGTool,
    num_articles: int = 5
) -> Dict[str, Any]:
    """
    Tìm tin tức liên quan ESG + phân loại nhanh theo FinBERT-ESG.
    """
    query = f'{company_name} ESG controversy OR scandal OR labor OR emissions OR bribery OR data breach'
    results = google_search_cse(query, num_results=num_articles)

    analyzed = []
    for r in results:
        url = r["link"]
        try:
            page_text = fetch_url_text(url)
            pred = finbert_tool.analyze(page_text)
            analyzed.append({
                "title": r["title"],
                "link": url,
                "snippet": r["snippet"],
                "finbert_esg": pred
            })
        except Exception as e:
            analyzed.append({
                "title": r["title"],
                "link": url,
                "snippet": r["snippet"],
                "finbert_esg": None,
                "error": str(e)
            })

    return {
        "query": query,
        "results": analyzed
    }
