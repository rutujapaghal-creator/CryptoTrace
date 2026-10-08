# PROJECT VED
### Virtual Evidence & Attribution Directorate
**Real-Time Cryptocurrency Fraud Attribution & Statutory Asset Freeze System**

---

## 1. Executive Summary

**Project VED** is an offline-ready, standalone cyber forensics and intelligence platform engineered for Law Enforcement Agencies (LEAs), State Cyber Police Directorates, and the Indian Cyber Crime Coordination Centre (I4C).

When a victim reports an illicit cryptocurrency wallet address to the National Cyber Crime Reporting Portal (NCRP) or the 1930 Cyber Crime Helpline, **VED traces the forward money flow through multi-hop mule networks, detects the nearest regulated Virtual Asset Service Provider (VASP / Exchange) where funds landed, evaluates multi-factor risk, and generates legally court-admissible Section 106 BNSS Freeze Directives and Section 63 BSA Digital Evidence Certificates within seconds.**

Because non-custodial decentralized wallets cannot be frozen on-chain, VED focuses on **identifying the exact regulated exchange custody point within the critical "Golden Hour" before criminal syndicates liquidate the proceeds of crime.**

---

## 2. High-Level System Architecture

```
   NCRP / 1930 / SAHYOG Complaint Feed
                  │
                  ▼
   ┌─────────────────────────────────────┐
   │        1. INGESTION LAYER           │  Base58Check & EIP-55 Address Validator,
   │ (Multi-Chain Detection & Deduping)  │  Auto-Deduplication & Multi-Victim Clustering
   └──────────────────┬──────────────────┘
                      ▼
   ┌─────────────────────────────────────┐      ┌───────────────────────────────┐
   │        2. BLOCKCHAIN INDEXER        │◄────►│ Local Forensic Graph Store    │
   │      (TRON, ETH, BSC, BITCOIN)      │      │ (High-Throughput SQLite WAL)  │
   └──────────────────┬──────────────────┘      └───────────────────────────────┘
                      ▼
   ┌─────────────────────────────────────┐      ┌───────────────────────────────┐
   │        3. TRACING ENGINE            │◄────►│ Cross-Chain Bridges & DEXes   │
   │  (BFS Traversal & Taint Tracking)   │      │ (Stargate, SunSwap, Uniswap)  │
   └──────────────────┬──────────────────┘      └───────────────────────────────┘
                      ▼
   ┌─────────────────────────────────────┐      ┌───────────────────────────────┐
   │       4. ATTRIBUTION ENGINE         │◄────►│ VASP & Entity Label Directory │
   │    (Exchange Deposit Sweep Cluster) │      │ (Binance, WazirX, CoinDCX)    │
   └──────────────────┬──────────────────┘      └───────────────────────────────┘
                      ▼
   ┌─────────────────────────────────────┐
   │    5. PATTERN & RISK ENGINE         │  Peel Chains, Rapid Pass-Through,
   │  (Typology MO & Golden Hour Logic)  │  Mixers (Tornado Cash), 0-100 Score
   └──────────────────┬──────────────────┘
                      ▼
   ┌─────────────────────────────────────┐
   │     6. STATUTORY OUTPUT LAYER       │  Interactive Canvas Graph, Section 106 BNSS
   │ (Freeze Directives & Court Dossier) │  Freeze Directives, Section 63 BSA Certs
   └─────────────────────────────────────┘
```

---

## 3. Core Modules

### Module 1: Ingestion & Deduplication Layer
- **Cryptographic Address Format Detection:**
  - **TRON (TRC-20 USDT):** Base58Check validation, prefix `0x41`, length 34 chars (the dominant currency in Indian task scams and investment frauds).
  - **Ethereum & EVM Chains (BSC, Polygon):** EIP-55 checksum validation (`0x` + 40 hex characters).
  - **Bitcoin (UTXO):** Native SegWit Bech32 (`bc1`), Legacy P2PKH (`1`), Script Hash P2SH (`3`).
- **Automated Case Deduplication:**
  - Multiple complaints reporting the same suspect wallet across different police stations/states are automatically merged into a single Master Case file.
  - Automatically calculates cumulative victim loss and escalates case priority.

### Module 2: Blockchain Indexer & Storage Engine
- Standalone, air-gapped forensic storage using SQLite in Write-Ahead-Logging (WAL) mode with indexed transaction ledgers.
- Supports both UTXO transaction graph heuristics (Bitcoin) and Account-based contract event transfers (TRC-20/ERC-20 USDT).

### Module 3: Tracing Engine (Taint Tracking & Graph Traversal)
- Directed forward money flow traversal starting from suspect wallet $W_0$.
- **Haircut Model Taint Tracking:** Proportional fund allocation across splits and mule intermediaries.
- **Handling Complications:**
  - **Peel Chains:** Detects sequential micro-extractions with remainder cascades.
  - **Cross-Chain Bridges:** Follows funds across lock/mint gateways (e.g. TRON $\to$ Ethereum Bridge $\to$ CoinDCX).
  - **DEX Swaps:** Decodes router contracts (Uniswap, SunSwap).
  - **Mixers / Privacy Pools:** Identifies and flags Tornado Cash and ChipMixer obfuscation.
- **Offline Synthetic Forensic Simulator:** For newly entered addresses with no prior index, VED builds a mathematically consistent multi-hop money flow graph to demonstrate real-time tracing offline.

### Module 4: Attribution Engine (VASP Identification)
- Curated entity registry of Indian (FIU-IND registered) and Global VASPs:
  - **Indian VASPs:** WazirX (Zanmai Labs), CoinDCX (Neblio Tech), Mudrex, ZebPay.
  - **Global VASPs:** Binance, OKX, KuCoin, Bybit, Kraken, Bitfinex.
- **Deposit-Address Sweep Heuristic:**
  - Identifies customer deposit addresses when funds are automatically swept into exchange centralized hot wallets.
  - Outputs VASP name, deposit address, transaction hash, confidence percentage, FIU registration status, and verified Nodal Officer email.

### Module 5: Pattern Detection & Risk Scoring
- **Typology Classification:** Identifies fraud modus operandi (Task/Part-Time Job Syndicate, Investment/Stock Trading Scam, Digital Arrest/Extortion, Ransomware).
- **Composite Risk Score (0 - 100):**
  - **CRITICAL (80-100):** Target funds resting in reachable VASP deposit address with Golden Hour window open.
  - **HIGH (60-79):** Multi-victim complaint density, mule layering.
  - **MEDIUM (40-59):** Decentralized intermediary movement without exchange hit.
  - **LOW (0-39):** Inactive or dust balance.

### Module 6: Statutory Notice & Digital Evidence Generator
- **Section 106 BNSS (Bharatiya Nagarik Suraksha Sanhita, 2023) Statutory Freeze Notice:**
  - Formal directive to VASP Nodal Officer ordering an immediate debit freeze and 2-hour KYC production.
- **Section 63 BSA (Bharatiya Sakshya Adhiniyam, 2023) Electronic Evidence Certificate:**
  - Court-admissible electronic certificate (replacing Section 65B of Indian Evidence Act) stamped with the SHA-256 hash of the complete forensic ledger snapshot.
- **Official Court Dossier:** Complete printable dossier with metadata, transaction tables, and statutory annexures.

---

## 4. Built-in Forensic Test Scenarios

The system includes pre-seeded forensic cases matching real-world investigative blueprints:

| Preset Name | Seed Wallet | Chain | Primary Target VASPs | Typology |
|---|---|---|---|---|
| **Pune Scam** | `T9xQZ1W8tKmPxN3vYe2a7L4bC9dEfG5hJk` | TRON | Binance (94%) & CoinDCX (96% via Bridge) | Investment Fraud |
| **Delhi Task Scam** | `TJobScam119xKzPmNvQtLw8vCe4a7LbC9dEfG5` | TRON | WazirX (95%) & KuCoin (92%) [42 Merged Complaints] | Task / Job Scam |
| **Mumbai Digital Arrest** | `0x742d35Cc6634C0532925a3b844Bc454e4438f44e` | ETH | Tornado Cash Mixer $\to$ Bybit (98%) | Digital Arrest / Sextortion |
| **Hospital Ransomware** | `bc1q9v8h2kmzpxnvqtlyw8vce4a7lbc9defg5hjkl` | BITCOIN | Bitfinex (96%) & Kraken (96%) [Peel Chain] | Ransomware Extortion |
| **Arbitrary Input** | *Any valid TRON / ETH / BTC address* | Auto | Dynamic 3-hop mule trail to reachable VASP | Offline Simulation |

---

## 5. Quick Start (Running Locally & Standalone)

Project VED is **100% self-contained and offline-ready**. All assets, styles, fonts, and graph logic are served locally without external CDN calls.

### Prerequisites
- Python 3.9+

### Launching the System

**On macOS / MacBook (Single-Click):**
- Simply double-click **`run.command`** in Finder!
  *(This will change to the project directory, verify Python, seed the database, auto-open your default browser to `http://127.0.0.1:8000`, and start the terminal server).*

**On Windows (Single-Click):**
- Simply double-click **`run.bat`**, or run from Command Prompt:
  ```cmd
  run.bat
  ```

**From Terminal (macOS / Linux):**
```bash
# Navigate to project directory
cd /Users/kalyanpatil/Downloads/rutuja

# Run the launch script
./run.sh
```

Alternatively, start the server directly:
```bash
python3 -m uvicorn ved.app:app --host 127.0.0.1 --port 8000
```

### Accessing the Command Center
Open your browser and navigate to:
```
http://127.0.0.1:8000
```

---

## 6. Verification & Automated Test Suite

To verify all system endpoints, cryptographic validations, and trace algorithms from the terminal:

```bash
python3 -c "
import urllib.request, json

def test_trace(addr):
    req = urllib.request.Request('http://127.0.0.1:8000/api/trace', method='POST',
                                 headers={'Content-Type': 'application/json'},
                                 data=json.dumps({'wallet_address': addr}).encode())
    res = urllib.request.urlopen(req)
    data = json.loads(res.read())
    print(f'Trace for {addr[:12]}... => Nodes: {data[\"nodes_count\"]}, Risk: {data[\"risk\"][\"score\"]}-{data[\"risk\"][\"tier\"]}, VASPs: {[v[\"vasp_name\"] for v in data[\"vasp_attribution\"]]}')

test_trace('T9xQZ1W8tKmPxN3vYe2a7L4bC9dEfG5hJk')
test_trace('TJobScam119xKzPmNvQtLw8vCe4a7LbC9dEfG5')
test_trace('0x742d35Cc6634C0532925a3b844Bc454e4438f44e')
test_trace('bc1q9v8h2kmzpxnvqtlyw8vce4a7lbc9defg5hjkl')
"
```

---

## 7. Directory Structure

```
ved/
├── app.py                      # FastAPI server & REST API endpoints
├── database/
│   ├── db.py                   # SQLite database connector & context manager
│   ├── schema.py               # Comprehensive forensic relational schema
│   ├── seed_data.py            # Pre-seeded multi-chain transaction ledgers & VASP directory
│   └── ved_forensics.db        # High-speed SQLite database (WAL mode)
├── core/
│   ├── validation.py           # Base58Check, EIP-55, and Bech32 cryptographic validator
│   ├── tracing.py              # BFS money flow traversal, haircut taint analysis, bridge handler
│   ├── attribution.py          # Sweep heuristic clustering & VASP confidence scoring
│   ├── patterns.py             # Peel chain, fan-out/fan-in, mixer, and typology classifier
│   └── risk.py                 # Multi-parameter risk scoring engine (0-100)
├── services/
│   ├── ncrp_service.py         # NCRP / 1930 complaint ingestion & automatic deduplication
│   ├── report_service.py       # Section 106 BNSS notice & Section 63 BSA certificate generator
│   └── watchtower.py           # Real-time alert monitor & golden hour countdown
├── static/
│   ├── css/
│   │   └── ved.css             # Industrial dark tactical LEA UI design system
│   └── js/
│       ├── graph.js            # Standalone Canvas interactive graph renderer (zero dependencies)
│       └── app.js              # Command Center UI interaction logic
├── templates/
│   └── index.html              # Command Center single-page application
├── run.sh                      # Standalone single-click startup script
└── README.md                   # System documentation & technical specifications
```
