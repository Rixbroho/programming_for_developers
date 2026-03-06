import tkinter as tk
from tkinter import ttk, messagebox
from itertools import permutations
import math

# ── Tourist Spot Dataset ──────────────────────────────────────────────────────
SPOTS = [
    {"name": "Pashupatinath Temple",    "lat": 27.7104, "lon": 85.3488,
     "fee": 100,  "visit": 70,  "open": "06:00", "close": "18:00",
     "tags": ["culture", "religious"],  "rating": 9.5},
    {"name": "Swayambhunath Stupa",     "lat": 27.7149, "lon": 85.2906,
     "fee": 200,  "visit": 60,  "open": "07:00", "close": "17:00",
     "tags": ["culture", "heritage"],   "rating": 9.2},
    {"name": "Garden of Dreams",        "lat": 27.7125, "lon": 85.3170,
     "fee": 150,  "visit": 45,  "open": "09:00", "close": "21:00",
     "tags": ["nature", "relaxation"],  "rating": 8.0},
    {"name": "Chandragiri Hills",       "lat": 27.6616, "lon": 85.2458,
     "fee": 700,  "visit": 120, "open": "09:00", "close": "17:00",
     "tags": ["nature", "adventure"],   "rating": 8.8},
    {"name": "Kathmandu Durbar Square", "lat": 27.7048, "lon": 85.3076,
     "fee": 100,  "visit": 75,  "open": "10:00", "close": "17:00",
     "tags": ["culture", "heritage"],   "rating": 8.6},
    {"name": "Boudhanath Stupa",        "lat": 27.7215, "lon": 85.3620,
     "fee": 400,  "visit": 55,  "open": "06:00", "close": "20:00",
     "tags": ["culture", "religious"],  "rating": 9.0},
]

# ── Helper Functions ──────────────────────────────────────────────────────────
def travel_time_min(a, b):
    """Euclidean-distance-based travel time (1 degree ~ 30 min for simplicity)."""
    if a["name"] == b["name"]:
        return 0
    dlat = a["lat"] - b["lat"]
    dlon = a["lon"] - b["lon"]
    dist = math.sqrt(dlat**2 + dlon**2)
    return max(15, int(dist * 3000))   # floor at 15 min

def fits_interests(spot, tags):
    """Return True if spot matches at least one selected interest tag."""
    if not tags:
        return True
    return any(t in spot["tags"] for t in tags)

# ── Greedy Heuristic ──────────────────────────────────────────────────────────
def greedy_plan(start_name, time_budget, budget_nrs, interest_tags):
    remaining = [s for s in SPOTS if fits_interests(s, interest_tags)]
    current   = next((s for s in remaining if s["name"] == start_name), remaining[0])
    remaining.remove(current)

    itinerary    = [current]
    total_time   = current["visit"]
    total_cost   = current["fee"]
    explanations = [f"Start: {current['name']} (rating {current['rating']})"]

    while remaining:
        best, best_score = None, -1
        for spot in remaining:
            tt   = travel_time_min(current, spot)
            cost = spot["fee"]
            if (total_time + tt + spot["visit"] <= time_budget and
                    total_cost + cost <= budget_nrs):
                score = spot["rating"] / (tt + spot["visit"])
                if score > best_score:
                    best, best_score = spot, score

        if best is None:
            break
        tt          = travel_time_min(current, best)
        total_time += tt + best["visit"]
        total_cost += best["fee"]
        itinerary.append(best)
        explanations.append(
            f"  -> {best['name']} | travel {tt}min | visit {best['visit']}min | "
            f"fee Rs.{best['fee']} | score {best_score:.4f} (rating/time)")
        current = best

    return itinerary, total_time, total_cost, explanations

# ── Brute-Force (small dataset) ───────────────────────────────────────────────
def brute_force_plan(spots, time_budget, budget_nrs):
    best_score, best_path = -1, []
    for perm in permutations(spots):
        t, c, score = 0, 0, 0
        path, prev  = [], None
        for spot in perm:
            tt  = travel_time_min(prev, spot) if prev else 0
            t  += tt + spot["visit"]
            c  += spot["fee"]
            if t > time_budget or c > budget_nrs:
                break
            path.append(spot)
            score += spot["rating"]
            prev   = spot
        if score > best_score:
            best_score, best_path = score, path
    return best_path, best_score

# ── GUI ───────────────────────────────────────────────────────────────────────
class TouristPlannerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tourist Spot Optimizer - Kathmandu")
        self.geometry("820x680")
        self.configure(bg="#f0f4f8")
        self._build_ui()

    def _build_ui(self):
        # Title bar
        tk.Label(self, text="Tourist Itinerary Planner",
                 font=("Arial", 16, "bold"), bg="#1F3864", fg="white",
                 pady=10).pack(fill="x")

        # Input frame
        frm = tk.Frame(self, bg="#f0f4f8", pady=8)
        frm.pack(fill="x", padx=20)

        tk.Label(frm, text="Time Budget (min):", bg="#f0f4f8").grid(row=0, col=0, sticky="w")
        self.time_entry = tk.Entry(frm, width=8)
        self.time_entry.insert(0, "300")
        self.time_entry.grid(row=0, column=1, padx=8)

        tk.Label(frm, text="Budget (NPR):", bg="#f0f4f8").grid(row=0, column=2, sticky="w")
        self.budget_entry = tk.Entry(frm, width=10)
        self.budget_entry.insert(0, "2000")
        self.budget_entry.grid(row=0, column=3, padx=8)

        tk.Label(frm, text="Start Location:", bg="#f0f4f8").grid(row=1, column=0, sticky="w", pady=6)
        self.start_var = tk.StringVar()
        ttk.Combobox(frm, textvariable=self.start_var,
                     values=[s["name"] for s in SPOTS], width=30).grid(
                     row=1, column=1, columnspan=3, sticky="w", padx=8)
        self.start_var.set(SPOTS[0]["name"])

        tk.Label(frm, text="Interests:", bg="#f0f4f8").grid(row=2, column=0, sticky="w")
        self.interest_vars = {}
        for i, tag in enumerate(["culture","nature","adventure","religious","heritage","relaxation"]):
            v = tk.BooleanVar()
            self.interest_vars[tag] = v
            tk.Checkbutton(frm, text=tag, variable=v, bg="#f0f4f8").grid(
                row=2, column=i % 6, padx=4)

        btn_frame = tk.Frame(self, bg="#f0f4f8")
        btn_frame.pack(pady=6)
        tk.Button(btn_frame, text="Generate Itinerary", command=self._generate,
                  bg="#2E75B6", fg="white", font=("Arial", 11, "bold"),
                  padx=12, pady=6).pack(side="left", padx=8)
        tk.Button(btn_frame, text="Compare Brute-Force", command=self._compare,
                  bg="#555", fg="white", padx=10, pady=6).pack(side="left", padx=8)
        tk.Button(btn_frame, text="Clear", command=self._clear,
                  padx=10, pady=6).pack(side="left")

        self.output = tk.Text(self, font=("Courier New", 10), height=22,
                              wrap="word", bg="#1a1a2e", fg="#e0e0e0")
        self.output.pack(fill="both", expand=True, padx=20, pady=10)

    def _get_inputs(self):
        try:
            tb = int(self.time_entry.get())
            bud = int(self.budget_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Time budget and budget must be integers.")
            return None, None, None, None
        tags = [t for t, v in self.interest_vars.items() if v.get()]
        return self.start_var.get(), tb, bud, tags

    def _generate(self):
        start, tb, bud, tags = self._get_inputs()
        if start is None:
            return
        itin, tt, tc, expl = greedy_plan(start, tb, bud, tags)
        self.output.delete("1.0", "end")
        self.output.insert("end", f"=== GREEDY ITINERARY ===")
        self.output.insert("end", f"Budget: {tb} min | Rs.{bud} | Interests: {tags or 'All'}")
        self.output.insert("end", "-" * 60 + "")
        for i, spot in enumerate(itin, 1):
            self.output.insert("end", f"{i}. {spot['name']}  (visit {spot['visit']}min, Rs.{spot['fee']})")
        self.output.insert("end", "-" * 60 + "")
        for e in expl:
            self.output.insert("end", e + "")
        self.output.insert("end", f"Total Time Used : {tt} min")
        self.output.insert("end", f"Total Cost      : Rs. {tc}")
        self.output.insert("end", f"Spots Visited   : {len(itin)}")
        self.output.insert("end", "Note: Greedy heuristic - fast but not guaranteed globally optimal.")

    def _compare(self):
        start, tb, bud, tags = self._get_inputs()
        if start is None:
            return
        small = [s for s in SPOTS[:5] if fits_interests(s, tags)]
        bf_path, bf_score = brute_force_plan(small, tb, bud)
        gr_itin, gr_tt, gr_tc, _ = greedy_plan(start, tb, bud, tags)
        self.output.delete("1.0", "end")
        self.output.insert("end", "=== BRUTE-FORCE vs GREEDY COMPARISON (first 5 spots) ===")
        self.output.insert("end", "BRUTE-FORCE:")
        for i, s in enumerate(bf_path, 1):
            self.output.insert("end", f"  {i}. {s['name']} (rating {s['rating']})")
        self.output.insert("end", f"  Total Rating Score: {bf_score:.1f}")
        self.output.insert("end", "GREEDY:")
        for i, s in enumerate(gr_itin, 1):
            self.output.insert("end", f"  {i}. {s['name']} (rating {s['rating']})")
        self.output.insert("end", f"  Total Time: {gr_tt} min | Total Cost: Rs.{gr_tc}")
        self.output.insert("end", "Trade-off: Brute-force is O(n!) - optimal but slow.")
        self.output.insert("end", "Greedy is O(n^2) - fast and practical for larger datasets.")

    def _clear(self):
        self.output.delete("1.0", "end")

if __name__ == "__main__":
    # Simulate user inputs since we can't show a window
    START_LOCATION = "Pashupatinath Temple"
    TIME_BUDGET = 400
    MONEY_BUDGET = 1500
    INTERESTS = ["culture", "religious"]

    print(f"--- Planning Itinerary for {START_LOCATION} ---")
    
    itin, tt, tc, expl = greedy_plan(START_LOCATION, TIME_BUDGET, MONEY_BUDGET, INTERESTS)
    
    for i, spot in enumerate(itin, 1):
        print(f"{i}. {spot['name']} (Visit: {spot['visit']}m, Fee: Rs.{spot['fee']})")
    
    print(f"\nTotal Time: {tt} min | Total Cost: Rs.{tc}")
    print("\nLog:")
    for e in expl:
        print(e)
