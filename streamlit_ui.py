import streamlit as st
import requests
import time
import os

os.environ["STREAMLIT_WATCH_FILE_SYSTEM"] = "false"

API_BASE = os.getenv("API_BASE")   

st.set_page_config(page_title="Meeting Automator", layout="centered")
st.title("📋 Meeting Automation Assistant")
st.caption("Upload an audio file to transcribe, summarize, and extract action items.")

audio_file = st.file_uploader("Upload your meeting audio", type=["wav"])

if audio_file and st.button("Transcribe + Analyze"):
    with st.spinner("Uploading and transcribing..."):
        # Transcribe
        transcribe_response = requests.post(
            f"{API_BASE}/transcribe",
            files={"file": audio_file}
        )

        if transcribe_response.status_code == 200:
            transcription = transcribe_response.json().get("transcription")
            st.subheader("📝 Transcription")
            st.text_area("Full Transcript", transcription, height=200)

            # Summarize
            with st.spinner("Summarizing..."):
                summary_response = requests.post(
                    f"{API_BASE}/summarize",
                    json={"text": transcription}
                )

            if summary_response.status_code == 200:
                summary = summary_response.json().get("summary")
                st.subheader("✏️ Summary")
                st.text_area("Meeting Summary", summary, height=150)
            else:
                st.error("Failed to summarize.")

            # Action Items
            with st.spinner("Extracting action items..."):
                action_response = requests.post(
                    f"{API_BASE}/action-items",
                    json={"text": transcription}
                )

            if action_response.status_code == 200:
                action_items = action_response.json().get("action_items")
                st.subheader("✅ Action Items")
                for i, item in enumerate(action_items, 1):
                    st.markdown(f"**{i}.** `{item.get('task')}`")
                    if item.get("owner"):
                        st.write(f"- Owner: {item['owner']}")
                    if item.get("due_date"):
                        st.write(f"- Due: {item['due_date']}")
            else:
                st.error("Failed to extract action items.")

        else:
            st.error("Failed to transcribe. Please check your file format.")

