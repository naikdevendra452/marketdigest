What we’re building (lean MVP)

Frontend: Vite + React + Tailwind (marketing site + signup + preferences + “digest history”).

Backend API: FastAPI (Python).

Database: Firestore (Native mode) → generous free tier, no servers to manage.

Scheduler: Cloud Scheduler (free tier) calls a protected API endpoint at 9:00 PM and 8:00 AM IST.

Aggregation + Summaries: A Python job inside the FastAPI service that pulls a few RSS/official feeds, dedupes, summarizes, stores to Firestore, then dispatches email/WhatsApp.

Email: SendGrid free tier (or AWS SES if you prefer).

WhatsApp: Meta WhatsApp Cloud API (has a free tier for a small number of conversations).

Hosting: Cloud Run (free tier), one container for both API + scheduler endpoint.

Why Firestore (instead of Postgres)? You had dependency pain on macOS + Docker before. Firestore + Cloud Run avoids all that and stays in the free tier.


Project layout
marketdigest/
  frontend/
  backend/
    app/
      main.py
      deps.py
      models.py
      news_job.py
      summarizer.py
      firebase.py
    requirements.txt
    Dockerfile
  .env.example



cmd used:

mkdir -p marketdigest && cd marketdigest
npm create vite@latest frontend -- --template react
cd frontend
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p




mkdir -p backend/app && cd backend
python3 -m venv venv
source venv/bin/activate
touch app/{main.py,deps.py,models.py,news_job.py,summarizer.py,firebase.py}

pip install -r requirements.txt



uvicorn main:app --reload  ==>Backend
http://localhost:8000/signup

npm start dev ==> front end
http://localhost:5173/










