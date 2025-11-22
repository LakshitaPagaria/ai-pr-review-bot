from fastapi import APIRouter, HTTPException
from .db import SessionLocal
from .models import PullRequestReview

router = APIRouter()


@router.get("/reviews/{owner}/{repo}/{pr_number}")
def get_latest_review(owner: str, repo: str, pr_number: int):
    """
    Fetch the latest AI review for a specific pull request.
    Returns summary, details, and GitHub comment URL.
    """
    db = SessionLocal()

    repo_full = f"{owner}/{repo}"

    review = (
        db.query(PullRequestReview)
        .filter(
            PullRequestReview.repo == repo_full,
            PullRequestReview.pr_number == pr_number,
        )
        .order_by(PullRequestReview.created_at.desc())
        .first()
    )

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    return {
        "repo": review.repo,
        "pr_number": review.pr_number,
        "summary": review.summary,
        "details": review.details,
        "comment_url": review.gh_comment_url,
        "created_at": review.created_at,
    }
