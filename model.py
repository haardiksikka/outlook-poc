from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class QueryRequest(BaseModel):
    userEmail: str
    clientEmail: str
    query: str
    months: int = 3


class EmailAddress(BaseModel):
    """Represents an email address"""
    address: str
    name: Optional[str] = None


class Email(BaseModel):
    """Represents a complete email message"""
    id: str
    subject: Optional[str] = None
    sender: Optional[EmailAddress] = None
    body: str
    receivedDateTime: datetime
    webLink: Optional[str] = None  # Direct URL to open email in Outlook
    
    class Config:
        arbitrary_types_allowed = True


class EmailChunk(BaseModel):
    """Represents a chunk of email text with context preservation"""
    email_id: str
    subject: Optional[str] = None
    sender: Optional[str] = None
    chunk: str  # The actual text chunk
    received_at: Optional[datetime] = None
    chunk_index: int  # Position of this chunk within the email
    total_chunks: int  # Total number of chunks for this email
    is_overlapped: bool = False  # Whether this chunk contains overlapping text
    webLink: Optional[str] = None  # Direct URL to open email in Outlook
    
    class Config:
        arbitrary_types_allowed = True


class RankedResult(BaseModel):
    """Represents a ranked search result"""
    email_id: str
    subject: Optional[str] = None
    sender: Optional[str] = None
    chunk: str
    received_at: Optional[datetime] = None
    relevance_score: float  # 0.0 to 1.0
    chunk_index: int
    
    class Config:
        arbitrary_types_allowed = True
