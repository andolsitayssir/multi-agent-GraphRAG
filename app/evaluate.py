import time
import sys
import os

# Ensure we can import from the current directory
sys.path.append(".")
from agent import ask_agent

# Define Test Scenarios
scenarios = [
    {
        "name": "Specific Book Search",
        "query": "Who wrote The Storm?",
        "expected_keywords": ["Leo Harding", "Storm Chaser","Children of the Storm",],
        "type": "retrieval"
    },
    {
        "name": "Topic/Genre Search",
        "query": "Do you have any books about space?",
        "expected_keywords": ["Edge of Tomorrow", "Mapping the Stars", "The Quantum Key", "The Memory Paradox","Reborn Skies"],
        "type": "retrieval"
    },
    {
        "name": "General Knowledge/Stats",
        "query": "How many books are in the database?",
        "expected_keywords": ["56", "books"],
        "type": "tool_usage"
    },
    {
        "name": "Author Search (Fuzzy)",
        "query": "Find books by Samira Hadded",
        "expected_keywords": ["Love Beyond Walls", "Samira Haddad"],
        "type": "retrieval"
    }
]

def run_evaluation():
    
    results = []
    
    for scenario in scenarios:
       
        print(f"Query: {scenario['query']}")
        
        start_time = time.time()
        try:
            response = ask_agent(scenario['query'])
            success = True
            error = None
        except Exception as e:
            response = str(e)
            success = False
            error = str(e)
        end_time = time.time()
        
        latency = end_time - start_time
        
        # Check accuracy
        passed = False
        if success:
            missing_keywords = [k for k in scenario['expected_keywords'] if k.lower() not in response.lower()]
            accuracy = 1 - (len(missing_keywords) / len(scenario['expected_keywords']))
            if not missing_keywords:
                passed = True
            else:
                print(f" Missed keywords: {missing_keywords}")
        
        print(f"Response: {response}")
        print(f"Latency: {latency:.4f}s")
        print(f"Result: {'PASS' if passed else ' FAIL'}")
        print("\n")
        
        results.append({
            "scenario": scenario['name'],
            "latency": latency,
            "passed": passed,
            "accuracy": accuracy,
            "response": response
        })

    # Summary
if __name__ == "__main__":
    run_evaluation()

