"""
Natural language query parser for attribute-based search.

This module provides simple keyword-based NLP parsing for search queries.
"""
import re
from typing import Optional

from loguru import logger


class NLPParser:
    """Natural language query parser for person attribute search."""

    # Color vocabulary mapping
    COLOR_MAP = {
        "red": "red",
        "blue": "blue",
        "navy": "blue",
        "black": "black",
        "white": "white",
        "gray": "gray",
        "grey": "gray",
        "green": "green",
        "yellow": "yellow",
        "brown": "brown",
        "pink": "pink",
        "orange": "orange",
        "purple": "purple",
        "beige": "brown",
        "tan": "brown",
        "khaki": "brown",
    }

    # Upper body keywords
    UPPER_KEYWORDS = [
        "shirt", "top", "jacket", "coat", "hoodie", "sweater",
        "blouse", "t-shirt", "tshirt", "upper", "torso", "vest",
        "cardigan", "blazer", "polo"
    ]

    # Lower body keywords
    LOWER_KEYWORDS = [
        "pants", "trousers", "jeans", "shorts", "skirt", "bottom",
        "lower", "legs", "slacks", "leggings", "joggers"
    ]

    def parse_query(self, query_text: str) -> dict[str, Optional[str]]:
        """
        Extract attributes from natural language query.

        Examples:
        - "male wearing red shirt" -> {gender: "male", upper_color: "red"}
        - "person with blue pants" -> {lower_color: "blue"}
        - "female with black top and white bottom" ->
            {gender: "female", upper_color: "black", lower_color: "white"}

        Args:
            query_text: Natural language search query

        Returns:
            Dictionary with extracted attributes
        """
        query_lower = query_text.lower().strip()
        logger.debug(f"Parsing query: {query_text}")

        result = {
            "gender": self._extract_gender(query_lower),
            "upper_color": self._extract_upper_color(query_lower),
            "lower_color": self._extract_lower_color(query_lower),
        }

        logger.info(f"Parsed query '{query_text}' -> {result}")
        return result

    def _extract_gender(self, query: str) -> Optional[str]:
        """Extract gender from query."""
        # Check for explicit gender mentions
        if re.search(r'\b(man|male|boy|guy|gentleman)\b', query):
            if not re.search(r'\b(woman|female|girl|lady)\b', query):
                return "male"

        if re.search(r'\b(woman|female|girl|lady)\b', query):
            return "female"

        return None

    def _extract_upper_color(self, query: str) -> Optional[str]:
        """Extract upper body clothing color."""
        # First, try to find color near upper body keywords
        for keyword in self.UPPER_KEYWORDS:
            if keyword in query:
                # Look for color before or after the keyword
                pattern = rf'(\w+)\s+{keyword}|{keyword}\s+(?:in\s+)?(\w+)'
                match = re.search(pattern, query)
                if match:
                    potential_color = match.group(1) or match.group(2)
                    if potential_color in self.COLOR_MAP:
                        return self.COLOR_MAP[potential_color]

        # Try pattern: "wearing [color]" or "[color] wearing"
        wearing_pattern = r'wearing\s+(?:a\s+)?(\w+)|(\w+)\s+(?:shirt|top)'
        match = re.search(wearing_pattern, query)
        if match:
            color = match.group(1) or match.group(2)
            if color in self.COLOR_MAP:
                return self.COLOR_MAP[color]

        return None

    def _extract_lower_color(self, query: str) -> Optional[str]:
        """Extract lower body clothing color."""
        # Look for color near lower body keywords
        for keyword in self.LOWER_KEYWORDS:
            if keyword in query:
                # Look for color before the keyword
                pattern = rf'(\w+)\s+{keyword}'
                match = re.search(pattern, query)
                if match:
                    potential_color = match.group(1)
                    if potential_color in self.COLOR_MAP:
                        return self.COLOR_MAP[potential_color]

        return None


# Global singleton instance
_parser_instance: NLPParser | None = None


def get_nlp_parser() -> NLPParser:
    """Get or create the NLP parser singleton."""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = NLPParser()
    return _parser_instance


def parse_query(query_text: str) -> dict[str, Optional[str]]:
    """Convenience function to parse a query."""
    return get_nlp_parser().parse_query(query_text)
