# ✨ Executive Video Summarizer

An interactive AI-powered web application built with Streamlit that extracts synced transcripts from YouTube videos and generates structured, actionable insights using the Qwen-2.5-3B-Instruct model.

## 🚀 Features
- **Multilingual Support:** Extracts both English and Arabic YouTube transcripts.
- **Dynamic Formatting:** Choose between concise Bullet Points or well-structured Paragraphs.
- **Custom Themes:** Supports elegant Pastel Light Mode and professional Dark Mode.
- **Open-Source LLM:** Powered by `Qwen/Qwen2.5-3B-Instruct` for high-quality reasoning.

## 🛠️ Tech Stack
- **Frontend:** Streamlit
- **Model:** Hugging Face `transformers`, `torch`
- **Data:** `youtube-transcript-api`

## 💻 How to Run Locally
1. Clone the repository.
2. Install the required dependencies: `pip install -r requirements.txt`
3. Run the Streamlit app: `streamlit run app.py`