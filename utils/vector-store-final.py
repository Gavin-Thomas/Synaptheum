import os
from openai import OpenAI
from typing import List, Dict, Any

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def create_paper_vector_store(papers):
    """Create a vector store from a list of papers"""
    # Create a new vector store
    vector_store = client.vector_stores.create(
        name="Research Papers"
    )
    
    # For each paper, create a file and add to vector store
    for paper in papers:
        # In a real implementation, we would process the PDF
        # For now, we'll create a text representation
        paper_content = f"""
        Title: {paper['title']}
        Authors: {paper['authors']}
        Publication: {paper.get('publication', 'Unknown Journal')}
        Year: {paper.get('year', 'N/A')}
        
        Abstract: {paper.get('abstract', 'No abstract available.')}
        
        This is a placeholder for the full content of the paper.
        In a real implementation, this would be the extracted text from the PDF.
        """
        
        # Create a temporary file
        temp_file_path = f"temp_paper_{papers.index(paper)}.txt"
        with open(temp_file_path, "w", encoding="utf-8") as f:
            f.write(paper_content)
        
        # Upload to OpenAI as a file
        with open(temp_file_path, "rb") as f:
            file = client.files.create(
                file=f,
                purpose="vector_store"
            )
        
        # Add to vector store
        client.vector_stores.files.create_and_poll(
            vector_store_id=vector_store.id,
            file_id=file.id,
            attributes={
                "title": paper["title"],
                "authors": paper["authors"],
                "year": paper.get("year", 0),
                "publication": paper.get("publication", "Unknown")
            }
        )
        
        # Clean up temporary file
        os.remove(temp_file_path)
    
    return vector_store.id


async def search_papers(vector_store_id, query):
    """Search for relevant papers in the vector store"""
    results = client.vector_stores.search(
        vector_store_id=vector_store_id,
        query=query,
        max_num_results=5
    )
    
    # Process and return the results
    relevant_papers = []
    for result in results.data:
        # Extract paper data from results
        paper = {
            "title": result.attributes.get("title", "Unknown Title"),
            "authors": result.attributes.get("authors", "Unknown Authors"),
            "year": result.attributes.get("year", 0),
            "publication": result.attributes.get("publication", "Unknown"),
            "content": "\n".join([c.text for c in result.content]) if result.content else "",
            "relevance_score": result.score,
            "file_id": result.file_id
        }
        relevant_papers.append(paper)
    
    return relevant_papers
