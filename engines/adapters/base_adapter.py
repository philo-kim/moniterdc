"""
Base adapter interface for content collection
All source adapters must implement this interface
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ParsedContent:
    """Parsed content from any source"""
    url: str
    source_id: str
    title: str
    body: str
    metadata: Dict
    published_at: Optional[datetime] = None

class BaseAdapter(ABC):
    """Base class for all source adapters"""

    @property
    @abstractmethod
    def source_type(self) -> str:
        """Source type identifier (e.g., 'dc_gallery', 'youtube')"""
        pass

    @abstractmethod
    async def fetch(self, **params) -> List[Dict]:
        """
        Fetch raw content from source

        Args:
            **params: Source-specific parameters

        Returns:
            List of raw content dictionaries
        """
        pass

    @abstractmethod
    def parse(self, raw: Dict) -> ParsedContent:
        """
        Parse raw content into standard format

        Args:
            raw: Raw content dictionary

        Returns:
            ParsedContent object
        """
        pass

    @abstractmethod
    def get_credibility(self) -> float:
        """
        Get base credibility score for this source type

        Returns:
            Float between 0-1
        """
        pass