# Crypto Fee Tracker

A lightweight macOS menu bar application that displays real-time cryptocurrency transaction fees for Ethereum and Bitcoin.

![Menu Bar Preview](https://img.shields.io/badge/Platform-macOS-blue)
![Python](https://img.shields.io/badge/Python-3.6+-green)
![License](https://img.shields.io/badge/License-MIT-orange)

## Features

### 📊 **Real-time Fee Monitoring**
- **Ethereum Gas Prices**: Safe and Fast gas prices in gwei
- **Bitcoin Transaction Fees**: Safe (70% confidence) and Fast (99% confidence) fees in sat/vB
- Updates every 30 seconds automatically

### 🔄 **Easy Chain Switching**
- Switch between Ethereum and Bitcoin with one click
- Visual indicators: `Ξ` for Ethereum, `₿` for Bitcoin
- Remembers your preference between sessions

### ⚙️ **Smart Configuration**
- Optional Etherscan API key support for higher rate limits
- Auto-startup option (launches silently at login)
- Persistent settings storage

### 🎨 **Native macOS Integration**
- Clean menu bar interface
- No dock icon (background-only app)
- Official cryptocurrency symbols
- Follows macOS design guidelines

## Screenshots

**Ethereum Gas Prices:**
```
Ξ S:12.34 F:15.67
```

**Bitcoin Transaction Fees:**
```
₿ S:1.23 F:3.45
```

## Installation

### Option 1: Download Pre-built App
1. Download the latest release from [Releases](https://github.com/pulsanoracle/macos_gas_tracker/releases)
2. Unzip and move `Crypto Fee Tracker.app` to your Applications folder
3. Right-click → Open (first time only for security)

### Option 2: Build from Source

**Prerequisites:**
- Python 3.6 or higher
- macOS 10.14+ (Mojave or later)

**Setup:**
```bash
# Clone the repository
git clone https://github.com/pulsanoracle/macos_gas_tracker.git
cd macos_gas_tracker

# Install dependencies
pip install rumps requests

# Run directly
python3 gas.py
```

**Build standalone app:**
```bash
# Install PyInstaller
pip install pyinstaller

# Build the app
pyinstaller --onefile --windowed --name "Crypto Fee Tracker" gas.py

# Find your app in dist/
open dist/
```

## Configuration

### API Key (Optional but Recommended)
1. Get a free API key from [Etherscan.io](https://etherscan.io/apis)
2. Click the menu bar icon → "API Key Settings"
3. Enter your API key and save

**Benefits of API Key:**
- Higher rate limits (5 calls/second vs 1/5 seconds)
- More reliable service during high traffic
- Priority access to Etherscan data

### Auto-startup
1. Click menu bar icon → "Auto-start Settings"
2. Launches silently at login (no Terminal window)
3. Only works with the packaged app version

## Menu Options

- **Refresh Now**: Manually update prices
- **Switch to Ethereum**: Monitor ETH gas prices
- **Switch to Bitcoin**: Monitor BTC transaction fees
- **API Key Settings**: Configure Etherscan API key
- **Auto-start Settings**: Toggle startup behavior
- **About**: View app information

## Data Sources

- **Ethereum**: [Etherscan API v2](https://docs.etherscan.io/etherscan-v2) - Gas Oracle endpoint
- **Bitcoin**: [Blocknative API](https://api.blocknative.com) - Bitcoin fee estimation

## Technical Details

**Built with:**
- Python 3
- [rumps](https://github.com/jaredks/rumps) - macOS menu bar framework
- [requests](https://docs.python-requests.org/) - HTTP library

**Architecture:**
- Background thread for API updates
- 30-second refresh interval
- Graceful error handling with automatic retry
- Persistent configuration storage

## Troubleshooting

### App won't start
- Make sure you're running the packaged app, not the Python script
- Check System Preferences → Security & Privacy → General

### No prices showing
- Check your internet connection
- Verify API services are accessible
- Look for error messages in the menu bar

### Auto-start not working
- Only works with the packaged .app version
- Grant accessibility permissions if prompted
- Manually check System Preferences → Users & Groups → Login Items

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -m 'Add feature-name'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## Roadmap

- [ ] Additional cryptocurrency support (Polygon, BSC, etc.)
- [ ] Customizable refresh intervals
- [ ] Price alerts and notifications
- [ ] Historical fee charts
- [ ] Dark/light mode themes

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Etherscan](https://etherscan.io) for Ethereum data
- [Blocknative](https://blocknative.com) for Bitcoin fee estimates
- [rumps](https://github.com/jaredks/rumps) for the macOS menu bar framework

## Support

If you find this project helpful, consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs or requesting features
- 💡 Contributing improvements

---

**Disclaimer:** This tool is for informational purposes only. Always verify transaction fees before making cryptocurrency transactions.
