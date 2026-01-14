import streamlit as st
import requests
import soundfile as sf
import numpy as np
import io
import uuid

# ==========================================
# 1. ★設定エリア：Secretsから情報を取得
# ==========================================
try:
    FIXED_API_KEY = st.secrets["FISH_AUDIO_API_KEY"]
    DEFAULT_MODEL_ID = st.secrets["FISH_AUDIO_MODEL_ID"]
except Exception:
    FIXED_API_KEY = ""
    DEFAULT_MODEL_ID = "74bd3fcb1f804bf9b2fa5ade3e8e0870"

# ==========================================
# 2. ページ設定 & カスタムデザイン (CSS)
# ==========================================
st.set_page_config(page_title="VOICE GEN PRO", page_icon="🔊", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Noto+Sans+JP:wght@400;700&display=swap');
    
    /* 背景をベージュに変更 */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #f2f0eb !important;
        color: #1a1a1a !important;
        font-family: 'Inter', 'Noto Sans JP', sans-serif !important;
    }
    
    /* ヘッダー部分 */
    .main-title {
        font-weight: 700;
        letter-spacing: -0.02em;
        font-size: 3rem;
        text-align: center;
        margin-top: 50px;
        color: #000000;
    }
    .sub-title {
        text-align: center;
        color: #8c8a84;
        font-size: 0.75rem;
        margin-bottom: 4rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
    }

    /* 入力フィールド・セレクトボックス */
    .stTextArea textarea, .stTextInput input {
        background-color: transparent !important;
        color: #000 !important;
        border: 1px solid #1a1a1a !important;
        border-radius: 0px !important;
        padding: 15px !important;
    }
    
    div[data-baseweb="select"] > div {
        background-color: transparent !important;
        border: 1px solid #1a1a1a !important;
        border-radius: 0px !important;
        color: #000 !important;
    }

    /* ラベル文字 */
    label p {
        color: #1a1a1a !important;
        font-weight: 700 !important;
        letter-spacing: 0.05em;
    }

    /* ボタンデザイン：黒背景に白文字 */
    .stButton > button {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 0px !important;
        padding: 18px !important;
        font-weight: 700 !important;
        letter-spacing: 0.15em;
        width: 100%;
        margin-top: 20px;
        transition: opacity 0.3s;
    }
    .stButton > button:hover {
        background-color: #333333 !important;
        color: #ffffff !important;
        opacity: 0.8;
    }
    
    /* ダウンロードボタン：枠線のみ */
    [data-testid="stDownloadButton"] > button {
        background-color: transparent !important;
        color: #000 !important;
        border: 1px solid #1a1a1a !important;
        border-radius: 0px !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        background-color: #1a1a1a !important;
        color: #fff !important;
    }

    /* オーディオプレイヤー（ベージュに合わせた色調調整） */
    audio {
        width: 100%;
        margin-top: 30px;
    }

    /* 不要な要素の非表示 */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* 区切り線 */
    hr {
        border-top: 1px solid #1a1a1a !important;
    }
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
        return None, "API Key is missing."
        
    url = "https://api.fish.audio/v1/tts"
    headers = {
        "Authorization": f"Bearer {FIXED_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "reference_id": model_id,
        "format": "pcm", 
        "sample_rate": 44100
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        if response.status_code != 200:
            return None, f"Error: {response.status_code}"

        audio_int16 = np.frombuffer(response.content, dtype=np.int16)
        wav_buffer = io.BytesIO()
        sf.write(wav_buffer, audio_int16, 44100, format='WAV', subtype='PCM_16')
        wav_buffer.seek(0)
        return wav_buffer, None
    except Exception as e:
        return None, str(e)

# --- UI構築 ---
st.markdown('<h1 class="main-title">VOICE GEN PRO</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">High-Fidelity Audio Synthesis</p>', unsafe_allow_html=True)

st.markdown("### SETTINGS")
model_id_input = st.text_input("MODEL ID", value=DEFAULT_MODEL_ID)

st.divider()

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

text_input = st.text_area("PROMPT", height=220, placeholder="Enter text to generate audio...")

if st.button("RUN GENERATION"):
    if not text_input:
        st.warning("Please enter some text.")
    else:
        final_prompt = f"{emotion_tag} {text_input}" if emotion_tag else text_input
        
        with st.spinner("Synthesizing..."):
            wav_data, error = generate_audio(final_prompt, model_id_input)
            
            if error:
                st.error(error)
            else:
                st.audio(wav_data, format="audio/wav")
                
                st.download_button(
                    label="DOWNLOAD WAV (44.1kHz)",
                    data=wav_data,
                    file_name=f"export_{uuid.uuid4().hex[:6]}.wav",
                    mime="audio/wav"
                )
