import argparse
import json
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path

# File: app/autoscaler/autoscaler.py
# parents[0] = autoscaler
# parents[1] = app
# parents[2] = project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROMETHEUS_URL = "http://localhost:9090"

MIN_REPLICAS = 3
MAX_REPLICAS = 10

SCALE_UP_THRESHOLD = 70.0
SCALE_DOWN_THRESHOLD = 30.0

CHECK_INTERVAL = 10
COOLDOWN_SECONDS = 30

SCALE_UP_CHECKS = 2

SCALE_DOWN_CHECKS = 3

CPU_QUERY = """
100 * avg(
  rate(container_cpu_usage_seconds_total{
    container_label_com_docker_compose_service="app",
    cpu="total"
  }[1m])
)
"""


def query_prometheus(query):
    params = urllib.parse.urlencode({"query": query})
    url = f"{PROMETHEUS_URL}/api/v1/query?{params}"

    with urllib.request.urlopen(url, timeout=5) as response:
        payload = json.loads(response.read().decode("utf-8"))

    if payload.get("status") != "success":
        raise RuntimeError(f"Prometheus query failed: {payload}")

    return payload["data"]["result"]


def get_cpu_usage():
    result = query_prometheus(CPU_QUERY)

    if not result:
        raise RuntimeError(
            "No app CPU metrics returned. Check "
            "http://localhost:9090/targets and verify cAdvisor metrics."
        )

    return float(result[0]["value"][1])


def get_replica_count():
    result = subprocess.run(
        [
            "docker",
            "compose",
            "ps",
            "--status",
            "running",
            "-q",
            "app",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    # FIX: len() requires a sized object, so use a list comprehension.
    running_containers = [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip()
    ]

    return len(running_containers)


def scale_app(replicas, dry_run):
    command = [
        "docker",
        "compose",
        "up",
        "-d",
        "--scale",
        f"app={replicas}",
        "app",
    ]

    if dry_run:
        print(f"[DRY RUN] Would execute: {' '.join(command)}")
        return

    print(f"[ACTION] Scaling app to {replicas} replicas")

    subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=True,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Automatically scale Flask containers using CPU metrics."
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Enable real scaling. Without this flag, simulate scaling.",
    )

    args = parser.parse_args()
    dry_run = not args.apply

    print("Local Container Platform Autoscaler")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE SCALING'}")
    print(f"Replica limits: {MIN_REPLICAS}-{MAX_REPLICAS}")
    print("Press Ctrl+C to stop.\n")

    high_checks = 0
    low_checks = 0
    last_scaling_time = 0.0

    while True:
        try:
            cpu = get_cpu_usage()
            replicas = get_replica_count()

            print(
                f"Average app CPU: {cpu:.2f}% | "
                f"Replicas: {replicas} | "
                f"Mode: {'DRY RUN' if dry_run else 'LIVE'}"
            )

            # Track sustained high or low CPU usage.
            if cpu > SCALE_UP_THRESHOLD:
                high_checks += 1
                low_checks = 0

            elif cpu < SCALE_DOWN_THRESHOLD:
                low_checks += 1
                high_checks = 0

            else:
                high_checks = 0
                low_checks = 0

            cooldown_complete = (
                time.monotonic() - last_scaling_time
                >= COOLDOWN_SECONDS
            )

            if not cooldown_complete:
                print("[INFO] Waiting for cooldown.")

            elif (
                high_checks >= SCALE_UP_CHECKS
                and replicas < MAX_REPLICAS
            ):
                scale_app(replicas + 1, dry_run)
                high_checks = 0
                low_checks = 0
                last_scaling_time = time.monotonic()

            elif (
                low_checks >= SCALE_DOWN_CHECKS
                and replicas > MIN_REPLICAS
            ):
                scale_app(replicas - 1, dry_run)
                high_checks = 0
                low_checks = 0
                last_scaling_time = time.monotonic()

            elif (
                replicas >= MAX_REPLICAS
                and high_checks >= SCALE_UP_CHECKS
            ):
                print("[INFO] Maximum replica count reached.")
                high_checks = 0

            elif (
                replicas <= MIN_REPLICAS
                and low_checks >= SCALE_DOWN_CHECKS
            ):
                print("[INFO] Minimum replica count reached.")
                low_checks = 0

        except Exception as error:
            print(f"[ERROR] {type(error).__name__}: {error}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAutoscaler stopped.")




# Condition	Decision

# CPU above 70% for 3 consecutive checks    	Add 1 replica
# CPU below 30% for 4 consecutive checks	    Remove 1 replica
# CPU between 30% and 70%	                    Maintain current count
# Current replicas = 3	                        Never scale down further
# Current replicas = 10	                        Never scale up further
# After a scaling decision                     	Wait 60 seconds before another




# python app/autoscaler/autoscaler.py  Dry run (simulate scaling decisions without applying changes)


# python app/autoscaler/autoscaler.py --apply  Live mode (apply scaling decisions to the app service)