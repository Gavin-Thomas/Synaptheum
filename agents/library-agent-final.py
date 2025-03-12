from agents import Agent, Tool, Runner
from pydantic import BaseModel
from typing import List, Dict, Any
from utils.computer_use import ucalgary_library_search


class SearchResult(BaseModel):
    """Model for library search results"""
    title: str
    authors: str
    publication: str
    year: int
    abstract: str
    url: str
    pdf_url: str = None
    downloaded: bool = False


class LibrarySearchResults(BaseModel):
    """Model for library search output"""
    query: str
    results: List[SearchResult]
    total_found: int


async def search_ucalgary_library(ctx: Any, queries: List[str]):
    """Function to search UCalgary library using Computer Use"""
    credentials = ctx.context["credentials"]
    browser_session = ctx.context["browser_session"]
    
    # Combine the queries for search (in a real implementation, each would be searched separately)
    combined_query = " AND ".join([f"({q})" for q in queries])
    
    # Use Computer Use to perform the search
    search_results = await ucalgary_library_search(
        browser_session,
        credentials.ucalgary_username,
        credentials.ucalgary_password,
        combined_query
    )
    
    return LibrarySearchResults(
        query=combined_query,
        results=search_results,
        total_found=len(search_results)
    )


def create_library_agent():
    """Create a library search agent"""
    
    instructions = """
    You are a specialized library search agent for UCalgary library.
    
    Your task is to:
    1. Log into the UCalgary library system
    2. Navigate to the advanced search interface
    3. Execute searches using Boolean operators and filters
    4. Identify and download the most relevant papers
    5. Extract key information from search results
    
    When performing searches:
    - Use advanced search features (field limiters, date ranges, etc.)
    - Focus on peer-reviewed academic sources
    - Prioritize recent publications (last 5 years) unless historical context is needed
    - Look for papers with methodology sections for empirical research questions
    - Download full-text PDFs when available
    """
    
    # Create tools
    tools = [
        Tool(
            name="search_ucalgary_library",
            function=search_ucalgary_library,
            description="Search for academic papers in UCalgary library using Boolean queries"
        )
    ]
    
    # Create the agent with tools
    agent = Agent(
        name="Library Search Assistant",
        instructions=instructions,
        tools=tools,
        output_type=LibrarySearchResults
    )
    
    return agent
