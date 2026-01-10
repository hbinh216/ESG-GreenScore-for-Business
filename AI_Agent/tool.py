"""
ESG Analysis Tools
Các công cụ hỗ trợ phân tích ESG từ nhiều nguồn dữ liệu
"""

import json
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import re


class ESGDataCollector:
    """Tool 1: Thu thập dữ liệu ESG từ Google Search"""

    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

    def google_search_esg(self, company_name: str, search_type: str = "general") -> List[Dict[str, str]]:
        """
        Tìm kiếm thông tin ESG của công ty qua Google

        Args:
            company_name: Tên công ty
            search_type: Loại tìm kiếm ("general", "environment", "social", "governance", "report")

        Returns:
            Danh sách kết quả tìm kiếm
        """
        # Tạo query theo loại tìm kiếm
        queries = {
            "general": f'"{company_name}" ESG sustainability report',
            "environment": f'"{company_name}" môi trường phát thải carbon năng lượng',
            "social": f'"{company_name}" trách nhiệm xã hội lao động cộng đồng',
            "governance": f'"{company_name}" quản trị doanh nghiệp HĐQT minh bạch',
            "report": f'"{company_name}" báo cáo bền vững phát triển bền vững',
            "news": f'"{company_name}" ESG news scandal violation',
            "awards": f'"{company_name}" giải thưởng ESG bền vững'
        }

        query = queries.get(search_type, queries["general"])

        try:
            # Mô phỏng Google search results
            # Trong thực tế, bạn có thể dùng: SerpAPI, Google Custom Search API, hoặc web scraping
            search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}"

            headers = {'User-Agent': self.user_agent}

            # Note: Đây là simulation - trong production nên dùng API chính thức
            results = {
                "query": query,
                "search_type": search_type,
                "company": company_name,
                "timestamp": datetime.now().isoformat(),
                "results": [
                    {
                        "title": f"Báo cáo ESG {company_name}",
                        "url": search_url,
                        "snippet": f"Thông tin về hoạt động ESG và phát triển bền vững của {company_name}",
                        "relevance": "high"
                    }
                ],
                "search_url": search_url
            }

            return results

        except Exception as e:
            return {
                "query": query,
                "company": company_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def search_company_info(self, company_name: str) -> Dict[str, Any]:
        """
        Tìm kiếm thông tin tổng quan về công ty

        Args:
            company_name: Tên công ty

        Returns:
            Dictionary chứa thông tin công ty từ Google Search
        """
        try:
            searches = {
                "overview": self.google_search_esg(company_name, "general"),
                "esg_report": self.google_search_esg(company_name, "report"),
                "environment": self.google_search_esg(company_name, "environment"),
                "social": self.google_search_esg(company_name, "social"),
                "governance": self.google_search_esg(company_name, "governance"),
                "news": self.google_search_esg(company_name, "news"),
                "awards": self.google_search_esg(company_name, "awards")
            }

            return {
                "company": company_name,
                "searches": searches,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }

        except Exception as e:
            return {
                "company": company_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "failed"
            }

    def get_industry_keywords(self, company_name: str) -> List[str]:
        """
        Trích xuất keywords về ngành nghề từ tên công ty

        Returns:
            List các keywords liên quan đến ngành
        """
        industry_mapping = {
            "bank": ["finance", "banking", "tài chính", "ngân hàng"],
            "tech": ["technology", "công nghệ", "software", "phần mềm"],
            "manufacture": ["manufacturing", "sản xuất", "công nghiệp"],
            "retail": ["retail", "bán lẻ", "thương mại"],
            "energy": ["energy", "năng lượng", "điện", "oil", "gas"],
            "real estate": ["real estate", "bất động sản", "property"],
            "food": ["food", "thực phẩm", "beverage", "đồ uống"],
            "pharma": ["pharmaceutical", "dược phẩm", "healthcare", "y tế"],
            "telecom": ["telecommunication", "viễn thông", "telco"]
        }

        detected_keywords = []
        company_lower = company_name.lower()

        for industry, keywords in industry_mapping.items():
            if any(kw in company_lower for kw in keywords):
                detected_keywords.extend(keywords)

        return detected_keywords if detected_keywords else ["general", "business"]


class ESGTextAnalyzer:
    """Tool 2: Phân tích văn bản ESG với AI (FinBERT-ESG simulation)"""

    def __init__(self):
        # Keywords mapping cho từng trụ cột ESG
        self.esg_keywords = {
            "E": {
                "positive": [
                    "renewable energy", "carbon neutral", "net zero", "green energy",
                    "emissions reduction", "sustainability", "clean energy", "solar",
                    "wind power", "energy efficiency", "recycling", "circular economy",
                    "năng lượng tái tạo", "giảm phát thải", "trung hòa carbon"
                ],
                "negative": [
                    "pollution", "toxic waste", "oil spill", "deforestation",
                    "high emissions", "environmental damage", "carbon intensive",
                    "ô nhiễm", "chất thải độc hại", "phá rừng"
                ]
            },
            "S": {
                "positive": [
                    "employee welfare", "diversity", "inclusion", "fair wage",
                    "training", "health and safety", "community engagement",
                    "labor rights", "gender equality", "employee benefits",
                    "phúc lợi nhân viên", "đa dạng", "công bằng", "đào tạo"
                ],
                "negative": [
                    "discrimination", "labor violation", "unsafe workplace",
                    "child labor", "harassment", "poor working conditions",
                    "phân biệt đối xử", "vi phạm lao động"
                ]
            },
            "G": {
                "positive": [
                    "board independence", "transparency", "ethics", "compliance",
                    "accountability", "anti-corruption", "stakeholder engagement",
                    "risk management", "data privacy", "corporate governance",
                    "minh bạch", "đạo đức", "tuân thủ"
                ],
                "negative": [
                    "corruption", "bribery", "fraud", "scandal", "conflict of interest",
                    "lack of transparency", "governance failure",
                    "tham nhũng", "hối lộ", "gian lận"
                ]
            }
        }

    def analyze_text_sentiment(self, text: str, max_length: int = 2000) -> Dict[str, Any]:
        """
        Phân tích sentiment ESG từ văn bản

        Args:
            text: Văn bản cần phân tích (báo cáo, tin tức, etc.)
            max_length: Độ dài tối đa văn bản xử lý

        Returns:
            Dictionary chứa phân loại E/S/G và điểm sentiment
        """
        # Chuẩn hóa text
        text_lower = text[:max_length].lower()

        results = {
            "text_length": len(text),
            "analyzed_length": min(len(text), max_length),
            "pillar_scores": {},
            "overall_sentiment": "neutral",
            "confidence": 0.0,
            "key_findings": []
        }

        # Phân tích từng trụ cột
        for pillar, keywords in self.esg_keywords.items():
            positive_count = sum(1 for kw in keywords["positive"] if kw in text_lower)
            negative_count = sum(1 for kw in keywords["negative"] if kw in text_lower)

            total_mentions = positive_count + negative_count

            if total_mentions > 0:
                sentiment_score = (positive_count - negative_count) / total_mentions
                confidence = min(total_mentions / 10, 1.0)  # Confidence tăng theo số lượng mentions

                results["pillar_scores"][pillar] = {
                    "sentiment": sentiment_score,
                    "confidence": round(confidence, 2),
                    "positive_mentions": positive_count,
                    "negative_mentions": negative_count,
                    "interpretation": self._interpret_sentiment(sentiment_score)
                }

                # Ghi lại findings
                if sentiment_score > 0.3:
                    results["key_findings"].append(f"✅ Tích cực về {self._pillar_name(pillar)}")
                elif sentiment_score < -0.3:
                    results["key_findings"].append(f"⚠️ Tiêu cực về {self._pillar_name(pillar)}")

        # Tính overall sentiment
        if results["pillar_scores"]:
            avg_sentiment = sum(p["sentiment"] for p in results["pillar_scores"].values()) / len(
                results["pillar_scores"])
            results["overall_sentiment"] = self._interpret_sentiment(avg_sentiment)
            results["confidence"] = round(
                sum(p["confidence"] for p in results["pillar_scores"].values()) / len(results["pillar_scores"]),
                2
            )

        return results

    def _interpret_sentiment(self, score: float) -> str:
        """Chuyển đổi điểm sentiment thành nhãn"""
        if score > 0.3:
            return "positive"
        elif score < -0.3:
            return "negative"
        else:
            return "neutral"

    def _pillar_name(self, code: str) -> str:
        """Trả về tên đầy đủ của trụ cột"""
        names = {"E": "Môi trường", "S": "Xã hội", "G": "Quản trị"}
        return names.get(code, code)

    def extract_esg_metrics_from_text(self, text: str) -> Dict[str, List[str]]:
        """
        Trích xuất các chỉ số ESG cụ thể từ văn bản

        Returns:
            Dictionary với key là loại chỉ số, value là list các findings
        """
        metrics = {
            "emissions": [],
            "energy": [],
            "water": [],
            "waste": [],
            "diversity": [],
            "safety": [],
            "training": [],
            "board": [],
            "ethics": []
        }

        # Regex patterns để tìm số liệu
        patterns = {
            "emissions": r"(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:tấn|tons?|tonnes?|kg)?\s*(?:CO2|carbon|phát thải)",
            "energy": r"(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:MWh|GWh|kWh|điện)",
            "water": r"(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:m3|lít|liters?|nước)",
            "diversity": r"(\d+(?:\.\d+)?)\s*%\s*(?:female|women|nữ|phụ nữ)",
        }

        for metric, pattern in patterns.items():
            findings = re.findall(pattern, text, re.IGNORECASE)
            if findings:
                metrics[metric] = findings[:5]  # Lấy tối đa 5 kết quả

        return {k: v for k, v in metrics.items() if v}  # Chỉ trả về metrics có dữ liệu


class ESGBenchmarkTool:
    """Tool 3: So sánh với ngành và benchmark"""

    def __init__(self):
        # Dữ liệu benchmark trung bình theo ngành (scale 0-100)
        self.industry_benchmarks = {
            "technology": {"E": 65, "S": 70, "G": 75},
            "finance": {"E": 60, "S": 68, "G": 80},
            "manufacturing": {"E": 55, "S": 62, "G": 65},
            "retail": {"E": 58, "S": 65, "G": 68},
            "energy": {"E": 45, "S": 60, "G": 70},
            "healthcare": {"E": 62, "S": 72, "G": 73},
            "default": {"E": 60, "S": 65, "G": 70}
        }

    def compare_with_benchmark(
            self,
            company_scores: Dict[str, float],
            industry: str = "default"
    ) -> Dict[str, Any]:
        """
        So sánh điểm ESG với trung bình ngành

        Args:
            company_scores: Dictionary {"E": score, "S": score, "G": score}
            industry: Tên ngành

        Returns:
            Báo cáo so sánh
        """
        benchmark = self.industry_benchmarks.get(
            industry.lower(),
            self.industry_benchmarks["default"]
        )

        comparison = {
            "industry": industry,
            "benchmark_scores": benchmark,
            "company_scores": company_scores,
            "differences": {},
            "performance": {},
            "recommendations": []
        }

        for pillar in ["E", "S", "G"]:
            company_score = company_scores.get(pillar, 0)
            benchmark_score = benchmark[pillar]
            diff = company_score - benchmark_score

            comparison["differences"][pillar] = round(diff, 2)

            if diff >= 10:
                comparison["performance"][pillar] = "Vượt trội"
                comparison["recommendations"].append(
                    f"✅ Duy trì và phát huy thế mạnh về {pillar}"
                )
            elif diff >= 0:
                comparison["performance"][pillar] = "Tốt"
            elif diff >= -10:
                comparison["performance"][pillar] = "Cần cải thiện"
                comparison["recommendations"].append(
                    f"⚠️ Tăng cường hoạt động về {pillar}"
                )
            else:
                comparison["performance"][pillar] = "Yếu"
                comparison["recommendations"].append(
                    f"🚨 Cần hành động khẩn cấp về {pillar}"
                )

        # Tính tổng điểm
        company_total = sum(company_scores.get(p, 0) * 0.33 for p in ["E", "S", "G"])
        benchmark_total = sum(benchmark[p] * 0.33 for p in ["E", "S", "G"])

        comparison["total_score"] = {
            "company": round(company_total, 2),
            "benchmark": round(benchmark_total, 2),
            "difference": round(company_total - benchmark_total, 2)
        }

        return comparison


class ESGRiskDetector:
    """Tool 4: Phát hiện rủi ro ESG"""

    def __init__(self):
        self.risk_indicators = {
            "high": [
                "scandal", "violation", "lawsuit", "fine", "penalty",
                "investigation", "fraud", "corruption", "bribery",
                "vi phạm", "phạt", "điều tra", "tham nhũng"
            ],
            "medium": [
                "concern", "issue", "complaint", "dispute", "controversy",
                "non-compliance", "breach", "incident",
                "tranh chấp", "không tuân thủ", "sự cố"
            ],
            "low": [
                "improvement needed", "room for improvement", "below average",
                "cần cải thiện", "dưới trung bình"
            ]
        }

    def detect_risks(self, text: str, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phát hiện các rủi ro ESG từ văn bản và dữ liệu

        Returns:
            Báo cáo rủi ro với mức độ ưu tiên
        """
        text_lower = text.lower()

        detected_risks = {
            "high_risks": [],
            "medium_risks": [],
            "low_risks": [],
            "risk_score": 0,
            "priority_actions": []
        }

        # Quét theo mức độ rủi ro
        for level, keywords in self.risk_indicators.items():
            findings = [kw for kw in keywords if kw in text_lower]

            if findings:
                risk_entry = {
                    "keywords_found": findings,
                    "count": len(findings)
                }

                if level == "high":
                    detected_risks["high_risks"].append(risk_entry)
                    detected_risks["risk_score"] += len(findings) * 3
                elif level == "medium":
                    detected_risks["medium_risks"].append(risk_entry)
                    detected_risks["risk_score"] += len(findings) * 2
                else:
                    detected_risks["low_risks"].append(risk_entry)
                    detected_risks["risk_score"] += len(findings) * 1

        # Phân tích dữ liệu số
        scores = company_data.get("pillar_scores", {})
        for pillar, score in scores.items():
            if score < 40:
                detected_risks["high_risks"].append({
                    "type": "low_score",
                    "pillar": pillar,
                    "score": score,
                    "message": f"Điểm {pillar} thấp nghiêm trọng"
                })
                detected_risks["priority_actions"].append(
                    f"🚨 Ưu tiên cải thiện {pillar} (điểm hiện tại: {score})"
                )

        # Tổng hợp risk level
        if detected_risks["risk_score"] > 20:
            detected_risks["overall_risk_level"] = "HIGH"
        elif detected_risks["risk_score"] > 10:
            detected_risks["overall_risk_level"] = "MEDIUM"
        else:
            detected_risks["overall_risk_level"] = "LOW"

        return detected_risks


# ===== FACTORY FUNCTION =====
def get_all_tools():
    """
    Khởi tạo và trả về tất cả các tools

    Returns:
        Dictionary chứa tất cả tools instance
    """
    return {
        "data_collector": ESGDataCollector(),
        "text_analyzer": ESGTextAnalyzer(),
        "benchmark": ESGBenchmarkTool(),
        "risk_detector": ESGRiskDetector()
    }


# ===== DEMO USAGE =====
if __name__ == "__main__":
    print("🔧 ESG Tools - Demo Mode\n")

    # Test 1: Data Collector
    print("=" * 60)
    print("TEST 1: Yahoo Finance ESG Data")
    print("=" * 60)
    collector = ESGDataCollector()
    data = collector.get_yahoo_esg_data("AAPL")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    # Test 2: Text Analyzer
    print("\n" + "=" * 60)
    print("TEST 2: Text Sentiment Analysis")
    print("=" * 60)
    analyzer = ESGTextAnalyzer()
    sample_text = """
    The company has committed to achieving net zero emissions by 2030 
    through renewable energy investments. However, recent reports indicate 
    labor violations in the supply chain and lack of board independence.
    """
    sentiment = analyzer.analyze_text_sentiment(sample_text)
    print(json.dumps(sentiment, indent=2, ensure_ascii=False))

    # Test 3: Benchmark
    print("\n" + "=" * 60)
    print("TEST 3: Industry Benchmark Comparison")
    print("=" * 60)
    benchmark_tool = ESGBenchmarkTool()
    comparison = benchmark_tool.compare_with_benchmark(
        {"E": 72, "S": 65, "G": 80},
        "technology"
    )
    print(json.dumps(comparison, indent=2, ensure_ascii=False))

    # Test 4: Risk Detector
    print("\n" + "=" * 60)
    print("TEST 4: Risk Detection")
    print("=" * 60)
    risk_tool = ESGRiskDetector()
    risks = risk_tool.detect_risks(
        "Company faces investigation for environmental violation and corruption scandal",
        {"pillar_scores": {"E": 35, "S": 45, "G": 50}}
    )
    print(json.dumps(risks, indent=2, ensure_ascii=False))

    print("\n✅ All tools tested successfully!")