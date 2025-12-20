import argparse
import requests
import json
import sys
import os

API_BASE_URL = "http://localhost:8000"

def main():
    parser = argparse.ArgumentParser(description="ArchIntel CLI - Structural Code Intelligence")
    subparsers = parser.add_subparsers(dest="command")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a repository")
    analyze_parser.add_argument("repo_url", help="Git repository URL")
    analyze_parser.add_argument("--name", help="Project name")

    # Query command
    query_parser = subparsers.add_parser("query", help="Query project architecture")
    query_parser.add_argument("project_id", help="UUID of the project")
    query_parser.add_argument("query_text", help="The question to ask")

    # List command
    subparsers.add_parser("list", help="List all projects")

    args = parser.parse_args()

    if args.command == "analyze":
        name = args.name or args.repo_url.split('/')[-1].replace('.git', '')
        response = requests.post(f"{API_BASE_URL}/projects", json={
            "name": name,
            "repo_url": args.repo_url
        })
        if response.status_code == 200:
            print(f"Successfully initialized analysis for {name}")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.text}")

    elif args.command == "query":
        # First find the repo_path for the project to satisfy the dummy implementation
        project_res = requests.get(f"{API_BASE_URL}/projects")
        projects = project_res.json().get("projects", [])
        project = next((p for p in projects if p['id'] == args.project_id), None)
        
        if not project:
            print(f"Project {args.project_id} not found.")
            return

        repo_name = project['repo_url'].split('/')[-1].replace('.git', '')
        repo_path = f"repos/{repo_name}"
        
        response = requests.post(f"{API_BASE_URL}/docs/{args.project_id}/query", json={
            "query": args.query_text,
            "repo_path": repo_path
        })
        if response.status_code == 200:
            print("\n--- ARCHINTEL INTELLIGENCE REPORT ---")
            print(response.json().get("response"))
        else:
            print(f"Error: {response.text}")

    elif args.command == "list":
        response = requests.get(f"{API_BASE_URL}/projects")
        if response.status_code == 200:
            projects = response.json().get("projects", [])
            print(f"{'ID':<40} | {'NAME':<20} | {'STATUS'}")
            print("-" * 80)
            for p in projects:
                status = p.get('status', 'active')
                print(f"{p['id']:<40} | {p['name']:<20} | {status}")
        else:
            print(f"Error: {response.text}")

if __name__ == "__main__":
    main()
