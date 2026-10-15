import argparse
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

def send_requests(worker_id, deadline, base_url):
    completed = 0
    failed = 0
    first_error_printed = False

    while time.monotonic() < deadline:
        url = f"{base_url}/work?duration=0.5"
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "LocalContainerPlatform-LoadGenerator"},
            )
            with urllib.request.urlopen(request, timeout=5) as response:
                response.read()
                if response.status == 200:
                    completed += 1
                else:
                    failed += 1
        except (urllib.error.URLError, TimeoutError, OSError, Exception) as error:
            failed += 1
            if not first_error_printed:
                print(f"Worker {worker_id} first error: {error!r}")
                first_error_printed = True
            # Avoid flooding the terminal if the target is unreachable.
            time.sleep(0.2)

    return worker_id, completed, failed

def main():
    parser = argparse.ArgumentParser(
        description="Generate bounded test traffic for the local platform."
    )
    parser.add_argument("--duration", type=int, default=60)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--url", default="http://localhost")
    args = parser.parse_args()

    duration = max(10, min(args.duration, 180))
    workers = max(1, min(args.workers, 12))
    base_url = args.url.rstrip("/")

    print("Local Container Platform - Load Generator")
    print(f"Target: {base_url}/work")
    print(f"Duration: {duration} seconds")
    print(f"Concurrent workers: {workers}")
    print("Starting load test... Press Ctrl+C to stop.\n")

    # Fail quickly and clearly if the endpoint is unavailable.
    try:
        with urllib.request.urlopen(f"{base_url}/health", timeout=3) as response:
            print(f"Health check: HTTP {response.status}\n")
    except Exception as error:
        raise SystemExit(
            f"Cannot reach {base_url}/health ({error}). "
            "Start Docker Compose and test http://localhost/health first."
        )

    deadline = time.monotonic() + duration
    try:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [
                executor.submit(send_requests, i + 1, deadline, base_url)
                for i in range(workers)
            ]
            totals = [future.result() for future in futures]

        successful = sum(item[1] for item in totals)
        failed = sum(item[2] for item in totals)
        for worker_id, completed, errors in totals:
            print(f"Worker {worker_id}: {completed} successful, {errors} failed")
        print("\nLoad test finished.")
        print(f"Successful requests: {successful}")
        print(f"Failed requests: {failed}")
    except KeyboardInterrupt:
        print("\nLoad test interrupted.")

if __name__ == "__main__":
    main()


# python app/load-generator/load_generator.py --duration 90 --workers 8