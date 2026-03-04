import concurrent.futures
import time, requests
from cpuinfo import get_cpu_info
from sys import exit
def load_test_api(url, json, num_requests=1000, concurrent_users=1000):
    response_times = []
    
    def fetch():
        start_time = time.time()
        response = requests.post(url, json=json)
        end_time = time.time()
        response_times.append(end_time - start_time)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        futures = [executor.submit(fetch) for _ in range(num_requests)]
        concurrent.futures.wait(futures)
    
    return response_times

if __name__ == "__main__":
    cpu_info = get_cpu_info()
    url = "http://localhost:8000/search"
    json = {"term": "black holes", "count":10, "fromYear": 1700, "toYear": 2026, "includeUnknown": True, "authorField": "", "departments": []}
    try:
        res = requests.post(url, json=json, timeout=5)
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
    
    for num_users in [1,10, 50, 100, 500, 1000]:
        print(f"Testing with {num_users} concurrent users...")
        res_times = load_test_api("http://localhost:8000/search", json=json, num_requests=num_users*10, concurrent_users=num_users)
        with open("load_test_results.txt", "a") as f:
            f.write(f"{num_users} Concurrent Users:\n")
            f.write(f"Average Response Time: {sum(res_times) / len(res_times)} seconds\n")
            f.write(f"Max Response Time: {max(res_times)} seconds\n\n")
            f.write("\n\n")