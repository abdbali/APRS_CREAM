import network
import socket
import time
from machine import Timer

# APRS Configurations
CALLSIGN = "YOUR_CALLSIGN"
SSID = "0"
PASSCODE = 12345  # Your calculated passcode
LAT = 40.7128     # Example latitude
LON = -74.0060    # Example longitude
SYMBOL_TABLE = '/'
SYMBOL = '>'
COMMENT = "ESP32 via APRS"
SERVER = "rotate.aprs2.net"
PORT = 14580
INTERVAL = 300  # Update interval in seconds

# WiFi Configuration
SSID_WIFI = "your_wifi_ssid"
PASSWORD_WIFI = "your_wifi_password"

# Connect to WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID_WIFI, PASSWORD_WIFI)
    
    while not wlan.isconnected():
        print('Connecting to WiFi...')
        time.sleep(1)
    print('Connected to WiFi:', wlan.ifconfig())

# APRS Position Formatters
def aprs_lat_format(latitude):
    lat_deg = int(abs(latitude))
    lat_min = (abs(latitude) - lat_deg) * 60
    direction = 'N' if latitude >= 0 else 'S'
    return f"{lat_deg:02d}{lat_min:05.2f}{direction}"

def aprs_lon_format(longitude):
    lon_deg = int(abs(longitude))
    lon_min = (abs(longitude) - lon_deg) * 60
    direction = 'E' if longitude >= 0 else 'W'
    return f"{lon_deg:03d}{lon_min:05.2f}{direction}"

# APRS Message Sender
def send_aprs_position():
    lat_str = aprs_lat_format(LAT)
    lon_str = aprs_lon_format(LON)
    
    aprs_position = f"{CALLSIGN}-{SSID}>APRS,TCPIP*:!{lat_str}{SYMBOL_TABLE}{lon_str}{SYMBOL}{COMMENT}\n"
    
    try:
        addr_info = socket.getaddrinfo(SERVER, PORT)[0][-1]
        s = socket.socket()
        s.connect(addr_info)
        login_cmd = f"user {CALLSIGN} pass {PASSCODE} vers ESP32 1.0\n"
        s.send(login_cmd.encode())
        s.send(aprs_position.encode())
        print('Position sent to APRS server.')
        s.close()
    except Exception as e:
        print("Error:", e)

# Timer for APRS position sharing
def start_aprs():
    connect_wifi()
    
    # Repeat APRS position sharing every INTERVAL seconds
    tim = Timer(-1)
    tim.init(period=INTERVAL * 1000, mode=Timer.PERIODIC, callback=lambda t: send_aprs_position())

# Start APRS position sharing
start_aprs()
