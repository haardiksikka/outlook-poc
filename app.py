from fastapi import FastAPI, Header
from typing import List, Optional
from pydantic import BaseModel
from model import QueryRequest, RankedResult, EmailChunk
from graph_client import fetch_client_emails
from email_processing import normalize_and_chunk
from main import query_with_llm, build_context_with_citations

app = FastAPI()


class Citation(BaseModel):
    """Citation of an email source"""
    email_id: str  # Microsoft Graph email ID
    webLink: str  # Direct URL to open email in Outlook
    sender: str
    subject: str
    received_at: str  # ISO format
    preview: str


class AnalysisResponse(BaseModel):
    """Response with analysis and citations"""
    analysis: str
    citations: List[Citation]


@app.post("/query")
def query_emails(
    req: QueryRequest,
    authorization: str = Header(...)
) -> AnalysisResponse:
    """
    Query emails using LLM with citations.
    
    Args:
        req: QueryRequest with userEmail, clientEmail, query, and months
        authorization: Bearer token from client
    
    Returns:
        AnalysisResponse with analysis text and citations
    """
    access_token = authorization.replace("Bearer ", "")

    messages = fetch_client_emails(
        access_token,
        req.userEmail,
        req.clientEmail,
        req.months
    )

    chunks = normalize_and_chunk(messages)
    
    # Get analysis with citations
    result = query_with_llm(chunks, req.query)
    
    # Convert cited chunks to Citation objects
    citations = [
        Citation(
            email_id=chunk.email_id,
            webLink=chunk.webLink or "",  # Direct URL from Microsoft Graph
            sender=chunk.sender,
            subject=chunk.subject or "No subject",
            received_at=chunk.received_at.isoformat(),
            preview=chunk.chunk[:150] + ("..." if len(chunk.chunk) > 150 else "")
        )
        for chunk in result.cited_chunks
    ]
    
    return AnalysisResponse(
        analysis=result.analysis,
        citations=citations
    )