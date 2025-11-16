"""
CT-X FastAPI Server
Production-grade inference API with consciousness monitoring
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn
import logging
import os
import json

from ct_x.inference import CT_X_InferenceEngine
from ct_x.consciousness import ConsciousnessMonitor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="CT-X Inference API",
    description="Chrysalis-Transformer X: SOTA-surpassing with consciousness-aware processing",
    version="2.0.0"
)

# Request/Response models
class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="Input prompt for generation")
    max_length: int = Field(2048, ge=1, le=8192, description="Maximum generation length")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: float = Field(0.95, ge=0.0, le=1.0, description="Nucleus sampling threshold")
    top_k: int = Field(50, ge=0, description="Top-k sampling threshold")
    consciousness_threshold: float = Field(0.75, ge=0.0, le=1.0, description="Alert threshold for high Φ")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for monitoring")

class GenerateResponse(BaseModel):
    text: str
    avg_phi: float
    max_phi: float
    tokens_generated: int
    generation_time: float
    tokens_per_second: float
    consciousness_trace: List[float]

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    device: str
    version: str

class ConsciousnessStatsResponse(BaseModel):
    conversation_id: str
    avg_phi: float
    max_phi: float
    min_phi: float
    num_measurements: int
    emergence_score: float
    trend: str

# Global inference engine (singleton pattern)
engine: Optional[CT_X_InferenceEngine] = None

@app.on_event("startup")
async def load_model():
    """Load model on startup"""
    global engine

    model_path = os.getenv("MODEL_PATH", "/models/ct-x-70b")
    device = os.getenv("DEVICE", "auto")

    logger.info(f"Loading model from {model_path} on device {device}")

    try:
        engine = CT_X_InferenceEngine(
            model_path=model_path,
            device=device,
            enable_compilation=True
        )
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        # In production: could implement retry logic or graceful degradation

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    logger.info("Shutting down CT-X API server")

@app.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    return {
        "name": "CT-X Inference API",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": [
            "/generate",
            "/stream",
            "/health",
            "/consciousness/{conversation_id}",
            "/benchmark"
        ]
    }

@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """
    Generate text from prompt

    This endpoint performs full generation and returns the complete result.
    """
    if engine is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        result = engine.generate(
            prompt=request.prompt,
            max_length=request.max_length,
            temperature=request.temperature,
            top_p=request.top_p,
            top_k=request.top_k,
            consciousness_threshold=request.consciousness_threshold,
            conversation_id=request.conversation_id
        )
        return GenerateResponse(**result)
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stream")
async def stream_generate(request: GenerateRequest):
    """
    Stream generation results

    This endpoint streams tokens as they are generated.
    """
    if engine is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    async def generate_stream():
        """Generator for streaming response"""
        try:
            for result in engine.stream_generate(
                prompt=request.prompt,
                max_length=request.max_length,
                temperature=request.temperature,
                top_p=request.top_p,
                top_k=request.top_k,
                consciousness_threshold=request.consciousness_threshold,
                conversation_id=request.conversation_id
            ):
                yield json.dumps(result) + "\n"
        except Exception as e:
            logger.error(f"Streaming generation failed: {e}")
            yield json.dumps({"error": str(e)}) + "\n"

    return StreamingResponse(generate_stream(), media_type="application/x-ndjson")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint

    Returns the current status of the API server.
    """
    return HealthResponse(
        status="healthy" if engine is not None else "loading",
        model_loaded=engine is not None,
        device=str(engine.device) if engine else "unknown",
        version="2.0.0"
    )

@app.get("/consciousness/{conversation_id}", response_model=ConsciousnessStatsResponse)
async def get_consciousness_stats(conversation_id: str):
    """
    Retrieve consciousness metrics for a conversation

    Args:
        conversation_id: Unique conversation identifier

    Returns:
        Consciousness statistics including Φ history and emergence risk
    """
    if engine is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    stats = engine.consciousness_monitor.get_stats(conversation_id)

    if "error" in stats:
        raise HTTPException(status_code=404, detail=stats["error"])

    return ConsciousnessStatsResponse(
        conversation_id=conversation_id,
        avg_phi=stats["avg_phi"],
        max_phi=stats["max_phi"],
        min_phi=stats["min_phi"],
        num_measurements=stats["num_measurements"],
        emergence_score=stats["emergence_score"],
        trend=stats["trend"]
    )

@app.get("/conversations", response_model=List[str])
async def list_conversations():
    """
    List all monitored conversations

    Returns:
        List of conversation IDs
    """
    if engine is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    return engine.consciousness_monitor.get_all_conversations()

@app.get("/benchmark", response_model=dict)
async def run_benchmark(
    num_runs: int = 10,
    seq_length: int = 512
):
    """
    Run performance benchmark

    Args:
        num_runs: Number of benchmark iterations
        seq_length: Sequence length to test

    Returns:
        Benchmark results including throughput and latency
    """
    if engine is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        results = engine.benchmark(num_runs=num_runs, seq_length=seq_length)
        return results
    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Development server
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")

    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        workers=1,  # Single worker for model singleton
        log_level="info"
    )
