#writing the endpoints where frontend is connected to backend

import uuid
from http.client import HTTPException
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Cookie, Response, BackgroundTasks
from sqlalchemy.orm import Session
from db.database import get_db, SessionLocal
from models.story import Story, StoryNode
from models.job import StoryJob
from schemas.story import (
    CompleteStoryNodeResponse, CompleteStoryNodeResponse, CreateStoryRequest, CompleteStoryResponse
)
from schemas.job import StoryJobResponse

#allows to make different endpoints in different files
router = APIRouter(
    prefix="/stories",
    tags=["stories"],
)
#because of this, the path to reach any backend api is: backendURL/API/stories/endpoint(whatever it is)

def get_session_id(session_id: Optional[str] = Cookie(None)): #checks if session id exists or not for pre-loading
    if session_id is None:
        session_id = str(uuid.uuid4())
    return session_id


@router.post("/create", response_model=StoryJobResponse) #do this whenever creating something new
def create_story(
        request: CreateStoryRequest,
        background_tasks: BackgroundTasks,
        response: Response,
        session_id: str = Depends(get_session_id),
        db: Session = Depends(get_db)        #depends() help in accessing any function so that values can be initialized
):
    response.set_cookie(key="session_id", value=session_id, httponly=True) #actually store the session id for future use

    job_id = str(uuid.uuid4())  #creating the job which will send the request to the LLM for story genreration
    job = StoryJob(
        job_id=job_id,
        session_id=session_id,
        theme=request.theme,
        status="pending"
    )
    db.add(job)
    db.commit()    #adding and saving the job in the database

    background_tasks.add_task( #call the function to get the background tasks running
        generate_story_task,
        job_id=job_id,
        theme=request.theme,
        session_id=session_id
    )
    return job

def generate_story_task(job_id:str, theme:str, session_id:str):
    db = SessionLocal() #creating a new db session to prevent hanging when multiple users are waiting on the LLM,to keep it asynchronous

    try:
        job = db.query(StoryJob).filter(StoryJob.job_id == job_id).first() #query to find job_id in the databse
        if not job:
            return

        try:
            job.status = "processing"
            db.commit()

            story = {} # will generate story here
            job.story_id = 1 #update story id here
            job.status = "completed"
            job.completed_at = datetime.now()
            db.commit()
        except Exception as e:
            job.story_id = 1  # update story id here
            job.status = "failed"
            job.completed_at = datetime.now()
            job.error = str(e)
            db.commit()
    finally:
        db.close() #whether job completes or fails, we have to close the new session after

@router.get("/{story_id}/complete", response_model=CompleteStoryResponse)
def get_complete_story(story_id: int, db: Session = Depends(get_db)): #line 84 and 85 should hvae the same story_id for dynamic populating
    story = db.query(Story).filter(Story.id == story_id).first() #finding the story
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    complete_story = build_complete_story_tree(db, story)
    return complete_story

def build_complete_story_tree(db: Session, story:Story) -> CompleteStoryResponse:
    pass