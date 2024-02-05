import streamlit as st
from dotenv import load_dotenv

load_dotenv()  # Load all environment variables
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

prompt = """You are YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here:  """


class VideoPrivate(Exception):
    pass


def extract_transcript_details(youtube_video_url):
    try:
        # Extracting video ID from various YouTube link formats
        video_id = None
        if "youtube.com" in youtube_video_url:
            video_id = youtube_video_url.split("v=")[1].split("&")[0]
        elif "youtu.be" in youtube_video_url:
            video_id = youtube_video_url.split("/")[-1].split("?")[0]

        if video_id:
            transcript_text = YouTubeTranscriptApi.get_transcript(video_id)

            transcript = ""
            for i in transcript_text:
                transcript += " " + i["text"]

            return transcript

    except TranscriptsDisabled as e:
        st.error(f"Transcripts are disabled for this video ({youtube_video_url}). Please enable subtitles for the video.")
        return None
    except Exception as e:
        # If you want to catch VideoPrivate, you can define a custom exception
        if "Video private" in str(e):
            raise VideoPrivate(f"The video ({youtube_video_url}) is private.")
        st.error(f"An error occurred: {e}")
        return None


def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text


st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = None
    if "youtube.com" in youtube_link:
        video_id = youtube_link.split("v=")[1].split("&")[0]
    elif "youtu.be" in youtube_link:
        video_id = youtube_link.split("/")[-1].split("?")[0]

    if video_id:
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Get Detailed Notes"):
    with st.spinner("Getting detailed notes..."):
        transcript_text = extract_transcript_details(youtube_link)
        if transcript_text:
            summary = generate_gemini_content(transcript_text, prompt)
            st.markdown("## Detailed Notes:")
            st.write(summary)


