import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import time
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
#  CARBON FIBRE + KOYU TEMA CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&family=Rajdhani:wght@300;400;600;700&display=swap');

  /* Carbon fibre desen arka plan */
  .stApp {
    background-color: #0a0a0a;
    background-image:
      repeating-linear-gradient(
        45deg,
        transparent,
        transparent 2px,
        rgba(255,255,255,0.015) 2px,
        rgba(255,255,255,0.015) 4px
      ),
      repeating-linear-gradient(
        -45deg,
        transparent,
        transparent 2px,
        rgba(255,255,255,0.015) 2px,
        rgba(255,255,255,0.015) 4px
      ),
      linear-gradient(180deg, #0a0a0a 0%, #111318 100%);
    font-family: 'Rajdhani', sans-serif;
  }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0f14 0%, #111520 100%);
    border-right: 1px solid rgba(0, 255, 200, 0.15);
  }

  /* Başlık */
  h1, h2, h3 {
    font-family: 'Orbitron', sans-serif !important;
    letter-spacing: 2px;
  }

  /* Metrik kartlar */
  [data-testid="metric-container"] {
    background: linear-gradient(135deg, rgba(0,255,200,0.06), rgba(0,150,255,0.04));
    border: 1px solid rgba(0,255,200,0.2);
    border-radius: 12px;
    padding: 14px;
    backdrop-filter: blur(6px);
  }

  [data-testid="stMetricValue"] {
    font-family: 'Share Tech Mono', monospace !important;
    color: #00ffc8 !important;
    font-size: 1.6rem !important;
  }

  [data-testid="stMetricLabel"] {
    color: #7ecfff !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.85rem !important;
    letter-spacing: 1px;
  }

  /* Sliderlar */
  .stSlider > div > div > div > div {
    background: linear-gradient(90deg, #00ffc8, #0096ff) !important;
  }

  /* Buton */
  .stButton > button {
    background: linear-gradient(135deg, #00ffc8 0%, #0096ff 100%);
    color: #000 !important;
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 700;
    font-size: 0.95rem;
    letter-spacing: 2px;
    border: none;
    border-radius: 8px;
    padding: 14px 36px;
    width: 100%;
    transition: all 0.3s ease;
    box-shadow: 0 0 20px rgba(0,255,200,0.3);
  }

  .stButton > button:hover {
    box-shadow: 0 0 40px rgba(0,255,200,0.6);
    transform: translateY(-2px);
  }

  /* Genel metin */
  p, label, .stMarkdown {
    color: #c8d8e8 !important;
    font-family: 'Rajdhani', sans-serif !important;
  }

  /* Divider */
  hr {
    border-color: rgba(0,255,200,0.15) !important;
  }

  /* Tab */
  button[data-baseweb="tab"] {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.75rem !important;
    letter-spacing: 1px;
    color: #7ecfff !important;
  }

  /* Status kutusu */
  [data-testid="stStatus"] {
    background: rgba(0,20,30,0.8) !important;
    border: 1px solid rgba(0,255,200,0.3) !important;
    border-radius: 10px;
  }

  /* Neon çizgi efekti */
  .neon-line {
    height: 2px;
    background: linear-gradient(90deg, transparent, #00ffc8, #0096ff, transparent);
    margin: 8px 0 20px 0;
    border-radius: 2px;
    box-shadow: 0 0 8px rgba(0,255,200,0.5);
  }

  .stat-card {
    background: linear-gradient(135deg, rgba(0,255,200,0.05), rgba(0,80,200,0.05));
    border: 1px solid rgba(0,255,200,0.18);
    border-radius: 14px;
    padding: 18px 22px;
    margin-bottom: 12px;
  }

  .tag {
    display: inline-block;
    background: rgba(0,255,200,0.12);
    border: 1px solid rgba(0,255,200,0.35);
    color: #00ffc8;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    padding: 2px 10px;
    border-radius: 20px;
    letter-spacing: 1px;
    margin: 2px;
  }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  LOGO
# ─────────────────────────────────────────────
def show_logo():
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        img = Image.open(logo_path)
        st.image(img, width=180)
    else:
        st.markdown("""
        <div style="font-family:'Orbitron',sans-serif; font-size:1.5rem;
             color:#00ffc8; letter-spacing:4px; margin-bottom:4px;">
          ⚡ MATH<span style="color:#0096ff;">ERGY</span>
        </div>
        <div style="font-family:'Share Tech Mono',monospace; font-size:0.7rem;
             color:#7ecfff; letter-spacing:3px;">212510 — SMART GRID SIMULATOR</div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  OYUN TEORİSİ FONKSİYONLARI
# ─────────────────────────────────────────────

def shapley_value(n_players: int, characteristic_fn) -> np.ndarray:
    """Shapley Değeri hesabı — koalisyon oyunu."""
    players = list(range(n_players))
    shapley = np.zeros(n_players)
    n_fact = np.math.factorial(n_players)

    for perm in itertools.permutations(players):
        coalition = set()
        for player in perm:
            prev_val = characteristic_fn(frozenset(coalition))
            coalition.add(player)
            curr_val = characteristic_fn(frozenset(coalition))
            shapley[player] += (curr_val - prev_val)

    return shapley / n_fact


def nash_equilibrium_energy(productions: np.ndarray, consumptions: np.ndarray,
                             solar_eff: float) -> dict:
    """Basit Nash Dengesi — her hane kendi çıkarını maksimize eder."""
    net_energy = productions * solar_eff - consumptions
    surplus = np.maximum(net_energy, 0)
    deficit = np.maximum(-net_energy, 0)

    total_surplus = surplus.sum()
    total_deficit = deficit.sum()

    if total_surplus > 0:
        transfer = np.minimum(deficit, deficit / (total_deficit + 1e-9) * total_surplus)
    else:
        transfer = np.zeros(len(productions))

    grid_load = np.maximum(deficit - transfer, 0)
    return {
        "surplus": surplus,
        "deficit": deficit,
        "transfer": transfer,
        "grid_load": grid_load,
        "net_balance": net_energy,
    }


def characteristic_fn_factory(productions, consumptions, solar_eff):
    """Koalisyon karakteristik fonksiyonu üreteci."""
    net = productions * solar_eff - consumptions

    def fn(coalition: frozenset) -> float:
        if not coalition:
            return 0.0
        c = list(coalition)
        total_net = net[c].sum()
        # Koalisyon içi paylaşım kazancı
        cooperation_bonus = len(coalition) ** 0.6 * 0.15
        return max(total_net, 0) * (1 + cooperation_bonus)

    return fn


def simulate(n_houses: int, solar_eff: float, storage_cap: float,
             peak_hours: int, volatility: float, seed: int = 42):
    """Ana simülasyon fonksiyonu."""
    rng = np.random.default_rng(seed)
    hours = 24

    # Üretim profili (güneş eğrisi)
    t = np.linspace(0, np.pi, hours)
    base_solar = np.sin(t) * solar_eff
    base_solar[base_solar < 0] = 0

    productions = np.array([
        base_solar * (0.7 + 0.6 * rng.random()) * (1 + volatility * rng.standard_normal(hours))
        for _ in range(n_houses)
    ]).clip(0)

    # Tüketim profili
    hour_weight = np.ones(hours)
    peak_start = max(0, 17 - peak_hours // 2)
    hour_weight[peak_start:peak_start + peak_hours] = 2.2
    hour_weight[6:9] = 1.6

    consumptions = np.array([
        hour_weight * (0.5 + 1.5 * rng.random()) * (1 + 0.15 * rng.standard_normal(hours))
        for _ in range(n_houses)
    ]).clip(0.1)

    # Nash dengesi (saatlik)
    hourly_grid = []
    for h in range(hours):
        eq = nash_equilibrium_energy(productions[:, h], consumptions[:, h], 1.0)
        hourly_grid.append(eq["grid_load"].sum())

    # Shapley değeri (günlük toplam)
    daily_prod = productions.mean(axis=1)
    daily_cons = consumptions.mean(axis=1)
    char_fn = characteristic_fn_factory(daily_prod, daily_cons, solar_eff)
    shapley = shapley_value(n_houses, char_fn)

    # Depolama simülasyonu
    storage_level = np.zeros(hours)
    level = storage_cap * 0.3
    for h in range(hours):
        total_prod = productions[:, h].sum()
        total_cons = consumptions[:, h].sum()
        balance = total_prod - total_cons
        if balance > 0:
            level = min(level + balance * 0.1, storage_cap)
        else:
            draw = min(abs(balance) * 0.1, level)
            level = max(level - draw, 0)
        storage_level[h] = level

    return {
        "productions": productions,
        "consumptions": consumptions,
        "hourly_grid": np.array(hourly_grid),
        "shapley": shapley,
        "storage": storage_level,
        "hours": list(range(hours)),
    }


# ─────────────────────────────────────────────
#  GRAFIK FONKSİYONLARI
# ─────────────────────────────────────────────

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(10,15,25,0.85)",
    font=dict(family="Rajdhani, sans-serif", color="#c8d8e8", size=13),
    margin=dict(l=40, r=20, t=50, b=40),
    xaxis=dict(gridcolor="rgba(0,255,200,0.06)", zerolinecolor="rgba(0,255,200,0.1)"),
    yaxis=dict(gridcolor="rgba(0,255,200,0.06)", zerolinecolor="rgba(0,255,200,0.1)"),
)


def pie_chart(shapley: np.ndarray, n_houses: int) -> go.Figure:
    labels = [f"Hane {i+1}" for i in range(n_houses)]
    values = np.maximum(shapley, 0.01)

    colors = px.colors.sample_colorscale(
        "Teal", [i / max(n_houses - 1, 1) for i in range(n_houses)]
    )

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=colors, line=dict(color="#0a0a0a", width=2)),
        textfont=dict(family="Share Tech Mono", size=11),
        hovertemplate="<b>%{label}</b><br>Shapley: %{value:.3f} kWh<extra></extra>",
    ))

    fig.update_layout(
        **PLOT_LAYOUT,
        title=dict(text="⚡ Shapley Kazanç Dağılımı", font=dict(family="Orbitron", size=15, color="#00ffc8")),
        showlegend=n_houses <= 15,
        legend=dict(font=dict(size=10)),
        annotations=[dict(
            text=f"<b>{n_houses}</b><br><span style='font-size:10px'>HANE</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(family="Orbitron", size=16, color="#00ffc8"),
            align="center",
        )],
    )
    return fig


def line_chart(hours, grid_load, storage, productions, consumptions) -> go.Figure:
    total_prod = productions.sum(axis=0)
    total_cons = consumptions.sum(axis=0)

    fig = go.Figure()

    # Şebeke yükü
    fig.add_trace(go.Scatter(
        x=hours, y=grid_load, name="Şebeke Yükü (kW)",
        line=dict(color="#ff4d6d", width=2.5, dash="solid"),
        fill="tozeroy", fillcolor="rgba(255,77,109,0.08)",
        hovertemplate="Saat %{x}:00 → %{y:.2f} kW<extra></extra>",
    ))

    # Toplam üretim
    fig.add_trace(go.Scatter(
        x=hours, y=total_prod, name="Toplam Üretim (kW)",
        line=dict(color="#00ffc8", width=2),
        hovertemplate="Saat %{x}:00 → %{y:.2f} kW<extra></extra>",
    ))

    # Toplam tüketim
    fig.add_trace(go.Scatter(
        x=hours, y=total_cons, name="Toplam Tüketim (kW)",
        line=dict(color="#0096ff", width=2, dash="dot"),
        hovertemplate="Saat %{x}:00 → %{y:.2f} kW<extra></extra>",
    ))

    # Depolama
    fig.add_trace(go.Scatter(
        x=hours, y=storage, name="Depolama (kWh)",
        line=dict(color="#ffd166", width=1.8, dash="dashdot"),
        hovertemplate="Saat %{x}:00 → %{y:.2f} kWh<extra></extra>",
    ))

    fig.update_layout(
        **PLOT_LAYOUT,
        title=dict(text="📊 24 Saatlik Enerji Profili", font=dict(family="Orbitron", size=15, color="#00ffc8")),
        xaxis=dict(**PLOT_LAYOUT["xaxis"], title="Saat", tickmode="linear", tick0=0, dtick=3),
        yaxis=dict(**PLOT_LAYOUT["yaxis"], title="kW / kWh"),
        legend=dict(
            bgcolor="rgba(0,0,0,0.4)",
            bordercolor="rgba(0,255,200,0.2)",
            borderwidth=1,
            font=dict(size=11),
        ),
        hovermode="x unified",
    )
    return fig


def heatmap_chart(productions: np.ndarray) -> go.Figure:
    n = min(productions.shape[0], 20)
    fig = go.Figure(go.Heatmap(
        z=productions[:n],
        colorscale="Teal",
        hovertemplate="Hane %{y} | Saat %{x}:00 → %{z:.2f} kW<extra></extra>",
        colorbar=dict(title="kW", tickfont=dict(color="#c8d8e8")),
    ))
    fig.update_layout(
        **PLOT_LAYOUT,
        title=dict(text="🔆 Güneş Üretim Isı Haritası (İlk 20 Hane)", font=dict(family="Orbitron", size=15, color="#00ffc8")),
        xaxis=dict(**PLOT_LAYOUT["xaxis"], title="Saat"),
        yaxis=dict(**PLOT_LAYOUT["yaxis"], title="Hane"),
    )
    return fig


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    show_logo()
    st.markdown('<div class="neon-line"></div>', unsafe_allow_html=True)

    st.markdown("### 🔧 Simülasyon Parametreleri")

    n_houses = st.slider("🏠 Hane Sayısı", min_value=2, max_value=100, value=10, step=1)
    solar_eff = st.slider("☀️ Güneş Verimliliği (%)", min_value=10, max_value=100, value=75, step=5) / 100
    storage_cap = st.slider("🔋 Depolama Kapasitesi (kWh)", min_value=5, max_value=500, value=50, step=5)
    peak_hours = st.slider("⏱️ Pik Saati Süresi (saat)", min_value=1, max_value=8, value=3, step=1)
    volatility = st.slider("🌩️ Üretim Değişkenliği", min_value=0.0, max_value=1.0, value=0.2, step=0.05)
    rng_seed = st.slider("🎲 Rastgele Tohum", min_value=1, max_value=999, value=42, step=1)

    st.markdown('<div class="neon-line"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'Share Tech Mono',monospace; font-size:0.68rem; color:#5a7a8a; line-height:1.7;">
      <span class="tag">OYUN TEORİSİ</span>
      <span class="tag">NASH DENGESİ</span>
      <span class="tag">SHAPLEY</span><br><br>
      © 2025 MathErgy 212510<br>
      Smart Grid Simulation Engine
    </div>
    """, unsafe_allow_html=True)

    start_btn = st.button("⚡  SİMÜLASYONU BAŞLAT")


# ─────────────────────────────────────────────
#  ANA EKRAN
# ─────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:4px;">
  <span style="font-family:'Orbitron',sans-serif; font-size:2rem; font-weight:900;
    color:#00ffc8; letter-spacing:5px; text-shadow: 0 0 30px rgba(0,255,200,0.4);">
    MATH<span style="color:#0096ff;">ERGY</span>
  </span>
  <span style="font-family:'Share Tech Mono',monospace; font-size:0.75rem;
    color:#5a7a8a; letter-spacing:3px; margin-left:12px;">212510</span>
</div>
<div style="font-family:'Rajdhani',sans-serif; font-size:1rem; color:#7ecfff;
  letter-spacing:2px; margin-bottom:2px;">
  Akıllı Mahalle Enerji Paylaşımı & Optimizasyon Simülatörü
</div>
""", unsafe_allow_html=True)
st.markdown('<div class="neon-line"></div>', unsafe_allow_html=True)

# Bilgi satırı
col_i1, col_i2, col_i3, col_i4 = st.columns(4)
col_i1.markdown(f'<div class="stat-card"><div style="color:#7ecfff;font-size:0.75rem;letter-spacing:1px;">HANE SAYISI</div><div style="font-family:\'Orbitron\',monospace;font-size:1.4rem;color:#00ffc8;">{n_houses}</div></div>', unsafe_allow_html=True)
col_i2.markdown(f'<div class="stat-card"><div style="color:#7ecfff;font-size:0.75rem;letter-spacing:1px;">GÜNEŞ VERİMLİLİĞİ</div><div style="font-family:\'Orbitron\',monospace;font-size:1.4rem;color:#00ffc8;">{solar_eff*100:.0f}%</div></div>', unsafe_allow_html=True)
col_i3.markdown(f'<div class="stat-card"><div style="color:#7ecfff;font-size:0.75rem;letter-spacing:1px;">DEPOLAMA KAP.</div><div style="font-family:\'Orbitron\',monospace;font-size:1.4rem;color:#00ffc8;">{storage_cap} kWh</div></div>', unsafe_allow_html=True)
col_i4.markdown(f'<div class="stat-card"><div style="color:#7ecfff;font-size:0.75rem;letter-spacing:1px;">DEĞİŞKENLİK</div><div style="font-family:\'Orbitron\',monospace;font-size:1.4rem;color:#00ffc8;">{volatility:.2f}</div></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SİMÜLASYON
# ─────────────────────────────────────────────
if start_btn:
    with st.status("⚡ Simülasyon hesaplanıyor...", expanded=True) as status:
        st.write("🔢 Nash Dengesi hesaplanıyor...")
        time.sleep(0.8)
        st.write("📐 Koalisyon karakteristik fonksiyonu oluşturuluyor...")
        time.sleep(0.7)
        st.write("🧮 Shapley değerleri hesaplanıyor (permütasyon analizi)...")
        time.sleep(1.0)
        st.write("🔋 Depolama optimizasyonu simüle ediliyor...")
        time.sleep(0.6)
        st.write("📊 Grafikler render ediliyor...")
        time.sleep(0.5)

        result = simulate(n_houses, solar_eff, storage_cap, peak_hours, volatility, rng_seed)
        status.update(label="✅ Simülasyon tamamlandı!", state="complete", expanded=False)

    # ── METRİKLER ──
    st.markdown("---")
    total_prod = result["productions"].sum()
    total_cons = result["consumptions"].sum()
    total_grid = result["hourly_grid"].sum()
    self_suff = max(0, (1 - total_grid / (total_cons + 1e-9))) * 100
    coop_gain = result["shapley"].sum()

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("⚡ Toplam Üretim", f"{total_prod:.1f} kWh")
    m2.metric("🏠 Toplam Tüketim", f"{total_cons:.1f} kWh")
    m3.metric("🔌 Şebeke Bağımlılığı", f"{total_grid:.1f} kWh")
    m4.metric("🌱 Öz Yeterlilik", f"{self_suff:.1f}%")
    m5.metric("🤝 İşbirliği Kazancı", f"{coop_gain:.2f}")

    st.markdown("---")

    # ── GRAFİKLER ──
    tab1, tab2, tab3 = st.tabs(["📊  ENERJİ PROFİLİ", "🥧  KAZANÇ DAĞILIMI", "🔆  ÜRETIM ISI HARİTASI"])

    with tab1:
        fig_line = line_chart(
            result["hours"],
            result["hourly_grid"],
            result["storage"],
            result["productions"],
            result["consumptions"],
        )
        st.plotly_chart(fig_line, use_container_width=True)

    with tab2:
        col_p1, col_p2 = st.columns([1.1, 0.9])
        with col_p1:
            fig_pie = pie_chart(result["shapley"], n_houses)
            st.plotly_chart(fig_pie, use_container_width=True)
        with col_p2:
            st.markdown("#### 🧮 Shapley Değerleri Tablosu")
            shapley_df = pd.DataFrame({
                "Hane": [f"Hane {i+1}" for i in range(n_houses)],
                "Shapley (kWh)": result["shapley"].round(4),
                "Pay (%)": (result["shapley"] / (result["shapley"].sum() + 1e-9) * 100).round(2),
            }).sort_values("Shapley (kWh)", ascending=False).reset_index(drop=True)
            st.dataframe(shapley_df, use_container_width=True, height=380)

    with tab3:
        fig_heat = heatmap_chart(result["productions"])
        st.plotly_chart(fig_heat, use_container_width=True)

    # ── ÖZET ──
    st.markdown("---")
    st.markdown("#### 📋 Simülasyon Özeti")
    st.markdown(f"""
    <div class="stat-card">
      <p>
        <b style="color:#00ffc8;">{n_houses}</b> hanelik mikrogrid simülasyonu tamamlandı.
        Güneş verimliliği <b style="color:#00ffc8;">{solar_eff*100:.0f}%</b> ile toplam
        <b style="color:#0096ff;">{total_prod:.1f} kWh</b> üretildi.
        Nash Dengesi algoritması ile adil enerji transferi hesaplandı;
        Shapley değerleri kooperatif kazancı <b style="color:#ffd166;">{coop_gain:.2f}</b> olarak dağıttı.
        Sistemin öz yeterlilik oranı <b style="color:#00ffc8;">{self_suff:.1f}%</b> olarak hesaplandı.
      </p>
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="text-align:center; padding: 80px 0; color:#3a5a6a;">
      <div style="font-family:'Orbitron',sans-serif; font-size:3.5rem; color:rgba(0,255,200,0.12);">⚡</div>
      <div style="font-family:'Share Tech Mono',monospace; font-size:0.85rem; letter-spacing:3px; margin-top:12px; color:#2a4a5a;">
        SİMÜLASYONU BAŞLATMAK İÇİN SOL PANELDEKİ BUTONA BASIN
      </div>
    </div>
    """, unsafe_allow_html=True)
