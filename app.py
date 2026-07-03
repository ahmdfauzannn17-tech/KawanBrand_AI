import streamlit as st
import google.generativeai as genai
import re
import os
from dotenv import load_dotenv
from PIL import Image

# 1. Konfigurasi Halaman & Tema
st.set_page_config(page_title="BrandAI - SMK Pembangunan", page_icon="🎨", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #FF4B4B; color: white; font-weight: bold; }
    .color-card { padding: 20px; border-radius: 10px; text-align: center; color: white; font-weight: bold; margin-bottom: 10px; border: 2px solid rgba(0,0,0,0.1); }
    .model-info { font-size: 0.8em; color: #666; font-style: italic; }
    </style>
     """, unsafe_allow_html=True)

# 2. Setup API Gemini
load_dotenv()
GENAI_API_KEY = os.getenv("GENAI_API_KEY")
genai.configure(api_key=GENAI_API_KEY)

def extract_colors(text):
    return re.findall(r'#([A-Fa-f0-9]{6})', text)

def check_api_health():
    try:
        genai.list_models()
        return "✅ API Active", "Normal"
    except Exception as e:
        if "429" in str(e):
            return "⚠️ Rate Limit", "Full"
        return "❌ Error", "Disconnected"

# 3. Header
st.title(" 🛍️ KawanBrand Ai")
st.subheader("Solusi Brand Identitas Instan untuk para UMKM")
st.info("Proyek Eksibisi AI - Jurusan Desain Komunikasi Visual SMK Pembangunan Bogor")

# 4. Sidebar Input
with st.sidebar:
    st.image("logo.png.png", width=120)
    st.header("Bangun Identitas Brandmu Sekarang !")
    
    status_label, status_type = check_api_health()
    if status_type == "Normal": st.success(status_label)
    elif status_type == "Full": st.warning(status_label)
    else: st.error(status_label)
    
    nama_brand = st.text_input("Nama Brand", placeholder="Contoh: Cimol Bojot AA")
    sektor = st.selectbox("Sektor Bisnis", ["Kuliner", "Fashion", "Teknologi", "Jasa", "Kesehatan"])
    target_pasar = st.text_input("Target Pasar", placeholder="Contoh: Ibu Rumah Tangga")
    deskripsi = st.text_area("Deskripsi Produk", placeholder="Jelaskan keunikan produk...")
    
    file_gambar = st.file_uploader("Upload Referensi Produk/Moodboard (Opsional)", type=["jpg", "jpeg", "png"])
    if file_gambar:
        st.image(file_gambar, caption="Gambar Referensi", use_container_width=True)
    
    generate_btn = st.button("✨ Bangun Identitas Brand")

# 5. Logika Eksekusi Gemini (Sudah Diperbaiki & Menyimpan Session State)
if generate_btn:
    if nama_brand and deskripsi:
        with st.spinner("Sedang menganalisis teks dan gambar..."):
            # Gunakan model stabil yang tersedia di Gemini API saat ini
            model_options = ['gemini-3.1-pro-preview', 'gemini-3-flash-preview', 'gemini-1.5-flash', 'gemini-pro']
            hasil_teks = None
            model_terpilih = None

            prompt_text = f"""
            Berperanlah sebagai Senior Art Director & Brand Consultant. 
            Buatlah strategi identitas visual lengkap untuk brand:
            Nama: {nama_brand} | Sektor: {sektor} | Target: {target_pasar}
            Deskripsi: {deskripsi}
            
            Jika ada gambar yang dilampirkan, analisis warna, bentuk, dan suasananya agar identitas visual yang dihasilkan selaras dengan gambar tersebut.

            Berikan output dalam format Markdown yang rapi:
            - **Filosofi Merek**: Penjelasan makna nama dan visi.
            - **Konsep Visual Logo**: Deskripsi bentuk dan gaya.
            - **Palet Warna**: Berikan setidaknya 3 kode HEX warna yang dominan (Wajib format #XXXXXX).
            - **Tipografi**: Rekomendasi font (Headline & Body) dan alasannya.
            - **Kesimpulan**: Berikan kesimpulan & alasan mengapa gaya visual yang diberikan itu cocok dengan usaha yang dibangun.
            """

            for model_name in model_options:
                try:
                    model = genai.GenerativeModel(model_name)
                    
                    if file_gambar:
                        img_ref = Image.open(file_gambar)
                        response = model.generate_content([prompt_text, img_ref])
                    else:
                        response = model.generate_content(prompt_text)
                    
                    hasil_teks = response.text
                    model_terpilih = model_name
                    break # Jika berhasil, langsung keluar loop
                except Exception as e:
                    continue
            
            if hasil_teks:
                # Simpan semua data yang dibutuhkan oleh UI ke Session State
                st.session_state['hasil_teks'] = hasil_teks
                st.session_state['brand_name'] = nama_brand
                st.session_state['model_terpilih'] = model_terpilih
            else:
                st.error("Gagal terhubung ke semua model Gemini. Silakan cek API Key Anda.")
    else:
        st.warning("Nama Brand dan Deskripsi wajib diisi!")

# 6. Menampilkan Hasil & Preview Warna (Tanpa DALL-E/OpenAI)
if 'hasil_teks' in st.session_state:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.success(f"Analisis Brand '{st.session_state['brand_name']}' Berhasil!")
        st.markdown(st.session_state['hasil_teks'])
        st.markdown(f"<p class='model-info'>Powered by: {st.session_state['model_terpilih']}</p>", unsafe_allow_html=True)
    
    with col2:
        st.subheader("🎨 Preview Warna")
        colors = extract_colors(st.session_state['hasil_teks'])
        if colors:
            unique_colors = list(dict.fromkeys(colors))
            for color in unique_colors[:4]:
                st.markdown(f"""
                    <div class="color-card" style="background-color: #{color};">
                        #{color.upper()}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Tidak ada kode warna HEX yang terdeteksi dalam teks.")

# 7. Footer
st.markdown("---")
st.caption("© 2026 BrandAI Project | SMK Pembangunan Bogor")