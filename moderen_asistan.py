import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime

# --- GENEL AYARLAR ---
st.set_page_config(page_title="MODEREN LAZER ERP V67", layout="wide")
DB_FILE = "moderen_lazer_kayit.csv"
STOK_FILE = "sac_stok_listesi.csv"

# --- YENİ ŞİFRELER ---
SIFRE_USTA = "USTA"
SIFRE_MUHENDIS = "ŞAHİN"

GUNLUK_MESAI_DK = 615

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

st.sidebar.title("🚜 MODEREN LAZER")
menu = st.sidebar.selectbox("Bölüm Seçiniz:", ["🛠️ Usta Paneli", "📦 Depo Bölümü", "📊 Mühendis Analiz"])

# --- 🛠️ USTA PANELİ (USTA ŞİFRELİ) ---
if menu == "🛠️ Usta Paneli":
    if st.sidebar.text_input("Usta Şifresi:", type="password") == SIFRE_USTA:
        st.title("🕹️ Üretim Takip")
        c1, c2, c3 = st.columns(3)
        kesim_p, ariza_p, verim_p = c1.empty(), c2.empty(), c3.empty()
        
        b1, b2, b3, b4 = st.columns(4)
        if st.session_state.k_baslangic is None:
            if b1.button("▶️ BAŞLAT", use_container_width=True):
                if not st.session_state.ilk_start: st.session_state.ilk_start = datetime.now().strftime("%H:%M:%S")
                if st.session_state.a_baslangic: 
                    st.session_state.a_toplam += time.time() - st.session_state.a_baslangic
                    st.session_state.a_baslangic = None
                st.session_state.k_baslangic = time.time(); st.rerun()
        else: b1.info("⌛ Kesim Sürüyor")

        if b2.button("🚨 ARZA", use_container_width=True):
            if st.session_state.k_baslangic: 
                st.session_state.k_toplam += time.time() - st.session_state.k_baslangic
                st.session_state.k_baslangic = None
            if st.session_state.a_baslangic is None: st.session_state.a_baslangic = time.time()
            st.rerun()

        if b3.button("⏹️ BİTİR", use_container_width=True):
            if st.session_state.k_baslangic: st.session_state.k_toplam += time.time() - st.session_state.k_baslangic
            if st.session_state.a_baslangic: st.session_state.a_toplam += time.time() - st.session_state.a_baslangic
            st.session_state.k_baslangic = st.session_state.a_baslangic = None; st.rerun()

        if b4.button("🔄 SIFIRLA", use_container_width=True):
            if st.checkbox("Sıfırlama Onayı"):
                st.session_state.update({"k_toplam": 0, "a_toplam": 0, "k_baslangic": None, "a_baslangic": None, "ilk_start": None}); st.rerun()

        curr_k = st.session_state.k_toplam + (time.time() - st.session_state.k_baslangic if st.session_state.k_baslangic else 0)
        curr_a = st.session_state.a_toplam + (time.time() - st.session_state.a_baslangic if st.session_state.a_baslangic else 0)
        kesim_p.metric("⚡ KESİM", hms_format(curr_k)); ariza_p.metric("🚨 ARZA", hms_format(curr_a))
        verim_p.metric("📊 VERİM", f"%{round((curr_k/(GUNLUK_MESAI_DK*60)*100),1)}")
        
        if st.session_state.k_baslangic or st.session_state.a_baslangic: time.sleep(1); st.rerun()

        st.markdown("---")
        st_df = pd.read_csv(STOK_FILE)
        tip_listesi = list(KATALOG.keys())
        secilen_kat = st.selectbox("Sac Tipi", tip_listesi, index=st.session_state.secilen_tip_index)
        st.session_state.secilen_tip_index = tip_listesi.index(secilen_kat)
        
        olcu_listesi = [f"{o} = {st_df[(st_df['Kategori']==secilen_kat) & (st_df['Olcu']==o)]['Adet'].values[0]} Adet" for o in KATALOG[secilen_kat]]
        secilen_gosterim = st.selectbox("Ölçü ve Stok", olcu_listesi)
        temiz_olcu = secilen_gosterim.split(" = ")[0]
        
        with st.form("kayit_formu"):
            f_is = st.text_input("Parça / İş Adı")
            st.write("⏱️ **Verilen Süre**")
            v1, v2, v3 = st.columns(3)
            vs, vd, vsn = v1.number_input("Saat", 0), v2.number_input("Dk", 0), v3.number_input("Sn", 0)

            if st.form_submit_button("🚀 KAYDET VE STOKTAN DÜŞ"):
                mevcut = st_df[(st_df['Kategori'] == secilen_kat) & (st_df['Olcu'] == temiz_olcu)]['Adet'].values[0]
                if f_is and st.session_state.ilk_start and mevcut > 0:
                    df = pd.read_csv(DB_FILE)
                    v_toplam_sn = (vs * 3600) + (vd * 60) + vsn
                    yeni_is = {'Tarih': datetime.now().strftime("%d-%m-%Y"), 'Baslama': st.session_state.ilk_start, 'Bitis': datetime.now().strftime("%H:%M:%S"),
                               'Is_Adi': f_is, 'Sac_Tipi': secilen_kat, 'Olcu': temiz_olcu, 'Kesim_Suresi': hms_format(st.session_state.k_toplam),
                               'Verilen_Sure': f"{vs:02d}:{vd:02d}:{vsn:02d}", 'Fark_Sn': int(st.session_state.k_toplam) - v_toplam_sn,
                               'Verim_%': round((st.session_state.k_toplam/(615*60)*100), 2)}
                    pd.concat([df, pd.DataFrame([yeni_is])], ignore_index=True).to_csv(DB_FILE, index=False)
                    st_df.loc[(st_df['Kategori'] == secilen_kat) & (st_df['Olcu'] == temiz_olcu), 'Adet'] -= 1
                    st_df.to_csv(STOK_FILE, index=False); st.success("Kayıt Başarılı!"); time.sleep(1); st.rerun()
                else: st.error("Bilgileri kontrol edin veya stok yetersiz!")
    else: st.info("Usta paneline erişmek için şifre giriniz.")

# --- 📦 DEPO BÖLÜMÜ (USTA ŞİFRELİ) ---
elif menu == "📦 Depo Bölümü":
    st.title("📦 Mal Kabul")
    if st.sidebar.text_input("Depo Yetki Şifresi (USTA):", type="password") == SIFRE_USTA:
        st_df = pd.read_csv(STOK_FILE)
        col_a, col_b = st.columns(2)
        g_kat = col_a.selectbox("Gelen Sac Cinsi", list(KATALOG.keys()))
        g_olcu = col_b.selectbox("Ölçü", KATALOG[g_kat])
        g_adet = st.number_input("Depodaki Toplam Adet", min_value=0, step=1)
        if st.button("📥 Stok Sayısını Güncelle", use_container_width=True):
            st_df.loc[(st_df['Kategori'] == g_kat) & (st_df['Olcu'] == g_olcu), 'Adet'] = g_adet
            st_df.to_csv(STOK_FILE, index=False); st.success("Stok güncellendi!")
        st.markdown("---")
        st.dataframe(st_df, use_container_width=True)
    else: st.error("Bu bölüme sadece USTA şifresi ile girilebilir!")

# --- 📊 MÜHENDİS ANALİZ (ŞAHİN ŞİFRELİ) ---
elif menu == "📊 Mühendis Analiz":
    st.title("📊 Üretim Geçmişi (Analiz)")
    if st.sidebar.text_input("Mühendis Şifresi (ŞAHİN):", type="password") == SIFRE_MUHENDIS:
        if os.path.exists(DB_FILE):
            df = pd.read_csv(DB_FILE)
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)
            if st.button("🧹 Tüm Kayıtları Temizle"):
                if st.checkbox("Tüm verileri silmeyi onaylıyorum"):
                    pd.DataFrame(columns=['Tarih', 'Baslama', 'Bitis', 'Is_Adi', 'Sac_Tipi', 'Olcu', 'Kesim_Suresi', 'Verilen_Sure', 'Fark_Sn', 'Verim_%']).to_csv(DB_FILE, index=False)
                    st.rerun()
    else: st.error("Bu bölüme sadece ŞAHİN şifresi ile girilebilir!")
