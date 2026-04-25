import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import time
import math
import itertools
from PIL import Image
import os

st.set_page_config(page_title="MathErgy 212510", page_icon="⚡", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&family=Rajdhani:wght@300;400;600;700&display=swap');

  /* ── ARKA PLAN: koyu lacivert-petrol ── */
  .stApp {
    background: linear-gradient(135deg, #0b1120 0%, #0d1a2e 40%, #0a1a1f 70%, #071520 100%);
    font-family: 'Rajdhani', sans-serif;
  }

  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #081018 0%, #0c1828 100%);
    border-right: 1px solid rgba(0,255,200,0.18);
  }

  h1,h2,h3 { font-family:'Orbitron',sans-serif !important; letter-spacing:2px; }

  [data-testid="metric-container"] {
    background: linear-gradient(135deg,rgba(0,255,200,0.07),rgba(0,100,200,0.05));
    border: 1px solid rgba(0,255,200,0.22);
    border-radius: 12px; padding: 14px;
  }
  [data-testid="stMetricValue"] { font-family:'Share Tech Mono',monospace !important; color:#00ffc8 !important; font-size:1.4rem !important; }
  [data-testid="stMetricLabel"] { color:#7ecfff !important; font-size:0.8rem !important; letter-spacing:1px; }

  .stSlider>div>div>div>div { background:linear-gradient(90deg,#00ffc8,#0096ff) !important; }

  .stButton>button {
    background: linear-gradient(135deg,#00ffc8 0%,#0096ff 100%);
    color:#000 !important; font-family:'Orbitron',sans-serif !important;
    font-weight:700; font-size:0.88rem; letter-spacing:2px;
    border:none; border-radius:8px; padding:14px 36px; width:100%;
    box-shadow:0 0 20px rgba(0,255,200,0.3); transition:all 0.3s;
  }
  .stButton>button:hover { box-shadow:0 0 40px rgba(0,255,200,0.6); transform:translateY(-2px); }

  p, label, .stMarkdown { color:#c8d8e8 !important; font-family:'Rajdhani',sans-serif !important; }
  hr { border-color:rgba(0,255,200,0.15) !important; }

  .neon-line {
    height:2px;
    background:linear-gradient(90deg,transparent,#00ffc8,#0096ff,transparent);
    margin:8px 0 18px 0; border-radius:2px; box-shadow:0 0 8px rgba(0,255,200,0.5);
  }

  /* Bölüm başlığı kutusu */
  .section-header {
    font-family:'Orbitron',sans-serif; font-size:0.85rem; font-weight:700;
    color:#00ffc8; letter-spacing:3px;
    border-left:3px solid #00ffc8; padding-left:12px; margin:28px 0 14px 0;
  }

  .house-card {
    background:linear-gradient(135deg,rgba(0,255,200,0.04),rgba(0,80,200,0.04));
    border:1px solid rgba(0,255,200,0.15);
    border-radius:10px; padding:12px 16px; margin-bottom:8px;
  }
  .surplus-badge  { display:inline-block; background:rgba(0,255,200,0.15);  border:1px solid #00ffc8; color:#00ffc8; font-family:'Share Tech Mono',monospace; font-size:0.68rem; padding:2px 8px; border-radius:20px; }
  .deficit-badge  { display:inline-block; background:rgba(255,77,109,0.15); border:1px solid #ff4d6d; color:#ff4d6d; font-family:'Share Tech Mono',monospace; font-size:0.68rem; padding:2px 8px; border-radius:20px; }
  .balanced-badge { display:inline-block; background:rgba(255,209,102,0.15);border:1px solid #ffd166; color:#ffd166; font-family:'Share Tech Mono',monospace; font-size:0.68rem; padding:2px 8px; border-radius:20px; }

  .info-box {
    background:rgba(8,16,28,0.75); border:1px solid rgba(0,255,200,0.18);
    border-radius:12px; padding:20px; margin-top:14px;
  }

  /* Expander */
  details { background:rgba(8,16,28,0.6) !important; border-radius:8px !important; }
</style>
""", unsafe_allow_html=True)


# ─── LOGO ───────────────────────────────────
def show_logo():
    if os.path.exists("logo.png"):
        st.image(Image.open("logo.png"), width=170)
    else:
        st.markdown("""
        <div style="font-family:'Orbitron',sans-serif;font-size:1.4rem;color:#00ffc8;letter-spacing:4px;">
          ⚡ MATH<span style="color:#0096ff;">ERGY</span>
        </div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.63rem;color:#7ecfff;letter-spacing:3px;">
          212510 — SMART GRID SIMULATOR
        </div>""", unsafe_allow_html=True)


# ─── HESAPLAMALAR ───────────────────────────
def shapley_value(productions: np.ndarray, consumptions: np.ndarray) -> np.ndarray:
    n   = len(productions)
    net = productions - consumptions
    sv  = np.zeros(n)
    for perm in itertools.permutations(range(n)):
        coalition = set()
        for player in perm:
            before = max(sum(net[i] for i in coalition), 0.0)
            coalition.add(player)
            after  = max(sum(net[i] for i in coalition), 0.0)
            sv[player] += (after - before)
    return sv / math.factorial(n)


def nash_transfer(productions: np.ndarray, consumptions: np.ndarray) -> dict:
    net           = productions - consumptions
    surplus_mask  = net > 0
    deficit_mask  = net < 0
    total_surplus = net[surplus_mask].sum()
    total_deficit = abs(net[deficit_mask].sum())
    n = len(productions)
    tr = np.zeros(n); tg = np.zeros(n)
    if total_surplus > 0 and total_deficit > 0:
        covered = min(total_surplus, total_deficit)
        for i in range(n):
            if deficit_mask[i]:  tr[i] = covered * abs(net[i]) / total_deficit
            if surplus_mask[i]:  tg[i] = covered * net[i]      / total_surplus
    return {
        "net": net, "transfer_received": tr, "transfer_given": tg,
        "grid_draw": np.maximum(-net - tr, 0),
        "grid_feed": np.maximum( net - tg, 0),
        "final_balance": net + tr - tg,
    }


def hourly_profile(n_houses, panel_counts, panel_watt, consumption_kwh, solar_eff, city_sun):
    sun_curve = np.zeros(24)
    for h in range(8, 19):
        sun_curve[h] = math.sin(math.pi * (h - 8) / 10)
    s = sun_curve.sum()
    if s > 0: sun_curve /= s

    cons_profile = np.array([
        0.02,0.01,0.01,0.01,0.01,0.02,
        0.04,0.06,0.06,0.04,0.03,0.03,
        0.04,0.03,0.03,0.04,0.05,0.08,
        0.09,0.08,0.07,0.06,0.04,0.03
    ]); cons_profile /= cons_profile.sum()

    prod = np.zeros((n_houses, 24))
    cons = np.zeros((n_houses, 24))
    for i in range(n_houses):
        daily = panel_counts[i] * (panel_watt / 1000) * city_sun * solar_eff
        prod[i] = sun_curve * daily
        cons[i] = cons_profile * consumption_kwh[i]
    return prod, cons


PLOT_BG = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(8,16,30,0.88)",
    font=dict(family="Rajdhani,sans-serif", color="#c8d8e8", size=13),
    margin=dict(l=40, r=20, t=50, b=40),
    xaxis=dict(gridcolor="rgba(0,255,200,0.07)", zerolinecolor="rgba(0,255,200,0.12)"),
    yaxis=dict(gridcolor="rgba(0,255,200,0.07)", zerolinecolor="rgba(0,255,200,0.12)"),
)

HOUSE_NAMES = [
    "Ahmet Bey","Fatma Hanım","Mehmet Bey","Ayşe Hanım",
    "Ali Bey","Zeynep Hanım","Hasan Bey","Merve Hanım",
    "Emre Bey","Elif Hanım",
]


# ─── SIDEBAR ────────────────────────────────
with st.sidebar:
    show_logo()
    st.markdown('<div class="neon-line"></div>', unsafe_allow_html=True)

    st.markdown("### 🏘️ Mahalle Kurulumu")
    n_houses = st.slider("Ev Sayısı", 2, 10, 4, 1)

    st.markdown("---")
    st.markdown("### ☀️ Güneş Paneli")
    panel_watt = st.slider("Panel Gücü (Watt/panel)", 100, 600, 300, 50)
    solar_eff  = st.slider("Verimlilik (%)", 10, 25, 18, 1) / 100
    city_sun   = st.slider("Günlük Güneşlenme (saat)", 3, 9, 5, 1)

    st.markdown("---")
    st.markdown("### 🏠 Her Ev")
    st.caption("Panel sayısı ve günlük tüketim girin:")

    panel_counts    = []
    consumption_kwh = []

    for i in range(n_houses):
        name = HOUSE_NAMES[i] if i < len(HOUSE_NAMES) else f"Ev {i+1}"
        with st.expander(f"🏠 {name}", expanded=(i < 2)):
            pc = st.slider("Panel sayısı", 0, 20, max(1, 5 - i % 4), key=f"p_{i}")
            ck = st.slider("Tüketim (kWh/gün)", 1, 30, 8 + i % 5,   key=f"c_{i}")
            panel_counts.append(pc)
            consumption_kwh.append(float(ck))

    st.markdown("---")
    start_btn = st.button("⚡  SİMÜLASYONU BAŞLAT")


# ─── BAŞLIK ─────────────────────────────────
st.markdown("""
<div style="margin-bottom:4px;">
  <span style="font-family:'Orbitron',sans-serif;font-size:1.9rem;font-weight:900;
    color:#00ffc8;letter-spacing:5px;text-shadow:0 0 30px rgba(0,255,200,0.4);">
    MATH<span style="color:#0096ff;">ERGY</span>
  </span>
  <span style="font-family:'Share Tech Mono',monospace;font-size:0.68rem;
    color:#5a7a8a;letter-spacing:3px;margin-left:12px;">212510</span>
</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:1rem;color:#7ecfff;letter-spacing:2px;">
  Mahalle Ölçeğinde Akıllı Güneş Enerjisi Paylaşım Simülatörü
</div>
<div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:#3a5a6a;letter-spacing:2px;margin-top:2px;">
  Oyun Teorisi · Nash Dengesi · Shapley Değeri
</div>
""", unsafe_allow_html=True)
st.markdown('<div class="neon-line"></div>', unsafe_allow_html=True)

names = [HOUSE_NAMES[i] if i < len(HOUSE_NAMES) else f"Ev {i+1}" for i in range(n_houses)]

# ─── SİMÜLASYON ─────────────────────────────
if start_btn:
    with st.status("⚡ Simülasyon hesaplanıyor...", expanded=True) as status:
        st.write("☀️ Güneş üretim profilleri modelleniyor...")
        time.sleep(0.7)
        prod, cons = hourly_profile(n_houses, panel_counts, panel_watt,
                                    consumption_kwh, solar_eff, city_sun)
        daily_prod = prod.sum(axis=1)
        daily_cons = np.array(consumption_kwh)

        st.write("🤝 Nash Dengesi ile enerji transferleri hesaplanıyor...")
        time.sleep(0.8)
        eq = nash_transfer(daily_prod, daily_cons)

        st.write("🧮 Shapley Değerleri hesaplanıyor...")
        time.sleep(1.0)
        shapley = shapley_value(daily_prod, daily_cons)

        st.write("📊 Grafikler oluşturuluyor...")
        time.sleep(0.4)
        status.update(label="✅ Tamamlandı!", state="complete", expanded=False)

    # ── METRİKLER ──
    total_p = daily_prod.sum()
    total_c = daily_cons.sum()
    g_draw  = eq["grid_draw"].sum()
    g_feed  = eq["grid_feed"].sum()
    suff    = max(0.0, 1.0 - g_draw / (total_c + 1e-9)) * 100

    m1,m2,m3,m4,m5 = st.columns(5)
    m1.metric("☀️ Mahalle Üretimi",   f"{total_p:.1f} kWh/gün")
    m2.metric("🏠 Toplam Tüketim",    f"{total_c:.1f} kWh/gün")
    m3.metric("🔌 Şebekeden Çekilen", f"{g_draw:.1f} kWh/gün")
    m4.metric("↗️ Şebekeye Verilen",  f"{g_feed:.1f} kWh/gün")
    m5.metric("🌱 Öz Yeterlilik",     f"{suff:.1f}%")

    # ════════════════════════════════════════
    # BÖLÜM 1 — EV BAZLI DURUM
    # ════════════════════════════════════════
    st.markdown('<div class="section-header">01 — EV BAZLI ENERJİ DURUMU</div>', unsafe_allow_html=True)

    df = pd.DataFrame({
        "Ev":                    names,
        "Panel":                 panel_counts,
        "Üretim (kWh)":          daily_prod.round(2),
        "Tüketim (kWh)":         daily_cons.round(2),
        "Net (kWh)":             eq["net"].round(2),
        "Komşudan Aldı (kWh)":   eq["transfer_received"].round(2),
        "Komşuya Verdi (kWh)":   eq["transfer_given"].round(2),
        "Şebekeden (kWh)":       eq["grid_draw"].round(2),
        "Şebekeye (kWh)":        eq["grid_feed"].round(2),
    })
    def durum(r):
        if r["Net (kWh)"] >  0.5: return "FAZLA ⬆️"
        if r["Net (kWh)"] < -0.5: return "EKSİK ⬇️"
        return "DENGEDE ⚖️"
    df["Durum"] = df.apply(durum, axis=1)
    st.dataframe(df.set_index("Ev"), use_container_width=True)

    # Kart görünümü
    card_cols = st.columns(min(n_houses, 4))
    for i, name in enumerate(names):
        nv = eq["net"][i]
        badge = "surplus-badge" if nv > 0.05 else ("deficit-badge" if nv < -0.05 else "balanced-badge")
        lbl   = f"+{nv:.1f} kWh FAZLA" if nv > 0.05 else (f"{nv:.1f} kWh EKSİK" if nv < -0.05 else "DENGEDE")
        card_cols[i % 4].markdown(f"""
        <div class="house-card">
          <div style="font-family:'Rajdhani',sans-serif;font-weight:700;color:#c8d8e8;font-size:0.92rem;">🏠 {name}</div>
          <div style="font-family:'Share Tech Mono',monospace;font-size:0.7rem;color:#7ecfff;margin:4px 0;">
            {panel_counts[i]} panel · ↑{daily_prod[i]:.1f} ↓{daily_cons[i]:.1f} kWh
          </div>
          <span class="{badge}">{lbl}</span>
        </div>""", unsafe_allow_html=True)

    # ════════════════════════════════════════
    # BÖLÜM 2 — 24 SAATLİK PROFİL
    # ════════════════════════════════════════
    st.markdown('<div class="section-header">02 — 24 SAATLİK ENERJİ PROFİLİ</div>', unsafe_allow_html=True)

    hours        = list(range(24))
    total_prod_h = prod.sum(axis=0)
    total_cons_h = cons.sum(axis=0)
    net_h        = total_prod_h - total_cons_h
    grid_h       = np.maximum(-net_h, 0)

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(x=hours, y=total_prod_h, name="Toplam Üretim (kWh)",
        line=dict(color="#00ffc8", width=2.5),
        fill="tozeroy", fillcolor="rgba(0,255,200,0.07)",
        hovertemplate="Saat %{x}:00 → %{y:.2f} kWh<extra></extra>"))
    fig_line.add_trace(go.Scatter(x=hours, y=total_cons_h, name="Toplam Tüketim (kWh)",
        line=dict(color="#0096ff", width=2.5, dash="dot"),
        hovertemplate="Saat %{x}:00 → %{y:.2f} kWh<extra></extra>"))
    fig_line.add_trace(go.Scatter(x=hours, y=grid_h, name="Şebekeden Çekilen (kWh)",
        line=dict(color="#ff4d6d", width=2),
        fill="tozeroy", fillcolor="rgba(255,77,109,0.07)",
        hovertemplate="Saat %{x}:00 → %{y:.2f} kWh<extra></extra>"))
    fig_line.update_layout(
        **PLOT_BG,
        title=dict(text="Mahallenin 24 Saatlik Enerji Profili",
                   font=dict(family="Orbitron", size=14, color="#00ffc8")),
        xaxis=dict(**PLOT_BG["xaxis"], title="Saat", tickmode="linear", tick0=0, dtick=2),
        yaxis=dict(**PLOT_BG["yaxis"], title="kWh"),
        legend=dict(bgcolor="rgba(0,0,0,0.4)", bordercolor="rgba(0,255,200,0.2)", borderwidth=1),
        hovermode="x unified", height=400,
    )
    st.plotly_chart(fig_line, use_container_width=True)
    st.caption("🟢 Yeşil alan: güneş üretiminiz tüketiminizi karşılıyor · 🔴 Kırmızı: şebekeden ek çekim gerekiyor")

    # ════════════════════════════════════════
    # BÖLÜM 3 — SHAPLEY DAĞILIMI
    # ════════════════════════════════════════
    st.markdown('<div class="section-header">03 — SHAPLEY ADIL KAZANÇ DAĞILIMI</div>', unsafe_allow_html=True)

    col_pie, col_tbl = st.columns([1.1, 0.9])
    sv_pos  = np.maximum(shapley, 0.001)
    colors  = px.colors.sample_colorscale("Teal", [i/max(n_houses-1,1) for i in range(n_houses)])

    with col_pie:
        fig_pie = go.Figure(go.Pie(
            labels=names, values=sv_pos, hole=0.52,
            marker=dict(colors=colors, line=dict(color="#0b1120", width=2)),
            textfont=dict(family="Share Tech Mono", size=10),
            hovertemplate="<b>%{label}</b><br>Shapley: %{value:.3f} kWh<extra></extra>",
        ))
        fig_pie.update_layout(
            **PLOT_BG,
            title=dict(text="Shapley Kazanç Payı",
                       font=dict(family="Orbitron", size=14, color="#00ffc8")),
            showlegend=True,
            legend=dict(font=dict(size=11)),
            annotations=[dict(text=f"<b>{n_houses}</b><br>EV",
                x=0.5, y=0.5, showarrow=False,
                font=dict(family="Orbitron", size=16, color="#00ffc8"))],
            height=420,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_tbl:
        st.markdown("*Her evin sisteme marjinal katkısına göre adil payı:*")
        sv_df = pd.DataFrame({
            "Ev":                 names,
            "Shapley (kWh)":     shapley.round(3),
            "Pay (%)":           (sv_pos/sv_pos.sum()*100).round(1),
            "Üretim (kWh)":      daily_prod.round(2),
            "Tüketim (kWh)":     daily_cons,
        }).sort_values("Shapley (kWh)", ascending=False).reset_index(drop=True)
        st.dataframe(sv_df.set_index("Ev"), use_container_width=True, height=380)

        st.markdown("""
        <div class="info-box" style="margin-top:16px;">
          <div style="font-family:'Share Tech Mono',monospace;font-size:0.7rem;color:#00ffc8;margin-bottom:8px;">SHAPLEY NEDİR?</div>
          <div style="font-family:'Rajdhani',sans-serif;font-size:0.9rem;color:#c8d8e8;line-height:1.7;">
            Her evin tüm olası koalisyonlara katkısı hesaplanır.
            Paneli fazla olan daha büyük pay alır; paneli olmayanlar
            tüketim oranına göre değerlendirilir.
          </div>
        </div>""", unsafe_allow_html=True)

    # ════════════════════════════════════════
    # BÖLÜM 4 — ENERJİ AKIŞI (SANKEY)
    # ════════════════════════════════════════
    st.markdown('<div class="section-header">04 — ENERJİ AKIŞ DİYAGRAMI (NASH DENGESİ)</div>', unsafe_allow_html=True)

    surplus_idx = [i for i in range(n_houses) if eq["transfer_given"][i]    > 0.05]
    deficit_idx  = [i for i in range(n_houses) if eq["transfer_received"][i] > 0.05]

    if surplus_idx and deficit_idx:
        n_s = len(surplus_idx); n_d = len(deficit_idx)
        node_labels = (
            [f"☀️ {names[i]}" for i in surplus_idx] +
            [f"🏠 {names[i]}" for i in deficit_idx] +
            ["🔌 Şebeke"]
        )
        sources, targets, values, lcolors = [], [], [], []
        total_s = sum(eq["transfer_given"][i]    for i in surplus_idx)
        total_d = sum(eq["transfer_received"][i]  for i in deficit_idx)
        covered = min(total_s, total_d)

        for si, s in enumerate(surplus_idx):
            for di, d in enumerate(deficit_idx):
                val = (eq["transfer_given"][s]/(total_s+1e-9)) * \
                      (eq["transfer_received"][d]/(total_d+1e-9)) * covered
                if val > 0.01:
                    sources.append(si); targets.append(n_s+di)
                    values.append(round(val,3)); lcolors.append("rgba(0,255,200,0.4)")

        gn = n_s + n_d
        for di, d in enumerate(deficit_idx):
            gd = eq["grid_draw"][d]
            if gd > 0.01:
                sources.append(gn); targets.append(n_s+di)
                values.append(round(gd,3)); lcolors.append("rgba(255,77,109,0.4)")

        fig_sank = go.Figure(go.Sankey(
            node=dict(pad=18, thickness=20,
                      line=dict(color="#0b1120", width=0.5),
                      label=node_labels,
                      color=(["rgba(0,255,200,0.75)"]*n_s +
                             ["rgba(0,150,255,0.75)"]*n_d +
                             ["rgba(255,77,109,0.75)"])),
            link=dict(source=sources, target=targets, value=values, color=lcolors),
        ))
        fig_sank.update_layout(
            **PLOT_BG,
            title=dict(text="Nash Dengesi — Komşular Arası Enerji Transferi",
                       font=dict(family="Orbitron", size=14, color="#00ffc8")),
            height=420,
        )
        st.plotly_chart(fig_sank, use_container_width=True)
    else:
        st.info("Sankey diyagramı için en az bir fazla enerjili ve bir eksik enerjili ev gerekiyor. Panel sayılarını ayarlayın.")

    st.markdown("""
    <div class="info-box">
      <div style="font-family:'Orbitron',sans-serif;font-size:0.78rem;color:#00ffc8;margin-bottom:10px;">
        SİSTEM NASIL ÇALIŞIR?
      </div>
      <div style="font-family:'Rajdhani',sans-serif;font-size:0.95rem;color:#c8d8e8;line-height:1.8;">
        <b style="color:#00ffc8;">Nash Dengesi:</b> Her ev kendi tüketimini karşıladıktan sonra fazla
        enerjisini komşularıyla paylaşır. Hiçbir ev tek başına daha iyi sonuç elde edemez —
        bu matematiksel denge noktasıdır.<br><br>
        <b style="color:#0096ff;">Shapley Değeri:</b> Her evin sisteme kattığı marjinal değer, tüm
        koalisyon permütasyonları üzerinden hesaplanır. Adil paylaşım ilkesi: katkın kadar al.<br><br>
        <b style="color:#ffd166;">Sonuç:</b> Şebekeye bağımlılık azalır, karbon ayak izi düşer,
        mahalle enerji maliyetleri matematiksel olarak adil biçimde paylaşılır.
      </div>
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="text-align:center;padding:90px 0;">
      <div style="font-size:4rem;color:rgba(0,255,200,0.08);">⚡</div>
      <div style="font-family:'Share Tech Mono',monospace;font-size:0.8rem;
        letter-spacing:3px;color:#1a3a5a;margin-top:18px;">
        SOL PANELİ DOLDURUN VE SİMÜLASYONU BAŞLATIN
      </div>
      <div style="font-family:'Rajdhani',sans-serif;font-size:0.92rem;
        color:#122a40;margin-top:10px;line-height:1.8;">
        Mahalledeki ev sayısını, her evin panel sayısını<br>
        ve günlük enerji tüketimini girerek<br>
        adil enerji dağılım modelini oluşturun.
      </div>
    </div>
    """, unsafe_allow_html=True)
