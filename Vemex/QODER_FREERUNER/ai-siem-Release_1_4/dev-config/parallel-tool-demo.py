#!/usr/bin/env python3
"""
Demo script showing parallel tool usage capabilities
"""

import concurrent.futures
import time

def simulate_tool_call(tool_name, duration):
    """Simulate a tool call that takes some time"""
    print(f"Starting {tool_name}...")
    time.sleep(duration)
    print(f"Completed {tool_name}")
    return f"Result from {tool_name}"

def demonstrate_parallel_execution():
    """Demonstrate parallel execution of multiple tool calls"""
    
    # Define tool calls with different durations
    tool_calls = [
        ("search_codebase", 2),
        ("read_file", 1),
        ("list_dir", 0.5),
        ("grep_code", 1.5),
        ("search_symbol", 1)
    ]
    
    print("Demonstrating parallel tool execution:")
    print("=" * 40)
    
    # Execute tools in parallel
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all tool calls
        future_to_tool = {
            executor.submit(simulate_tool_call, tool_name, duration): tool_name 
            for tool_name, duration in tool_calls
        }
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_tool):
            tool_name = future_to_tool[future]
            try:
                result = future.result()
                print(f"Received result: {result}")
            except Exception as e:
                print(f"Tool {tool_name} generated an exception: {e}")
    
    end_time = time.time()
    print(f"\nAll tools completed in {end_time - start_time:.2f} seconds")

def demonstrate_sequential_execution():
    """Demonstrate sequential execution for comparison"""
    
    tool_calls = [
        ("search_codebase", 2),
        ("read_file", 1),
        ("list_dir", 0.5),
        ("grep_code", 1.5),
        ("search_symbol", 1)
    ]
    
    print("\n\nDemonstrating sequential tool execution:")
    print("=" * 40)
    
    start_time = time.time()
    
    # Execute tools sequentially
    for tool_name, duration in tool_calls:
        result = simulate_tool_call(tool_name, duration)
        print(f"Received result: {result}")
    
    end_time = time.time()
    print(f"\nAll tools completed in {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    demonstrate_parallel_execution()
    demonstrate_sequential_execution()
    
    print("\n\nConclusion:")
    print("Parallel execution can significantly reduce total execution time")
    print("when multiple independent tool calls are needed.")