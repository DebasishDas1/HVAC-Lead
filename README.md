# HVAC Lead Qualification System

A full-stack application for qualifying HVAC service leads using AI (LangGraph + OpenAI).

## Features
- **Frontend**: React (Vite), TypeScript, TailwindCSS, shadcn/ui.
- **Backend**: Python, FastAPI, LangGraph.
- **AI**: Structured lead qualification using LLM.
- **Mock Integration**: Simulates saving qualified leads to Google Sheets.

## Prerequisites
- Python 3.11+
- Node.js & npm
- [uv](https://github.com/astral-sh/uv) (Python package manager)

## Setup & Running

### 1. Backend
1. Navigate to `backend/`.
2. Install tools (if not already): `pip install uv`
3. Initialize and add dependencies:
   ```bash
   uv init
   uv add fastapi langgraph openai pydantic uvicorn python-dotenv langchain-openai langchain-core uuid
   ```
4. Create a `.env` file based on `.env.example` and add your `OPENAI_API_KEY`.
5. Run the server:
   ```bash
   uv run uvicorn main:app --reload
   ```

### 2. Frontend
1. Navigate to `frontend/`.
2. Initialize and install:
   ```bash
   npm create vite@latest
   npm install
   npx shadcn-ui@latest init
   npm install axios lucide-react uuid clsx tailwind-merge
   ```
   *(Note: These are the commands used to build this project)*
3. Start the dev server:
   ```bash
   npm run dev
   ```

## How it Works
1. User enters name, email, and phone.
2. A unique `sessionId` is generated and stored in `localStorage`.
3. The user chats with an AI assistant specifically trained for HVAC qualification.
4. When the AI determines the user is ready for a service (repair, install, or maintenance), it marks the lead as `qualified`.
5. The system "saves" the lead to a mock service (logs to console) and notifies the user.
