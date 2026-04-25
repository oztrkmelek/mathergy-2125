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

# ─────────────────────────────────────────────
#  SAYFA AYARLARI
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="MathErgy 212510",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CSS — CARBON FIBRE KOYU TEMA
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&family=Rajdhani:wght@300;400;600;700&display=swap');

  .stApp {
    background-color: #0a0a0a;
    background-image:
      repeating-linear-gradient(45deg,  transparent, transparent 2px, rgba(255,255,255,0.015) 2px, rgba(255,255,255,0.015) 4px),
      repeating-linear-gradient(-45deg, transparent, transparent 2px, rgba(255,255,255,0.015) 2px, rgba(255,255,255,0.015) 4px);
    font-family: 'Rajdhani', sans-serif;
  }
  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0f14 0%, #111520 100%);
    border-right: 1px solid rgba(0,255,200,0.15);
  }
  h1,h2,h3 { font-family:'Orbitron',sans-serif !important; letter-spacing:2px; }
  [data-testid="metric-container"] {
    background: linear-gradient(135deg,rgba(0,255,200,0.06),rgba(0,150,255,0.04));
    border: 1px solid rgba(0,255,200,0.2);
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
  button[data-baseweb="tab"] {
    font-family:'Orbitron',sans-serif !important;
    font-size:0.7rem !important; letter-spacing:1px; color:#7ecfff !important;
  }
  .neon-line {
    height:2px;
    background:linear-gradient(90deg,transparent,#00ffc8,#0096ff,transparent);
    margin:8px 0 18px 0; border-radius:2px;
    box-shadow:0 0 8px rgba(0,255,200,0.5);
  }
  .house-card {
    background:linear-gradient(135deg,rgba(0,255,200,0.04),rgba(0,80,200,0.04));
    border:1px solid rgba(0,255,200,0.15);
    border-radius:10px; padding:12px 16px; margin-bottom:8px;
  }
  .surplus-badge  { display:inline-block; background:rgba(0,255,200,0.15);  border:1px solid #00ffc8; color:#00ffc8; font-family:'Share Tech Mono',monospace; font-size:0.68rem; padding:2px 8px; border-radius:20px; }
  .deficit-badge  { display:inline-block; background:rgba(255,77,109,0.15);  border:1px solid #ff4d6d; color:#ff4d6d; font-family:'Share Tech Mono',monospace; font-size:0.68rem; padding:2px 8px; border-radius:20px; }
  .balanced-badge { display:inline-block; background:rgba(255,209,102,0.15); border:1px solid #ffd166; color:#ffd166; font-family:'Share Tech Mono',monospace; font-size:0.68rem; padding:2px 8px; border-radius:20px; }
  .info-box {
    background:rgba(0,20,30,0.6); border:1px solid rgba(0,255,200,0.15);
    border-radius:10px; padding:16px; margin-top:12px;
  }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  LOGO
# ─────────────────────────────────────────────
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


# ─────────────────────────────────────────────
#  HESAPLAMA FONKSİYONLARI
#  NOT: np.math kaldırıldı → math.factorial kullanılıyor
# ─────────────────────────────────────────────

def shapley_value(productions: np.ndarray, consumptions: np.ndarray) -> np.ndarray:
    """
    Shapley Değeri: Her hanenin koalisyona marjinal katkısını hesaplar.
    Adil paylaşım ilkesi: Katkısı kadar al.
    """
    n = len(productions)
    net = productions - consumptions
    shapley = np.zeros(n)
    players = list(range(n))

    for perm in itertools.permutations(players):
        coalition = set()
        for player in perm:
            before = max(sum(net[i] for i in coalition), 0.0)
            coalition.add(player)
            after  = max(sum(net[i] for i in coalition), 0.0)
            shapley[player] += (after - before)

    return shapley / math.factorial(n)   # math.factorial — güvenli


def nash_transfer(productions: np.ndarray, consumptions: np.ndarray) -> dict:
    """
    Nash Dengesi: Fazlası olanlar eksik olanlara oransal aktarım yapar.
    Sonuç: Şebeke bağımlılığı minimize edilir.
    """
    net = productions - consumptions
    surplus_mask = net > 0
    deficit_mask  = net < 0

    total_surplus = net[surplus_mask].sum()
    total_deficit  = abs(net[deficit_mask].sum())

    transfer_received = np.zeros(n := len(productions))
    transfer_given    = np.zeros(n)

    if total_surplus > 0 and total_deficit > 0:
        covered = min(total_surplus, total_deficit)
        for i in range(n):
            if deficit_mask[i]:
                transfer_received[i] = covered * (abs(net[i]) / total_deficit)
            if surplus_mask[i]:
                transfer_given[i]    = covered * (net[i] / total_surplus)

    grid_draw = np.maximum(-net - transfer_received, 0)
    grid_feed = np.maximum( net - transfer_given,    0)

    return {
        "net": net,
        "transfer_received": transfer_received,
        "transfer_given":    transfer_given,
        "grid_draw":         grid_draw,
        "grid_feed":         grid_feed,
        "final_balance":     net + transfer_received - transfer_given,
    }


def hourly_profile(n_houses: int, panel_counts: list, panel_watt: float,
                   consumption_kwh: list, solar_eff: float, city_sun_hours: float):
    """
    24 saatlik güneş üretim ve tüketim profili.
    Üretim: sinüs eğrisi (08-18 arası), tüketim: sabah/akşam pikli profil.
    """
    hours = np.arange(24)

    # Güneş eğrisi
    sun_curve = np.zeros(24)
    for h in range(8, 19):
        angle = math.pi * (h - 8) / 10
        sun_curve[h] = math.sin(angle)
    total_sin = sun_curve.sum()
    if total_sin > 0:
        sun_curve /= total_sin   # normalize

    # Tüketim profili
    cons_profile = np.array([
        0.02,0.01,0.01,0.01,0.01,0.02,
        0.04,0.06,0.06,0.04,0.03,0.03,
        0.04,0.03,0.03,0.04,0.05,0.08,
        0.09,0.08,0.07,0.06,0.04,0.03
    ])
    cons_profile /= cons_profile.sum()

    productions  = np.zeros((n_houses, 24))
    consumptions = np.zeros((n_houses, 24))

    for i in range(n_houses):
        daily_prod = panel_counts[i] * (panel_watt / 1000) * city_sun_hours * solar_eff
        productions[i]  = sun_curve * daily_prod
        consumptions[i] = cons_profile * consumption_kwh[i]

    return productions, consumptions, hours


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
HOUSE_NAMES = [
    "Ahmet Bey","Fatma Hanım","Mehmet Bey","Ayşe Hanım",
    "Ali Bey","Zeynep Hanım","Hasan Bey","Merve Hanım",
    "Emre Bey","Elif Hanım","Can Bey","Selin Hanım",
    "Burak Bey","Derya Hanım","Kemal Bey","Sevgi Hanım",
    "Tarık Bey","Büşra Hanım","Ercan Bey","Nisa Hanım",
]

with st.sidebar:
    show_logo()
    st.markdown('<div class="neon-line"></div>', unsafe_allow_html=True)

    st.markdown("### 🏘️ Mahalle Kurulumu")
    n_houses = st.slider("Mahalledeki Ev Sayısı", 2, 10, 5, 1,
                         help="Shapley hesabı için max 10 önerilir")

    st.markdown("---")
    st.markdown("### ☀️ Güneş Paneli Ayarları")
    panel_watt = st.slider("Panel Gücü (Watt/panel)", 100, 600, 300, 50)
    solar_eff  = st.slider("Panel Verimliliği (%)",   10,  25,  18,  1) / 100
    city_sun   = st.slider("Günlük Güneşlenme (saat)", 3,   9,   5,  1,
                           help="Şehrinizin yıllık ortalama güneşlenme süresi")

    st.markdown("---")
    st.markdown("### 🏠 Her Evin Detayları")
    st.caption("Her ev için panel sayısı ve günlük tüketim girin:")

    panel_counts    = []
    consumption_kwh = []

    for i in range(n_houses):
        name = HOUSE_NAMES[i] if i < len(HOUSE_NAMES) else f"Ev {i+1}"
        with st.expander(f"🏠 {name}", expanded=(i < 2)):
            pc = st.slider("Panel sayısı (0 = panel yok)", 0, 20,
                           max(1, 5 - i % 5), key=f"p_{i}")
            ck = st.slider("Günlük tüketim (kWh)", 1, 30,
                           8 + (i % 5),        key=f"c_{i}")
            panel_counts.append(pc)
            consumption_kwh.append(float(ck))

    st.markdown("---")
    start_btn = st.button("⚡  SİMÜLASYONU BAŞLAT")


# ─────────────────────────────────────────────
#  ANA BAŞLIK
# ─────────────────────────────────────────────
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
  Oyun Teorisi · Nash Dengesi · Shapley Değeri · TÜBİTAK 2204-A
</div>
""", unsafe_allow_html=True)
st.markdown('<div class="neon-line"></div>', unsafe_allow_html=True)

names = [HOUSE_NAMES[i] if i < len(HOUSE_NAMES) else f"Ev {i+1}" for i in range(n_houses)]

PLOT_BG = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(10,15,25,0.85)",
    font=dict(family="Rajdhani,sans-serif", color="#c8d8e8", size=13),
    margin=dict(l=40, r=20, t=50, b=40),
    xaxis=dict(gridcolor="rgba(0,255,200,0.06)", zerolinecolor="rgba(0,255,200,0.1)"),
    yaxis=dict(gridcolor="rgba(0,255,200,0.06)", zerolinecolor="rgba(0,255,200,0.1)"),
)

# ─────────────────────────────────────────────
#  SİMÜLASYON ÇALIŞMASI
# ─────────────────────────────────────────────
if start_btn:

    with st.status("⚡ Simülasyon hesaplanıyor...", expanded=True) as status:
        st.write("☀️ Güneş üretim profilleri modelleniyor...")
        time.sleep(0.7)
        productions, consumptions, hours = hourly_profile(
            n_houses, panel_counts, panel_watt, consumption_kwh, solar_eff, city_sun
        )
        daily_prod = productions.sum(axis=1)
        daily_cons = np.array(consumption_kwh)

        st.write("🤝 Nash Dengesi ile enerji transferleri hesaplanıyor...")
        time.sleep(0.8)
        eq = nash_transfer(daily_prod, daily_cons)

        st.write("🧮 Shapley Değerleri hesaplanıyor (koalisyon analizi)...")
        time.sleep(1.0)
        shapley = shapley_value(daily_prod, daily_cons)

        st.write("📊 Grafikler oluşturuluyor...")
        time.sleep(0.5)
        status.update(label="✅ Simülasyon tamamlandı!", state="complete", expanded=False)

    # ── METRİKLER ──
    st.markdown("---")
    total_prod_mah  = daily_prod.sum()
    total_cons_mah  = daily_cons.sum()
    grid_draw_total = eq["grid_draw"].sum()
    grid_feed_total = eq["grid_feed"].sum()
    self_suff       = max(0.0, 1.0 - grid_draw_total / (total_cons_mah + 1e-9)) * 100

    m1,m2,m3,m4,m5 = st.columns(5)
    m1.metric("☀️ Mahalle Üretimi",   f"{total_prod_mah:.1f} kWh/gün")
    m2.metric("🏠 Toplam Tüketim",    f"{total_cons_mah:.1f} kWh/gün")
    m3.metric("🔌 Şebekeden Çekilen", f"{grid_draw_total:.1f} kWh/gün")
    m4.metric("↗️ Şebekeye Verilen",  f"{grid_feed_total:.1f} kWh/gün")
    m5.metric("🌱 Öz Yeterlilik",     f"{self_suff:.1f}%")

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🏠  EV BAZLI DURUM",
        "📊  24 SAATLİK PROFİL",
        "🥧  SHAPLEY DAĞILIMI",
        "🔄  ENERJİ AKIŞI",
    ])

    # ── TAB 1: Ev bazlı ──
    with tab1:
        st.markdown("#### Her Evin Günlük Enerji Özeti")

        df = pd.DataFrame({
            "Ev":                    names,
            "Panel Sayısı":          panel_counts,
            "Üretim (kWh)":          daily_prod.round(2),
            "Tüketim (kWh)":         daily_cons.round(2),
            "Net (kWh)":             eq["net"].round(2),
            "Komşudan Aldığı (kWh)": eq["transfer_received"].round(2),
            "Komşuya Verdiği (kWh)": eq["transfer_given"].round(2),
            "Şebekeden (kWh)":       eq["grid_draw"].round(2),
            "Şebekeye (kWh)":        eq["grid_feed"].round(2),
        })
        def durum(row):
            if row["Net (kWh)"] >  0.5: return "FAZLA ⬆️"
            if row["Net (kWh)"] < -0.5: return "EKSİK ⬇️"
            return "DENGEDE ⚖️"
        df["Durum"] = df.apply(durum, axis=1)
        st.dataframe(df.set_index("Ev"), use_container_width=True)

        # Kart görünümü
        cols = st.columns(min(n_houses, 4))
        for i, name in enumerate(names):
            net_val = eq["net"][i]
            badge   = "surplus-badge" if net_val > 0.05 else ("deficit-badge" if net_val < -0.05 else "balanced-badge")
            label   = f"+{net_val:.1f} kWh FAZLA" if net_val > 0.05 else (f"{net_val:.1f} kWh EKSİK" if net_val < -0.05 else "DENGEDE")
            cols[i % 4].markdown(f"""
            <div class="house-card">
              <div style="font-family:'Rajdhani',sans-serif;font-weight:700;color:#c8d8e8;font-size:0.92rem;">
                🏠 {name}
              </div>
              <div style="font-family:'Share Tech Mono',monospace;font-size:0.72rem;color:#7ecfff;margin:4px 0;">
                {panel_counts[i]} panel · ↑{daily_prod[i]:.1f} ↓{daily_cons[i]:.1f} kWh
              </div>
              <span class="{badge}">{label}</span>
            </div>""", unsafe_allow_html=True)

    # ── TAB 2: 24 Saatlik Profil ──
    with tab2:
        total_prod_h = productions.sum(axis=0)
        total_cons_h = consumptions.sum(axis=0)
        net_h        = total_prod_h - total_cons_h
        grid_draw_h  = np.maximum(-net_h, 0)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hours, y=total_prod_h, name="Toplam Üretim (kWh)",
            line=dict(color="#00ffc8", width=2.5),
            fill="tozeroy", fillcolor="rgba(0,255,200,0.07)",
            hovertemplate="Saat %{x}:00 → %{y:.2f} kWh<extra></extra>"))
        fig.add_trace(go.Scatter(x=hours, y=total_cons_h, name="Toplam Tüketim (kWh)",
            line=dict(color="#0096ff", width=2.5, dash="dot"),
            hovertemplate="Saat %{x}:00 → %{y:.2f} kWh<extra></extra>"))
        fig.add_trace(go.Scatter(x=hours, y=grid_draw_h, name="Şebekeden Çekilen (kWh)",
            line=dict(color="#ff4d6d", width=2),
            fill="tozeroy", fillcolor="rgba(255,77,109,0.07)",
            hovertemplate="Saat %{x}:00 → %{y:.2f} kWh<extra></extra>"))
        fig.update_layout(
            **PLOT_BG,
            title=dict(text="Mahallenin 24 Saatlik Enerji Profili",
                       font=dict(family="Orbitron", size=14, color="#00ffc8")),
            xaxis=dict(**PLOT_BG["xaxis"], title="Saat", tickmode="linear", tick0=0, dtick=2),
            yaxis=dict(**PLOT_BG["yaxis"], title="kWh"),
            legend=dict(bgcolor="rgba(0,0,0,0.4)", bordercolor="rgba(0,255,200,0.2)", borderwidth=1),
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Yeşil: Güneş üretiminiz tüketiminizi karşılıyor · Kırmızı: Şebekeden ek çekim gerekiyor")

    # ── TAB 3: Shapley Dağılımı ──
    with tab3:
        col_p, col_t = st.columns([1.1, 0.9])
        with col_p:
            sv_pos  = np.maximum(shapley, 0.001)
            colors  = px.colors.sample_colorscale("Teal", [i/max(n_houses-1,1) for i in range(n_houses)])
            fig_pie = go.Figure(go.Pie(
                labels=names, values=sv_pos, hole=0.52,
                marker=dict(colors=colors, line=dict(color="#0a0a0a", width=2)),
                textfont=dict(family="Share Tech Mono", size=10),
                hovertemplate="<b>%{label}</b><br>Shapley: %{value:.3f} kWh<extra></extra>",
            ))
            fig_pie.update_layout(
                **PLOT_BG,
                title=dict(text="Shapley Adil Kazanç Dağılımı",
                           font=dict(family="Orbitron", size=14, color="#00ffc8")),
                showlegend=True,
                legend=dict(font=dict(size=10)),
                annotations=[dict(text=f"<b>{n_houses}</b><br>EV",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(family="Orbitron", size=16, color="#00ffc8"))],
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_t:
            st.markdown("#### 🧮 Adil Pay Tablosu")
            st.caption("Her evin sisteme marjinal katkısına göre hesaplanan pay.")
            sv_df = pd.DataFrame({
                "Ev":                names,
                "Shapley Payı (kWh)": shapley.round(3),
                "Yüzde (%)":         (sv_pos/sv_pos.sum()*100).round(1),
                "Üretim (kWh)":      daily_prod.round(2),
                "Tüketim (kWh)":     daily_cons,
            }).sort_values("Shapley Payı (kWh)", ascending=False).reset_index(drop=True)
            st.dataframe(sv_df.set_index("Ev"), use_container_width=True, height=400)

    # ── TAB 4: Enerji Akışı (Sankey) ──
    with tab4:
        st.markdown("#### 🔄 Nash Dengesi — Enerji Transfer Diyagramı")
        st.caption("Fazla enerjisi olan evler, eksik olanlara matematiksel en adil şekilde aktarım yapar.")

        surplus_idx = [i for i in range(n_houses) if eq["transfer_given"][i] > 0.05]
        deficit_idx  = [i for i in range(n_houses) if eq["transfer_received"][i] > 0.05]

        if surplus_idx and deficit_idx:
            n_s = len(surplus_idx)
            n_d = len(deficit_idx)
            node_labels = (
                [f"☀️ {names[i]}" for i in surplus_idx] +
                [f"🏠 {names[i]}" for i in deficit_idx] +
                ["🔌 Şebeke"]
            )
            sources, targets, values, link_colors = [], [], [], []
            total_s = sum(eq["transfer_given"][i]    for i in surplus_idx)
            total_d = sum(eq["transfer_received"][i]  for i in deficit_idx)
            covered = min(total_s, total_d)

            for si, s in enumerate(surplus_idx):
                for di, d in enumerate(deficit_idx):
                    val = (eq["transfer_given"][s] / (total_s+1e-9)) * \
                          (eq["transfer_received"][d] / (total_d+1e-9)) * covered
                    if val > 0.01:
                        sources.append(si);    targets.append(n_s+di)
                        values.append(round(val,3)); link_colors.append("rgba(0,255,200,0.4)")

            grid_node = n_s + n_d
            for di, d in enumerate(deficit_idx):
                gd = eq["grid_draw"][d]
                if gd > 0.01:
                    sources.append(grid_node); targets.append(n_s+di)
                    values.append(round(gd,3)); link_colors.append("rgba(255,77,109,0.4)")

            fig_sank = go.Figure(go.Sankey(
                node=dict(
                    pad=15, thickness=18,
                    line=dict(color="#0a0a0a", width=0.5),
                    label=node_labels,
                    color=(["rgba(0,255,200,0.7)"]*n_s +
                           ["rgba(0,150,255,0.7)"]*n_d +
                           ["rgba(255,77,109,0.7)"]),
                ),
                link=dict(source=sources, target=targets,
                          value=values, color=link_colors),
            ))
            fig_sank.update_layout(
                **PLOT_BG,
                title=dict(text="Nash Dengesi Enerji Akış Diyagramı",
                           font=dict(family="Orbitron", size=14, color="#00ffc8")),
            )
            st.plotly_chart(fig_sank, use_container_width=True)
        else:
            st.info("Transfer diyagramı için en az bir fazla enerjili ve bir eksik enerjili ev olmalı.")

        st.markdown("""
        <div class="info-box">
          <div style="font-family:'Orbitron',sans-serif;font-size:0.78rem;color:#00ffc8;margin-bottom:10px;">
            NASIL ÇALIŞIR?
          </div>
          <div style="font-family:'Rajdhani',sans-serif;font-size:0.95rem;color:#c8d8e8;line-height:1.8;">
            <b style="color:#00ffc8;">Nash Dengesi:</b> Her ev kendi tüketimini karşıladıktan sonra
            fazla enerjisini komşularıyla paylaşır. Hiçbir ev tek başına daha iyi bir sonuç
            elde edemez — bu denge noktasıdır.<br><br>
            <b style="color:#0096ff;">Shapley Değeri:</b> Her evin sisteme kattığı marjinal değer
            tüm koalisyon permütasyonları üzerinden hesaplanır. Panel sayısı fazla olan evler
            daha büyük pay alır; hiç paneli olmayanlar da tüketimleri oranında değerlendirilir.<br><br>
            <b style="color:#ffd166;">Sonuç:</b> Şebekeye bağımlılık azalır, karbon ayak izi düşer,
            mahalle enerji maliyetleri matematiksel olarak adil biçimde paylaşılır.
          </div>
        </div>
        """, unsafe_allow_html=True)

else:
    # Bekleme ekranı
    st.markdown("""
    <div style="text-align:center;padding:80px 0;">
      <div style="font-size:3.5rem;color:rgba(0,255,200,0.1);">⚡</div>
      <div style="font-family:'Share Tech Mono',monospace;font-size:0.8rem;
        letter-spacing:3px;color:#2a4a5a;margin-top:16px;">
        SOL PANELİ DOLDURUN VE SİMÜLASYONU BAŞLATIN
      </div>
      <div style="font-family:'Rajdhani',sans-serif;font-size:0.9rem;color:#1a3a4a;margin-top:10px;line-height:1.8;">
        Mahalledeki ev sayısını, her evin panel sayısını<br>
        ve günlük enerji tüketimini girerek<br>
        adil enerji dağılım modelini oluşturun.
      </div>
    </div>
    """, unsafe_allow_html=True)
