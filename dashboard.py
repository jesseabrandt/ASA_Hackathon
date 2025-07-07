import streamlit as st
from openai import OpenAI
import set_environmental_variables
import pandas as pd
import numpy as np

def new_recording():
    st.session_state.new_recording = True
audio_value = st.audio_input("Record a voice message", on_change= new_recording)

client = OpenAI()
# initialize session state variable new_recording. 
# new_recording must be true to transcribe audio and classify sentences
# Much of this code should probably be moved to a function in a separate file
if "new_recording" not in st.session_state:
    st.session_state.new_recording = True
if "response_list" not in st.session_state:
    st.session_state.response_list = pd.DataFrame(columns = ["sentence", "type"])

if audio_value:
    
    st.audio(audio_value)
    if st.session_state.new_recording:
        st.session_state.transcript = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=audio_value
        )
    st.write("Transcription:", st.session_state.transcript.text)
    sentences = str.split(st.session_state.transcript.text, ".")  # Split the transcription into sentences
    for i, sentence in enumerate(sentences):
        sentences[i] = sentence.strip()
        if(len(sentence) > 0 and sentence[-1] != "."):
            sentences[i] += "."
    
    if st.session_state.new_recording:
        st.session_state.new_recording = False
        st.session_state.response_list = []
        for sentence in sentences:
            if len(sentence )> 0:    
                # st.write(sentence, "is a sentence")
                st.session_state.response = client.responses.create(
                prompt={
                    "id": "pmpt_686ada65dc448190b8e52891791bcad2041f63c0533aad72",
                    "version": "2"
                },
                input = sentence
                )
                # st.write(st.session_state.response.output[0].content[0].text)
                row_data = {
                    "sentence": sentence,
                    "type": st.session_state.response.output[0].content[0].text
                }
                st.session_state.response_list.append(row_data)

# Display the responses in a table (remove later)
response_df = pd.DataFrame(st.session_state.response_list)
st.write(response_df)
# Display the responses in a badge format with toggle buttons for reclassification
col1, col2 = st.columns(2)
toggles = []
for i in range(len(response_df)):
    toggles.append(col2.toggle("Reclassify", key = f"Reclassify_{i}"))
def reclassify_type(toggle, type):
    for i in range(len(toggle)):
        if toggle[i]:
            if type[i] == "Observation":
                type[i] = "Activity"
            elif type[i] == "Activity":
                type[i] = "Observation"
    return type   
            
response_df["reclassify"] = toggles
response_df["type"] = reclassify_type(response_df["reclassify"], response_df["type"])

for i in range(len(response_df)):
    if response_df["type"][i] == "Observation":
        col1.badge(response_df["sentence"][i], color = "blue")
    elif response_df["type"][i] == "Activity":   
        col1.badge(response_df["sentence"][i], color = "green")
    
st.write(response_df)