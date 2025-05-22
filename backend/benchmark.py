#!/usr/bin/env python
"""
Dream Interpreter Backend Benchmark
This script benchmarks the performance of the dream interpretation backend.
"""

import requests
import time
import json
import statistics
import argparse
import concurrent.futures
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

# Configuration
DEFAULT_URL = "http://localhost:5000/api/interpret"
DEFAULT_ITERATIONS = 20
DEFAULT_CONCURRENCY = 4
SAMPLE_DREAMS = [
    "I was flying over a city at night, feeling free and excited.",
    "I was being chased by a large dog in a maze of dark alleys.",
    "I was swimming in crystal clear water with colorful fish all around me.",
    "I was taking an exam but realized I hadn't studied and the questions made no sense.",
    "I was in my childhood home, but the rooms were bigger and there were doors that led to unfamiliar places.",
    "I was trying to use my phone but the screen kept changing and I couldn't dial a number.",
    "I was talking to someone who I knew was dead in real life, but in the dream it seemed normal.",
    "I was driving a car and suddenly realized I was in the backseat and no one was driving.",
    "I was looking in a mirror but my reflection was distorted or looked like someone else.",
    "I was in an elevator that started moving sideways instead of up and down."
]

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Benchmark Dream Interpreter API")
    parser.add_argument("--url", default=DEFAULT_URL, help="API URL to benchmark")
    parser.add_argument("--iterations", type=int, default=DEFAULT_ITERATIONS, 
                        help="Number of iterations for each dream")
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                        help="Number of concurrent requests")
    parser.add_argument("--use-ml", action="store_true", default=True,
                        help="Use machine learning models")
    parser.add_argument("--output", default="benchmark_results.json",
                        help="Output file for benchmark results")
    parser.add_argument("--plot", action="store_true", help="Generate performance plots")
    return parser.parse_args()

def analyze_dream(url, dream_text, use_ml=True):
    """Send a dream to the API for analysis and measure response time"""
    start_time = time.time()
    try:
        response = requests.post(
            url,
            json={"dream_text": dream_text, "use_ml": use_ml},
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            # Extract model used and server-side processing time
            model_used = result.get("model_used", "unknown")
            processing_time = result.get("processing_time", "")
            if isinstance(processing_time, str) and processing_time.endswith("s"):
                processing_time = float(processing_time[:-1])
            else:
                processing_time = None
                
            return {
                "success": True,
                "response_time": response_time,
                "processing_time": processing_time,
                "model_used": model_used,
                "status_code": response.status_code
            }
        else:
            return {
                "success": False,
                "response_time": response_time,
                "error": response.text,
                "status_code": response.status_code
            }
    except Exception as e:
        return {
            "success": False,
            "response_time": time.time() - start_time,
            "error": str(e),
            "status_code": None
        }

def run_benchmark(args):
    """Run the benchmark with the specified configuration"""
    results = {}
    all_timings = []
    
    # Clear cache before running benchmark
    try:
        requests.post(args.url.replace("/interpret", "/clear-cache"))
        print("Cache cleared successfully")
    except:
        print("Warning: Failed to clear cache")
    
    print(f"Running benchmark with {args.iterations} iterations per dream at {args.concurrency} concurrency")
    print(f"Using machine learning: {args.use_ml}")
    
    for dream_idx, dream_text in enumerate(SAMPLE_DREAMS):
        dream_id = f"dream_{dream_idx + 1}"
        print(f"\nBenchmarking {dream_id}: {dream_text[:50]}...")
        
        # First pass (may include model loading time)
        print("First pass (cold start)...")
        first_result = analyze_dream(args.url, dream_text, args.use_ml)
        
        # Multi-threaded benchmark
        dream_results = []
        tasks = [dream_text] * args.iterations
        
        print(f"Running {args.iterations} iterations with {args.concurrency} concurrent requests...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as executor:
            # Use tqdm for a progress bar
            futures = [executor.submit(analyze_dream, args.url, task, args.use_ml) for task in tasks]
            for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
                result = future.result()
                dream_results.append(result)
                all_timings.append(result["response_time"])
        
        # Calculate statistics
        successful_results = [r for r in dream_results if r["success"]]
        response_times = [r["response_time"] for r in successful_results]
        processing_times = [r["processing_time"] for r in successful_results if r["processing_time"] is not None]
        
        if response_times:
            stats = {
                "cold_start": first_result["response_time"],
                "mean_response_time": statistics.mean(response_times),
                "median_response_time": statistics.median(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "stddev_response_time": statistics.stdev(response_times) if len(response_times) > 1 else 0,
                "success_rate": len(successful_results) / len(dream_results) * 100,
                "sample_count": len(dream_results),
                "model_used": successful_results[0]["model_used"] if successful_results else "unknown"
            }
            
            if processing_times:
                stats.update({
                    "mean_processing_time": statistics.mean(processing_times),
                    "median_processing_time": statistics.median(processing_times),
                    "min_processing_time": min(processing_times),
                    "max_processing_time": max(processing_times),
                })
            
            results[dream_id] = stats
            
            # Print summary for this dream
            print(f"Results for {dream_id}:")
            print(f"  Model used: {stats['model_used']}")
            print(f"  Cold start: {stats['cold_start']:.2f}s")
            print(f"  Mean response time: {stats['mean_response_time']:.2f}s")
            print(f"  Median response time: {stats['median_response_time']:.2f}s")
            print(f"  Success rate: {stats['success_rate']:.1f}%")
        else:
            print(f"No successful results for {dream_id}")
            results[dream_id] = {"error": "No successful results"}
    
    # Calculate overall statistics
    if all_timings:
        results["overall"] = {
            "mean_response_time": statistics.mean(all_timings),
            "median_response_time": statistics.median(all_timings),
            "min_response_time": min(all_timings),
            "max_response_time": max(all_timings),
            "stddev_response_time": statistics.stdev(all_timings) if len(all_timings) > 1 else 0,
            "total_requests": len(all_timings),
            "benchmark_configuration": {
                "iterations": args.iterations,
                "concurrency": args.concurrency,
                "use_ml": args.use_ml,
                "url": args.url
            }
        }
        
        print("\nOverall Results:")
        print(f"  Mean response time: {results['overall']['mean_response_time']:.2f}s")
        print(f"  Median response time: {results['overall']['median_response_time']:.2f}s")
        print(f"  Total requests: {results['overall']['total_requests']}")
    
    # Save results to file
    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nBenchmark results saved to {args.output}")
    
    return results

def generate_plots(results, args):
    """Generate performance visualization plots"""
    if not results or "overall" not in results:
        print("No results to plot")
        return
    
    # Extract dream-specific results (excluding overall)
    dream_results = {k: v for k, v in results.items() if k != "overall"}
    
    # Create figure and subplots
    plt.figure(figsize=(12, 10))
    
    # Plot 1: Mean response times by dream
    plt.subplot(2, 2, 1)
    dreams = list(dream_results.keys())
    response_times = [dream_results[d].get("mean_response_time", 0) for d in dreams]
    
    plt.bar(dreams, response_times)
    plt.title("Mean Response Time by Dream")
    plt.ylabel("Time (s)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Plot 2: Cold start vs. warm response times
    plt.subplot(2, 2, 2)
    cold_times = [dream_results[d].get("cold_start", 0) for d in dreams]
    warm_times = [dream_results[d].get("mean_response_time", 0) for d in dreams]
    
    x = np.arange(len(dreams))
    width = 0.35
    
    plt.bar(x - width/2, cold_times, width, label="Cold Start")
    plt.bar(x + width/2, warm_times, width, label="Warm Average")
    plt.title("Cold Start vs. Warm Response Times")
    plt.ylabel("Time (s)")
    plt.xticks(x, dreams, rotation=45)
    plt.legend()
    plt.tight_layout()
    
    # Plot 3: Response time distribution (box plot)
    plt.subplot(2, 2, 3)
    plt.boxplot(
        [
            [dream_results[d].get("min_response_time", 0),
             dream_results[d].get("median_response_time", 0),
             dream_results[d].get("max_response_time", 0)] 
            for d in dreams
        ],
        labels=dreams
    )
    plt.title("Response Time Distribution")
    plt.ylabel("Time (s)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Plot 4: Success rate by dream
    plt.subplot(2, 2, 4)
    success_rates = [dream_results[d].get("success_rate", 0) for d in dreams]
    plt.bar(dreams, success_rates)
    plt.title("Success Rate by Dream")
    plt.ylabel("Success Rate (%)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save the figure
    plt.savefig("benchmark_results.png")
    print("Performance plots saved to benchmark_results.png")
    
    # Optional: display the plot
    plt.show()

def main():
    """Main function to run the benchmark"""
    args = parse_args()
    results = run_benchmark(args)
    
    if args.plot:
        try:
            generate_plots(results, args)
        except Exception as e:
            print(f"Error generating plots: {e}")
    
    return results

if __name__ == "__main__":
    main() 