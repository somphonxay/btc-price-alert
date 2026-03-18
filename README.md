# ₿ BTC Price Alert

Simple CLI tool to monitor Bitcoin (BTC/USDT) price from Binance and get notified when your target price is hit.

## Features

- ⚡ Real-time BTC/USDT price from Binance public API (no API key needed)
- 📈📉 Set alerts for price above or below a threshold
- 🔔 Multiple concurrent alerts
- 💾 Persistent alert storage (JSON file)
- ⏱️ Configurable check interval (default: 60s)
- 📝 Optional notes on each alert

## Install

```bash
pip install -r requirements.txt
```

## Usage

### Check current price
```bash
python main.py price
```

### Set alerts
```bash
# Alert when BTC goes above $100,000
python main.py set --above 100000

# Alert when BTC drops below $80,000
python main.py set --below 80000

# Add a note
python main.py set --above 120000 -n "New ATH zone!"
```

### List all alerts
```bash
python main.py list
```

### Remove an alert
```bash
python main.py remove 3
```

### Start watching
```bash
# Check every 60 seconds (default)
python main.py watch

# Custom interval (30 seconds)
python main.py watch --interval 30
```

Press `Ctrl+C` to stop watching.

## Example Output

```
$ python main.py price
₿ BTC/USDT: $84,523.17

$ python main.py set --above 100000
📈 Alert set: BTC above $100,000.00 [#1]

$ python main.py watch
👀 Watching BTC price (check every 60s, Ctrl+C to stop)
   1 active alert(s)
----------------------------------------
  [13:45:01] BTC: $84,523.17
  [13:46:01] BTC: $84,612.33

  🚨 ALERT #1📈 BTC $100,234.50 — Target: $100,000.00

✅ All alerts triggered! Done.
```

## License

MIT
