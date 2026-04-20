import streamlit as st
import pandas as pd
from datetime import datetime
import time
import webbrowser
import urllib.parse
import os

# --- KONFİGÜRASYON ---
st.set_page_config(page_title="MODEREN Mühendislik Pro", layout="wide", page_icon="🔥")
DB_FILE = "moderen_kesim_database.csv"
MUHENDIS_TEL = "+905XXXXXXXXX"  # BURAYI GÜNCELLE USTA!

# --- STİL VE ARAYÜZ ---
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; font-weight: bold; }
    .st-emotion-cache-1cv0aru { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0px 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🔧 MODEREN Mühendislik | Bodor Lazer Asistanı")
st.info("Eren Usta, sistem hazır. Kesimi başlat, kaydet ve gerisini asistana bırak.")

# --- ANA PANEL ---
col_form, col_hata = st.columns([2, 1])

with col_form:
    st.subheader("📋 Kesim Detayları")
    with st.container():
        c1, c2 = st.columns(2)
        malzeme = c1.text_input("Malzeme / Parça Adı", placeholder="Örn: 10mm Flanş")
        cins = c2.selectbox("Malzeme Cinsi", ["Siyah Sac (S235)", "Paslanmaz (304/316)", "Alüminyum", "Galvaniz"])
        
        c3, c4 = st.columns(2)
        kalinlik = c3.number_input("Kalınlık (mm)", 0.5, 50.0, 5.0)
        gaz = c4.radio("Kesim Gazı", ["Oksijen (O2)", "Azot (N2)"], horizontal=True)

    # Süre Ölçer Bölümü
    st.divider()
    if 'start_time' not in st.session_state: st.session_state.start_time = None
    if 'last_duration' not in st.session_state: st.session_state.last_duration = 0

    sc1, sc2, sc3 = st.columns(3)
    if sc1.button("⏱️ KESİMİ BAŞLAT", type="primary"):
        st.session_state.start_time = time.time()
        st.toast("Kronometre başladı!", icon="🚀")

    if sc2.button("⏹️ KESİMİ BİTİR"):
        if st.session_state.start_time:
            duration = round((time.time() - st.session_state.start_time) / 60, 2)
            st.session_state.last_duration = duration
            st.success(f"Süre: {duration} Dakika")
        else:
            st.warning("Önce başlatmalısın!")

    # --- KAYIT VE WHATSAPP PAKETİ ---
    if st.button("✅ KAYDI TAMAMLA VE MÜHENDİSE RAPORLA"):
        tarih = datetime.now().strftime("%d/%m/%Y %H:%M")
        sure_dk = st.session_state.last_duration
        
        yeni_data = {
            "Tarih": tarih, "Malzeme": malzeme, "Cins": cins, 
            "Kalınlık": f"{kalinlik}mm", "Gaz": gaz, "Süre (dk)": sure_dk
        }
        
        # Veriyi Kaydet
        df = pd.DataFrame([yeni_data])
        if os.path.exists(DB_FILE):
            mevcut_df = pd.read_csv(DB_FILE)
            df = pd.concat([mevcut_df, df], ignore_index=True)
        df.to_csv(DB_FILE, index=False)
        
        # WhatsApp Mesajı Oluştur (Özet Rapor)
        rapor_mesaj = (
            f"📢 *MODEREN MÜHENDİSLİK KESİM RAPORU*\n\n"
            f"✅ *Son İş:* {malzeme}\n"
            f"🔹 *Detay:* {cins} - {kalinlik}mm\n"
            f"⛽ *Gaz:* {gaz}\n"
            f"⏱️ *Süre:* {sure_dk} Dakika\n"
            f"📅 *Tarih:* {tarih}\n\n"
            f"📊 _Not: Bu veri sisteme otomatik işlenmiştir._"
        )
        
        wp_url = f"https://wa.me/{MUHENDIS_TEL}?text={urllib.parse.quote(rapor_mesaj)}"
        webbrowser.open(wp_url)
        st.balloons()
        st.success("Veri kaydedildi ve rapor WhatsApp'a gönderildi!")

with col_hata:
    st.subheader("🛠️ Bodor Hata Sözlüğü")
    hata_kod = st.text_input("Hata Kodunu Yaz (Örn: E28)", "").upper()
    sozluk = {
        "E28": "Kesim kafası çarpma hatası! Sensörü kontrol et.",
        "E510": "Sürücü (Driver) hatası. Enerjiyi kapat-aç, kabloları kontrol et.",
        "E100": "Gaz basıncı yetersiz! Tüpü veya kompresörü kontrol et."
    }
    if hata_kod:
        st.error(sozluk.get(hata_kod, "Kod bulunamadı. Lütfen kılavuza bak veya mühendise sor."))

# --- GEÇMİŞ TABLOSU ---
st.divider()
st.subheader("📜 Geçmiş Kesim Kayıtları")
if os.path.exists(DB_FILE):
    data = pd.read_csv(DB_FILE)
    st.dataframe(data.sort_index(ascending=False), use_container_width=True)