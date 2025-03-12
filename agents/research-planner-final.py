from agents import Agent, Tool
from pydantic import BaseModel
from typing import List


class ResearchPlan(BaseModel):
    """Model for research plan output"""
    research_question: str
    key_concepts: List[str]
    search_terms: List[str]
    search_queries: List[str]  # Boolean search queries
    potential_databases: List[str]  # Specific databases to search
    research_approach: str


def create_research_planner():
    """Create a research planning agent"""
    
    instructions = """
    You are a research planning specialist who helps break down research questions into searchable components.
    
    Your task is to:
    1. Analyze the research question to identify key concepts and variables
    2. Generate effective search terms including synonyms and related concepts
    3. Create Boolean search queries using AND, OR, NOT operators
    4. Identify relevant academic databases appropriate for the research domain
    5. Suggest an overall approach to answering the research question
    
    Create search queries that are specific enough to yield relevant results but broad enough to capture all pertinent literature.
    Include both general terms and discipline-specific terminology.
    """
    
    # Create the agent with structured output
    agent = Agent(
        name="Research Planner",
        instructions=instructions,
        output_type=ResearchPlan
    )
    
    return agent
