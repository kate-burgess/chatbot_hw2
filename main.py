
import os
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as gen_ai
import time

import pandas as pd #For reading from the spreadsheet

# Load environment variables
load_dotenv()

# Configure Streamlit page settings
st.set_page_config(
    page_title="ChatBot!",
    page_icon=":brain:",  # Favicon emoji
    layout="centered",    # Page layout option
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Set up Google Gemini-Pro AI model
gen_ai.configure(api_key=GOOGLE_API_KEY)

# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 200,
}

model = gen_ai.GenerativeModel(
    model_name="gemini-2.0-flash-lite",
    generation_config=generation_config,
    # safety_settings = Adjust safety settings
    # See https://ai.google.dev/gemini-api/docs/safety-settings
)

# Initialize chat session
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Display the chatbot's title on the page
st.title("💭💭ChatBot")

# Function to translate roles between Gemini-Pro and Streamlit terminology
def translate_role_for_streamlit(user_role):
    if user_role == "model":
        return "assistant"
    else:
        return user_role

# Display the chat history
for message in st.session_state.chat_session.history:
    with st.chat_message(translate_role_for_streamlit(message.role)):
        st.markdown(message.parts[0])


prompt_file = pd.read_csv("mental_health_prompts.csv")
prompt_file = prompt_file.drop_duplicates(subset=["Statement"]) 
prompts = prompt_file.sample(n=10)["Statement"] #acquires 10 unique rows, couldn't do 30 bc of quota 

contexts = [
    "",                         
    "I am an Asian male.",       
    "I am an Asian female.",     
    "I am a White male.",        
    "I am a White female."       
]

results = []
results_df = pd.DataFrame(columns=["Context", "Statement", "Response"])
results_df.to_csv("mental_health_prompts_and_responses.csv", index=False)

for prompt in prompts:
    for context in contexts:
        #needed to add this because there was too long of a response and limiting the number of token only made the bot get cut off mid-sentence
         prompt_1 = f"{prompt}{context}\nPlease give a response under 100 words"
       
        # Add user's message to chat and display it
         st.chat_message("user").markdown(prompt_1)
        # Send user's message to Gemini-Pro and get the response
         gemini_response = st.session_state.chat_session.send_message(prompt_1)
        # Display Gemini-Pro's response
         with st.chat_message("assistant"):
                st.markdown(gemini_response.text)
            
         results.append({
            "Context": context,
            "Statement": prompt,
            "Response" : gemini_response.text
        })
         
         #add immediately to csv file incase crashes because of quota 
         pd.DataFrame([results[-1]]).to_csv("mental_health_prompts_and_responses.csv", mode='a', header=False, index=False)
         time.sleep(2) 

