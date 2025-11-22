from app.db import Base, engine
from app.models import PullRequestReview

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done.")
