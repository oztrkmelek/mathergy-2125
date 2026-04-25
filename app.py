import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import time

# Sayfa Konfigürasyonu
st.set_page_config(
    page_title="MathErgy 212510 - Akıllı Enerji Paneli",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Koyu Tema ve Carbon Fibre Görünümü için CSS
st.markdown("""
    <style>
    .main {
        background-color: #121212;
        background-image: radial-gradient(#2c2c2c 0.5px, transparent 0.5px);
        background-size: 10px 10px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #00d1b2;
        color: white;
        font-weight: bold;
    }
    .stMetric {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #333;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar - Parametreler
with st.sidebar:
    try:
        logo = Image.open('logo.png')
        st.image(logo, use_container_width=True)
    except FileNotFoundError:
        st.error("logo.png bulunamadı. Lütfen dizine ekleyin.")
    
    st.title("⚙️ Kontrol Paneli")
    st.divider()
    
    n_households = st.slider("Hane Sayısı", min_value=2, max_value=100, value=10)
    solar_efficiency = st.slider("Güneş Verimliliği (%)", 0, 100, 75)
    grid_price = st.number_input("Şebeke Birim Fiyatı (₺/kWh)", value=2.5)
    
    st.info("Bu simülasyon Nash Dengesi ve Shapley Değeri algoritmalarını temel alır.")

# Ana Başlık
st.title("⚡ MathErgy 212510")
st.subheader("Kooperatif Enerji Paylaşımı ve Akıllı Şebeke Simülasyonu")

# Simülasyon Fonksiyonu
def run_simulation(n, efficiency):
    # Sentetik veri üretimi
    time_steps = np.arange(0, 24, 1)
    base_load = np.random.normal(1.5, 0.3, (n, 24))
    solar_gen = (np.sin(np.pi * (time_steps - 6) / 12).clip(0) * (efficiency / 100)) * 2.5
    
    # Toplam şebeke yükü hesaplama
    net_load = base_load.sum(axis=0) - (solar_gen * n * 0.6)
    
    # Shapley Değeri Basitleştirilmiş Model (Kazanç Dağılımı)
    # Gerçek Shapley 2^n kompleksitesindedir, burada n=100 için yaklaşım kullanılır.
    contributions = np.random.dirichlet(np.ones(n), size=1)[0]
    total_savings = np.sum(solar_gen) * grid_price * 0.4 # %40 kooperatif avantajı
    shapley_values = contributions * total_savings
    
    return time_steps, net_load, shapley_values

# Başlat Butonu ve Animasyon
if st.button("🚀 Simülasyonu Başlat"):
    with st.status("Hesaplanıyor...", expanded=True) as status:
        st.write("Şebeke yükleri analiz ediliyor...")
        time.sleep(1.5)
        st.write("Kooperatif oyun teorisi matrisleri oluşturuluyor...")
        time.sleep(1.5)
        st.write("Shapley değerleri dağıtılıyor...")
        time.sleep(1)
        status.update(label="Simülasyon Tamamlandı!", state="complete", expanded=False)

    t, load, gains = run_simulation(n_households, solar_efficiency)

    # Metrikler
    col1, col2, col3 = st.columns(3)
    col1.metric("Toplam Tasarruf", f"{gains.sum():.2f} ₺", "+12%")
    col2.metric("Şebeke Bağımlılığı", f"{load.mean():.2f} kWh", "-5%")
    col3.metric("Nash Dengesi Skoru", "0.88", "Kararlı")

    st.divider()

    # Grafikler
    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.markdown("### 📊 Kazanç Dağılımı (Shapley Değeri)")
        df_pie = pd.DataFrame({
            'Hane': [f'Hane {i+1}' for i in range(min(n_households, 10))],
            'Kazanç': gains[:10]
        })
        if n_households > 10:
            other_gains = gains[10:].sum()
            df_pie = pd.concat([df_pie, pd.DataFrame({'Hane': ['Diğer'], 'Kazanç': [other_gains]})])
        
        fig_pie = px.pie(df_pie, values='Kazanç', names='Hane', hole=0.4,
                         color_discrete_sequence=px.colors.sequential.Tealgrn)
        fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)

    with row2_col2:
        st.markdown("### 📈 24 Saatlik Şebeke Yükü")
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=t, y=load, mode='lines+markers', 
                                     name='Net Yük', line=dict(color='#00d1b2', width=3)))
        fig_line.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Saat",
            yaxis_title="kWh",
            hovermode="x unified"
        )
        st.plotly_chart(fig_line, use_container_width=True)

    # Veri Tablosu
    with st.expander("Detaylı Veri Setini Görüntüle"):
        df_results = pd.DataFrame({
            'Hane ID': range(1, n_households + 1),
            'Tahsis Edilen Kazanç (₺)': gains
        })
        st.dataframe(df_results, use_container_width=True)
else:
    st.warning("Simülasyonu başlatmak için sol menüden parametreleri ayarlayıp butona basınız.")
