from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from .config import get_settings
from .routers import auth, users, problems, practice, chat, execute, translate, farm, agent, solutions, friends, ws, shop, placement, solvedac
from .intents import intent_classifier
from .services.collection_embeddings import initialize_collection_embeddings
from .services.discovery_embeddings import initialize_discovery_embeddings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    settings = get_settings()
    print(f"Starting {settings.app_name} v{settings.app_version}")

    # Intent Classifier 초기화 (백그라운드에서)
    # 서버 시작 시 임베딩 생성 (시간 소요될 수 있음)
    asyncio.create_task(initialize_intent_classifier())

    # Collection Embeddings 초기화 (정보 수집 단계용)
    asyncio.create_task(initialize_collection_embeddings_startup())

    # Discovery Embeddings 초기화 (문제 탐색 단계용)
    asyncio.create_task(initialize_discovery_embeddings_startup())

    yield
    # Shutdown
    print("Shutting down...")


async def initialize_intent_classifier():
    """Intent Classifier 임베딩 초기화"""
    try:
        await intent_classifier.initialize()
        print("Intent classifier initialized successfully")
    except Exception as e:
        print(f"Intent classifier initialization failed: {e}")
        print("Will initialize on first request instead")


async def initialize_collection_embeddings_startup():
    """Collection Embeddings 초기화 (정보 수집용 topic/difficulty/language)"""
    try:
        success = await initialize_collection_embeddings()
        if success:
            print("Collection embeddings initialized successfully")
        else:
            print("Collection embeddings initialization returned false")
    except Exception as e:
        print(f"Collection embeddings initialization failed: {e}")
        print("Will use keyword fallback instead")


async def initialize_discovery_embeddings_startup():
    """Discovery Embeddings 초기화 (문제 탐색용 action/selection/rerank)"""
    try:
        success = await initialize_discovery_embeddings()
        if success:
            print("Discovery embeddings initialized successfully")
        else:
            print("Discovery embeddings initialization returned false")
    except Exception as e:
        print(f"Discovery embeddings initialization failed: {e}")
        print("Will use keyword fallback instead")


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered active coding learning platform API",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(problems.router, prefix="/problems", tags=["Problems"])
app.include_router(practice.router, prefix="/practice", tags=["Practice"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(execute.router, prefix="/execute", tags=["Code Execution"])
app.include_router(translate.router, prefix="/translate", tags=["Translation"])
app.include_router(farm.router, prefix="/farm", tags=["Farm"])
app.include_router(shop.router, prefix="/shop", tags=["Shop"])
app.include_router(placement.router, prefix="/placement", tags=["Placement"])
app.include_router(agent.router, prefix="/agent", tags=["AI Agents"])
app.include_router(solutions.router, prefix="/solutions", tags=["Solutions"])
app.include_router(friends.router, prefix="/friends", tags=["Friends"])
app.include_router(ws.router, prefix="/ws", tags=["WebSocket"])
app.include_router(solvedac.router, prefix="/solvedac", tags=["solved.ac"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
