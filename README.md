# K-Rural-Mobility | K-루럴 모빌리티

**فارسی:** پلتفرم سفر خودران برای سالمندان روستاهای کره جنوبی — سه‌زبانه (فارسی/English/한국어)
**English:** Autonomous ride-hailing platform for rural Korean seniors — trilingual (FA/EN/KR)
**한국어:** 한국 농촌 어르신을 위한 자율주행 콜택시 플랫폼 — 3개 국어 지원

## اجرا | Run | 실행
هیچ نصبی لازم نیست — فقط پایتون:
```
python app.py
```
No installation needed — just Python. No external libraries required.
외부 라이브러리 불필요 — Python만 있으면 됩니다.

سپس مرورگر روی http://localhost:8000 باز می‌شود.
Then open http://localhost:8000 in your browser.
브라우저에서 http://localhost:8000 을 열어주세요.

## امکانات | Features | 기능
- درخواست سفر با صدا (شبیه‌سازی) | Voice request (simulated) | 음성 호출 (시뮬레이션)
- انتخاب مبدأ/مقصد روی نقشه | Tap pickup & destination on map | 지도에서 출발지/도착지 선택
- تخصیص نزدیک‌ترین کپسول خودران | Nearest AV capsule matching | 가장 가까운 캡슐 매칭
- کرایه و صرفه‌جویی CO₂ | Fare & CO₂ savings | 요금 및 CO₂ 절감

## ساختار | Structure | 구조
```
data/rural_nodes.json     station data (Yangpyeong-gun)
modules/                  voice, routing, simulator logic
app.py                    main cute trilingual app (no deps)
streamlit_app.py          optional monitoring dashboard (needs pip)
requirements.txt          optional, only for streamlit_app.py
```
