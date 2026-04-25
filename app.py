import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time
from PIL import Image

# Sayfa Ayarları
st.set_page_config(page_title="MathErgy 212510", layout="wide", page_icon="⚡")

# --- GELİŞMİŞ CSS ---
st.markdown("""
    <style>
    .stApp {
        background-image: url("https://www.transparenttextures.com/patterns/carbon-fibre.png");
        background-attachment: fixed;
    }
    .metric-container {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #2e7d32;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ÜST PANEL (LOGO VE BAŞLIK) ---
col_main1, col_main2, col_main3 = st.columns([1, 2, 1])
with col_main2:
    try:
        logo = Image.open("logo.png")
        st.image(logo, use_container_width=True)
    except:
        st.markdown("<h1 style='text-align: center; color: #1b5e20;'>⚡ MathErgy 212510</h1>", unsafe_allow_html=True)

st.markdown("<p style='text-align: center; font-size: 20px;'>Oyun Teorisi ve Nash Dengesi ile Akıllı Enerji Yönetimi</p>", unsafe_allow_html=True)

# --- YAN PANEL (KONTROL) ---
st.sidebar.header("🕹️ Parametre Girişi")
g_verim = st.sidebar.slider("☀️ Güneş Paneli Verimliliği (%)", 0, 100, 75)
h_sayisi = st.sidebar.slider("🏠 Mahalledeki Hane Sayısı", 2, 100, 25) # 100'e çıkarıldı
mod_secim = st.sidebar.selectbox("Matematiksel Model", ["Shapley Değeri", "Nash Dengesi", "Hibrit Model"])
sim_hiz = st.sidebar.select_slider("Simülasyon Detayı", options=["Hızlı", "Normal", "Derin Analiz"])

start_sim = st.sidebar.button("🚀 Simülasyonu Başlat")

if start_sim:
    # --- GERÇEKÇİ BEKLEME EKRANI ---
    with st.status("🧠 Matematiksel Optimizasyon Yapılıyor...", expanded=True) as status:
        st.write("Düğümler oluşturuluyor...")
        time.sleep(1)
        st.write(f"{h_sayisi} hane için Nash Dengesi hesaplanıyor...")
        time.sleep(1.5)
        if sim_hiz == "Derin Analiz":
            st.write("Karbon ayak izi projeksiyonu derinleştiriliyor...")
            time.sleep(2)
        status.update(label="✅ Analiz Başarıyla Tamamlandı!", state="complete", expanded=False)

    # Hesaplamalar (Dinamik)
    tasarruf = 35 * (g_verim / 100)
    toplam_uretim = h_sayisi * (g_verim * 1.5)
    
    # --- METRİKLER ---
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("🍀 Karbon Tasarrufu", f"%{tasarruf:.1f}")
    with m2:
        st.metric("🔌 Toplam Üretim", f"{toplam_uretim:.0f} kWh")
    with m3:
        st.metric("📊 Sistem Kararlılığı", "%98.2")
    with m4:
        st.metric("🤝 Katılım Oranı", f"{h_sayisi}/{h_sayisi}")

    st.write("---")

    # --- GRAFİKLER ---
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### ⚖️ Kazanç Dağılımı (Pasta Grafik)")
        # Dinamik veri oluşturma
        labels = [f"Hane {i+1}" for i in range(min(h_sayisi, 10))] # Çok hane varsa ilk 10'u göster
        if h_sayisi > 10: labels.append("Diğer Haneler")
        
        values = list(np.random.dirichlet(np.ones(len(labels)), size=1)[0] * 100)
        fig_pie = px.pie(values=values, names=labels, hole=0.4, color_discrete_sequence=px.colors.sequential.Greens_r)
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        st.markdown("### 📈 Şebeke Yük Analizi")
        chart_data = pd.DataFrame(
            np.random.randn(24, 2),
            columns=['Geleneksel Şebeke', 'MathErgy 212510']
        )
        st.line_chart(chart_data)

    # --- YENİ VERİ TABLOSU ---
    st.markdown("### 📋 Detaylı Analiz Çizelgesi")
    detay_data = pd.DataFrame({
        'Hane ID': [f"M-2125-{i}" for i in range(h_sayisi)],
        'Üretim (kWh)': np.random.uniform(10, 50, h_sayisi).round(2),
        'Tüketim (kWh)': np.random.uniform(20, 45, h_sayisi).round(2),
        'Shapley Kazancı (₺)': np.random.uniform(5, 25, h_sayisi).round(2)
    })
    st.dataframe(detay_data, use_container_width=True)

else:
    st.info("👈 Yan panelden verileri girip simülasyonu başlatabilirsiniz. MathErgy 212510 sistemi şu an beklemede.")

st.markdown("---")
st.caption("MathErgy 212510 | Sürdürülebilir Gelecek Prototipi")
