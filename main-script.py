import asyncio
import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from agents import Agent, Runner, Tool, Handoff, input_guardrail, GuardrailFunctionOutput

from agents.research_planner import create_research_planner
from agents.library_agent import create_library_agent
from agents.paper_agent import create_paper_agent
from agents.document_agent import create_document_agent
from agents.writing_agent import create_writing_agent
from agents.journal_agent import create_journal_agent

from utils.security import security_guardrail, Credentials
from utils.computer_use import initialize_browser

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class ResearchAssistant:
    """Main application class for the research assistant"""
    
    def __init__(self):
        """Initialize the research assistant with credentials and agents"""
        # Initialize credentials (in production, these should come from a secure store)
        self.credentials = Credentials(
            ucalgary_username="gt123@ucalgary.com",
            ucalgary_password="deeznuts123",
            google_username="gg123@gmail.com",
            google_password="deeznuts123"
        )
        
        # Create specialized agents
        self.research_planner = create_research_planner()
        self.library_agent = create_library_agent()
        self.paper_agent = create_paper_agent()
        self.document_agent = create_document_agent()
        self.writing_agent = create_writing_agent()
        self.journal_agent = create_journal_agent()
        
        # Create handoffs for the main agent
        self.handoffs = [
            Handoff(
                name="plan_research",
                agent=self.research_planner,
                description="Analyze research questions and create a structured plan"
            ),
            Handoff(
                name="search_library",
                agent=self.library_agent,
                description="Search for academic papers in UCalgary library"
            ),
            Handoff(
                name="screen_papers",
                agent=self.paper_agent,
                description="Screen and evaluate papers for relevance and quality"
            ),
            Handoff(
                name="manage_documents",
                agent=self.document_agent,
                description="Create and organize Google Docs"
            ),
            Handoff(
                name="write_paper",
                agent=self.writing_agent,
                description="Write academic content with proper citations"
            ),
            Handoff(
                name="recommend_journals",
                agent=self.journal_agent,
                description="Recommend journals for publication"
            )
        ]
        
        # Create the main agent with handoffs and guardrails
        self.main_agent = Agent(
            name="Research Workflow Coordinator",
            instructions="""
            You are a comprehensive research assistant that helps users with academic research.
            Your capabilities include:
            1. Understanding research questions and breaking them down into searchable components
            2. Logging into university library systems to find relevant papers
            3. Screening papers for relevance and quality
            4. Creating and editing Google Docs with citations
            5. Suggesting appropriate journals for publication
            
            Follow these steps for each research task:
            1. Analyze the research question and identify key concepts
            2. Develop a search strategy with appropriate keywords and Boolean operators
            3. Access library resources and conduct searches
            4. Evaluate and select the most relevant papers
            5. Create a structured document with properly formatted citations
            6. Suggest potential journals for publication
            
            Always maintain academic integrity and proper citation practices.
            """,
            handoffs=self.handoffs,
            input_guardrails=[security_guardrail]
        )
    
    async def run_research_workflow(self, research_question, target_journal=None):
        """Run the complete research workflow"""
        try:
            # Initialize browser for Computer Use
            browser_session = await initialize_browser()
            
            # Create context with necessary data
            context = {
                "credentials": self.credentials,
                "browser_session": browser_session,
                "research_question": research_question,
                "target_journal": target_journal
            }
            
            # Run the main agent
            print("Starting research workflow...")
            
            # If target journal is specified, include it in the prompt
            if target_journal:
                prompt = f"Conduct research on the following question: {research_question}. Format the final paper according to the style guidelines of {target_journal}."
            else:
                prompt = f"Conduct research on the following question: {research_question}"
                
            result = await Runner.run(
                self.main_agent, 
                prompt,
                context=context
            )
            
            print("\nResearch completed successfully!")
            return result.final_output
            
        except Exception as e:
            print(f"Error in research workflow: {e}")
            raise


async def main():
    # Get research question from user
    research_question = input("Enter your research question: ")
    
    # Ask if user wants to target a specific journal
    target_journal_response = input("Would you like to target a specific journal? (yes/no): ")
    target_journal = None
    
    if target_journal_response.lower() in ("yes", "y"):
        target_journal = input("Enter the name of the target journal: ")
        print(f"Will format paper according to {target_journal} guidelines.")
    
    # Create and run the research assistant
    assistant = ResearchAssistant()
    result = await assistant.run_research_workflow(research_question, target_journal)
    
    print(f"Research Results: {result}")
    print("Your document has been created in Google Drive.")

if __name__ == "__main__":
    asyncio.run(main())
