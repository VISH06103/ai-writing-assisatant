import json
import os
import streamlit as st
from groq import Groq

# Page Setup
st.set_page_config(page_title="AI Grammar & Writing Improver", layout="wide", page_icon="✍️")
st.title("✍️ AI Grammar & Writing Improver")
st.caption("Enhance clarity, correct errors, and tailor your tone effortlessly using Groq.")

# Read GROQ_API_KEY from Streamlit Secrets or Environment Variables
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

if not os.environ.get("GROQ_API_KEY"):
    st.error("⚠️ GROQ_API_KEY environment variable is missing. Add it to your secrets or environment variables.")
    st.stop()

# Initialize Groq client
client = Groq()

# User Inputs Form
with st.form("improver_form"):
    user_text = st.text_area(
        "Paragraph or Essay", 
        height=200, 
        placeholder="Paste your draft here..."
    )
    col1, col2 = st.columns(2)
    with col1:
        tone = st.selectbox("Desired Tone", ["Professional", "Friendly", "Formal", "Casual"])
    with col2:
        level = st.selectbox("Language Level", ["Simple", "Intermediate", "Advanced"])
    
    submitted = st.form_submit_button("Analyze & Improve", use_container_width=True)

# Processing Logic
if submitted:
    if not user_text.strip():
        st.warning("Please enter some text to process.")
    else:
        try:
            prompt = f"""
            You are an expert editor and writing assistant. 
            Analyze the input text and generate a structured JSON output with corrections and enhancements.

            TARGET SPECIFICATIONS:
            - Target Tone: {tone}
            - Target Language Level: {level}

            INPUT TEXT:
            \"\"\"
            {user_text}
            \"\"\"

            Respond ONLY with a JSON object following this exact schema:
            {{
              "corrected_text": "Grammatically fixed version keeping original tone and structure",
              "grammar_mistakes": [
                {{
                  "original": "incorrect phrase or word",
                  "correction": "corrected phrase or word",
                  "explanation": "concise explanation of the grammar rule"
                }}
              ],
              "improved_version": "Rewritten version adapted to {tone} tone and {level} language level",
              "writing_tips": [
                "Tip 1 for future improvement",
                "Tip 2 for future improvement"
              ]
            }}
            """

            with st.spinner("Analyzing text with Groq..."):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a helpful writing assistant that outputs valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                
                data = json.loads(response.choices[0].message.content)

            # Display Results
            st.divider()

            st.subheader("1. Corrected Text")
            st.success(data.get("corrected_text", "No changes needed."))

            st.subheader("2. Grammar Mistakes & Explanations")
            mistakes = data.get("grammar_mistakes", [])
            if mistakes:
                for idx, m in enumerate(mistakes, 1):
                    st.markdown(f"**{idx}.** Original: `{m.get('original')}` ➡️ Fix: `{m.get('correction')}`")
                    st.caption(f"💡 *Rule:* {m.get('explanation')}")
            else:
                st.info("No major grammar or spelling mistakes detected!")

            st.subheader(f"3. Improved Version ({tone} • {level})")
            st.info(data.get("improved_version", ""))

            st.subheader("4. Writing Tips")
            for tip in data.get("writing_tips", []):
                st.markdown(f"- {tip}")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
