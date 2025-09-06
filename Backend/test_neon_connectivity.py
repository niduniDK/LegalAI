#!/usr/bin/env python3
"""
Test Neon database connectivity and status
"""
import requests
import time
import socket

def test_neon_api():
    """Test if we can reach Neon's API"""
    print("🌐 Testing Neon API connectivity...")
    try:
        response = requests.get("https://console.neon.tech/api/v2/projects", timeout=10)
        print(f"✅ Neon API reachable (Status: {response.status_code})")
        return True
    except Exception as e:
        print(f"❌ Cannot reach Neon API: {e}")
        return False

def test_dns_resolution():
    """Test DNS resolution for the database host"""
    hostname = "ep-wandering-rice-a14f00h6-pooler.ap-southeast-1.aws.neon.tech"
    print(f"🔍 Testing DNS resolution for {hostname}...")
    
    try:
        ips = socket.gethostbyname_ex(hostname)
        print(f"✅ DNS resolved to IPs: {ips[2]}")
        return True
    except Exception as e:
        print(f"❌ DNS resolution failed: {e}")
        return False

def test_tcp_connection():
    """Test raw TCP connection to database"""
    hostname = "ep-wandering-rice-a14f00h6-pooler.ap-southeast-1.aws.neon.tech"
    port = 5432
    print(f"🔌 Testing TCP connection to {hostname}:{port}...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)  # 10 second timeout
        result = sock.connect_ex((hostname, port))
        sock.close()
        
        if result == 0:
            print("✅ TCP connection successful")
            return True
        else:
            print(f"❌ TCP connection failed (Error code: {result})")
            return False
    except Exception as e:
        print(f"❌ TCP connection error: {e}")
        return False

def suggest_solutions():
    """Provide troubleshooting suggestions"""
    print("\n🛠️  Troubleshooting suggestions:")
    print("1. 🌙 Neon databases auto-sleep - try waking it up via Neon Console")
    print("2. 🔥 Check Windows Firewall settings")
    print("3. 🌐 Try using a VPN if on corporate network")
    print("4. 📍 Verify the database branch is active in Neon Console")
    print("5. 🔑 Check if the database credentials are correct")
    print("6. 🏥 Check Neon status page: https://neonstatus.com/")

if __name__ == "__main__":
    print("🚀 Neon Database Connectivity Diagnostics\n")
    
    # Run tests
    api_ok = test_neon_api()
    dns_ok = test_dns_resolution()
    tcp_ok = test_tcp_connection()
    
    print(f"\n📊 Test Results:")
    print(f"   Neon API: {'✅' if api_ok else '❌'}")
    print(f"   DNS Resolution: {'✅' if dns_ok else '❌'}")
    print(f"   TCP Connection: {'✅' if tcp_ok else '❌'}")
    
    if not any([api_ok, dns_ok, tcp_ok]):
        print("\n🚨 Severe connectivity issues detected!")
    elif tcp_ok:
        print("\n🤔 TCP works but database connection fails - likely authentication or database sleep issue")
    
    suggest_solutions()
