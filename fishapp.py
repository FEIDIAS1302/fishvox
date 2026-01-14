import streamlit as st
import requests
import soundfile as sf
import numpy as np
import io
import uuid

# ==========================================
# 1. ★設定エリア：Secretsから情報を取得
# ==========================================
# Streamlit Cloudの管理画面で設定した値を取得します
try:
    FIXED_API_KEY = st.secrets["FISH_AUDIO_API_KEY"]
    DEFAULT_MODEL_ID = st.secrets["FISH_AUDIO_MODEL_ID"]


# ==========================================
# 2. ページ設定 & カスタムデザイン (CSS)
# ==========================================
st.set_page_config(page_title="VOICE GEN PRO", page_icon="🔊", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #000000 !important;
        color: #f5f5f5 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .main-title {
        font-weight: 700;
        letter-spacing: -0.05em;
        font-size: 3rem;
        text-align: center;
        margin-top: 50px;
        color: #ffffff;
    }
    .sub-title {
        text-align: center;
        color: #666;
        font-size: 0.8rem;
        margin-bottom: 4rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
    }

    .stTextArea textarea, .stTextInput input {
        background-color: #000 !important;
        color: #fff !important;
        border: 1px solid #222 !important;
        border-radius: 0px !important;
        padding: 15px !important;
    }
    
    div[data-baseweb="select"] > div {
        background-color: #000 !important;
        border: 1px solid #222 !important;
        border-radius: 0px !important;
    }

    .stButton > button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 0px !important;
        padding: 15px !important;
        font-weight: 700 !important;
        letter-spacing: 0.1em;
        width: 100%;
        margin-top: 20px;
    }
    
    [data-testid="stDownloadButton"] > button {
        background-color: transparent !important;
        color: #fff !important;
        border: 1px solid #333 !important;
        border-radius: 0px !important;
    }

    audio {
        filter: invert(100%) hue-rotate(180deg) brightness(1.5);
        width: 100%;
        margin-top: 30px;
    }

    #MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 感情データの定義 ---
emotions_data = {
    "基本感情 (Basic)": {
        "楽しい (Happy)": "(happy)", "悲しい (Sad)": "(sad)", "怒り (Angry)": "(angry)",
        "興奮 (Excited)": "(excited)", "穏やか (Calm)": "(calm)", "驚き (Surprised)": "(surprised)",
        "恐怖 (Scared)": "(scared)", "共感 (Empathetic)": "(empathetic)", "リラックス (Relaxed)": "(relaxed)"
    },
    "応用感情 (Advanced)": {
        "不安 (Anxious)": "(anxious)", "無関心 (Indifferent)": "(indifferent)", "混乱 (Confused)": "(confused)",
        "失望 (Disappointed)": "(disappointed)", "希望 (Hopeful)": "(hopeful)", "決意 (Determined)": "(determined)"
    },
    "トーン (Tone)": {
        "急ぎ (Hurried)": "(in a hurry tone)", "叫び (Shouting)": "(shouting)", 
        "ささやき (Whispering)": "(whispering)", "優しい (Soft)": "(soft tone)"
    },
    "効果音 (Effects)": {
        "笑い (Laughing)": "(laughing)", "ため息 (Sighing)": "(sighing)", 
        "息切れ (Panting)": "(panting)", "あくび (Yawning)": "(yawning)"
    }
}

# --- API処理 (48000Hz) ---
def generate_audio(text, model_id):
    if not FIXED_API_KEY:
        return None, "API Key is not set in Secrets."
        
    url = "https://api.fish.audio/v1/tts"
    headers = {
        "Authorization": f"Bearer {FIXED_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "reference_id": model_id,
        "format": "pcm", 
        "sample_rate": 48000
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        if response.status_code != 200:
            return None, f"Error: {response.status_code}"

        audio_int16 = np.frombuffer(response.content, dtype=np.int16)
        wav_buffer = io.BytesIO()
        sf.write(wav_buffer, audio_int16, 48000, format='WAV', subtype='PCM_16')
        wav_buffer.seek(0)
        return wav_buffer, None
    except Exception as e:
        return None, str(e)

# --- UI構築 ---
st.markdown('<h1 class="main-title">VOICE GEN PRO</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">48kHz / High-Fidelity Export</p>', unsafe_allow_html=True)

st.markdown("### SETTINGS")
model_id_input = st.text_input("MODEL ID", value=DEFAULT_MODEL_ID)

st.markdown("---")

col_cat, col_det = st.columns(2)
with col_cat:
    selected_category = st.selectbox("CATEGORY", ["指定なし"] + list(emotions_data.keys()))

with col_det:
    if selected_category == "指定なし":
        emotion_tag = ""
        st.selectbox("DETAIL", ["DEFAULT"], disabled=True)
    else:
        current_options = emotions_data[selected_category]
        selected_label = st.selectbox("DETAIL", list(current_options.keys()))
        emotion_tag = current_options[selected_label]

text_input = st.text_area("PROMPT", height=200, placeholder="Enter text here...")

if st.button("RUN SYNTHESIS"):
    if not text_input:
        st.warning("Please enter some text.")
    else:
        final_prompt = f"{emotion_tag} {text_input}" if emotion_tag else text_input
        
        with st.spinner("Processing..."):
            wav_data, error = generate_audio(final_prompt, model_id_input)
            
            if error:
                st.error(error)
            else:
                st.audio(wav_data, format="audio/wav")
                
                st.download_button(
                    label="DOWNLOAD WAV (48kHz)",
                    data=wav_data,
                    file_name=f"export_{uuid.uuid4().hex[:6]}.wav",
                    mime="audio/wav"
                )