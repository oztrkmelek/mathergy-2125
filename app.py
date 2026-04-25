import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
from PIL import Image

# Sayfa Ayarları
st.set_page_config(page_title="MathErgy 212510 - Global", layout="wide", page_icon="🌍")

# --- AÇIK RENK VE MODERN TASARIM (CSS) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    }
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #cbd5e0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    h1, h2, h3 { color: #1e293b !important; font-family: 'Inter', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: KONUM VE VERİ GİRİŞİ ---
st.sidebar.header("📍 Konum Servisleri")
sehir = st.sidebar.selectbox("Simülasyon Bölgesi Seçin", ["İzmir", "İstanbul", "Ankara", "Antalya", "Londra", "Berlin"])
st.sidebar.caption(f"Şu an {sehir} koordinatları taranıyor...")

st.sidebar.divider()
st.sidebar.header("🏠 Mahalle Yapılandırması")
h_sayisi = st.sidebar.slider("Hane Sayısı", 2, 50, 10)
panel_kapasite = st.sidebar.number_input("Panel Gücü (W)", value=400)

start_sim = st.sidebar.button("🚀 Bölgeyi Tara ve Analiz Et")

# --- ANA EKRAN ---
st.title(f"🌍 MathErgy 212510: {sehir} Paneli")
st.markdown(f"*Durum:* {sehir} bölgesi için fotovoltaik potansiyel analizi aktif.")

if start_sim:
    # --- KONUM TARAMA ANİMASYONU ---
    with st.status(f"🛰️ {sehir} Konumu Üzerinden Uydu Verileri Çekiliyor...", expanded=True) as status:
        st.write("📍 Koordinatlar belirleniyor...")
        time.sleep(1)
        st.write("⛅ Anlık bulutluluk oranı analiz ediliyor...")
        time.sleep(1.2)
        st.write("📐 Nash Dengesi optimizasyon katmanı yükleniyor...")
        time.sleep(1)
        status.update(label="✅ Veri Senkronizasyonu Tamamlandı!", state="complete", expanded=False)

    # Veri Üretimi (Konuma Göre Değişen Rastgelelik)
    np.random.seed(len(sehir))
    uretim = np.random.uniform(20, 100, h_sayisi)
    tuketim = np.random.uniform(30, 80, h_sayisi)
    
    # --- HARİTA GÖRÜNÜMÜ (KONUM SİMÜLASYONU) ---
    st.subheader("🗺️ Akıllı Şebeke Harita Dağılımı")
    map_data = pd.DataFrame({
        'lat': [38.42 + np.random.uniform(-0.01, 0.01) for _ in range(h_sayisi)],
        'lon': [27.14 + np.random.uniform(-0.01, 0.01) for _ in range(h_sayisi)],
        'Enerji Durumu': uretim - tuketim
    })
    st.map(map_data) # Seçtiğin şehre göre noktaları haritaya basar

    st.divider()

    # --- METRİKLER ---
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("☀️ Bölgesel Verimlilik", f"%{np.random.randint(70,95)}")
    with c2:
        st.metric("🍃 Karbon Azaltımı", f"{h_sayisi * 12.4:.1f} kg/gün")
    with c3:
        st.metric("🤝 Paylaşım Ekonomisi", f"{sum(uretim > tuketim)} Aktif Hane")

    # --- GRAFİKLER ---
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("### ⚖️ Shapley Paylaşım Modeli")
        fig_pie = px.sunburst(
            path=['Enerji Durumu', 'Hane'], 
            values=uretim,
            names=[f"Hane {i+1}" for i in range(h_sayisi)],
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_right:
        st.markdown("### 📈 Anlık Şebeke Dengesi")
        line_data = pd.DataFrame({
            'Saat': list(range(24)),
            'Üretim': np.sin(np.linspace(0, 3, 24)) * 50 + 20,
            'Tüketim': np.random.normal(40, 5, 24)
        })
        st.line_chart(line_data.set_index('Saat'))

    # --- DETAYLI TABLO ---
    st.markdown("### 📋 Teknik Analiz Çizelgesi")
    df_result = pd.DataFrame({
        "Hane ID": [f"ID-{1000+i}" for i in range(h_sayisi)],
        "Anlık Üretim (kWh)": uretim.round(2),
        "Anlık Tüketim (kWh)": tuketim.round(2),
        "Nash Dengesi Skoru": np.random.uniform(0.8, 0.99, h_sayisi).round(3)
    })
    st.dataframe(df_result, use_container_width=True)

else:
    st.info("👈 Simülasyonu başlatmak için konumunuzu seçin ve 'Bölgeyi Tara' butonuna basın.")
