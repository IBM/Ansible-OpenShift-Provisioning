#!/usr/bin/env python3
"""
Parse and validate OCP node resource usage against threshold.
Usage: python3 check_node_resources.py "<oc_adm_top_output>" <threshold_percentage>
"""

import sys
import json
import re
from typing import Dict, List, Tuple

def parse_node_output(output: str) -> List[Dict]:
    """
    Parse 'oc adm top nodes' output into structured data.
    
    Expected format:
    NAME                                    CPU(cores)   CPU%        MEMORY(bytes)   MEMORY%
    node1.example.com                       2000m        50%         4Gi             75%
    node2.example.com                       1500m        37%         3Gi             50%
    """
    lines = output.strip().split('\n')
    
    if len(lines) < 2:
        raise ValueError("Invalid output format - no node data found")
    
    nodes = []
    # Skip header line (first line)
    for line in lines[1:]:
        if not line.strip():
            continue
        
        # Parse the line
        parts = line.split()
        if len(parts) < 5:
            continue
        
        node_name = parts[0]
        cpu_cores = parts[1]
        cpu_percent = parts[2].rstrip('%')
        memory_bytes = parts[3]
        memory_percent = parts[4].rstrip('%')
        
        try:
            node = {
                'name': node_name,
                'cpu_cores': cpu_cores,
                'cpu_percent': float(cpu_percent),
                'memory_bytes': memory_bytes,
                'memory_percent': float(memory_percent),
            }
            nodes.append(node)
        except ValueError as e:
            print(f"Warning: Could not parse line: {line}", file=sys.stderr)
            continue
    
    return nodes

def validate_nodes(nodes: List[Dict], threshold: float) -> Tuple[bool, List[str]]:
    """
    Validate that all nodes are below the threshold.
    Returns (is_valid, error_messages)
    """
    errors = []
    is_valid = True
    
    for node in nodes:
        cpu_exceeds = node['cpu_percent'] > threshold
        memory_exceeds = node['memory_percent'] > threshold
        
        if cpu_exceeds or memory_exceeds:
            is_valid = False
            msg_parts = [f"Node '{node['name']}'"]
            
            if cpu_exceeds:
                msg_parts.append(f"CPU: {node['cpu_percent']:.1f}% (threshold: {threshold}%)")
            
            if memory_exceeds:
                msg_parts.append(f"MEMORY: {node['memory_percent']:.1f}% (threshold: {threshold}%)")
            
            errors.append(" | ".join(msg_parts))
    
    return is_valid, errors

def print_summary(nodes: List[Dict], threshold: float, errors: List[str]) -> None:
    """Print detailed summary of node status."""
    print("\n" + "="*80)
    print("OCP NODE RESOURCE USAGE REPORT")
    print("="*80)
    print(f"Threshold: {threshold}%\n")
    
    # Print all nodes
    print(f"{'Node Name':<40} {'CPU%':<10} {'MEMORY%':<10} {'Status':<15}")
    print("-"*80)
    
    for node in nodes:
        cpu_status = "⚠️ ALERT" if node['cpu_percent'] > threshold else "✓ OK"
        mem_status = "⚠️ ALERT" if node['memory_percent'] > threshold else "✓ OK"
        
        # Combined status
        if node['cpu_percent'] > threshold or node['memory_percent'] > threshold:
            status = "EXCEEDS"
        else:
            status = "WITHIN"
        
        print(f"{node['name']:<40} {node['cpu_percent']:>6.1f}%    {node['memory_percent']:>6.1f}%    {status:<15}")
    
    print("-"*80)
    
    # Print errors if any
    if errors:
        print("\n⚠️  NODES EXCEEDING THRESHOLD:\n")
        for error in errors:
            print(f"  • {error}")
    else:
        print("\n✓ All nodes are within the acceptable resource limits")
    
    print("\n" + "="*80 + "\n")

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 check_node_resources.py '<oc_output>' <threshold>", file=sys.stderr)
        sys.exit(1)
    
    oc_output = sys.argv[1]
    try:
        threshold = float(sys.argv[2])
    except ValueError:
        print(f"Error: Threshold must be a number, got '{sys.argv[2]}'", file=sys.stderr)
        sys.exit(1)
    
    if threshold < 0 or threshold > 100:
        print(f"Error: Threshold must be between 0 and 100, got {threshold}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Parse the output
        nodes = parse_node_output(oc_output)
        
        if not nodes:
            print("Error: No nodes found in output", file=sys.stderr)
            sys.exit(1)
        
        # Validate against threshold
        is_valid, errors = validate_nodes(nodes, threshold)
        
        # Print summary
        print_summary(nodes, threshold, errors)
        
        # Exit with appropriate code
        sys.exit(0 if is_valid else 1)
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
