from bs4 import BeautifulSoup
import re
from typing import List, Generator
from model import EmailChunk, Email


def clean_html(html: str) -> str:
    """Remove HTML tags and normalize whitespace"""
    soup = BeautifulSoup(html or "", "html.parser")
    text = soup.get_text(separator=" ")
    return re.sub(r"\s+", " ", text).strip()


def chunk_text(
    text: str, 
    chunk_size: int = 300, 
    overlap_size: int = 50
) -> Generator[str, None, None]:
    """
    Split text into overlapping chunks to preserve context.
    
    Args:
        text: Text to chunk
        chunk_size: Number of words per chunk
        overlap_size: Number of words to overlap between chunks
    
    Yields:
        Text chunks with overlap
    """
    words = text.split()
    
    # If text is smaller than chunk size, return as is
    if len(words) <= chunk_size:
        yield " ".join(words)
        return
    
    step = chunk_size - overlap_size
    
    for i in range(0, len(words), step):
        # Get chunk from current position to chunk_size
        chunk_end = min(i + chunk_size, len(words))
        chunk = " ".join(words[i:chunk_end])
        
        if chunk.strip():  # Only yield non-empty chunks
            yield chunk
        
        # Stop if we've reached the end
        if chunk_end == len(words):
            break


def normalize_and_chunk(
    emails: List[Email],
    chunk_size: int = 300,
    overlap_size: int = 50
) -> List[EmailChunk]:
    """
    Normalize emails and split into overlapping chunks.
    
    Args:
        emails: List of Email objects from graph_client
        chunk_size: Words per chunk
        overlap_size: Words to overlap between chunks
    
    Returns:
        List of EmailChunk objects with preserved context
    """
    chunks: List[EmailChunk] = []

    for email in emails:
        # Clean email body
        body = clean_html(email.body)
        
        # Skip empty emails
        if not body.strip():
            continue
        
        # Extract metadata
        email_id = email.id
        subject = email.subject or ""
        sender = email.sender.address if email.sender else ""
        received_at = email.receivedDateTime
        web_link = email.webLink  # Get direct URL from email
        
        # Generate overlapping chunks
        chunk_list = list(chunk_text(body, chunk_size, overlap_size))
        total_chunks = len(chunk_list)
        
        # Create EmailChunk objects
        for chunk_idx, chunk_text_content in enumerate(chunk_list):
            email_chunk = EmailChunk(
                email_id=email_id,
                subject=subject,
                sender=sender,
                chunk=chunk_text_content,
                received_at=received_at,
                chunk_index=chunk_idx,
                total_chunks=total_chunks,
                is_overlapped=(chunk_idx > 0 and overlap_size > 0),  # All but first chunk contain overlap
                webLink=web_link  # Pass direct URL to chunk
            )
            chunks.append(email_chunk)

    return chunks
