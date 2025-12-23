import streamlit as st
import os
import time
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
geminiApiKey = os.getenv("GEMINI_API_KEY")
heygenApiKey = os.getenv("HEYGEN_API_KEY")

genai.configure(api_key=geminiApiKey)

class WebScraper:
    @staticmethod
    def getTextFromUrl(targetUrl):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(targetUrl, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            textElements = [p.get_text() for p in soup.find_all('p')]
            fullText = " ".join(textElements)
            return fullText[:4000]
        except Exception as e:
            return None

class ScriptWriter:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-flash-latest')

    def writeScript(self, contentText, selectedMode="roast"):
        if selectedMode == "roast":
            prompt = (
                "You are a sarcastic, deadpan tech critic. Read the following website text "
                "and write a short script (max 3 sentences) roasting it. "
                "Make fun of the buzzwords. Be funny but safe for work. "
                f"TEXT: {contentText}"
            )
        else:
            prompt = (
                "You are an overly energetic infomercial host. Read the following website text "
                "and write a short script (max 3 sentences) selling this concept like it's the future. "
                "Use exclamation points! "
                f"TEXT: {contentText}"
            )
        aiResponse = self.model.generate_content(prompt)
        return aiResponse.text.strip()

class VideoProducer:
    @staticmethod
    def getAvatarId():
        endpoint = "https://api.heygen.com/v2/avatars"
        authHeader = {"X-Api-Key": heygenApiKey}
        try:
            resp = requests.get(endpoint, headers=authHeader)
            if resp.status_code == 200:
                respData = resp.json()
                avatarList = respData.get("data", {}).get("avatars", [])
                if avatarList:
                    return avatarList[0]["avatar_id"]
        except Exception as e:
            pass
        return "Viola_public_58_20240509"

    @staticmethod
    def generateVideo(scriptContent):
        currentAvatarId = VideoProducer.getAvatarId()
        endpoint = "https://api.heygen.com/v2/video/generate"
        reqHeaders = {
            "X-Api-Key": heygenApiKey,
            "Content-Type": "application/json"
        }
        reqPayload = {
            "video_inputs": [
                {
                    "character": {
                        "type": "avatar",
                        "avatar_id": currentAvatarId,
                        "avatar_style": "normal"
                    },
                    "voice": {
                        "type": "text",
                        "input_text": scriptContent,
                        "voice_id": "1bd001e7e50f421d891986aad5158bc8"
                    }
                }
            ],
            "dimension": { "width": 1280, "height": 720 }
        }
        apiResp = requests.post(endpoint, headers=reqHeaders, json=reqPayload)
        if apiResp.status_code == 200:
            respJson = apiResp.json()
            if respJson["error"]: return None
            return respJson["data"]["video_id"]
        return None

    @staticmethod
    def checkStatus(jobId):
        statusUrl = f"https://api.heygen.com/v1/video_status.get?video_id={jobId}"
        authHead = {"X-Api-Key": heygenApiKey}
        statusDisplay = st.empty() 
        
        while True:
            statusResp = requests.get(statusUrl, headers=authHead)
            statusData = statusResp.json()
            currentStatus = statusData["data"]["status"]
            
            if currentStatus == "completed":
                statusDisplay.text("RENDERING COMPLETE!")
                return statusData["data"]["video_url"]
            elif currentStatus == "failed":
                return None
            
            statusDisplay.text(f"⏳ Status: {currentStatus} (Waiting...)")
            time.sleep(5)

st.set_page_config(page_title="URL Roaster", page_icon="🔥")

st.title("The URL Roaster")
st.markdown("Paste a URL below and let AI roast it (or hype it up).")

inputUrl = st.text_input("Enter Website URL:", placeholder="https://example.com")
selectedPersona = st.radio("Choose Persona:", ["💀 Roast Mode", "🎉 Hype Man Mode"])

if st.button("Generate Script"):
    if not inputUrl:
        st.error("Please enter a URL first!")
    else:
        with st.spinner("🕵️ Scoping out the website..."):
            siteScraper = WebScraper()
            scrapedText = siteScraper.getTextFromUrl(inputUrl)
        
        if scrapedText:
            with st.spinner("Writing the script..."):
                aiWriter = ScriptWriter()
                personaKey = "roast" if "Roast" in selectedPersona else "hype"
                generatedScript = aiWriter.writeScript(scrapedText, personaKey)
            
            st.session_state['script'] = generatedScript
            st.success("Script Generated!")
        else:
            st.error("Could not scrape text from that URL.")

if 'script' in st.session_state:
    st.text_area("AI Script:", st.session_state['script'], height=150)    
    st.markdown("---")
    st.warning("Video generation costs API credits!")
    if st.button("Generate Video with HeyGen"):
        with st.spinner("sending to HeyGen..."):
            videoMaker = VideoProducer()
            submittedVideoId = videoMaker.generateVideo(st.session_state['script'])
            
            if submittedVideoId:
                st.info(f"Job submitted! ID: {submittedVideoId}")
                finalVideoUrl = videoMaker.checkStatus(submittedVideoId)
                
                if finalVideoUrl:
                    st.success("Video is Ready!")
                    st.video(finalVideoUrl)
                else:
                    st.error("Video generation failed.")
            else:
                st.error("Could not start video job. Check API credits.")