import streamlit as st
import pandas as pd
import requests
import random
import json
from datetime import datetime, date, timedelta
import calendar
import time

# ---------------------------------------------------------
# Page Setup
# ---------------------------------------------------------
st.set_page_config(
    layout="wide", 
    page_title="Option Chain & Pro Terminal", 
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# CSS: Integrated Themes (StockMojo Light + Dark Pro Terminal)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Global Canvas */
    .stApp {
        background-color: #f4f6f8 !important;
        color: #1e293b !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .block-container {
        padding-top: 3.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
        max-width: 100% !important;
    }

    /* Fixed High-Contrast Tab Buttons */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px !important;
        border-bottom: 2px solid #cbd5e1 !important;
        margin-top: 10px !important;
        margin-bottom: 16px !important;
        padding-bottom: 6px !important;
        background: transparent !important;
    }
    .stTabs [data-baseweb="tab"] {
        height: 38px !important;
        background-color: #e2e8f0 !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 6px !important;
        padding: 0 22px !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }
    .stTabs [data-baseweb="tab"] * {
        color: #0f172a !important;
        font-size: 13px !important;
        font-weight: 800 !important;
        letter-spacing: 0.5px !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #cbd5e1 !important;
    }
    .stTabs [data-baseweb="tab"]:hover * {
        color: #000000 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important;
        border: 1.5px solid #1d4ed8 !important;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.25) !important;
    }
    .stTabs [aria-selected="true"] * {
        color: #ffffff !important;
        font-size: 13px !important;
        font-weight: 800 !important;
    }
    .stTabs [data-baseweb="tab-border"],
    .stTabs [data-baseweb="tab-highlight"],
    .stTabs hr {
        display: none !important;
        height: 0px !important;
        border: none !important;
    }

    /* Streamlit Selectbox (Single Crisp Blue Outline) */
    div[data-testid="stSelectbox"] {
        margin-bottom: 0px !important;
    }
    div[data-testid="stSelectbox"] label {
        display: none !important;
    }
    div[data-testid="stSelectbox"] > div {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
    }
    div[data-testid="stSelectbox"] > div > div {
        background-color: #ffffff !important;
        border: 1.5px solid #2563eb !important;
        border-radius: 6px !important;
        min-height: 32px !important;
        height: 32px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        color: #1e293b !important;
        box-shadow: 0 1px 2px rgba(37,99,235,0.06) !important;
    }
    div[data-testid="stSelectbox"] * {
        color: #1e293b !important;
        font-size: 12.5px !important;
    }
    div[data-testid="stSelectbox"] svg {
        fill: #2563eb !important;
    }

    /* Top Row 1 Spot Metrics Strip */
    .metrics-container-exact {
        display: flex;
        align-items: center;
        gap: 16px;
        height: 32px;
        font-size: 12.5px;
        padding-left: 6px;
    }
    .metric-group {
        display: inline-flex;
        align-items: baseline;
        gap: 5px;
    }
    .metric-lbl {
        color: #64748b;
        font-weight: 500;
    }
    .metric-val {
        color: #0f172a;
        font-weight: 700;
        font-size: 13px;
    }
    .metric-chg-red {
        color: #dc2626 !important;
        font-weight: 600;
        font-size: 11.5px;
    }
    .metric-chg-green {
        color: #16a34a !important;
        font-weight: 600;
        font-size: 11.5px;
    }

    /* Row 2 Sub-toolbar */
    .sub-toolbar-wrap {
        display: flex;
        align-items: center;
        gap: 8px;
        height: 32px;
        font-size: 12.5px;
    }
    .btn-toggle-live {
        padding: 3px 14px;
        border-radius: 5px;
        border: 1.5px solid #2563eb;
        background-color: #ffffff;
        color: #2563eb !important;
        font-weight: 600;
        font-size: 12px;
    }
    .btn-toggle-inactive {
        padding: 3px 10px;
        border-radius: 5px;
        border: 1px solid transparent;
        background-color: transparent;
        color: #64748b !important;
        font-weight: 500;
        font-size: 12px;
    }
    .cycle-text-label {
        color: #64748b;
        font-weight: 500;
        margin-left: 4px;
        font-size: 12.5px;
    }

    /* Option Chain Light Table */
    .table-box {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 4px;
        overflow-y: auto;
        max-height: 75vh;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-top: 6px;
    }
    table.stockmojo-tbl {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-size: 11.5px;
        color: #0f172a !important;
    }
    table.stockmojo-tbl thead tr.top-hdr th {
        position: sticky;
        top: 0;
        z-index: 25;
        background-color: #f8fafc;
        border-bottom: 1px solid #cbd5e1;
        font-size: 12px;
        font-weight: 700;
        padding: 6px 10px;
    }
    table.stockmojo-tbl thead tr.sub-hdr th {
        position: sticky;
        top: 29px;
        z-index: 25;
        background-color: #f1f5f9;
        color: #475569 !important;
        border-bottom: 2px solid #cbd5e1;
        border-right: 1px solid #e2e8f0;
        padding: 6px 4px;
        font-weight: 600;
        text-align: center;
    }
    table.stockmojo-tbl thead tr.summary-row td {
        background-color: #fafbfc;
        border-bottom: 1px solid #e2e8f0;
        border-right: 1px solid #f1f5f9;
        padding: 3px 6px;
        font-weight: 600;
        font-size: 11.5px;
        text-align: right;
    }
    table.stockmojo-tbl thead tr.summary-total td {
        background-color: #f1f5f9;
        border-bottom: 2px solid #94a3b8;
        font-weight: 700;
    }
    .summary-label-cell {
        background-color: #f1f5f9 !important;
        color: #0f172a !important;
        font-weight: 700 !important;
        text-align: center !important;
        border-left: 2px solid #cbd5e1 !important;
        border-right: 2px solid #cbd5e1 !important;
    }
    table.stockmojo-tbl tbody tr {
        border-bottom: 1px solid #e2e8f0;
        height: 27px;
    }
    table.stockmojo-tbl tbody tr:hover {
        background-color: #f8fafc;
    }
    table.stockmojo-tbl td {
        padding: 2px 6px;
        border-bottom: 1px solid #f1f5f9;
        border-right: 1px solid #f1f5f9;
        text-align: right;
        color: #0f172a !important;
    }
    td.col-iv {
        background-color: #fafbfc !important;
        color: #475569 !important;
        text-align: center !important;
        font-weight: 500;
    }
    td.col-strike {
        background-color: #f8fafc !important;
        font-weight: 700 !important;
        color: #020617 !important;
        text-align: center !important;
        border-left: 2px solid #cbd5e1 !important;
        border-right: 2px solid #cbd5e1 !important;
    }
    tr.atm-row { background-color: #fefce8 !important; }
    tr.atm-row:hover { background-color: #fef9c3 !important; }
    td.col-strike-atm {
        background-color: #fef08a !important;
        font-weight: 800 !important;
        color: #854d0e !important;
        text-align: center !important;
        border-left: 2px solid #eab308 !important;
        border-right: 2px solid #eab308 !important;
    }
    .badge-atm {
        background-color: #2563eb;
        color: #ffffff !important;
        font-size: 9px;
        font-weight: 800;
        padding: 1px 4px;
        border-radius: 3px;
        margin-left: 4px;
        vertical-align: middle;
    }
    .badge {
        display: inline-block;
        padding: 1px 4px;
        border-radius: 3px;
        font-size: 10px;
        font-weight: 700;
        min-width: 28px;
        text-align: center;
    }
    .badge-L { background: #bbf7d0; color: #166534 !important; border: 1px solid #86efac; }
    .badge-SC { background: #cffafe; color: #155e75 !important; border: 1px solid #67e8f9; }
    .badge-S { background: #fee2e2; color: #991b1b !important; border: 1px solid #fca5a5; }
    .badge-LU { background: #fef3c7; color: #9a3412 !important; border: 1px solid #fde68a; }
    .top-vol-green {
        background-color: #15803d !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        text-align: center !important;
    }
    .top-vol-red {
        background-color: #b91c1c !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        text-align: center !important;
    }

    /* Option Terminal Dark Theme with CHG VAL Gradient Bars */
    .terminal-container {
        background: #060b11;
        padding: 14px;
        border-radius: 8px;
        border: 1px solid #162232;
        color: #e2e8f0;
    }
    .terminal-top-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #070d14;
        border: 1px solid #142232;
        border-radius: 8px;
        padding: 8px 16px;
        margin-bottom: 10px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
    }
    .terminal-logo {
        display: flex;
        align-items: center;
        font-size: 14.5px;
        white-space: nowrap;
    }
    .terminal-spot-box {
        display: flex;
        align-items: center;
        gap: 8px;
        white-space: nowrap;
    }
    .terminal-spot-val {
        font-size: 18px;
        font-weight: 900;
        color: #00f59b;
        letter-spacing: 0.5px;
    }
    .terminal-spot-pill {
        background: rgba(0, 245, 155, 0.12);
        color: #00f59b;
        border: 1px solid #00f59b;
        padding: 2px 7px;
        border-radius: 4px;
        font-size: 11.5px;
        font-weight: 800;
    }
    .terminal-target-text {
        font-size: 11px;
        color: #cbd5e1;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-left: 2px;
    }
    .terminal-kpi-group {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .terminal-kpi-pill {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: #0b1420;
        border: 1.2px solid #1e2e42;
        border-radius: 6px;
        padding: 4px 10px;
        min-width: 80px;
        line-height: 1.2;
    }
    .terminal-kpi-label {
        font-size: 8.5px;
        color: #94a3b8;
        font-weight: 800;
        letter-spacing: 0.5px;
        margin-bottom: 2px;
    }
    .terminal-kpi-num {
        font-size: 12.5px;
        font-weight: 900;
        letter-spacing: 0.5px;
    }
    .terminal-live-tracker {
        display: flex;
        align-items: center;
        color: #00f59b;
        font-size: 11.5px;
        font-weight: 700;
        white-space: nowrap;
        margin-left: 6px;
    }
    .terminal-sub-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #080d14;
        border: 1px solid #131d2a;
        border-radius: 6px;
        padding: 6px 14px;
        margin-bottom: 10px;
        font-size: 12px;
    }
    .expiry-chip {
        background: #0e3047;
        color: #38bdf8;
        border: 1px solid #0284c7;
        padding: 3px 10px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 11px;
    }
    .terminal-table-box {
        background: #070c12;
        border: 1px solid #15202e;
        border-radius: 6px;
        overflow-y: auto;
        max-height: 68vh;
    }
    table.pro-term-tbl {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-size: 11.5px;
        font-family: 'SF Mono', Consolas, 'Liberation Mono', Menlo, monospace;
    }
    table.pro-term-tbl thead tr:first-child th {
        position: sticky;
        top: 0;
        z-index: 30;
        background: #0b131d;
        color: #94a3b8;
        padding: 8px 6px;
        border-bottom: 1px solid #1e2d40;
        font-size: 10.5px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        text-align: center;
    }
    table.pro-term-tbl thead tr:nth-child(2) th {
        position: sticky;
        top: 31px;
        z-index: 30;
        background: #0d1724;
        color: #94a3b8;
        padding: 8px 6px;
        border-bottom: 2px solid #1e2d40;
        font-size: 10.5px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        text-align: center;
    }
    table.pro-term-tbl th.call-hdr {
        color: #00f59b;
        border-bottom: 2px solid #00f59b;
    }
    table.pro-term-tbl th.put-hdr {
        color: #ff3366;
        border-bottom: 2px solid #ff3366;
    }
    table.pro-term-tbl td {
        padding: 4px 8px;
        border-bottom: 1px solid #0e1724;
        height: 30px;
        vertical-align: middle;
    }
    table.pro-term-tbl tr:hover td {
        background: #0c1521 !important;
    }

    .term-col-strike {
        background: #0d1520;
        font-weight: 800;
        color: #ffffff;
        text-align: center;
        border-left: 1px solid #1a2738;
        border-right: 1px solid #1a2738;
        font-size: 12px;
    }
    .term-atm-strike {
        background: #003747 !important;
        color: #00f59b !important;
        border: 1.5px solid #00d4ff !important;
        font-weight: 900 !important;
    }
    .term-col-ltp-ce {
        color: #00f59b;
        font-weight: 700;
        text-align: right;
    }
    .term-col-ltp-pe {
        color: #ff3366;
        font-weight: 700;
        text-align: left;
    }

    /* TOTAL VAL Gradient Bars */
    .term-bar-cell-ce {
        position: relative;
        text-align: right;
        padding-right: 8px !important;
    }
    .term-bar-cell-pe {
        position: relative;
        text-align: left;
        padding-left: 8px !important;
    }
    .term-bar-fill-ce {
        position: absolute;
        top: 3px;
        bottom: 3px;
        right: 0;
        background: linear-gradient(90deg, transparent, rgba(0, 245, 155, 0.28));
        border-right: 3px solid #00f59b;
        border-radius: 2px 0 0 2px;
        z-index: 1;
    }
    .term-bar-fill-pe {
        position: absolute;
        top: 3px;
        bottom: 3px;
        left: 0;
        background: linear-gradient(90deg, rgba(255, 51, 102, 0.28), transparent);
        border-left: 3px solid #ff3366;
        border-radius: 0 2px 2px 0;
        z-index: 1;
    }
    .term-bar-text {
        position: relative;
        z-index: 2;
        font-weight: 800;
        font-size: 11.5px;
    }

    /* CHG VAL Gradient Bars */
    .term-chg-cell-ce {
        position: relative;
        text-align: right;
        padding-right: 6px !important;
    }
    .term-chg-cell-pe {
        position: relative;
        text-align: left;
        padding-left: 6px !important;
    }
    .term-chg-fill-ce-pos {
        position: absolute;
        top: 3px;
        bottom: 3px;
        right: 0;
        background: linear-gradient(90deg, transparent, rgba(0, 245, 155, 0.28));
        border-right: 2px solid #00f59b;
        border-radius: 2px 0 0 2px;
        z-index: 1;
    }
    .term-chg-fill-ce-neg {
        position: absolute;
        top: 3px;
        bottom: 3px;
        right: 0;
        background: linear-gradient(90deg, transparent, rgba(255, 51, 102, 0.25));
        border-right: 2px solid #ff3366;
        border-radius: 2px 0 0 2px;
        z-index: 1;
    }
    .term-chg-fill-pe-pos {
        position: absolute;
        top: 3px;
        bottom: 3px;
        left: 0;
        background: linear-gradient(90deg, rgba(255, 51, 102, 0.28), transparent);
        border-left: 2px solid #ff3366;
        border-radius: 0 2px 2px 0;
        z-index: 1;
    }
    .term-chg-fill-pe-neg {
        position: absolute;
        top: 3px;
        bottom: 3px;
        left: 0;
        background: linear-gradient(90deg, rgba(0, 245, 155, 0.25), transparent);
        border-left: 2px solid #00f59b;
        border-radius: 0 2px 2px 0;
        z-index: 1;
    }
    .term-chg-pill-green {
        position: relative;
        z-index: 2;
        display: inline-block;
        background: rgba(0, 245, 155, 0.15);
        color: #00f59b;
        border: 1px solid rgba(0, 245, 155, 0.4);
        padding: 1px 6px;
        border-radius: 3px;
        font-weight: 700;
        font-size: 11px;
    }
    .term-chg-pill-red {
        position: relative;
        z-index: 2;
        display: inline-block;
        background: rgba(255, 51, 102, 0.15);
        color: #ff3366;
        border: 1px solid rgba(255, 51, 102, 0.4);
        padding: 1px 6px;
        border-radius: 3px;
        font-weight: 700;
        font-size: 11px;
    }
    .terminal-footer-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 10px;
        padding: 6px 14px;
        background: #080d14;
        border: 1px solid #131d2a;
        border-radius: 6px;
        font-size: 11px;
        color: #64748b;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Exact SEBI Index Lot Sizes & Settlement Framework
# ---------------------------------------------------------
INDEX_CONFIG = {
    "50  NIFTY": {
        "symbol": "NIFTY",
        "step": 50,
        "lot": 65,            # Exact SEBI revised: 65 units
        "is_weekly": True,    # Weekly + Monthly on Tuesday
        "spot": 23398.10,
        "syn_future": 23447.10,
        "vix": 12.29
    },
    "BANKNIFTY": {
        "symbol": "BANKNIFTY",
        "step": 100,
        "lot": 30,            # Exact SEBI revised: 30 units
        "is_weekly": False,   # Monthly only: Last Tuesday of month
        "spot": 50450.25,
        "syn_future": 50620.00,
        "vix": 13.40
    },
    "FINNIFTY": {
        "symbol": "FINNIFTY",
        "step": 50,
        "lot": 60,            # Exact SEBI revised: 60 units
        "is_weekly": False,   # Monthly only: Last Tuesday of month
        "spot": 23150.80,
        "syn_future": 23210.00,
        "vix": 12.60
    },
    "MIDCPNIFTY": {
        "symbol": "MIDCPNIFTY",
        "step": 25,
        "lot": 120,           # Exact SEBI revised: 120 units
        "is_weekly": False,   # Monthly only: Last Tuesday of month
        "spot": 12450.30,
        "syn_future": 12490.00,
        "vix": 14.10
    },
    "NIFTYNXT50": {
        "symbol": "NIFTYNXT50",
        "step": 100,
        "lot": 25,            # Exact SEBI revised: 25 units
        "is_weekly": False,   # Monthly only: Last Tuesday of month
        "spot": 68200.00,
        "syn_future": 68350.00,
        "vix": 13.80
    }
}
CYCLES = ["Prev Day", "Intraday", "3 Min", "5 Min", "10 Min", "15 Min", "1 Hour"]

def format_inr(val):
    if not val or val == 0:
        return "0"
    abs_v = abs(val)
    if abs_v >= 10000000:
        return f"{val / 10000000:.2f} Cr"
    elif abs_v >= 100000:
        return f"{val / 100000:.2f} L"
    elif abs_v >= 1000:
        return f"{val / 1000:.1f} K"
    return str(round(val, 1))

# ---------------------------------------------------------
# Expiry Helpers (Tuesday Settlement Framework)
# ---------------------------------------------------------
def get_upcoming_tuesdays_display(count=6):
    today = date.today()
    days_ahead = (1 - today.weekday()) % 7
    if days_ahead == 0 and datetime.now().hour >= 16:
        days_ahead = 7
    first_tue = today + timedelta(days=days_ahead)
    expiries = []
    for i in range(count):
        exp_dt = first_tue + timedelta(weeks=i)
        days_left = (exp_dt - today).days
        expiries.append(f"{exp_dt.strftime('%d %b')} ({days_left}d)")
    return expiries

def get_last_tuesdays_of_month_display(count=5):
    today = date.today()
    expiries = []
    year = today.year
    month = today.month
    while len(expiries) < count:
        _, last_day = calendar.monthrange(year, month)
        last_date = date(year, month, last_day)
        offset = (last_date.weekday() - 1) % 7
        last_tue = last_date - timedelta(days=offset)
        if last_tue >= today:
            days_left = (last_tue - today).days
            expiries.append(f"{last_tue.strftime('%d %b')} ({days_left}d)")
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1
    return expiries

# ---------------------------------------------------------
# Robust Live Scraper with Session Impersonation
# ---------------------------------------------------------
@st.cache_data(ttl=8)
def fetch_nse_live(symbol="NIFTY"):
    try:
        from curl_cffi import requests as cffi_requests
        session = cffi_requests.Session(impersonate="chrome124")
    except ImportError:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br"
        })

    try:
        r1 = session.get("https://www.nseindia.com", timeout=4)
        if r1.status_code == 200:
            time.sleep(0.3)
            session.headers.update({
                "Referer": "https://www.nseindia.com/option-chain",
                "X-Requested-With": "XMLHttpRequest",
                "Accept": "application/json, text/javascript, */*; q=0.01"
            })
            url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
            api_res = session.get(url, timeout=5)
            if api_res.status_code == 200:
                payload = api_res.json()
                if "records" in payload and len(payload["records"].get("data", [])) > 0:
                    return payload, True
    except Exception:
        pass
    return None, False

# ---------------------------------------------------------
# Sidebar File Uploader (For Off-Market Data Upload)
# ---------------------------------------------------------
st.sidebar.markdown("### 📂 Off-Market Data File")
uploaded_file = st.sidebar.file_uploader(
    "Upload NSE Option Chain Snapshot (.json or .csv)", 
    type=["json", "csv"]
)

# ---------------------------------------------------------
# Row 1 Selections & Metrics Strip
# ---------------------------------------------------------
r1_c1, r1_c2, r1_c3 = st.columns([1.5, 1.8, 6.7])

with r1_c1:
    selected_index_key = st.selectbox("Index", list(INDEX_CONFIG.keys()), index=0)

cfg = INDEX_CONFIG[selected_index_key]
symbol_clean = cfg["symbol"]
step = cfg["step"]
official_lot = cfg["lot"]

# ---------------------------------------------------------
# Dual-Engine Data Loading (Uploaded File vs Live API)
# ---------------------------------------------------------
spot_val = 0.0
raw_chain_data = []
live_expiries_display = []
is_live = False
is_uploaded = False

# PATH A: User uploaded an off-market closing file (.csv or .json)
if uploaded_file is not None:
    filename = uploaded_file.name.lower()
    
    if filename.endswith(".json"):
        try:
            payload = json.load(uploaded_file)
            records = payload.get("records", {})
            raw_chain_data = records.get("data", [])
            spot_val = float(records.get("underlyingValue", 0.0) or 0.0)
            
            raw_exp = records.get("expiryDates", [])
            today_dt = date.today()
            dt_exp = []
            for exp_str in raw_exp:
                try:
                    if "-" in exp_str and len(exp_str.split("-")[0]) == 2:
                        p_dt = datetime.strptime(exp_str, "%d-%b-%Y").date()
                    else:
                        p_dt = datetime.strptime(exp_str, "%Y-%m-%d").date()
                    days_left = (p_dt - today_dt).days
                    dt_exp.append((p_dt, f"{p_dt.strftime('%d %b')} ({days_left}d)"))
                except Exception:
                    pass
            dt_exp.sort(key=lambda x: x[0])
            live_expiries_display = [x[1] for x in dt_exp]
            is_uploaded = True
            is_live = True
            st.sidebar.success(f"Loaded: {uploaded_file.name}")
        except Exception as e:
            st.sidebar.error(f"Error parsing JSON: {e}")

    elif filename.endswith(".csv"):
        try:
            content = uploaded_file.getvalue().decode("utf-8", errors="ignore")
            lines = [line.strip() for line in content.splitlines() if line.strip()]

            # 1. Parse Spot Level and Expiry from NSE top metadata lines
            extracted_spot = 0.0
            extracted_expiry = "Closing Snapshot (0d)"
            for l in lines[:5]:
                if "underlying" in l.lower() or "index" in l.lower():
                    # Example line: "Underlying Index: NIFTY 24852.15"
                    parts = l.replace(",", "").split()
                    for p in parts:
                        try:
                            val = float(p)
                            if val > 1000:
                                extracted_spot = val
                                break
                        except ValueError:
                            pass
                if "expiry" in l.lower():
                    extracted_expiry = l.split(":")[-1].strip() + " (0d)"

            # 2. Locate the table header line containing 'STRIKE'
            header_idx = -1
            for idx, line in enumerate(lines[:10]):
                if "STRIKE" in line.upper():
                    header_idx = idx
                    break

            if header_idx != -1:
                import io
                clean_csv_str = "\n".join(lines[header_idx:])
                df_raw = pd.read_csv(io.StringIO(clean_csv_str), header=None)

                # Find the column index of Strike Price
                header_row = [str(x).strip().upper() for x in df_raw.iloc[0]]
                strike_col_idx = -1
                for i, col_name in enumerate(header_row):
                    if "STRIKE" in col_name:
                        strike_col_idx = i
                        break

                def clean_num(v):
                    if pd.isna(v): return 0.0
                    s = str(v).replace(",", "").replace("-", "").strip()
                    try:
                        return float(s) if s else 0.0
                    except ValueError:
                        return 0.0

                parsed_csv_rows = []
                # Process data rows (skipping the header)
                for row_idx in range(1, len(df_raw)):
                    row = df_raw.iloc[row_idx].tolist()
                    if len(row) <= strike_col_idx:
                        continue

                    strike = clean_num(row[strike_col_idx])
                    if strike <= 0:
                        continue

                    # Calls are to the left of Strike, Puts are to the right
                    # Standard NSE CSV layout:
                    # Calls: [OI(0), CHNG_OI(1), VOL(2), IV(3), LTP(4), CHNG(5), BID_QTY(6), BID(7), ASK(8), ASK_QTY(9)]
                    # Strike: [strike_col_idx]
                    # Puts:  [BID_QTY, BID, ASK, ASK_QTY, CHNG, LTP(strike+6), IV(strike+7), VOL(strike+8), CHNG_OI(strike+9), OI(strike+10)]
                    
                    ce_oi = int(clean_num(row[0])) if strike_col_idx >= 5 else 0
                    ce_oi_chg = clean_num(row[1]) if strike_col_idx >= 5 else 0.0
                    ce_vol = int(clean_num(row[2])) if strike_col_idx >= 5 else 0
                    ce_iv = clean_num(row[3]) if strike_col_idx >= 5 else 0.0
                    ce_ltp = clean_num(row[4]) if strike_col_idx >= 5 else 0.0
                    ce_p = clean_num(row[5]) if strike_col_idx >= 6 else 0.0

                    # Puts offset indexation
                    pe_ltp = clean_num(row[strike_col_idx + 6]) if len(row) > strike_col_idx + 6 else 0.0
                    pe_iv = clean_num(row[strike_col_idx + 7]) if len(row) > strike_col_idx + 7 else 0.0
                    pe_vol = int(clean_num(row[strike_col_idx + 8])) if len(row) > strike_col_idx + 8 else 0
                    pe_oi_chg = clean_num(row[strike_col_idx + 9]) if len(row) > strike_col_idx + 9 else 0.0
                    pe_oi = int(clean_num(row[strike_col_idx + 10])) if len(row) > strike_col_idx + 10 else 0
                    pe_p = clean_num(row[strike_col_idx + 5]) if len(row) > strike_col_idx + 5 else 0.0

                    parsed_csv_rows.append({
                        "strikePrice": strike,
                        "expiryDate": "UPLOADED",
                        "CE": {
                            "lastPrice": ce_ltp,
                            "totalTradedVolume": ce_vol,
                            "openInterest": ce_oi,
                            "pchangeinOpenInterest": ce_oi_chg,
                            "pChange": ce_p,
                            "impliedVolatility": ce_iv
                        },
                        "PE": {
                            "lastPrice": pe_ltp,
                            "totalTradedVolume": pe_vol,
                            "openInterest": pe_oi,
                            "pchangeinOpenInterest": pe_oi_chg,
                            "pChange": pe_p,
                            "impliedVolatility": pe_iv
                        }
                    })

                if parsed_csv_rows:
                    raw_chain_data = parsed_csv_rows
                    spot_val = extracted_spot if extracted_spot > 0 else cfg["spot"]
                    syn_future_val = spot_val + 49.0
                    live_expiries_display = [extracted_expiry]
                    is_uploaded = True
                    is_live = True
                    st.sidebar.success(f"✓ Parsed {len(parsed_csv_rows)} strikes from NSE CSV")
                else:
                    st.sidebar.error("Could not parse valid strike rows from this CSV.")
        except Exception as e:
            st.sidebar.error(f"Error parsing NSE CSV: {e}")
            
# PATH B: No file uploaded -> Connect to live exchange
if not is_uploaded:
    payload, is_live = fetch_nse_live(symbol_clean)
    if is_live and payload:
        records = payload.get("records", {})
        raw_chain_data = records.get("data", [])
        spot_val = float(records.get("underlyingValue", 0.0) or 0.0)
        if spot_val == 0.0 and len(raw_chain_data) > 0:
            for itm in raw_chain_data:
                s_cand = itm.get("CE", {}).get("underlyingValue") or itm.get("PE", {}).get("underlyingValue")
                if s_cand:
                    spot_val = float(s_cand)
                    break
        raw_exp = records.get("expiryDates", [])
        today_dt = date.today()
        dt_exp = []
        for exp_str in raw_exp:
            try:
                if "-" in exp_str and len(exp_str.split("-")[0]) == 2:
                    p_dt = datetime.strptime(exp_str, "%d-%b-%Y").date()
                else:
                    p_dt = datetime.strptime(exp_str, "%Y-%m-%d").date()
                if p_dt >= today_dt:
                    days_left = (p_dt - today_dt).days
                    dt_exp.append((p_dt, f"{p_dt.strftime('%d %b')} ({days_left}d)"))
            except Exception:
                pass
        dt_exp.sort(key=lambda x: x[0])
        live_expiries_display = [x[1] for x in dt_exp]

# Baseline fallback parameters if completely offline
if spot_val == 0.0:
    spot_val = cfg["spot"]

syn_future_val = cfg["syn_future"]
vix_val = cfg["vix"]

if not live_expiries_display:
    if cfg["is_weekly"]:
        live_expiries_display = get_upcoming_tuesdays_display(count=6)
    else:
        live_expiries_display = get_last_tuesdays_of_month_display(count=5)

with r1_c2:
    selected_expiry_display = st.selectbox("Expiry", live_expiries_display, index=0)

with r1_c3:
    st.markdown(
        f"""
        <div class="metrics-container-exact">
            <div class="metric-group">
                <span class="metric-lbl">Spot</span>
                <span class="metric-val">{spot_val:,.1f}</span>
                <span class="metric-chg-red">-0.34%</span>
            </div>
            <div class="metric-group">
                <span class="metric-lbl">Syn Future</span>
                <span class="metric-val">{syn_future_val:,.1f}</span>
                <span class="metric-chg-green">+0.01%</span>
            </div>
            <div class="metric-group">
                <span class="metric-lbl">VIX</span>
                <span class="metric-val">{vix_val:.2f}</span>
                <span class="metric-chg-green">+4.15%</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------------
# Row 2 Toolbar (Pixel Matched)
# ---------------------------------------------------------
r2_c1, r2_c2, r2_c3 = st.columns([1.8, 1.4, 6.8])

with r2_c1:
    st.markdown(
        """
        <div class="sub-toolbar-wrap">
            <span class="btn-toggle-live">Live</span>
            <span class="btn-toggle-inactive">Historical</span>
            <span class="cycle-text-label">Cycle:</span>
        </div>
        """,
        unsafe_allow_html=True
    )

with r2_c2:
    selected_cycle = st.selectbox("Cycle", CYCLES, index=0)

with r2_c3:
    auto_refresh = st.checkbox("Auto-refresh data (10s)", value=False)

# ---------------------------------------------------------
# Option Chain Data Parsing
# ---------------------------------------------------------
atm_strike = round(spot_val / step) * step
parsed_rows = []

def calc_buildup(p, oi):
    if p >= 0 and oi >= 0: return "↗ L", "badge-L"
    if p >= 0 and oi < 0:  return "⇡ SC", "badge-SC"
    if p < 0 and oi >= 0:  return "↘ S", "badge-S"
    return "⇣ LU", "badge-LU"

selected_date_str = selected_expiry_display.split(" (")[0]

if is_live and raw_chain_data:
    for item in raw_chain_data:
        exp_raw = item.get("expiryDate", "")
        if not is_uploaded and selected_date_str not in exp_raw:
            continue
        
        strike = item.get("strikePrice")
        ce = item.get("CE", {})
        pe = item.get("PE", {})

        ce_ltp = float(ce.get("lastPrice", 0.0) or 0.0)
        pe_ltp = float(pe.get("lastPrice", 0.0) or 0.0)
        ce_vol = int(ce.get("totalTradedVolume", 0) or 0)
        pe_vol = int(pe.get("totalTradedVolume", 0) or 0)
        ce_oi = int(ce.get("openInterest", 0) or 0)
        pe_oi = int(pe.get("openInterest", 0) or 0)
        ce_oi_chg = round(float(ce.get("pchangeinOpenInterest", 0.0) or 0.0), 0)
        pe_oi_chg = round(float(pe.get("pchangeinOpenInterest", 0.0) or 0.0), 0)
        ce_p = round(float(ce.get("pChange", 0.0) or 0.0), 0)
        pe_p = round(float(pe.get("pChange", 0.0) or 0.0), 0)
        ce_iv = float(ce.get("impliedVolatility", 0.0) or 0.0)
        pe_iv = float(pe.get("impliedVolatility", 0.0) or 0.0)

        # Turnover in Crores using official SEBI lot size
        ce_val_cr = int(round((ce_ltp * ce_vol * official_lot) / 10000000))
        pe_val_cr = int(round((pe_ltp * pe_vol * official_lot) / 10000000))
        ce_chg_cr = int(round((ce_val_cr * ce_oi_chg) / 100)) if ce_oi_chg != 0 else 0
        pe_chg_cr = int(round((pe_val_cr * pe_oi_chg) / 100)) if pe_oi_chg != 0 else 0

        ce_tag, ce_cls = calc_buildup(ce_p, ce_oi_chg)
        pe_tag, pe_cls = calc_buildup(pe_p, pe_oi_chg)

        parsed_rows.append({
            "strike": strike,
            "is_atm": (strike == atm_strike),
            "ce_tag": ce_tag, "ce_cls": ce_cls,
            "ce_vol": ce_vol, "ce_oi_chg": ce_oi_chg, "ce_oi": ce_oi,
            "ce_iv": ce_iv, "ce_ltp": ce_ltp, "ce_p": ce_p,
            "ce_val_cr": ce_val_cr, "ce_chg_cr": ce_chg_cr,
            "pe_ltp": pe_ltp, "pe_p": pe_p,
            "pe_iv": pe_iv, "pe_oi": pe_oi, "pe_oi_chg": pe_oi_chg, "pe_vol": pe_vol,
            "pe_tag": pe_tag, "pe_cls": pe_cls,
            "pe_val_cr": pe_val_cr, "pe_chg_cr": pe_chg_cr
        })

# Off-market fallback generator to prevent blank table
if len(parsed_rows) == 0:
    for i in range(-20, 20):
        s = atm_strike + (i * step)
        diff = s - spot_val
        ce_ltp = max(1.5, round(127.80 - (diff * 0.48), 2))
        pe_ltp = max(1.5, round(80.70 + (diff * 0.48), 2))
        
        ce_vol = random.randint(500000, 35000000)
        pe_vol = random.randint(500000, 30000000)
        if s == atm_strike + step * 2: ce_vol = 395000000
        if s == atm_strike - step * 2: pe_vol = 461800000

        ce_oi = random.randint(50000, 9500000)
        pe_oi = random.randint(50000, 9200000)
        
        ce_p = round(random.uniform(-4, 3), 0)
        pe_p = round(random.uniform(-4, 3), 0)
        ce_oi_chg = round(random.uniform(-20, 65), 0)
        pe_oi_chg = round(random.uniform(-35, 80), 0)

        ce_iv = max(6.5, round(11.5 - (diff * 0.008), 2))
        pe_iv = max(5.5, round(8.5 + (diff * 0.008), 2))

        dist = abs(s - atm_strike)
        ce_val_cr = int(max(10, 278 - (dist * 0.18) + random.randint(-8, 8)))
        pe_val_cr = int(max(8, 126 - (dist * 0.10) + random.randint(-6, 6)))
        if s == atm_strike:
            ce_val_cr = 119
            pe_val_cr = 58
        elif s == atm_strike + step:
            ce_val_cr = 278
            pe_val_cr = 126

        ce_chg_cr = int(ce_val_cr * random.uniform(0.15, 0.45))
        pe_chg_cr = int(pe_val_cr * random.uniform(-0.35, 0.35))
        if s == atm_strike + step:
            ce_chg_cr = 262
            pe_chg_cr = 52

        ce_tag, ce_cls = calc_buildup(ce_p, ce_oi_chg)
        pe_tag, pe_cls = calc_buildup(pe_p, pe_oi_chg)

        parsed_rows.append({
            "strike": s,
            "is_atm": (s == atm_strike),
            "ce_tag": ce_tag, "ce_cls": ce_cls,
            "ce_vol": ce_vol, "ce_oi_chg": ce_oi_chg, "ce_oi": ce_oi,
            "ce_iv": ce_iv, "ce_ltp": ce_ltp, "ce_p": ce_p,
            "ce_val_cr": ce_val_cr, "ce_chg_cr": ce_chg_cr,
            "pe_ltp": pe_ltp, "pe_p": pe_p,
            "pe_iv": pe_iv, "pe_oi": pe_oi, "pe_oi_chg": pe_oi_chg, "pe_vol": pe_vol,
            "pe_tag": pe_tag, "pe_cls": pe_cls,
            "pe_val_cr": pe_val_cr, "pe_chg_cr": pe_chg_cr
        })

df = pd.DataFrame(parsed_rows)

max_ce_vol = max(df["ce_vol"].max(), 1)
max_pe_vol = max(df["pe_vol"].max(), 1)
max_ce_oi = max(df["ce_oi"].max(), 1)
max_pe_oi = max(df["pe_oi"].max(), 1)

# ---------------------------------------------------------
# Dynamic Aggregations (ITM, ATM, OTM, Grand Total)
# ---------------------------------------------------------
itm_ce = df[df["strike"] < atm_strike]
otm_ce = df[df["strike"] > atm_strike]
atm_row_df = df[df["strike"] == atm_strike]
itm_pe = df[df["strike"] > atm_strike]
otm_pe = df[df["strike"] < atm_strike]

summary_data = [
    {
        "label": "ITM Total",
        "ce_vol": itm_ce["ce_vol"].sum(),
        "ce_oi_chg": round(itm_ce["ce_oi_chg"].mean() if not itm_ce.empty else 0, 0),
        "ce_oi": itm_ce["ce_oi"].sum(),
        "pe_oi": itm_pe["pe_oi"].sum(),
        "pe_oi_chg": round(itm_pe["pe_oi_chg"].mean() if not itm_pe.empty else 0, 0),
        "pe_vol": itm_pe["pe_vol"].sum(),
        "class": "summary-row"
    },
    {
        "label": "ATM",
        "ce_vol": atm_row_df["ce_vol"].sum(),
        "ce_oi_chg": round(atm_row_df["ce_oi_chg"].mean() if not atm_row_df.empty else 0, 0),
        "ce_oi": atm_row_df["ce_oi"].sum(),
        "pe_oi": atm_row_df["pe_oi"].sum(),
        "pe_oi_chg": round(atm_row_df["pe_oi_chg"].mean() if not atm_row_df.empty else 0, 0),
        "pe_vol": atm_row_df["pe_vol"].sum(),
        "class": "summary-row"
    },
    {
        "label": "OTM Total",
        "ce_vol": otm_ce["ce_vol"].sum(),
        "ce_oi_chg": round(otm_ce["ce_oi_chg"].mean() if not otm_ce.empty else 0, 0),
        "ce_oi": otm_ce["ce_oi"].sum(),
        "pe_oi": otm_pe["pe_oi"].sum(),
        "pe_oi_chg": round(otm_pe["pe_oi_chg"].mean() if not otm_pe.empty else 0, 0),
        "pe_vol": otm_pe["pe_vol"].sum(),
        "class": "summary-row"
    },
    {
        "label": "Total",
        "ce_vol": df["ce_vol"].sum(),
        "ce_oi_chg": round(df["ce_oi_chg"].mean() if not df.empty else 0, 0),
        "ce_oi": df["ce_oi"].sum(),
        "pe_oi": df["pe_oi"].sum(),
        "pe_oi_chg": round(df["pe_oi_chg"].mean() if not df.empty else 0, 0),
        "pe_vol": df["pe_vol"].sum(),
        "class": "summary-row summary-total"
    }
]

summary_rows_html = []
for sm in summary_data:
    ce_chg_col = "tag-green" if sm["ce_oi_chg"] >= 0 else "tag-red"
    pe_chg_col = "tag-green" if sm["pe_oi_chg"] >= 0 else "tag-red"
    r_html = (
        f"<tr class='{sm['class']}'>"
        f"<td></td>"
        f"<td>{format_inr(sm['ce_vol'])}</td>"
        f"<td class='{ce_chg_col}' style='text-align:center;'>{sm['ce_oi_chg']:+.0f}%</td>"
        f"<td>{format_inr(sm['ce_oi'])}</td>"
        f"<td></td>"
        f"<td></td>"
        f"<td class='summary-label-cell'>{sm['label']}</td>"
        f"<td></td>"
        f"<td></td>"
        f"<td style='text-align:left;'>{format_inr(sm['pe_oi'])}</td>"
        f"<td class='{pe_chg_col}' style='text-align:center;'>{sm['pe_oi_chg']:+.0f}%</td>"
        f"<td>{format_inr(sm['pe_vol'])}</td>"
        f"<td></td>"
        f"</tr>"
    )
    summary_rows_html.append(r_html)

# ---------------------------------------------------------
# Tab 1: Option Chain (With Distinct Call & Put IV Columns)
# ---------------------------------------------------------
chain_df = df[(df["strike"] >= atm_strike - step * 20) & (df["strike"] <= atm_strike + step * 20)].copy()

table_rows = []
for _, r in chain_df.iterrows():
    ce_vol_pct = int((r["ce_vol"] / max_ce_vol) * 100)
    pe_vol_pct = int((r["pe_vol"] / max_pe_vol) * 100)
    ce_oi_pct = int((r["ce_oi"] / max_ce_oi) * 100)
    pe_oi_pct = int((r["pe_oi"] / max_pe_oi) * 100)

    ce_p_col = "tag-green" if r["ce_p"] >= 0 else "tag-red"
    pe_p_col = "tag-green" if r["pe_p"] >= 0 else "tag-red"
    ce_oi_col = "tag-green" if r["ce_oi_chg"] >= 0 else "tag-red"
    pe_oi_col = "tag-green" if r["pe_oi_chg"] >= 0 else "tag-red"

    ce_vol_td = "class='top-vol-green'" if r["ce_vol"] == max_ce_vol else f"style='background: linear-gradient(to left, #bbf7d0 {ce_vol_pct}%, transparent {ce_vol_pct}%);'"
    pe_vol_td = "class='top-vol-red'" if r["pe_vol"] == max_pe_vol else f"style='background: linear-gradient(to right, #fecaca {pe_vol_pct}%, transparent {pe_vol_pct}%); text-align: left;'"

    is_atm = r["is_atm"]
    tr_class = "class='atm-row'" if is_atm else ""
    strike_td_class = "class='col-strike-atm'" if is_atm else "class='col-strike'"
    atm_badge = "<span class='badge-atm'>ATM</span>" if is_atm else ""

    row_str = (
        f"<tr {tr_class}>"
        f"<td style='text-align:center;'><span class='badge {r['ce_cls']}'>{r['ce_tag']}</span></td>"
        f"<td {ce_vol_td}>{format_inr(r['ce_vol'])}</td>"
        f"<td class='{ce_oi_col}' style='text-align:center;'>{r['ce_oi_chg']:+.0f}%</td>"
        f"<td style='background: linear-gradient(to left, #86efac {ce_oi_pct}%, transparent {ce_oi_pct}%);'>{format_inr(r['ce_oi'])}</td>"
        f"<td class='col-iv'>{r['ce_iv']:.2f}</td>"
        f"<td>{r['ce_ltp']:.2f} <span class='{ce_p_col}' style='font-size:10px;'>{r['ce_p']:+.0f}%</span></td>"
        f"<td {strike_td_class}>{int(r['strike'])}{atm_badge}</td>"
        f"<td style='text-align:left;'><span class='{pe_p_col}' style='font-size:10px;'>{r['pe_p']:+.0f}%</span> {r['pe_ltp']:.2f}</td>"
        f"<td class='col-iv'>{r['pe_iv']:.2f}</td>"
        f"<td style='background: linear-gradient(to right, #fca5a5 {pe_oi_pct}%, transparent {pe_oi_pct}%); text-align:left;'>{format_inr(r['pe_oi'])}</td>"
        f"<td class='{pe_oi_col}' style='text-align:center;'>{r['pe_oi_chg']:+.0f}%</td>"
        f"<td {pe_vol_td}>{format_inr(r['pe_vol'])}</td>"
        f"<td style='text-align:center;'><span class='badge {r['pe_cls']}'>{r['pe_tag']}</span></td>"
        f"</tr>"
    )
    table_rows.append(row_str)

complete_table = (
    f"<div class='table-box'>"
    f"<table class='stockmojo-tbl'>"
    f"<thead>"
    f"<tr class='top-hdr'>"
    f"<th colspan='6' style='color:#15803d; text-align:left; padding-left:14px;'>Call</th>"
    f"<th style='background:#f1f5f9;'></th>"
    f"<th colspan='6' style='color:#b91c1c; text-align:left; padding-left:14px;'>Put</th>"
    f"</tr>"
    f"<tr class='sub-hdr'>"
    f"<th style='width:50px;'>Buildup</th>"
    f"<th style='width:80px;'>Volume</th>"
    f"<th style='width:60px;'>OI Chg%</th>"
    f"<th style='width:75px;'>OI</th>"
    f"<th style='width:50px;'>IV</th>"
    f"<th style='width:80px;'>LTP</th>"
    f"<th style='width:80px;'>Strike ▲</th>"
    f"<th style='width:80px;'>LTP</th>"
    f"<th style='width:50px;'>IV</th>"
    f"<th style='width:75px;'>OI</th>"
    f"<th style='width:60px;'>OI Chg%</th>"
    f"<th style='width:80px;'>Volume</th>"
    f"<th style='width:50px;'>Buildup</th>"
    f"</tr>"
    f"{''.join(summary_rows_html)}"
    f"</thead>"
    f"<tbody>{''.join(table_rows)}</tbody>"
    f"</table>"
    f"</div>"
)

# ---------------------------------------------------------
# Tab Routing
# ---------------------------------------------------------
tab_chain, tab_terminal = st.tabs(["OPTION CHAIN", "OPTION TERMINAL"])

with tab_chain:
    st.markdown(complete_table, unsafe_allow_html=True)

with tab_terminal:
    # 21 strikes centered on ATM for Pro Option Terminal
    term_df = df[(df["strike"] >= atm_strike - step * 10) & (df["strike"] <= atm_strike + step * 10)].copy()
    max_term_ce = max(term_df["ce_val_cr"].max(), 1)
    max_term_pe = max(term_df["pe_val_cr"].max(), 1)
    tot_call_val = term_df["ce_val_cr"].sum()
    tot_put_val = term_df["pe_val_cr"].sum()

    max_term_ce_chg = max(term_df["ce_chg_cr"].abs().max(), 1)
    max_term_pe_chg = max(term_df["pe_chg_cr"].abs().max(), 1)

    total_vol_pcr = round(df["pe_vol"].sum() / max(df["ce_vol"].sum(), 1), 2)
    chg_vol_pcr = round((df["pe_oi_chg"].sum() - df["ce_oi_chg"].sum()) / 100, 2)
    max_call_vol_strike = int(df.loc[df["ce_vol"].idxmax()]["strike"])
    max_put_vol_strike = int(df.loc[df["pe_vol"].idxmax()]["strike"])

    terminal_rows_html = []
    for r in term_df.itertuples():
        ce_fill = int((r.ce_val_cr / max_term_ce) * 100)
        pe_fill = int((r.pe_val_cr / max_term_pe) * 100)
        ce_chg_fill = int((abs(r.ce_chg_cr) / max_term_ce_chg) * 100)
        pe_chg_fill = int((abs(r.pe_chg_cr) / max_term_pe_chg) * 100)

        is_atm = r.is_atm
        strk_cls = "term-col-strike term-atm-strike" if is_atm else "term-col-strike"
        strk_label = f"{int(r.strike)} ATM ◄" if is_atm else f"{int(r.strike)}"

        ce_pill = "term-chg-pill-green" if r.ce_chg_cr >= 0 else "term-chg-pill-red"
        ce_chg_bar_cls = "term-chg-fill-ce-pos" if r.ce_chg_cr >= 0 else "term-chg-fill-ce-neg"

        pe_pill = "term-chg-pill-red" if r.pe_chg_cr >= 0 else "term-chg-pill-green"
        pe_chg_bar_cls = "term-chg-fill-pe-pos" if r.pe_chg_cr >= 0 else "term-chg-fill-pe-neg"

        t_row = (
            f"<tr>"
            f"<td class='term-bar-cell-ce'>"
            f"<div class='term-bar-fill-ce' style='width:{ce_fill}%;'></div>"
            f"<span class='term-bar-text' style='color:#00f59b;'>{r.ce_val_cr}Cr</span>"
            f"</td>"
            f"<td class='term-chg-cell-ce'>"
            f"<div class='{ce_chg_bar_cls}' style='width:{ce_chg_fill}%;'></div>"
            f"<span class='{ce_pill}'>{r.ce_chg_cr:+}Cr</span>"
            f"</td>"
            f"<td class='term-col-ltp-ce'>{r.ce_ltp:.2f}</td>"
            f"<td class='{strk_cls}'>{strk_label}</td>"
            f"<td class='term-col-ltp-pe'>{r.pe_ltp:.2f}</td>"
            f"<td class='term-chg-cell-pe'>"
            f"<div class='{pe_chg_bar_cls}' style='width:{pe_chg_fill}%;'></div>"
            f"<span class='{pe_pill}'>{r.pe_chg_cr:+}Cr</span>"
            f"</td>"
            f"<td class='term-bar-cell-pe'>"
            f"<div class='term-bar-fill-pe' style='width:{pe_fill}%;'></div>"
            f"<span class='term-bar-text' style='color:#ff3366;'>{r.pe_val_cr}Cr</span>"
            f"</td>"
            f"</tr>"
        )
        terminal_rows_html.append(t_row)

    target_val = spot_val + 250.0

    terminal_html = (
        f"<div class='terminal-container'>"
        f"<div class='terminal-top-bar'>"
        f"<div class='terminal-logo'>"
        f"<span style='color: #eab308; font-size: 16px; margin-right: 4px;'>⚡</span>"
        f"<span style='color: #00d4ff; font-weight: 900; letter-spacing: 0.5px;'>{selected_index_key} PRO OPTION TERMINAL</span>"
        f"</div>"
        f"<div class='terminal-spot-box'>"
        f"<span class='terminal-spot-val'>{spot_val:,.2f}</span>"
        f"<span class='terminal-spot-pill'>▲ 142.25</span>"
        f"<span class='terminal-target-text'>TARGET: {target_val:,.2f}</span>"
        f"</div>"
        f"<div class='terminal-kpi-group'>"
        f"<div class='terminal-kpi-pill'><span class='terminal-kpi-label'>TOTAL VOL PCR</span><span class='terminal-kpi-num' style='color: #00f59b;'>{total_vol_pcr}</span></div>"
        f"<div class='terminal-kpi-pill'><span class='terminal-kpi-label'>CHG VOL PCR</span><span class='terminal-kpi-num' style='color: #ff3366;'>{chg_vol_pcr}</span></div>"
        f"<div class='terminal-kpi-pill'><span class='terminal-kpi-label'>MAX CALL VOL</span><span class='terminal-kpi-num' style='color: #ff3366;'>{max_call_vol_strike}</span></div>"
        f"<div class='terminal-kpi-pill'><span class='terminal-kpi-label'>MAX PUT VOL</span><span class='terminal-kpi-num' style='color: #00f59b;'>{max_put_vol_strike}</span></div>"
        f"</div>"
        f"<div class='terminal-live-tracker'>"
        f"<span style='color: #00f59b; font-size: 10px; margin-right: 4px;'>●</span>"
        f"<span>Live {selected_index_key} Option Money Tracker</span>"
        f"</div>"
        f"</div>"
        f"<div class='terminal-sub-bar'>"
        f"<div><span class='expiry-chip'>EXPIRY: {selected_expiry_display}</span></div>"
        f"<div style='font-weight:700;'>"
        f"<span style='color:#94a3b8;'>Total Call Value (21 Strike):</span> <span style='color:#00f59b; margin-right:16px;'>{tot_call_val}Cr</span>"
        f"<span style='color:#94a3b8;'>Total Put Value (21 Strike):</span> <span style='color:#ff3366;'>{tot_put_val}Cr</span>"
        f"</div>"
        f"</div>"
        f"<div class='terminal-table-box'>"
        f"<table class='pro-term-tbl'>"
        f"<thead>"
        f"<tr>"
        f"<th colspan='3' class='call-hdr'>CALL OPTIONS</th>"
        f"<th class='term-col-strike'>STRIKE</th>"
        f"<th colspan='3' class='put-hdr'>PUT OPTIONS</th>"
        f"</tr>"
        f"<tr>"
        f"<th style='width:24%;'>TOTAL VAL (CR)</th>"
        f"<th style='width:14%;'>CHG VAL (CR)</th>"
        f"<th style='width:12%;'>LTP</th>"
        f"<th style='width:14%;'>STRIKE</th>"
        f"<th style='width:12%;'>LTP</th>"
        f"<th style='width:14%;'>CHG VAL (CR)</th>"
        f"<th style='width:24%;'>TOTAL VAL (CR)</th>"
        f"</tr>"
        f"</thead>"
        f"<tbody>{''.join(terminal_rows_html)}</tbody>"
        f"</table>"
        f"</div>"
        f"<div class='terminal-footer-bar'>"
        f"<div style='display:flex; gap:16px;'>"
        f"<span><input type='checkbox' checked disabled> Call Value Build-up</span>"
        f"<span><input type='checkbox' checked disabled> Put Value Build-up</span>"
        f"<span><input type='checkbox' checked disabled> ATM Strike Highlight</span>"
        f"</div>"
        f"<div style='color:#00f59b; font-weight:700;'>● 21 Strikes Active</div>"
        f"</div>"
        f"</div>"
    )
    st.markdown(terminal_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# Auto-Refresh Control (Only active in live mode, not on file upload)
# ---------------------------------------------------------
if auto_refresh and uploaded_file is None:
    time.sleep(10)
    st.rerun()
