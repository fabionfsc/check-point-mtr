#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# cpmtr - A simple traceroute and ping monitoring tool.

import os
import sys
import time
import socket
import subprocess
import re
import statistics

DEFAULT_MAX_HOPS = 30
INTERVAL = 1 # Seconds

def discover_hops(destination, max_hops):
    """Discovers hops using the system's traceroute command."""
    command = ['traceroute', '-n', '-m', str(max_hops), destination]
    hops = []
    
    try:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = proc.communicate(timeout=60)

        if proc.returncode != 0 and stderr and "Unsupported Werror" in stderr:
            command = ['traceroute', '-I', '-n', '-m', str(max_hops), destination]
            proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, _ = proc.communicate(timeout=60)

        ip_regex = re.compile(r'\s*(\d+\.\d+\.\d+\.\d+)\s*')
        
        for line in stdout.splitlines():
            if not line.strip() or not line.lstrip()[0].isdigit():
                continue

            match = ip_regex.search(line)
            if match:
                # Se o traceroute retornar o próprio IP de origem, pode pular
                if len(hops) == 0 and match.group(1) == socket.gethostbyname(socket.gethostname()):
                    continue
                hops.append(match.group(1))
            else:
                hops.append('*')
        
        if hops and hops[-1] != destination:
             if any(h == destination for h in hops):
                 while hops[-1] != destination:
                     hops.pop()
             else:
                 hops.append(destination)

    except FileNotFoundError:
        print("Error: 'traceroute' command not found. Aborting.", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("Error: 'traceroute' timed out. Please check connectivity.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error during traceroute: {e}", file=sys.stderr)
        sys.exit(1)

    if len(hops) > 1 and hops[-1] == hops[-2]:
        hops.pop()
        
    return hops

def ping_host(ip):
    """Pings a single host using the system's ping command."""
    if ip == '*':
        return None
        
    command = ['ping', '-c', '1', '-W', '1', ip]
    try:
        output = subprocess.check_output(command, stderr=subprocess.DEVNULL, text=True)
        match = re.search(r'time=([\d.]+)\s*ms', output)
        if match:
            return float(match.group(1))
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return None

def main(destination):
    try:
        dest_ip = socket.gethostbyname(destination)
    except socket.gaierror:
        print(f"Error: Could not resolve host: {destination}", file=sys.stderr)
        sys.exit(1)

    hops_ips = discover_hops(destination, DEFAULT_MAX_HOPS)
    if not hops_ips:
        print("Error: Could not discover route.", file=sys.stderr)
        sys.exit(1)
        
    hops_stats = [{
        'ip': ip,
        'sent': 0, 'lost': 0, 'last': 0.0,
        'rtts': [], 'best': 9999.9, 'worst': 0.0
    } for ip in hops_ips]

    try:
        while True:
            for stats in hops_stats:
                rtt = ping_host(stats['ip'])
                
                stats['sent'] += 1
                if rtt is not None:
                    stats['last'] = rtt
                    stats['rtts'].append(rtt)
                    stats['best'] = min(stats['best'], rtt)
                    stats['worst'] = max(stats['worst'], rtt)
                else:
                    stats['lost'] += 1
                    stats['last'] = 0.0

            os.system('clear' if os.name == 'posix' else 'cls')
            print(f" cpmtr v0.1                                                    {destination} ({dest_ip})")
            # --- CABEÇALHO CORRIGIDO ---
            print(f"{'Host':<28}{'Loss%':>7}{'Snt':>6}{'Last':>7}{'Avg':>7}{'Best':>7}{'Wrst':>7}")

            for i, stats in enumerate(hops_stats):
                host_display = stats['ip']
                if host_display == '*':
                     hop_str = f" {i+1}. ???"
                     print(f"{hop_str:<28}")
                     continue

                # --- LINHA DE DADOS CORRIGIDA ---
                hop_str = f" {i+1}. {host_display}"
                loss_str = f"{stats['lost']/stats['sent']*100 if stats['sent']>0 else 0.0:.1f}%"
                avg = statistics.mean(stats['rtts']) if stats['rtts'] else 0.0
                
                print(f"{hop_str:<28}"
                      f"{loss_str:>7}"
                      f"{stats['sent']:>6}"
                      f"{stats['last']:>7.1f}"
                      f"{avg:>7.1f}"
                      f"{stats['best'] if stats['best'] != 9999.9 else 0.0:>7.1f}"
                      f"{stats['worst']:>7.1f}")
            
            time.sleep(INTERVAL)

    except KeyboardInterrupt:
        print("\nQuitting.")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <destination_host>", file=sys.stderr)
        sys.exit(1)
    
    main(sys.argv[1])