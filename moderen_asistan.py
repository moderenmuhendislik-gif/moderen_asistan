import streamlit as st
import pandas as pd
from datetime import datetime
import time
import webbrowser
import urllib.parse
import os
# SES KÜTÜPHANESİ (Yüklemiş olman lazım: pip install streamlit-mic-recorder)
from streamlit_mic_recorder import mic_recorder

# --- AYARLAR ---
st.set_page_config(page_title="MODEREN Lazer V5", layout="wide", page_icon="🎙️")
DB_FILE = "moderen_database_v5.csv"
MUHENDIS_TEL = "+905511254762" 
MESAI_SANIYE = 36900 # 08:00 - 18:15

def format_sure(saniye):
    hrs, rem = divmod(int(saniye), 3600)
    mins, secs = divmod(rem, 60)
    return f"{hrs:02d}:{mins:02d}:{secs:02d}"

st.title("🚀 MODEREN Mühendislik | Sesli Asistan")

# --- ÜST PANEL (VERİMLİLİK) ---
if os.path.exists(DB_FILE):
    df_all = pd.read_csv(DB_FILE)
    bugun = datetime.now().strftime("%d/%m/%Y")
    bugun_df = df_all[df_all['Tarih'].str.contains(bugun)]
    toplam_s = bugun_df['Saniye_Ham'].sum() if not bugun_df.empty else 0
    oran = (toplam_s / MESAI_SANIYE) * 100
    m1, m2, m3 = st.columns(3)
    m1.metric("Toplam Kesim", format_sure(toplam_s))
    m2.metric("Çalışma Oranı", f"%{oran:.2f}")
    m3.progress(min(oran/100, 1.0))
else:
    toplam_s = 0

st.divider()

# --- SESLİ KOMUT MERKEZİ ---
st.subheader("🎙️ Sesli Kontrol (Başla / Durdur / Kaydet)")
ses_verisi = mic_recorder(start_prompt="Sesli Komut Ver", stop_prompt="Dinlemeyi Bitir", key='recorder')

if 'start' not in st.session_state: st.session_state.start = None
if 'current_s' not in st.session_state: st.session_state.current_s = 0

if ses_verisi:
    komut = ses_verisi['text'].lower()
    st.write(f"Anlaşılan: *{komut}*")
    
    if "başla" in komut or "başlat" in komut:
        st.session_state.start = time.time()
        st.success("Kesim Başlatıldı!")
    elif "durdur" in komut or "bitir" in komut:
        if st.session_state.start:
            st.session_state.current_s = int(time.time() - st.session_state.start)
            st.session_state.start = None
            st.warning("Kesim Durduruldu!")
    elif "kaydet" in komut:
        st.info("Kayıt işlemi tetikleniyor...")
        # Kayıt mantığı burada da çalıştırılabilir

# --- MANUEL PANEL ---
col_sol, col_sag = st.columns([2, 1])

with col_sol:
    st.subheader("📋 Kesim Girişi")
    c1, c2, c3 = st.columns(3)
    malzeme = c1.text_input("Parça Adı", "Parça 1")
    cins = c2.selectbox("Cins", ["Siyah Sac", "Paslanmaz", "Alüminyum"])
    kalinlik = c3.number_input("mm", 0.5, 50.0, 5.0)

    st.write(f"## ⏱️ {format_sure(st.session_state.current_s)}")
    
    b1, b2, b3 = st.columns(3)
    if b1.button("▶️ BAŞLAT"):
        st.session_state.start = time.time()
    if b2.button("⏹️ BİTİR"):
        if st.session_state.start:
            st.session_state.current_s = int(time.time() - st.session_state.start)
            st.session_state.start = None
    if b3.button("💾 KAYDET", type="primary"):
        tarih = datetime.now().strftime("%d/%m/%Y %H:%M")
        yeni = {"Tarih": tarih, "Malzeme": malzeme, "Cins": cins, "Süre": format_sure(st.session_state.current_s), "Saniye_Ham": st.session_state.current_s}
        df = pd.DataFrame([yeni])
        if os.path.exists(DB_FILE):
            df = pd.concat([pd.read_csv(DB_FILE), df], ignore_index=True)
        df.to_csv(DB_FILE, index=False)
        st.success("Kaydedildi!")
        st.rerun()

with col_sag:
    st.subheader("🛠️ Hata Kodu")
    hata = st.text_input("Bodor Hata Kodu").upper()
    sozluk = {"E28": "Kafa Çarpma!", "E510": "Sürücü Hatası!", "E100": "Gaz Düşük!"}
    if hata: st.error(sozluk.get(hata, "Bilinmeyen Kod"))

# --- GÜN SONU ---
st.divider()
if st.button("🚀 GÜN SONU RAPORUNU MÜHENDİSE AT"):
    if os.path.exists(DB_FILE):
        bugun_str = datetime.now().strftime("%d/%m/%Y")
        msg = f"🚀 *GÜN SONU RAPORU*\n📅 *Tarih:* {bugun_str}\n📊 *Verim:* %{oran:.2f}\n⏱️ *Toplam:* {format_sure(toplam_s)}"
        link = f"https://wa.me/{MUHENDIS_TEL}?text={urllib.parse.quote(msg)}"
        webbrowser.open(link)

st.dataframe(pd.read_csv(DB_FILE).sort_index(ascending=False) if os.path.exists(DB_FILE) else pd.DataFrame())
