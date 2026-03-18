"""
Example: Deploy a web application using Novita Artifact Hosting SDK

This script demonstrates how to:
1. Create a sandbox from a template
2. Create or reuse a project
3. Deploy the application with environment variables
4. Monitor deployment status via callback

Usage:
    python app.py --template ecomm-with-sql --project-name ecomm-with-sql --project-dir ecomm-with-sql
"""
import argparse
import logging
import os
import sys
from pathlib import Path

import dotenv
dotenv.load_dotenv()

from novita_sandbox.code_interpreter import Sandbox
from novita_sandbox.artifact_hosting import DeploymentClient, DeploymentStatus, DeploymentError, is_successful


# ========== Configuration ==========
parser = argparse.ArgumentParser(description="Deploy a web application using Novita Artifact Hosting SDK")
parser.add_argument("--template", type=str, required=True, help="Sandbox template name")
parser.add_argument("--project-name", type=str, required=True, help="Project name for deployment URL")
parser.add_argument("--project-dir", type=str, required=True, help="Project directory containing Dockerfile")
parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging (DEBUG)")
parser.add_argument(
    "--log-level",
    choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    default=None,
    help="Log level (default: no logging, -v is equivalent to DEBUG)"
)
parser.add_argument(
    "--http-port",
    type=int,
    default=3000,
    help="HTTP port the application listens on (default: 3000, use 80 for Nginx)"
)
parser.add_argument(
    "--sandbox-timeout",
    type=int,
    default=600,
    help="Sandbox timeout in seconds, default 600"
)
args = parser.parse_args()

if args.verbose:
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
elif args.log_level:
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

TEMPLATE_NAME = args.template
PROJECT_NAME = args.project_name

ARTI_DIR = "/app"

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = args.project_dir
DOCKERFILE_PATH = SCRIPT_DIR / PROJECT_DIR / "Dockerfile"

API_KEY = os.environ.get("NOVITA_API_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")

ENVIRONMENT_VARIABLES = {
    "NODE_ENV": "production",
    "DATABASE_URL": os.getenv("DATABASE_URL", ""),
    "OAUTH_SERVER_URL": os.getenv("OAUTH_SERVER_URL", ""),
    "OAUTH_API_SERVER_URL": os.getenv("OAUTH_API_SERVER_URL", ""),
    "APP_SECRET": os.getenv("APP_SECRET", ""),
}

ENVIRONMENT_VARIABLES = {k: v for k, v in ENVIRONMENT_VARIABLES.items() if v}


def main():
    if not API_KEY:
        print("❌ Please set NOVITA_API_KEY environment variable")
        sys.exit(1)

    if not DOCKERFILE_PATH.exists():
        print(f"❌ Dockerfile not found: {DOCKERFILE_PATH}")
        sys.exit(1)

    dockerfile_content = DOCKERFILE_PATH.read_text()

    print("=" * 60)
    print("🚀 Starting deployment")
    print("=" * 60)
    print(f"   Template: {TEMPLATE_NAME}")
    print(f"   Project: {PROJECT_NAME}")
    print(f"   Dockerfile: {DOCKERFILE_PATH}")
    print(f"   Environment variables: {list(ENVIRONMENT_VARIABLES.keys())}")
    print()

    sandbox = None

    try:
        # Step 1: Create Sandbox from template
        print("📦 Step 1: Creating Sandbox...")
        sandbox = Sandbox.create(template=TEMPLATE_NAME, timeout=args.sandbox_timeout)
        full_sandbox_id = sandbox.sandbox_id
        sandbox_id = full_sandbox_id.split("-")[0] if "-" in full_sandbox_id else full_sandbox_id
        print(f"✅ Sandbox created: {full_sandbox_id} -> Using ID: {sandbox_id}")

        print("🗑️  Cleaning build context...")
        sandbox.commands.run(f"sudo rm -rf {ARTI_DIR}/node_modules {ARTI_DIR}/.env {ARTI_DIR}/dist {ARTI_DIR}/.git")
        print("✅ Build context cleaned")
        print()

        # Step 2: Deploy to Artifact Hosting
        with DeploymentClient(api_key=API_KEY) as client:
            print("🔍 Step 2: Setting up project...")
            project = None

            for p in client.list_projects():
                if p.name == PROJECT_NAME:
                    project = p
                    print(f"✅ Found existing project: {project.id}")
                    break

            if project is None:
                print(f"📝 Creating new project: {PROJECT_NAME}")
                project = client.create_project(
                    name=PROJECT_NAME,
                    description="Deployed via Novita Artifact Hosting",
                )
                print(f"✅ Project created: {project.id}")

            print()

            # Step 3: Deploy
            print("🚀 Step 3: Deploying...")

            def on_status_change(deployment):
                print(f"   📍 Status changed: {deployment.status.name}")

            deployment = project.deploy(
                sandbox_id=sandbox_id,
                arti_dir=ARTI_DIR,
                dockerfile=dockerfile_content,
                message="Deployment via SDK",
                environment_variables=ENVIRONMENT_VARIABLES,
                http_port=args.http_port,
                check_health_path="/",
                wait=True,
                on_status_change=on_status_change,
            )

            print()
            if is_successful(deployment.status):
                print("=" * 60)
                print("🎉 Deployment successful!")
                print("=" * 60)
                print(f"   Deployment ID: {deployment.id}")
                print(f"   Status: {deployment.status.name}")
                print()

                project = client.get_project(project.id)
                if project.endpoint and project.endpoint.default_url:
                    print("🌐 Access application:")
                    print(f"   {project.endpoint.default_url}")
                else:
                    print(f"⚠️  URL not retrieved (endpoint: {project.endpoint})")
            else:
                print(f"❌ Deployment failed: {deployment.status.name}")
                if deployment.error_message:
                    print(f"   Error: {deployment.error_message}")

                print()
                print("📋 Deployment Logs:")
                print("-" * 60)
                try:
                    for log in deployment.stream_logs():
                        print(log.message)
                except Exception as log_err:
                    print(f"⚠️  Failed to stream logs: {log_err}")
                print("-" * 60)
                sys.exit(1)

    except DeploymentError as e:
        print(f"❌ Deployment failed: {e}")
        print()
        print("📋 Deployment Logs:")
        print("-" * 60)
        try:
            with DeploymentClient(api_key=API_KEY) as client:
                for p in client.list_projects():
                    if p.name == PROJECT_NAME:
                        for dep in p.list_deployments():
                            print(f"Streaming logs for deployment: {dep.id}")
                            print()
                            for log in dep.stream_logs():
                                print(log.message)
                            break
                        break
        except Exception as log_err:
            print(f"⚠️  Failed to stream logs: {log_err}")
        print("-" * 60)
        sys.exit(1)

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        if sandbox:
            print()
            print("🧹 Cleaning up Sandbox...")
            try:
                sandbox.kill()
                print("✅ Sandbox cleaned up")
            except Exception as e:
                print(f"⚠️  Failed to cleanup Sandbox: {e}")


if __name__ == "__main__":
    main()
