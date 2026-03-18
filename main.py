#!/usr/bin/env python3
"""
BTC Price Alert System
Monitor BTC/USDT price from Binance and get notified when targets are hit.
"""

import argparse
import json
import os
import signal
import sys
import time
from datetime import datetime

import requests

ALERTS_FILE = "alerts.json"
BINANCE_URL = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"


def load_alerts() -> list[dict]:
    """Load alerts from JSON file."""
    if not os.path.exists(ALERTS_FILE):
        return []
    with open(ALERTS_FILE, "r") as f:
        return json.load(f)


def save_alerts(alerts: list[dict]) -> None:
    """Save alerts to JSON file."""
    with open(ALERTS_FILE, "w") as f:
        json.dump(alerts, f, indent=2)


def get_btc_price() -> float:
    """Fetch current BTC/USDT price from Binance."""
    try:
        resp = requests.get(BINANCE_URL, timeout=10)
        resp.raise_for_status()
        return float(resp.json()["price"])
    except requests.RequestException as e:
        print(f"❌ Error fetching price: {e}")
        sys.exit(1)


def check_price() -> None:
    """Print current BTC price."""
    price = get_btc_price()
    print(f"₿ BTC/USDT: ${price:,.2f}")


def set_alert(direction: str, price: float, note: str = "") -> None:
    """Add a new price alert."""
    alerts = load_alerts()
    alert = {
        "id": len(alerts) + 1,
        "direction": direction,  # "above" or "below"
        "target": price,
        "note": note,
        "created": datetime.now().isoformat(),
        "triggered": False,
    }
    alerts.append(alert)
    save_alerts(alerts)
    arrow = "📈" if direction == "above" else "📉"
    print(f"{arrow} Alert set: BTC {'above' if direction == 'above' else 'below'} ${price:,.2f} [#{alert['id']}]")


def list_alerts() -> None:
    """List all alerts."""
    alerts = load_alerts()
    if not alerts:
        print("📭 No alerts set.")
        return
    print(f"📋 Alerts ({len(alerts)}):")
    print("-" * 60)
    for a in alerts:
        status = "✅ Triggered" if a["triggered"] else "⏳ Active"
        arrow = "📈 above" if a["direction"] == "above" else "📉 below"
        note = f" — {a['note']}" if a.get("note") else ""
        print(f"  #{a['id']} {arrow} ${a['target']:,.2f} | {status}{note}")
    print("-" * 60)


def remove_alert(alert_id: int) -> None:
    """Remove an alert by ID."""
    alerts = load_alerts()
    new_alerts = [a for a in alerts if a["id"] != alert_id]
    if len(new_alerts) == len(alerts):
        print(f"❌ Alert #{alert_id} not found.")
        sys.exit(1)
    save_alerts(new_alerts)
    print(f"🗑️ Alert #{alert_id} removed.")


def watch(interval: int = 60) -> None:
    """Watch BTC price and trigger alerts."""
    alerts = load_alerts()
    active = [a for a in alerts if not a["triggered"]]
    if not active:
        print("📭 No active alerts. Set one first!")
        sys.exit(1)

    print(f"👀 Watching BTC price (check every {interval}s, Ctrl+C to stop)")
    print(f"   {len(active)} active alert(s)")
    print("-" * 40)

    stop = False

    def handler(sig, frame):
        nonlocal stop
        stop = True
        print("\n⏹️ Stopped.")

    signal.signal(signal.SIGINT, handler)

    while not stop:
        price = get_btc_price()
        now = datetime.now().strftime("%H:%M:%S")
        print(f"  [{now}] BTC: ${price:,.2f}")

        alerts = load_alerts()
        changed = False
        for a in alerts:
            if a["triggered"]:
                continue
            triggered = (
                (a["direction"] == "above" and price >= a["target"])
                or (a["direction"] == "below" and price <= a["target"])
            )
            if triggered:
                a["triggered"] = True
                a["triggered_at"] = datetime.now().isoformat()
                changed = True
                arrow = "📈" if a["direction"] == "above" else "📉"
                note = f" ({a['note']})" if a.get("note") else ""
                print(f"\n  🚨 ALERT #{a['id']}{arrow} BTC ${price:,.2f} — Target: ${a['target']:,.2f}{note}\n")

        if changed:
            save_alerts(alerts)
            remaining = sum(1 for a in alerts if not a["triggered"])
            if remaining == 0:
                print("✅ All alerts triggered! Done.")
                break

        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(
        description="₿ BTC Price Alert — Monitor Bitcoin and get notified",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py price                        Check current BTC price
  python main.py set --above 100000           Alert when BTC > $100k
  python main.py set --below 80000            Alert when BTC < $80k
  python main.py set --above 120000 -n "ATH!" Alert with note
  python main.py list                         Show all alerts
  python main.py remove 3                     Remove alert #3
  python main.py watch                        Start watching
  python main.py watch --interval 30          Check every 30 seconds
        """,
    )
    sub = parser.add_subparsers(dest="command")

    # price
    sub.add_parser("price", help="Check current BTC price")

    # set
    set_p = sub.add_parser("set", help="Set a new price alert")
    set_p.add_argument("--above", type=float, help="Alert when price goes above this value")
    set_p.add_argument("--below", type=float, help="Alert when price goes below this value")
    set_p.add_argument("-n", "--note", type=str, default="", help="Note for this alert")

    # list
    sub.add_parser("list", help="List all alerts")

    # remove
    rem_p = sub.add_parser("remove", help="Remove an alert")
    rem_p.add_argument("id", type=int, help="Alert ID to remove")

    # watch
    watch_p = sub.add_parser("watch", help="Start watching prices")
    watch_p.add_argument("--interval", type=int, default=60, help="Check interval in seconds (default: 60)")

    args = parser.parse_args()

    if args.command == "price":
        check_price()
    elif args.command == "set":
        if not args.above and not args.below:
            parser.error("Specify --above or --below")
        if args.above:
            set_alert("above", args.above, args.note)
        if args.below:
            set_alert("below", args.below, args.note)
    elif args.command == "list":
        list_alerts()
    elif args.command == "remove":
        remove_alert(args.id)
    elif args.command == "watch":
        watch(args.interval)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
