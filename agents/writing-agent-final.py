from agents import Agent, Tool, Runner
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from utils.computer_use import write_google_doc, format_according_to_journal_style


class DocumentSection(BaseModel):
    """Model for a document section"""
    title: str
    content: str
    citations: List[str]


class JournalStyleGuidelines(BaseModel):
    """Model for journal style guidelines"""
    citation_style: str  # APA, MLA, Chicago, IEEE, etc.
    max_word_count: int
    section_requirements: Dict[str, str]  # Section name to requirements
    formatting_notes: str
    reference_format: str
    figure_requirements: Optional[str]
    table_requirements: Optional[str]


class WrittenDocument(BaseModel):
    """Model for a completed written document"""
    title: str
    url: str
    sections: List[DocumentSection]
    total_word_count: int
    citation_count: int
    citation_style: str
    target_journal: Optional[str]
    conforms_to_journal_guidelines: bool = False
    journal_guidelines: Optional[JournalStyleGuidelines] = None


async def get_journal_guidelines(ctx: Any, journal_name: str) -> JournalStyleGuidelines:
    """Get the style guidelines for a specific journal"""
    # In a real implementation, this would fetch actual journal guidelines
    # from a database or by scraping the journal's website
    
    # Mock implementation with sample journal guidelines
    if "applied" in journal_name.lower():
        return JournalStyleGuidelines(
            citation_style="APA",
            max_word_count=6000,
            section_requirements={
                "Abstract": "Max 250 words, structured with Objectives, Methods, Results, Conclusions",
                "Introduction": "Brief context, clear research gap, explicit aims",
                "Methods": "Detailed enough for replication, ethics approval mentioned",
                "Results": "Only results, no interpretation",
                "Discussion": "Interpret results, acknowledge limitations, suggest applications",
                "Conclusion": "Brief, no new information"
            },
            formatting_notes="Double-spaced, 12pt Times New Roman, 1-inch margins",
            reference_format="APA 7th edition, DOI required when available",
            figure_requirements="High resolution (300 dpi), legends below figures",
            table_requirements="Tables should be editable (not images), titles above tables"
        )
    elif "review" in journal_name.lower():
        return JournalStyleGuidelines(
            citation_style="Chicago",
            max_word_count=8000,
            section_requirements={
                "Abstract": "Unstructured, max 300 words",
                "Introduction": "Comprehensive literature background",
                "Methods": "Clear criteria for literature inclusion/exclusion",
                "Discussion": "Synthesis of literature, identify patterns and gaps",
                "Conclusion": "Future research directions"
            },
            formatting_notes="Double-spaced, 12pt font, numbered pages",
            reference_format="Chicago author-date style, full DOI URLs",
            figure_requirements="TIFF or EPS format only",
            table_requirements="No vertical lines, minimal horizontal lines"
        )
    else:
        # Default guidelines
        return JournalStyleGuidelines(
            citation_style="APA",
            max_word_count=7000,
            section_requirements={
                "Abstract": "Max 250 words",
                "Introduction": "Context, gap, aims",
                "Methods": "Clear description of approach",
                "Results": "Key findings only",
                "Discussion": "Interpretation of results",
                "Conclusion": "Brief summary and implications"
            },
            formatting_notes="Double-spaced, 12pt font",
            reference_format="APA style",
            figure_requirements="High-quality images, properly labeled",
            table_requirements="Clear formatting with titles"
        )


async def write_document_section(ctx: Any, section: str, papers: List[Dict], citation_style: str = "APA", journal_guidelines: Optional[JournalStyleGuidelines] = None):
    """Write a section of the research document with proper citations"""
    # In a real implementation, this would use the LLM to generate content
    
    # Generate placeholder content based on section
    if section.lower() == "introduction":
        content = "This introduction provides context for the research question and outlines the paper structure."
        citations = [papers[0]["citation"]] if papers else []
    elif section.lower() == "literature review":
        content = "This literature review synthesizes existing research on the topic, identifying key themes and gaps."
        citations = [p["citation"] for p in papers[:2]] if papers else []
    elif section.lower() == "methodology":
        content = "This methodology section details the research approach and data collection methods."
        citations = [papers[1]["citation"]] if len(papers) > 1 else []
    elif section.lower() == "results" or section.lower() == "findings":
        content = "This section presents the key findings from the analysis."
        citations = []
    elif section.lower() == "discussion":
        content = "This discussion interprets the findings in light of existing literature and identifies implications."
        citations = [p["citation"] for p in papers] if papers else []
    elif section.lower() == "conclusion":
        content = "This conclusion summarizes key points and suggests directions for future research."
        citations = []
    else:
        content = f"Content for {section} section."
        citations = []
    
    return DocumentSection(
        title=section,
        content=content,
        citations=citations
    )


async def format_for_journal(ctx: Any, document_url: str, journal_name: str) -> JournalStyleGuidelines:
    """Format a document according to a specific journal's requirements"""
    browser_session = ctx.context["browser_session"]
    
    # Get journal guidelines
    guidelines = await get_journal_guidelines(ctx, journal_name)
    
    # Use Computer Use to apply formatting
    await format_according_to_journal_style(
        browser_session,
        document_url,
        guidelines
    )
    
    return guidelines


async def write_complete_document(ctx: Any, document_info: Dict, screened_papers: Dict, citation_style: str = "APA", target_journal: str = None):
    """Write a complete research document with all sections"""
    if not ctx.context.get("google_logged_in"):
        raise ValueError("Not logged into Google. Login first.")
    
    browser_session = ctx.context["browser_session"]
    document_url = document_info["url"]
    sections = document_info["sections"]
    
    # Get paper data
    papers = screened_papers.get("selected_papers", [])
    
    # If target journal is specified, get journal guidelines
    journal_guidelines = None
    if target_journal:
        journal_guidelines = await get_journal_guidelines(ctx, target_journal)
        # Use the journal's preferred citation style
        citation_style = journal_guidelines.citation_style
    
    # Generate content for each section
    written_sections = []
    for section in sections:
        # Pass journal guidelines for section-specific formatting
        section_requirements = None
        if journal_guidelines and section in journal_guidelines.section_requirements:
            section_requirements = journal_guidelines.section_requirements[section]
        
        section_content = await write_document_section(
            ctx, 
            section, 
            papers, 
            citation_style,
            journal_guidelines
        )
        written_sections.append(section_content)
    
    # Use Computer Use to write content to the Google Doc
    for section in written_sections:
        await write_google_doc(
            browser_session["page"],
            document_url,
            f"# {section.title}\n\n{section.content}\n\n"
        )
        
    # If target journal specified, apply journal-specific formatting
    if target_journal:
        await format_for_journal(ctx, document_url, target_journal)
    
    # Generate reference list
    references = "\n".join([f"- {p.get('citation', '')}" for p in papers])
    await write_google_doc(
        browser_session["page"],
        document_url,
        f"# References\n\n{references}"
    )
    
    # Calculate word count
    total_word_count = sum(len(s.content.split()) for s in written_sections)
    
    # Check if document conforms to journal guidelines
    conforms_to_guidelines = True
    if journal_guidelines and total_word_count > journal_guidelines.max_word_count:
        conforms_to_guidelines = False
        print(f"Warning: Document exceeds journal word limit ({total_word_count} > {journal_guidelines.max_word_count})")
    
    return WrittenDocument(
        title=document_info["title"],
        url=document_info["url"],
        sections=written_sections,
        total_word_count=total_word_count,
        citation_count=sum(len(s.citations) for s in written_sections),
        citation_style=citation_style,
        target_journal=target_journal,
        conforms_to_journal_guidelines=conforms_to_guidelines,
        journal_guidelines=journal_guidelines
    )


def create_writing_agent():
    """Create an academic writing agent"""
    
    instructions = """
    You are a specialized academic writing agent.
    
    Your task is to:
    1. Generate well-structured academic content
    2. Incorporate research findings from selected papers
    3. Create properly formatted in-text citations
    4. Maintain consistent academic style and terminology
    5. Generate a complete bibliography/reference list
    
    When writing academic content:
    - Use formal academic language appropriate for the discipline
    - Incorporate evidence from the literature with proper attribution
    - Balance summary, synthesis, and critical analysis
    - Maintain logical flow between sections and paragraphs
    - Use discipline-appropriate terminology consistently
    - Format all citations according to the specified style guide
    """
    
    # Create tools
    tools = [
        Tool(
            name="get_journal_guidelines",
            function=get_journal_guidelines,
            description="Get style guidelines for a specific academic journal"
        ),
        Tool(
            name="write_document_section",
            function=write_document_section,
            description="Write a section of a research document with proper citations"
        ),
        Tool(
            name="write_complete_document",
            function=write_complete_document,
            description="Write a complete research document with all sections"
        ),
        Tool(
            name="format_for_journal",
            function=format_for_journal,
            description="Format a document according to a specific journal's requirements"
        )
    ]
    
    # Create the agent with tools
    agent = Agent(
        name="Academic Writing Assistant",
        instructions=instructions,
        tools=tools,
        output_type=WrittenDocument
    )
    
    return agent
