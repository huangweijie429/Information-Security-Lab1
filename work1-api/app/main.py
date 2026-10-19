"""HDU IS Lab 1 - secure REST API (FastAPI + SQLite)."""
from contextlib import asynccontextmanager

import html

import jwt
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from . import db
from .security import create_token, verify_password, verify_token

bearer = HTTPBearer(auto_error=False)


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.init_db()
    yield


app = FastAPI(
    title="HDU IS Lab 1 - Secure REST API",
    description="Lab work 1: JWT auth, parameterized SQL, escaped output.",
    version="1.0.0",
    lifespan=lifespan,
)


class LoginRequest(BaseModel):
    # allow-list validation: only safe characters ever reach the database layer
    username: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class Post(BaseModel):
    id: int
    author: str
    title: str
    body: str


class Me(BaseModel):
    username: str
    created_at: str


def current_user(cred: HTTPAuthorizationCredentials | None = Depends(bearer)) -> str:
    if cred is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return verify_token(cred.credentials)
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/auth/login", response_model=TokenResponse, tags=["auth"])
def login(body: LoginRequest) -> TokenResponse:
    with db.connect() as conn:
        row = conn.execute(
            "SELECT username, password_hash FROM users WHERE username = ?",  # noqa: E501
            (body.username,),
        ).fetchone()
    if row is None or not verify_password(body.password, row["password_hash"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    return TokenResponse(access_token=create_token(row["username"]))


@app.get("/api/data", response_model=list[Post], tags=["data"])
def data(
    user: str = Depends(current_user),
    q: str | None = Query(default=None, max_length=64),
) -> list[Post]:
    with db.connect() as conn:
        if q:
            rows = conn.execute(
                "SELECT id, author, title, body FROM posts"
                " WHERE title LIKE ? OR body LIKE ?",
                (f"%{q}%", f"%{q}%"),
            ).fetchall()
        else:
            rows = conn.execute("SELECT id, author, title, body FROM posts").fetchall()
    # XSS defence: escape user-controlled content on the way out
    return [
        Post(
            id=r["id"],
            author=html.escape(r["author"]),
            title=html.escape(r["title"]),
            body=html.escape(r["body"]),
        )
        for r in rows
    ]


@app.get("/api/me", response_model=Me, tags=["data"])
def me(user: str = Depends(current_user)) -> Me:
    with db.connect() as conn:
        row = conn.execute(
            "SELECT username, created_at FROM users WHERE username = ?", (user,)
        ).fetchone()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return Me(username=row["username"], created_at=row["created_at"])
