# 🤖 AI Pull Request Review Bot

### *Automatic GitHub PR Reviewer powered by OpenAI + FastAPI + Celery + Redis + PostgreSQL*

This project is a fully automated GitHub Pull Request reviewer.
Whenever a PR is opened or updated, the bot performs an AI-driven review and posts a detailed comment directly on GitHub — fully hands-free.

---

## 🚀 Features

✔ Automatically reviews every PR
✔ Detailed summary + code suggestions
✔ Uses GitHub App installation tokens
✔ FastAPI webhook for event handling
✔ Celery worker for async processing
✔ Redis for job queueing
✔ PostgreSQL for storing review logs
✔ 100% Dockerized for easy deployment
✔ Clean and modular backend architecture

---

## 🏗 Architecture Overview

```mermaid
flowchart TD

A[GitHub Pull Request Event] --> B[FastAPI /webhook]
B --> C[Redis Queue]
C --> D[Celery Worker]
D --> E[OpenAI GPT - LLM Review]
E --> F[GitHub PR Comment]
E --> G[PostgreSQL Save Review]
```

---

## 📂 Project Structure

```
/
├── backend/
│   ├── app/
│   │   ├── api.py
│   │   ├── db.py
│   │   ├── github_client.py
│   │   ├── llm.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── tasks.py
│   │   ├── webhook.py
│   ├── create_tables.py
│   ├── requirements.txt
│   ├── Dockerfile
│
├── secrets/
│   └── github_app_private_key.pem
│
├── docker-compose.yml
└── README.md
```

---

## 🔑 Environment Variables

Create a `.env` file **inside `/backend`**:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini

DATABASE_URL=postgresql://postgres:postgres@postgres:5432/postgres
CELERY_BROKER_URL=redis://redis:6379/1

GITHUB_APP_ID=your_github_app_id
GITHUB_PRIVATE_KEY_PATH=/secrets/github_app_private_key.pem
WEBHOOK_SECRET=your_webhook_secret
```

---

## 🐳 Run the Project (Docker)

### 1️⃣ Start all services

```bash
docker compose up --build
```

### 2️⃣ Create database tables

```bash
docker compose exec api python backend/create_tables.py
```

### 3️⃣ Check everything is running

* API → [http://localhost:8000](http://localhost:8000)
* Redis → within container
* PostgreSQL → within container
* Celery Worker → auto-starting

---

## 🔗 GitHub App Setup (IMPORTANT)

### Step 1: Create a GitHub App

**GitHub → Settings → Developer Settings → GitHub Apps → New GitHub App**

Set:

* **Homepage URL:** anything
* **Webhook URL:**

  ```
  http://YOUR-DOMAIN/webhook
  ```
* **Webhook secret:** create a random string → add to `.env`

### Step 2: Permissions

| Permission    | Access       |
| ------------- | ------------ |
| Pull Requests | Read & Write |
| Contents      | Read         |
| Metadata      | Read         |

### Step 3: Generate Private Key

Download → place here:

```
/secrets/github_app_private_key.pem
```

### Step 4: Install the App

Install it on the repository you want to auto-review.

---

## 🔥 How the Workflow Operates

### ✔ 1. PR opened / updated

GitHub sends event → `/webhook`.

### ✔ 2. FastAPI

Validates signature → sends job to Celery.

### ✔ 3. Celery Worker

* Creates GitHub installation token
* Fetches PR changed files
* Builds LLM prompt
* Sends request to OpenAI
* Parses JSON
* Formats GitHub markdown

### ✔ 4. Posts PR Comment

Comments automatically appear on GitHub.

### ✔ 5. Saves Review in PostgreSQL

Useful for dashboards, analytics, history, etc.

---

## 🤖 Expected LLM Output Format

The bot expects JSON but gracefully handles plain text.

```json
{
  "summary": "Overall review summary...",
  "suggestions": [
    {
      "file": "app.py",
      "severity": "MINOR",
      "comment": "Add newline at EOF.",
      "fix": "Add a blank line at the end."
    }
  ]
}
```

---

## 🛠 Common Development Commands

### Rebuild everything

```bash
docker compose down -v
docker compose up --build
```

### View worker logs

```bash
docker compose logs -f worker
```

### View API logs

```bash
docker compose logs -f api
```

### Open PostgreSQL shell

```bash
docker compose exec postgres psql -U postgres
```

---

## 🧪 Test Webhook Locally

```bash
curl -X POST http://localhost:8000/webhook \
     -H "Content-Type: application/json" \
     --data @sample_payload.json
```

---

## 📘 Technologies Used

| Technology         | Purpose            |
| ------------------ | ------------------ |
| **FastAPI**        | Webhook Server     |
| **Celery**         | Async Task Queue   |
| **Redis**          | Celery Broker      |
| **PostgreSQL**     | Review Logging     |
| **OpenAI GPT**     | Code Review Engine |
| **GitHub App API** | Repo Access        |
| **Docker Compose** | Full Orchestration |

---

## 🤝 Contributing

Pull requests are welcome!
If you face issues, feel free to open an issue.

---

## 📄 License

MIT License — free for personal and commercial use.

---

