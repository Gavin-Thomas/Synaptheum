from agents import Agent, Tool, Runner
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from utils.computer_use import google_drive_login, create_google_doc


class DocumentInfo(BaseModel):
    """Model for document information"""
    title: str
    doc_id: str
    url: str
    sections: List[str]  # Document sections/headings


async def login_to_google(ctx: Any):
    """Log into Google account using Computer Use"""
    credentials = ctx.context["credentials"]
    browser_session = ctx.context["browser_session"]
    
    # Use Computer Use to login to Google
    result = await google_drive_login(
        browser_session,
        credentials.google_username,
        credentials.google_password
    )
    
    ctx.context["google_logged_in"] = True
    return {"status": "success", "message": "Logged into Google Drive"}


async def create_research_document(ctx: Any, title: str, sections: List[str]):
    """Create a Google Doc with proper structure"""
    if not ctx.context.get("google_logged_in"):
        await login_to_google(ctx)
    
    browser_session = ctx.context["browser_session"]
    
    # Use Computer Use to create a document
    doc_info = await create_google_doc(
        browser_session,
        title,
        sections
    )
    
    # Store document info in context
    ctx.context["document"] = doc_info
    
    return DocumentInfo(
        title=title,
        doc_id=doc_info["id"],
        url=doc_info["url"],
        sections=sections
    )


def create_document_agent():
    """Create a Google Drive document agent"""
    
    instructions = """
    You are a specialized Google Drive document management agent.
    
    Your task is to:
    1. Log into Google Drive
    2. Create new properly structured documents
    3. Set up academic formatting with appropriate sections
    4. Organize content hierarchically with headings
    5. Apply consistent formatting throughout
    
    When creating research documents:
    - Use descriptive, specific titles
    - Create standard academic paper structure
    - Set up proper heading hierarchy (H1, H2, H3)
    - Add placeholder sections for all standard parts
    - Apply consistent font and paragraph styles
    """
    
    # Create tools
    tools = [
        Tool(
            name="login_to_google",
            function=login_to_google,
            description="Log into Google account"
        ),
        Tool(
            name="create_research_document",
            function=create_research_document,
            description="Create a new Google Doc with proper academic structure"
        )
    ]
    
    # Create the agent with tools
    agent = Agent(
        name="Document Management Assistant",
        instructions=instructions,
        tools=tools,
        output_type=DocumentInfo
    )
    
    return agent
