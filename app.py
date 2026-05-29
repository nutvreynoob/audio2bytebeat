import streamlit as st
import audio2bOG # Your existing script

st.title("Audio to Bytebeat Converter")

# Creates a file uploader on the website
uploaded_file = st.file_uploader("Upload your MP3 file", type=["mp3"])

if uploaded_file is not None:
    st.write("Converting...")
    # Your script processes 'uploaded_file' here
    bytebeat_result = audio2bOG.convert(uploaded_file) 
    st.code(bytebeat_result, language="javascript")
