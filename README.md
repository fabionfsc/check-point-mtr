# cpmtr

A simple, `mtr`-like network monitoring tool for restrictive environments like Check Point GAiA.

This repository contains a single script:

  - **cpmtr.py** – Discovers a network route and continuously monitors each hop for latency and packet loss, displaying the results in a real-time terminal interface.

## Description

  - **cpmtr.py**:
      - Discovers the network path by calling the system's `traceroute` command.
      - Parses the `traceroute` output to identify each hop's IP address.
      - Enters a continuous loop to monitor each hop in real-time.
      - Pings each hop using the system's `ping` binary to measure latency.
      - Calculates key statistics: Packet Loss (`Loss%`), Sent packets (`Snt`), and latency (`Last`, `Avg`, `Best`, `Wrst`).
      - Refreshes the terminal UI every second with the live data.

## Features

  - Real-time network path monitoring in a single view.
  - Zero Python dependencies.
  - Runs without `root` or `sudo` in restricted environments.
  - Single-file script for easy deployment.
  - Clean, aligned terminal interface.

## Requirements

  - Unix-like OS (e.g., Check Point GAiA)
  - Python 3
  - Shell access (`expert` mode)
  - `ping` and `traceroute` binaries available in the system's `PATH`

## Dependencies

None. This script only requires standard Python 3 libraries and system binaries (`ping`, `traceroute`).

## Setup

1.  Clone this repository or copy `cpmtr.py` to the target machine.

2.  Make the script executable:

    ```bash
    chmod +x cpmtr.py
    ```

## Usage

Run the script from the terminal, providing a destination host as an argument.

```bash
./cpmtr.py <destination_host>
```

To quit the application at any time, press `Ctrl+C`.

## Example Usage

**Command:**

```bash
[Expert@FW-EXT:0]# ./cpmtr.py google.com
```

**Output:**

```
 cpmtr v0.1                                                    google.com (142.251.128.142)
Host                           Loss%    Snt   Last    Avg   Best   Wrst
 1. 192.168.1.1                0.0%     50    1.2    1.5    1.1    4.3
 2. 10.0.0.1                   0.0%     50    8.4    9.1    8.2   15.7
 3. example.isp.com            0.0%     50    8.9    9.5    8.4   16.2
 4. 142.250.174.12             0.0%     50   10.1   10.3    9.8   19.5
 5. google.com                 0.0%     50    9.7    9.8    9.5   11.1
```

## Disclaimer

This is an unofficial tool and is not affiliated with or supported by Check Point Software Technologies Ltd. Use at your own risk.
