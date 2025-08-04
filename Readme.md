# Unitn affitti scraper

### Architecture:
- mongodb database with:
  - list of chats to scrape
  - messages of chats already downloaded
  - list of available chats?
- API endpoint to start syncing chats
  - starts downloading one at a time without duplicates
- ollama endpoint running a small llm model
- API endpoint to analyze messages with langchain:
  - price (with/out *bollette*)
  - location
  - single / double room
  - 
