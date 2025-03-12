import base64
import time
import asyncio
from openai import OpenAI
import os
from playwright.async_api import async_playwright
from typing import Dict, List, Any

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def initialize_browser():
    """Initialize a browser for computer use"""
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)  # Set to True in production
    context = await browser.new_context(
        viewport={"width": 1280, "height": 800}
    )
    page = await context.new_page()
    return {"playwright": playwright, "browser": browser, "context": context, "page": page}


async def take_screenshot(page):
    """Take a screenshot of the current page"""
    screenshot_bytes = await page.screenshot()
    screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")
    return screenshot_base64


async def execute_computer_action(page, action):
    """Execute a computer action on the page"""
    action_type = action.get("type")
    
    if action_type == "click":
        await page.mouse.click(action.get("x"), action.get("y"))
    elif action_type == "type":
        await page.keyboard.type(action.get("text"))
    elif action_type == "keypress":
        for key in action.get("keys", []):
            await page.keyboard.press(key)
    elif action_type == "scroll":
        await page.mouse.move(action.get("x"), action.get("y"))
        await page.evaluate(f"window.scrollBy({action.get('scroll_x', 0)}, {action.get('scroll_y', 0)})")
    elif action_type == "wait":
        await asyncio.sleep(2)  # Default wait time
    
    # Wait for any potential page changes to complete
    await page.wait_for_load_state("networkidle", timeout=5000)
    
    return await take_screenshot(page)


async def computer_use_loop(page, goal):
    """Run the computer use loop for a specific goal"""
    # Take initial screenshot
    screenshot = await take_screenshot(page)
    
    # Create initial response with computer use tool
    response = client.responses.create(
        model="computer-use-preview",
        tools=[{
            "type": "computer_use_preview",
            "display_width": 1280,
            "display_height": 800,
            "environment": "browser"
        }],
        input=[
            {
                "role": "user",
                "content": goal
            },
            {
                "type": "input_image",
                "image_url": f"data:image/png;base64,{screenshot}"
            }
        ],
        truncation="auto"
    )
    
    # Loop until the task is completed
    while True:
        # Check for computer calls
        computer_calls = [item for item in response.output if item.type == "computer_call"]
        
        if not computer_calls:
            # No more actions, task is complete
            final_messages = [item for item in response.output if item.type == "message"]
            if final_messages:
                return {"status": "completed", "message": final_messages[0].content[0].text}
            else:
                return {"status": "completed", "message": "Task completed successfully"}
        
        # Get the computer call
        computer_call = computer_calls[0]
        call_id = computer_call.call_id
        action = computer_call.action
        
        # Execute the action
        print(f"Executing action: {action.type}")
        screenshot = await execute_computer_action(page, action)
        
        # Send the updated screenshot back
        response = client.responses.create(
            model="computer-use-preview",
            previous_response_id=response.id,
            tools=[{
                "type": "computer_use_preview",
                "display_width": 1280,
                "display_height": 800,
                "environment": "browser"
            }],
            input=[
                {
                    "call_id": call_id,
                    "type": "computer_call_output",
                    "output": {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{screenshot}"
                    }
                }
            ],
            truncation="auto"
        )


async def ucalgary_library_search(browser_session, username, password, search_query):
    """Search UCalgary library using computer use"""
    page = browser_session["page"]
    
    # Form the search goal
    goal = f"""
    Please help me search for academic papers in the UCalgary library. 
    Follow these steps:
    1. Navigate to https://library.ucalgary.ca/
    2. Log in with username '{username}' and password '{password}'
    3. Navigate to the advanced search page
    4. Search for papers using the following query: {search_query}
    5. Use advanced filters to limit to peer-reviewed articles from the last 5 years
    6. Download at least 3 relevant papers
    7. Report the titles and authors of the papers you found
    """
    
    # Run the computer use loop
    result = await computer_use_loop(page, goal)
    
    # For demonstration, return mock data
    # In a real implementation, we would parse the results from the computer use
    return [
        {
            "title": "The Impact of AI on Research Methodologies",
            "authors": "Smith, J. & Johnson, A.",
            "publication": "Journal of AI Research",
            "year": 2023,
            "abstract": "This paper examines how artificial intelligence is transforming research methodologies across disciplines.",
            "url": "https://example.com/paper1",
            "pdf_url": "https://example.com/paper1.pdf",
            "downloaded": True
        },
        {
            "title": "A Comparative Analysis of Machine Learning Techniques",
            "authors": "Chen, L. & Patel, V.",
            "publication": "Computational Research",
            "year": 2022,
            "abstract": "This study compares various machine learning techniques for data analysis.",
            "url": "https://example.com/paper2",
            "pdf_url": "https://example.com/paper2.pdf",
            "downloaded": True
        },
        {
            "title": "Ethical Considerations in Automated Research",
            "authors": "Garcia, M. et al.",
            "publication": "Ethics in Technology",
            "year": 2021,
            "abstract": "This paper discusses ethical considerations when deploying automated research systems.",
            "url": "https://example.com/paper3",
            "pdf_url": "https://example.com/paper3.pdf",
            "downloaded": True
        }
    ]


async def google_drive_login(browser_session, username, password):
    """Login to Google Drive using computer use"""
    page = browser_session["page"]
    
    # Form the login goal
    goal = f"""
    Please help me log in to Google Drive. 
    Follow these steps:
    1. Navigate to https://drive.google.com/
    2. Log in with Google account username '{username}' and password '{password}'
    3. Navigate to the main Google Drive interface
    """
    
    # Run the computer use loop
    result = await computer_use_loop(page, goal)
    
    return {"status": "logged_in", "page": page}


async def create_google_doc(browser_session, title, sections=None):
    """Create a Google Doc using computer use"""
    page = browser_session["page"]
    
    if sections is None:
        sections = [
            "Title", "Abstract", "Introduction", "Literature Review", 
            "Methodology", "Results", "Discussion", "Conclusion", "References"
        ]
    
    sections_str = "\n".join([f"- {section}" for section in sections])
    
    # Form the document creation goal
    goal = f"""
    Please help me create a new Google Doc. 
    Follow these steps:
    1. Click on the "New" button in Google Drive
    2. Select "Google Docs" from the dropdown menu
    3. Wait for the new document to open
    4. Name the document "{title}"
    5. Set up the document with the following sections:
    {sections_str}
    6. Format each section as a heading and add some space below each one
    """
    
    # Run the computer use loop
    result = await computer_use_loop(page, goal)
    
    # In a real implementation, we would extract the URL from the page
    # For now, return mock data
    return {
        "id": "doc_" + "".join([c for c in title if c.isalnum()])[:10],
        "url": f"https://docs.google.com/document/d/mock_{title.replace(' ', '_')}",
        "title": title
    }


async def write_google_doc(page, document_url, content):
    """Write content to a Google Doc using computer use"""
    # Form the writing goal
    goal = f"""
    Please help me write content in a Google Doc. 
    Follow these steps:
    1. Navigate to {document_url}
    2. Wait for the document to load completely
    3. Click in the document where the content should be added
    4. Type out the following content:
    
    {content}
    
    5. Format the document appropriately with headings, paragraphs, etc.
    6. Ensure citations are properly formatted
    """
    
    # Run the computer use loop
    result = await computer_use_loop(page, goal)
    
    return {"status": "content_written"}


async def format_according_to_journal_style(browser_session, document_url, guidelines):
    """Format a Google Doc according to journal style guidelines"""
    page = browser_session["page"]
    
    # Create a formatted version of the guidelines for the computer use prompt
    formatting_instructions = f"""
    Citation Style: {guidelines.citation_style}
    Word Count Limit: {guidelines.max_word_count} words
    Formatting: {guidelines.formatting_notes}
    Reference Format: {guidelines.reference_format}
    
    Section Requirements:
    {chr(10).join([f"- {section}: {requirement}" for section, requirement in guidelines.section_requirements.items()])}
    
    Figure Requirements: {guidelines.figure_requirements or 'N/A'}
    Table Requirements: {guidelines.table_requirements or 'N/A'}
    """
    
    # Form the formatting goal
    goal = f"""
    Please help me format this Google Doc according to specific journal guidelines. 
    Follow these steps:
    1. Navigate to {document_url}
    2. Wait for the document to load completely
    3. Apply the following formatting guidelines:
    
    {formatting_instructions}
    
    4. Make sure all citations follow the {guidelines.citation_style} style
    5. Ensure the document complies with all section-specific requirements
    6. Check that figures and tables (if any) follow the journal's requirements
    7. Make sure the document doesn't exceed {guidelines.max_word_count} words
    """
    
    # Run the computer use loop
    result = await computer_use_loop(page, goal)
    
    return {"status": "formatting_applied"}
