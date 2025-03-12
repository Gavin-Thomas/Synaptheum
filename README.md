# ResearchBot: Academic Research Assistant

ResearchBot is a comprehensive research assistant application that automates your entire academic workflow using OpenAI's Agents SDK and Computer Use capabilities.

## Features

- **Research Question Analysis**: Breaks down complex research questions into searchable components
- **UCalgary Library Integration**: Automatically logs in, searches for papers, and downloads relevant results
- **Paper Screening**: Evaluates and selects the most relevant papers for your research
- **Google Drive Integration**: Creates and organizes research documents automatically
- **Academic Writing**: Generates well-structured content with proper citations
- **Journal Recommendations**: Suggests appropriate journals for publication
- **Journal-Specific Formatting**: Formats papers according to target journal style guidelines

## Setup Instructions

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/research-assistant.git
   cd research-assistant
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Playwright browsers:
   ```bash
   playwright install
   ```

4. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

5. (Optional) Update credentials in `main.py` if needed

## Usage

Run the main script and enter your research question when prompted:

```bash
python main.py
```

The application will:
1. Analyze your research question
2. Search the UCalgary library for relevant papers
3. Screen and select the most appropriate papers
4. Create a structured Google Doc
5. Write a complete academic paper
6. Format according to journal guidelines (if specified)
7. Recommend journals for publication

## Security Note

This application requires your UCalgary and Google credentials. For security, you may want to:
1. Update the security.py file to use a secure credential store
2. Run the application in a sandboxed environment
3. Reset any passwords after using the application

## Requirements

- Python 3.8+
- OpenAI API key with access to GPT-4o and Computer Use preview
- UCalgary library credentials
- Google account credentials
