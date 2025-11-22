from sqlalchemy import Column, Integer, String, JSON, DateTime, func
from .db import Base

class PullRequestReview(Base):
    __tablename__ = "pr_reviews"

    id = Column(Integer, primary_key=True, index=True)
    repo = Column(String, index=True)
    pr_number = Column(Integer)
    summary = Column(String)
    details = Column(JSON)
    gh_comment_url = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
