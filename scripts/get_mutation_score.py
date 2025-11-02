#!/usr/bin/env python3
"""Get mutation testing score from mutmut results."""

import json
import sys
from pathlib import Path

def get_mutation_score():
    """Calculate mutation score from mutmut cache."""
    cache_file = Path(".mutmut-cache")
    
    if not cache_file.exists():
        print("⚠️  Mutmut cache not found. Run 'mutmut run' first.")
        return None
    
    try:
        with open(cache_file) as f:
            data = json.load(f)
        
        # Count mutants (keys starting with 'mut')
        mutant_keys = [k for k in data.keys() if k.startswith('mut')]
        total = len(mutant_keys)
        
        # Count survived (status == 'survived')
        survived = sum(
            1 for v in data.values() 
            if isinstance(v, dict) and v.get('status') == 'survived'
        )
        
        killed = total - survived
        score = (killed / total * 100) if total > 0 else 0
        
        print(f"📊 Mutation Testing Score:")
        print(f"   Total mutants: {total}")
        print(f"   Killed: {killed}")
        print(f"   Survived: {survived}")
        print(f"   Score: {score:.2f}%")
        
        return {
            'total': total,
            'killed': killed,
            'survived': survived,
            'score': score
        }
        
    except Exception as e:
        print(f"❌ Error reading cache: {e}")
        return None

if __name__ == "__main__":
    get_mutation_score()

