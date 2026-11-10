
# CogniStream
### Developer Flow-State & Cognitive Load Analytics

CogniStream is a data analytics project designed to analyze simulated developer activity and understand focus time, interruptions, context switching, and flow-state sessions.

The project transforms activity-event data into meaningful analytics through Python, FastAPI, ClickHouse, and an interactive React dashboard.

## Project Objectives

- Analyze developer activity patterns.
- Measure focus time and interruptions.
- Identify context-switching behavior.
- Detect long focus sessions.
- Present analytical insights through dashboards.

## Technology Stack

| Area | Technologies |
|---|---|
| Programming | Python |
| Data Processing | Polars, Pandas |
| Database | ClickHouse |
| Backend | FastAPI |
| Frontend | React, Vite |
| Visualization | Recharts |
| Testing | Pytest |
| Version Control | Git, GitHub |

## Key Features

- Developer activity analytics
- Focus vs interruption analysis
- Cognitive load indicators
- Flow-state session analysis
- Context-switching analytics
- REST API endpoints
- Interactive React dashboard
- Automated API testing

## Project Structure

```text
CogniStream/
├── .github/
│   └── workflows/
├── data/
├── frontend/
├── screenshots/
├── scripts/
├── tests/
├── dashboard.py
├── README.md
└── .gitignore
```

## API Endpoints

| Endpoint | Description |
|---|---|
| `/health` | API health check |
| `/developers` | Developer information |
| `/event-summary` | Activity event summary |
| `/activity` | Activity analytics |
| `/cognitive-load` | Cognitive load analytics |
| `/flow-sessions` | Flow-state sessions |
| `/context-switching` | Context-switching analysis |

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/Gajendra-Datacode/CogniStream.git
cd CogniStream
```

### 2. Set up Python environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Start the backend

```bash
python -m uvicorn scripts.api:app --reload
```

Backend:
`http://127.0.0.1:8000`

API documentation:
`http://127.0.0.1:8000/docs`

### 4. Start the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend:
`http://localhost:5173`

## Testing

Run automated tests:

```bash
pytest
```

## Important Note

This project uses simulated developer activity data for analytical and demonstration purposes. Its cognitive-load indicators are analytical proxies, not direct measurements of a person's mental state.

## Author

**Gajendra Sinh Chavada**

GitHub: [Gajendra-Datacode](https://github.com/Gajendra-Datacode)

Project: [CogniStream](https://github.com/Gajendra-Datacode/CogniStream)
