# The URL Roaster

**The URL Roaster** is an AI-powered full-stack application that transforms ordinary (and often boring) webpages into engaging AI-generated video commentaries. Just paste in a URL, pick a personality, and watch an AI avatar either roast it or hype it up like a startup pitch.

Behind the scenes, the app scrapes webpage content, uses a large language model to craft a creative script, and then generates a realistic AI avatar video to deliver the final performance.

---

## Features

- Two Distinct AI Personas  
  💀 Roast Mode — sarcastic, blunt, and brutally honest  
  🎉 Hype Mode — energetic, persuasive, and pitch-deck ready  

- Multi-Agent AI Pipeline  
  Scraper Agent → Creative Writer Agent (Gemini) → Video Producer Agent (HeyGen)

- Dynamic Avatar Handling  
  Automatically fetches available avatars from the HeyGen API, eliminating fragile hard-coded dependencies

- Cost-Aware Design  
  A built-in Safety Switch separates free script generation from paid video rendering to prevent accidental API credit usage

- Clean Streamlit Interface  
  A simple, responsive web dashboard built entirely in Python

---

## Tech Stack

- Frontend: Streamlit (Python)  
- AI Logic: Google Gemini 1.5 Flash (google-generativeai)
- Video Generation: HeyGen API v2  
- Web Scraping: BeautifulSoup4 & Requests  

---

## Setup & Installation

1. Clone the repository  
git clone https://github.com/Anurag7897/url-roaster.git  
cd url-roaster  

2. Create a virtual environment  
python -m venv virtualEnv 

Activate it:  
macOS / Linux → source venv/bin/activate  
Windows → venv\Scripts\activate  

3. Install dependencies  
pip install streamlit requests beautifulsoup4 google-generativeai python-dotenv  

4. Configure environment variables  
Create a .env file in the project root and add:

GEMINI_API_KEY=your_google_gemini_api_key  
HEYGEN_API_KEY=your_heygen_api_key  

---

## Usage

Start the application using:  
python -m streamlit run app.py  

Then:  
1. Open the local URL (typically http://localhost:8501)  
2. Paste any webpage URL  
3. Choose a persona (Roast or Hype)  
4. Generate the script  
5. Render the video once you’re happy with the output  

---

## Project Structure

app.py — Main Streamlit application (UI + backend logic)  
roaster.py — Legacy CLI version for testing logic without the UI  
check_models.py — Utility script for inspecting available Gemini models  
.env — API keys (ignored by Git)  
README.md  

---
