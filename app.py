from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import sqlite3
import os
from dotenv import load_dotenv
import json
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
import requests
import logging

# Load environment variables
load_dotenv()

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Xabar TV API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database initialization
DB_NAME = "news.db"

def init_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_message_id INTEGER UNIQUE,
            title TEXT,
            text TEXT,
            image TEXT,
            video TEXT,
            date TEXT,
            telegram_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

# Models
class NewsItem(BaseModel):
    telegram_message_id: Optional[int] = None
    title: Optional[str] = None
    text: Optional[str] = None
    image: Optional[str] = None
    video: Optional[str] = None
    date: Optional[str] = None
    telegram_url: Optional[str] = None

class NewsResponse(BaseModel):
    id: int
    telegram_message_id: Optional[int] = None
    title: Optional[str] = None
    text: Optional[str] = None
    image: Optional[str] = None
    video: Optional[str] = None
    date: Optional[str] = None
    telegram_url: Optional[str] = None
    created_at: str

# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# API Endpoints
@app.post("/api/news", response_model=NewsResponse)
async def create_news(news: NewsItem, background_tasks: BackgroundTasks):
    """Create new news item"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Check if news already exists
        if news.telegram_message_id:
            cursor.execute(
                "SELECT id FROM news WHERE telegram_message_id = ?",
                (news.telegram_message_id,)
            )
            existing = cursor.fetchone()
            if existing:
                conn.close()
                raise HTTPException(status_code=400, detail="News already exists")
        
        # Insert news
        cursor.execute("""
            INSERT INTO news 
            (telegram_message_id, title, text, image, video, date, telegram_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            news.telegram_message_id,
            news.title,
            news.text,
            news.image,
            news.video,
            news.date or datetime.now().isoformat(),
            news.telegram_url
        ))
        
        news_id = cursor.lastrowid
        conn.commit()
        
        # Get created news
        cursor.execute("""
            SELECT id, telegram_message_id, title, text, image, video, date, telegram_url, created_at
            FROM news WHERE id = ?
        """, (news_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="News not found")
        
        response = NewsResponse(
            id=row[0],
            telegram_message_id=row[1],
            title=row[2],
            text=row[3],
            image=row[4],
            video=row[5],
            date=row[6],
            telegram_url=row[7],
            created_at=row[8]
        )
        
        # Broadcast new news via WebSocket
        background_tasks.add_task(
            manager.broadcast,
            json.dumps({"type": "new_news", "data": response.dict()})
        )
        
        logger.info(f"New news created: {news.title}")
        return response
        
    except Exception as e:
        logger.error(f"Error creating news: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/news", response_model=List[NewsResponse])
async def get_news(limit: int = 50, offset: int = 0):
    """Get all news items"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, telegram_message_id, title, text, image, video, date, telegram_url, created_at
            FROM news 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            NewsResponse(
                id=row[0],
                telegram_message_id=row[1],
                title=row[2],
                text=row[3],
                image=row[4],
                video=row[5],
                date=row[6],
                telegram_url=row[7],
                created_at=row[8]
            )
            for row in rows
        ]
        
    except Exception as e:
        logger.error(f"Error getting news: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/news/{news_id}", response_model=NewsResponse)
async def get_news_by_id(news_id: int):
    """Get news by ID"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, telegram_message_id, title, text, image, video, date, telegram_url, created_at
            FROM news WHERE id = ?
        """, (news_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="News not found")
        
        return NewsResponse(
            id=row[0],
            telegram_message_id=row[1],
            title=row[2],
            text=row[3],
            image=row[4],
            video=row[5],
            date=row[6],
            telegram_url=row[7],
            created_at=row[8]
        )
        
    except Exception as e:
        logger.error(f"Error getting news: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/news/{news_id}")
async def delete_news(news_id: int):
    """Delete news by ID"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM news WHERE id = ?", (news_id,))
        conn.commit()
        conn.close()
        
        return {"message": "News deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting news: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_database()
    logger.info("Xabar TV API started successfully")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)