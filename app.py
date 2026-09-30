from urllib.parse import parse_qs, urlparse
import streamlit as st
import torch
from transformers import pipeline
from youtube_transcript_api import YouTubeTranscriptApi

# --- 1. Page Configuration ---
st.set_page_config(page_title="Video Summarizer", page_icon="✨", layout="wide")

# --- 2. Dynamic Sidebar Setup ---
with st.sidebar:
  summary_lang = st.selectbox(
      "Language / اللغة",
      ["English", "Arabic (العربية)", "Same as Source"],
      index=0,
  )

  if summary_lang == "Arabic (العربية)":
      st.markdown("### ⚙️ الإعدادات")
      theme_choice = st.radio("الوضع", ["Light Mode", "Dark Mode"], horizontal=True)
      summary_format = st.selectbox("شكل الملخص", ["نقاط (Bullet Points)", "فقرة (Paragraph)"], index=0)
  else:
      st.markdown("### ⚙️ Settings")
      theme_choice = st.radio("Mode", ["Light Mode", "Dark Mode"], horizontal=True)
      summary_format = st.selectbox("Output Format", ["Bullet Points", "Paragraph"], index=0)
      
  max_tokens = st.slider("Max Summary Length", 150, 600, 350, 50)


# --- 3. Bulletproof CSS Injection ---
is_dark = theme_choice == "Dark Mode"

if is_dark:
    # 🔴 NIGHT MODE: Absolute Black & Dark Red
    st.markdown("""
    <style>
        /* إخفاء شريط ستريملت العلوي لمنع تداخل الإعدادات */
        [data-testid="stHeader"] { display: none !important; }
        
        /* الخلفيات: أسود صريح */
        [data-testid="stAppViewContainer"] { background-color: #000000 !important; }
        [data-testid="stSidebar"] { background-color: #0A0000 !important; border-right: 1px solid #4A0000 !important; }
        
        /* ألوان النصوص: أبيض */
        p, label, li, span { color: #EAEAEA !important; }
        
        /* إجبار مربعات الإدخال والقوائم المنسدلة على اللون الأسود والأحمر */
        div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, div[data-baseweb="popover"] > div, ul[data-baseweb="menu"] { 
            background-color: #110000 !important; border: 1px solid #8B0000 !important; 
        }
        div[data-baseweb="input"] input, div[data-baseweb="select"] div, li[data-baseweb="menu-item"] { 
            color: #FFFFFF !important; background-color: transparent !important; 
        }
        
        /* الزرار الأساسي */
        .stButton > button { background: linear-gradient(135deg, #8B0000 0%, #4A0000 100%) !important; color: #FFFFFF !important; border: 1px solid #FF0000 !important; font-weight: bold !important; border-radius: 8px;}
        .stButton > button:hover { opacity: 0.8 !important; }
    </style>
    """, unsafe_allow_html=True)
    
    # العناوين للوضع الداكن
    st.markdown('<h1 style="color: #FF3333; font-weight: 900;">✨ Video Summarizer</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #AA8888; margin-bottom: 2rem;">Extract synced transcripts and generate structured insights.</p>', unsafe_allow_html=True)

else:
    # 🌸 LIGHT MODE: Baby Yellow & Baby Pink
    st.markdown("""
    <style>
        /* إخفاء شريط ستريملت العلوي */
        [data-testid="stHeader"] { display: none !important; }
        
        /* الخلفيات: أصفر هادي ووردي هادي */
        [data-testid="stAppViewContainer"] { background-color: #FFFDF5 !important; }
        [data-testid="stSidebar"] { background-color: #FFF0F5 !important; border-right: 1px solid #FFD1DC !important; }
        
        /* ألوان النصوص: رمادي داكن واضح */
        p, label, li, span { color: #222222 !important; }
        
        /* إجبار مربعات الإدخال والقوائم المنسدلة على اللون الأبيض (علشان نعالج المربع الأسود اللي كان بيظهر) */
        div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, div[data-baseweb="popover"] > div, ul[data-baseweb="menu"] { 
            background-color: #FFFFFF !important; border: 1px solid #FFB6C1 !important; 
        }
        div[data-baseweb="input"] input, div[data-baseweb="select"] div, li[data-baseweb="menu-item"] { 
            color: #222222 !important; background-color: transparent !important; 
        }
        
        /* الزرار الأساسي */
        .stButton > button { background: linear-gradient(135deg, #FFB6C1 0%, #FFF5BA 100%) !important; color: #111111 !important; border: 1px solid #FFB6C1 !important; font-weight: bold !important; border-radius: 8px;}
        .stButton > button:hover { opacity: 0.8 !important; }
    </style>
    """, unsafe_allow_html=True)
    
    # العناوين للوضع الفاتح
    st.markdown('<h1 style="color: #D84B79; font-weight: 900;">✨ Video Summarizer</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #666666; margin-bottom: 2rem;">Extract synced transcripts and generate structured insights.</p>', unsafe_allow_html=True)


# --- 4. Model Loading ---
@st.cache_resource(show_spinner="Initializing Qwen pipeline...")
def load_model():
  return pipeline("text-generation", model="Qwen/Qwen2.5-3B-Instruct", torch_dtype=torch.bfloat16, device_map="auto")

pipe = load_model()


# --- 5. Helper Functions ---
def extract_video_id(url: str) -> str:
  parsed = urlparse(url)
  host = (parsed.hostname or "").lower()
  if host.startswith("www."): host = host[4:]
  if host == "youtu.be":
    video_id = parsed.path.lstrip("/").split("/")[0]
    if video_id: return video_id
  if host in ("youtube.com", "m.youtube.com", "music.youtube.com"):
    qs = parse_qs(parsed.query)
    if qs.get("v"): return qs["v"][0]
    parts = parsed.path.strip("/").split("/")
    if len(parts) >= 2 and parts[0] in ("shorts", "embed", "live", "v"): return parts[1]
  raise ValueError("Invalid YouTube URL.")

def fetch_transcript(video_id: str) -> str:
  api = YouTubeTranscriptApi()
  fetched = api.fetch(video_id, languages=["ar", "en"])
  return "\n".join(snippet.text for snippet in fetched)


# --- 6. Interface Components ---
left_col, right_col = st.columns([1.2, 0.8], gap="medium")

with left_col:
  url_input = st.text_input("YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...")
  run_btn = st.button("Generate Summary", use_container_width=True)

with right_col:
  if url_input.strip():
    try:
      st.video(url_input)
    except Exception:
      st.caption("Provide a valid link to render preview.")

# --- 7. Processing ---
if run_btn:
  if not url_input.strip():
    st.warning("Please enter a valid YouTube link.")
  else:
    with st.status("Processing transcript & generating summary...", expanded=True) as status:
      try:
        vid_id = extract_video_id(url_input)
        text = fetch_transcript(vid_id)
        word_count = len(text.split())
        
        is_bullet = "Bullet Points" in summary_format or "نقاط" in summary_format
        format_en = "concise, executive bullet points" if is_bullet else "a clear, well-structured paragraph"
        format_ar = "نقاط رئيسية واضحة وموجزة" if is_bullet else "فقرة واحدة متصلة وواضحة"

        if summary_lang == "Arabic (العربية)":
          prompt = f"لخص النص التالي المستخرج من الفيديو في {format_ar} باللغة العربية:\n\n{text}"
          system_inst = "أنت مساعد محترف يلخص محتوى الفيديوهات بدقة عالية."
        else:
          prompt = f"Summarize the following video transcript clearly in {format_en}:\n\n{text}"
          system_inst = "You are an executive assistant that produces clean, structured summaries."

        messages = [{"role": "system", "content": system_inst}, {"role": "user", "content": prompt}]
        outputs = pipe(messages, max_new_tokens=max_tokens)
        summary = outputs[0]["generated_text"][-1]["content"]

        status.update(label="Complete", state="complete", expanded=False)

        st.divider()
        res_col1, res_col2 = st.columns([1.6, 1], gap="medium")

        with res_col1:
          st.markdown("### 📌 Summary")
          st.markdown(summary)
          st.download_button("Download Summary (.txt)", data=summary, file_name="video_summary.txt", mime="text/plain")

        with res_col2:
          st.markdown("### 📊 Metrics & Data")
          st.metric("Words Transcribed", f"{word_count:,}")
          with st.expander("View Raw Transcript"):
            st.text_area("Transcript", text, height=280, label_visibility="collapsed")

      except Exception as e:
        status.update(label="Failed", state="error")
        st.error(f"Error: {e}")
