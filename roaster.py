import os
import time
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv

# API keys
load_dotenv()
geminiApiKey = os.getenv("GEMINI_API_KEY")
heygenApiKey = os.getenv("HEYGEN_API_KEY")

# Google Gemini
genai.configure(api_key=geminiApiKey)

class WebScraper:
    @staticmethod
    def getTextFromUrl(targetUrl):
        print(f"Scoping out {targetUrl}...")
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(targetUrl, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            textElements = [p.get_text() for p in soup.find_all('p')]
            fullText = " ".join(textElements)
            
            # Truncate to ~4000 chars 
            return fullText[:4000] 
        except Exception as e:
            return f"Error scraping: {e}"

class ScriptWriter:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-flash-latest')

    def writeScript(self, contentText, selectedMode="roast"):
        print("Analyzing content and writing script...")
        
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
        print("Fetching available avatars...")
        endpoint = "https://api.heygen.com/v2/avatars"
        authHeader = {"X-Api-Key": heygenApiKey}
        
        try:
            response = requests.get(endpoint, headers=authHeader)
            if response.status_code == 200:
                respData = response.json()
                avatarList = respData.get("data", {}).get("avatars", [])
                if avatarList:
                    firstAvatar = avatarList[0]["avatar_id"]
                    print(f"Found Avatar: {firstAvatar}")
                    return firstAvatar
            print("No avatars found. Using fallback ID.")
        except Exception as e:
            print(f"Could not fetch avatars: {e}")
            
        return "Viola_public_58_20240509" 

    @staticmethod
    def generateVideo(scriptContent):
        currentAvatarId = VideoProducer.getAvatarId()
        print("Sending script to HeyGen (this takes a moment)...")
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

        apiResponse = requests.post(endpoint, headers=reqHeaders, json=reqPayload)
        
        if apiResponse.status_code == 200:
            respJson = apiResponse.json()
            if respJson["error"]:
                print(f"HeyGen Error: {respJson['error']}")
                return None
            videoId = respJson["data"]["video_id"]
            return videoId
        else:
            print(f"API Request Failed: {apiResponse.status_code} - {apiResponse.text}")
            return None

    @staticmethod
    def checkStatus(jobId):
        """Polls the API to see if the video is ready."""
        statusUrl = f"https://api.heygen.com/v1/video_status.get?video_id={jobId}"
        authHeaders = {
            "X-Api-Key": heygenApiKey,
            "Content-Type": "application/json"
        }
        
        while True:
            statusResponse = requests.get(statusUrl, headers=authHeaders)
            statusData = statusResponse.json()
            currentStatus = statusData["data"]["status"]
            
            if currentStatus == "completed":
                return statusData["data"]["video_url"]
            elif currentStatus == "failed":
                return "Video generation failed."
            elif currentStatus == "processing" or currentStatus == "pending":
                print("⏳ Rendering... (waiting 5s)")
                time.sleep(5)
            else:
                print(f"Unknown status: {currentStatus}")
                time.sleep(5)

def main():
    print("WELCOME TO THE URL ROASTER ")    
    inputUrl = input("Paste a URL to roast (e.g., a startup homepage or a person name or a celebrity): ")
    modeInput = input("Choose mode: (1) Roast  (2) Hype Man: ")
    selectedMode = "roast" if modeInput == "1" else "hype"
    
    siteScraper = WebScraper()
    scrapedText = siteScraper.getTextFromUrl(inputUrl)
    
    scriptGen = ScriptWriter()
    finalScript = scriptGen.writeScript(scrapedText, selectedMode)
    print(f"\nGenerated {selectedMode.upper()} Script:\n\"{finalScript}\"\n")
    
    userConfirm = input("Generate video with HeyGen? (consumes credits) [y/n]: ")
    
    if userConfirm.lower() == 'y':
        videoMaker = VideoProducer()
        activeVideoId = videoMaker.generateVideo(finalScript)
        
        if activeVideoId:
            finalVideoUrl = videoMaker.checkStatus(activeVideoId)
            print(f"\nDONE! Watch your video here:\n{finalVideoUrl}")
        else:
            print("\nCould not generate video (Check API credits or Key).")
    else:
        print("\nSkipping video generation. Have a nice day!")

if __name__ == "__main__":
    main()