import threading
import time
import urllib.request
import json
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, clear_output

# ── City Definitions ──────────────────────────────────────────────────────────
CITIES = [
    {"name": "Kathmandu",  "lat": 27.7172, "lon": 85.3240},
    {"name": "Pokhara",    "lat": 28.2096, "lon": 83.9856},
    {"name": "Biratnagar", "lat": 26.4525, "lon": 87.2718},
    {"name": "Nepalgunj",  "lat": 28.0500, "lon": 81.6167},
    {"name": "Dhangadhi",  "lat": 28.6833, "lon": 80.5833},
]

# ── Fetch Logic ───────────────────────────────────────────────────────────────
def fetch_weather(city, results, lock):
    url = (f"https://api.open-meteo.com/v1/forecast?"
           f"latitude={city['lat']}&longitude={city['lon']}"
           f"&current_weather=true&hourly=relativehumidity_2m")
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            cw = data.get("current_weather", {})
            hum = data.get("hourly", {}).get("relativehumidity_2m", [None])[0]
            result = {
                "temp": cw.get("temperature", "N/A"),
                "wind": cw.get("windspeed", "N/A"),
                "humidity": hum if hum is not None else "N/A",
                "status": "OK"
            }
    except Exception as e:
        result = {"temp": "ERR", "wind": "ERR", "humidity": "ERR", "status": str(e)}

    with lock:
        results[city["name"]] = result

# ── Comparison Logic ──────────────────────────────────────────────────────────
def run_comparison(out_area):
    results_par = {}
    results_seq = {}
    lock = threading.Lock()

    with out_area:
        clear_output(wait=True)
        print("🚀 Starting comparison... Please wait.")

        # 1. Sequential Fetch
        t0_seq = time.perf_counter()
        for city in CITIES:
            fetch_weather(city, results_seq, lock)
        latency_seq = time.perf_counter() - t0_seq

        # 2. Parallel Fetch
        threads = [threading.Thread(target=fetch_weather, args=(c, results_par, lock)) for c in CITIES]
        t0_par = time.perf_counter()
        for th in threads: th.start()
        for th in threads: th.join()
        latency_par = time.perf_counter() - t0_par

        # ── Display Results ──
        clear_output(wait=True)
        print(f"✅ Comparison Complete!")
        print(f"Sequential Time: {latency_seq:.2f}s")
        print(f"Parallel Time:   {latency_par:.2f}s")
        print(f"Speedup:         {latency_seq/latency_par:.2f}x faster\n")

        # Table Output
        print(f"{'City':<15} | {'Temp (°C)':<10} | {'Humidity %':<10} | {'Status'}")
        print("-" * 55)
        for city in CITIES:
            r = results_par[city['name']]
            print(f"{city['name']:<15} | {r['temp']:<10} | {r['humidity']:<10} | {r['status']}")

        # Plotting
        
        plt.figure(figsize=(8, 4))
        bars = plt.bar(["Sequential", "Parallel"], [latency_seq, latency_par], color=['#E05252', '#2E75B6'])
        plt.ylabel("Seconds")
        plt.title("Network Latency: Sequential vs Parallel Threads")
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval + 0.05, f'{yval:.2f}s', ha='center', va='bottom')
        plt.show()

# ── Interface ─────────────────────────────────────────────────────────────────
output = widgets.Output()
btn = widgets.Button(description="Compare Latency", button_style='primary', icon='check')

def on_button_clicked(b):
    run_comparison(output)

btn.on_click(on_button_clicked)

print("Weather Monitor: Multi-threaded Comparison")
display(btn, output)