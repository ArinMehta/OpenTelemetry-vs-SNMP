Perfect — you’ve got a clearly structured, well-documented summary already, so let’s elegantly weave in the **updated topology** and **context** while keeping everything else intact.

Below is the **revised `project_summary.md`** rewritten for your *current* Mininet topology and project context.
I’ve updated the **architecture**, **implementation**, and **environment** descriptions to match your latest design (the routed two-subnet topology with one router and six hosts), while preserving all your achievements and findings.

---

# Project Summary: Network Monitoring – OpenTelemetry vs SNMP

## CS331 Computer Networks Project – IIT Gandhinagar

---

## 📋 Project Overview

This project implements and compares two major network monitoring technologies:

* **SNMP (Simple Network Management Protocol)** – Traditional device monitoring
* **OpenTelemetry** – Modern application observability framework

### Team Members

| Name               | Roll Number | Responsibility                                        |
| ------------------ | ----------- | ----------------------------------------------------- |
| Vedant Chichmalkar | 22110282    | SNMP Implementation & Prometheus Integration          |
| Arin Mehta         | 23110038    | OpenTelemetry Implementation & Prometheus Integration |
| Bhavya Parmar      | 23110059    | Integration Testing & Performance Comparison          |

---

## 📍 Context

This project compares **OpenTelemetry vs SNMP** for network monitoring in a **Mininet-based simulated environment**.
The network simulation runs inside a **virtualized Mininet VM**, with all monitoring components — **Prometheus**, **Grafana**, **SNMP Exporter**, and the **OpenTelemetry Collector** — containerized using **Docker Compose**.

The topology emulates a **routed enterprise-style network** with two subnets connected by a router, allowing both intra- and inter-subnet communication as well as external (Internet) access via NAT.

---

## 🏗️ Network Topology

### Topology Description

```
Subnet 1 (10.0.1.0/24)              Subnet 2 (10.0.2.0/24)
h1 (10.0.1.101) --- s1 --- r1 --- s2 --- h4 (10.0.2.104)
h2 (10.0.1.102) ---/       |         \--- h5 (10.0.2.105)
h3 (10.0.1.103) ---/       |         \--- h6 (10.0.2.106)
                           |
                  (10.0.1.1 / 10.0.2.1)
```

**Router (r1):** Connects Subnet 1 and Subnet 2, performs IP forwarding, and routes traffic between hosts.
**Switches (s1, s2):** Provide connectivity within each subnet.
**Hosts (h1–h6):** Run SNMP agents, traffic generators, and monitoring services.
**NAT Gateway:** Enables Internet access for all Mininet nodes for package installation and testing.

---

## 🎯 Objectives Achieved

✅ **Objective 1:** Learn how OpenTelemetry and SNMP work for network monitoring
✅ **Objective 2:** Deploy both tools inside a Mininet-based routed topology
✅ **Objective 3:** Compare data collection and visualization using Prometheus and Grafana
✅ **Objective 4:** Explore hybrid integration for unified monitoring

---

## ⚙️ System Architecture

### Overall Design

```
┌───────────────────────────────────────────────────────────┐
│                     Mininet Network                        │
│  Subnet1 ↔ Router (r1) ↔ Subnet2 + NAT                    │
│  • Hosts (h1–h6) with SNMP & OTel agents                   │
│  • Traffic generation (ICMP, TCP, HTTP)                    │
└─────────────────────┬──────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
   ┌────▼──────┐              ┌─────▼─────┐
   │ SNMP      │              │ OTel      │
   │ Exporter  │              │ Collector │
   └────┬──────┘              └────┬──────┘
        │                          │
        └────────────┬─────────────┘
                     │
              ┌──────▼──────┐
              │ Prometheus  │
              │  (Storage)  │
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │   Grafana   │
              │ Dashboards  │
              └─────────────┘
```

### Technology Stack

* **Network Simulation:** Mininet
* **Monitoring Tools:** SNMP, OpenTelemetry
* **Metrics Storage:** Prometheus
* **Visualization:** Grafana
* **Containerization:** Docker, Docker Compose
* **Programming:** Python 3.10

---

## 📊 Implementation Details

### SNMP Implementation (Vedant)

**Components**

* SNMP Collector (`snmp/collect_snmp.py`)
* SNMP Exporter configuration
* Prometheus integration

**Metrics Collected**

* Interface statistics (ifInOctets, ifOutOctets)
* Bandwidth utilization
* Error counts
* System uptime
* TCP/UDP statistics

**Highlights**

* Automatic OID walking
* Real-time counter handling
* Integration with Prometheus for live visualization

---

### OpenTelemetry Implementation (Arin)

**Components**

* Network monitor (`opentelemetry/network_monitor.py`)
* OpenTelemetry Collector configuration
* Python instrumentation

**Metrics Collected**

* Latency (ping RTT)
* Packet loss
* Bandwidth (TX/RX)
* Connection states
* Custom application metrics

**Highlights**

* Histogram-based latency tracking
* Real-time metric streaming
* Correlated traces for end-to-end visibility

---

### Integration & Dashboards (Bhavya)

**Dashboards**

1. **SNMP Dashboard**

   * Interface throughput
   * Bandwidth utilization
   * Error and uptime metrics

2. **OpenTelemetry Dashboard**

   * Latency percentiles (p50, p95, p99)
   * Packet loss visualization
   * Connection states and trends

3. **Comparison Dashboard**

   * Side-by-side metric visualization
   * Correlation analysis
   * Performance and coverage benchmarking

---

## 🔬 Experimental Results

| Metric             | SNMP       | OpenTelemetry      |
| ------------------ | ---------- | ------------------ |
| CPU Usage          | ~2%        | ~5–8%              |
| Memory Usage       | ~50 MB     | ~150–200 MB        |
| Network Overhead   | 1–2 KB/s   | 5–10 KB/s          |
| Latency Detection  | 15–30s     | <1s                |
| Metric Granularity | Fixed OIDs | Fully Customizable |
| Setup Complexity   | Low        | Medium–High        |

**Observations**

* OpenTelemetry detects latency spikes significantly faster.
* SNMP provides stable, lightweight monitoring with minimal overhead.
* Combining both gives deep, multi-layer visibility.

---

## 💡 Insights

### SNMP Strengths

* Lightweight and stable
* Broad hardware support
* Ideal for routers, switches, and legacy devices

### SNMP Limitations

* Limited metric flexibility
* Polling-based delays
* Less suited for modern app monitoring

### OpenTelemetry Strengths

* Real-time streaming metrics
* Custom instrumentation and tracing
* Cloud-native and extensible

### OpenTelemetry Limitations

* Higher resource usage
* Requires instrumentation effort
* Less compatible with legacy systems

---

## 🎓 Lessons Learned

**Technical**

1. No single “best” monitoring solution
2. Hybrid SNMP + OTel yields the richest results
3. Integration with Prometheus & Grafana is straightforward
4. Mininet + Docker provides a powerful, reproducible lab setup

**Teamwork**

* Clear role distribution improved efficiency
* Regular testing avoided late-stage bugs
* Comprehensive documentation aided collaboration

---

## 📁 Deliverables

* 🐳 `docker-compose.yml` for monitoring stack
* 🧩 SNMP Collector (`snmp/`)
* 🧠 OpenTelemetry Monitor (`opentelemetry/`)
* 📊 Prometheus and Grafana configs
* 🧱 Mininet topology (`mininet/topology.py`)
* 🧾 Documentation (`docs/`, `README.md`)
* 🔧 Traffic generator and test scripts (`scripts/`)

---

## 🚀 Running the Project

```bash
# 1. Set up the environment
./scripts/setup.sh

# 2. Start monitoring stack
./scripts/start.sh

# 3. Launch topology
sudo python3 mininet/topology.py

# 4. Access Grafana
http://localhost:3000  (admin / admin)

# 5. Generate traffic
python3 mininet/traffic_generator.py
```

---

## 🔮 Future Enhancements

* Implement SNMPv3 for secure monitoring
* Add alerting and anomaly detection
* Integrate eBPF for kernel-level insights
* Explore service-mesh and multi-cloud monitoring
* ML-based predictive analytics

---

## 🏁 Conclusion

This project demonstrates a **comprehensive comparison** between traditional and modern monitoring frameworks within a **custom routed network topology**.

* **SNMP** excels in efficiency and compatibility
* **OpenTelemetry** offers high-resolution observability
* **Hybrid approaches** bridge the gap between infrastructure and applications

Together, they represent the evolution of network visibility — from device-level polling to distributed, real-time observability.

---

## 📞 Contact

**Team Members:**

* Vedant Chichmalkar – [vedant.chichmalkar@iitgn.ac.in](mailto:vedant.chichmalkar@iitgn.ac.in)
* Arin Mehta – [arin.mehta@iitgn.ac.in](mailto:arin.mehta@iitgn.ac.in)
* Bhavya Parmar – [bhavya.parmar@iitgn.ac.in](mailto:bhavya.parmar@iitgn.ac.in)

**Course:** CS331 – Computer Networks
**Institution:** IIT Gandhinagar
**Date:** November 2025

---

**Thank you for reviewing our project!** 🙏

---

Would you like me to also add a **network diagram** (ASCII or Markdown image block) reflecting the updated two-subnet + router topology for the README visuals? It makes the summary pop in presentation reports.
