
import streamlit as st
import google.generativeai as genai
import re
from openai import OpenAI
import time
from PIL import Image
# 1. Konfigurasi Halaman & Tema
st.set_page_config(page_title="BrandAI - SMK Pembangunan", page_icon="🎨", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #FF4B4B; color: white; font-weight: bold; }
    .color-card { padding: 20px; border-radius: 10px; text-align: center; color: white; font-weight: bold; margin-bottom: 10px; border: 2px solid rgba(0,0,0,0.1); }
    .model-info { font-size: 0.8em; color: #666; font-style: italic; }
    .prompt-box { 
        background-color: #ffffff; /* Background putih bersih */
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #FF4B4B; 
        font-family: monospace; 
        font-size: 0.9em; 
        color: #1f2937; /* Warna teks abu-abu gelap kehitaman */
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05); /* Tambah bayangan tipis agar elegan */
        margin-bottom: 10px;
            </style>
     """, unsafe_allow_html=True)

# 2. Setup API
# 2. Setup API
import os
from dotenv import load_dotenv

load_dotenv()  # Ini buat ngambil kunci dari file .env yang kamu buat tadi

GENAI_API_KEY = os.getenv("GENAI_API_KEY")
genai.configure(api_key=GENAI_API_KEY)

# Inisialisasi client OpenAI pakai kunci dari .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
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

# 4. Sidebar
with st.sidebar:
    st.image("logo.png.png", width=120)
    st.header("Bangun Identitas Brandmu Sekarang !")
    
    # Monitor Kuota
    status_label, status_type = check_api_health()
    if status_type == "Normal": st.success(status_label)
    elif status_type == "Full": st.warning(status_label)
    else: st.error(status_label)
    
    nama_brand = st.text_input("Nama Brand", placeholder="Contoh: Cimol Bojot AA")
    sektor = st.selectbox("Sektor Bisnis", ["Kuliner", "Fashion", "Teknologi", "Jasa", "Kesehatan"])
    target_pasar = st.text_input("Target Pasar", placeholder="Contoh: Ibu Rumah Tangga")
    deskripsi = st.text_area("Deskripsi Produk", placeholder="Jelaskan keunikan produk...")
    
    # TOMBOL UPLOAD
    file_gambar = st.file_uploader("Upload Referensi Produk/Moodboard (Opsional)", type=["jpg", "jpeg", "png"])
    if file_gambar:
        st.image(file_gambar, caption="Gambar Referensi", use_container_width=True)
    
    generate_btn = st.button("✨ Bangun Identitas Brand")

# 5. Logika Eksekusi
if generate_btn:
    if nama_brand and deskripsi:
        with st.spinner("Sedang menganalisis teks dan gambar..."):
            model_options = ['gemini-3.1-pro-preview', 'gemini-3-flash-preview', 'gemini-1.5-flash', 'gemini-pro']
            hasil_teks = None
            model_terpilih = None

            for model_name in model_options:
                try:
                    model = genai.GenerativeModel(model_name)
                    
                    # Prompt Dasar
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
                    - **kesimpulan**: berikan kesimpulan & alasan mengapa gaya visual yang diberikan itu cocok dengan usaha yang di bangun 
                    """
                    
                    # LOGIKA MULTIMODAL: Kirim Gambar jika Ada
                    if file_gambar:
                        img = OpenAI.Image.open(file_gambar)
                        response = model.generate_content([prompt_text, img])
                    else:
                        response = model.generate_content(prompt_text)
                        
                    hasil_teks = response.text
                    model_terpilih = model_name
                    
                    st.session_state['hasil_teks'] = hasil_teks
                    st.session_state['model_terpilih'] = model_terpilih
                    st.session_state['brand_name'] = nama_brand
                    st.session_state['desc_fix'] = deskripsi
                    st.session_state['sektor_fix'] = sektor
                    break 
                except Exception:
                    continue
            
            if not hasil_teks:
                st.error("Gagal terhubung ke model AI.")
    else:
        st.warning("Mohon lengkapi Nama Brand dan Deskripsi!")

# 6. Menampilkan Hasil
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
        
        st.markdown("---")
        st.subheader("🖼️ Visual Concept")
        
       # 1. Tombol untuk generate semua prompt sekaligus
        if st.button("🔍 Generate All Brand Assets"):
            with st.spinner("Merancang identitas brand lengkap..."):
                try:
                    img_model = genai.GenerativeModel(st.session_state['model_terpilih'])
                    
                    # Prompt master untuk Gemini agar membuat 4 kategori
                    master_request = f"""
                    Create 4 distinct DALL-E 3 image prompts in English for the brand '{st.session_state['brand_name']}'.
                    Sector: {st.session_state['sektor_fix']}.
                    Description: {st.session_state['desc_fix']}.

                    Format your response strictly as follows:
                    ---LOGO---
                    [Prompt for a minimalist and iconic logo]
                    ---PACKAGING---
                    [Prompt for modern product packaging/pouch]
                    ---PHOTOGRAPHY---
                    [Prompt for high-end commercial product photography with studio lighting]
                    ---IDENTITY---
                    [Prompt for brand identity stationery, like business cards and letterheads]
                    """
                    
                    if file_gambar:
                        img_ref = Image.open(file_gambar)
                        response = img_model.generate_content([master_request, img_ref])
                    else:
                        response = img_model.generate_content(master_request)
                    
                    # Simpan hasil teks ke session state
                    full_text = response.text
                    st.session_state['all_prompts'] = {
                        'Logo': full_text.split('---LOGO---')[1].split('---PACKAGING---')[0].strip(),
                        'Packaging': full_text.split('---PACKAGING---')[1].split('---PHOTOGRAPHY---')[0].strip(),
                        'Photography': full_text.split('---PHOTOGRAPHY---')[1].split('---IDENTITY---')[0].strip(),
                        'Identity': full_text.split('---IDENTITY---')[1].strip()
                    }
                except Exception as e:
                    st.error(f"Gagal merancang: {e}")

        # 2. Menampilkan Hasil dalam Tabs
        if 'all_prompts' in st.session_state:
            tab1, tab2, tab3, tab4 = st.tabs(["🎯 Logo", "📦 Packaging", "📸 Photo", "💳 Identity"])
            
            # Fungsi helper untuk menampilkan konten di setiap tab
            def render_brand_tab(category_name, prompt_text):
                st.markdown(f"**Visual Prompt for {category_name}:**")
                st.markdown(f"<div class='prompt-box'>{prompt_text}</div>", unsafe_allow_html=True)
                
                btn_key = f"btn_{category_name.lower()}"
                img_key = f"img_{category_name.lower()}"
                
                if st.button(f"🎨 Lukis {category_name}", key=btn_key):
                    with st.spinner(f"DALL-E sedang melukis {category_name}..."):
                        try:
                            result = client.images.generate(
                                model="dall-e-3",
                                prompt=prompt_text,
                                n=1, size="1024x1024"
                            )
                            st.session_state[img_key] = result.data[0].url
                        except Exception as e:
                            st.error(f"Gagal: {e}")
                
                if img_key in st.session_state:
                    st.image(st.session_state[img_key], use_container_width=True)

            with tab1: render_brand_tab("Logo", st.session_state['all_prompts']['Logo'])
            with tab2: render_brand_tab("Packaging", st.session_state['all_prompts']['Packaging'])
            with tab3: render_brand_tab("Photography", st.session_state['all_prompts']['Photography'])
            with tab4: render_brand_tab("Identity", st.session_state['all_prompts']['Identity'])
# 7. Footer
st.markdown("---")
st.caption("© 2026 BrandAI Project | SMK Pembangunan Bogor")