"""
Deploy a web application using Novita Artifact Hosting SDK.

Usage:
    python app.py --template ecomm-with-sql --project-name ecomm-with-sql --dockerfile ecomm-with-sql/Dockerfile
    python app.py --template snake-game-static --project-name snake-game --dockerfile snake-game-static/Dockerfile --http-port 80
"""
import argparse
import logging
import os
import sys
from pathlib import Path

import dotenv
dotenv.load_dotenv()

from novita_sandbox.code_interpreter import Sandbox
from novita_sandbox.artifact_hosting import DeploymentClient, is_successful

SCRIPT_DIR = Path(__file__).parent
ARTI_DIR = "/app"

ENV_KEYS = ["NODE_ENV", "DATABASE_URL", "OAUTH_SERVER_URL", "OAUTH_API_SERVER_URL", "APP_SECRET"]


def parse_args():
    parser = argparse.ArgumentParser(description="Deploy via Novita Artifact Hosting SDK")
    parser.add_argument("--template", required=True, help="Sandbox template name")
    parser.add_argument("--project-name", required=True, help="Project name for deployment URL")
    parser.add_argument("--dockerfile", required=True, help="Path to Dockerfile (relative to this script)")
    parser.add_argument("--http-port", type=int, default=3000, help="HTTP port (default: 3000, use 80 for Nginx)")
    parser.add_argument("--sandbox-timeout", type=int, default=600, help="Sandbox timeout in seconds (default: 600)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    return parser.parse_args()


def get_env_variables():
    env = {"NODE_ENV": "production"}
    for key in ENV_KEYS:
        val = os.getenv(key, "")
        if val:
            env[key] = val
    return env


def find_or_create_project(client, name):
    for p in client.list_projects():
        if p.name == name:
            print(f"  Found existing project: {p.id}")
            return p

    project = client.create_project(name=name, description="Deployed via Novita Artifact Hosting")
    print(f"  Created new project: {project.id}")
    return project


def stream_failure_logs(deployment):
    print("\nDeployment Logs:")
    print("-" * 40)
    try:
        for log in deployment.stream_logs():
            print(log.message)
    except Exception as e:
        print(f"  Failed to stream logs: {e}")
    print("-" * 40)


def main():
    args = parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(name)s %(levelname)s %(message)s")

    api_key = os.environ.get("NOVITA_API_KEY")
    if not api_key:
        print("Error: NOVITA_API_KEY environment variable is not set")
        sys.exit(1)

    dockerfile_path = SCRIPT_DIR / args.dockerfile
    if not dockerfile_path.exists():
        print(f"Error: Dockerfile not found: {dockerfile_path}")
        sys.exit(1)

    dockerfile_content = dockerfile_path.read_text()
    env_vars = get_env_variables()

    print(f"Deploying [{args.project_name}] with template [{args.template}]")
    print(f"  Dockerfile: {dockerfile_path}")
    print(f"  HTTP port: {args.http_port}")
    print(f"  Env vars: {list(env_vars.keys())}")

    sandbox = None
    try:
        # Step 1: Create sandbox
        print("\n[1/3] Creating sandbox...")
        sandbox = Sandbox.create(template=args.template, timeout=args.sandbox_timeout)
        full_id = sandbox.sandbox_id
        sandbox_id = full_id.split("-")[0] if "-" in full_id else full_id
        print(f"  Sandbox ready: {sandbox_id}")

        sandbox.commands.run(f"sudo rm -rf {ARTI_DIR}/node_modules {ARTI_DIR}/.env {ARTI_DIR}/dist {ARTI_DIR}/.git")

        # Step 2: Find or create project
        print("\n[2/3] Setting up project...")
        with DeploymentClient(api_key=api_key) as client:
            project = find_or_create_project(client, args.project_name)

            # Step 3: Deploy
            print("\n[3/3] Deploying...")
            deployment = project.deploy(
                sandbox_id=sandbox_id,
                arti_dir=ARTI_DIR,
                dockerfile=dockerfile_content,
                message="Deployment via SDK",
                environment_variables=env_vars,
                http_port=args.http_port,
                check_health_path="/",
                wait=True,
                on_status_change=lambda d: print(f"  Status: {d.status.name}"),
            )

            if is_successful(deployment.status):
                project = client.get_project(project.id)
                url = getattr(project.endpoint, "default_url", None) if project.endpoint else None
                print(f"\nDeployment successful! (ID: {deployment.id})")
                if url:
                    print(f"  URL: {url}")
            else:
                print(f"\nDeployment failed: {deployment.status.name}")
                if deployment.error_message:
                    print(f"  Error: {deployment.error_message}")
                stream_failure_logs(deployment)
                sys.exit(1)

    except Exception as e:
        print(f"\nError: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

    finally:
        if sandbox:
            try:
                sandbox.kill()
                print("\nSandbox cleaned up.")
            except Exception:
                pass


if __name__ == "__main__":
    main()
