import concurrent.futures
import random
import statistics
import threading
import time, requests
from cpuinfo import get_cpu_info
from sys import exit

lock = threading.Lock()
randomTerms = ["black holes", "computer vision", "history of France", "harry potter", "climate change", "world war 2", "renewable energy"]

def load_test_api(url, session, num_requests=1000, concurrent_users=1000):
    response_times = []
    def getRandomPayload():
        return {
            "term": random.choice(randomTerms),
            "count": 10,
            "fromYear": 1700,
            "toYear": 2026,
            "includeUnknown": True,
            "authorField": "",
            "departments": []
        }
    
    def fetch():
        try:
            DelayMax = 0.5  # Max delay of 500ms between requests
            time.sleep(random.uniform(0, DelayMax))

            start_time = time.perf_counter()
            payload = getRandomPayload()
            response = session.post(url, json=payload, timeout=100)
            end_time = time.perf_counter()

            if response.ok:
                with lock:
                    response_times.append(end_time - start_time)
        except Exception as e:
            print("Error during request:", e) # Could be timeout, connection error, etc.
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        futures = [executor.submit(fetch) for _ in range(num_requests)]
        concurrent.futures.wait(futures)
    
    return response_times
if __name__ == "__main__":
    cpu_info = get_cpu_info()
    url = "http://localhost:8000/search"
    randomTermSelect = random.choice(randomTerms)

    json = {"term": randomTermSelect, "count":10, "fromYear": 1700, "toYear": 2026, "includeUnknown": True, "authorField": "", "departments": []}
    try:
        session = requests.Session()
        res = session.post(url, json=json, timeout=10)
        if res.ok:
            print("API is reachable. Starting load test...")
        else:
            print("API is not reachable. Status code:", res.status_code)
            exit(1)
    except Exception as e:
        print("Error connecting to API:", e)
        exit(1)
    with open("load_test_results.txt", "w") as f:
        f.write(f"CPU: {cpu_info['brand_raw']}\n")
        f.write(f"Frequency: {cpu_info['hz_advertised_friendly']}\n")
        f.write(f"Architecture: {cpu_info['arch']}\n")
        f.write(f"Threads: {cpu_info['count']}\n")
        f.write("\n\n")
    
    for num_users in [1, 10, 50, 100, 500, 1000, 2000]:
        start = time.perf_counter()
        print(f"Testing with {num_users} concurrent users...")
        res_times = load_test_api("http://localhost:8000/search", session, num_requests=num_users*10, concurrent_users=num_users)

        duration = time.perf_counter() - start
        print(f"Completed {num_users*10} requests in {duration:.2f} seconds")

        rps = len(res_times) / duration if duration > 0 else 0

        p95 = statistics.quantiles(res_times, n=100)[94]
        p99 = statistics.quantiles(res_times, n=100)[98]
        with open("load_test_results.txt", "a") as f:
            f.write(f"{num_users} Concurrent Users:\n")
            f.write(f"Average Response Time: {sum(res_times) / len(res_times)} seconds\n")
            f.write(f"Max Response Time: {max(res_times)} seconds\n\n")
            f.write(f"95th Percentile: {p95} seconds\n")
            f.write(f"99th Percentile: {p99} seconds\n")
            f.write(f"Requests per Second: {rps}\n")
            f.write(f"Total Duration: {duration:.2f} seconds\n")
            f.write("\n\n")