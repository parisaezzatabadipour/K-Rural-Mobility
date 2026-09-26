# -*- coding: utf-8 -*-
"""
K-Rural-Mobility — اپ درخواست سفر سه‌زبانه (فارسی / English / 한국어)
نسخه اصلی: فقط پایتون خام، بدون هیچ نصبی.  →  python app.py
طراحی: کیوت و پاستیلی در سبک اپ‌های کره‌ای
"""
import http.server
import socketserver
import webbrowser
import threading

PORT = 8000

HTML = r"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>K-Rural-Mobility | K-루럴 모빌리티</title>
<style>
:root{
  --bg:#F0F7FF; --card:#FFFFFF; --ink:#22406B; --ink2:#5B7CA6; --ink3:#8FA8C6;
  --blue:#4A9BEB; --blue-d:#2F7FD6; --blue-l:#DBEAFE; --blue-xl:#EEF6FF;
  --pink:#F9A8D4; --mint:#5EEAD4; --sun:#FCD34D; --line:#D6E7FA;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:'Segoe UI',Tahoma,'Malgun Gothic','Apple SD Gothic Neo',sans-serif;}
.wrap{max-width:1180px;margin:0 auto;padding:18px 16px 30px;display:flex;flex-direction:column;gap:16px}
/* ---------- top bar ---------- */
.topbar{display:flex;align-items:center;gap:12px;flex-wrap:wrap;
  background:var(--card);border:1px solid var(--line);border-radius:22px;
  padding:12px 18px;box-shadow:0 6px 20px rgba(74,155,235,.12)}
.logo{display:flex;align-items:center;gap:10px}
.logo b{font-size:19px;color:var(--blue-d)}
.logo small{display:block;font-size:11px;color:var(--ink3)}
.langs{margin-inline-start:auto;display:flex;gap:6px;background:var(--blue-xl);
  border-radius:999px;padding:4px;border:1px solid var(--line)}
.langs button{border:none;background:transparent;color:var(--ink2);
  border-radius:999px;padding:6px 14px;font-size:13px;cursor:pointer;font-family:inherit;transition:all .18s}
.langs button.on{background:var(--blue);color:#fff;box-shadow:0 3px 10px rgba(74,155,235,.4)}
/* ---------- layout ---------- */
.grid{display:grid;grid-template-columns:1.5fr 1fr;gap:16px}
@media(max-width:880px){.grid{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid var(--line);border-radius:22px;
  padding:16px;box-shadow:0 6px 20px rgba(74,155,235,.10)}
.mapbox{position:relative;padding:0;overflow:hidden}
canvas{display:block;width:100%;height:560px}
.maphint{position:absolute;top:10px;inset-inline-start:10px;font-size:11.5px;color:var(--ink2);
  background:rgba(255,255,255,.9);border:1px solid var(--line);border-radius:999px;padding:5px 12px}
.legend{position:absolute;bottom:10px;inset-inline-start:10px;display:flex;gap:10px;flex-wrap:wrap;
  font-size:11px;color:var(--ink2);background:rgba(255,255,255,.92);
  border:1px solid var(--line);border-radius:999px;padding:5px 14px}
.legend i{display:inline-block;width:9px;height:9px;border-radius:50%;margin-inline-end:4px;vertical-align:middle}
/* ---------- app card ---------- */
.app{display:flex;flex-direction:column;gap:12px}
.sec{font-size:12.5px;color:var(--ink3);font-weight:600}
.vrow{display:flex;gap:10px;align-items:center}
.mic{width:50px;height:50px;flex:0 0 50px;border-radius:50%;border:none;background:var(--blue);
  color:#fff;font-size:20px;cursor:pointer;position:relative;transition:transform .15s;box-shadow:0 5px 14px rgba(74,155,235,.45)}
.mic:hover{transform:scale(1.08)}
.mic:active{transform:scale(.94)}
.mic.listen::after{content:"";position:absolute;inset:-7px;border-radius:50%;
  border:3px solid var(--blue);animation:ring 1.1s infinite}
@keyframes ring{0%{transform:scale(.75);opacity:.9}100%{transform:scale(1.4);opacity:0}}
input,select{width:100%;border:2px solid var(--line);border-radius:14px;padding:10px 12px;
  font-size:13.5px;background:var(--blue-xl);color:var(--ink);font-family:inherit;outline:none;transition:border-color .15s}
input:focus,select:focus{border-color:var(--blue)}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.btn{border:none;border-radius:16px;padding:13px 16px;font-size:15px;cursor:pointer;
  font-family:inherit;font-weight:700;transition:all .15s}
.btn.blue{background:var(--blue);color:#fff;box-shadow:0 6px 16px rgba(74,155,235,.4)}
.btn.blue:hover{background:var(--blue-d);transform:translateY(-2px)}
.btn.blue:active{transform:scale(.97)}
.btn.ghost{background:var(--blue-l);color:var(--blue-d)}
.btn:disabled{opacity:.45;cursor:not-allowed;transform:none}
.farebox{background:linear-gradient(135deg,var(--blue-xl),#FDF3FF);border:2px dashed var(--blue);
  border-radius:16px;padding:10px 14px;font-size:13px;color:var(--ink2);text-align:center}
.farebox b{color:var(--blue-d)}
.status{min-height:10px}
.dcard{display:flex;flex-direction:column;gap:10px;border:2px solid var(--blue-l);
  border-radius:18px;padding:14px;background:linear-gradient(180deg,#fff,var(--blue-xl));
  animation:pop .35s cubic-bezier(.34,1.56,.64,1)}
@keyframes pop{0%{transform:scale(.85);opacity:0}100%{transform:scale(1);opacity:1}}
.dhead{display:flex;align-items:center;gap:12px}
.dav{width:52px;height:52px;flex:0 0 52px;border-radius:18px;background:var(--blue);
  display:flex;align-items:center;justify-content:center;font-size:24px;box-shadow:0 4px 12px rgba(74,155,235,.4)}
.dhead b{font-size:15px}
.dhead .sub{font-size:11.5px;color:var(--ink3)}
.eta{font-size:30px;font-weight:800;text-align:center;color:var(--blue-d);
  font-variant-numeric:tabular-nums;background:var(--blue-l);border-radius:14px;padding:8px}
.dots{display:flex;gap:6px;justify-content:center;padding:6px 0}
.dots i{width:9px;height:9px;border-radius:50%;background:var(--blue);animation:bnc 1s infinite}
.dots i:nth-child(2){animation-delay:.15s}.dots i:nth-child(3){animation-delay:.3s}
@keyframes bnc{0%,100%{transform:translateY(0);opacity:.4}50%{transform:translateY(-7px);opacity:1}}
.banner{border-radius:14px;padding:10px 14px;font-size:13.5px;font-weight:700;text-align:center;
  background:#E7FBF3;color:#0E9F6E;border:2px solid #B9F2DC;animation:pop .3s}
.prog{height:10px;border-radius:999px;background:var(--blue-l);overflow:hidden}
.prog i{display:block;height:100%;border-radius:999px;background:linear-gradient(90deg,var(--blue),var(--pink));transition:width .25s linear}
.rcp{width:100%;border-collapse:collapse;font-size:13.5px}
.rcp td{padding:8px 2px;border-bottom:1.5px dashed var(--line)}
.rcp td:last-child{text-align:end;font-variant-numeric:tabular-nums;font-weight:600}
.rcp tr.tot td{font-size:17px;font-weight:800;color:var(--blue-d);border-bottom:none}
.note{font-size:11px;color:var(--ink3);text-align:center}
.foot{text-align:center;font-size:12px;color:var(--ink3)}
.spark{display:inline-block;animation:spk 1.6s infinite}
@keyframes spk{0%,100%{transform:scale(1) rotate(0)}50%{transform:scale(1.25) rotate(15deg)}}
</style>
</head>
<body>
<div class="wrap">
  <div class="topbar">
    <div class="logo">
      <svg width="46" height="34" viewBox="0 0 46 34"><rect x="2" y="4" width="42" height="24" rx="12" fill="#4A9BEB"/><rect x="8" y="9" width="12" height="9" rx="4.5" fill="#EAF4FF"/><rect x="24" y="9" width="12" height="9" rx="4.5" fill="#EAF4FF"/><circle cx="17" cy="18" r="2.2" fill="#22406B"/><circle cx="29" cy="18" r="2.2" fill="#22406B"/><path d="M19 22 q4 3 8 0" stroke="#22406B" stroke-width="1.8" fill="none" stroke-linecap="round"/><circle cx="12" cy="21" r="2.4" fill="#F9A8D4" opacity=".85"/><circle cx="34" cy="21" r="2.4" fill="#F9A8D4" opacity=".85"/><circle cx="8" cy="30" r="4" fill="#22406B"/><circle cx="38" cy="30" r="4" fill="#22406B"/><circle cx="8" cy="30" r="1.7" fill="#B9CBE0"/><circle cx="38" cy="30" r="1.7" fill="#B9CBE0"/></svg>
      <div><b>K-Rural-Mobility</b><small id="tag"></small></div>
    </div>
    <div class="langs" id="langs">
      <button data-l="fa" class="on">🇮🇷 فارسی</button>
      <button data-l="en">🇺🇸 EN</button>
      <button data-l="ko">🇰🇷 한국어</button>
    </div>
  </div>

  <div class="grid">
    <div class="card mapbox">
      <canvas id="cv"></canvas>
      <div class="maphint" id="mapHint"></div>
      <div class="legend" id="legend"></div>
    </div>

    <div class="card app">
      <div class="sec" id="secVoice"></div>
      <div class="vrow">
        <button class="mic" id="mic">🎤</button>
        <div style="flex:1">
          <input id="vIn" readonly>
          <div class="note" id="vHint" style="text-align:start"></div>
        </div>
      </div>
      <div class="row2">
        <select id="selP"></select>
        <select id="selD"></select>
      </div>
      <div class="farebox" id="fareBox"></div>
      <button class="btn blue" id="btnReq" disabled></button>
      <button class="btn ghost" id="btnCancel" style="display:none"></button>
      <div class="status" id="status"></div>
    </div>
  </div>

  <div class="foot" id="foot"></div>
</div>

<script>
/* ================= DATA ================= */
var ST=[
 {id:"ST01",n:{fa:"ایستگاه مرکزی",en:"Yangpyeong Stn.",ko:"양평역"},lat:37.4886,lng:127.5467,t:"hub"},
 {id:"ST02",n:{fa:"درمانگاه محلی",en:"Local Clinic",ko:"보건진료소"},lat:37.4901,lng:127.5428,t:"health"},
 {id:"ST03",n:{fa:"مرکز دهیاری",en:"Town Office",ko:"면사무소"},lat:37.4923,lng:127.5458,t:"admin"},
 {id:"ST04",n:{fa:"رفاه سالمندان",en:"Senior Center",ko:"노인복지관"},lat:37.4880,lng:127.5400,t:"welfare"},
 {id:"ST05",n:{fa:"ایستگاه اوکچئون",en:"Okcheon",ko:"옥천면"},lat:37.5360,lng:127.6530,t:"rural"},
 {id:"ST06",n:{fa:"ایستگاه دان‌وُل",en:"Danwol",ko:"단월면"},lat:37.6900,lng:127.6200,t:"rural"},
 {id:"ST07",n:{fa:"ایستگاه چئونگون",en:"Cheongun",ko:"청울면"},lat:37.6050,lng:127.5800,t:"rural"},
 {id:"ST08",n:{fa:"ایستگاه گانگ‌ها",en:"Gangha",ko:"강하면"},lat:37.4150,lng:127.4600,t:"rural"},
 {id:"ST09",n:{fa:"ایستگاه یونگمون",en:"Yongmun",ko:"용문면"},lat:37.2950,lng:127.5700,t:"rural"}];
var KW=[
 ["ST02",["درمانگاه","clinic","hospital","보건","병원","진료소"]],
 ["ST04",["رفاه سالمندان","سالمندان","senior","welfare","노인복지","노인"]],
 ["ST05",["اوکچئ","okcheon","옥천"]],
 ["ST06",["دان‌وُل","دانوول","danwol","단월"]],
 ["ST07",["چئونگون","cheongun","청운"]],
 ["ST08",["گانگ","gangha","강하"]],
 ["ST09",["یونگمون","yongmun","용문"]],
 ["ST01",["ایستگاه مرکزی","yangpyeong station","양평역"]],
 ["ST03",["دهیاری","town office","면사무소","읍사무소"]]];
var PH={
 fa:["می‌خواهم به درمانگاه محلی بروم","می‌خوام برم مرکز رفاه سالمندان","می‌خوام برم ایستگاه یونگمون","می‌خواهم به ایستگاه گانگ‌ها بروم"],
 en:["I want to go to the local clinic","take me to the senior welfare center","I want to go to Yongmun station","go to Gangha station please"],
 ko:["보건진료소에 가고 싶어요","노인복지관으로 가주세요","용문면 역으로 가고 싶어요","강하면으로 가주세요"]};

/* ================= I18N ================= */
var T={
 fa:{dir:"rtl",tag:"پلتفرم سفر خودران برای سالمندان روستاهای کره",
  mapHint:"روی نقشه بزن: اول مبدأ، بعد مقصد",lgU:"شما",lgP:"مبدأ",lgD:"مقصد",lgS:"ایستگاه",
  secVoice:"سفر با صدا — مثل یک تماس ساده",
  micHint:"دکمه میکروفون را بزن و مقصدت را بگو",micListen:"در حال گوش دادن…",micDone:"صدا تشخیص داده شد ✓",
  selP:"انتخاب مبدأ…",selD:"انتخاب مقصد…",noFare:"مبدأ و مقصد را انتخاب کن تا کرایه را ببینی",
  fare:"مسافت ≈ {d} km | زمان ≈ {m} دقیقه | کرایه ≈ {f} وون",
  req:"درخواست کپسول خودران 🚐",cancel:"لغو درخواست",
  searching:"در حال یافتن نزدیک‌ترین کپسول…",plate:"پلاک KR-4821",cap:"ظرفیت ۲ نفر",stars:"امتیاز {r}",
  etaCome:"{s} ثانیه تا رسیدن کپسول",etaGo:"{s} ثانیه تا مقصد",coming:"کپسول در راه است…",
  arrived:"کپسول رسید! در {p} منتظر توست",board:"سوار شو و بریم ←",
  riding:"در حال حرکت به سمت {d}",dist:"مسافت سفر: {d} km",
  rcpT:"رسید سفر 🎉",rcpFrom:"مبدأ ← مقصد",rcpDist:"مسافت",rcpBase:"کرایه پایه",rcpKm:"کرایه مسافت",
  rcpTot:"جمع کل",rcpCO:"صرفه‌جویی CO₂ نسبت به خودروی شخصی",newRide:"سفر جدید",
  noAv:"کپسول آزادی در نزدیکی نیست — دوباره تلاش کن",
  foot:"ساخته‌شده با عشق برای سالمندان روستاهای کره • K-Rural-Mobility",
  busy:"در سفر"},
 en:{dir:"ltr",tag:"Autonomous ride platform for rural Korean seniors",
  mapHint:"Tap the map: pickup first, then destination",lgU:"You",lgP:"Pickup",lgD:"Drop-off",lgS:"Station",
  secVoice:"Ride by voice — as easy as a call",
  micHint:"Tap the mic and say where you want to go",micListen:"Listening…",micDone:"Voice recognized ✓",
  selP:"Choose pickup…",selD:"Choose destination…",noFare:"Pick pickup & destination to see the fare",
  fare:"Distance ≈ {d} km | Time ≈ {m} min | Fare ≈ {f} KRW",
  req:"Request AV capsule 🚐",cancel:"Cancel request",
  searching:"Finding the nearest capsule…",plate:"Plate KR-4821",cap:"Seats 2",stars:"Rating {r}",
  etaCome:"Capsule arrives in {s}s",etaGo:"{s}s to destination",coming:"Your capsule is on the way…",
  arrived:"Capsule arrived! Waiting at {p}",board:"Board & go ←",
  riding:"Heading to {d}",dist:"Trip distance: {d} km",
  rcpT:"Trip receipt 🎉",rcpFrom:"Pickup ← Drop-off",rcpDist:"Distance",rcpBase:"Base fare",rcpKm:"Distance fare",
  rcpTot:"Total",rcpCO:"CO₂ saved vs private car",newRide:"New ride",
  noAv:"No capsule nearby — try again",
  foot:"Made with ♡ for rural Korean seniors • K-Rural-Mobility",
  busy:"on trip"},
 ko:{dir:"ltr",tag:"한국 농촌 어르신을 위한 자율주행 콜택시",
  mapHint:"지도를 누르세요: 먼저 출발지, 다음 도착지",lgU:"나",lgP:"출발지",lgD:"도착지",lgS:"정류장",
  secVoice:"음성으로 부르는 콜택시",
  micHint:"마이크를 누르고 가실 곳을 말핵세요",micListen:"듣는 중…",micDone:"음성 인식 완료 ✓",
  selP:"출발지 선택…",selD:"도착지 선택…",noFare:"출발지와 도착지를 고를면 요금이 표시됩니다",
  fare:"거리 ≈ {d} km | 시간 ≈ {m} 분 | 요금 ≈ {f} 원",
  req:"자율주행 캡슐 호출하기 🚐",cancel:"호출 취소",
  searching:"가장 가까운 캡슐을 찾는 중…",plate:"번호판 KR-4821",cap:"2인승",stars:"평점 {r}",
  etaCome:"캡슐 도착까지 {s}초",etaGo:"도착까지 {s}초",coming:"캡슐이 오고 있어요…",
  arrived:"캡슐 도착! {p}에서 기다리고 있어요",board:"탑승하고 출발 ←",
  riding:"{d}(으)로 이동 중",dist:"이동 거리: {d} km",
  rcpT:"이용 내역 🎉",rcpFrom:"출발지 ← 도착지",rcpDist:"거리",rcpBase:"기본 요금",rcpKm:"거리 요금",
  rcpTot:"총액",rcpCO:"승용차 대비 CO₂ 절감",newRide:"새로운 여정",
  noAv:"주변에 캡슐이 없어요 — 다시 시도해 주세요",
  foot:"한국 농촌 어르신을 위해 사랑을 담아 제작 • K-Rural-Mobility",
  busy:"운행 중"}};

var lang="fa";
function t(k){return T[lang][k]}
function nm(s){return s.n[lang]}
function num(v,d){var s=d?v.toFixed(d):String(v);
  if(lang==="fa")return s.replace(/\d/g,function(c){return "۰۱۲۳۴۵۶۷۸۹"[c]});
  return s}
function money(n){if(lang==="fa")return num(n.toLocaleString())+" وون";
  if(lang==="ko")return num(n.toLocaleString())+" 원";return num(n.toLocaleString())+" KRW"}

/* ================= helpers ================= */
var byId={};ST.forEach(function(s){byId[s.id]=s});
function dKm(a,b){var dx=(a.lat-b.lat)*111,dy=(a.lng-b.lng)*88;return Math.sqrt(dx*dx+dy*dy)}
function fareOf(d){return Math.round((3000+d*1300)/100)*100}
var AVS=[
 {id:"AV-01",lat:37.4886,lng:127.5467,busy:false,r:{fa:"۴٫۹",en:"4.9",ko:"4.9"}},
 {id:"AV-02",lat:37.5360,lng:127.6530,busy:false,r:{fa:"۴٫۸",en:"4.8",ko:"4.8"}},
 {id:"AV-03",lat:37.4150,lng:127.4600,busy:false,r:{fa:"۵٫۰",en:"5.0",ko:"5.0"}}];

var S={phase:"idle",pickup:"ST01",dest:null,av:null,eta:0,dist:0,fare:0,prog:0,step:0};
var cv=document.getElementById("cv"),ctx=cv.getContext("2d");
var MINL=127.44,MAXL=127.67,MINA=37.27,MAXA=37.71,lastT=performance.now();
function X(l){return 26+(l-MINL)/(MAXL-MINL)*(cv.clientWidth-52)}
function Y(a){return 20+(MAXA-a)/(MAXA-MINA)*(cv.clientHeight-60)}

/* ================= i18n render ================= */
var selP=document.getElementById("selP"),selD=document.getElementById("selD");
function buildSelects(){
 selP.innerHTML="";selD.innerHTML="";
 selP.insertAdjacentHTML("beforeend",'<option value="">'+t("selP")+'</option>');
 selD.insertAdjacentHTML("beforeend",'<option value="">'+t("selD")+'</option>');
 ST.forEach(function(s){
  selP.insertAdjacentHTML("beforeend",'<option value="'+s.id+'">📍 '+nm(s)+'</option>');
  selD.insertAdjacentHTML("beforeend",'<option value="'+s.id+'">🎯 '+nm(s)+'</option>');});
 selP.value=S.pickup||"";selD.value=S.dest||"";}
function renderStatic(){
 document.documentElement.lang=lang;
 document.documentElement.dir=t("dir");
 document.getElementById("tag").textContent=t("tag");
 document.getElementById("mapHint").textContent=t("mapHint");
 document.getElementById("legend").innerHTML=
  '<span><i style="background:#4A9BEB"></i>'+t("lgU")+' / AV</span>'+
  '<span><i style="background:#22c55e"></i>'+t("lgP")+'</span>'+
  '<span><i style="background:#ef4444"></i>'+t("lgD")+'</span>'+
  '<span><i style="background:#94a3b8"></i>'+t("lgS")+'</span>';
 document.getElementById("secVoice").textContent=t("secVoice");
 document.getElementById("vHint").textContent=t("micHint");
 document.getElementById("btnReq").textContent=t("req");
 document.getElementById("btnCancel").textContent=t("cancel");
 document.getElementById("foot").innerHTML='<span class="spark">✨</span> '+t("foot")+' <span class="spark">✨</span>';
 buildSelects();refreshFare();}
document.getElementById("langs").addEventListener("click",function(e){
 var b=e.target.closest("button");if(!b)return;
 lang=b.dataset.l;
 document.querySelectorAll("#langs button").forEach(function(x){x.classList.toggle("on",x===b)});
 renderStatic();renderStatus();});

/* ================= selection & fare ================= */
function refreshFare(){
 var fb=document.getElementById("fareBox");
 if(S.pickup&&S.dest&&S.pickup!==S.dest){
  S.dist=dKm(byId[S.pickup],byId[S.dest]);S.fare=fareOf(S.dist);
  fb.innerHTML=t("fare").replace("{d}",num(S.dist.toFixed(1)))
    .replace("{m}",num(Math.max(1,Math.round(S.dist/110*60))))
    .replace("{f}",money(S.fare));
  document.getElementById("btnReq").disabled=false;
 }else{fb.textContent=t("noFare");document.getElementById("btnReq").disabled=true;}}
selP.onchange=function(){S.pickup=selP.value||null;S.step=S.pickup?1:0;refreshFare()};
selD.onchange=function(){S.dest=selD.value||null;S.step=S.dest?2:(S.pickup?1:0);refreshFare()};

cv.addEventListener("click",function(e){
 if(S.phase!=="idle")return;
 var r=cv.getBoundingClientRect(),mx=e.clientX-r.left,my=e.clientY-r.top,best=null,bd=1e9;
 ST.forEach(function(s){var dx=X(s.lng)-mx,dy=Y(s.lat)-my,d=dx*dx+dy*dy;if(d<bd){bd=d;best=s}});
 if(!best)return;
 if(!S.pickup||S.step===0){S.pickup=best.id;selP.value=best.id;S.step=1;refreshFare();return}
 if(S.step===1&&best.id!==S.pickup){S.dest=best.id;selD.value=best.id;S.step=2;refreshFare();return}
 if(S.step===2){S.pickup=best.id;selP.value=best.id;S.step=1;S.dest=null;selD.value="";refreshFare();}});

/* ================= voice ================= */
var mic=document.getElementById("mic"),vIn=document.getElementById("vIn"),vHint=document.getElementById("vHint");
mic.onclick=function(){
 if(S.phase!=="idle")return;
 mic.classList.add("listen");vHint.textContent=t("micListen");
 var list=PH[lang],ph=list[Math.floor(Math.random()*list.length)],i=0;vIn.value="";
 setTimeout(function type(){
  if(i<ph.length){vIn.value+=ph[i++];setTimeout(type,42)}
  else setTimeout(function(){
   mic.classList.remove("listen");vHint.textContent=t("micDone");
   var dest=null;
   outer:for(var k=0;k<KW.length;k++){for(var j=0;j<KW[k][1].length;j++){
    if(ph.toLowerCase().indexOf(KW[k][1][j].toLowerCase())>-1){dest=KW[k][0];break outer}}}
   if(dest){S.dest=dest;selD.value=dest;S.step=2;refreshFare();}
  },450)},1100);};

/* ================= status rendering ================= */
var stEl=document.getElementById("status");
var btnReq=document.getElementById("btnReq"),btnCancel=document.getElementById("btnCancel");
function renderStatus(){
 if(S.phase==="idle"){stEl.innerHTML="";btnReq.style.display="";btnCancel.style.display="none";return}
 btnReq.style.display="none";btnCancel.style.display="";
 if(S.phase==="searching"){
  stEl.innerHTML='<div class="dcard"><div class="dots"><i></i><i></i><i></i></div>'+
   '<div class="note" style="font-size:13.5px;font-weight:700;color:var(--ink2)">'+t("searching")+'</div></div>';}
 else if(S.phase==="arriving"||S.phase==="arrived"||S.phase==="riding"){
  if(S.phase==="arriving"){
   stEl.innerHTML='<div class="dcard"><div class="dhead"><div class="dav">🚐</div><div>'+
    '<b>'+S.av.id+' · '+(lang==="ko"?"자율주행 캡슐":lang==="fa"?"کپسول خودران":"AV Capsule")+'</b>'+
    '<div class="sub">'+t("plate")+' · ⭐ '+t("stars").replace("{r}",S.av.r[lang])+' · '+t("cap")+'</div></div></div>'+
    '<div class="eta" id="eta"></div><div class="note">'+t("coming")+'</div></div>';}
  else if(S.phase==="arrived"){
   stEl.innerHTML='<div class="dcard"><div class="banner">🚐 '+t("arrived").replace("{p}",nm(byId[S.pickup]))+'</div>'+
    '<button class="btn blue" id="btnBoard">'+t("board")+'</button></div>';
   document.getElementById("btnBoard").onclick=beginRide;}
  else{
   stEl.innerHTML='<div class="dcard"><div class="banner">'+t("riding").replace("{d}",nm(byId[S.dest]))+'</div>'+
    '<div class="eta" id="eta"></div><div class="prog"><i id="pb"></i></div>'+
    '<div class="note">'+t("dist").replace("{d}",num(S.dist.toFixed(1)))+'</div></div>';}}}

/* ================= flow ================= */
btnReq.onclick=function(){
 if(!S.pickup||!S.dest||S.pickup===S.dest||S.phase!=="idle")return;
 S.phase="searching";renderStatus();
 setTimeout(function(){
  var best=null,bd=1e9;
  AVS.forEach(function(a){if(a.busy)return;var d=dKm(a,byId[S.pickup]);if(d<bd){bd=d;best=a}});
  if(!best){S.phase="idle";stEl.innerHTML='<div class="banner" style="background:#FEF3C7;color:#B45309;border-color:#FDE68A">'+t("noAv")+'</div>';btnReq.style.display="";btnCancel.style.display="none";return}
  best.busy=true;S.av=best;S.phase="arriving";
  S.eta=Math.max(8,Math.round(bd/110*3600));renderStatus();},1800);};
btnCancel.onclick=function(){
 if(S.av){S.av.busy=false;S.av=null}
 S.phase="idle";S.prog=0;renderStatus();refreshFare();};
function beginRide(){
 S.phase="riding";S.eta=Math.max(10,Math.round(S.dist/110*3600));S.prog=0;renderStatus();}
function finishRide(){
 S.phase="done";
 var co2=Math.round(S.dist*0.5*10)/10;
 stEl.innerHTML='<div class="dcard"><div style="text-align:center;font-weight:800;font-size:15.5px">'+t("rcpT")+'</div>'+
  '<table class="rcp">'+
  '<tr><td>'+t("rcpFrom")+'</td><td>'+nm(byId[S.pickup])+' ← '+nm(byId[S.dest])+'</td></tr>'+
  '<tr><td>'+t("rcpDist")+'</td><td>'+num(S.dist.toFixed(1))+' km</td></tr>'+
  '<tr><td>'+t("rcpBase")+'</td><td>'+money(3000)+'</td></tr>'+
  '<tr><td>'+t("rcpKm")+'</td><td>'+money(S.fare-3000)+'</td></tr>'+
  '<tr class="tot"><td>'+t("rcpTot")+'</td><td>'+money(S.fare)+'</td></tr>'+
  '<tr><td>'+t("rcpCO")+'</td><td>≈ '+num(co2)+' kg</td></tr></table>'+
  '<button class="btn blue" id="btnAgain">'+t("newRide")+' ✨</button></div>';
 document.getElementById("btnAgain").onclick=function(){
  if(S.av){S.av.busy=false;S.av=null}
  S.phase="idle";S.dest=null;S.prog=0;selD.value="";renderStatus();refreshFare();};}

/* ================= simulation ================= */
function step(dt){
 var sp=0.00032*dt*60;
 function mv(av,la,ln){var dx=la-av.lat,dy=ln-av.lng,d=Math.sqrt(dx*dx+dy*dy);
  if(d<=sp){av.lat=la;av.lng=ln;return true}av.lat+=dx/d*sp;av.lng+=dy/d*sp;return false}
 if(S.phase==="arriving"&&S.av){
  S.eta=Math.max(0,S.eta-dt);
  var e=document.getElementById("eta");if(e)e.textContent=t("etaCome").replace("{s}",num(Math.ceil(S.eta)));
  if(mv(S.av,byId[S.pickup].lat,byId[S.pickup].lng)){S.phase="arrived";renderStatus();}}
 else if(S.phase==="riding"&&S.av){
  S.eta=Math.max(0,S.eta-dt);
  var e2=document.getElementById("eta");if(e2)e2.textContent=t("etaGo").replace("{s}",num(Math.ceil(S.eta)));
  S.prog=Math.min(1,S.prog+dt/Math.max(S.dist/110*3600,1));
  var pb=document.getElementById("pb");if(pb)pb.style.width=(S.prog*100)+"%";
  if(mv(S.av,byId[S.dest].lat,byId[S.dest].lng))finishRide();}}

/* ================= drawing ================= */
function rr(x,y,w,h,r){ctx.beginPath();ctx.moveTo(x+r,y);ctx.arcTo(x+w,y,x+w,y+h,r);
 ctx.arcTo(x+w,y+h,x,y+h,r);ctx.arcTo(x,y+h,x,y,r);ctx.arcTo(x,y,x+w,y,r);ctx.closePath()}
function draw(){
 var W=cv.clientWidth,H=560;
 cv.width=W*devicePixelRatio;cv.height=H*devicePixelRatio;
 ctx.setTransform(devicePixelRatio,0,0,devicePixelRatio,0,0);
 var g=ctx.createLinearGradient(0,0,0,H);
 g.addColorStop(0,"#FDFBFF");g.addColorStop(1,"#EAF4FF");
 ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
 /* soft clouds */
 ctx.fillStyle="rgba(255,255,255,.75)";
 [[.15,.2],[.55,.12],[.85,.3],[.35,.55],[.7,.68]].forEach(function(c,i){
  var cx=c[0]*W,cy=c[1]*H,p=performance.now()/900+i;
  cx+=Math.sin(p)*8;
  ctx.beginPath();ctx.arc(cx,cy,16,0,7);ctx.arc(cx+18,cy+4,12,0,7);ctx.arc(cx-18,cy+5,11,0,7);ctx.fill();});
 /* grid */
 ctx.strokeStyle="rgba(74,155,235,.10)";ctx.lineWidth=1;
 for(var i=1;i<10;i++){ctx.beginPath();ctx.moveTo(i*W/10,0);ctx.lineTo(i*W/10,H);ctx.stroke();
  ctx.beginPath();ctx.moveTo(0,i*H/10);ctx.lineTo(W,i*H/10);ctx.stroke();}
 /* preview route */
 if(S.pickup&&S.dest){
  ctx.strokeStyle="#4A9BEB";ctx.globalAlpha=.55;ctx.lineWidth=4;
  ctx.setLineDash([10,8]);ctx.lineDashOffset=-performance.now()/40;
  ctx.beginPath();ctx.moveTo(X(byId[S.pickup].lng),Y(byId[S.pickup].lat));
  ctx.lineTo(X(byId[S.dest].lng),Y(byId[S.dest].lat));ctx.stroke();ctx.setLineDash([]);ctx.globalAlpha=1;}
 /* live route */
 if((S.phase==="arriving"||S.phase==="arrived")&&S.av){
  ctx.strokeStyle="#2F7FD6";ctx.lineWidth=4.5;ctx.setLineDash([12,7]);ctx.lineDashOffset=-performance.now()/30;
  ctx.beginPath();ctx.moveTo(X(S.av.lng),Y(S.av.lat));ctx.lineTo(X(byId[S.pickup].lng),Y(byId[S.pickup].lat));ctx.stroke();ctx.setLineDash([]);}
 if(S.phase==="riding"&&S.av){
  ctx.strokeStyle="#2F7FD6";ctx.lineWidth=4.5;ctx.setLineDash([12,7]);ctx.lineDashOffset=-performance.now()/30;
  ctx.beginPath();ctx.moveTo(X(S.av.lng),Y(S.av.lat));ctx.lineTo(X(byId[S.dest].lng),Y(byId[S.dest].lat));ctx.stroke();ctx.setLineDash([]);}
 /* stations */
 ST.forEach(function(s){
  var x=X(s.lng),y=Y(s.lat),isP=s.id===S.pickup,isD=s.id===S.dest;
  if(isP||isD){var pu=performance.now()/450;
   ctx.beginPath();ctx.arc(x,y,14+Math.sin(pu)*3,0,7);
   ctx.strokeStyle=isP?"#22c55e":"#ef4444";ctx.globalAlpha=.45;ctx.lineWidth=3;ctx.stroke();ctx.globalAlpha=1;}
  ctx.beginPath();ctx.arc(x,y,isP||isD?9:6.5,0,7);
  ctx.fillStyle=isP?"#22c55e":isD?"#ef4444":"#fff";ctx.fill();
  ctx.lineWidth=3;ctx.strokeStyle=isP?"#22c55e":isD?"#ef4444":"#94a3b8";ctx.stroke();
  ctx.font="600 11.5px 'Segoe UI',Tahoma,sans-serif";ctx.fillStyle="#5B7CA6";ctx.textAlign="center";
  ctx.fillText(nm(s),x,y+(isP||isD?25:21));});
 /* capsules */
 AVS.forEach(function(a){
  var x=X(a.lng),y=Y(a.lat);
  ctx.save();ctx.translate(x,y);
  rr(-15,-10,30,20,10);ctx.fillStyle=a.busy?"#4A9BEB":"#B9CBE0";ctx.fill();
  ctx.lineWidth=2.5;ctx.strokeStyle="#fff";ctx.stroke();
  rr(-9,-6,7,6,3);ctx.fillStyle="#EAF4FF";ctx.fill();rr(2,-6,7,6,3);ctx.fill();
  if(a.busy){ctx.beginPath();ctx.arc(0,2,4.5,0.15*Math.PI,0.85*Math.PI);
   ctx.strokeStyle="#22406B";ctx.lineWidth=1.6;ctx.stroke();
   ctx.beginPath();ctx.arc(-6,0,1.3,0,7);ctx.arc(6,0,1.3,0,7);ctx.fillStyle="#22406B";ctx.fill();
   ctx.beginPath();ctx.arc(-11,2.5,1.8,0,7);ctx.arc(11,2.5,1.8,0,7);ctx.fillStyle="#F9A8D4";ctx.fill();}
  ctx.restore();
  ctx.font="700 11px 'Segoe UI',Tahoma,sans-serif";ctx.fillStyle="#22406B";ctx.textAlign="center";
  ctx.fillText(a.busy?a.id+" · "+t("busy"):a.id,x,y-17);});}

function loop(tm){
 var dt=Math.min((tm-lastT)/1000,0.1);lastT=tm;
 if(S.phase!=="idle")step(dt);
 draw();requestAnimationFrame(loop);}

renderStatic();
requestAnimationFrame(loop);
</script>
</body>
</html>"""


   
