import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from telethon import TelegramClient
from telethon.tl.types import Message
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TelegramNewsHandler:
    def __init__(self, api_id: str, api_hash: str, phone: str, session_path: str = None):
        """
        Initialize the Telegram client
        
        Args:
            api_id: Telegram API ID
            api_hash: Telegram API Hash
            phone: Phone number for authentication
            session_path: Path to session file (optional)
        """
        if session_path:
            # Use provided session path
            session_file = os.path.join(session_path, 'news_session')
        else:
            # Use default session file in current directory
            session_file = 'news_session'
            
        self.client = TelegramClient(session_file, api_id, api_hash)
        self.phone = phone
        
    async def start(self):
        """Start the Telegram client"""
        await self.client.start(phone=self.phone)
        
    async def stop(self):
        """Stop the Telegram client"""
        await self.client.disconnect()
        
    async def get_channel_posts(self, channel: str, duration_hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get posts from a specific channel within the specified duration
        
        Args:
            channel: Channel username or ID
            duration_hours: Number of hours to look back (default: 24)
            
        Returns:
            List of posts with their details
        """
        try:
            # Calculate the time threshold (make it timezone-aware)
            now = datetime.now().replace(tzinfo=None)
            time_threshold = now - timedelta(hours=duration_hours)
            
            posts = []
            
            # Get the entity (channel)
            entity = await self.client.get_entity(channel)
            
            # Fetch messages from the channel
            async for message in self.client.iter_messages(entity, limit=None):
                # Stop if we've gone past our time threshold
                # Convert message.date to timezone-naive for comparison
                message_date = message.date.replace(tzinfo=None)
                if message_date < time_threshold:
                    break
                    
                # Only include text messages (skip media-only posts)
                if message.text:
                    post_data = {
                        'date': message.date.isoformat(),
                        'text': message.text,
                    }
                    posts.append(post_data)
                    
            return posts
            
        except Exception as e:
            print(f"Error fetching posts from {channel}: {str(e)}")
            return []
    
    async def get_all_channel_posts(self, channels: List[str], duration_hours: int = 24) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get posts from multiple channels within the specified duration
        
        Args:
            channels: List of channel usernames or IDs
            duration_hours: Number of hours to look back (default: 24)
            
        Returns:
            Dictionary with channel names as keys and lists of posts as values
        """
        all_posts = {}
        
        for channel in channels:
            print(f"Fetching posts from {channel}...")
            posts = await self.get_channel_posts(channel, duration_hours)
            all_posts[channel] = posts
            print(f"Found {len(posts)} posts from {channel}")
            
        return all_posts

async def main():
    """Main function to demonstrate usage"""
    # Load configuration
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    phone = os.getenv('TELEGRAM_PHONE')
    
    if not all([api_id, api_hash, phone]):
        print("Please set TELEGRAM_API_ID, TELEGRAM_API_HASH, and TELEGRAM_PHONE environment variables")
        return
    
    # Load channels from sources.json
    try:
        with open('sources.json', 'r', encoding='utf-8') as f:
            sources = json.load(f)
            channels = sources.get('telegram', [])
    except FileNotFoundError:
        print("sources.json not found, using default channels")
        channels = ["@lachentyt", "@lvivych_news"]
    
    # Initialize the handler
    handler = TelegramNewsHandler(api_id, api_hash, phone)
    
    try:
        # Start the client
        await handler.start()
        print("Connected to Telegram")
        
        # Get posts from the last 24 hours (you can change this duration)
        duration_hours = 24
        all_posts = await handler.get_all_channel_posts(channels, duration_hours)
        
        # Print results
        print(f"\n=== Posts from the last {duration_hours} hours ===")
        for channel, posts in all_posts.items():
            print(f"\n{channel}: {len(posts)} posts")
            for post in posts[:3]:  # Show first 3 posts as example
                print(f"  - {post['date']}: {post['text'][:100]}...")
                
        # Save results to file
        with open('telegram_posts.json', 'w', encoding='utf-8') as f:
            json.dump(all_posts, f, ensure_ascii=False, indent=2, default=str)
        print(f"\nResults saved to telegram_posts.json")
        
    finally:
        await handler.stop()

if __name__ == "__main__":
    asyncio.run(main())
