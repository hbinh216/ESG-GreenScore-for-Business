import json
import time
import os
import sys
import re
from typing import Dict, List, Any

# --- CẤU HÌNH THƯ VIỆN ---
try:
    import PyPDF2
    import google.generativeai as genai
except ImportError:
    print("❌ THIẾU THƯ VIỆN!")
    print("👉 Chạy lệnh này: pip install PyPDF2 google-generativeai")
    sys.exit(1)

# --- CẤU HÌNH HỆ THỐNG ---
ESG_CONFIG = {
    "pillars": {
        "E": {"weight": 0.35, "name": "Environmental"},
        "S": {"weight": 0.35, "name": "Social"},
        "G": {"weight": 0.30, "name": "Governance"}
    },
    "metrics": {
        "E1": {"name": "Phát thải GHG", "pillar": "E", "weight": 0.40, "mandatory": True},
        "E2": {"name": "Năng lượng", "pillar": "E", "weight": 0.20, "mandatory": False},
        "E3": {"name": "Quản lý Nước", "pillar": "E", "weight": 0.15, "mandatory": False},
        "E4": {"name": "Chất thải", "pillar": "E", "weight": 0.15, "mandatory": False},
        "E5": {"name": "Chứng chỉ Xanh", "pillar": "E", "weight": 0.10, "mandatory": False},
        "S1": {"name": "An toàn lao động", "pillar": "S", "weight": 0.30, "mandatory": False},
        "S2": {"name": "Đa dạng giới", "pillar": "S", "weight": 0.20, "mandatory": False},
        "S3": {"name": "Đào tạo", "pillar": "S", "weight": 0.20, "mandatory": False},
        "S4": {"name": "Chuỗi cung ứng", "pillar": "S", "weight": 0.15, "mandatory": False},
        "S5": {"name": "Cộng đồng", "pillar": "S", "weight": 0.15, "mandatory": False},
        "G1": {"name": "Độc lập HĐQT", "pillar": "G", "weight": 0.40, "mandatory": False},
        "G2": {"name": "Đạo đức kinh doanh", "pillar": "G", "weight": 0.30, "mandatory": True},
        "G3": {"name": "Minh bạch thuế", "pillar": "G", "weight": 0.15, "mandatory": False},
        "G4": {"name": "Bảo mật dữ liệu", "pillar": "G", "weight": 0.15, "mandatory": False}
    }
}


class GreenScoreAgent:
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        # Model Gemini 2.5 Flash
        self.model_name = "gemini-2.5-flash"

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Đọc toàn bộ file PDF"""
        if not os.path.exists(pdf_path):
            print(f"❌ LỖI: Không tìm thấy file tại {pdf_path}")
            sys.exit(1)

        print(f"📄 Đang đọc file: {os.path.basename(pdf_path)}...")
        text = ""
        try:
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += (page.extract_text() or "") + "\n"
            print(f"✅ Đã đọc xong {len(text)} ký tự.")
            return text
        except Exception as e:
            print(f"❌ Lỗi đọc PDF: {e}")
            sys.exit(1)

    def collect_data_with_ai(self, report_content: str) -> str:
        """Gửi dữ liệu cho AI phân tích"""
        print(f"🚀 Đang gửi dữ liệu tới {self.model_name}...")

        # Tạo danh sách chỉ số để nhắc AI
        metrics_list = "\n".join([f"- {k}: {v['name']}" for k, v in ESG_CONFIG['metrics'].items()])

        prompt = f"""
        Bạn là chuyên gia kiểm toán ESG. Hãy đọc báo cáo và chấm điểm định lượng (0-100) cho từng chỉ số.

        DANH SÁCH CHỈ SỐ CẦN CHẤM:
        {metrics_list}

        YÊU CẦU OUTPUT QUAN TRỌNG:
        Trả về đúng định dạng JSON này (không markdown, không giải thích):
        {{
            "scores": {{
                "E1": <điểm>, "E2": <điểm>, "E3": <điểm>, "E4": <điểm>, "E5": <điểm>,
                "S1": <điểm>, "S2": <điểm>, "S3": <điểm>, "S4": <điểm>, "S5": <điểm>,
                "G1": <điểm>, "G2": <điểm>, "G3": <điểm>, "G4": <điểm>
            }},
            "insights": {{
                "E": "Nhận xét E", "S": "Nhận xét S", "G": "Nhận xét G"
            }},
            "flags": ["Cảnh báo rủi ro"]
        }}

        DỮ LIỆU BÁO CÁO:
        {report_content}
        """

        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={"response_mime_type": "application/json", "temperature": 0.1}
            )
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"❌ Lỗi AI: {e}")
            sys.exit(1)

    def process_final_report(self, ai_output_json: str) -> Dict[str, Any]:
        """Xử lý kết quả trả về"""
        try:
            data = json.loads(ai_output_json)
        except:
            data = {"scores": {}, "flags": ["Lỗi JSON"]}

        raw_scores = data.get("scores", {})
        pillar_results = {}
        final_flags = data.get("flags", [])
        is_gold_locked = False

        # Tính điểm
        for p_code, p_info in ESG_CONFIG['pillars'].items():
            p_metrics = {k: v for k, v in ESG_CONFIG['metrics'].items() if v['pillar'] == p_code}
            weighted_sum = 0.0
            available_weight = 0.0

            for m_code, m_info in p_metrics.items():
                val = raw_scores.get(m_code, 0)
                if val > 0:
                    weighted_sum += (val * m_info['weight'])
                    available_weight += m_info['weight']
                elif m_info['mandatory']:
                    is_gold_locked = True
                    if f"Thiếu {m_code}" not in final_flags: final_flags.append(f"Thiếu chỉ số bắt buộc: {m_code}")

            p_score = (weighted_sum / available_weight) if available_weight > 0 else 0
            if any(m['mandatory'] and raw_scores.get(k, 0) == 0 for k, m in p_metrics.items()):
                p_score *= 0.5
            pillar_results[p_code] = round(p_score, 2)

        total_score = round(sum(pillar_results[p] * ESG_CONFIG['pillars'][p]['weight'] for p in pillar_results), 2)

        rank = "UNRANKED"
        if total_score >= 80 and not is_gold_locked:
            rank = "GOLD"
        elif total_score >= 55:
            rank = "SILVER"
        elif total_score >= 35:
            rank = "BRONZE"

        return {
            "metadata": {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S")},
            "evaluation": {
                "final_score": total_score,
                "rank": rank,
                "pillar_scores": pillar_results
            },
            # PHẦN QUAN TRỌNG: Hiển thị chi tiết điểm thành phần
            "detailed_scores": raw_scores,
            "analysis": {
                "insights": data.get("insights", {}),
                "flags": final_flags
            }
        }


if __name__ == "__main__":
    print("=" * 60)
    print("🌱 GREENSCORE AI AGENT - FULL DETAIL VERSION")
    print("=" * 60)

    # 1. API KEY
    MY_API_KEY = "AIzaSyAo-vCLFA26xbjHOUvUDe94PxEb80qE9z0"

    # 2. FILE PDF
    PDF_FILE = r"D:/OneDrive - uel.edu.vn/HocTap_UEL/Cuoc_thi_hoc_thuat/ESG/ESG-GreenScore-for-Business/hpg.pdf"

    agent = GreenScoreAgent(api_key=MY_API_KEY)

    # Chạy
    content = agent.extract_text_from_pdf(PDF_FILE)
    json_ai = agent.collect_data_with_ai(content)
    final_report = agent.process_final_report(json_ai)

    # In kết quả
    print("\n" + "═" * 60)
    print("🎯 KẾT QUẢ ĐÁNH GIÁ CHI TIẾT")
    print("═" * 60)
    print(json.dumps(final_report, indent=4, ensure_ascii=False))

    # Lưu file
    with open("ket_qua_full.json", "w", encoding="utf-8") as f:
        json.dump(final_report, f, indent=4, ensure_ascii=False)
    print(f"\n💾 Đã lưu kết quả chi tiết vào file: ket_qua_full.json")