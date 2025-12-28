"""
Translation Router
- Azure Translator API를 활용한 번역 엔드포인트
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from ..services.translator import (
    translate_text,
    detect_language,
    get_supported_languages,
)

router = APIRouter()


class TranslateRequest(BaseModel):
    """번역 요청 모델"""
    text: str
    to_language: str  # 대상 언어 코드 (예: 'ko', 'en')
    from_language: Optional[str] = None  # 원본 언어 (None이면 자동 감지)


class TranslateResponse(BaseModel):
    """번역 응답 모델"""
    success: bool
    translated_text: Optional[str] = None
    detected_language: Optional[str] = None
    to_language: Optional[str] = None
    error: Optional[str] = None


class DetectRequest(BaseModel):
    """언어 감지 요청 모델"""
    text: str


class DetectResponse(BaseModel):
    """언어 감지 응답 모델"""
    success: bool
    language: Optional[str] = None
    language_name: Optional[str] = None
    score: Optional[float] = None
    error: Optional[str] = None


class LanguagesResponse(BaseModel):
    """지원 언어 응답 모델"""
    languages: dict


@router.post("/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    """
    텍스트 번역

    - **text**: 번역할 텍스트
    - **to_language**: 대상 언어 코드 (ko, en, ja, zh-Hans 등)
    - **from_language**: 원본 언어 코드 (선택, 없으면 자동 감지)
    """
    if not request.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text cannot be empty"
        )

    if len(request.text) > 50000:  # Azure 제한: 50,000자
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text exceeds maximum length (50,000 characters)"
        )

    result = await translate_text(
        text=request.text,
        to_language=request.to_language,
        from_language=request.from_language,
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Translation failed")
        )

    return TranslateResponse(**result)


@router.post("/detect", response_model=DetectResponse)
async def detect(request: DetectRequest):
    """
    텍스트 언어 감지

    - **text**: 언어를 감지할 텍스트
    """
    if not request.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text cannot be empty"
        )

    result = await detect_language(request.text)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Language detection failed")
        )

    return DetectResponse(**result)


@router.get("/languages", response_model=LanguagesResponse)
async def languages():
    """
    지원 언어 목록 조회

    번역에 사용할 수 있는 언어 코드와 이름을 반환합니다.
    """
    return LanguagesResponse(languages=get_supported_languages())
