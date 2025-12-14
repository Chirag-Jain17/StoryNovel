#represents the intent to make a story, gives time for story to get generated
#frontend submits a job, then backend starts doing the job,
#frontend asks if job is done, backend reports its status
#if job is done, backend sends it

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from db.database import Base

class StoryJob(Base):
    __tablename__ = "story_jobs"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, index=True, unique=True)
    session_id = Column(String, index=True)
    theme = Column(String)
    status = Column(String)
    story_id = Column(Integer, nullable=True)
    error = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    completed_at = Column(DateTime(timezone=True), default=func.now(), nullable=True)

