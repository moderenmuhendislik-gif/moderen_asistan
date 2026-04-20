import streamlit as st
import pandas as pd
from datetime import datetime
import time
import os
from PIL import Image

# --- MODEREN MÜHENDİSLİK | V25 ---
st.set_page_config(page_title="MODEREN Üretim Portalı", layout="wide", page_icon="🏗️")

# --- 🎨 PRESTİJ TASARIM VE LOGO STİLİ ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    
    /* Logo Alanı */
    .header-container {
        text-align: center;
        padding: 30px;
        background: linear-gradient(180deg, #161b22 0%, #0d1117 100%);
        border-radius: 0 0 30px 30px;
        border-bottom: 3px solid #58a6ff;
        margin-bottom: 25px;
    }
    
    .logo-text {
        font-size: 50px;
        font-weight: 900;
        color: #ffffff;
        letter-spacing: 4px;
        text-shadow: 0px 0px 15px rgba(88, 166, 255, 0.6);
    }

    /* Giriş Butonları */
    .stButton>button {
        border-radius: 15px;
        font-size: 18px !important;
        font-weight: bold;
        height: 80px !important;
        transition: 0.4s;
    }
    </style>
    """, unsafe_allow_html=True)

# --- AYARLAR ---
USTA_SIFRE = "moderen38"
DB_FILE = "moderen_aktif_gun.csv"
INSTA_LINK = "https://www.instagram.com/moderen_muhendislik"
LOGO_PATH = "logo.png"

if 'sayfa' not in st.session_state: st.session_state.sayfa = "ANA_SAYFA"
if 'auth' not in st.session_state: st.session_state.auth = False

# Fonksiyonlar
def format_sure(saniye):
    hrs, rem = divmod(int(saniye), 3600)
    mins, secs = divmod(rem, 60)
    return f"{hrs:02d}:{mins:02d}:{secs:02d}"

def logo_koy(width=200):
    if os.path.exists(LOGO_PATH):
        try:
            image = Image.open(LOGO_PATH)
            st.image(image, width=width)
        except: pass # Logo açılmazsa hata verme

# --- [1] ANA SAYFA (GİRİŞ EKRANI) ---
if st.session_state.sayfa == "ANA_SAYFA":
    st.markdown("""
        <div class="header-container">
            <div class="logo-text">MODEREN MÜHENDİSLİK</div>
            <div style="color:#58a6ff; font-size:20px;">Lazer Kesim & Hassas Mühendislik</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Giriş ekranında logonun büyük hali
    c_l, c_log, c_r = st.columns([1, 2, 1])
    with c_log:
        logo_koy(width=350)
    
    st.write("<br>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<h3 style='text-align:center;'>👨‍🔧 ÜRETİM HATTI</h3>", unsafe_allow_html=True)
        if st.button("USTA PANELİNE GİRİŞ", use_container_width=True):
            st.session_state.sayfa = "USTA_GIRIS"; st.rerun()
    with c2:
        st.markdown("<h3 style='text-align:center;'>📊 ANALİZ VE TAKİP</h3>", unsafe_allow_html=True)
        if st.button("MÜHENDİS PANELİNE GİRİŞ", use_container_width=True):
            st.session_state.sayfa = "MUHENDIS_PANELI"; st.rerun()

# --- [2] USTA GİRİŞ ---
elif st.session_state.sayfa == "USTA_GIRIS":
    st.title("🔐 Usta Giriş Doğrulama")
    sifre = st.text_input("Şifre", type="password")
    
    col_b1, col_b2 = st.columns(2)
    if col_b1.button("✅ GİRİŞ YAP", use_container_width=True, type="primary"):
        if sifre == USTA_SIFRE:
            st.session_state.auth = True; st.session_state.sayfa = "USTA_PANELI"; st.rerun()
        else: st.error("Hatalı!")
    if col_b2.button("🔙 ANA SAYFAYA DÖN", use_container_width=True):
        st.session_state.sayfa = "ANA_SAYFA"; st.rerun()

# --- [3] USTA PANELİ ---
elif st.session_state.sayfa == "USTA_PANELI" and st.session_state.auth:
    with st.sidebar:
        logo_koy(width=150) # Sidebar'da logo
        st.header("👷 Eren Usta")
        if st.button("🔴 Çıkış"):
            st.session_state.auth = False; st.session_state.sayfa = "ANA_SAYFA"; st.rerun()

    st.title("🕹️ Üretim Komut Merkezi")
    st.info("Sayaçlar ve kayıtlar burada aktif.")

# --- [4] MÜHENDİS PANELİ ---
elif st.session_state.sayfa == "MUHENDIS_PANELI":
    with st.sidebar:
        logo_koy(width=150) # Sidebar'da logo
        st.header("📊 Mühendis")
        if st.button("🔙 Ana Menü"):
            st.session_state.sayfa = "ANA_SAYFA"; st.rerun()

    st.title("🏗️ Mühendislik Takip Ekranı")
    st.success("Tüm üretim verileri burada.")
