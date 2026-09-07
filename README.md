Axion AI is a coaching application for competitive gamers where you connect your Valorant account, review your latest match history and stats, and get coached by an AI coach that actually knows how to play the game - agents, maps, economy, rank specific mistakes, everything. I play a lot of Valorant, and got tired of having to jump back and forth from the stats website to the coaching forum/YouTube, thought I could consolidate the two into one site

It aims to be somewhere between a stat tracker and a coach who watched enough Radiant VODs to give you actual advice rather than “just aim better”.

Google Sign In - a quick landing page, no account creation required

Valorant Tracker retrieves your rank, RR, peak rank, and the last 5 competitive matches (kills/deaths ratio, headshots, agent, map, wins/loses) through the Henrik API

Stat Analyzer receives your kills, deaths, and accuracy, and returns your performance score with targeted feedback 

AI Chat Coach responds to your questions related to Valorant, CS2, and Fortnite strategy as a real coach, not as Wiki

Backend - FastAPI (Python)

Frontend - just HTML, CSS, and JS, no frameworks, keep things simple

AI Chat uses Google Gemini (gemini-2.5-flash)

Match and Rank data comes from Henrik’s unofficial Valorant API

Authentication uses Google Identity Services for sign-in

Deployed on Vercel, Website: https://axion-coach.vercel.app/

For local execution: git clone the repo, cd into it, then pip install -r requirements.txt

Copy .env.example to .env and populate with HENRIK_API_KEY and GEMINI_API_KEY

Execute the backend with uvicorn main:app --reload

Visit frontend/index.html through your web browser, or host it however you wish, all it does is call /api/... at whatever backend is running

You will require your own keys for Henrik and Gemini, both of which have free tiers sufficient for testing


AI usage disclaimer: The primary function of this app involves the use of AI, the coaching chat employs the use of Google's Gemini API, that is the whole purpose of the app. The entire coaching system, prompt creation and output formatting within services/gemini_client.py is all my work, except for the reply generator itself, which is Gemini, and Claude was employed as a coding assistant while creating this app, mainly for debugging a routing problem between my frontend fetch requests and FastAPI routes, and a secondary review of the project before submitting. Architecture, functionality, and the actual code were written by me, AI just helped me find and patch up some bugs along the way. The rest, scoring logic, coaching prompt, UI, API structure, were all created by me

Known limitations:
- Valorant statistics tracker is hardcoded to use the NA region only
- Google sign-in is only cosmetic at the moment, it uses your profile information client-side to display your name and profile picture, no session/account management on backend side at the moment
- Only Valorant can pull stats from the game at the moment, CS2 and Fortnite are chat-coaching only

