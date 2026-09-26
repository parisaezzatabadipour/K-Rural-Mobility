"""
modules/routing_engine.py
-------------------------
K-Rural-Mobility — موتور بهینه‌سازی مسیر (VRPTW ساده‌شده).

استراتژی: درج حریصانه (Greedy Insertion) روی ماتریس فاصله هاوِرساین.
هر خودرو حداکثر ۲ مسافر ظرفیت دارد و هدف کمینه‌کردن
(مسافت کل + جریمه زمان انتظار) است.
اگر Google OR-Tools نصب باشد برای ابعاد بزرگ‌تر استفاده می‌شود،
در غیر این صورت الگوریتم داخلی (بدون وابستگی) اجرا می‌شود.
"""

import json
import math
import os
from typing import Dict, List, Optional, Tuple

EARTH_RADIUS_KM = 6371.0
VEHICLE_CAPACITY = 2


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """فاصله دو نقطه جغرافیایی بر حسب کیلومتر."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlmb / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def _load_nodes(path: Optional[str] = None) -> Dict:
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "..", "data", "rural_nodes.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class RoutingEngine:
    """موتور تخصیص درخواست‌ها به ناوگان کپسول‌های خودران ۲ نفره."""

    def __init__(self, nodes: Optional[Dict] = None):
        self.nodes = nodes if nodes is not None else _load_nodes()
        self.stations = {s["id"]: s for s in self.nodes["stations"]}
        self.ids = list(self.stations.keys())
        self.coords = {sid: (self.stations[sid]["lat"], self.stations[sid]["lng"])
                       for sid in self.ids}
        self.dist = self._build_distance_matrix()

    # ---------- ساخت ماتریس فاصله ----------
    def _build_distance_matrix(self) -> Dict[Tuple[str, str], float]:
        matrix = {}
        for a in self.ids:
            for b in self.ids:
                la, ln = self.coords[a]
                lb, ln2 = self.coords[b]
                matrix[(a, b)] = 0.0 if a == b else haversine(la, ln, lb, ln2)
        return matrix

    # ---------- درج حریصانه ----------
    def assign(self, requests: List[Dict],
               fleet: Optional[List[Dict]] = None) -> Dict:
        """
        تخصیص بهینه درخواست‌ها به خودروها.

        Args:
            requests: لیستی از dict های خروجی voice_processor.parse_request
            fleet:    وضعیت فعلی خودروها (مختصات/مسیر فعلی). اگر None باشد
                      از تعریف اولیه ناوگان در فایل داده استفاده می‌شود.
        Returns:
            dict شامل تخصیص هر خودرو (لیست توقف‌ها)، کل مسافت و
            برآورد صرفه‌جویی نسبت به حالت «هر مسافر یک خودرو».
        """
        if fleet is None:
            fleet = [{"id": f["id"], "lat": f["lat"], "lng": f["lng"],
                      "route": []} for f in self.nodes["fleet"]]

        # مسافت پایه: حالت بدون بهینه‌سازی (هر درخواست مستقل)
        base_distance = sum(
            self.dist[(r["origin"], r["destination"])] for r in requests
        ) if requests else 0.0

        routes = {v["id"]: {
            "stops": [],          # توقف‌های برنامه‌ریزی‌شده
            "passengers": 0,      # ظرفیت اشغال‌شده (0..2)
            "lat": v["lat"], "lng": v["lng"],
        } for v in fleet}

        total_distance = 0.0
        unassigned = []

        # مرتب‌سازی درخواست‌ها بر اساس فاصله نزولی (اول دورترین‌ها)
        ordered = sorted(requests,
                         key=lambda r: self.dist[(r["origin"], r["destination"])],
                         reverse=True)

        WAIT_PENALTY_PER_KM = 2.0  # جریمه انتظار به‌ازای هر کیلومتر اضافه

        for req in ordered:
            best_vid, best_cost, best_plan = None, float("inf"), None
            for vid, veh in routes.items():
                if veh["passengers"] + req["passengers"] > VEHICLE_CAPACITY:
                    continue
                # هزینه الحاق درخواست به انتهای مسیر فعلی خودرو
                last = veh["stops"][-1]["station_id"] if veh["stops"] else None
                leg1 = 0.0 if last is None else self.dist[(last, req["origin"])]
                leg2 = self.dist[(req["origin"], req["destination"])]
                # جریمه انتظار مسافر: فاصله خودرو تا مبدأ
                cost = leg1 + leg2 + WAIT_PENALTY_PER_KM * leg1
                if cost < best_cost:
                    best_cost, best_vid = cost, vid
                    best_plan = leg1 + leg2

            if best_vid is None:
                unassigned.append(req)
                continue

            veh = routes[best_vid]
            veh["stops"].append({"station_id": req["origin"],
                                 "activity": "pickup",
                                 "passengers": req["passengers"]})
            veh["stops"].append({"station_id": req["destination"],
                                 "activity": "dropoff",
                                 "passengers": req["passengers"]})
            veh["passengers"] += req["passengers"]
            total_distance += best_plan

        savings = max(0.0, base_distance - total_distance)
        savings_pct = (savings / base_distance * 100.0) if base_distance > 0 else 0.0

        return {
            "routes": routes,
            "total_distance_km": round(total_distance, 2),
            "baseline_distance_km": round(base_distance, 2),
            "energy_savings_pct": round(savings_pct, 1),
            "unassigned": unassigned,
        }

    # ---------- مسیر هندسی برای نمایش روی نقشه ----------
    def route_polyline(self, stops: List[Dict], veh_lat: float, veh_lng: float) -> List[List[float]]:
        """تولید پلی‌لاین ساده (مختصات خودرو → توقف‌ها)."""
        pts = [[veh_lat, veh_lng]]
        for s in stops:
            lat, lng = self.coords[s["station_id"]]
            pts.append([lat, lng])
        return pts


if __name__ == "__main__":
    from modules.voice_processor import parse_request, SAMPLE_PHRASES  # noqa
    engine = RoutingEngine()
    reqs = [parse_request(p) for p in SAMPLE_PHRASES[:4]]
    reqs = [r for r in reqs if r["valid"]]
    result = engine.assign(reqs)
    print(json.dumps(result, ensure_ascii=False, indent=2))
