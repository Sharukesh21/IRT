#!/usr/bin/env python3
"""Regression CLI — calls the same backend orchestrator.

Usage:
  python cli.py run --incident INC-00081
  python cli.py run --suite
  python cli.py run --commit abc123 --branch main
"""
import argparse
import asyncio
import json
import os
import sys
from datetime import datetime

import httpx

BASE_URL = os.environ.get("REGRESSION_API_URL", "http://localhost:8000/api/v1")


def log(msg: str) -> None:
    ts = datetime.utcnow().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


async def run_incident(incident_id: str, strategy: str, commit: str | None, branch: str | None) -> None:
    log(f"CI trigger received — incident={incident_id} strategy={strategy}")
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(f"{BASE_URL}/ci/regression/run", json={
            "incident_id": incident_id,
            "strategy": strategy,
            "commit_sha": commit,
            "branch": branch,
            "trigger_source": "CLI"
        })
        resp.raise_for_status()
        data = resp.json()

    log(f"Tests selected: {data.get('tests', 0)}")
    log(f"Passed: {data.get('passed', 0)} | Failed: {data.get('failed', 0)} | Errors: {data.get('errors', 0)}")
    log(f"CI STATUS: {data.get('status', 'UNKNOWN')}")

    print(json.dumps(data, indent=2))

    if data.get("status") != "PASSED":
        sys.exit(1)


async def run_suite() -> None:
    log("Running full regression suite")
    async with httpx.AsyncClient(timeout=300) as client:
        resp = await client.post(f"{BASE_URL}/regression/suite/run", json={})
        resp.raise_for_status()
        data = resp.json()
    log(f"Pass rate: {data.get('pass_rate', 0):.1f}%")
    print(json.dumps(data, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(prog="regression", description="Regression CLI")
    sub = parser.add_subparsers(dest="command")

    run_p = sub.add_parser("run", help="Run regression tests")
    run_p.add_argument("--incident", help="Incident ID (e.g. INC-00081)")
    run_p.add_argument("--suite", action="store_true", help="Run full regression suite")
    run_p.add_argument("--commit", help="Commit SHA")
    run_p.add_argument("--branch", help="Branch name")
    run_p.add_argument("--strategy", default="TARGETED", choices=["TARGETED", "FULL"])

    args = parser.parse_args()

    if args.command == "run":
        if args.suite:
            asyncio.run(run_suite())
        elif args.incident:
            asyncio.run(run_incident(args.incident, args.strategy, args.commit, args.branch))
        else:
            print("Error: provide --incident <id> or --suite")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
