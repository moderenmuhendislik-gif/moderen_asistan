import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime

# --- GENEL AYARLAR ---
st.set_page_config(page_title="MODEREN MÜHENDİSLİK ERP", layout="wide")
DB_FILE = "moderen_lazer_kayit.csv"
STOK_FILE = "sac_stok_listesi.csv"

# --- ÖZEL ŞİFRELER ---
PASS_USTA_PANELI = "moderen38"
PASS_DEPO = "USTA"
PASS_ANALIZ = "ŞAHİN"

GUNLUK_MESAI_DK = 615

# --- 🎨 ÖZEL TASARIM (CSS) ---
st.markdown("""
    <style>
    /* Ana Arka Plan ve Yazı Tipi */
    .stApp {
        background-color: #f4f7f6;
    }
    
    /* Yan Menü Tasarımı */
    [data-testid="stSidebar"] {
        background-color: #1e272e;
        color: white;
    }
    
    /* Başlık Tasarımı */
    .main-header {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #e74c3c;
        text-align: center;
        padding: 10px;
        border-bottom: 2px solid #e74c3c;
        margin-bottom: 20px;
    }

    /* Buton Tasarımı */
    .stButton>button {
        border-radius: 8px;
        border: none;
        height: 3em;
        background-color: #2f3542;
        color: white;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #e74c3c;
        color: white;
    }

    /* Metrik Kartları */
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #e74c3c;
    }
    </style>
    """, unsafe_allow_html=True)

# --- KATALOG ---
KATALOG = {
    "DKP 1.5mm": ["2000x1000", "2400x1200", "2500x1250", "2700x1500"],
    "DKP 2mm": ["2000x1000", "1800x1250", "2150x1250", "2400x1200", "2500x1250"],
    "DKP 2.5mm": ["2000x1250", "2300x1250", "2500x1250", "3000x1250", "4000x1200"],
    "GLV 1.5mm": ["2000x1000", "2400x1200", "2500x1250"],
    "Krom 2mm": ["2000x1000"],
    "Siyah 3mm": ["3150x1500"],
    "Siyah 4mm": ["6000x1500", "6000x2000"],
    "Siyah 5mm": ["6000x1500", "6000x2000"],
    "Siyah 6mm": ["6000x1500"],
    "Siyah 8mm": ["6000x1500"],
    "Siyah 10mm": ["6000x1500"],
    "Siyah 12mm": ["6000x1500"],
    "Siyah 15mm": ["6000x1500"],
    "Siyah 25mm": ["6000x1500"],
    "Yağ Kazanı 4mm": ["6000x1000"],
    "Yağ Kazanı 5mm": ["6000x1000"]
}

def veritabani_hazirla():
    # Tablodaki "None" hatalarını önleyen temiz kolon yapısı
    hedef_kolonlar = ['Tarih', 'Baslama', 'Bitis', 'Is_Adi', 'Sac_Tipi', 'Olcu', 'Kesim_Suresi', 'Verilen_Sure', 'Fark_Sn', 'Verim_%']
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            if list(df.columns) != hedef_kolonlar:
                pd.DataFrame(columns=hedef_kolonlar).to_csv(DB_FILE, index=False)
        except:
            pd.DataFrame(columns=hedef_kolonlar).to_csv(DB_FILE, index=False)
    else:
        pd.DataFrame(columns=hedef_kolonlar).to_csv(DB_FILE, index=False)

    if not os.path.exists(STOK_FILE):
        stok_verisi = [{"Kategori": k, "Olcu": o, "Adet": 0} for k, v in KATALOG.items() for o in v]
        pd.DataFrame(stok_verisi).to_csv(STOK_FILE, index=False)

def hms_format(saniye):
    saniye = int(saniye)
    saat, kalan = divmod(saniye, 3600)
    dakika, sn = divmod(kalan, 60)
    return f"{saat:02d}:{dakika:02d}:{sn:02d}"

veritabani_hazirla()

if "k_baslangic" not in st.session_state:
    st.session_state.update({"k_baslangic": None, "k_toplam": 0, "a_baslangic": None, "a_toplam": 0, "ilk_start": None, "secilen_tip_index": 0})

# --- REKLAM VE SIDEBAR ---
st.sidebar.markdown("<h1 style='text-align: center; color: #ff4b4b;'>🏗️ MODEREN</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<h3 style='text-align: center; margin-top: -20px; color: #ffffff;'>Mühendislik</h3>", unsafe_allow_html=True)
st.sidebar.markdown("---")

menu = st.sidebar.selectbox("Bölüm Seçiniz:", ["🛠️ Usta Paneli", "📦 Depo Bölümü", "📊 Mühendis Analiz"])

# --- 🛠️ USTA PANELİ ---
if menu == "🛠️ Usta Paneli":
    sifre = st.sidebar.text_input("Usta Paneli Şifresi:", type="password")
    if sifre == PASS_USTA_PANELI:
        st.markdown("<div class='main-header'><h1>🏗️ MODEREN MÜHENDİSLİK</h1></div>", unsafe_allow_html=True)
        st.subheader("🕹️ Üretim Kontrol Merkezi")
        
        c1, c2, c3 = st.columns(3)
        curr_k = st.session_state.k_toplam + (time.time() - st.session_state.k_baslangic if st.session_state.k_baslangic else 0)
        curr_a = st.session_state.a_toplam + (time.time() - st.session_state.a_baslangic if st.session_state.a_baslangic else 0)
        
        c1.metric("⚡ AKTİF KESİM", hms_format(curr_k))
        c2.metric("🚨 ARIZA SÜRESİ", hms_format(curr_a))
        c3.metric("📊 GÜNLÜK VERİM", f"%{round((curr_k/(GUNLUK_MESAI_DK*60)*100),1)}")
        
        st.write("")
        b1, b2, b3, b4 = st.columns(4)
        if st.session_state.k_baslangic is None:
            if b1.button("▶️ KESİMİ BAŞLAT", use_container_width=True):
                if not st.session_state.ilk_start: st.session_state.ilk_start = datetime.now().strftime("%H:%M:%S")
                if st.session_state.a_baslangic: 
                    st.session_state.a_toplam += time.time() - st.session_state.a_baslangic
                    st.session_state.a_baslangic = None
                st.session_state.k_baslangic = time.time(); st.rerun()
        else: b1.warning("⌛ Kesim Devam Ediyor...")

        if b2.button("🚨 ARIZA / DURUŞ", use_container_width=True):
            if st.session_state.k_baslangic: 
                st.session_state.k_toplam += time.time() - st.session_state.k_baslangic
                st.session_state.k_baslangic = None
            if st.session_state.a_baslangic is None: st.session_state.a_baslangic = time.time()
            st.rerun()

        if b3.button("⏹️ VARDİYA BİTİR", use_container_width=True):
            if st.session_state.k_baslangic: st.session_state.k_toplam += time.time() - st.session_state.k_baslangic
            if st.session_state.a_baslangic: st.session_state.a_toplam += time.time() - st.session_state.a_baslangic
            st.session_state.k_baslangic = st.session_state.a_baslangic = None; st.rerun()

        if b4.button("🔄 SAYAÇ SIFIRLA", use_container_width=True):
            st.session_state.update({"k_toplam": 0, "a_toplam": 0, "k_baslangic": None, "a_baslangic": None, "ilk_start": None}); st.rerun()

        st.markdown("<hr style='border: 1px solid #e74c3c;'>", unsafe_allow_html=True)
        st_df = pd.read_csv(STOK_FILE)
        tip_listesi = list(KATALOG.keys())
        col1, col2 = st.columns(2)
        secilen_kat = col1.selectbox("Sac Malzemesi", tip_listesi, index=st.session_state.secilen_tip_index)
        st.session_state.secilen_tip_index = tip_listesi.index(secilen_kat)
        
        olcu_listesi = [f"{o} (Stok: {st_df[(st_df['Kategori']==secilen_kat) & (st_df['Olcu']==o)]['Adet'].values[0]})" for o in KATALOG[secilen_kat]]
        secilen_gosterim = col2.selectbox("Ölçü Seçimi", olcu_listesi)
        temiz_olcu = secilen_gosterim.split(" (")[0]
        
        with st.form("kayit_formu"):
            f_is = st.text_input("Parça İsmi veya İş Numarası")
            st.write("⏱️ **Operatör Hedef Süresi**")
            v1, v2, v3 = st.columns(3)
            vs, vd, vsn = v1.number_input("Saat", 0), v2.number_input("Dakika", 0), v3.number_input("Saniye", 0)

            if st.form_submit_button("🚀 İŞİ KAYDET VE STOKTAN DÜŞ"):
                mevcut = st_df[(st_df['Kategori'] == secilen_kat) & (st_df['Olcu'] == temiz_olcu)]['Adet'].values[0]
                if f_is and st.session_state.ilk_start and mevcut > 0:
                    df = pd.read_csv(DB_FILE)
                    v_toplam_sn = (vs * 3600) + (vd * 60) + vsn
                    kesim_sn = int(st.session_state.k_toplam)
                    yeni_is = {'Tarih': datetime.now().strftime("%d-%m-%Y"), 'Baslama': st.session_state.ilk_start, 'Bitis': datetime.now().strftime("%H:%M:%S"),
                               'Is_Adi': f_is, 'Sac_Tipi': secilen_kat, 'Olcu': temiz_olcu, 'Kesim_Suresi': hms_format(kesim_sn),
                               'Verilen_Sure': f"{vs:02d}:{vd:02d}:{vsn:02d}", 'Fark_Sn': kesim_sn - v_toplam_sn, 'Verim_%': round((kesim_sn/(615*60)*100), 2)}
                    pd.concat([df, pd.DataFrame([yeni_is])], ignore_index=True).to_csv(DB_FILE, index=False)
                    st_df.loc[(st_df['Kategori'] == secilen_kat) & (st_df['Olcu'] == temiz_olcu), 'Adet'] -= 1
                    st_df.to_csv(STOK_FILE, index=False); st.success("Veri Başarıyla İşlendi!"); time.sleep(1); st.rerun()
                else: st.error("HATA: İş adı eksik veya stok yetersiz!")
        if st.session_state.k_baslangic or st.session_state.a_baslangic: time.sleep(1); st.rerun()
    elif sifre != "":
        st.sidebar.error("Geçersiz Şifre!")

# --- 📦 DEPO BÖLÜMÜ ---
elif menu == "📦 Depo Bölümü":
    sifre = st.sidebar.text_input("Depo Şifresi:", type="password")
    if sifre == PASS_DEPO:
        st.markdown("<div class='main-header'><h1>📦 DEPO YÖNETİMİ</h1></div>", unsafe_allow_html=True)
        st_df = pd.read_csv(STOK_FILE)
        with st.container():
            col_a, col_b, col_c = st.columns([2,2,1])
            g_kat = col_a.selectbox("Malzeme Cinsi", list(KATALOG.keys()))
            g_olcu = col_b.selectbox("Boyut", KATALOG[g_kat])
            g_adet = col_c.number_input("Adet", min_value=0, step=1)
            if st.button("📥 STOK GÜNCELLE", use_container_width=True):
                st_df.loc[(st_df['Kategori'] == g_kat) & (st_df['Olcu'] == g_olcu), 'Adet'] = g_adet
                st_df.to_csv(STOK_FILE, index=False); st.success("Stok Başarıyla Güncellendi!")
        st.markdown("### 📊 Mevcut Stok Durumu")
        st.dataframe(st_df, use_container_width=True)
    elif sifre != "":
        st.sidebar.error("Geçersiz Şifre!")

# --- 📊 MÜHENDİS ANALİZ ---
elif menu == "📊 Mühendis Analiz":
    sifre = st.sidebar.text_input("Mühendis Şifresi:", type="password")
    if sifre == PASS_ANALIZ:
        st.markdown("<div class='main-header'><h1>📊 ÜRETİM ANALİZİ</h1></div>", unsafe_allow_html=True)
        if os.path.exists(DB_FILE):
            df = pd.read_csv(DB_FILE)
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)
            if st.button("🧹 TÜM VERİLERİ TEMİZLE VE SİSTEMİ ONAR"):
                # Görüntüdeki karmaşayı çözen tam sıfırlama
                pd.DataFrame(columns=['Tarih', 'Baslama', 'Bitis', 'Is_Adi', 'Sac_Tipi', 'Olcu', 'Kesim_Suresi', 'Verilen_Sure', 'Fark_Sn', 'Verim_%']).to_csv(DB_FILE, index=False)
                st.success("Sistem Fabrika Ayarlarına Döndü!"); st.rerun()
    elif sifre != "":
        st.sidebar.error("Geçersiz Şifre!")
