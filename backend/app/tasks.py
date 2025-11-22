import os
import json
from celery import Celery
from .github_client import (
    get_installation_token,
    fetch_pr_files,
    post_pr_comment
)
from .llm import run_llm_review, build_prompt_from_files
from .db import SessionLocal
from .models import PullRequestReview

celery_app = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/1")
)


@celery_app.task(bind=True, max_retries=3)
def process_pr_event_task(self, payload):
    try:
        repo_full = payload["repository"]["full_name"]
        owner, repo_name = repo_full.split("/")
        pr_number = payload["pull_request"]["number"]
        installation_id = payload["installation"]["id"]

        # 1. GitHub App token
        token = get_installation_token(installation_id)

        # 2. Files changed
        files = fetch_pr_files(owner, repo_name, pr_number, token)

        # 3. Create prompt
        prompt = build_prompt_from_files(files, payload)

        # 4. Get LLM response
        llm_output = run_llm_review(prompt)

        # 5. Convert to JSON
        try:
            parsed = json.loads(llm_output)
        except Exception:
            parsed = {
                "summary": llm_output,
                "suggestions": []
            }

        # 6. Convert JSON to markdown
        body_text = format_review_to_markdown(parsed)

        # 7. Post comment to GitHub
        comment = post_pr_comment(owner, repo_name, pr_number, body_text, token)

        # 8. Save review in DB
        db = SessionLocal()
        review = PullRequestReview(
            repo=repo_full,
            pr_number=pr_number,
            summary=parsed.get("summary", ""),
            details=parsed,
            gh_comment_url=comment.get("html_url")
        )
        db.add(review)
        db.commit()

    except Exception as e:
        raise self.retry(exc=e, countdown=30)

    finally:
        try:
            db.close()
        except:
            pass


def format_review_to_markdown(parsed):
    md = []
    md.append("## 🤖 AI Code Review Summary\n")
    md.append(parsed.get("summary", ""))

    suggestions = parsed.get("suggestions", [])

    if suggestions:
        md.append("\n### 📌 Suggestions\n")
        for s in suggestions:
            md.append(
                f"- **{s.get('severity', 'INFO')}** in `{s.get('file', '')}`: {s.get('comment', '')}"
            )
            fix = s.get("fix")
            if fix:
                md.append("\n```diff\n" + fix + "\n```")
    else:
        md.append("\n_No issues found._")

    return "\n".join(md)
