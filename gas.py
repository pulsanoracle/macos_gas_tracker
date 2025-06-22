#!/usr/bin/env python3
import rumps
import requests
import threading
import time
import os
import json
import subprocess
import sys

class EthGasPriceApp(rumps.App):
    def __init__(self):
        super(EthGasPriceApp, self).__init__("Loading...")
        
        # Hide from Dock - make it menu bar only
        try:
            import AppKit
            if AppKit.NSApp:
                AppKit.NSApp.setActivationPolicy_(AppKit.NSApplicationActivationPolicyAccessory)
        except (ImportError, AttributeError):
            pass  # Not on macOS or AppKit not available
        
        self.title = "Loading..."
        self.eth_base_url = "https://api.etherscan.io/v2/api"
        self.btc_base_url = "https://api.blocknative.com/gasprices/blockprices"
        self.config_file = os.path.expanduser("~/.eth_gas_tracker_config.json")
        self.api_key = self.load_api_key()
        self.current_chain = self.load_chain_selection()
        
        # Start the background update thread
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
    
    def load_api_key(self):
        """Load API key from config file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('api_key', '')
        except Exception as e:
            print(f"Error loading config: {e}")
        return ''
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
        return {}
    
    def save_config(self, config):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
            rumps.alert("Error", f"Could not save configuration: {e}")
    
    def is_auto_start_enabled(self):
        """Check if auto-start is enabled"""
        config = self.load_config()
        return config.get('auto_start', False)
    
    def load_chain_selection(self):
        """Load selected chain from config"""
        config = self.load_config()
        return config.get('chain', 'ethereum')  # Default to ethereum
    
    def save_chain_selection(self, chain):
        """Save selected chain to config"""
        config = self.load_config()
        config['chain'] = chain
        self.save_config(config)
        self.current_chain = chain
    
    def save_api_key(self, api_key):
        """Save API key to config file"""
        try:
            config = self.load_config()
            config['api_key'] = api_key
            self.save_config(config)
            self.api_key = api_key
        except Exception as e:
            print(f"Error saving config: {e}")
            rumps.alert("Error", f"Could not save API key: {e}")
    
    def toggle_auto_start(self):
        """Toggle auto-start setting"""
        config = self.load_config()
        current_state = config.get('auto_start', False)
        new_state = not current_state
        config['auto_start'] = new_state
        self.save_config(config)
        
        app_name = "Ethereum Gas Price Tracker"
        if new_state:
            self.enable_auto_start()
            rumps.alert("Auto-start Enabled", f"{app_name} will now start automatically when you log in.")
        else:
            self.disable_auto_start()
            rumps.alert("Auto-start Disabled", f"{app_name} will no longer start automatically.")
    
    def enable_auto_start(self):
        """Add app to login items"""
        try:
            # Get the correct app path
            if getattr(sys, 'frozen', False):
                # Running as PyInstaller bundle
                app_path = sys.executable
                app_name = os.path.basename(app_path)
            else:
                # Running as Python script - not ideal for auto-start
                rumps.alert("Auto-start Warning", "Auto-start works best with the packaged app. Consider using the .app version for auto-start.")
                return
            
            # Use osascript to add to login items
            script = f'''
            tell application "System Events"
                make login item at end with properties {{path:"{app_path}", hidden:true, name:"{app_name}"}}
            end tell
            '''
            subprocess.run(['osascript', '-e', script], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error enabling auto-start: {e}")
            rumps.alert("Error", "Could not enable auto-start. Please add manually in System Preferences > Users & Groups > Login Items.")
    
    def disable_auto_start(self):
        """Remove app from login items"""
        try:
            # Get app name for removal
            if getattr(sys, 'frozen', False):
                app_name = os.path.basename(sys.executable)
            else:
                app_name = "Ethereum Gas Price Tracker"
                
            script = f'''
            tell application "System Events"
                delete login item "{app_name}"
            end tell
            '''
            subprocess.run(['osascript', '-e', script], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error disabling auto-start: {e}")
            # Silently fail - login item might not exist
    
    def build_api_url(self):
        """Build API URL based on selected chain"""
        if self.current_chain == 'ethereum':
            url = f"{self.eth_base_url}?chainid=1&module=gastracker&action=gasoracle"
            if self.api_key:
                url += f"&apikey={self.api_key}"
            return url
        elif self.current_chain == 'bitcoin':
            return f"{self.btc_base_url}?chainid=0"
    
    def update_loop(self):
        """Background thread to update gas prices every 30 seconds"""
        while True:
            try:
                self.update_gas_price()
                time.sleep(30)  # Update every 30 seconds
            except Exception as e:
                print(f"Error in update loop: {e}")
                self.title = "Error"
                time.sleep(30)
    
    def update_gas_price(self):
        """Fetch and update gas price from selected chain API"""
        try:
            api_url = self.build_api_url()
            print(f"Fetching from: {api_url}")  # Debug output
            response = requests.get(api_url, timeout=10)
            
            print(f"HTTP Status: {response.status_code}")  # Debug output
            response.raise_for_status()
            
            data = response.json()
            print(f"API Response: {data}")  # Debug output
            
            if self.current_chain == 'ethereum':
                self.process_ethereum_data(data)
            elif self.current_chain == 'bitcoin':
                self.process_bitcoin_data(data)
                
        except requests.exceptions.Timeout:
            print(f"Request timeout after 10 seconds")
            self.title = f"{'₿' if self.current_chain == 'bitcoin' else 'Ξ'} Timeout"
        except requests.exceptions.ConnectionError:
            print(f"Connection error - network may be down")
            self.title = f"{'₿' if self.current_chain == 'bitcoin' else 'Ξ'} No Network"
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
            icon = '₿' if self.current_chain == 'bitcoin' else 'Ξ'
            if response.status_code == 429:
                self.title = f"{icon} Rate Limited"
            elif response.status_code == 403:
                self.title = f"{icon} API Key Issue"
            else:
                self.title = f"{icon} HTTP {response.status_code}"
        except requests.RequestException as e:
            print(f"Network error: {e}")
            self.title = f"{'₿' if self.current_chain == 'bitcoin' else 'Ξ'} Network Error"
        except (KeyError, ValueError) as e:
            print(f"Data parsing error: {e}")
            self.title = f"{'₿' if self.current_chain == 'bitcoin' else 'Ξ'} Parse Error"
        except Exception as e:
            print(f"Unexpected error: {e}")
            self.title = f"{'₿' if self.current_chain == 'bitcoin' else 'Ξ'} Error"
    
    def process_ethereum_data(self, data):
        """Process Ethereum gas price data"""
        if data.get('status') == '1' and data.get('result'):
            safe_price = float(data['result']['SafeGasPrice'])
            fast_price = float(data['result']['FastGasPrice'])
            
            print(f"ETH - Safe: {safe_price}, Fast: {fast_price}")  # Debug output
            
            # Update the menu bar title with Ethereum gas prices (gwei)
            self.title = f"Ξ S:{safe_price:.2f} F:{fast_price:.2f}"
            
        else:
            error_msg = data.get('message', 'Unknown error')
            print(f"Ethereum API Error - Status: {data.get('status')}, Message: {error_msg}")
            
            # Show more specific error in menu bar
            if 'rate limit' in error_msg.lower():
                self.title = "Ξ Rate Limited"
            elif 'invalid' in error_msg.lower():
                self.title = "Ξ Invalid API"
            else:
                self.title = "Ξ API Error"
    
    def process_bitcoin_data(self, data):
        """Process Bitcoin fee data"""
        if data.get('blockPrices') and len(data['blockPrices']) > 0:
            block_prices = data['blockPrices'][0]
            estimated_prices = block_prices.get('estimatedPrices', [])
            
            # Find confidence 70 (safe) and confidence 99 (fast)
            safe_price = None
            fast_price = None
            
            for price_data in estimated_prices:
                if price_data['confidence'] == 70:
                    safe_price = price_data['price']
                elif price_data['confidence'] == 99:
                    fast_price = price_data['price']
            
            if safe_price is not None and fast_price is not None:
                print(f"BTC - Safe (70%): {safe_price}, Fast (99%): {fast_price}")  # Debug output
                
                # Update the menu bar title with Bitcoin fees (sat/vB) - 2 decimal places
                self.title = f"₿ S:{safe_price:.2f} F:{fast_price:.2f}"
            else:
                print(f"Bitcoin API Error - Could not find confidence 70 or 99")
                self.title = "₿ Data Error"
        else:
            print(f"Bitcoin API Error - No block prices data")
            self.title = "₿ API Error"
    
    @rumps.clicked("Refresh Now")
    def refresh_now(self, _):
        """Menu item to manually refresh gas prices"""
        threading.Thread(target=self.update_gas_price, daemon=True).start()
    
    @rumps.clicked("Switch to Ethereum")
    def switch_to_ethereum(self, _):
        """Switch to Ethereum monitoring"""
        if self.current_chain != 'ethereum':
            self.save_chain_selection('ethereum')
            # Immediately update with new chain
            self.title = "Loading..."
            threading.Thread(target=self.update_gas_price, daemon=True).start()
    
    @rumps.clicked("Switch to Bitcoin")
    def switch_to_bitcoin(self, _):
        """Switch to Bitcoin monitoring"""
        if self.current_chain != 'bitcoin':
            self.save_chain_selection('bitcoin')
            # Immediately update with new chain
            self.title = "Loading..."
            threading.Thread(target=self.update_gas_price, daemon=True).start()
    
    @rumps.clicked("API Key Settings")
    def api_key_settings(self, _):
        """Menu item to configure API key"""
        if self.current_chain == 'bitcoin':
            rumps.alert("API Key Not Needed", "Bitcoin fee data doesn't require an API key.\n\nAPI key is only used for Ethereum gas prices.")
            return
            
        current_key = "Set" if self.api_key else "Not Set"
        response = rumps.Window(
            title="Etherscan API Key Configuration",
            message=f"Current API Key: {current_key}\n\nEnter your Etherscan API key (optional but recommended for Ethereum):",
            default_text=self.api_key,
            ok="Save",
            cancel="Cancel",
            dimensions=(400, 160)
        ).run()
        
        if response.clicked:
            new_key = response.text.strip()
            self.save_api_key(new_key)
            if new_key:
                rumps.alert("Success", "API key saved successfully!")
            else:
                rumps.alert("Info", "API key cleared. Using public API access.")
            # Refresh gas price with new API key
            threading.Thread(target=self.update_gas_price, daemon=True).start()
    
    @rumps.clicked("Auto-start Settings")
    def auto_start_settings(self, _):
        """Menu item to toggle auto-start"""
        self.toggle_auto_start()
    
    @rumps.clicked("About")
    def about(self, _):
        """Show about dialog"""
        chain_name = self.current_chain.title()
        
        if self.current_chain == 'ethereum':
            api_status = "With API Key" if self.api_key else "Public Access"
            unit = "gwei"
        else:
            api_status = "No API Key Needed"
            unit = "sat/vB"
            
        auto_start_status = "Enabled" if self.is_auto_start_enabled() else "Disabled"
        
        rumps.alert("Crypto Fee Tracker", 
                   f"Real-time {chain_name} fees in your menu bar.\n\nS = Safe (70% confidence)\nF = Fast (99% confidence)\nUnit: {unit}\n\nCurrent Chain: {chain_name}\nAPI Status: {api_status}\nAuto-start: {auto_start_status}")

if __name__ == "__main__":
    app = EthGasPriceApp()
    app.run()