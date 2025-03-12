from agents import Agent, Tool, Runner
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union


class JournalRecommendation(BaseModel):
    """Model for journal recommendation"""
    name: str
    publisher: str
    impact_factor: Optional[float]
    acceptance_rate: Optional[float]
    review_time: Optional[str]  # e.g., "3-6 months"
    publication_fees: Optional[str]
    open_access: bool
    submission_requirements: str
    suitability_score: float  # 0-10 rating
    rationale: str


class JournalRecommendations(BaseModel):
    """Model for journal recommendations output"""
    recommended_journals: List[JournalRecommendation]
    research_area: str
    publication_strategy: str


async def recommend_journals(ctx: Any, research_area: str, paper_title: str, abstract: str):
    """Recommend journals for publication based on research area and paper details"""
    # In a real implementation, this would use the LLM to generate recommendations
    # or query a journal database
    
    # Generate mock journal recommendations
    recommendations = [
        JournalRecommendation(
            name="Journal of Research Studies",
            publisher="Academic Press",
            impact_factor=2.3,
            acceptance_rate=35.0,
            review_time="2-4 months",
            publication_fees="$1,500 for open access",
            open_access=True,
            submission_requirements="Max 8,000 words, APA style, double-blind peer review",
            suitability_score=8.5,
            rationale="Strong match with research area and methodological approach"
        ),
        JournalRecommendation(
            name="International Review of Academic Topics",
            publisher="Global Science Publishers",
            impact_factor=1.8,
            acceptance_rate=42.0,
            review_time="1-3 months",
            publication_fees="$800 for open access",
            open_access=True,
            submission_requirements="Max 6,000 words, Chicago style",
            suitability_score=7.8,
            rationale="Good match with topic, faster review time, higher acceptance rate"
        ),
        JournalRecommendation(
            name="Applied Research Quarterly",
            publisher="University Press",
            impact_factor=1.5,
            acceptance_rate=48.0,
            review_time="1-2 months",
            publication_fees="None for standard publication",
            open_access=False,
            submission_requirements="Max 5,000 words, APA style",
            suitability_score=7.2,
            rationale="Highest acceptance rate, fastest review time, no fees for standard publication"
        )
    ]
    
    return JournalRecommendations(
        recommended_journals=recommendations,
        research_area=research_area,
        publication_strategy="Recommend starting with the Applied Research Quarterly for fastest publication, then trying higher impact journals if rejected"
    )


def create_journal_agent():
    """Create a journal recommendation agent"""
    
    instructions = """
    You are a specialized journal recommendation agent.
    
    Your task is to:
    1. Identify appropriate journals matching the research area
    2. Evaluate journal metrics (impact factor, acceptance rate)
    3. Consider review timelines and publication fees
    4. Assess submission requirements and formatting guidelines
    5. Recommend a publication strategy for maximum success
    
    When recommending journals:
    - Prioritize journals with higher acceptance rates for easier publication
    - Consider both open access and traditional publication models
    - Evaluate the match between paper methodology and journal preferences
    - Check journal scope and recent publications for relevance
    - Consider special issues that may align with the research topic
    - Suggest a tiered submission strategy (starting with most likely to accept)
    """
    
    # Create tools
    tools = [
        Tool(
            name="recommend_journals",
            function=recommend_journals,
            description="Recommend journals for publication based on research area and paper details"
        )
    ]
    
    # Create the agent with tools
    agent = Agent(
        name="Journal Recommendation Assistant",
        instructions=instructions,
        tools=tools,
        output_type=JournalRecommendations
    )
    
    return agent
