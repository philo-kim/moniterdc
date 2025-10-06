"""
Embedding utilities using OpenAI
"""

import os
from typing import List
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class EmbeddingGenerator:
    """Generate embeddings using OpenAI"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "text-embedding-3-small"
        self.dimensions = 1536

    async def generate(self, text: str) -> List[float]:
        """
        Generate embedding for text

        Args:
            text: Text to embed

        Returns:
            List of floats (1536 dimensions)
        """
        response = await self.client.embeddings.create(
            model=self.model,
            input=text,
            dimensions=self.dimensions
        )

        return response.data[0].embedding

    async def generate_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts

        Args:
            texts: List of texts to embed

        Returns:
            List of embeddings
        """
        response = await self.client.embeddings.create(
            model=self.model,
            input=texts,
            dimensions=self.dimensions
        )

        return [data.embedding for data in response.data]

# Global instance
_embedding_generator = None

def get_embedding_generator() -> EmbeddingGenerator:
    """Get or create embedding generator instance"""
    global _embedding_generator
    if _embedding_generator is None:
        _embedding_generator = EmbeddingGenerator()
    return _embedding_generator