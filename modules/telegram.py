import os
import logging
import requests
from typing import Optional, Dict, Any
from contextlib import contextmanager
import urllib.parse
import gc

class TelegramSender:
    """Manages Telegram message sending with proper resource management"""

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.session = requests.Session()  # Reuse session for better performance
        self.base_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    def __del__(self):
        """Ensure session is closed on object deletion"""
        self.cleanup()

    def cleanup(self) -> None:
        """Clean up resources"""
        if hasattr(self, 'session') and self.session:
            try:
                self.session.close()
            except Exception as e:
                logging.error(f"Error closing session: {e}")

    def _prepare_message(self, msg: str) -> str:
        """Prepare and sanitize message text"""
        # Replace underscores and encode message
        sanitized_msg = msg.replace('_', ' ')
        return urllib.parse.quote(sanitized_msg)

    def _log_message(self, msg: str) -> None:
        """Log shortened version of sent message"""
        try:
            # Extract and log only the relevant part of the message
            message_preview = msg.replace('_', ' ').split('pararius.com/')[-1]
            logging.info(f"Sent message: {message_preview}")
        except Exception as e:
            logging.error(f"Error logging message: {e}")

    def send(self, msg: str = 'Test message') -> Optional[Dict[str, Any]]:
        """Send message to Telegram with proper resource management"""
        response = None

        try:
            # Prepare message parameters
            params = {
                'chat_id': self.chat_id,
                'parse_mode': 'Markdown',
                'text': msg.replace('_', ' ')  # Direct replacement without additional memory allocation
            }

            # Send request using session
            response = self.session.get(
                self.base_url,
                params=params,
                timeout=10  # Add timeout to prevent hanging
            )

            # Log message
            self._log_message(msg)

            # Return JSON response
            return response.json() if response.ok else None

        except requests.RequestException as e:
            logging.error(f"Request error: {e}")
            return None

        except Exception as e:
            logging.error(f"Error sending message: {e}")
            return None

        finally:
            # Clear response object if it exists
            if response:
                response.close()
                del response

            # Force garbage collection after sending message
            gc.collect()

@contextmanager
def telegram_sender(bot_token: str, chat_id: str):
    """Context manager for TelegramSender"""
    sender = TelegramSender(bot_token, chat_id)
    try:
        yield sender
    finally:
        sender.cleanup()

def send_text(msg: str = 'Test message',
              bot_token: str = '',
              chat_id: str = '') -> Optional[Dict[str, Any]]:
    """
    Send text message to Telegram with proper resource management

    Args:
        msg: Message to send
        bot_token: Telegram bot token
        chat_id: Telegram chat ID

    Returns:
        Optional[Dict[str, Any]]: Response from Telegram API or None if error occurs
    """
    with telegram_sender(bot_token, chat_id) as sender:
        return sender.send(msg)

def configure_logging():
    """Configure logging with proper format"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

if __name__ == "__main__":
    configure_logging()

    # Example usage with environment variables
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.getenv('TELEGRAM_CHAT_ID', '')

    result = send_text(
        msg="Test message",
        bot_token=bot_token,
        chat_id=chat_id
    )

    if result:
        print("Message sent successfully")
        print(f"Response: {result}")
    else:
        print("Failed to send message")
