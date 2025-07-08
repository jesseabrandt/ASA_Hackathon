import streamlit as st
from openai import OpenAI
import set_environmental_variables
import pandas as pd
import numpy as np

top = st.container()
def new_recording():
    st.session_state.new_recording = True
audio_value = top.audio_input("Record a voice message", on_change= new_recording)

client = OpenAI()
# initialize session state variable new_recording. 
# new_recording must be true to transcribe audio and classify sentences
# Much of this code should probably be moved to a function in a separate file
if "new_recording" not in st.session_state:
    st.session_state.new_recording = True
if "response_list" not in st.session_state:
    st.session_state.response_list = pd.DataFrame(columns = ["sentence", "type"])

# can be moved to different file possibly
def classify_sentences():
    # Split the transcription into sentences
    sentences = str.split(st.session_state.transcript.text, ".")  # Split the transcription into sentences
    for i, sentence in enumerate(sentences):
        sentences[i] = sentence.strip()
        if(len(sentence) > 0 and sentence[-1] != "."):
            sentences[i] += "."
    
    
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

if audio_value:
    #display audio player
    top.audio(audio_value)
    # Transcribe the audio if a new recording is made
    # TODO: prompt user to save previous transcription
    if st.session_state.new_recording:
        st.session_state.transcript = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=audio_value
        )
    st.session_state.new_recording = False
    st.session_state.transcript.text = top.text_area("Transcription:", st.session_state.transcript.text)
    top.button("Classify", on_click=classify_sentences)
    # should edits trigger reclassification? Or maybe a button to reclassify?
    # either way, some of this should be moved to a function
    


response_df = pd.DataFrame(st.session_state.response_list)
# Display the responses in an editable table (can be deleted later)
#response_df = st.data_editor(response_df)

# Display the responses in a badge format with toggle buttons for reclassification
# (todo: combine with the editable table above)
col1, col2, col3 = st.columns(3) 
toggles = []
for i in range(len(response_df)):
    toggles.append(col3.toggle("Reclassify", key = f"Reclassify_{i}"))
    
#Reclassify sentences based on toggles
def reclassify_type(toggle, type):
    for i in range(len(toggle)):
        if toggle[i]:
            if type[i] == "Observation":
                type[i] = "Activity"
            elif type[i] == "Activity":
                type[i] = "Observation"
            else:
                type[i] = "Observation" #Default to Observation if output is something else
        elif type[i] != "Observation" and type[i] != "Activity":
            type[i] = "Activity" 
    return type   
            
response_df["reclassify"] = toggles
response_df["type"] = reclassify_type(response_df["reclassify"], response_df["type"])

for i in range(len(response_df)):
    if response_df["type"][i] == "Observation":
        col1.badge(response_df["sentence"][i], color = "blue")
        col2.badge(response_df["type"][i], color = "blue")
    elif response_df["type"][i] == "Activity":   
        col1.badge(response_df["sentence"][i], color = "green")
        col2.badge(response_df["type"][i], color = "green")

"output (should be saved to file instead of displayed)"    
st.write(response_df)