#!/usr/bin/env python3
"""
Schitzo Neural Router CLI Tool
Manage the neural router deployment and operations.
"""

import argparse
import subprocess
import sys
import time
import requests
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def check_health(url, timeout=30):
    """Check if a service is healthy."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(2)
    return False

def start_services():
    """Start all services using Docker Compose."""
    print("Starting Schitzo Neural Router services...")
    
    # Start core services (router + langfuse) without dashboard
    if not run_command("docker compose -f docker-compose.dev.yml up -d"):
        print("Failed to start core services")
        return False
    
    print("Waiting for core services to be healthy...")
    
    # Check Langfuse
    print("Checking Langfuse...")
    if not check_health("http://localhost:3000"):
        print("Warning: Langfuse may not be ready")
    
    # Check Router
    print("Checking Router...")
    if not check_health("http://localhost:8000"):
        print("Warning: Router may not be ready")
    
    print("Core services started successfully!")
    print("Access points:")
    print("  - Router API: http://localhost:8000")
    print("  - Langfuse: http://localhost:3000")
    print("")
    print("To start the dashboard:")
    print("  cd dashboard && npm run dev")
    print("  Dashboard will be at: http://localhost:5173")
    return True

def stop_services():
    """Stop all services."""
    print("Stopping Schitzo Neural Router services...")
    return run_command("docker compose down")

def restart_services():
    """Restart all services."""
    print("Restarting services...")
    stop_services()
    time.sleep(2)
    return start_services()

def show_logs(service=None):
    """Show logs for services."""
    if service:
        cmd = f"docker compose logs -f {service}"
    else:
        cmd = "docker compose logs -f"
    
    try:
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print("\nStopped following logs")

def show_status():
    """Show status of all services."""
    print("Service Status:")
    run_command("docker compose ps")
    
    print("\nHealth Checks:")
    
    # Router
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("  Router: [OK] Healthy")
        else:
            print("  Router: [ERROR] Unhealthy")
    except:
        print("  Router: [ERROR] Not responding")
    
    # Langfuse
    try:
        response = requests.get("http://localhost:3000/api/public/health", timeout=5)
        if response.status_code == 200:
            print("  Langfuse: [OK] Healthy")
        else:
            print("  Langfuse: [ERROR] Unhealthy")
    except:
        print("  Langfuse: [ERROR] Not responding")
    
    # Dashboard
    try:
        response = requests.get("http://localhost", timeout=5)
        if response.status_code == 200:
            print("  Dashboard: [OK] Healthy")
        else:
            print("  Dashboard: [ERROR] Unhealthy")
    except:
        print("  Dashboard: [ERROR] Not responding")

def test_router():
    """Test the router with a sample request."""
    print("Testing router with sample request...")
    
    test_payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "Hello, how are you?"}
        ]
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/v1/chat/completions",
            json=test_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("[OK] Router test successful")
            print(f"Response: {response.json()}")
        else:
            print(f"[ERROR] Router test failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"[ERROR] Router test failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Schitzo Neural Router CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Start command
    subparsers.add_parser("start", help="Start all services")
    
    # Stop command
    subparsers.add_parser("stop", help="Stop all services")
    
    # Restart command
    subparsers.add_parser("restart", help="Restart all services")
    
    # Status command
    subparsers.add_parser("status", help="Show service status")
    
    # Logs command
    logs_parser = subparsers.add_parser("logs", help="Show service logs")
    logs_parser.add_argument("service", nargs="?", help="Specific service to show logs for")
    
    # Test command
    subparsers.add_parser("test", help="Test the router")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "start":
        start_services()
    elif args.command == "stop":
        stop_services()
    elif args.command == "restart":
        restart_services()
    elif args.command == "status":
        show_status()
    elif args.command == "logs":
        show_logs(args.service)
    elif args.command == "test":
        test_router()

if __name__ == "__main__":
    main()