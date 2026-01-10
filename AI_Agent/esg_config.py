# esg_config.py
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
