import json
import time
import requests
import io
import re
import os
from typing import Dict, List, Any

try:
    import PyPDF2
except ImportError:
    print("Vui lòng cài đặt PyPDF2: pip install PyPDF2")

# --- CẤU HÌNH HỆ THỐNG THEO TÀI LIỆU THIẾT KẾ ---
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
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        # Groq API endpoint và models
        self.base_url = "https://api.groq.com/openai/v1"
        # Models hiện tại còn hoạt động (tháng 1/2025)
        self.models_to_try = [
            "llama-3.3-70b-versatile",  # Model chính
            "llama-3.1-8b-instant",  # Nhanh, nhẹ
            "llama-3.2-90b-text-preview",  # Model lớn
            "gemma-7b-it"  # Dự phòng
        ]

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Đọc văn bản từ file PDF - ĐỌC HẾT TẤT CẢ TRANG"""
        if not os.path.exists(pdf_path):
            print(f"❌ KHÔNG TÌM THẤY FILE TẠI: {pdf_path}")
            return ""

        print(f"📄 AI Agent: Đang đọc file PDF tại: {pdf_path}...")
        text = ""
        try:
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                total_pages = len(reader.pages)
                print(f"📊 Tổng số trang: {total_pages}")

                # ĐỌC HẾT TẤT CẢ TRANG
                for i in range(total_pages):
                    page_text = reader.pages[i].extract_text()
                    if page_text:
                        text += f"\n[TRANG {i + 1}]\n{page_text}"

                    # Hiển thị tiến trình
                    if (i + 1) % 10 == 0:
                        print(f"   ⏳ Đã đọc {i + 1}/{total_pages} trang...")

            print(f"✅ Đã đọc thành công TOÀN BỘ {total_pages} trang!")
            print(f"📝 Tổng số ký tự: {len(text):,}")
            return text
        except Exception as e:
            print(f"❌ Lỗi xử lý PDF: {e}")
            return ""

    def collect_data_with_ai(self, report_content: str, is_mock: bool = False) -> str:
        """Gửi văn bản tới Groq AI và nhận về JSON"""
        if is_mock or not self.api_key or len(self.api_key) < 10:
            return self._get_mock_schema("LỖI_FILE_HOẶC_KHOÁ_API")

        # GIẢM KÍCH THƯỚC để tránh lỗi 413
        # Groq free tier: ~12,000 tokens = ~30,000 ký tự
        max_content_length = 25000  # An toàn hơn

        if len(report_content) > max_content_length:
            print(f"⚠️ Báo cáo quá dài ({len(report_content):,} ký tự)")
            print(f"📝 Đang rút gọn xuống {max_content_length:,} ký tự...")

            # Lấy đầu và cuối file (phần quan trọng thường ở đây)
            head_size = int(max_content_length * 0.7)
            tail_size = max_content_length - head_size

            report_content = (
                    report_content[:head_size] +
                    "\n\n[... PHẦN GIỮA ĐÃ BỊ RÚT GỌN ...]\n\n" +
                    report_content[-tail_size:]
            )

        metrics_desc = ", ".join([f"{k} ({v['name']})" for k, v in ESG_CONFIG['metrics'].items()])

        system_prompt = """Bạn là chuyên gia phân tích ESG chuyên nghiệp. 
Nhiệm vụ của bạn là đọc báo cáo và đánh giá điểm số cho các chỉ số ESG.
CHỈ TRẢ VỀ JSON HỢP LỆ, KHÔNG THÊM GÌ KHÁC."""

        user_prompt = f"""Phân tích báo cáo ESG dưới đây và trả về JSON theo ĐÚNG cấu trúc:

{{
    "scores": {{
        "E1": <số từ 0-100>,
        "E2": <số từ 0-100>,
        "E3": <số từ 0-100>,
        "E4": <số từ 0-100>,
        "E5": <số từ 0-100>,
        "S1": <số từ 0-100>,
        "S2": <số từ 0-100>,
        "S3": <số từ 0-100>,
        "S4": <số từ 0-100>,
        "S5": <số từ 0-100>,
        "G1": <số từ 0-100>,
        "G2": <số từ 0-100>,
        "G3": <số từ 0-100>,
        "G4": <số từ 0-100>
    }},
    "insights": {{
        "E": "Tóm tắt về môi trường",
        "S": "Tóm tắt về xã hội",
        "G": "Tóm tắt về quản trị"
    }},
    "flags": ["Các cảnh báo quan trọng nếu có"]
}}

Giải thích các chỉ số:
{metrics_desc}

NỘI DUNG BÁO CÁO:
{report_content}

CHỈ TRẢ VỀ JSON, KHÔNG GIẢI THÍCH THÊM."""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Thử lần lượt các model cho đến khi thành công
        for model in self.models_to_try:
            print(f"🧠 AI Agent: Đang phân tích bằng Groq ({model})...")

            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 2000,  # Giảm xuống để tránh lỗi
                "response_format": {"type": "json_object"}
            }

            try:
                url = f"{self.base_url}/chat/completions"
                response = requests.post(url, headers=headers, json=payload, timeout=90)

                if response.status_code == 200:
                    result = response.json()
                    raw_text = result['choices'][0]['message']['content']
                    # Loại bỏ markdown code blocks nếu có
                    cleaned_text = re.sub(r'```json|```', '', raw_text).strip()
                    print(f"✅ Phân tích thành công với {model}!")
                    return cleaned_text

                elif response.status_code == 400:
                    error_data = response.json()
                    if "decommissioned" in error_data.get("error", {}).get("message", ""):
                        print(f"⚠️ Model {model} đã ngừng hoạt động, thử model khác...")
                        continue
                    else:
                        print(f"❌ Lỗi 400: {response.text[:200]}")
                        continue

                elif response.status_code == 404:
                    print(f"⚠️ Model {model} không khả dụng, thử model khác...")
                    continue

                elif response.status_code == 413:
                    print(f"⚠️ Request quá lớn cho {model}, thử model khác hoặc giảm kích thước...")
                    # Giảm thêm kích thước nếu vẫn quá lớn
                    if len(report_content) > 15000:
                        report_content = report_content[:15000]
                    continue

                elif response.status_code == 429:
                    print(f"⚠️ Rate limit với {model}, thử model khác...")
                    continue

                else:
                    error_msg = response.text[:300]
                    print(f"❌ Lỗi API Groq (Code {response.status_code}): {error_msg}")
                    if "quota" in error_msg.lower() or "limit" in error_msg.lower():
                        continue  # Thử model khác nếu hết quota

            except requests.exceptions.Timeout:
                print(f"⏱️ Timeout với {model}, thử model khác...")
                continue
            except Exception as e:
                print(f"❌ Lỗi với {model}: {str(e)[:100]}")
                continue

        # Nếu tất cả model đều thất bại
        return self._get_mock_schema("TẤT_CẢ_MODEL_ĐỀU_THẤT_BẠI")

    def _get_mock_schema(self, reason: str) -> str:
        """Trả về dữ liệu mô phỏng khi có lỗi"""
        return json.dumps({
            "scores": {
                "E1": 85, "E2": 70, "E3": 0, "E4": 60, "E5": 40,
                "S1": 90, "S2": 50, "S3": 80, "S4": 0, "S5": 60,
                "G1": 100, "G2": 100, "G3": 90, "G4": 85
            },
            "insights": {
                "E": f"⚠️ Dữ liệu mô phỏng. Lý do: {reason}",
                "S": "Vui lòng kiểm tra API Key tại console.groq.com",
                "G": "Groq API hoàn toàn miễn phí, không cần thẻ tín dụng!"
            },
            "flags": [f"⚠️ CHẾ ĐỘ MÔ PHỎNG - {reason}"]
        })

    def process_final_report(self, ai_output_json: str) -> Dict[str, Any]:
        """Xử lý kết quả từ AI và tính toán điểm số cuối cùng"""
        try:
            data = json.loads(ai_output_json)
        except Exception as e:
            print(f"⚠️ Lỗi parse JSON: {e}")
            data = json.loads(self._get_mock_schema("LỖI_PHÂN_TÍCH_JSON"))

        raw_scores = data.get("scores", {})
        pillar_results = {}
        final_flags = data.get("flags", [])
        is_gold_locked = False

        # Tính điểm cho từng trụ cột (E, S, G)
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
                    msg = f"⚠️ THIẾU CHỈ SỐ BẮT BUỘC: {m_info['name']}"
                    if msg not in final_flags:
                        final_flags.append(msg)

            p_score = (weighted_sum / available_weight) if available_weight > 0 else 0

            # Giảm điểm nếu thiếu chỉ số bắt buộc
            if any(m['mandatory'] and raw_scores.get(k, 0) == 0 for k, m in p_metrics.items()):
                p_score *= 0.5

            pillar_results[p_code] = round(p_score, 2)

        # Tính tổng điểm
        total_score = round(sum(
            pillar_results[p] * ESG_CONFIG['pillars'][p]['weight']
            for p in pillar_results
        ), 2)

        # Xếp hạng
        rank = "UNRANKED"
        if total_score >= 80 and not is_gold_locked:
            rank = "GOLD"
        elif total_score >= 55:
            rank = "SILVER"
        elif total_score >= 35:
            rank = "BRONZE"

        return {
            "metadata": {
                "agent": "GreenScore AI Agent (Groq)",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "api": "Groq (FREE)"
            },
            "evaluation": {
                "score": total_score,
                "rank": rank,
                "badge": f"GREENSCORE_{rank}_NFT",
                "pillar_breakdown": pillar_results
            },
            "analysis": {
                "insights": data.get("insights", {}),
                "flags": list(set(final_flags)),
                "raw_scores": raw_scores
            }
        }


if __name__ == "__main__":
    print("🌱 GREEN SCORE AI AGENT - Groq Edition (FREE & FAST)")
    print("=" * 60)

    # 1. API KEY từ Groq (https://console.groq.com/keys)
    MY_API_KEY = "YOUR_GROQ_API_KEY_HERE"  # Thay bằng API key của bạn

    # 2. FILE PDF
    PDF_FILE = r"D:/OneDrive - uel.edu.vn/HocTap_UEL/Cuoc_thi_hoc_thuat/ESG/ESG-GreenScore-for-Business/baocaovnm.pdf"

    # Kiểm tra API key
    if MY_API_KEY == "YOUR_GROQ_API_KEY_HERE":
        print("⚠️ CẢNH BÁO: Bạn chưa thay API key!")
        print("📝 Hướng dẫn:")
        print("   1. Truy cập: https://console.groq.com/keys")
        print("   2. Đăng ký/Đăng nhập (MIỄN PHÍ)")
        print("   3. Tạo API key mới")
        print("   4. Copy và dán vào biến MY_API_KEY trong code")
        print("\n🔄 Đang chạy ở CHẾ ĐỘ MÔ PHỎNG...\n")

    agent = GreenScoreAgent(api_key=MY_API_KEY)
    content = agent.extract_text_from_pdf(PDF_FILE)

    is_using_mock = not bool(content)
    json_from_ai = agent.collect_data_with_ai(content, is_mock=is_using_mock)
    final_report = agent.process_final_report(json_from_ai)

    print("\n" + "═" * 60)
    print("🎯 KẾT QUẢ ĐÁNH GIÁ TỰ ĐỘNG (GREEN SCORE)")
    print("═" * 60)
    print(json.dumps(final_report, indent=4, ensure_ascii=False))
    print("═" * 60)

    if "CHẾ ĐỘ MÔ PHỎNG" in str(final_report):
        print("\n⚠️ Kết quả trên là dữ liệu mô phỏng!")
        print("💡 Để có kết quả thật, vui lòng:")
        print("   - Kiểm tra API key Groq")
        print("   - Đảm bảo file PDF tồn tại")