# Telegram News Handler

A FastAPI application that fetches posts from Telegram channels within a specified duration.

## Features

- Fetch posts from multiple Telegram channels via REST API
- Configurable time duration (default: 24 hours)
- Bearer token authentication
- Docker deployment with session persistence
- Session management tools for setup and reset

## Setup

### 1. Get Telegram API Credentials

1. Go to https://my.telegram.org/apps
2. Create a new application
3. Note down your `api_id` and `api_hash`

### 2. Set Environment Variables

Create a `.env` file in the project root:

```env
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE=your_phone_number_here
API_TOKEN=your_secure_api_token_here
```

## API Usage

### Start the API Server

```bash
# Install dependencies
pip install -r requirements.txt

# Start the API
python api.py
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### POST /fetch-news

Fetch posts from Telegram channels with authentication.

**Headers:**
```
Authorization: Bearer your_api_token_here
```

**Request Body:**
```json
{
  "channels": ["@channel1", "@channel2"],
  "duration_hours": 24
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "@channel1": [
      {
        "date": "2024-01-01T12:00:00",
        "text": "Post content..."
      }
    ]
  },
  "message": "Successfully fetched posts from 2 channels"
}
```



## Docker Deployment

### Prerequisites

1. Install Docker and Docker Compose
2. Set up your `.env` file with all required variables

### Quick Start with Docker

```bash
# Build and start the container
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop the container
docker-compose down
```

### Session Management

The Docker setup includes session persistence and management tools:

#### First-time Setup (Interactive)
```bash
# Set up session interactively (you'll need to enter phone code)
docker-compose run --rm telegram-api python session_manager.py setup /app/sessions
```

#### Reset Session (if needed)
```bash
# Reset existing session
docker-compose run --rm telegram-api python session_manager.py reset /app/sessions
```

#### Session Persistence

- Session files are stored in a Docker volume (`telegram_sessions`)
- Sessions persist across container restarts
- To completely reset, remove the volume: `docker-compose down -v`

### Docker Commands

```bash
# Build image
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f telegram-api

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# Access container shell
docker-compose exec telegram-api bash
```

### Environment Variables for Docker

Your `.env` file should contain:
```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=your_phone_number
API_TOKEN=your_secure_api_token
```

## Notes

- The API only fetches text messages (skips media-only posts)
- Authentication requires your phone number for the first run
- The API handles rate limiting automatically
- API requires Bearer token authentication
- Session files are persisted in Docker volumes 