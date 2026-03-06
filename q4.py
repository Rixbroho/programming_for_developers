from typing import Dict, List

# --- Input Data ---
hours = list(range(6, 16))  # Hours 06 to 15
demand = {
    "A": [20, 22, 24, 28, 30, 26, 25, 27, 29, 31],
    "B": [15, 16, 18, 20, 21, 19, 17, 18, 20, 22],
    "C": [25, 28, 30, 32, 35, 33, 31, 30, 34, 36],
}
sources = [
    {"id": "S1", "type": "Solar",  "cap": 50, "from": 6,  "to": 18, "cost": 1.0},
    {"id": "S2", "type": "Hydro",  "cap": 40, "from": 0,  "to": 24, "cost": 1.5},
    {"id": "S3", "type": "Diesel", "cap": 60, "from": 17, "to": 23, "cost": 3.0},
]

def available_sources(hour: int) -> List[dict]:
    """Return sources available this hour, sorted cheapest first (greedy)."""
    avail = [s for s in sources if s["from"] <= hour <= s["to"]]
    return sorted(avail, key=lambda x: x["cost"])

def allocate_hour(hour: int, demands: Dict[str, float], tol: float = 0.10):
    """
    Greedy allocation for one hour.
    Returns (feasible, detail_dict, hour_cost, diesel_used).
    """
    districts = list(demands.keys())
    low  = {d: (1 - tol) * demands[d] for d in districts}
    high = {d: (1 + tol) * demands[d] for d in districts}

    avail = available_sources(hour)
    caps  = {s["id"]: float(s["cap"]) for s in avail}

    # Infeasibility check: can minimum demand be met?
    if sum(caps.values()) < sum(low.values()):
        return False, None, 0.0, False

    alloc = {d: {s["id"]: 0.0 for s in avail} for d in districts}

    # Step A: satisfy lower bounds greedily
    remaining = {d: low[d] for d in districts}
    for s in avail:
        sid, cap_left = s["id"], caps[s["id"]]
        for d in districts:
            if cap_left <= 0: break
            take = min(remaining[d], cap_left)
            alloc[d][sid] += take
            remaining[d]  -= take
            cap_left       -= take
        caps[sid] = cap_left

    if any(remaining[d] > 1e-9 for d in districts):
        return False, None, 0.0, False

    # Step B: fill up to upper bounds with leftover capacity
    extra_cap = {d: high[d] - low[d] for d in districts}
    for s in avail:
        sid, cap_left = s["id"], caps[s["id"]]
        for d in districts:
            if cap_left <= 0: break
            take = min(extra_cap[d], cap_left)
            alloc[d][sid] += take
            extra_cap[d]  -= take
            cap_left       -= take
        caps[sid] = cap_left

    received = {d: sum(alloc[d].values()) for d in districts}
    cost_map  = {s["id"]: s["cost"] for s in avail}

    hour_cost    = sum(kwh * cost_map[sid]
                       for d in districts for sid, kwh in alloc[d].items())
    diesel_used  = any(alloc[d].get("S3", 0) > 0 for d in districts)

    return True, {"alloc": alloc, "received": received, "low": low, "high": high}, hour_cost, diesel_used

# --- Run and Report ---
total_cost = total_energy = total_renewable = 0.0
diesel_hours = []

print(f"{'HOUR':>4} | {'Dist':>4} | {'Solar':>6} | {'Hydro':>6} | "
      f"{'Diesel':>7} | {'Given':>8} | {'Demand':>7} | {'%Met':>6} | Note")
print("-" * 90)

for idx, h in enumerate(hours):
    demands_h = {k: float(demand[k][idx]) for k in "ABC"}
    ok, detail, cost, diesel = allocate_hour(h, demands_h)

    if not ok:
        print(f" {h:02d} | ALL  | INFEASIBLE")
        continue

    total_cost += cost
    for d in "ABC":
        sol  = detail["alloc"][d].get("S1", 0.0)
        hyd  = detail["alloc"][d].get("S2", 0.0)
        die  = detail["alloc"][d].get("S3", 0.0)
        give = detail["received"][d]
        dem  = demands_h[d]
        pct  = (give / dem) * 100
        note = "Diesel used" if die > 0 else ""
        print(f" {h:02d} | {d}    | {sol:6.1f} | {hyd:6.1f} | {die:7.1f} | "
              f"{give:8.1f} | {dem:7.1f} | {pct:5.1f}% | {note}")
        total_energy     += give
        total_renewable  += sol + hyd

    if diesel: diesel_hours.append(h)

renew_pct = (total_renewable / total_energy * 100) if total_energy else 0
print(f"\nTotal Cost (Rs.): {total_cost:.2f}")
print(f"Renewable Energy %: {renew_pct:.2f}%")
print(f"Diesel hours: {diesel_hours if diesel_hours else 'None'}")
