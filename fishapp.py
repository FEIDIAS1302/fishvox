import streamlit as st
import requests
import soundfile as sf
import numpy as np
import io
import uuid

# ==========================================
# 1. ページ設定 & カスタムデザイン (CSS)
# ==========================================
st.set_page_config(page_title="Fish Audio High-Res Generator", page_icon="🔊", layout="centered")

# Creative Class風のミニマル・スタイリッシュなデザインを適用
st.markdown("""
<style>
    /* 全体の背景と基本フォント */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #000000 !important;
        color: #f5f5f5 !important;
        font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif !important;
    }
    
    /* ヘッダー・タイトルの装飾 */
    .main-title {
        font-weight: 700;
        letter-spacing: -0.05em;
        font-size: 2.8rem;
        text-align: center;
        margin-bottom: 0;
        color: #ffffff;
    }
    .sub-title {
        text-align: center;
        color: #888;
        font-size: 0.9rem;
        margin-bottom: 3rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    /* サイドバーのカスタマイズ */
    [data-testid="stSidebar"] {
        background-color: #0a0a0a !important;
        border-right: 1px solid #222;
    }

    /* 入力エリアのスタイル */
    .stTextArea textarea {
        background-color: #111 !important;
        color: #fff !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
        padding: 15px !important;
        font-size: 16px !important;
    }
    .stTextArea textarea:focus {
        border-color: #666 !important;
        box-shadow: none !important;
    }

    /* セレクトボックスのスタイル */
    div[data-baseweb="select"] > div {
        background-color: #111 !important;
        border: 1px solid #333 !important;
        color: white !important;
    }

    /* ボタンのスタイル (Creative Class風) */
    .stButton > button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 12px 24px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        transition: all 0.3s ease;
        margin-top: 10px;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #cccccc !important;
        transform: translateY(-2px);
    }

    /* ダウンロードボタンのスタイル */
    [data-testid="stDownloadButton"] > button {
        background-color: transparent !important;
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
        border-radius: 4px !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    /* オーディオプレイヤーの調整 */
    audio {
        filter: invert(100%) hue-rotate(180deg) brightness(1.5); /* プレイヤーをダークモード化 */
        width: 100%;
        margin-top: 20px;
    }

    /* 余計なStreamlit要素を非表示 */
    #MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 感情データの定義
# ==========================================
emotions_data = {
    "基本感情 (Basic)": {
        "楽しい (Happy)": "(happy)", "悲しい (Sad)": "(sad)", "怒り (Angry)": "(angry)",
        "興奮 (Excited)": "(excited)", "穏やか (Calm)": "(calm)", "緊張 (Nervous)": "(nervous)",
        "自信 (Confident)": "(confident)", "驚き (Surprised)": "(surprised)", "満足 (Satisfied)": "(satisfied)",
        "大喜び (Delighted)": "(delighted)", "恐怖 (Scared)": "(scared)", "心配 (Worried)": "(worried)",
        "動揺 (Upset)": "(upset)", "不満 (Frustrated)": "(frustrated)", "落ち込み (Depressed)": "(depressed)",
        "共感 (Empathetic)": "(empathetic)", "恥 (Embarrassed)": "(embarrassed)", "嫌悪 (Disgusted)": "(disgusted)",
        "感動 (Moved)": "(moved)", "誇り (Proud)": "(proud)", "リラックス (Relaxed)": "(relaxed)",
        "感謝 (Grateful)": "(grateful)", "好奇心 (Curious)": "(curious)", "皮肉 (Sarcastic)": "(sarcastic)"
    },
    "応用感情 (Advanced)": {
        "軽蔑 (Disdainful)": "(disdainful)", "不幸 (Unhappy)": "(unhappy)", "不安 (Anxious)": "(anxious)",
        "ヒステリック (Hysterical)": "(hysterical)", "無関心 (Indifferent)": "(indifferent)", "不確実 (Uncertain)": "(uncertain)",
        "疑念 (Doubtful)": "(doubtful)", "混乱 (Confused)": "(confused)", "失望 (Disappointed)": "(disappointed)",
        "後悔 (Regretful)": "(regretful)", "罪悪感 (Guilty)": "(guilty)", "恥 (Ashamed)": "(ashamed)",
        "嫉妬 (Jealous)": "(jealous)", "羨望 (Envious)": "(envious)", "希望 (Hopeful)": "(hopeful)",
        "楽観的 (Optimistic)": "(optimistic)", "悲観的 (Pessimistic)": "(pessimistic)", "ノスタルジック (Nostalgic)": "(nostalgic)",
        "孤独 (Lonely)": "(lonely)", "退屈 (Bored)": "(bored)", "侮蔑 (Contemptuous)": "(contemptuous)",
        "同情 (Sympathetic)": "(sympathetic)", "慈悲 (Compassionate)": "(compassionate)", "決意 (Determined)": "(determined)",
        "諦め (Resigned)": "(resigned)"
    },
    "トーン (Tone)": {
        "急ぎ (Hurried)": "(in a hurry tone)", "叫び (Shouting)": "(shouting)", "悲鳴 (Screaming)": "(screaming)",
        "ささやき (Whispering)": "(whispering)", "優しい (Soft)": "(soft tone)"
    },
    "効果音 (Effects)": {
        "笑い (Laughing)": "(laughing)", "くすくす (Chuckling)": "(chuckling)", "すすり泣き (Sobbing)": "(sobbing)",
        "号泣 (Crying Loudly)": "(crying loudly)", "ため息 (Sighing)": "(sighing)", "うめき (Groaning)": "(groaning)",
        "息切れ (Panting)": "(panting)", "あえぎ (Gasping)": "(gasping)", "あくび (Yawning)": "(yawning)",
        "いびき (Snoring)": "(snoring)"
    }
}

# ==========================================
# 3. APIロジック (48000Hz仕様)
# ==========================================
def generate_wav_48k(text, reference_id, api_key):
    url = "https://api.fish.audio/v1/tts"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 48000HzのPCMを指定
    payload = {
        "text": text,
        "reference_id": reference_id,
        "format": "pcm", 
        "sample_rate": 48000
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        if response.status_code != 200:
            return None, f"Error {response.status_code}: {response.text}"

        raw_data = response.content
        audio_int16 = np.frombuffer(raw_data, dtype=np.int16)
        
        # WAVファイル作成も48000Hzで実行
        wav_buffer = io.BytesIO()
        sf.write(wav_buffer, audio_int16, 48000, format='WAV', subtype='PCM_16')
        wav_buffer.seek(0)
        
        return wav_buffer, None
    except Exception as e:
        return None, str(e)

# ==========================================
# 4. UIの描画
# ==========================================

# タイトル
st.markdown('<h1 class="main-title">VOICE GEN</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">High-Resolution Voice synthesis</p>', unsafe_allow_html=True)

# サイドバー設定
with st.sidebar:
    st.markdown("### CONFIGURATION")
    api_key = st.text_input("API KEY", value=st.secrets.get("FISH_AUDIO_API_KEY", ""), type="password")
    model_id = st.text_input("MODEL ID", value=st.secrets.get("FISH_AUDIO_MODEL_ID", ""))
    st.markdown("---")
    st.caption("Output: WAV (48,000Hz / 16-bit)")

# メインコンテンツレイアウト
col_cat, col_det = st.columns(2)

with col_cat:
    category_options = ["指定なし"] + list(emotions_data.keys())
    selected_category = st.selectbox("CATEGORY", category_options)

with col_det:
    if selected_category == "指定なし":
        emotion_tag = ""
        st.selectbox("DETAIL", ["DEFAULT"], disabled=True)
    else:
        current_options = emotions_data[selected_category]
        selected_emotion_label = st.selectbox("DETAIL", options=list(current_options.keys()))
        emotion_tag = current_options[selected_emotion_label]

# テキスト入力
text_input = st.text_area("TEXT PROMPT", height=180, placeholder="Enter text to synthesize...")

# 生成・結果エリア
if st.button("GENERATE VOICE"):
    if not api_key or not model_id:
        st.error("API Key and Model ID are required.")
    elif not text_input:
        st.warning("Please enter some text.")
    else:
        final_text = f"{emotion_tag} {text_input}" if emotion_tag else text_input
        
        with st.spinner("Synthesizing..."):
            wav_data, error = generate_wav_48k(final_text, model_id, api_key)
            
            if error:
                st.error(f"Failed: {error}")
            else:
                # 生成成功時の表示
                st.audio(wav_data, format="audio/wav")
                
                filename = f"audio_48k_{uuid.uuid4().hex[:6]}.wav"
                st.download_button(
                    label="Download WAV (48kHz)",
                    data=wav_data,
                    file_name=filename,
                    mime="audio/wav"
                )