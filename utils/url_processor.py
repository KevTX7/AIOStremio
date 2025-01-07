import base64
import os
from typing import Dict, Optional
from urllib.parse import urlencode

import aiohttp
from cryptography.fernet import Fernet
from fastapi import HTTPException

from utils.cache import cached_decorator
from utils.config import config
from utils.logger import logger


class URLProcessor:
    def __init__(self, encryption_key: bytes):
        self.fernet = Fernet(encryption_key)
        self.addon_url = config.addon_url
        self.mediaflow_api_key = os.getenv("MEDIAFLOW_API_KEY")

    async def _generate_mediaflow_url(self, url: str) -> str:
        """Generate an encrypted MediaFlow URL."""
        params = {
            "mediaflow_proxy_url": config.mediaflow_url,
            "endpoint": "/proxy/stream",
            "destination_url": url,
            "query_params": {},
            "request_headers": {
                "referer": config.addon_url,
                "origin": config.addon_url,
            },
            "response_headers": {},
            "expiration": 2592000,
            "api_password": self.mediaflow_api_key,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config.mediaflow_url}/generate_encrypted_or_encoded_url", json=params
            ) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=500, detail="Failed to generate MediaFlow URL"
                    )
                data = await response.json()
                logger.info(f"Generated MediaFlow URL: {data['encoded_url']}")
                return data["encoded_url"]

    async def process_stream_urls(
        self, streams: Dict[str, list], user_path: str, proxy_enabled: bool
    ) -> None:
        """Process URLs in streams, encrypting them if proxy is enabled."""
        for stream in streams:
            if "url" in stream and proxy_enabled:
                if config.mediaflow_enabled and config.mediaflow_url:
                    # Use MediaFlow URL encryption
                    try:
                        mediaflow_url = await self._generate_mediaflow_url(
                            stream["url"]
                        )
                        stream["url"] = mediaflow_url
                    except Exception as e:
                        logger.error(f"Failed to generate MediaFlow URL: {str(e)}")
                        streams.remove(stream)
                        continue
                else:
                    encrypted_url = self.fernet.encrypt(stream["url"].encode()).decode()
                    safe_encrypted_url = base64.urlsafe_b64encode(
                        encrypted_url.encode()
                    ).decode()
                    proxy_url = (
                        f"{self.addon_url}/{user_path}/proxy/{safe_encrypted_url}"
                    )
                    logger.info(f"Generated proxy URL: {proxy_url}")
                    stream["url"] = proxy_url

    def decrypt_url(self, encrypted_url: str) -> str:
        """Decrypt an encrypted URL."""
        try:
            # Add padding if needed
            padding_needed = len(encrypted_url) % 4
            if padding_needed:
                encrypted_url += "=" * (4 - padding_needed)

            decoded_url = base64.urlsafe_b64decode(encrypted_url.encode()).decode()
            original_url = self.fernet.decrypt(decoded_url.encode()).decode()
            return original_url

        except Exception as e:
            logger.error(f"URL processing error: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid URL format")
