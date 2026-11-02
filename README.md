
# 🧠 CogniStream
### Developer Flow-State & Cognitive Load Analytics

[![CogniStream API Tests](https://github.com/Gajendra-Datacode/CogniStream/actions/workflows/tests.yml/badge.svg)](https://github.com/Gajendra-Datacode/CogniStream/actions/workflows/tests.yml)

CogniStream is a developer activity analytics project designed to analyze coding patterns, focus sessions, interruptions, and context switching using Python-based data processing and interactive dashboards.

## 🎯 Project Objective

The goal of CogniStream is to transform developer activity events into meaningful analytical insights that help understand:

- Developer focus time
- Deep-focus sessions
- Work interruptions
- Context switching patterns
- Cognitive-load indicators
- Developer activity trends

**Note:** This project uses simulated activity data. Its focus and cognitive-load indicators are analytical estimates, not direct measurements of mental workload or actual productivity.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data generation and analytics |
| Polars | Data processing |
| ClickHouse | Analytical database |
| FastAPI | REST API backend |
| Streamlit | Interactive dashboard |
| Plotly | Data visualization |
| Apache Airflow | Workflow orchestration (planned) |
| Pytest | Automated API testing |
| GitHub Actions | Continuous integration |

## ✨ Key Features

- Synthetic developer activity data generation
- Activity data validation
- Developer activity summaries
- Context-switching analysis
- Focus-session analysis
- Deep-focus session detection (90+ minutes)
- Cognitive-load indicator analysis
- REST API endpoints using FastAPI
- Interactive analytics dashboard
- CSV report downloads
- Automated API testing with GitHub Actions

## 🏗️ Project Structure

```text
CogniStream/
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── data/
│   ├── activity_events.csv
│   ├── activity_events.json
│   ├── developer_summary.csv
│   ├── context_switching_summary.csv
│   ├── flow_sessions.csv
│   └── cognitive_load_summary.csv
│
├── scripts/
│   ├── mock_activity_generator.py
│   ├── validate_activity_data.py
│   ├── developer_analytics.py
│   ├── context_switching_analysis.py
│   ├── flow_state_analysis.py
│   ├── cognitive_load_analysis.py
│   └── api.py
│
├── tests/
│   └── test_api.py
│
├── dashboard.py
├── requirements.txt
├── .gitignore
└── README.md
```

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/Gajendra-Datacode/CogniStream.git
cd CogniStream
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Generate activity data

```bash
python scripts/mock_activity_generator.py
```

### 6. Run analytics scripts

```bash
python scripts/developer_analytics.py
python scripts/flow_state_analysis.py
python scripts/cognitive_load_analysis.py
python scripts/context_switching_analysis.py
```

## 🚀 Running the Application

### Start FastAPI

```bash
python -m uvicorn scripts.api:app --reload
```

API URL:

http://127.0.0.1:8000

Interactive API documentation:

http://127.0.0.1:8000/docs

### Start Streamlit Dashboard

Open another terminal and run:

```bash
streamlit run dashboard.py
```

Dashboard URL:

http://localhost:8501

## 🔌 API Endpoints

| Endpoint | Description |
|---|---|
| `/` | API home |
| `/health` | Health check |
| `/developers` | Developer information |
| `/event-summary` | Event summary |
| `/activity` | Activity records |
| `/cognitive-load` | Cognitive-load indicators |
| `/flow-sessions` | Focus-session information |

## 🧪 Automated Testing

Run API tests locally:

```bash
python -m pytest tests/test_api.py -v
```

GitHub Actions automatically runs the API tests when code is pushed to the `main` branch or a pull request targets `main`.

## 📊 Analytical Modules

- **Developer Analytics:** Summarizes developer activity.
- **Context Switching Analysis:** Examines interruptions and activity switching.
- **Flow-State Analysis:** Estimates focus sessions using activity timestamps and a 15-minute event-gap threshold.
- **Cognitive Load Analysis:** Calculates focus and interruption indicators from activity events.

## 🔮 Future Enhancements

- Apache Airflow workflow orchestration
- React-based frontend
- Real-time activity ingestion
- Advanced developer activity analytics
- Additional interactive visualizations
- Expanded automated testing

## 👨‍💻 Author

**Gajendra Sinh Chavada**

GitHub: [Gajendra-Datacode](https://github.com/Gajendra-Datacode)

Project Repository: [CogniStream](https://github.com/Gajendra-Datacode/CogniStream)

---

⭐ If you find this project interesting, consider giving it a star!
