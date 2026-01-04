#!/usr/bin/env python3
"""
Main Entry Point - Reverse Proxy Architecture
Starts all three servers:
1. HTTP server (port 8081) - insecure routes
2. HTTPS server (port 8082) - secure routes  
3. Proxy server (port 8080) - routes traffic
"""
import sys
import os
import time
from server_manager import ServerManager, setup_signal_handlers
from proxy import app, HTTP_SERVER_URL, HTTPS_SERVER_URL

def check_ssl_certificates():
    """Check if SSL certificates exist"""
    cert_path = 'ssl/cert.pem'
    key_path = 'ssl/key.pem'
    
    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        print("=" * 60)
        print("⚠️  SSL certificates not found!")
        print("=" * 60)
        print("HTTPS server requires SSL certificates.")
        print("Run './generate_cert.sh' to generate them.")
        print("=" * 60)
        return False
    return True

def main():
    """Main function to start all servers"""
    print("=" * 60)
    print("Secure Computing Project - Reverse Proxy Architecture")
    print("=" * 60)
    print("\nThis will start 3 servers:")
    print("  1. HTTP Server (port 8081) - Insecure routes")
    print("  2. HTTPS Server (port 8082) - Secure routes")
    print("  3. Proxy Server (port 8080) - Routes traffic")
    print("\n" + "=" * 60)
    
    # Check SSL certificates
    if not check_ssl_certificates():
        print("\nCannot start without SSL certificates. Exiting.")
        sys.exit(1)
    
    # Create server manager
    server_manager = ServerManager(http_port=8081, https_port=8082)
    
    # Setup signal handlers for graceful shutdown
    setup_signal_handlers(server_manager)
    
    try:
        # Start HTTP server
        if not server_manager.start_http_server():
            print("\n✗ Failed to start HTTP server. Exiting.")
            sys.exit(1)
        
        # Start HTTPS server
        if not server_manager.start_https_server():
            print("\n✗ Failed to start HTTPS server. Exiting.")
            server_manager.stop_all()
            sys.exit(1)
        
        # Wait for servers to be ready
        if not server_manager.wait_for_servers(timeout=10):
            print("\n⚠️  Servers may not be fully ready, but continuing...")
        
        # Print status
        print("\n" + "=" * 60)
        print("All servers started successfully!")
        print("=" * 60)
        print("\nAccess the application at:")
        print("  → http://localhost:8080  (Proxy - main entry point)")
        print("\nBackend servers:")
        print(f"  → {HTTP_SERVER_URL}  (HTTP - insecure routes)")
        print(f"  → {HTTPS_SERVER_URL}  (HTTPS - secure routes)")
        print("\n⚠️  Browser will show security warning for HTTPS")
        print("   This is expected for self-signed certificates.")
        print("\nPress Ctrl+C to stop all servers")
        print("=" * 60 + "\n")
        
        # Start proxy server (runs in main process)
        app.run(debug=False, host='0.0.0.0', port=8080, threaded=True)
        
    except KeyboardInterrupt:
        print("\n\n[Main] Shutting down...")
    except Exception as e:
        print(f"\n[Main] Error: {e}")
    finally:
        # Cleanup
        print("\n[Main] Stopping all servers...")
        server_manager.stop_all()
        print("[Main] All servers stopped. Goodbye!")

if __name__ == '__main__':
    main()

