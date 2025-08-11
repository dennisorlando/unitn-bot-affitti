# Unitn affitti scraper

### How to run:
- obtain a telegram {app_id, api_key} pair from [https://my.telegram.org/apps](https://my.telegram.org/apps)
- copy `config.yaml.example` to `config.yaml` and populate it with the relevant values
- `docker compose up`

##### Optional:
- to run with Gemini, populate `config.yaml` with the API_KEY and, in `init.py`/`run_pipeline`, change 'ollama' to 'gemini' in `process_message(...)`.

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
