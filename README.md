# Telegram News Handler

A simple Telethon script that fetches posts from Telegram channels within a specified duration.

## Features

- Fetch posts from multiple Telegram channels
- Configurable time duration (default: 24 hours)
- Automatic loading of channels from `sources.json`
- Saves results to JSON file
- Handles authentication and session management

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Telegram API Credentials

1. Go to https://my.telegram.org/apps
2. Create a new application
3. Note down your `api_id` and `api_hash`

### 3. Set Environment Variables

Create a `.env` file in the project root:

```env
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE=your_phone_number_here
```

### 4. Configure Channels

Edit `sources.json` to include your target channels:

```json
{
  "telegram": [
    "@channel1",
    "@channel2",
    "channel_id_or_username"
  ]
}
```

## Usage

### Basic Usage

```bash
python news_handler.py
```

This will:
- Load channels from `sources.json`
- Fetch posts from the last 24 hours
- Save results to `telegram_posts.json`

### Programmatic Usage

```python
import asyncio
from news_handler import TelegramNewsHandler

async def main():
    handler = TelegramNewsHandler(api_id, api_hash, phone)
    await handler.start()
    
    # Get posts from specific channels for last 12 hours
    channels = ["@channel1", "@channel2"]
    posts = await handler.get_all_channel_posts(channels, duration_hours=12)
    
    await handler.stop()

asyncio.run(main())
```

## Output Format

The script returns a dictionary with channel names as keys and lists of posts as values:

```json
{
  "@channel1": [
    {
      "channel": "@channel1",
      "message_id": 123,
      "date": "2024-01-01T12:00:00",
      "text": "Post content...",
      "views": 1000,
      "forwards": 5,
      "replies": 10
    }
  ]
}
```

## Notes

- The script only fetches text messages (skips media-only posts)
- Authentication requires your phone number for the first run
- Results are saved to `telegram_posts.json` by default
- The script handles rate limiting automatically 