# ESG-GreenScore-for-Business
[Doanh nghiệp] → Upload dữ liệu/báo cáo
                        ↓
                  [AI Agent] → Phân tích & đánh giá E-S-G
                        ↓
              [Smart Contract] → Ghi điểm + Hash báo cáo
                        ↓
                   [Blockchain] → Lưu trữ bất biến
                        ↓
   	  [Dashboard] ← Tra cứu & Xem khuyến nghị cải thiện

# 🌱 GreenScore AI Agent - Enhanced Version

## 📋 Tổng quan

Hệ thống đánh giá ESG (Environmental, Social, Governance) tự động sử dụng AI và nhiều công cụ phân tích chuyên sâu.

### ✨ Tính năng nổi bật

1. **Multi-Source Data Collection** - Thu thập dữ liệu từ nhiều nguồn
2. **AI-Powered Scoring** - Chấm điểm tự động với Gemini AI
3. **Sentiment Analysis** - Phân tích cảm xúc ESG từ văn bản
4. **Industry Benchmark** - So sánh với trung bình ngành
5. **Risk Detection** - Phát hiện rủi ro ESG tự động
6. **Comprehensive Reporting** - Báo cáo chi tiết đa chiều

---

## 📁 Cấu trúc Project

```
.
├── esg_tools.py           # 4 tools phân tích ESG
├── main_enhanced.py       # Main script với workflow đầy đủ
├── README.md              # File này
└── requirements.txt       # Dependencies
```

---

## 🚀 Cài đặt

### Bước 1: Cài đặt thư viện

```bash
pip install PyPDF2 google-generativeai requests
```

### Bước 2: Lấy API Key

1. Truy cập: https://aistudio.google.com/app/apikey
2. Tạo API key mới
3. Copy và paste vào `main_enhanced.py` dòng 257

---

## 🛠️ Các Tools Available

### 1. **ESGDataCollector** 
Thu thập dữ liệu từ Yahoo Finance và news sources

**Chức năng:**
- `get_yahoo_esg_data(ticker)` - Lấy ESG score có sẵn từ Yahoo Finance
- `search_esg_news(company_name)` - Tìm tin tức ESG liên quan

**Ví dụ:**
```python
from esg_tools import ESGDataCollector

collector = ESGDataCollector()
data = collector.get_yahoo_esg_data("AAPL")
print(data)
```

### 2. **ESGTextAnalyzer**
Phân tích sentiment và trích xuất metrics từ văn bản

**Chức năng:**
- `analyze_text_sentiment(text)` - Phân loại E/S/G và tính sentiment score
- `extract_esg_metrics_from_text(text)` - Trích xuất số liệu định lượng

**Ví dụ:**
```python
from esg_tools import ESGTextAnalyzer

analyzer = ESGTextAnalyzer()
result = analyzer.analyze_text_sentiment("""
    Company committed to net zero by 2030 and improved diversity.
""")
print(result['pillar_scores'])
```

### 3. **ESGBenchmarkTool**
So sánh với benchmark theo ngành

**Chức năng:**
- `compare_with_benchmark(scores, industry)` - So sánh điểm với trung bình ngành

**Ví dụ:**
```python
from esg_tools import ESGBenchmarkTool

benchmark = ESGBenchmarkTool()
comparison = benchmark.compare_with_benchmark(
    {"E": 72, "S": 65, "G": 80},
    "technology"
)
print(comparison['recommendations'])
```

### 4. **ESGRiskDetector**
Phát hiện rủi ro từ văn bản và dữ liệu

**Chức năng:**
- `detect_risks(text, company_data)` - Quét và phân loại rủi ro

**Ví dụ:**
```python
from esg_tools import ESGRiskDetector

risk_tool = ESGRiskDetector()
risks = risk_tool.detect_risks(
    "Company faces environmental violation lawsuit",
    {"pillar_scores": {"E": 35, "S": 50, "G": 60}}
)
print(risks['overall_risk_level'])
```

---

## 📖 Hướng dẫn sử dụng Main Script

### Cấu hình cơ bản

Mở file `main_enhanced.py` và chỉnh sửa:

```python
# Dòng 257-260
MY_API_KEY = "YOUR_GEMINI_API_KEY"  # ⚠️ BẮT BUỘC
PDF_FILE = r"path/to/your/esg_report.pdf"  # Đường dẫn file PDF

# Dòng 263-265 (Optional)
COMPANY_TICKER = "AAPL"  # Mã CK (nếu có)
COMPANY_NAME = "Apple Inc"  # Tên công ty
INDUSTRY = "technology"  # Ngành: technology, finance, manufacturing, retail, energy, healthcare
```

### Chạy chương trình

```bash
python main_enhanced.py
```

### Output

Script sẽ tạo ra:

1. **Console output** - Hiển thị progress và kết quả
2. **JSON file** - `esg_report_enhanced_YYYYMMDD_HHMMSS.json`

---

## 📊 Cấu trúc Output JSON

```json
{
  "metadata": {
    "timestamp": "2025-01-10 14:30:00",
    "industry": "manufacturing",
    "model_used": "gemini-2.0-flash-exp"
  },
  "evaluation": {
    "final_score": 67.5,
    "rank": "SILVER",
    "pillar_scores": {
      "E": 65.2,
      "S": 72.3,
      "G": 64.8
    }
  },
  "detailed_scores": {
    "E1": 70, "E2": 65, "E3": 60, ...
  },
  "analysis": {
    "insights": {
      "E": "Strong renewable energy commitment",
      "S": "Good diversity but labor issues",
      "G": "Board independence needs improvement"
    },
    "highlights": [...],
    "improvement_areas": [...],
    "flags": [...]
  },
  "benchmark_comparison": {
    "industry": "manufacturing",
    "total_score": {
      "company": 67.5,
      "benchmark": 62.0,
      "difference": +5.5
    },
    "recommendations": [...]
  },
  "risk_assessment": {
    "overall_risk_level": "MEDIUM",
    "high_risks": [...],
    "medium_risks": [...],
    "priority_actions": [...]
  },
  "sentiment_analysis": {
    "overall_sentiment": "positive",
    "pillar_scores": {...}
  }
}
```

---

## 🔧 Tùy chỉnh nâng cao

### 1. Thêm ngành mới vào Benchmark

Mở `esg_tools.py`, tìm dòng 156:

```python
self.industry_benchmarks = {
    "technology": {"E": 65, "S": 70, "G": 75},
    "your_industry": {"E": 60, "S": 65, "G": 70},  # Thêm dòng này
    ...
}
```

### 2. Điều chỉnh trọng số chỉ số

Mở `main_enhanced.py`, tìm dòng 30:

```python
"E1": {"name": "Phát thải GHG", "pillar": "E", "weight": 0.40, "mandatory": True},
# Thay đổi weight từ 0.40 thành giá trị khác
```

### 3. Thêm keywords cho Sentiment Analysis

Mở `esg_tools.py`, tìm dòng 95:

```python
self.esg_keywords = {
    "E": {
        "positive": [
            "renewable energy",
            "your_keyword_here",  # Thêm keyword
            ...
        ]
    }
}
```

---

## ⚠️ Lưu ý quan trọng

### Yahoo Finance Data
- **Chỉ có sẵn cho các công ty lớn** (Apple, Microsoft, etc.)
- **Không có cho hầu hết công ty Việt Nam**
- Nếu không có data, tool sẽ trả về `available: false`

### API Rate Limits
- Gemini API có giới hạn requests/phút
- Nếu gặp lỗi 429, đợi vài phút rồi thử lại

### PDF Format
- PDF phải là dạng text (không phải ảnh scan)
- File nên < 50MB để tránh timeout

---

## 🧪 Test từng Tool riêng lẻ

```bash
# Test tất cả tools
python esg_tools.py
```

Output sẽ hiển thị demo cho cả 4 tools.

---

## 📈 Workflow hoàn chỉnh

```
1. Đọc PDF
   ↓
2. Thu thập dữ liệu bên ngoài (Yahoo Finance, News)
   ↓
3. Phân tích sentiment từ văn bản
   ↓
4. Chấm điểm với AI (Gemini)
   ↓
5. So sánh với benchmark ngành
   ↓
6. Phát hiện rủi ro
   ↓
7. Tổng hợp báo cáo JSON
```

---

## 🤝 Contributing

Để thêm tool mới:

1. Tạo class trong `esg_tools.py`
2. Thêm vào function `get_all_tools()`
3. Import và sử dụng trong `main_enhanced.py`

---

## 📞 Support

Nếu gặp lỗi, kiểm tra:

1. ✅ API key đã đúng chưa?
2. ✅ File PDF có tồn tại không?
3. ✅ Đã cài đủ thư viện chưa?
4. ✅ Internet connection ổn định?

---

## 📄 License

MIT License - Free to use and modify

---

**Phát triển bởi:** GreenScore Team  
**Phiên bản:** 2.0 Enhanced  
**Cập nhật:** 2025-01-10