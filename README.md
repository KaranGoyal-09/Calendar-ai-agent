# 🤖 Calendar AI Agent

Book your Google Calendar appointments via chat using AI!

**Live Demo:** [Streamlit Frontend](https://calendar-frontend-4vfa.onrender.com/)

**Backend API Docs:** [FastAPI Swagger UI](https://calendar-backend-c3xn.onrender.com/docs)

**GitHub Repo:** [KaranGoyal-09/Calendar-ai-agent](https://github.com/KaranGoyal-09/Calendar-ai-agent/tree/main)

---

## 🚀 Features

- Conversational AI agent for booking Google Calendar events
- Natural language understanding powered by Gemini (Google AI)
- Checks calendar availability and creates events
- Modern Streamlit chat UI
- FastAPI backend with documented API endpoints

---

## 🖥️ Live Demo

- **Frontend:** [https://calendar-frontend-4vfa.onrender.com/](https://calendar-frontend-4vfa.onrender.com/)
- **Backend API Docs:** [https://calendar-backend-c3xn.onrender.com/docs](https://calendar-backend-c3xn.onrender.com/docs)

---

## 🗂️ Project Structure

```
calendar-ai-agent/
│
├── agent/                # Conversational agent logic (LLM, extraction, etc.)
├── backend/              # FastAPI backend (API endpoints, calendar utils)
├── streamlit_app.py      # Streamlit frontend
├── requirements.txt      # Python dependencies
├── .gitignore
└── README.md
```

---

## ⚙️ Setup & Deployment

### 1. Clone the Repo

```sh
git clone https://github.com/KaranGoyal-09/Calendar-ai-agent.git
cd Calendar-ai-agent
```

### 2. Install Dependencies

```sh
pip install -r requirements.txt
```

### 3. Environment Variables

Set the following environment variables (on Render or locally):

- `GEMINI_API_KEY` — Your Gemini API key
- `CALENDAR_ID` — Your Google Calendar ID
- (If using a service account file) Add `service_account.json` as a secret file

### 4. Run Locally

**Backend:**
```sh
uvicorn backend.main:app --reload
```

**Frontend:**
```sh
streamlit run streamlit_app.py
```

---

## 🌐 Deployment

Both backend and frontend are deployed on [Render](https://render.com/):

- **Backend:** [https://calendar-backend-c3xn.onrender.com/docs](https://calendar-backend-c3xn.onrender.com/docs)
- **Frontend:** [https://calendar-frontend-4vfa.onrender.com/](https://calendar-frontend-4vfa.onrender.com/)

---

## 📝 Usage

1. Open the [Streamlit frontend](https://calendar-frontend-4vfa.onrender.com/).
2. Chat with the AI to book, check, or ask about calendar events.
3. The bot will extract details, check your Google Calendar, and book events if available.

---

## 🛡️ Security

- **No secrets are committed to GitHub.**
- All API keys and service account files are managed via environment variables and Render's secret files.

---

## 📝 Notes

- **Service Account Setup:**  
  The Google service account JSON is securely managed using Render's Secret Files.  
  The backend expects the file to be named `service_account.json` and located at the project root.

- **Environment Variables:**  
  All sensitive keys (Gemini API, Calendar ID, etc.) are set as environment variables on Render and are not included in the public repo.

- **Frontend/Backend URLs:**  
  The Streamlit frontend is configured to communicate with the deployed backend URL.  
  If you fork or redeploy, update the backend URL in `streamlit_app.py` accordingly.

- **CORS:**  
  The FastAPI backend includes CORS middleware to allow requests from the frontend.

- **Dependencies:**  
  The `requirements.txt` is kept minimal to avoid dependency conflicts.  
  If you add new features, install new packages locally and update `requirements.txt` with `pip freeze > requirements.txt`.

- **Troubleshooting:**  
  If you see errors about missing files or keys, double-check your Render environment variables and secret files.
  If you get a 405 or 404 error, ensure you are POSTing to `/chat` and not to `/docs` or another path.

- **Extending the Project:**  
  You can add more conversational features, support for recurring events, or integrate with other calendar providers.  
  For production, consider adding authentication and HTTPS.

---

## 📄 Project Note

**Overview:**  
This project is a full-stack AI-powered assistant that allows users to book Google Calendar appointments through a conversational chat interface. The system leverages modern Python frameworks and Google's Gemini LLM to provide a seamless, natural language booking experience.

### Key Components & What I Did

1. **Conversational AI Agent (Langchain + Gemini):**
   - Built an agent using Langchain and Gemini (Google's LLM) to extract event details (summary, date, time, description) from user queries.
   - Implemented robust prompt engineering and JSON extraction to ensure reliable parameter parsing from free-form text.

2. **FastAPI Backend:**
   - Developed a FastAPI backend with endpoints for chat and booking.
   - Integrated Google Calendar API using a service account for secure, automated event creation and availability checking.
   - Added CORS middleware for secure frontend-backend communication.
   - Managed all sensitive credentials via environment variables and Render's secret files.

3. **Streamlit Frontend:**
   - Designed a modern, user-friendly chat interface using Streamlit.
   - Implemented real-time chat flow, sending user messages to the backend and displaying AI responses.
   - Configured the frontend to communicate with the deployed backend URL.

4. **Deployment & DevOps:**
   - Containerized and deployed both backend and frontend on Render for public access.
   - Ensured all secrets are excluded from the GitHub repo and managed securely in the cloud.
   - Wrote a clean, minimal `requirements.txt` to avoid dependency conflicts and ensure smooth deployment.

5. **Testing & Debugging:**
   - Thoroughly tested the booking flow, error handling, and edge cases (e.g., missing info, busy slots).
   - Added detailed logging and user feedback for missing or ambiguous input.

### What I Learned / Skills Demonstrated

- Full-stack Python web development (FastAPI, Streamlit)
- LLM prompt engineering and integration (Langchain, Gemini)
- Secure API integration (Google Calendar, service accounts)
- Cloud deployment and environment management (Render)
- Best practices for secrets management and codebase hygiene
- Debugging, error handling, and user experience design

---

## 📄 License

MIT License

---

## 🙏 Acknowledgements

- [Langchain](https://github.com/langchain-ai/langchain)
- [Streamlit](https://streamlit.io/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Google Gemini API](https://ai.google.dev/)

---

**Questions or issues? Open an issue on [GitHub](https://github.com/KaranGoyal-09/Calendar-ai-agent/issues)!** 