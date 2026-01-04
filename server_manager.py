"""
Server Manager
Utilities to start and stop HTTP and HTTPS backend servers as subprocesses
"""
import subprocess
import sys
import os
import signal
import time
import requests


class ServerManager:
    """Manages HTTP and HTTPS backend servers"""
    
    def __init__(self, http_port=8081, https_port=8082):
        self.http_port = http_port
        self.https_port = https_port
        self.http_process = None
        self.https_process = None
        
    def start_http_server(self):
        """Start HTTP server as subprocess"""
        print(f"[Server Manager] Starting HTTP server on port {self.http_port}...")
        try:
            self.http_process = subprocess.Popen(
                [sys.executable, 'server_http.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            # Wait a bit for server to start
            time.sleep(2)
            
            # Check if server is actually running
            if self.is_http_running():
                print(f"[Server Manager] ✓ HTTP server started (PID: {self.http_process.pid})")
                return True
            else:
                print("[Server Manager] ✗ HTTP server failed to start")
                return False
        except Exception as e:
            print(f"[Server Manager] ✗ Error starting HTTP server: {e}")
            return False
    
    def start_https_server(self):
        """Start HTTPS server as subprocess"""
        print(f"[Server Manager] Starting HTTPS server on port {self.https_port}...")
        try:
            self.https_process = subprocess.Popen(
                [sys.executable, 'server_https.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            # Wait a bit for server to start
            time.sleep(2)
            
            # Check if server is actually running
            if self.is_https_running():
                print(f"[Server Manager] ✓ HTTPS server started (PID: {self.https_process.pid})")
                return True
            else:
                print("[Server Manager] ✗ HTTPS server failed to start")
                return False
        except Exception as e:
            print(f"[Server Manager] ✗ Error starting HTTPS server: {e}")
            return False
    
    def is_http_running(self):
        """Check if HTTP server is responding"""
        try:
            response = requests.get(
                f'http://localhost:{self.http_port}/insecure/register',
                timeout=2
            )
            return response.status_code < 500
        except:
            return False
    
    def is_https_running(self):
        """Check if HTTPS server is responding"""
        try:
            response = requests.get(
                f'https://localhost:{self.https_port}/secure/register',
                timeout=2,
                verify=False  # Self-signed certificate
            )
            return response.status_code < 500
        except:
            return False
    
    def stop_http_server(self):
        """Stop HTTP server"""
        if self.http_process:
            print(f"[Server Manager] Stopping HTTP server (PID: {self.http_process.pid})...")
            try:
                self.http_process.terminate()
                self.http_process.wait(timeout=5)
                print("[Server Manager] ✓ HTTP server stopped")
            except subprocess.TimeoutExpired:
                print("[Server Manager] Force killing HTTP server...")
                self.http_process.kill()
                self.http_process.wait()
            except Exception as e:
                print(f"[Server Manager] Error stopping HTTP server: {e}")
            finally:
                self.http_process = None
    
    def stop_https_server(self):
        """Stop HTTPS server"""
        if self.https_process:
            print(f"[Server Manager] Stopping HTTPS server (PID: {self.https_process.pid})...")
            try:
                self.https_process.terminate()
                self.https_process.wait(timeout=5)
                print("[Server Manager] ✓ HTTPS server stopped")
            except subprocess.TimeoutExpired:
                print("[Server Manager] Force killing HTTPS server...")
                self.https_process.kill()
                self.https_process.wait()
            except Exception as e:
                print(f"[Server Manager] Error stopping HTTPS server: {e}")
            finally:
                self.https_process = None
    
    def stop_all(self):
        """Stop all servers"""
        self.stop_http_server()
        self.stop_https_server()
    
    def wait_for_servers(self, timeout=10):
        """Wait for both servers to be ready"""
        print("[Server Manager] Waiting for servers to be ready...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            http_ready = self.is_http_running()
            https_ready = self.is_https_running()
            
            if http_ready and https_ready:
                print("[Server Manager] ✓ Both servers are ready!")
                return True
            
            time.sleep(0.5)
        
        print("[Server Manager] ⚠️  Timeout waiting for servers")
        return False


def setup_signal_handlers(server_manager):
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        print("\n[Server Manager] Received shutdown signal, stopping servers...")
        server_manager.stop_all()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

