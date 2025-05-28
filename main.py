# Author: Tarun Agarwal
# Multi-Agent AI System
# See README.md for details

import os
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
import json

from memory.shared_memory import SharedMemory
from agents.classifier_agent import ClassifierAgent
from agents.json_agent import JSONAgent
from agents.email_agent import EmailAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent AI System",
    description="A system that processes and routes different types of input to specialized agents",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Initialize shared memory
memory = SharedMemory(os.getenv("REDIS_URL", "redis://localhost:6379"))

# Initialize agents
classifier_agent = ClassifierAgent(memory)
json_agent = JSONAgent(memory)
email_agent = EmailAgent(memory)

class ProcessRequest(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process")
async def process_input(request: ProcessRequest):
    """Process text input."""
    try:
        logger.info("Processing text input")
        # Always pass metadata (empty dict if not provided)
        metadata = request.metadata or {}
        classification = await classifier_agent.process(request.content, metadata)
        logger.info(f"Classification result: {classification}")
        # Process based on format
        if classification["format"] == "json":
            metadata["intent"] = classification["intent"]
            result = await json_agent.process(request.content, metadata)
        elif classification["format"] == "email":
            metadata["intent"] = classification["intent"]
            result = await email_agent.process(request.content, metadata)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {classification['format']}")
        return {
            "classification": classification,
            "processing_result": result
        }
    except Exception as e:
        logger.error(f"Error processing input: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process/file")
async def process_file(file: UploadFile = File(...)):
    """Process uploaded file (supports JSON, Email, PDF)."""
    try:
        logger.info(f"Processing file: {file.filename}")
        content = await file.read()
        try:
            content_str = content.decode('utf-8')
            classification = await classifier_agent.process(content_str, {})
            logger.info(f"Classification result: {classification}")
            if classification["format"] == "json":
                metadata = {"intent": classification["intent"]}
                result = await json_agent.process(content_str, metadata)
            elif classification["format"] == "email":
                metadata = {"intent": classification["intent"]}
                result = await email_agent.process(content_str, metadata)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported format: {classification['format']}")
        except UnicodeDecodeError:
            classification = await classifier_agent.process(content, {})
            logger.info(f"Classification result: {classification}")
            if classification["format"] == "pdf":
                metadata = {"intent": classification["intent"]}
                result = await json_agent.process(content, metadata) if classification["intent"] == "invoice" else {"message": "PDF processed, but only invoice intent is supported for PDF in this demo."}
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported binary format: {classification['format']}")
        return {
            "classification": classification,
            "processing_result": result
        }
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 