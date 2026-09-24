"""
app.py — K-Rural-Mobility | داشبورد مدیریتی Streamlit
تم: آبی ـ سفید (Blue-White Theme)
اجرا:  streamlit run app.py
"""

import json
import time
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

from modules.voice_processor import parse_request, SAMPLE_PHRASES
from modules.routing_engine import RoutingEngine
from modules.av_simulator import FleetSimulator

# ---------------- تنظیمات صفحه و تم آبی ـ سفید ----------------
st.set_page_config(
    page_title="K-Rural-Mobility | پلتفرم حمل‌ونقل هوشمند روستایی",
    page_icon="🚐",
    layout="wide",
)

BLUE = "#1565C0"
BLUE_DARK = "#0D47A1"
BLUE_LIGHT = "#E3F2FD"

st.markdown(f"""
<style>
    /* پس‌زمینه سفید و سربرگ آبی */
    .stApp {{ background-color: #FFFFFF; }}
    header[data-testid="stHeader"] {{ background-color: {BLUE_DARK}; }}
    header[data-testid="stHeader"] * {{ color: #FFFFFF !important; }}

    /* تیتر اصلی */
    .main-title {{
        color: {BLUE_DARK};
        font-size: 2.1rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.2rem;
    }}
    .sub-title {{
        color: {BLUE};
        text-align: center;
        font-size: 1.05rem;
        margin-bottom: 1.2rem;
    }}

    /* کارت‌های KPI */
    [data-testid="stMetric"] {{
        background: {BLUE_LIGHT};
        border: 1px solid #BBDEFB;
        border-radius: 12px;
        padding: 12px;
    }}
    [data-testid="stMetricLabel"] {{ color: {BLUE_DARK} !important; }}
    [data-testid="stMetricValue"] {{ color: {BLUE} !important; }}

    /* دکمه‌ها */
    .stButton button {{
        background-color: {BLUE};
        color: #FFFFFF;
        border-radius: 10px;
        border: none;
        font-weight: 700;
    }}
    .stButton button:hover {{ background-color: {BLUE_DARK}; }}

    /* سایدبار */
    [data-testid="stSidebar"] {{ background-color: {BLUE_LIGHT}; }}
</style>
""", unsafe_allow_html=True)

# ---------------- بارگذاری داده و سرویس‌ها ----------------
@st.cache_data
def load_data():
    with open("data/rural_nodes.json", "r", encoding="utf-8") as f:
        return json.load(f)

data = load_data()
engine = RoutingEngine(nodes=data)

if "sim" not in st.session_state:
    st.session_state.sim = FleetSimulator(data["fleet"])
if "queue" not in st.session_state:
    st.session_state.queue = []          # درخواست‌های در انتظار تخصیص
if "energy_savings" not in st.session_state:
    st.session_state.energy_savings = 0.0

sim = st.session_state.sim

# ---------------- سربرگ ----------------
st.markdown('<div class="main-title">🚐 K-Rural-Mobility</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">پلتفرم حمل‌ونقل خودران درخواستی برای سالمندان مناطق روستایی کره جنوبی</div>',
            unsafe_allow_html=True)

# ---------------- ستون‌ها ----------------
col_map, col_panel = st.columns([3, 2])

# ============ ستون راست: پنل سفارش و KPI ============
with col_panel:
    st.subheader("🎙️ سفارش سفر سالمند (شبیه‌سازی صوتی)")

    sample = st.selectbox("عبارت نمونه صوتی:", SAMPLE_PHRASES)
    custom = st.text_input("یا متن خود را بنویسید:", placeholder="مثلاً: می‌خواهم به درمانگاه محلی بروم")
    text = custom.strip() if custom.strip() else sample

    if st.button("📡 پردازش درخواست و افزودن به صف"):
        req = parse_request(text, nodes=data)
        if req["valid"]:
            st.session_state.queue.append(req)
            st.success(f"✅ درخواست ثبت شد: {req['origin_name']} ← {req['destination_name']} | مسافر: {req['passengers']}")
        else:
            st.error("❌ مقصد در متن شناسایی نشد؛ لطفاً نام یکی از ایستگاه‌ها را ذکر کنید.")

    st.divider()
    st.subheader("🗺️ صف درخواست‌ها")
    if st.session_state.queue:
        df_q = pd.DataFrame([{
            "مبدأ": r["origin_name"], "مقصد": r["destination_name"],
            "مسافر": r["passengers"]} for r in st.session_state.queue])
        st.dataframe(df_q, use_container_width=True, hide_index=True)
    else:
        st.info("صف خالی است — یک درخواست ثبت کنید.")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("⚡ تخصیص بهینه به ناوگان"):
            if st.session_state.queue:
                fleet_state = [{"id": vid, "lat": v.lat, "lng": v.lng}
                               for vid, v in sim.vehicles.items()]
                result = engine.assign(st.session_state.queue, fleet_state)
                for vid, route in result["routes"].items():
                    if route["stops"]:
                        sim.vehicles[vid].assign_route(route["stops"], route["passengers"])
                st.session_state.energy_savings = result["energy_savings_pct"]
                st.session_state.queue = result["unassigned"]
                st.success(f"تخصیص انجام شد | مسافت کل: {result['total_distance_km']} km")
                if result["unassigned"]:
                    st.warning(f"{len(result['unassigned'])} درخواست به‌علت ظرفیت باقی ماند.")
            else:
                st.warning("صف درخواست خالی است.")

    with c2:
        if st.button("▶️ تیک زمانی شبیه‌سازی"):
            sim.tick(engine.coords)
            st.toast("شبیه‌سازی یک تیک جلو رفت 🚐")

    st.divider()
    st.subheader("📊 آمار و KPIها")
    k = sim.kpis()
    k1, k2, k3 = st.columns(3)
    k1.metric("سفرهای انجام‌شده", k["completed_trips"])
    k2.metric("میانگین انتظار (ثانیه)", k["avg_wait_seconds"])
    k3.metric("صرفه‌جویی انرژی (٪)", st.session_state.energy_savings)
    k4, k5, k6 = st.columns(3)
    k4.metric("ناوگان فعال", f"{k['fleet_active']}/{k['fleet_size']}")
    k5.metric("در حال شارژ", k["fleet_charging"])
    k6.metric("مسافت کل (km)", k["total_distance_km"])

# ============ ستون چپ: نقشه زنده ============
with col_map:
    st.subheader("🗺️ نقشه زنده ناوگان و ایستگاه‌ها")
    center = [37.49, 127.55]
    m = folium.Map(location=center, zoom_start=10, tiles="CartoDB positron")

    # ایستگاه‌ها
    for s in data["stations"]:
        color = {"hub": "darkblue", "health": "red", "admin": "orange",
                 "welfare": "green", "rural": "blue"}[s["type"]]
        folium.Marker(
            [s["lat"], s["lng"]],
            popup=f"{s['name_en']} — {s['name_fa']}",
            tooltip=s["name_en"],
            icon=folium.Icon(color=color, icon="info-sign"),
        ).add_to(m)

    # وضعیت لحظه‌ای خودروها
    snap = sim.snapshot()
    for vid, v in snap.items():
        if v["status"] == "moving" and sim.vehicles[vid].stops:
            poly = engine.route_polyline(sim.vehicles[vid].stops, v["lat"], v["lng"])
            folium.PolyLine(poly, color=BLUE, weight=4, opacity=0.8).add_to(m)
        icon_color = "blue" if v["status"] == "moving" else (
                      "green" if v["status"] == "idle" else "purple")
        folium.Marker(
            [v["lat"], v["lng"]],
            popup=(f"{vid} | باتری: {v['battery']}% | مسافر: {v['passengers']}/2 | "
                   f"وضعیت: {v['status']}"),
            tooltip=vid,
            icon=folium.Icon(color=icon_color, icon="car", prefix="fa"),
        ).add_to(m)

    st_folium(m, width=None, height=520, key="live_map")

    # جدول وضعیت ناوگان
    st.subheader("🚐 وضعیت ناوگان")
    df_f = pd.DataFrame([
        {"خودرو": vid, "باتری ٪": v["battery"], "مسافر": f'{v["passengers"]}/2',
         "وضعیت": v["status"], "توقف بعدی": v["next_stop"] or "—"}
        for vid, v in snap.items()])
    st.dataframe(df_f, use_container_width=True, hide_index=True)

# ---------------- به‌روزرسانی خودکار نقشه ----------------
time.sleep(1.5)
sim.tick(engine.coords)
