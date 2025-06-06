"""
FastAPI AI Service for Docker Chat Platform
Integrates with Google Gemini API for intelligent responses
"""
import os
import time
import logging
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

import google.generativeai as genai
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY not found. AI service will use mock responses.")
else:
    genai.configure(api_key=GEMINI_API_KEY)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan events"""
    logger.info("AI Service starting up...")
    
    # Test Gemini API connection
    if GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            test_response = model.generate_content("Hello")
            logger.info("Gemini API connection successful")
        except Exception as e:
            logger.error(f"Gemini API connection failed: {e}")
    
    yield
    
    logger.info("AI Service shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Docker Chat Platform AI Service",
    description="AI-powered chat service using Google Gemini API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class ChatMessage(BaseModel):
    """Chat message model"""
    content: str = Field(..., description="Message content")
    role: str = Field(..., description="Message role: 'user', 'assistant', or 'system'")


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    conversation_history: List[ChatMessage] = Field(default=[], description="Previous messages")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Response creativity (0-2)")
    max_tokens: int = Field(default=1000, ge=1, le=4000, description="Maximum response tokens")


class ChatResponse(BaseModel):
    """Chat response model"""
    content: str = Field(..., description="AI response content")
    tokens_used: int = Field(..., description="Number of tokens used")
    model: str = Field(..., description="AI model used")
    response_time_ms: int = Field(..., description="Response time in milliseconds")


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    gemini_api_configured: bool = Field(..., description="Whether Gemini API is configured")


class AIService:
    """AI Service class for handling Gemini API interactions"""
    
    def __init__(self):
        self.model_name = "gemini-1.5-flash"
        self.model = None
        if GEMINI_API_KEY:
            try:
                self.model = genai.GenerativeModel(self.model_name)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini model: {e}")
    
    async def generate_response(
        self, 
        message: str, 
        conversation_history: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """Generate AI response using Gemini API"""
        start_time = time.time()
        
        try:
            if not self.model:
                # Mock response when API is not configured
                return await self._generate_mock_response(message, start_time)
            
            # Prepare conversation context
            context = self._prepare_context(conversation_history, message)
            
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                top_p=0.8,
                top_k=40
            )
            
            # Generate response
            response = self.model.generate_content(
                context,
                generation_config=generation_config
            )
            
            # Calculate tokens (approximate)
            tokens_used = len(response.text.split()) + len(message.split())
            response_time_ms = int((time.time() - start_time) * 1000)
            
            return {
                'content': response.text,
                'tokens_used': tokens_used,
                'model': self.model_name,
                'response_time_ms': response_time_ms
            }
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return await self._generate_error_response(str(e), start_time)
    
    def _prepare_context(self, conversation_history: List[ChatMessage], current_message: str) -> str:
        """Prepare conversation context for AI model"""
        context_parts = [
            "You are a helpful AI assistant in a chat platform. ",
            "Provide clear, helpful, and engaging responses. ",
            "Be concise but informative.\n\n"
        ]
        
        # Add conversation history
        if conversation_history:
            context_parts.append("Previous conversation:\n")
            for msg in conversation_history[-10:]:  # Last 10 messages for context
                role_label = "Human" if msg.role == "user" else "Assistant"
                context_parts.append(f"{role_label}: {msg.content}\n")
            context_parts.append("\n")
        
        # Add current message
        context_parts.append(f"Human: {current_message}\nAssistant:")
        
        return "".join(context_parts)
    
    async def _generate_mock_response(self, message: str, start_time: float) -> Dict[str, Any]:
        """Generate mock response when API is not configured"""
        mock_responses = [
            "I'm a mock AI assistant. To get real responses, please configure your GEMINI_API_KEY.",
            "This is a demo response from the AI service. The system is working correctly!",
            "Hello! I'm responding from the AI microservice. Please set up Gemini API for real AI responses.",
            f"You said: '{message}'. I'm a placeholder response until Gemini API is configured.",
        ]
        
        # Simple response selection based on message length
        response_index = len(message) % len(mock_responses)
        response_content = mock_responses[response_index]
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        return {
            'content': response_content,
            'tokens_used': len(response_content.split()) + len(message.split()),
            'model': 'mock-model',
            'response_time_ms': response_time_ms
        }
    
    async def _generate_error_response(self, error: str, start_time: float) -> Dict[str, Any]:
        """Generate error response"""
        response_time_ms = int((time.time() - start_time) * 1000)
        
        return {
            'content': f"I apologize, but I encountered an error: {error}. Please try again later.",
            'tokens_used': 20,  # Approximate
            'model': self.model_name or 'error-model',
            'response_time_ms': response_time_ms
        }


# Initialize AI service
ai_service = AIService()


# Dependency injection
async def get_ai_service() -> AIService:
    """Dependency injection for AI service"""
    return ai_service


# API endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """API root endpoint"""
    return {
        "message": "Docker Chat Platform AI Service",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="ai-service",
        version="1.0.0",
        gemini_api_configured=bool(GEMINI_API_KEY)
    )


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """Main chat endpoint for AI interactions"""
    try:
        logger.info(f"Received chat request: {request.message[:50]}...")
        
        response = await ai_service.generate_response(
            message=request.message,
            conversation_history=request.conversation_history,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return ChatResponse(**response)
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/models")
async def list_models():
    """List available AI models"""
    return {
        "available_models": [
            {
                "name": "gemini-1.5-flash",
                "description": "Google's Gemini 1.5 Flash model for text generation",
                "configured": bool(GEMINI_API_KEY)
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    ) 