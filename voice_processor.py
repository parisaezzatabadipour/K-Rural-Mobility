"""
modules/voice_processor.py
--------------------------
K-Rural-Mobility — ماژول پردازش ورودی صوتی/متنی (شبیه‌سازی‌شده).

در نسخه نمونه، ورودی «صوتی» به‌صورت متن شبیه‌سازی می‌شود و با
تطبیق الگوی کلیدواژه (فارسی/انگلیسی/کره‌ای) به یک درخواست
ساختاریافته شامل مبدأ، مقصد و تعداد مسافر تبدیل می‌شود.
"""

import json
import os
import re
from typing import Dict, Optional

# کلیدواژه‌های شناسایی هر ایستگاه در سه زبان
STATION_KEYWORDS = {
    "ST01": ["ایستگاه مرکزی", "ایستگاه", "station", "yangpyeong station", "역", "중앙역"],
    "ST02": ["درمانگاه", "کلینیک", "clinic", "hospital", "병원", "보건소"],
    "ST03": ["دهیاری", "شهر داری", "town office", "office", "면사무소", "읍사무소"],
    "ST04": ["رفاه سالمندان", "سالمندان", "senior", "welfare", "노인복지관"],
    "ST05": ["اوکچئن", "اوکچئون", "okcheon", "옥천"],
    "ST06": ["دان‌وُل", "دانوول", "danwol", "단월"],
    "ST07": ["چئونگون", "cheongun", "청운"],
    "ST08": ["گانگ‌ها", "گانگ", "gangha", "강하"],
    "ST09": ["یونگمون", "yongmun", "용문"],
}


def _load_nodes(path: Optional[str] = None) -> Dict:
    """بارگذاری فایل ایستگاه‌ها از data/rural_nodes.json"""
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "..", "data", "rural_nodes.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _normalize(text: str) -> str:
    """نرمال‌سازی متن ورودی (حذف اعراب، نقطه‌گذاری اضافی و حروف کشیده)."""
    text = text.strip().lower()
    text = re.sub(r"[\u064B-\u0652\u0640]", "", text)  # اعراب و کشیده عربی
    text = re.sub(r"[^\w\s\u0600-\u06FF\uAC00-\uD7A3-]", " ", text)
    return re.sub(r"\s+", " ", text)


def _find_station(text: str) -> Optional[str]:
    """یافتن نخستین ایستگاهی که کلیدواژه‌اش در متن موجود است."""
    norm = _normalize(text)
    # کلیدواژه‌های عمومی که به‌تنهایی ایستگاه خاصی را مشخص نمی‌کنند
    generic = {"station", "ایستگاه", "역", "office", "clinic", "hospital", "병원"}
    # اول کلیدواژه‌های طولانی‌تر (مشخص‌تر) بررسی شوند
    best_generic = None
    for sid, keywords in sorted(STATION_KEYWORDS.items(),
                                key=lambda kv: -max(len(k) for k in kv[1])):
        for kw in keywords:
            if kw and kw.lower() in norm:
                if kw.lower() in generic:
                    if best_generic is None:
                        best_generic = sid
                    continue
                return sid
    return best_generic


def _extract_passengers(text: str) -> int:
    """استخراج تعداد مسافر از متن (پیش‌فرض ۱)."""
    norm = _normalize(text)
    fa_digits = {"یک": 1, "دو": 2, "تنها": 1, "alone": 1}
    for word, n in fa_digits.items():
        if word in norm:
            return min(n, 2)  # ظرفیت کپسول: حداکثر ۲ نفر
    m = re.search(r"(\d+)\s*(nafar|people|passenger|نفر|명|명의)?", norm)
    if m:
        return max(1, min(int(m.group(1)), 2))
    return 1


def parse_request(text: str, nodes: Optional[Dict] = None) -> Dict:
    """
    تبدیل متن شبیه‌سازی‌شده صوتی به درخواست ساختاریافته.

    مثال:
        "می‌خواهم از ایستگاه مرکزی به درمانگاه محلی بروم"
        -> {"origin": "ST01", "destination": "ST02", "passengers": 1}
    """
    if nodes is None:
        nodes = _load_nodes()
    norm = _normalize(text)

    origin, destination = None, None

    # الگوی «از X به Y» (فارسی/انگلیسی)
    m = re.search(r"(?:از|from)\s+(.+?)\s+(?:به|to)\s+(.+)", norm)
    if m:
        origin = _find_station(m.group(1))
        destination = _find_station(m.group(2))

    # اگر فقط مقصد آمده: مبدأ = نزدیک‌ترین ایستگاه به «اینجا» یا ایستگاه مرکزی
    if destination is None:
        destination = _find_station(norm)
    if origin is None:
        origin = "ST01"  # پیش‌فرض: ایستگاه مرکزی

    passengers = _extract_passengers(text)
    names = {s["id"]: s["name_fa"] for s in nodes["stations"]}

    return {
        "raw_text": text,
        "origin": origin,
        "destination": destination,
        "origin_name": names.get(origin, origin),
        "destination_name": names.get(destination, destination),
        "passengers": passengers,
        "valid": destination is not None,
    }


# مثال‌های آماده برای داشبورد
SAMPLE_PHRASES = [
    "می‌خواهم از ایستگاه مرکزی به درمانگاه محلی بروم",
    "از مرکز رفاه سالمندان به ایستگاه روستایی اوکچئون",
    "به درمانگاه محلی، دو نفر",
    "from Gangha station to Yangpyeong Station",
    "병원에 가고 싶어요",  # "می‌خواهم به بیمارستان بروم"
]

if __name__ == "__main__":
    for phrase in SAMPLE_PHRASES:
        print(parse_request(phrase))
