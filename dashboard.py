import streamlit as st
from openai import OpenAI
import set_environmental_variables

audio_value = st.audio_input("Record a voice message")

client = OpenAI()


if audio_value:
    st.audio(audio_value)
    transcript = client.audio.transcriptions.create(
  model="gpt-4o-transcribe",
  file=audio_value
)
    st.write("Transcription:", transcript.text)
# Display the audio input value


