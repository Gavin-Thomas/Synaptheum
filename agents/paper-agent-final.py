from agents import Agent, Tool, Runner
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from utils.vector_store import create_paper_vector_store, search_papers


class PaperEvaluation(BaseModel):
    """Model for paper evaluation"""
    title: str
    authors: str
    relevance_score: float  # 0-10 rating
    quality_score: float    # 0-10 rating
    key_findings: List[str]
    methodology: Optional[str]
    limitations: Optional[str]
    citation: str  # Formatted citation
    pdf_url: Optional[str]


class ScreenedPapers(BaseModel):
    """Model for paper screening output"""
    selected_papers: List[PaperEvaluation]
    rejected_papers: List[str]  # Titles of rejected papers
    thematic_categories: Dict[str, List[str]]  # Theme -> List of paper titles


async def create_paper_index(ctx: Any, papers: List[Dict]):
    """Create a vector store index of papers for semantic search"""
    # Create a vector store for the papers
    vector_store_id = await create_paper_vector_store(papers)
    ctx.context["vector_store_id"] = vector_store_id
    return {"status": "created", "vector_store_id": vector_store_id}


async def evaluate_papers(ctx: Any, research_question: str):
    """Evaluate papers based on research question"""
    vector_store_id = ctx.context.get("vector_store_id")
    if not vector_store_id:
        raise ValueError("Paper index not created. Run create_paper_index first.")
    
    # Search for relevant papers
    relevant_papers = await search_papers(vector_store_id, research_question)
    
    # For demonstration, create evaluations (in a real implementation, this would use the model)
    evaluations = []
    for paper in relevant_papers:
        eval = PaperEvaluation(
            title=paper["title"],
            authors=paper["authors"],
            relevance_score=paper.get("relevance_score", 5) * 2,  # Convert to 0-10 scale
            quality_score=7.5,  # Placeholder
            key_findings=["Key finding 1", "Key finding 2"],
            methodology="Qualitative analysis",
            limitations="Small sample size",
            citation=f"{paper['authors']} ({paper.get('year', '2023')}). {paper['title']}.",
            pdf_url=paper.get("pdf_url")
        )
        evaluations.append(eval)
    
    # Group papers by themes (placeholder implementation)
    themes = {"Methodology": [], "Theoretical": [], "Application": []}
    for i, eval in enumerate(evaluations):
        if i % 3 == 0:
            themes["Methodology"].append(eval.title)
        elif i % 3 == 1:
            themes["Theoretical"].append(eval.title)
        else:
            themes["Application"].append(eval.title)
    
    return ScreenedPapers(
        selected_papers=evaluations,
        rejected_papers=["Irrelevant paper 1", "Low quality paper 2"],
        thematic_categories=themes
    )


def create_paper_agent():
    """Create a paper screening agent"""
    
    instructions = """
    You are a specialized paper screening and evaluation agent.
    
    Your task is to:
    1. Evaluate papers for relevance to the research question
    2. Assess methodological quality and rigor
    3. Extract key findings and contributions
    4. Identify limitations and potential biases
    5. Categorize papers by themes or approaches
    6. Create properly formatted citations
    
    When evaluating papers:
    - Focus on methodology quality and sample size adequacy
    - Consider recency and citation count as quality indicators
    - Extract key quotes that directly address the research question
    - Note any conflicting findings between different papers
    - Categorize papers by theoretical approach, methodology, or findings
    """
    
    # Create tools
    tools = [
        Tool(
            name="create_paper_index",
            function=create_paper_index,
            description="Create a searchable index of papers for semantic analysis"
        ),
        Tool(
            name="evaluate_papers",
            function=evaluate_papers,
            description="Evaluate papers for relevance and quality"
        )
    ]
    
    # Create the agent with tools
    agent = Agent(
        name="Paper Screening Assistant",
        instructions=instructions,
        tools=tools,
        output_type=ScreenedPapers
    )
    
    return agent
