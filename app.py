import streamlit as st
import pandas as pd
from PIL import Image

# Sayfa ayarları - Tarayıcı sekmesinde 212510 görünecek
st.set_page_config(page_title="MathErgy 212510", layout="wide", page_icon="⚡")

# --- LOGO VE BAŞLIK KISMI ---
# Not: Logonun adını 'logo.png' yapıp GitHub'a yüklemeyi unutma.
try:
    logo = Image.open("logo.png")
    col_l1, col_l2, col_l3 = st.columns([1, 1, 1])
    with col_l2:
        st.image(logo, width=180)
except:
    st.info("Logo dosyası (logo.png) yüklenince burada şık bir şekilde görünecek.")

st.markdown("<h1 style='text-align: center; color: #1B5E20;'>⚡ MathErgy 212510</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px; color: #4CAF50;'>Akıllı Enerji Paylaşımı ve Karbon Tasarrufu Optimizasyon Sistemi</p>", unsafe_allow_html=True)
st.write("---")

# --- YAN PANEL ---
st.sidebar.header("🕹️ Sistem Kontrol Merkezi")
st.sidebar.write(f"*Sürüm:* 212510-Alpha")
gunes_verimi = st.sidebar.slider("☀️ Güneş Paneli Verimliliği (%)", 0, 100, 85)
ev_sayisi = st.sidebar.slider("🏠 Mahalledeki Ev Sayısı", 2, 12, 6)
isbirligi = st.sidebar.toggle("MathErgy 212510 Optimizasyonunu Çalıştır", value=True)

# --- ANALİZ VE HESAPLAMA ---
tasarruf = 30 * (gunes_verimi / 100) if isbirligi else 0

st.subheader("📊 Canlı Veri Analizi")
m1, m2, m3 = st.columns(3)

with m1:
    st.metric("Karbon Tasarrufu", f"%{tasarruf:.1f}", delta="Hedef %30")
with m2:
    st.metric("Paylaşım Ağı", f"{ev_sayisi} Hane", delta="Aktif Bağlantı")
with m3:
    st.metric("Sistem Verimliliği", "Yüksek" if isbirligi else "Düşük", delta="Model Aktif")

st.write("---")

# --- GRAFİKLER ---
c1, c2 = st.columns(2)

with c1:
    st.markdown("### ⚖️ Adil Kazanç Dağılımı (Shapley)")
    evler = [f"Ev {i+1}" for i in range(ev_sayisi)]
    # Her ev için adil dağıtılmış kazanç simülasyonu
    kazanc = [round((120/ev_sayisi) * (1 + (i*0.04)), 2) for i in range(ev_sayisi)]
    df_shapley = pd.DataFrame({"Haneler": evler, "Kazanç Payı (Unit)": kazanc})
    st.bar_chart(df_shapley.set_index("Haneler"))

with c2:
    st.markdown("### 🌳 Karbon Ayak İzi Karşılaştırması")
    sebeke_etki = 100
    mathergy_etki = 100 - tasarruf
    df_co2 = pd.DataFrame({
        "Model": ["Geleneksel Şebeke", "MathErgy 212510"],
        "CO2 Salınımı": [sebeke_etki, mathergy_etki]
    })
    st.area_chart(df_co2.set_index("Model"))

st.write("---")
st.caption("MathErgy 212510 © 2026 - Geleceğin Şehirleri İçin Matematiksel Paylaşım Modeli")
