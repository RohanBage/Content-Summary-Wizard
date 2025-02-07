import streamlit as st
import os
os.system("pip install -r requirement.txt")

import validators
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import UnstructuredURLLoader
from youtube_transcript_api import YouTubeTranscriptApi
from langchain.schema import Document

# Streamlit App Configuration
st.set_page_config(
    page_title="✨ Content Summary Wizard",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark mode styling
st.markdown("""
    <style>
        /* Global Dark Theme */
        body {
            color: #E0E0E0;
            background-color: #0E1117;
        }
        
        /* Sidebar */
        .css-1d391kg {
            background-color: #1E1E1E;
        }
        
        /* Cards */
        .card {
            background-color: #1E1E1E;
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid #2D2D2D;
            margin-bottom: 1rem;
        }
        
        /* Instructions Card */
        .instructions-card {
            background-color: #162447;
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid #1E3A8A;
            margin-bottom: 1rem;
        }
        
        /* Success Message */
        .success-message {
            background-color: #064E3B;
            color: #6EE7B7;
            padding: 0.75rem;
            border-radius: 6px;
            margin: 0.5rem 0;
        }
        
        /* Error Message */
        .error-message {
            background-color: #7F1D1D;
            color: #FCA5A5;
            padding: 0.75rem;
            border-radius: 6px;
            margin: 0.5rem 0;
        }
        
        /* Summary Box */
        .summary-box {
            background-color: #1F2937;
            color: #E5E7EB;
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid #374151;
            margin-top: 1rem;
        }
        
        /* Input Field */
        .stTextInput input {
            background-color: #111827;
            color: #E5E7EB;
            border: 1px solid #374151;
        }
        
        /* Button */
        .stButton>button {
            background: linear-gradient(90deg, #10B981 0%, #059669 100%);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
        }
        
        .stButton>button:hover {
            background: linear-gradient(90deg, #059669 0%, #047857 100%);
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: #E5E7EB !important;
        }
        
        /* Links */
        a {
            color: #60A5FA !important;
        }
        
        /* Progress Bar */
        .stProgress > div > div {
            background-color: #10B981;
        }
    </style>
""", unsafe_allow_html=True)

# App Header
st.markdown("""
    <div class="card">
        <h1 class="text-primary" style='text-align: center; font-size: 2.5rem; font-weight: 700;'>
            ✨ Content Summary Wizard
        </h1>
        <p class="text-secondary" style='text-align: center; font-size: 1.2rem; margin-top: 0.5rem;'>
            Transform any content into concise, intelligent summaries powered by AI
        </p>
    </div>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    with st.expander("🔑 API Settings", expanded=True):
        groq_api_key = st.text_input(
            "Groq API Key",
            type="password",
            help="Enter your Groq API key here",
            placeholder="sk-xxxxxxxxxxxxxxxx"
        )
    
    st.markdown("---")
    st.markdown("""
        <div class="card">
            <h3 class="text-primary">✨ Features</h3>
            <ul class="text-secondary">
                <li>🎥 YouTube Video Summarization</li>
                <li>🌐 Website Content Analysis</li>
                <li>🤖 AI-Powered Insights</li>
                <li>⚡ Powered by Llama3</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

# Input Instructions
st.markdown("""
    <div class="info-box">
        <h4 style='margin: 0; color: var(--text-color);'>📝 Usage Instructions</h4>
        <p style='margin: 0.5rem 0; color: var(--secondary-text-color);'>
            <b>For YouTube Videos:</b>
            <ul>
                <li>Only videos with available closed captions/subtitles can be summarized</li>
                <li>Supported languages: English, Spanish, French, German, and more</li>
                <li>Auto-generated YouTube captions are also supported</li>
            </ul>
            <b>For Websites:</b>
            <ul>
                <li>Public websites with readable text content</li>
                <li>News articles, blog posts, and documentation pages work best</li>
            </ul>
        </p>
    </div>
""", unsafe_allow_html=True)


# # Main Content Area with improved layout
# st.markdown("<div style='background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)

col1, col2 = st.columns([5, 1])
with col1:
    generic_url = st.text_input(
        "Enter URL:",
        placeholder="🔗 Paste YouTube video or website URL here...",
        label_visibility="collapsed"
    )
with col2:
    process_button = st.button("🚀 Summarize", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)


# Enhanced Prompt Template
prompt_template = """
As an expert content analyst, provide a comprehensive summary of the following content.
Focus on extracting key insights, crucial details, and main conclusions while maintaining clarity and engagement.

Content: {text}

Please structure your summary as follows:
1. Executive Summary (2-3 sentences)
2. Key Highlights (3-5 bullet points)
3. Detailed Analysis (250-300 words)
4. Key Takeaways (3-4 points)

Use appropriate emojis to enhance readability and engagement.
"""
prompt = PromptTemplate(template=prompt_template, input_variables=["text"])

# Process Button Logic
if process_button:
    if not groq_api_key.strip():
        st.markdown("""
            <div class="error-message">
                ⚠️ Please enter your Groq API key in the sidebar first
            </div>
        """, unsafe_allow_html=True)
    elif not generic_url.strip():
        st.markdown("""
            <div class="error-message">
                ⚠️ Please enter a URL to summarize
            </div>
        """, unsafe_allow_html=True)
    elif not validators.url(generic_url):
        st.markdown("""
            <div class="error-message">
                ❌ Invalid URL format. Please enter a complete URL from your browser's address bar
            </div>
        """, unsafe_allow_html=True)
    else:
        try:
            with st.spinner("🔮 Processing your content..."):
                progress_bar = st.progress(0)
                
                # Initialize ChatGroq
                llm = ChatGroq(model="llama3-8b-8192", groq_api_key=groq_api_key)
                progress_bar.progress(30)

                # Content Loading
                if "youtube.com" in generic_url or "youtu.be" in generic_url:
                    try:
                        # Extract video ID from various YouTube URL formats
                        if "youtu.be" in generic_url:
                            video_id = generic_url.split("youtu.be/")[1].split("?")[0]
                        else:
                            video_id = generic_url.split("v=")[1].split("&")[0]
                            
                        transcript = YouTubeTranscriptApi.get_transcript(video_id)
                        text = " ".join([line['text'] for line in transcript])
                        docs = [Document(page_content=text)]
                        st.markdown("""
                            <div class="success-message">
                                🎥 Successfully loaded YouTube content!
                            </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown(f"""
                            <div class="error-message">
                                ❌ Error loading YouTube video: This video might not have available captions
                            </div>
                        """, unsafe_allow_html=True)
                        st.stop()
                else:
                    try:
                        loader = UnstructuredURLLoader(
                            urls=[generic_url],
                            ssl_verify=False,
                            headers={"User-Agent": "Mozilla/5.0"}
                        )
                        docs = loader.load()
                        st.markdown("""
                            <div class="success-message">
                                🌐 Successfully loaded website content!
                            </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown(f"""
                            <div class="error-message">
                                ❌ Error loading website: Could not access the content
                            </div>
                        """, unsafe_allow_html=True)
                        st.stop()
                
                progress_bar.progress(60)

                # Generate Summary
                chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
                output_summary = chain.run(docs)
                progress_bar.progress(100)

                # Display Result
                st.markdown(f"""
                    <div class="summary-box">
                        <h2>🎉 Summary Generated</h2>
                        <div style='white-space: pre-line;'>
                            {output_summary}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                st.balloons()

        except Exception as e:
            st.markdown(f"""
                <div class="error-message">
                    ⚠️ An error occurred: {str(e)}
                </div>
            """, unsafe_allow_html=True)
            st.stop()