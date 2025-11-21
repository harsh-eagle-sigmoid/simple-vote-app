# backend/app/main.py

import os
from typing import Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .s3_utils import load_votes, save_votes, DEFAULT_OPTIONS

# Load environment variables from .env (for local dev)
load_dotenv()


class Option(BaseModel):
    id: str
    label: str
    votes: int


class VotesResponse(BaseModel):
    question: str
    options: List[Option]
    totalVotes: int


class VoteResult(BaseModel):
    message: str
    votes: Dict[str, int]
    totalVotes: int


app = FastAPI(title="Simple Vote App Backend")

# CORS: allow all origins while developing (safe enough locally)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict later to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

QUESTION_TEXT = "Which option do you like the most?"


@app.get("/")
def root():
    return {
        "message": "Backend is running. Try /health or /api/votes",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/votes", response_model=VotesResponse)
def get_votes():
    """
    Fetch current vote counts from S3.
    """
    votes = load_votes()

    options: List[Option] = []
    total = 0

    for opt_id in DEFAULT_OPTIONS:
        count = int(votes.get(opt_id, 0))
        total += count
        options.append(
            Option(
                id=opt_id,
                label=f"Option {opt_id}",
                votes=count,
            )
        )

    return VotesResponse(
        question=QUESTION_TEXT,
        options=options,
        totalVotes=total,
    )


@app.post("/api/vote/{option_id}", response_model=VoteResult)
def vote(option_id: str):
    """
    Increment the vote count for the given option_id.
    Valid options: A, B, C (from DEFAULT_OPTIONS).
    """
    option_id = option_id.upper()

    if option_id not in DEFAULT_OPTIONS:
        raise HTTPException(status_code=400, detail="Invalid option")

    votes = load_votes()
    current = int(votes.get(option_id, 0))
    votes[option_id] = current + 1

    save_votes(votes)

    total = sum(int(v) for v in votes.values())

    return VoteResult(
        message=f"Vote registered for option {option_id}",
        votes=votes,
        totalVotes=total,
    )
