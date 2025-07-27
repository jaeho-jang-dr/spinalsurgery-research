#!/usr/bin/env python3
"""
Generate sample papers for lumbar fusion research
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.sample_papers_generator import sample_generator

def main():
    """Run the sample paper generator"""
    try:
        print("Generating sample papers for lumbar fusion 2-year outcomes...")
        print("-" * 60)
        
        # Generate and save papers
        folder_path, papers = sample_generator.save_papers_to_folder()
        
        print("-" * 60)
        print("Sample papers generated successfully!")
        print(f"Total papers: {len(papers)}")
        print(f"Papers with full text: {sum(1 for p in papers if p['has_full_text'])}")
        
    except Exception as e:
        print(f"Error generating papers: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()