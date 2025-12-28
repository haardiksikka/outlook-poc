from auth import get_token_device_flow2
from graph_client import fetch_client_emails
from email_processing import normalize_and_chunk
from model import EmailChunk
from dialogueagent import DialogueAgent
from typing import NamedTuple


class AnalysisWithCitations(NamedTuple):
    """Response with cited email chunks"""
    analysis: str
    cited_chunks: list[EmailChunk]
    citation_map: dict  # Maps chunk_id to chunk for easy lookup


def build_context_with_citations(chunks: list[EmailChunk]) -> tuple[str, dict]:
    """Build context string from chunks with unique identifiers for citations."""
    context_parts = []
    citation_map = {}
    
    for idx, chunk in enumerate(chunks):
        chunk_id = f"[EMAIL-{idx+1}]"
        header = f"{chunk_id} From: {chunk.sender} | {chunk.received_at.strftime('%Y-%m-%d %H:%M')}"
        subject = f"Subject: {chunk.subject}"
        body = f"Content:\n{chunk.chunk}"
        
        context_parts.append(f"{header}\n{subject}\n{body}")
        citation_map[chunk_id] = chunk
    
    context = "\n" + "=" * 80 + "\n".join(context_parts)
    return context, citation_map


def extract_citations(response: str, citation_map: dict) -> list[EmailChunk]:
    """Extract cited chunks from LLM response."""
    cited_chunks = []
    cited_ids = set()
    
    # Look for citation patterns like [EMAIL-1], [EMAIL-2], etc.
    import re
    pattern = r'\[EMAIL-\d+\]'
    matches = re.findall(pattern, response)
    
    for match in matches:
        if match in citation_map and match not in cited_ids:
            cited_chunks.append(citation_map[match])
            cited_ids.add(match)
    
    return cited_chunks


def query_with_llm(chunks: list[EmailChunk], user_query: str) -> AnalysisWithCitations:
    """Send unfiltered chunks to Claude for intelligent analysis with citations."""
    client = DialogueAgent()
    
    # Build complete context with citations
    context, citation_map = build_context_with_citations(chunks)
    
    response = client.dialogue(query=user_query, context=context)
    
    # Extract cited chunks from response
    cited_chunks = extract_citations(response, citation_map)
    
    return AnalysisWithCitations(
        analysis=response,
        cited_chunks=cited_chunks,
        citation_map=citation_map
    )


def main():
    print("=" * 80)
    print("OUTLOOK EMAIL ANALYSIS - LLM-POWERED WITH CITATIONS")
    print("Direct LLM analysis with source tracking")
    print("=" * 80)
    
    print("\n📧 Authenticating...")
    access_token, claims = get_token_device_flow2()

    # Get user email from token
    user_email = claims.get("preferred_username") or claims.get("email") or claims.get("upn")
    print(f"   User Email: {user_email}")
    
    client_email = "hsikka95@gmail.com"

    print("\n📬 Fetching emails...")
    messages = fetch_client_emails(
        access_token=access_token,
        user_email=user_email,
        client_email=client_email,
        months=3
    )
    print(f"   Fetched {len(messages)} emails")

    print("\n✂️  Chunking emails with overlap (context preservation)...")
    chunks = normalize_and_chunk(messages, chunk_size=300, overlap_size=50)
    print(f"   Generated {len(chunks)} chunks from {len(messages)} emails")
    
    if len(chunks) > 100:
        print(f"\n⚠️  Warning: {len(chunks)} chunks exceeds typical limit of 100")
        print("   Consider adjusting time filter in fetch_client_emails()")

    # Example 1: Summarization query
    print("\n" + "=" * 80)
    print("QUERY 1: SUMMARIZATION")
    print("=" * 80)
    print("\n Query: 'Summarize all our recent interactions and key topics discussed'\n")
    
    result = query_with_llm(
        chunks=chunks,
        user_query="Summarize all our recent interactions and key topics discussed. What are the main areas we've focused on?"
    )
    
    print("\n SUMMARY:\n")
    print(result.analysis)
    print("\n SOURCES CITED:")
    if result.cited_chunks:
        for i, chunk in enumerate(result.cited_chunks, 1):
            print(f"\n  [{i}] Email ID: {chunk.email_id}")
            print(f"      Web Link: {chunk.webLink}")
            print(f"      From: {chunk.sender}")
            print(f"      Subject: {chunk.subject}")
            print(f"      Date: {chunk.received_at.strftime('%Y-%m-%d %H:%M')}")
            print(f"      Preview: {chunk.chunk[:100]}...")
    else:
        print("  No specific emails cited")

    # Example 2: Concerns and issues query
    print("\n" + "=" * 80)
    print("QUERY 2: CONCERNS & ISSUES")
    print("=" * 80)
    print("\n Query: 'What concerns, problems, or issues has the client raised?'\n")
    
    result = query_with_llm(
        chunks=chunks,
        user_query="What concerns, problems, or issues has the client raised? Please highlight any risks or challenges mentioned."
    )
    
    print("\n  CONCERNS:\n")
    print(result.analysis)
    print("\n SOURCES CITED:")
    if result.cited_chunks:
        for i, chunk in enumerate(result.cited_chunks, 1):
            print(f"\n  [{i}] Email ID: {chunk.email_id}")
            print(f"      Web Link: {chunk.webLink}")
            print(f"      From: {chunk.sender}")
            print(f"      Subject: {chunk.subject}")
            print(f"      Date: {chunk.received_at.strftime('%Y-%m-%d %H:%M')}")
            print(f"      Preview: {chunk.chunk[:100]}...")
    else:
        print("  No specific emails cited")

    # Example 3: Opportunities and next steps
    print("\n" + "=" * 80)
    print("QUERY 3: OPPORTUNITIES & ACTION ITEMS")
    print("=" * 80)
    print("\n Query: 'What opportunities for growth or expansion has the client mentioned?'\n")
    
    result = query_with_llm(
        chunks=chunks,
        user_query="What opportunities for growth, expansion, or improvement has the client mentioned? What are the next steps we discussed?"
    )
    
    print("\n🚀 OPPORTUNITIES:\n")
    print(result.analysis)
    print("\n📌 SOURCES CITED:")
    if result.cited_chunks:
        for i, chunk in enumerate(result.cited_chunks, 1):
            print(f"\n  [{i}] Email ID: {chunk.email_id}")
            print(f"      Web Link: {chunk.webLink}")
            print(f"      From: {chunk.sender}")
            print(f"      Subject: {chunk.subject}")
            print(f"      Date: {chunk.received_at.strftime('%Y-%m-%d %H:%M')}")
            print(f"      Preview: {chunk.chunk[:100]}...")
    else:
        print("  No specific emails cited")


if __name__ == "__main__":
    main()
