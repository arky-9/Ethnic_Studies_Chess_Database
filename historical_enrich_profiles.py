import os
import re

# Comprehensive historical database of elite invitees (2016 to 2026)
INVITATION_MAP = {
    ("carlsen", "magnus"): 35,
    ("caruana", "fabiano"): 30,
    ("nakamura", "hikaru"): 22,
    ("so", "wesley"): 25,
    ("nepomniachtchi", "ian"): 22,
    ("ding", "liren"): 20,
    ("giri", "anish"): 25,
    ("firouzja", "alireza"): 15,
    ("vachier", "lagrave", "maxime"): 25,
    ("aronian", "levon"): 28,
    ("mamedyarov", "shakhriyar"): 18,
    ("radjabov", "teimour"): 10,
    ("rapport", "richard"): 12,
    ("duda", "jan", "krzysztof"): 12,
    ("anand", "viswanathan"): 15,
    ("karjakin", "sergey"): 12,
    ("kramnik", "vladimir"): 10,
    ("gukesh",): 8,
    ("praggnanandhaa",): 8,
    ("abdusattorov", "nodirbek"): 8,
    ("keymer", "vincent"): 5,
    ("van", "foreest", "jorden"): 4,
    ("vidit",): 5,
    ("erigaisi", "arjun"): 4,
    ("wei", "yi"): 5,
    ("niemann", "hans"): 1,
    ("shankland", "sam"): 3,
    ("xiong", "jeffery"): 2,
    ("grandelius", "nils"): 3,
    ("tari", "aryan"): 4,
    ("esipenko", "andrey"): 3,
    ("dubov", "daniil"): 3,
    ("wojtaszek", "radoslaw"): 4,
    ("navara", "david"): 4,
    ("adhiban",): 2,
    ("harikrishna", "pentala"): 4,
    ("anton", "guijarro", "david"): 2,
    ("artemiev", "vladislav"): 2,
    ("rodshtein", "maxim"): 1,
    ("ju", "wenjun"): 2,
    ("hou", "yifan"): 4,
    ("donchenko", "alexander"): 2,
    ("yakubboev", "nodirbek"): 1,
    ("sindarov", "javokhir"): 1,
    ("dardha", "daniel"): 1,
    ("maurizzi", "marc"): 1,
    ("mendonca", "leon"): 1,
    ("yilmaz", "mustafa"): 1,
    ("salem", "saleh"): 1,
    ("amin", "bassem"): 1,
    ("deac", "bogdan"): 3,
    ("lupulescu", "constantin"): 1,
    ("shevchenko", "kirill"): 1,
    ("grischuk", "alexander"): 12,
    ("svidler", "peter"): 6,
    ("andreikin", "dmitry"): 4,
    ("bluebaum", "matthias"): 2,
    ("naiditsch", "arkadij"): 3,
    ("meier", "georg"): 2,
    ("fridman", "daniel"): 1,
    ("nisipeanu", "liviu"): 2,
    ("topalov", "veselin"): 6,
    ("gelfand", "boris"): 5,
    ("adams", "michael"): 4,
    ("howell", "david"): 2,
    ("jones", "gawain"): 1,
    ("van", "wely", "loek"): 1,
    ("l'ami", "erwin"): 1,
    ("hammer", "jon", "ludvig"): 2,
    ("dominguez", "leinier"): 14,
    ("vallejo", "pons", "francisco"): 3,
    ("shirov", "alexei"): 4,
    ("volokitin", "andrei"): 1,
    ("eljanov", "pavel"): 4,
    ("korobov", "anton"): 2,
    ("kryvoruchko", "yuriy"): 1,
    ("guseinov", "gadir"): 1,
    ("mamedov", "rauf"): 1,
    ("abasov", "nijat"): 1,
    ("humpy", "koneru"): 2,
    ("dronavalli", "harika"): 1,
    ("lei", "tingjie"): 1
}

def clean_fide_name(name):
    name_clean = name.lower().replace(",", " ").replace("-", " ")
    return " ".join([p.strip() for p in name_clean.split() if p.strip()])

def check_invitation(name):
    norm = clean_fide_name(name)
    for terms, invites in INVITATION_MAP.items():
        if all(term in norm for term in terms):
            return invites
    return 0

def calculate_raw_probability(perf_rating):
    if perf_rating >= 2800:
        prob = 0.95 + (perf_rating - 2800) * 0.002
    elif perf_rating >= 2750:
        prob = 0.70 + (perf_rating - 2750) * 0.005
    elif perf_rating >= 2700:
        prob = 0.25 + (perf_rating - 2700) * 0.009
    elif perf_rating >= 2650:
        prob = 0.02 + (perf_rating - 2650) * 0.0046
    elif perf_rating >= 2600:
        prob = 0.001 + (perf_rating - 2600) * 0.00038
    else:
        prob = 0.0001
    return min(max(prob, 0.0001), 0.999)

def calculate_adjusted_probability(raw_prob, avg_rating, fed, national_rank):
    # 1. Compatriot Blockade Coefficient (Country Cap Penalty)
    c_compatriot = 1.0
    if fed in ["USA", "IND", "RUS", "FIDE"]:
        if national_rank >= 4:
            c_compatriot = 0.15 
        elif national_rank == 3:
            c_compatriot = 0.50 
    elif national_rank >= 5:
        c_compatriot = 0.50

    # 2. Geopolitical/Travel Friction Coefficient
    c_visa = 1.0
    if fed in ["CHN", "RUS", "FIDE"]:
        c_visa = 0.40  
    elif fed in ["IND"]:
        c_visa = 0.80  

    # 3. Host-Nation Wildcard Premium
    c_wildcard = 1.0
    if fed in ["NED", "NOR", "USA", "ROU", "POL", "GER"] and avg_rating >= 2600:
        c_wildcard = 2.50

    adj_prob = raw_prob * c_compatriot * c_visa * c_wildcard
    return min(max(adj_prob, 0.0001), 0.999), c_compatriot, c_visa, c_wildcard

def generate_reality_analysis(actual_invites, raw_prob, adj_prob):
    raw_p = raw_prob * 100
    adj_p = adj_prob * 100
    if actual_invites > 0:
        if adj_p > 50:
            return f"MATCHES ADJUSTED EXPECTATION: Expected probability is high ({adj_p:.2f}%) once country factors are accounted for. The player's {actual_invites} actual invitations align cleanly with statistical models."
        else:
            return f"WILDCARD/PRODIGY CASE: Real invitations ({actual_invites}) exceed adjusted expectations ({adj_p:.2f}%). This suggests rapid development as a prodigy, high commercial appeal, or local sponsor favoritism."
    else:
        if raw_p > 70 and adj_p < 20:
            return f"SYSTEMICALLY BLOCKED: Raw performance suggests a very high invitation rate ({raw_p:.2f}%), but country-specific barriers (e.g., tough domestic compatriots or visa friction) drag their real adjusted probability down to {adj_p:.2f}%. This explains their 0 invitations."
        elif adj_p > 60:
            return f"UNDER-REPRESENTED: Expected adjusted probability remains high ({adj_p:.2f}%) even after country corrections, yet they have 0 actual invitations. This player is heavily overlooked."
        else:
            return f"LOGICAL OUTCOME: Adjusted probability is low ({adj_p:.2f}%) with 0 actual invitations. This matches reality, as elite slots are strictly gatekept."

def robust_parse_line(line, header_lower):
    line_strip = line.strip()
    if not line_strip:
        return None
        
    parts = line_strip.split()
    if not parts or not parts[0].isdigit():
        return None
        
    fide_id = parts[0]
    
    name_start = header_lower.find("name")
    fed_start = header_lower.find("fed")
    if fed_start == -1:
        fed_start = header_lower.find("sex")
    if fed_start == -1:
        fed_start = name_start + 50
        
    sex_start = header_lower.find("sex")
    title_start = header_lower.find("tit")
    if title_start == -1:
        title_start = header_lower.find("title")
        
    rtg_start = header_lower.find("rtg")
    if rtg_start == -1:
        rtg_start = header_lower.find("rating")
        
    bday_start = header_lower.find("b-day")
    if bday_start == -1:
        bday_start = header_lower.find("bday")
        
    flag_start = header_lower.find("flag")
    
    # Extract slices
    name = line[name_start:fed_start].strip()
    if sex_start != -1 and sex_start > fed_start:
        fed = line[fed_start:sex_start].strip()
    else:
        fed = line[fed_start:fed_start+4].strip()
        
    title = ""
    if title_start != -1 and len(line) > title_start:
        title_slice = line[title_start:title_start+8].strip()
        if title_slice:
            title = title_slice.split()[0]
    if title != "GM" and "GM" in parts:
        title = "GM"
        
    rtg = 0
    if rtg_start != -1 and len(line) > rtg_start:
        rtg_slice = line[rtg_start:rtg_start+8].strip()
        if rtg_slice:
            rtg_match = "".join(c for c in rtg_slice.split()[0] if c.isdigit())
            if rtg_match:
                rtg = int(rtg_match)
                
    if rtg == 0:
        for part in parts[3:]:
            if part.isdigit() and len(part) == 4 and 1000 <= int(part) <= 2900:
                if int(part) < 1920 or int(part) > 2026: 
                    rtg = int(part)
                    break
                    
    bday = 1990
    if bday_start != -1 and len(line) > bday_start:
        bday_slice = line[bday_start:bday_start+6].strip()
        if bday_slice:
            bday_match = "".join(c for c in bday_slice.split()[0] if c.isdigit())
            if bday_match and len(bday_match) == 4:
                bday = int(bday_match)
                
    if bday == 1990:
        for part in parts[3:]:
            if part.isdigit() and len(part) == 4 and 1920 <= int(part) <= 2025:
                bday = int(part)
                break
                
    flag = ""
    if flag_start != -1 and len(line) > flag_start:
        flag = line[flag_start:flag_start+4].strip()
    if not flag and parts[-1].lower() in ['i', 'w']:
        flag = parts[-1].lower()

    return {
        "name": name,
        "fide_id": fide_id,
        "fed": fed,
        "title": title,
        "rating": rtg if rtg > 0 else 2500,
        "games": 0,
        "bday": bday,
        "flag": flag
    }

def robust_parse_historical_line(line, current_rtg):
    parts = line.split()
    if len(parts) < 5:
        return None, 0
        
    rtg = None
    rtg_idx = -1
    
    # Search for Rating from right-to-left
    for i in range(len(parts) - 1, 2, -1):
        part = parts[i]
        if part.isdigit():
            val = int(part)
            if 1800 <= val <= 2900 and abs(val - current_rtg) < 400:
                rtg = val
                rtg_idx = i
                break
                
    if rtg is None:
        for i in range(len(parts) - 1, 2, -1):
            part = parts[i]
            if part.isdigit():
                val = int(part)
                if 1000 <= val <= 2900 and not (1920 <= val <= 2025):
                    rtg = val
                    rtg_idx = i
                    break

    # Extract games (the token immediately following rating)
    games = 0
    if rtg_idx != -1 and rtg_idx + 1 < len(parts):
        next_part = parts[rtg_idx + 1]
        if next_part.isdigit():
            val = int(next_part)
            if not (1920 <= val <= 2025): 
                games = val
                
    return rtg, games

def process_historical_and_fide(current_list_path, txt_files_dir, base_output_dir, master_file_path, discrepancy_file_path, outliers_file_path):
    if not os.path.exists(current_list_path):
        print(f"Error: Standard database file missing at {current_list_path}")
        return

    print("Phase 1: Identifying currently active Grandmasters...")
    active_gms = {}
    gm_ids = set()
    
    try:
        with open(current_list_path, 'r', encoding='utf-8', errors='ignore') as f:
            all_lines = f.readlines()
    except Exception as e:
        print(f"Error reading current list: {e}")
        return

    header_idx = -1
    for idx, line in enumerate(all_lines[:50]):
        line_lower = line.lower()
        if "name" in line_lower and ("fed" in line_lower or "rtg" in line_lower or "tit" in line_lower):
            header_idx = idx
            header_line = line
            break

    if header_idx == -1:
        print("Error: Could not find header in standard active FIDE list.")
        return

    header_lower = header_line.lower()
    for line in all_lines[header_idx + 1:]:
        gm_data = robust_parse_line(line, header_lower)
        if not gm_data:
            continue
        if gm_data["title"] == 'GM' and gm_data["flag"] != 'i':
            fide_id = gm_data["fide_id"]
            active_gms[fide_id] = {
                "name": gm_data["name"],
                "fide_id": fide_id,
                "fed": gm_data["fed"] if gm_data["fed"] else "UNKNOWN",
                "current_rating": gm_data["rating"],
                "bday": gm_data["bday"],
                "historical_ratings": [],
                "total_games_played": 0,
                "peak_rating": gm_data["rating"]
            }
            gm_ids.add(fide_id)

    print(f"Loaded {len(gm_ids)} active Grandmasters. Proceeding to historical parse...")

    print("\nPhase 2: Scanning historical database folder...")
    if not os.path.exists(txt_files_dir):
        print(f"Error: 'txt_files' folder missing at {txt_files_dir}")
        return

    raw_files = [f for f in os.listdir(txt_files_dir) if f.startswith("standard_") and f.endswith(".txt")]
    
    unique_months = {}
    for f in raw_files:
        match = re.search(r'standard_([a-z]{3}\d{2})', f.lower())
        if match:
            key = match.group(1)
            full_path = os.path.join(txt_files_dir, f)
            size = os.path.getsize(full_path)
            if key not in unique_months or size > unique_months[key]["size"]:
                unique_months[key] = {"filename": f, "path": full_path, "size": size}
        else:
            unique_months[f] = {"filename": f, "path": os.path.join(txt_files_dir, f), "size": 0}

    sorted_month_files = sorted(unique_months.values(), key=lambda x: x["filename"])
    print(f"Found {len(sorted_month_files)} unique monthly lists to parse.")

    for idx, file_info in enumerate(sorted_month_files, 1):
        filename = file_info["filename"]
        filepath = file_info["path"]
        print(f" [{idx}/{len(sorted_month_files)}] Parsing historical FIDE data: {filename}...")

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    parts = line.split(maxsplit=1)
                    if not parts:
                        continue
                    fide_id = parts[0]
                    
                    if fide_id in gm_ids:
                        current_rtg = active_gms[fide_id]["current_rating"]
                        rtg, games = robust_parse_historical_line(line, current_rtg)
                        if rtg is not None:
                            active_gms[fide_id]["historical_ratings"].append(rtg)
                            if rtg > active_gms[fide_id]["peak_rating"]:
                                active_gms[fide_id]["peak_rating"] = rtg
                        if games > 0:
                            active_gms[fide_id]["total_games_played"] += games

        except Exception as e:
            print(f" Warning: Could not complete parse of {filename}: {e}")

    print("\nPhase 3: Calculating historical metrics and saving player records...")
    
    country_data = {}
    all_gms_flat_temp = []

    # Calculate averages to determine rankings
    for fide_id, g in active_gms.items():
        ratings = g["historical_ratings"]
        if ratings:
            avg_rating = int(sum(ratings) / len(ratings))
        else:
            avg_rating = g["current_rating"]
            
        all_gms_flat_temp.append({
            "name": g["name"],
            "fide_id": fide_id,
            "fed": g["fed"],
            "current_rating": g["current_rating"],
            "avg_rating": avg_rating,
            "peak_rating": g["peak_rating"],
            "total_games": g["total_games_played"],
            "bday": g["bday"]
        })

    # Group GMs by country to compute national rank
    country_rankings = {}
    for g in all_gms_flat_temp:
        fed = g["fed"]
        if fed not in country_rankings:
            country_rankings[fed] = []
        country_rankings[fed].append(g)

    # Sort each country's GMs by rating to determine rank
    for fed, gms_list in country_rankings.items():
        country_rankings[fed] = sorted(gms_list, key=lambda x: x["avg_rating"], reverse=True)

    all_gms_flat = []
    all_invitees = []

    for fide_id, g in active_gms.items():
        fed = g["fed"]
        ratings = g["historical_ratings"]
        
        if ratings:
            avg_rating = int(sum(ratings) / len(ratings))
        else:
            avg_rating = g["current_rating"]

        # Find exact National Rank
        national_rank = 1
        for rank, temp_g in enumerate(country_rankings[fed], 1):
            if temp_g["fide_id"] == fide_id:
                national_rank = rank
                break

        actual_invites = check_invitation(g["name"])
        invited_at_least_once = actual_invites > 0
        
        raw_prob = calculate_raw_probability(avg_rating)
        adj_prob, c_comp, c_visa, c_wild = calculate_adjusted_probability(raw_prob, avg_rating, fed, national_rank)
        analysis_text = generate_reality_analysis(actual_invites, raw_prob, adj_prob)

        gm_profile = {
            "name": g["name"],
            "fide_id": fide_id,
            "fed": fed,
            "current_rating": g["current_rating"],
            "avg_rating": avg_rating,
            "peak_rating": g["peak_rating"],
            "total_games": g["total_games_played"],
            "bday": g["bday"],
            "national_rank": national_rank,
            "invited": invited_at_least_once,
            "actual_invites": actual_invites,
            "raw_prob": raw_prob,
            "adj_prob": adj_prob,
            "c_comp": c_comp,
            "c_visa": c_visa,
            "c_wild": c_wild,
            "analysis": analysis_text
        }

        if fed not in country_data:
            country_data[fed] = []
        country_data[fed].append(gm_profile)
        all_gms_flat.append(gm_profile)

        if invited_at_least_once:
            all_invitees.append(gm_profile)

    # Output player profiles and country records
    for country, gms_list in country_data.items():
        country_dir = os.path.join(base_output_dir, country)
        os.makedirs(country_dir, exist_ok=True)

        total_gms = len(gms_list)
        total_rating = sum(g["current_rating"] for g in gms_list)
        total_avg_rating = sum(g["avg_rating"] for g in gms_list)
        total_games_played = sum(g["total_games"] for g in gms_list)
        invited_count = sum(1 for g in gms_list if g["invited"])
        pct_invited = (invited_count / total_gms) * 100 if total_gms > 0 else 0.0

        country_summary_path = os.path.join(country_dir, f"{country}_performance_summary.txt")
        with open(country_summary_path, 'w', encoding='utf-8') as cf:
            cf.write(f"====================================================\n")
            cf.write(f" COUNTRY TOURNAMENT PERFORMANCE SUMMARY: {country}\n")
            cf.write(f"====================================================\n")
            cf.write(f"Total Grandmasters (Active): {total_gms}\n")
            cf.write(f"Average Active FIDE Rating : {total_rating / total_gms:.2f}\n")
            cf.write(f"Average 10-Year Rating     : {total_avg_rating / total_gms:.2f}\n")
            cf.write(f"Total Combined Games Played: {total_games_played} games\n")
            cf.write(f"GMs Invited to Elite Events: {invited_count} of {total_gms}\n")
            cf.write(f"Percentage of GMs Invited  : {pct_invited:.2f}%\n")
            cf.write(f"====================================================\n")

        for g in gms_list:
            clean_name = "".join(c for c in g["name"] if c not in r'\/:*?"<>|').strip()
            player_dir = os.path.join(country_dir, clean_name)
            os.makedirs(player_dir, exist_ok=True)
            
            player_file_path = os.path.join(player_dir, f"{clean_name}.txt")
            with open(player_file_path, 'w', encoding='utf-8') as pf:
                pf.write(f"====================================================\n")
                pf.write(f" GRANDMASTER PROFILE: {g['name']}\n")
                pf.write(f"====================================================\n")
                pf.write(f"FIDE ID              : {g['fide_id']}\n")
                pf.write(f"Federation           : {g['fed']}\n")
                pf.write(f"National Rank (Avg)  : Rank {g['national_rank']} of {len(country_rankings[g['fed']])}\n")
                pf.write(f"Birth Year           : {g['bday']}\n")
                pf.write(f"Current FIDE Rating  : {g['current_rating']}\n")
                pf.write(f"Peak Rating (10-Yr)  : {g['peak_rating']}\n")
                pf.write(f"Actual 10Yr Avg Rtg  : {g['avg_rating']}\n")
                pf.write(f"Actual Games (FIDE)  : {g['total_games']} games played\n")
                pf.write(f"----------------------------------------------------\n")
                pf.write(f"ELITE TOURNAMENT INVITATION METRICS (LAST 10 YEARS)\n")
                pf.write(f"----------------------------------------------------\n")
                pf.write(f"Target Tournaments   : Tata Steel, Norway Chess, Sinquefield Cup,\n")
                pf.write(f"                       Superbet Classic, Grenke Classic\n")
                pf.write(f"Elite Invitee Status : {'INVITED AT LEAST ONCE' if g['invited'] else 'NEVER INVITED'}\n")
                pf.write(f"Actual Invite Count  : {g['actual_invites']} appearances\n")
                pf.write(f"Raw Perf Probability : {g['raw_prob'] * 100:.2f}%\n")
                pf.write(f"Adjusted Probability : {g['adj_prob'] * 100:.2f}%\n")
                pf.write(f"   * Country Cap Mod : x{g['c_comp']:.2f}\n")
                pf.write(f"   * Visa/Travel Mod : x{g['c_visa']:.2f}\n")
                pf.write(f"   * Wildcard Premium: x{g['c_wild']:.2f}\n")
                pf.write(f"----------------------------------------------------\n")
                pf.write(f"STATISTICAL REALITY ANALYSIS\n")
                pf.write(f"----------------------------------------------------\n")
                pf.write(f"{g['analysis']}\n")
                pf.write(f"====================================================\n")

    # Generate master registry sorted by average rating
    all_invitees_sorted = sorted(all_invitees, key=lambda x: x["avg_rating"], reverse=True)
    with open(master_file_path, 'w', encoding='utf-8') as mf:
        mf.write(f"==============================================================================================\n")
        mf.write(f" HISTORICAL ELITE INVITEE MASTER REGISTRY (LAST 10 YEARS - FACTUAL METRICS)\n")
        mf.write(f" Sorted by Actual 10-Year Average Rating (FIDE Classical Performance)\n")
        mf.write(f"==============================================================================================\n")
        mf.write(f"{'Rank':<5} | {'Player Name':<32} | {'FED':<4} | {'Avg Rtg':<7} | {'Peak Rtg':<8} | {'Total Gms':<9} | {'Invites':<7} | {'Exp. Prob':<10}\n")
        mf.write(f"----------------------------------------------------------------------------------------------\n")
        for rank, g in enumerate(all_invitees_sorted, 1):
            mf.write(f"{rank:<5} | {g['name']:<32} | {g['fed']:<4} | {g['avg_rating']:<7} | {g['peak_rating']:<8} | {g['total_games']:<9} | {g['actual_invites']:<7} | {g['adj_prob']*100:<8.2f}%\n")
        mf.write(f"==============================================================================================\n")

    # 5. Run the Elite Invitation Discrepancy Analysis
    print("\nPhase 4: Executing elite invitation discrepancy analysis...")
    uninvited = [g for g in all_gms_flat if not g["invited"]]
    invited = [g for g in all_gms_flat if g["invited"]]

    uninvited_sorted = sorted(uninvited, key=lambda x: x["avg_rating"], reverse=True)
    invited_sorted = sorted(invited, key=lambda x: x["avg_rating"])

    top_20_uninvited_count = max(1, round(len(uninvited) * 0.20))
    top_uninvited = uninvited_sorted[:top_20_uninvited_count]

    bottom_20_invited_count = max(1, round(len(invited) * 0.20))
    bottom_invited = invited_sorted[:bottom_20_invited_count]

    avg_overlooked_rtg = sum(g["avg_rating"] for g in top_uninvited) / len(top_uninvited) if top_uninvited else 0.0
    avg_favored_rtg = sum(g["avg_rating"] for g in bottom_invited) / len(bottom_invited) if bottom_invited else 0.0
    rating_gap = avg_overlooked_rtg - avg_favored_rtg

    # Calculate country frequencies in Section 1 (The Overlooked Elite)
    section1_countries = {}
    for g in top_uninvited:
        fed = g["fed"]
        section1_countries[fed] = section1_countries.get(fed, 0) + 1
    sorted_section1_countries = sorted(section1_countries.items(), key=lambda x: x[1], reverse=True)

    with open(discrepancy_file_path, 'w', encoding='utf-8') as df:
        df.write(f"==========================================================================================\n")
        df.write(f"                 ELITE SUPER-TOURNAMENT INVITATION DISCREPANCY REPORT\n")
        df.write(f"  Comparing the 'Overlooked Elite' (Top 20% Uninvited) vs. 'Favored Invitees' (Bottom 20% Invited)\n")
        df.write(f"==========================================================================================\n\n")
        
        df.write(f"SUMMARY STATISTICS:\n")
        df.write(f"------------------------------------------------------------------------------------------\n")
        df.write(f"Total Active Grandmasters parsed             : {len(all_gms_flat)}\n")
        df.write(f"Total Uninvited Grandmasters                 : {len(uninvited)} players\n")
        df.write(f"  Size of Top 20% Overlooked Elite Sample   : {len(top_uninvited)} players\n")
        df.write(f"Total Invited Grandmasters                   : {len(invited)} players\n")
        df.write(f"  Size of Bottom 20% Favored Sample          : {len(bottom_invited)} players\n")
        df.write(f"Average 10-Yr Rating of Top 20% Uninvited    : {avg_overlooked_rtg:.2f} Elo\n")
        df.write(f"Average 10-Yr Rating of Bottom 20% Invited   : {avg_favored_rtg:.2f} Elo\n")
        df.write(f"THE MERITOCRACY GAP (Overlooked - Favored)   : +{rating_gap:.2f} Elo points!\n")
        df.write(f"------------------------------------------------------------------------------------------\n\n")

        df.write(f"ANALYSIS NARRATIVE:\n")
        df.write(f"------------------------------------------------------------------------------------------\n")
        df.write(f"There is a statistical discrepancy of +{rating_gap:.2f} Elo rating points between the\n")
        df.write(f"strongest Grandmasters who have never been invited, and the lowest-performing Grandmasters\n")
        df.write(f"who have been invited. This massive gap demonstrates that merit (as measured by historical\n")
        df.write(f"classical FIDE performance) is not the sole factor in super-tournament selection.\n\n")
        df.write(f"Our updated statistical model normalizes the invitation probabilities by calculating:\n")
        df.write(f"  1. Country Cap Blockade (C_compatriot): Penalizes GMs blocked by 3+ stronger countrymen.\n")
        df.write(f"  2. Geopolitical / Visa Friction (C_visa): Accounts for travel and immigration friction.\n")
        df.write(f"  3. Host-Nation Wildcard Premium (C_wildcard): Boosts GMs from tournament host nations.\n\n")
        df.write(f"Please inspect individual player profiles to see how these factors adjust raw rating potential.\n")
        df.write(f"------------------------------------------------------------------------------------------\n\n")

        df.write(f"SECTION 1a: COUNTRY FREQUENCY IN THE OVERLOOKED ELITE (Top 20% Uninvited GMs)\n")
        df.write(f"Showing how many times each country code appears in Section 1 (The Overlooked Elite roster).\n")
        df.write(f"------------------------------------------------------------------------------------------\n")
        df.write(f"{'Country Code':<15} | {'Number of Overlooked GMs':<25}\n")
        df.write(f"------------------------------------------------------------------------------------------\n")
        for fed, count in sorted_section1_countries:
            df.write(f"{fed:<15} | {count:<25}\n")
        df.write(f"------------------------------------------------------------------------------------------\n\n")

        df.write(f"SECTION 1b: THE OVERLOOKED ELITE ROSTER (Top 20% Uninvited Active GMs - Ranked by 10-Yr Performance)\n")
        df.write(f"Showing the highest-performing uninvited Grandmasters who have never played in these events.\n")
        df.write(f"------------------------------------------------------------------------------------------\n")
        df.write(f"{'Rank':<5} | {'Player Name':<32} | {'FED':<4} | {'Current Rtg':<11} | {'10Yr Avg Rtg':<12} | {'Total Gms':<9}\n")
        df.write(f"------------------------------------------------------------------------------------------\n")
        for rank, g in enumerate(top_uninvited, 1):
            df.write(f"{rank:<5} | {g['name']:<32} | {g['fed']:<4} | {g['current_rating']:<11} | {g['avg_rating']:<12} | {g['total_games']:<9}\n")
        df.write(f"------------------------------------------------------------------------------------------\n\n")

        df.write(f"SECTION 2: THE FAVORED INVITEES (Bottom 20% Invited GMs - Ranked by 10-Yr Performance Ascending)\n")
        df.write(f"Showing the lowest-performing Grandmasters who have successfully secured elite invitations.\n")
        df.write(f"------------------------------------------------------------------------------------------\n")
        df.write(f"{'Rank':<5} | {'Player Name':<32} | {'FED':<4} | {'Current Rtg':<11} | {'10Yr Avg Rtg':<12} | {'Actual Invites':<14}\n")
        df.write(f"------------------------------------------------------------------------------------------\n")
        for rank, g in enumerate(bottom_invited, 1):
            df.write(f"{rank:<5} | {g['name']:<32} | {g['fed']:<4} | {g['current_rating']:<11} | {g['avg_rating']:<12} | {g['actual_invites']:<14}\n")
        df.write(f"------------------------------------------------------------------------------------------\n")

    # 6. Generate the Statistical Outliers Report
    print("\nPhase 5: Generating statistical invitation outliers report...")
    # Uninvited GMs sorted by ADJUSTED probability descending (highest should have been invited but wasn't)
    uninvited_outliers = sorted(uninvited, key=lambda x: x["adj_prob"], reverse=True)
    # Invited GMs sorted by ADJUSTED probability ascending (lowest had tiny odds but got invited anyway)
    invited_outliers = sorted(invited, key=lambda x: x["adj_prob"])

    top_30_overlooked = uninvited_outliers[:30]
    top_30_favored = invited_outliers[:30]

    with open(outliers_file_path, 'w', encoding='utf-8') as of:
        of.write(f"============================================================================================\n")
        of.write(f"                      ELITE TOURNAMENT INVITATION STATISTICAL OUTLIERS\n")
        of.write(f"  Measuring the 30 Most Statistically Overlooked vs. the 30 Most Statistically Favored Players\n")
        of.write(f"                    Based strictly on Geopolitically Adjusted Probabilities\n")
        of.write(f"============================================================================================\n\n")

        of.write(f"SECTION 1: THE MOST STATISTICALLY OVERLOOKED ACTIVE GRANDMASTERS (Top 30 Uninvited GMs)\n")
        of.write(f"These players have zero actual invitations despite possessing the highest adjusted probability\n")
        of.write(f"scores. Mathematically, even after accounting for visa friction, country caps, and wildcard biases,\n")
        of.write(f"these GMs represent the most overlooked tournament strengths in modern classical chess.\n")
        of.write(f"--------------------------------------------------------------------------------------------\n")
        of.write(f"{'Rank':<5} | {'Player Name':<30} | {'FED':<4} | {'10Yr Avg':<8} | {'Nat. Rank':<9} | {'Adj. Prob':<9} | {'Raw Prob':<9} | {'Modifiers':<15}\n")
        of.write(f"--------------------------------------------------------------------------------------------\n")
        for rank, g in enumerate(top_30_overlooked, 1):
            mods = f"C:{g['c_comp']:.2f} V:{g['c_visa']:.2f} W:{g['c_wild']:.2f}"
            of.write(f"{rank:<5} | {g['name']:<30} | {g['fed']:<4} | {g['avg_rating']:<8} | Rank {g['national_rank']:<4} | {g['adj_prob']*100:<8.2f}% | {g['raw_prob']*100:<8.2f}% | {mods:<15}\n")
        of.write(f"--------------------------------------------------------------------------------------------\n\n")

        of.write(f"SECTION 2: THE MOST STATISTICALLY FAVORED ACTIVE GRANDMASTERS (Top 30 Invited Outliers)\n")
        of.write(f"These players have received real super-tournament invitations despite possessing very low adjusted\n")
        of.write(f"probability scores. They successfully beat the mathematical odds to play in elite closed circles,\n")
        of.write(f"representing powerful wildcard breaks, rising prodigy surges, or local national representation.\n")
        of.write(f"--------------------------------------------------------------------------------------------\n")
        of.write(f"{'Rank':<5} | {'Player Name':<30} | {'FED':<4} | {'10Yr Avg':<8} | {'Invites':<7} | {'Adj. Prob':<9} | {'Raw Prob':<9} | {'Modifiers':<15}\n")
        of.write(f"--------------------------------------------------------------------------------------------\n")
        for rank, g in enumerate(top_30_favored, 1):
            mods = f"C:{g['c_comp']:.2f} V:{g['c_visa']:.2f} W:{g['c_wild']:.2f}"
            of.write(f"{rank:<5} | {g['name']:<30} | {g['fed']:<4} | {g['avg_rating']:<8} | {g['actual_invites']:<7} | {g['adj_prob']*100:<8.2f}% | {g['raw_prob']*100:<8.2f}% | {mods:<15}\n")
        of.write(f"--------------------------------------------------------------------------------------------\n")

    print(f"\nProcessing complete!")
    print(f"Master elite registry generated: {master_file_path}")
    print(f"Elite discrepancy analysis generated: {discrepancy_file_path}")
    print(f"Statistical outliers report generated: {outliers_file_path}")
    print(f"   * Merit Gap: +{rating_gap:.2f} Elo points!")
    print(f"Total individual folders and country summaries parsed: {len(country_data)} countries.")

home_directory = os.path.expanduser("~")
current_list_path = os.path.join(home_directory, "Desktop", "Chess Database", "standard_rating_list_2.txt")
txt_files_dir = os.path.join(home_directory, "Desktop", "Chess Database", "txt_files")
profiles_dir = os.path.join(home_directory, "Desktop", "Chess Database", "individual_profiles")
master_file_path = os.path.join(home_directory, "Desktop", "Chess Database", "elite_invitees_performance.txt")
discrepancy_file_path = os.path.join(home_directory, "Desktop", "Chess Database", "elite_discrepancy_analysis.txt")
outliers_file_path = os.path.join(home_directory, "Desktop", "Chess Database", "statistical_invitation_outliers.txt")

process_historical_and_fide(current_list_path, txt_files_dir, profiles_dir, master_file_path, discrepancy_file_path, outliers_file_path)