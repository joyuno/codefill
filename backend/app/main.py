from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from .config import get_settings, setup_logging, get_logger
from .routers import auth, users, problems, practice, chat, execute, translate, farm, agent, solutions, friends, ws, shop, placement, solvedac, analysis, ranking, missions
from .intents import intent_classifier
from .services.collection_embeddings import initialize_collection_embeddings
from .services.discovery_embeddings import initialize_discovery_embeddings
from .graphs.orchestrator_v2 import initialize_orchestrator
from .graphs.checkpointer import close_checkpointer

# Initialize logging at module load
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    settings = get_settings()
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    # Intent Classifier 초기화 (백그라운드에서)
    # 서버 시작 시 임베딩 생성 (시간 소요될 수 있음)
    asyncio.create_task(initialize_intent_classifier())

    # Collection Embeddings 초기화 (정보 수집 단계용)
    asyncio.create_task(initialize_collection_embeddings_startup())

    # Discovery Embeddings 초기화 (문제 탐색 단계용)
    asyncio.create_task(initialize_discovery_embeddings_startup())

    # LangGraph Orchestrator 초기화 (Checkpointer 포함)
    asyncio.create_task(initialize_orchestrator_startup())

    yield

    # Shutdown
    logger.info("Shutting down...")

    # Checkpointer 연결 정리
    await close_checkpointer()
    logger.info("Checkpointer closed")


async def initialize_intent_classifier():
    """Intent Classifier 임베딩 초기화"""
    try:
        await intent_classifier.initialize()
        logger.info("Intent classifier initialized successfully")
    except Exception as e:
        logger.warning(f"Intent classifier initialization failed: {e}")
        logger.info("Will initialize on first request instead")


async def initialize_collection_embeddings_startup():
    """Collection Embeddings 초기화 (정보 수집용 topic/difficulty/language)"""
    try:
        success = await initialize_collection_embeddings()
        if success:
            logger.info("Collection embeddings initialized successfully")
        else:
            logger.warning("Collection embeddings initialization returned false")
    except Exception as e:
        logger.warning(f"Collection embeddings initialization failed: {e}")
        logger.info("Will use keyword fallback instead")


async def initialize_discovery_embeddings_startup():
    """Discovery Embeddings 초기화 (문제 탐색용 action/selection/rerank)"""
    try:
        success = await initialize_discovery_embeddings()
        if success:
            logger.info("Discovery embeddings initialized successfully")
        else:
            logger.warning("Discovery embeddings initialization returned false")
    except Exception as e:
        logger.warning(f"Discovery embeddings initialization failed: {e}")
        logger.info("Will use keyword fallback instead")


async def initialize_orchestrator_startup():
    """LangGraph Orchestrator 초기화 (Checkpointer 포함)"""
    try:
        await initialize_orchestrator()
        logger.info("LangGraph Orchestrator initialized successfully (with Checkpointer)")
    except Exception as e:
        logger.warning(f"Orchestrator initialization failed: {e}")
        logger.info("Will initialize on first request instead")


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
## CodeFill API

AI 기반 능동적 코딩 학습 플랫폼 API입니다.

### 주요 기능

- **Authentication**: 소셜 로그인 (카카오, 구글, 깃허브)
- **AI Agents**: LangGraph 기반 대화형 AI 튜터
- **Practice**: 빈칸 채우기, 퍼즐, 대화형 문제 풀이
- **Code Execution**: Judge0 기반 코드 실행 및 채점
- **Farm**: 게이미피케이션 (농장 시스템)

### 인증

대부분의 API는 JWT 토큰 인증이 필요합니다.
`Authorization: Bearer <token>` 헤더를 포함해주세요.
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "Authentication", "description": "사용자 인증 및 OAuth"},
        {"name": "Users", "description": "사용자 프로필 및 설정"},
        {"name": "Problems", "description": "문제 조회 및 관리"},
        {"name": "Practice", "description": "문제 풀이 및 제출"},
        {"name": "AI Agents", "description": "LangGraph 기반 AI 튜터"},
        {"name": "Chat", "description": "대화 히스토리 관리"},
        {"name": "Code Execution", "description": "코드 실행 및 채점"},
        {"name": "Farm", "description": "게이미피케이션 시스템"},
        {"name": "Shop", "description": "상점 아이템"},
        {"name": "Placement", "description": "농장 아이템 배치"},
        {"name": "Friends", "description": "친구 시스템"},
        {"name": "Translation", "description": "문제 번역"},
        {"name": "Solutions", "description": "문제 풀이 솔루션"},
        {"name": "solved.ac", "description": "solved.ac 연동"},
        {"name": "WebSocket", "description": "실시간 통신"},
        {"name": "Analysis", "description": "약점 분석 및 추천"},
        {"name": "Ranking", "description": "랭킹 시스템"},
        {"name": "Missions", "description": "일일 미션 및 주간 챌린지"},
    ],
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
app.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
app.include_router(ranking.router, prefix="/ranking", tags=["Ranking"])
app.include_router(missions.router, tags=["Missions"])


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
