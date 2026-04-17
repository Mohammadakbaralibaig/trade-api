import os
import time
import logging
from fastapi import Header
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv

from middleware.auth import verify_api_key
from middleware.rate_limiter import limiter
from services.search_service import search_market_data
from services.gemini_service import analyze_with_gemini

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Trade Opportunities API",
    description="""
    ## Trade Opportunities API
    
    Analyzes real-time market data and generates structured trade opportunity 
    reports for specific sectors in India.
    
    ### How to use
    - Call `GET /analyze/{sector}` with a sector name
    - Pass your API key in the `X-API-Key` header
    - Get back a detailed markdown report
    
    ### Example sectors
    `pharmaceuticals`, `technology`, `agriculture`, `textiles`, `automobiles`
    """,
    version="1.0.0"
)

# Rate limiter setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage
sessions = {}


@app.get("/", tags=["General"])
async def root():
    """Check if API is running."""
    return {
        "message": "Trade Opportunities API is running!",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["General"])
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "active_sessions": len(sessions)
    }


@app.get("/analyze/{sector}", tags=["Analysis"])
@limiter.limit("5/minute")
async def analyze_sector(
    request: Request,
    sector: str,
    x_api_key: str = Header(default="mysecretkey123")
):
    """
    Analyze trade opportunities for a given sector in India.
    
    - **sector**: Name of the sector (e.g. pharmaceuticals, technology)
    - Returns a detailed markdown report with trade insights
    """

    # Input validation
    sector = sector.strip().lower()

    if len(sector) < 2 or len(sector) > 50:
        raise HTTPException(
            status_code=400,
            detail="Sector name must be between 2 and 50 characters."
        )

    if not sector.replace(" ", "").isalpha():
        raise HTTPException(
            status_code=400,
            detail="Sector name must contain letters only."
        )

    # Track session
    client_ip = request.client.host
    sessions[client_ip] = {
        "sector": sector,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    logger.info(f"Request received — sector: {sector} | IP: {client_ip}")

    # Step 1: Collect market data
    logger.info("Searching for market data...")
    market_data = search_market_data(sector)

    # Step 2: Analyze with Gemini
    logger.info("Sending data to Gemini for analysis...")
    report = analyze_with_gemini(sector, market_data)

    return {
        "sector": sector,
        "report": report,
        "format": "markdown"
    }