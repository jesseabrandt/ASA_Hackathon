#streamlit app for summarizing data
import streamlit as st
import pandas as pd
import datetime



st.title("Smart Summarizer")
selectors = st.container() # container for selectors
summary_space = st.container() # container for summary display

# select date range
date_range = selectors.radio("Select date range for summarization:", 
    ("Today", "Past 7 days", "Past 30 days", "Custom range")
)
if date_range == "Custom range":
    start_date = selectors.date_input("Start date")
    end_date = selectors.date_input("End date")
elif date_range == "Today":
    start_date = datetime.date.today()
    end_date = datetime.date.today()
elif date_range == "Past 7 days":
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=6)
elif date_range == "Past 30 days":
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=29)

# select summarization mode
mode = selectors.segmented_control(
    options = ["Template-based Summarization", "AI Summarization"],
    label = "Select summarization mode",
    selection_mode = "multi",
    default = "Template-based Summarization"
    )
def generate_summary():
    summary_space.write(("SUMMARY!!!! start and end date are type:" + str(type(start_date)))) # placeholder. will need to use session state here
    #numerical_data = pd.read_csv("data/numerical_data.csv")
    #text_data = pd.read_csv("data/text_data.csv")
    # how to store data best?
    #write summary code in separate file. Functions should take start and end date as arguments
selectors.button("Generate Summary", on_click = generate_summary)


