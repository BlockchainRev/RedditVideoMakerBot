#!/usr/bin/env python3
"""
Test script for Dream Analysis Integration

This script tests the dream analysis functionality independently
from the main video creation workflow. Use this to verify your
Supabase edge function is working correctly.

Usage:
    python test_dream_analysis.py
"""

import sys
from pathlib import Path

# Add the project root to the path so we can import our modules
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils import settings
from utils.dream_analysis import (
    DreamAnalyzer, 
    analyze_dream_content, 
    is_dream_analysis_enabled,
    clear_analysis_cache,
    test_dream_analysis
)
from utils.console import print_step, print_substep

def check_configuration():
    """Check if dream analysis is properly configured"""
    print_step("Checking Dream Analysis Configuration")
    
    # Load configuration
    try:
        config = settings.config.get("dream_analysis", {})
        
        enabled = config.get("enabled", False)
        supabase_url = config.get("supabase_url", "").strip()
        supabase_key = config.get("supabase_key", "").strip()
        edge_function = config.get("edge_function_name", "analyze-dream")
        
        print_substep(f"Enabled: {'✅' if enabled else '❌'} {enabled}")
        print_substep(f"Supabase URL: {'✅' if supabase_url else '❌'} {supabase_url[:50] + '...' if len(supabase_url) > 50 else supabase_url}")
        print_substep(f"Supabase Key: {'✅' if supabase_key else '❌'} {'*' * min(len(supabase_key), 20) if supabase_key else 'Not set'}")
        print_substep(f"Edge Function: {edge_function}")
        
        if not enabled:
            print_substep("Dream analysis is disabled. Enable it in config.toml", "yellow")
            return False
        
        if not supabase_url or not supabase_key:
            print_substep("Missing Supabase credentials. Please configure them in config.toml", "red")
            return False
        
        print_substep("Configuration looks good!", "green")
        return True
        
    except Exception as e:
        print_substep(f"Error checking configuration: {e}", "red")
        return False

def test_with_sample_dreams():
    """Test the analysis with sample dreams"""
    print_step("Testing Dream Analysis with Sample Dreams")
    
    sample_dreams = [
        {
            "title": "Flying Dream",
            "content": """I dreamed I was soaring high above the clouds, feeling completely free and weightless. 
            The sky was a brilliant blue and I could see the entire world spread out below me like a beautiful map. 
            I felt incredibly peaceful and powerful at the same time."""
        },
        {
            "title": "Lost in a Forest",
            "content": """I found myself walking through a dark, mysterious forest. The trees seemed to whisper secrets 
            as I passed by. I was searching for something important but couldn't remember what it was. Eventually, 
            I found a clearing with a beautiful pond that reflected the moonlight perfectly."""
        },
        {
            "title": "Childhood Home",
            "content": """I was back in my childhood home, but everything was slightly different. The rooms were 
            larger and filled with warm, golden light. My grandmother was there, even though she passed away years ago. 
            She smiled at me and handed me a key without saying a word."""
        }
    ]
    
    analyzer = DreamAnalyzer()
    successful_tests = 0
    
    for i, dream in enumerate(sample_dreams, 1):
        print_substep(f"Testing dream {i}: {dream['title']}")
        
        try:
            result = analyzer.analyze_dream(dream['content'])
            
            if result:
                print_substep(f"✅ Analysis successful! Found {len(result['sections'])} sections", "green")
                print_substep(f"   Full text length: {len(result['full_text'])} characters")
                
                # Show a preview of the analysis
                if result['sections']:
                    for section in result['sections']:
                        preview = section['content'][:100] + "..." if len(section['content']) > 100 else section['content']
                        print_substep(f"   {section['title']}: {preview}", "blue")
                
                successful_tests += 1
            else:
                print_substep("❌ Analysis returned no results", "red")
                
        except Exception as e:
            print_substep(f"❌ Analysis failed: {e}", "red")
    
    print_substep(f"Completed {successful_tests}/{len(sample_dreams)} tests successfully", 
                 "green" if successful_tests == len(sample_dreams) else "yellow")
    
    return successful_tests == len(sample_dreams)

def interactive_test():
    """Allow user to test with their own dream content"""
    print_step("Interactive Dream Analysis Test")
    
    print("Enter your dream content (press Ctrl+D or Ctrl+Z when finished):")
    print("=" * 50)
    
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    
    dream_text = "\n".join(lines).strip()
    
    if not dream_text:
        print_substep("No dream content entered", "yellow")
        return False
    
    print_substep(f"Analyzing dream ({len(dream_text)} characters)...")
    
    try:
        result = analyze_dream_content(dream_text)
        
        if result:
            print_substep("✅ Analysis completed successfully!", "green")
            print("\n" + "=" * 60)
            print("DREAM ANALYSIS RESULTS")
            print("=" * 60)
            
            for section in result['sections']:
                print(f"\n{section['title']}")
                print("-" * len(section['title']))
                print(section['content'])
            
            print(f"\nFull TTS Text ({len(result['full_text'])} characters):")
            print("-" * 40)
            print(result['full_text'])
            
            return True
        else:
            print_substep("❌ Analysis failed or returned no results", "red")
            return False
            
    except Exception as e:
        print_substep(f"❌ Analysis error: {e}", "red")
        return False

def show_menu():
    """Show the main menu"""
    print("\n" + "🌙" * 20)
    print("    DREAM ANALYSIS TESTER")
    print("🌙" * 20)
    print("\nWhat would you like to do?")
    print("1. Check configuration")
    print("2. Test with sample dreams")
    print("3. Test with your own dream")
    print("4. Clear analysis cache")
    print("5. Run all tests")
    print("6. Exit")
    
    return input("\nEnter your choice (1-6): ").strip()

def main():
    """Main test function"""
    print("Dream Analysis Integration Tester")
    print("=" * 40)
    
    # Ensure we can load settings
    try:
        # Load configuration
        directory = Path().absolute()
        config = settings.check_toml(
            f"{directory}/utils/.config.template.toml", 
            f"{directory}/config.toml"
        )
        if not config:
            print("❌ Failed to load configuration")
            return False
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return False
    
    while True:
        choice = show_menu()
        
        if choice == "1":
            check_configuration()
        
        elif choice == "2":
            if check_configuration():
                test_with_sample_dreams()
            else:
                print_substep("Please fix configuration issues first", "yellow")
        
        elif choice == "3":
            if check_configuration():
                interactive_test()
            else:
                print_substep("Please fix configuration issues first", "yellow")
        
        elif choice == "4":
            clear_analysis_cache()
        
        elif choice == "5":
            if check_configuration():
                print_step("Running All Tests")
                sample_success = test_with_sample_dreams()
                
                if sample_success:
                    print_substep("✅ All tests passed! Dream analysis is working correctly.", "green")
                else:
                    print_substep("❌ Some tests failed. Check your configuration and network connection.", "red")
            else:
                print_substep("Please fix configuration issues first", "yellow")
        
        elif choice == "6":
            print("Happy dream analyzing! 🌙✨")
            break
        
        else:
            print_substep("Invalid choice. Please enter 1-6.", "yellow")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main() 