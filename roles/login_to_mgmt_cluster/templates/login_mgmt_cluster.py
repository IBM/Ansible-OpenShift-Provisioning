#!/usr/bin/env python3
"""
Login to OCP Management Cluster and display node/cluster operator info.
"""

import sys
import subprocess
import os
import argparse
from pathlib import Path
from typing import Tuple

class OCLoginManager:
    """Manages OCP cluster login."""
    
    def __init__(self, api_server: str, username: str, password: str, 
                 kubeconfig_path: str, context_name: str):
        """Initialize OCP login manager."""
        self.api_server = api_server.rstrip('/')
        self.username = username
        self.password = password
        self.kubeconfig_path = os.path.expanduser(kubeconfig_path)
        self.context_name = context_name
    
    def ensure_kubeconfig_dir(self) -> Tuple[bool, str]:
        """Ensure .kube directory exists."""
        try:
            kube_dir = os.path.dirname(self.kubeconfig_path)
            Path(kube_dir).mkdir(parents=True, exist_ok=True)
            return True, ""
        except Exception as e:
            return False, f"Failed to create kubeconfig directory: {str(e)}"
    
    def login_to_cluster(self) -> Tuple[bool, str]:
        """Perform login to OCP cluster."""
        try:
            cmd = [
                'oc', 'login',
                '--server', self.api_server,
                '--username', self.username,
                '--password', self.password,
                '--kubeconfig', self.kubeconfig_path,
                '--insecure-skip-tls-verify=false'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return True, ""
            else:
                error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
                return False, f"Login failed: {error_msg}"
        
        except subprocess.TimeoutExpired:
            return False, "Login command timed out (30s)"
        except FileNotFoundError:
            return False, "oc CLI not found"
        except Exception as e:
            return False, f"Login error: {str(e)}"
    
    def get_nodes(self) -> str:
        """Get nodes info."""
        try:
            cmd = ['oc', 'get', 'nodes', '-o', 'wide', '--kubeconfig', self.kubeconfig_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return result.stdout if result.returncode == 0 else ""
        except:
            return ""
    
    def get_cluster_operators(self) -> str:
        """Get cluster operators info."""
        try:
            cmd = ['oc', 'get', 'co', '--kubeconfig', self.kubeconfig_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return result.stdout if result.returncode == 0 else ""
        except:
            return ""
    
    def login(self) -> Tuple[bool, str]:
        """Execute login and get cluster info."""
        # Setup kubeconfig dir
        success, msg = self.ensure_kubeconfig_dir()
        if not success:
            return False, msg
        
        # Login
        success, msg = self.login_to_cluster()
        if not success:
            return False, msg
        
        # Get nodes and cluster operators
        nodes = self.get_nodes()
        operators = self.get_cluster_operators()
        
        output = f"\n✓ Login successful to {self.api_server}\n"
        output += "\n" + "="*100 + "\n"
        output += "NODES:\n"
        output += "="*100 + "\n"
        output += nodes + "\n"
        output += "="*100 + "\n"
        output += "CLUSTER OPERATORS:\n"
        output += "="*100 + "\n"
        output += operators
        
        return True, output

def main():
    parser = argparse.ArgumentParser(description='Login to OCP and display cluster info')
    parser.add_argument('--api-server', required=True, help='OCP API server URL')
    parser.add_argument('--username', required=True, help='Username for OCP login')
    parser.add_argument('--password', required=True, help='Password for OCP login')
    parser.add_argument('--kubeconfig-path', default=os.path.expanduser('~/.kube/config'),
                       help='Path to kubeconfig file')
    parser.add_argument('--context-name', default='mgmt-cluster', help='Name for the OCP context')
    
    args = parser.parse_args()
    
    try:
        manager = OCLoginManager(
            api_server=args.api_server,
            username=args.username,
            password=args.password,
            kubeconfig_path=args.kubeconfig_path,
            context_name=args.context_name
        )
        
        success, message = manager.login()
        
        print(message)
        sys.exit(0 if success else 1)
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()