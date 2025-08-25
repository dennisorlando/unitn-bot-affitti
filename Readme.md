# Unitn affitti scraper

### How to run:
- Run `./init_telegram.py` and follow the CLI instructions to allow access to the telegram chats
- Run `docker compose up`
- access the frontend at `localhost:3000`, and add the chats to "sniff" using the settings button in the bottom left.
- then, from the frontend:
  - press `Sync Messages` to fetch the messages from the Telegram chats
  - press `Process Messages` to process the messages (and extract useful features) using Ollama LLM (it will probably spin up your fans)
  - when finished (or while processing, if you want incomplete results), press the "refresh" button in the toolbar to update the list of processed rental announcements
  - Voila'! You can now navigate, filter and sort the rental announcements

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
