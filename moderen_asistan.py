import streamlit as st
import pandas as pd
from datetime import datetime
import time
import webbrowser
import urllib.parse
import os
from PIL import Image

# --- MODEREN MÜHENDİSLİK | V26 FİNAL - HATASIZ SÜRÜM ---
st.set_page_config(page_title="MODEREN Üretim Portalı", layout="wide", page_icon="🏗️")

# --- AYARLAR ---
LOGO_PATH = "logo.png"
USTA_SIFRE = "moderen38"
DB_FILE = "moderen_aktif_gun.csv"
MESAI_SANIYE = 36900 
MUHENDIS_TEL = "+905511254762"

# --- TASARIM ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .reklam-alani {
        background: linear-gradient(90deg, #161b22 0%, #001d3d 100%);
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        border: 2px solid #58a6ff;
        margin-bottom: 25px;
    }
    .reklam-baslik { color: white; font-size: 50px; font-weight: 900; letter-spacing: 5px; }
    .reklam-slogan { color: #58a6ff; font-size: 20px; font-style: italic; }
    div.stMetric { background-color: #161b22; padding: 20px; border-radius: 15px; border-top: 4px solid #58a6ff; }
    </style>
    """, unsafe_allow_html=True)

# --- YARDIMCI FONKSİYONLAR ---
def format_sure(saniye):
    hrs, rem = divmod(int(saniye), 3600)
    mins, secs = divmod(rem, 60)
    return f"{hrs:02d}:{mins:02d}:{secs:02d}"

def verileri_yukle():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Tarih", "İş Adı", "Sac Cinsi", "İş Süresi", "Arıza Süresi", "Saniye_Is", "Saniye_Ariza", "Yüzde"])

def logo_goster(genislik=200):
    if os.path.exists(LOGO_PATH):
        try:
            img = Image.open(LOGO_PATH)
            st.image(img, width=genislik)
        except: pass

# --- OTURUM VE MAKİNE HAFIZASI ---
if 'auth_role' not in st.session_state: st.session_state.auth_role = None
if 'makine_durumu' not in st.session_state: st.session_state.makine_durumu = "BEKLEMEDE"
if 'is_suresi_sn' not in st.session_state: st.session_state.is_suresi_sn = 0.0
if 'ariza_suresi_sn' not in st.session_state: st.session_state.ariza_suresi_sn = 0.0
if 'son_zaman' not in st.session_state: st.session_state.son_zaman = None
if 'f_is' not in st.session_state: st.session_state.f_is = 0
if 'f_ariza' not in st.session_state: st.session_state.f_ariza = 0

df_aktif = verileri_yukle()

# --- [1] GİRİŞ EKRANI ---
if st.session_state.auth_role is None:
    c_l1, c_l2, c_l3 = st.columns([1, 1, 1])
    with c_l2: logo_goster(350)
    
    st.markdown("""<div class="reklam-alani">
        <div class="reklam-baslik">MODEREN MÜHENDİSLİK</div>
        <div class="reklam-slogan">"Konya'nın Çeliğe Atılan İmzası"</div>
    </div>""", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("👨‍🔧 Usta Paneli")
        sifre = st.text_input("Giriş Kodu", type="password", autocomplete="new-password", key="login_pass")
        if st.button("Sistemi Yönet (Şifreli)", use_container_width=True):
            if sifre == USTA_SIFRE: 
                st.session_state.auth_role = "USTA"
                st.rerun()
            else: st.error("Hatalı Şifre!")
    with c2:
        st.subheader("📊 Mühendis Paneli")
        if st.button("Hattı İzle (Şifresiz)", use_container_width=True):
            st.session_state.auth_role = "MUHENDIS"
            st.rerun()
    st.stop()

# --- [2] USTA PANELİ ---
if st.session_state.auth_role == "USTA":
    with st.sidebar:
        logo_goster(150)
        st.header(f"👷 Eren Usta")
        if st.button("🔴 Çıkış Yap"): 
            st.session_state.auth_role = None
            st.rerun()

    st.title("🕹️ Üretim Komut Merkezi")
    
    m1, m2, m3 = st.columns(3)
    toplam_is_sn = df_aktif['Saniye_Is'].sum() if not df_aktif.empty else 0
    m1.metric("Aktif Lazer Süresi", format_sure(toplam_is_sn))
    m2.metric("Günlük Verim", f"%{(toplam_is_sn/MESAI_SANIYE)*100:.1f}")
    m3.metric("Tamamlanan İş", len(df_aktif))

    st.divider()

    c_sol, c_sag = st.columns([2, 1])
    
    with c_sol:
        st.subheader("📡 Makine Kontrol")
        k1, k2, k3 = st.columns(3)
        
        if k1.button("▶️ KESİMİ BAŞLAT", type="primary", use_container_width=True):
            if st.session_state.makine_durumu != "KESIMDE":
                if st.session_state.makine_durumu == "ARIZADA" and st.session_state.son_zaman:
                    st.session_state.ariza_suresi_sn += time.time() - st.session_state.son_zaman
                st.session_state.son_zaman = time.time()
                st.session_state.makine_durumu = "KESIMDE"
            st.rerun()
            
        if k2.button("⚠️ ARIZA / DURAKLAT", use_container_width=True):
            if st.session_state.makine_durumu == "KESIMDE" and st.session_state.son_zaman:
                st.session_state.is_suresi_sn += time.time() - st.session_state.son_zaman
                st.session_state.son_zaman = time.time()
                st.session_state.makine_durumu = "ARIZADA"
            st.rerun()
            
        if k3.button("⏹️ İŞİ BİTİR", use_container_width=True):
            if st.session_state.makine_durumu == "KESIMDE" and st.session_state.son_zaman:
                st.session_state.is_suresi_sn += time.time() - st.session_state.son_zaman
            elif st.session_state.makine_durumu == "ARIZADA" and st.session_state.son_zaman:
                st.session_state.ariza_suresi_sn += time.time() - st.session_state.son_zaman
            
            st.session_state.f_is = int(st.session_state.is_suresi_sn)
            st.session_state.f_ariza = int(st.session_state.ariza_suresi_sn)
            st.session_state.makine_durumu = "BEKLEMEDE"
            st.session_state.son_zaman = None
            st.session_state.is_suresi_sn = 0.0
            st.session_state.ariza_suresi_sn = 0.0
            st.rerun()

        # CANLI SAYAÇ ALANI
        st.write("---")
        placeholder = st.empty()
        if st.session_state.makine_durumu == "KESIMDE":
            anlik = st.session_state.is_suresi_sn + (time.time() - st.session_state.son_zaman)
            placeholder.success(f"🚀 MAKİNE ÇALIŞIYOR: {format_sure(anlik)}")
            time.sleep(1)
            st.rerun()
        elif st.session_state.makine_durumu == "ARIZADA":
            anlik_ar = st.session_state.ariza_suresi_sn + (time.time() - st.session_state.son_zaman)
            placeholder.warning(f"⚠️ MAKİNE BEKLEMEDE: {format_sure(anlik_ar)}")
            time.sleep(1)
            st.rerun()
        else:
            placeholder.info("⚪ Makine yeni iş emri bekliyor.")

    with c_sag:
        st.subheader("💾 Kayıt Formu")
        is_adi = st.text_input("Proje Adı", key="is_in")
        sac_tipi = st.text_input("Sac Cinsi", key="sac_in")
        if st.button("📥 VERİYE İŞLE", use_container_width=True):
            f_is = st.session_state.get('f_is', 0)
            f_ariza = st.session_state.get('f_ariza', 0)
            if f_is > 0 or f_ariza > 0:
                yeni_veri = {
                    "Tarih": datetime.now().strftime("%d/%m/%Y"), "İş Adı": is_adi, "Sac Cinsi": sac_tipi,
                    "İş Süresi": format_sure(f_is), "Arıza Süresi": format_sure(f_ariza),
                    "Saniye_Is": f_is, "Saniye_Ariza": f_ariza, "Yüzde": f"%{round((f_is / MESAI_SANIYE) * 100, 2)}"
                }
                df_yeni = pd.concat([df_aktif, pd.DataFrame([yeni_veri])], ignore_index=True)
                df_yeni.to_csv(DB_FILE, index=False)
                st.session_state.f_is = 0
                st.session_state.f_ariza = 0
                st.success("Kaydedildi!")
                st.rerun()
            else:
                st.error("Kaydedilecek süre bulunamadı!")

    st.divider()
    st.subheader("📋 Bugünün Üretim Çizelgesi")
    st.dataframe(df_aktif[["İş Adı", "Sac Cinsi", "İş Süresi", "Arıza Süresi", "Yüzde"]], use_container_width=True)

    if st.button("🗑️ TÜM ÇİZELGEYİ SİL VE SIFIRLA"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            st.warning("Veritabanı sıfırlandı!")
            st.rerun()

    if st.button("🚀 GÜN SONU RAPORU GÖNDER"):
        msg = f"🚀 *MODEREN MÜHENDİSLİK GÜNLÜK RAPOR*\n\nEren Usta bugün dükkanı inletti!\n\n📊 *Verim:* %{round((toplam_is_sn/MESAI_SANIYE)*100, 1)}\n⏱️ *Lazer Çalışma:* {format_sure(toplam_is_sn)}\n\n🏗️ *MODEREN MÜHENDİSLİK*"
        webbrowser.open(f"https://wa.me/{MUHENDIS_TEL}?text={urllib.parse.quote(msg)}")

# --- [3] MÜHENDİS PANELİ ---
elif st.session_state.auth_role == "MUHENDIS":
    with st.sidebar:
        logo_goster(150)
        st.header("📊 Mühendis Takip")
        if st.button("🔙 Geri Dön"): 
            st.session_state.auth_role = None
            st.rerun()
            
    st.title("🏗️ Atölye Canlı İzleme Ekranı")
    
    # Hata düzeltmesi: Mühendis tablosuna Arıza Süresi eklendi
    st.subheader("📍 Günlük Üretim Verileri")
    if not df_aktif.empty:
        st.table(df_aktif[["Tarih", "İş Adı", "Sac Cinsi", "İş Süresi", "Arıza Süresi", "Yüzde"]])
    else:
        st.info("Henüz veri girişi yapılmadı.")
        
    if st.session_state.makine_durumu == "KESIMDE":
        st.success("🟢 CANLI: Makine Şu An Aktif Kesim Yapıyor.")
    elif st.session_state.makine_durumu == "ARIZADA":
        st.error("🔴 CANLI: Makine Arıza Sebebiyle Beklemede.")
    
    time.sleep(3)
    st.rerun()
