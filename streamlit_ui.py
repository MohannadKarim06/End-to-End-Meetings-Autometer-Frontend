import streamlit as st
import requests
import os

# Disable file system watcher to prevent inotify errors
os.environ["STREAMLIT_WATCH_FILE_SYSTEM"] = "false"

# Load API base from Streamlit secrets
API_BASE = st.secrets.get("API_BASE")

if not API_BASE:
    st.error("🚨 API endpoint not set. Please configure the `API_BASE` in Streamlit secrets.")
    st.stop()

st.set_page_config(page_title="Meeting Automator", layout="centered")
st.title("📋 Meeting Automation Assistant")
st.caption("Upload an audio file to transcribe, summarize, and extract action items.")

audio_file = st.file_uploader("Upload your meeting audio", type=["wav"])

if audio_file and st.button("Transcribe + Analyze"):
    try:
        with st.spinner("Uploading and transcribing..."):
            transcribe_response = requests.post(
                f"{API_BASE}/transcribe",
                files={"file": audio_file},
                timeout=60
            )

        if transcribe_response.status_code == 200:
            # FIXED: match the misspelled key in FastAPI backend
            transcription = transcribe_response.json().get("transcribtion")

            if not transcription:
                st.error("❌ No transcription was returned from the backend.")
                st.stop()

            st.success("✅ Transcription completed successfully!")

            with st.spinner("Summarizing..."):
                summary_response = requests.post(
                    f"{API_BASE}/summarize",
                    params={"text": transcription},  # FIXED: FastAPI expects raw string, use query param
                    timeout=60
                )

            if summary_response.status_code == 200:
                summary = summary_response.json().get("summary")
                st.subheader("✏️ Summary")
                st.text_area("Meeting Summary", summary, height=150)
            else:
                st.error("❌ Failed to summarize.")

            with st.spinner("Extracting action items..."):
                action_response = requests.post(
                    f"{API_BASE}/action-items",
                    params={"text": transcription},  # FIXED
                    timeout=60
                )

            if action_response.status_code == 200:
                action_items = action_response.json().get("action_items")
                st.subheader("✅ Action Items")
                for i, item in enumerate(action_items, 1):
                    st.markdown(f"**{i}.** `{item.get('task')}`")
                    if item.get("owner"):
                        st.write(f"- Owner: {item['owner']}")
                    if item.get("deadline"):
                        st.write(f"- Deadline: {item['deadline']}")
            else:
                st.error("❌ Failed to extract action items.")
        else:
            st.error("❌ Failed to transcribe. Please check your audio file format.")
    except Exception as e:
        st.error(f"⚠️ Something went wrong: {e}")
        st.stop()
