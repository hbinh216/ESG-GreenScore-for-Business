# main.py
import os
import json
import time
from typing import Dict, Any

from google import genai

from esg_config import ESG_CONFIG
from esg_tools import (
    extract_text_from_pdf,
    get_basic_esg_data,
    FinBertESGTool,
    collect_esg_news_signals
)

from esg_tools import FinBertESGTool


from google import genai

class GreenScoreAgent:
    def __init__(self, gemini_api_key: str, model_name: str = "gemini-2.5-flash"):
        self.client = genai.Client(api_key=gemini_api_key)
        self.model_name = model_name
        self.finbert = FinBertESGTool()




    def call_gemini(self, prompt: str) -> str:
        # CHỈ gọi AI ở đây
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config={
                "temperature": 0.1,
                "response_mime_type": "application/json"
            }
        )
        return response.text

    def collect_data_with_ai(
            self,
            company_name: str,
            report_content: str,
            ticker: str = "",
            include_news: bool = True,
            num_articles: int = 5
    ) -> str:
        print(f"🚀 Đang gửi dữ liệu tới {self.model_name}...")

        metrics_list = "\n".join([f"- {k}: {v['name']}" for k, v in ESG_CONFIG["metrics"].items()])

        hard_data = ""
        if ticker.strip():
            print("📈 Lấy hard data từ yfinance...")
            hard_data = get_basic_esg_data(ticker.strip())

        # ✅ SOFT DATA: luôn có biến, và không crash nếu Google lỗi
        news_block = ""
        if include_news:
            print("📰 Tìm & phân tích soft data từ Google (CSE) + FinBERT-ESG...")
            try:
                news_signals = collect_esg_news_signals(company_name, self.finbert, num_articles=num_articles)
                news_block = json.dumps(news_signals, ensure_ascii=False, indent=2)
            except Exception as e:
                print("⚠️ Không lấy được soft data từ Google CSE, sẽ bỏ qua phần news.")
                print("Chi tiết lỗi:", str(e))
                news_block = json.dumps({"error": str(e), "results": []}, ensure_ascii=False, indent=2)
        else:
            news_block = json.dumps({"disabled": True, "results": []}, ensure_ascii=False, indent=2)

        prompt = f"""
    Bạn là chuyên gia kiểm toán ESG. Hãy đọc báo cáo thường niên + dữ liệu hard/soft để chấm điểm định lượng (0-100) cho từng chỉ số.

    TÊN CÔNG TY: {company_name}
    TICKER (NẾU CÓ): {ticker}

    DANH SÁCH CHỈ SỐ CẦN CHẤM:
    {metrics_list}

    QUY TẮC:
    - Chỉ chấm điểm khi có bằng chứng/đề cập rõ. Nếu mơ hồ hoặc không thấy thông tin, cho 0–20 và nêu cảnh báo.
    - Nếu có rủi ro từ tin tức (controversy/scandal), phản ánh giảm điểm đúng trụ cột liên quan.
    - Ưu tiên số liệu, mục tiêu, lộ trình, chính sách, audit/certification.

    HARD DATA (yfinance, nếu có):
    {hard_data}

    SOFT DATA (Google Search + FinBERT-ESG):
    {news_block}

    YÊU CẦU OUTPUT QUAN TRỌNG:
    Trả về đúng JSON (không markdown, không giải thích):
    {{
      "scores": {{
        "E1": <điểm>, "E2": <điểm>, "E3": <điểm>, "E4": <điểm>, "E5": <điểm>,
        "S1": <điểm>, "S2": <điểm>, "S3": <điểm>, "S4": <điểm>, "S5": <điểm>,
        "G1": <điểm>, "G2": <điểm>, "G3": <điểm>, "G4": <điểm>
      }},
      "insights": {{
        "E": "Nhận xét E",
        "S": "Nhận xét S",
        "G": "Nhận xét G"
      }},
      "flags": ["Cảnh báo rủi ro"]
    }}

    DỮ LIỆU BÁO CÁO THƯỜNG NIÊN (TRÍCH XUẤT PDF):
    {report_content}
    """

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config={
                "temperature": 0.1,
                "response_mime_type": "application/json"
            }
        )
        return response.text

    def process_final_report(self, ai_output_json: str) -> Dict[str, Any]:
        try:
            data = json.loads(ai_output_json)
        except Exception:
            data = {"scores": {}, "flags": ["Lỗi JSON từ AI (không parse được)"]}

        raw_scores = data.get("scores", {})
        pillar_results = {}
        final_flags = data.get("flags", [])
        is_gold_locked = False

        for p_code, p_info in ESG_CONFIG["pillars"].items():
            p_metrics = {k: v for k, v in ESG_CONFIG["metrics"].items() if v["pillar"] == p_code}
            weighted_sum = 0.0
            available_weight = 0.0

            for m_code, m_info in p_metrics.items():
                val = raw_scores.get(m_code, 0)

                if isinstance(val, str):
                    try:
                        val = float(val)
                    except:
                        val = 0

                if val > 0:
                    weighted_sum += (val * m_info["weight"])
                    available_weight += m_info["weight"]
                elif m_info["mandatory"]:
                    is_gold_locked = True
                    msg = f"Thiếu chỉ số bắt buộc: {m_code}"
                    if msg not in final_flags:
                        final_flags.append(msg)

            p_score = (weighted_sum / available_weight) if available_weight > 0 else 0

            # phạt thêm nếu thiếu metric bắt buộc (trong trụ)
            if any(m["mandatory"] and raw_scores.get(k, 0) in [0, "0", None] for k, m in p_metrics.items()):
                p_score *= 0.5

            pillar_results[p_code] = round(p_score, 2)

        total_score = round(
            sum(pillar_results[p] * ESG_CONFIG["pillars"][p]["weight"] for p in pillar_results),
            2
        )

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
            "detailed_scores": raw_scores,
            "analysis": {
                "insights": data.get("insights", {}),
                "flags": final_flags
            }
        }


def main():
    print("=" * 60)
    print("🌱 GREENSCORE AI AGENT - MAIN")
    print("=" * 60)

    # (A) Input
    company_name = input("Nhập tên công ty: ").strip()
    pdf_path = input("Chọn đường dẫn file báo cáo thường niên (PDF): ").strip()
    ticker = input("Nhập ticker (nếu có, Enter để bỏ qua): ").strip()

    # (B) Keys từ env (khuyên dùng)
    gemini_key = "AIzaSyDPp0Q6aWqOw2kPESMx_64ineVMWdqZegY"
    if not gemini_key:
        raise EnvironmentError("Thiếu GEMINI_API_KEY trong biến môi trường.")

    agent = GreenScoreAgent(gemini_api_key=gemini_key, model_name="gemini-2.5-flash")

    # (C) Run
    print("📄 Đang đọc PDF...")
    report_text = extract_text_from_pdf(pdf_path)

    json_ai = agent.collect_data_with_ai(
        company_name=company_name,
        report_content=report_text,
        ticker=ticker,
        include_news=True,
        num_articles=5
    )

    final_report = agent.process_final_report(json_ai)

    print("\n" + "═" * 60)
    print("🎯 KẾT QUẢ ĐÁNH GIÁ CHI TIẾT")
    print("═" * 60)
    print(json.dumps(final_report, indent=4, ensure_ascii=False))

    out_file = "ket_qua_full.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(final_report, f, indent=4, ensure_ascii=False)
    print(f"\n💾 Đã lưu kết quả vào: {out_file}")


if __name__ == "__main__":
    main()
