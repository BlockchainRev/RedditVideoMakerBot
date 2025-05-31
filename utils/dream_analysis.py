"""
Dream Analysis Module for Reddit Video Maker Bot

This module handles integration with lucidrem.com's dream analysis system
via Supabase edge functions. It provides dream analysis functionality
including symbol interpretation, emotional analysis, and meaning extraction.

Features:
- Supabase edge function integration
- Response caching to avoid duplicate API calls
- Comprehensive error handling and fallbacks
- Text processing and formatting for video integration
- Configurable analysis types (symbols, emotions, meanings)
"""

import hashlib
import json
import os
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import requests
from rich.console import Console

from utils import settings
from utils.console import print_step, print_substep

console = Console()

# Cache directory for storing analysis results
CACHE_DIR = Path("assets/temp/analysis_cache")

class DreamAnalysisError(Exception):
    """Custom exception for dream analysis errors"""
    pass


class DreamAnalyzer:
    """Main class for handling dream analysis via Supabase edge functions"""
    
    def __init__(self):
        """Initialize the dream analyzer with configuration settings"""
        self.config = settings.config.get("dream_analysis", {})
        self.enabled = self.config.get("enabled", False)
        self.supabase_url = self.config.get("supabase_url", "").strip()
        self.supabase_key = self.config.get("supabase_key", "").strip()
        self.edge_function_name = self.config.get("edge_function_name", "analyze-dream")
        self.timeout = self.config.get("timeout_seconds", 30)
        self.cache_enabled = self.config.get("cache_analysis", True)
        
        # Analysis options
        self.include_symbols = self.config.get("include_symbols", True)
        self.include_emotions = self.config.get("include_emotions", True)
        self.include_meanings = self.config.get("include_meanings", True)
        self.max_length = self.config.get("max_analysis_length", 800)
        self.voice_style = self.config.get("analysis_voice_style", "analytical")
        
        # Create cache directory if it doesn't exist
        if self.cache_enabled:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    def is_configured(self) -> bool:
        """Check if dream analysis is properly configured"""
        if not self.enabled:
            return False
        
        if not self.supabase_url or not self.supabase_key:
            print_substep("Dream analysis is enabled but Supabase credentials are missing", "yellow")
            return False
        
        return True
    
    def _generate_cache_key(self, dream_text: str) -> str:
        """Generate a unique cache key for the dream text"""
        # Create a hash of the dream text and configuration
        content = f"{dream_text}_{self.include_symbols}_{self.include_emotions}_{self.include_meanings}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cached_analysis(self, cache_key: str) -> Optional[Dict]:
        """Retrieve cached analysis if it exists"""
        if not self.cache_enabled:
            return None
        
        cache_file = CACHE_DIR / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                
                # Check if cache is not too old (24 hours)
                cache_age = time.time() - cached_data.get("timestamp", 0)
                if cache_age < 86400:  # 24 hours in seconds
                    print_substep("Using cached dream analysis", "green")
                    return cached_data.get("analysis")
                else:
                    # Remove old cache
                    cache_file.unlink()
            except (json.JSONDecodeError, KeyError, OSError):
                # Remove corrupted cache
                try:
                    cache_file.unlink()
                except OSError:
                    pass
        
        return None
    
    def _save_to_cache(self, cache_key: str, analysis: Dict) -> None:
        """Save analysis result to cache"""
        if not self.cache_enabled:
            return
        
        cache_file = CACHE_DIR / f"{cache_key}.json"
        
        try:
            cache_data = {
                "timestamp": time.time(),
                "analysis": analysis
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
        except OSError as e:
            print_substep(f"Failed to save analysis to cache: {e}", "yellow")
    
    def _create_dream_in_database(self, dream_text: str) -> Optional[str]:
        """
        First step: Create the dream in the database using Supabase REST API
        Returns the dream ID if successful, None if failed
        """
        if not self.supabase_url.endswith('/'):
            self.supabase_url += '/'
        
        # Use Supabase REST API to insert into dreams table
        dreams_url = f"{self.supabase_url}rest/v1/dreams"
        
        headers = {
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "apikey": self.supabase_key,
            "Prefer": "return=representation"  # Return the created record
        }
        
        # Generate a proper UUID for dream ID
        dream_id = str(uuid.uuid4())
        
        # Use the specific user ID for reddit_video_bot
        user_id = "bcd3a8e1-fa17-4c8d-93c2-1dce29c8d211"
        
        # Prepare payload for dreams table insertion with correct schema
        payload = {
            "id": dream_id,
            "user_id": user_id,
            "title": "Dream from Reddit Video Bot",
            "description": dream_text.strip(),  # This is the correct field name
            "category": "normal",  # Lowercase enum value
            "emotion": "neutral",   # Lowercase enum value  
            "is_public": False      # Keep bot dreams private by default
        }
        
        try:
            print_substep("Creating dream in database...", "blue")
            
            response = requests.post(
                dreams_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            result = response.json()
            
            # Supabase returns an array of created records
            if isinstance(result, list) and len(result) > 0:
                created_dream_id = result[0].get("id", dream_id)
            else:
                created_dream_id = dream_id
            
            print_substep("Dream created successfully in database", "green")
            return created_dream_id
            
        except requests.exceptions.HTTPError as e:
            error_text = ""
            try:
                error_detail = e.response.json()
                error_text = f": {error_detail}"
            except:
                error_text = f": {e.response.text}"
            
            print_substep(f"Failed to create dream: HTTP {e.response.status_code}{error_text}", "red")
            return None
        except Exception as e:
            print_substep(f"Failed to create dream: {e}", "red")
            return None

    def _get_dream_content(self, dream_id: str) -> Optional[str]:
        """
        Fetch dream content from database by ID
        """
        if not self.supabase_url.endswith('/'):
            self.supabase_url += '/'
        
        # Use Supabase REST API to get the dream description (not content)
        dream_url = f"{self.supabase_url}rest/v1/dreams?id=eq.{dream_id}&select=description"
        
        headers = {
            "Authorization": f"Bearer {self.supabase_key}",
            "apikey": self.supabase_key
        }
        
        try:
            response = requests.get(dream_url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("description")  # Updated field name
            
            return None
            
        except Exception as e:
            print_substep(f"Failed to fetch dream content: {e}", "red")
            return None

    def _analyze_existing_dream(self, dream_id: str, user_id: str) -> Dict:
        """
        Second step: Analyze an existing dream by ID
        """
        # First, fetch the dream content from the database
        dream_content = self._get_dream_content(dream_id)
        
        if not dream_content:
            raise DreamAnalysisError(f"Could not fetch dream content for ID {dream_id}")
        
        if not self.supabase_url.endswith('/'):
            self.supabase_url += '/'
        
        # Construct the edge function URL
        edge_url = f"{self.supabase_url}functions/v1/{self.edge_function_name}"
        
        headers = {
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "apikey": self.supabase_key
        }
        
        # Include dream content as required by the current edge function
        payload = {
            "dreamContent": dream_content,
            "dreamId": dream_id,
            "userId": user_id
        }
        
        try:
            print_substep("Analyzing existing dream with lucidrem.com system...", "blue")
            
            response = requests.post(
                edge_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            result = response.json()
            
            # Validate response structure
            if not isinstance(result, dict):
                raise DreamAnalysisError("Invalid response format from analysis API")
            
            print_substep("Dream analysis completed successfully", "green")
            return result
            
        except requests.exceptions.Timeout:
            raise DreamAnalysisError(f"Analysis request timed out after {self.timeout} seconds")
        
        except requests.exceptions.ConnectionError:
            raise DreamAnalysisError("Failed to connect to dream analysis service")
        
        except requests.exceptions.HTTPError as e:
            error_text = ""
            try:
                error_detail = e.response.json()
                error_text = f": {error_detail}"
            except:
                error_text = f": {e.response.text}"
            
            if e.response.status_code == 401:
                raise DreamAnalysisError("Invalid Supabase credentials for dream analysis")
            elif e.response.status_code == 404:
                raise DreamAnalysisError(f"Edge function '{self.edge_function_name}' not found")
            else:
                raise DreamAnalysisError(f"HTTP error {e.response.status_code}{error_text}")
        
        except requests.exceptions.RequestException as e:
            raise DreamAnalysisError(f"Request failed: {str(e)}")
        
        except json.JSONDecodeError:
            raise DreamAnalysisError("Invalid JSON response from analysis API")

    def _call_supabase_edge_function(self, dream_text: str) -> Dict:
        """
        Updated method: Two-step process for dream creation and analysis
        """
        user_id = "bcd3a8e1-fa17-4c8d-93c2-1dce29c8d211"
        
        # Step 1: Create the dream in the database
        dream_id = self._create_dream_in_database(dream_text)
        
        if not dream_id:
            raise DreamAnalysisError("Failed to create dream in database")
        
        # Step 2: Analyze the dream
        return self._analyze_existing_dream(dream_id, user_id)

    def _prepare_analysis_request(self, dream_text: str) -> Dict:
        """
        DEPRECATED: This method is now replaced by the two-step process
        Keeping it for backward compatibility but it won't be used
        """
        # Generate a proper UUID for dream ID
        dream_id = str(uuid.uuid4())
        
        # Use the specific user ID created in the database for reddit_video_bot
        user_id = "bcd3a8e1-fa17-4c8d-93c2-1dce29c8d211"
        
        return {
            "dreamContent": dream_text.strip(),
            "dreamId": dream_id,
            "userId": user_id
        }

    def _format_analysis_for_video(self, analysis_data: Dict) -> Dict:
        """Format the analysis data for video creation"""
        
        # Extract the analysis object from the response
        analysis = analysis_data.get("analysis", analysis_data)
        
        formatted = {
            "title": "🌙 Dream Analysis",
            "sections": [],
            "full_text": "",
            "metadata": {
                "rating": analysis.get("rating", 0),
                "themes": analysis.get("themes", []),
                "symbols": analysis.get("symbols", []),
                "emotions": analysis.get("emotions", [])
            }
        }
        
        # Create sections based on the analysis content
        if self.include_symbols and analysis.get("symbols"):
            symbols = analysis["symbols"]
            if symbols:
                symbols_text = f"Key symbols in your dream include: {', '.join(symbols)}"
                formatted["sections"].append({
                    "type": "symbols",
                    "title": "🔮 Symbolic Meanings",
                    "content": symbols_text
                })
        
        if self.include_emotions and analysis.get("emotions"):
            emotions = analysis["emotions"]
            if emotions:
                emotions_text = f"Emotional themes present: {', '.join(emotions)}"
                formatted["sections"].append({
                    "type": "emotions",
                    "title": "💭 Emotional Analysis",
                    "content": emotions_text
                })
        
        if self.include_meanings and analysis.get("interpretation"):
            interpretation = analysis["interpretation"]
            if interpretation and interpretation.strip():
                formatted["sections"].append({
                    "type": "interpretation",
                    "title": "✨ Dream Interpretation",
                    "content": interpretation.strip()
                })
        
        # If no specific sections were created, use the interpretation as general analysis
        if not formatted["sections"] and analysis.get("interpretation"):
            formatted["sections"].append({
                "type": "general",
                "title": "🌙 Dream Analysis",
                "content": analysis["interpretation"]
            })
        
        # Create combined full text for TTS
        if formatted["sections"]:
            text_parts = []
            for section in formatted["sections"]:
                text_parts.append(f"{section['title']}: {section['content']}")
            formatted["full_text"] = " ".join(text_parts)
        
        # Truncate if too long
        if len(formatted["full_text"]) > self.max_length:
            formatted["full_text"] = formatted["full_text"][:self.max_length - 3] + "..."
            # Also truncate the last section accordingly
            if formatted["sections"]:
                remaining_length = self.max_length - sum(
                    len(f"{s['title']}: {s['content']} ") 
                    for s in formatted["sections"][:-1]
                )
                if remaining_length > 0:
                    last_section = formatted["sections"][-1]
                    title_length = len(f"{last_section['title']}: ")
                    max_content_length = remaining_length - title_length - 3
                    if max_content_length > 0:
                        last_section["content"] = last_section["content"][:max_content_length] + "..."
        
        return formatted
    
    def analyze_dream(self, dream_text: str) -> Optional[Dict]:
        """
        Analyze a dream and return formatted results
        
        Args:
            dream_text (str): The dream content to analyze
            
        Returns:
            Optional[Dict]: Formatted analysis data or None if analysis fails/disabled
        """
        # Check if analysis is enabled and configured
        if not self.is_configured():
            return None
        
        # Clean and validate dream text
        dream_text = dream_text.strip()
        if len(dream_text) < 50:  # Too short to analyze meaningfully
            print_substep("Dream text too short for analysis (minimum 50 characters)", "yellow")
            return None
        
        if len(dream_text) > 5000:  # Truncate very long dreams
            print_substep("Dream text truncated to 5000 characters for analysis", "yellow")
            dream_text = dream_text[:5000]
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(dream_text)
            cached_analysis = self._get_cached_analysis(cache_key)
            
            if cached_analysis:
                return self._format_analysis_for_video(cached_analysis)
            
            # Call the analysis API
            analysis_result = self._call_supabase_edge_function(dream_text)
            
            # Save to cache
            self._save_to_cache(cache_key, analysis_result)
            
            # Format for video creation
            formatted_analysis = self._format_analysis_for_video(analysis_result)
            
            return formatted_analysis
            
        except DreamAnalysisError as e:
            print_substep(f"Dream analysis failed: {e}", "red")
            return None
        
        except Exception as e:
            print_substep(f"Unexpected error during dream analysis: {e}", "red")
            return None


# Global analyzer instance
_analyzer = None

def get_dream_analyzer() -> DreamAnalyzer:
    """Get the global dream analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = DreamAnalyzer()
    return _analyzer


def analyze_dream_content(dream_text: str) -> Optional[Dict]:
    """
    Convenience function to analyze dream content
    
    Args:
        dream_text (str): The dream content to analyze
        
    Returns:
        Optional[Dict]: Formatted analysis data or None if analysis fails/disabled
    """
    analyzer = get_dream_analyzer()
    return analyzer.analyze_dream(dream_text)


def is_dream_analysis_enabled() -> bool:
    """Check if dream analysis is enabled and properly configured"""
    analyzer = get_dream_analyzer()
    return analyzer.is_configured()


def clear_analysis_cache() -> None:
    """Clear all cached analysis results"""
    if CACHE_DIR.exists():
        try:
            for cache_file in CACHE_DIR.glob("*.json"):
                cache_file.unlink()
            print_substep("Dream analysis cache cleared", "green")
        except OSError as e:
            print_substep(f"Failed to clear analysis cache: {e}", "yellow")
    else:
        print_substep("No analysis cache to clear", "blue")


# Example usage and testing functions
def test_dream_analysis():
    """Test function for dream analysis functionality"""
    test_dream = """
    I dreamed I was flying over a vast ocean under a full moon. The water was crystal clear and I could see 
    colorful fish swimming below. Suddenly, I landed on a small island with a single tree. Under the tree 
    was a golden key that seemed to glow with its own light. When I picked it up, I woke up feeling peaceful 
    and hopeful.
    """
    
    print("Testing dream analysis functionality...")
    analyzer = get_dream_analyzer()
    
    if not analyzer.is_configured():
        print("Dream analysis is not configured. Please set up Supabase credentials.")
        return False
    
    result = analyzer.analyze_dream(test_dream)
    
    if result:
        print("✅ Dream analysis test successful!")
        print(f"Analysis sections: {len(result['sections'])}")
        print(f"Full text length: {len(result['full_text'])}")
        return True
    else:
        print("❌ Dream analysis test failed")
        return False


if __name__ == "__main__":
    # Run test when module is executed directly
    test_dream_analysis() 