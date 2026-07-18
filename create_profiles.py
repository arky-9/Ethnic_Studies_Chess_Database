import os
import xml.etree.ElementTree as ET

def sanitize_name(name):
    # Remove characters that are illegal in folder/file names on Windows and macOS
    return "".join(c for c in name if c not in r'\/:*?"<>|').strip()

def diagnose_and_build(file_path, base_output_dir):
    if not os.path.exists(file_path):
        print(f"Error: Could not find the file at {file_path}")
        return

    # Check first 15 lines to detect format
    lines = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for _ in range(15):
                line = f.readline()
                if not line:
                    break
                lines.append(line)
    except Exception as e:
        print(f"Failed to read file: {e}")
        return

    # Check if the file is XML
    is_xml = False
    for line in lines[:5]:
        if "<?xml" in line or "<players_list" in line or "<player>" in line:
            is_xml = True
            break

    # Extract active GMs and their federations
    gms = [] # Will store tuples of (name, fed)
    
    if is_xml:
        gms = parse_xml(file_path)
    else:
        gms = parse_text(file_path)

    if not gms:
        print("No active GMs found or database could not be parsed.")
        return

    print(f"\nFound {len(gms)} active Grandmasters. Generating folder structures...")
    build_folders(gms, base_output_dir)

def parse_xml(file_path):
    print("Detected format: XML")
    gms = []
    try:
        context = ET.iterparse(file_path, events=('end',))
        for event, elem in context:
            if elem.tag == 'player':
                title_el = elem.find('title')
                flag_el = elem.find('flag')
                name_el = elem.find('name')
                
                fed_el = elem.find('country')
                if fed_el is None:
                    fed_el = elem.find('fed')
                
                title = title_el.text.strip() if title_el is not None and title_el.text else ""
                flag = flag_el.text.strip() if flag_el is not None and flag_el.text else ""
                name = name_el.text.strip() if name_el is not None and name_el.text else ""
                fed = fed_el.text.strip() if fed_el is not None and fed_el.text else "UNKNOWN"
                
                if title == 'GM' and flag != 'i' and name:
                    gms.append((name, fed))
                
                elem.clear()
    except Exception as e:
        print(f"Error parsing XML structure: {e}")
    return gms

def parse_text(file_path):
    print("Detected format: Text")
    gms = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            all_lines = f.readlines()
    except Exception as e:
        print(f"Error reading file lines: {e}")
        return gms

    # Find the header row
    header_idx = -1
    header_line = ""
    for idx, line in enumerate(all_lines[:50]): 
        line_lower = line.lower()
        if "name" in line_lower and ("fed" in line_lower or "rtg" in line_lower or "tit" in line_lower):
            header_idx = idx
            header_line = line
            break

    if header_idx == -1:
        print("Error: Could not identify the column header in the text file.")
        return gms

    # Detect if delimited
    delim = None
    for d in ['|', '\t', ';']:
        if d in header_line:
            delim = d
            break

    if delim:
        # Delimited Text parsing
        cols = [c.lower().strip() for c in header_line.split(delim)]
        name_col_idx = next((i for i, c in enumerate(cols) if "name" in c), None)
        fed_col_idx = next((i for i, c in enumerate(cols) if c in ["fed", "country"]), None)
        title_col_idx = next((i for i, c in enumerate(cols) if c == "tit" or c == "title"), None)
        if title_col_idx is None:
            title_col_idx = next((i for i, c in enumerate(cols) if "tit" in c and "w-" not in c and "o-" not in c), None)
        flag_col_idx = next((i for i, c in enumerate(cols) if "flag" in c), None)

        for line in all_lines[header_idx + 1:]:
            parts = line.split(delim)
            if len(parts) <= max(name_col_idx, title_col_idx):
                continue
            
            name = parts[name_col_idx].strip()
            title = parts[title_col_idx].strip()
            fed = parts[fed_col_idx].strip() if (fed_col_idx is not None and fed_col_idx < len(parts)) else "UNKNOWN"
            flag = parts[flag_col_idx].strip() if (flag_col_idx is not None and flag_col_idx < len(parts)) else ""

            if title == 'GM' and flag != 'i' and name:
                gms.append((name, fed if fed else "UNKNOWN"))
    else:
        # Fixed-Width Text parsing
        header_lower = header_line.lower()
        name_start = header_lower.find("name")
        fed_start = header_lower.find("fed")
        sex_start = header_lower.find("sex")
        
        if fed_start == -1:
            fed_start = header_lower.find("sex")
        if fed_start == -1:
            fed_start = name_start + 50
            
        if sex_start != -1 and sex_start > fed_start:
            fed_end = sex_start
        else:
            fed_end = fed_start + 4
            
        title_start = header_lower.find("tit")
        if title_start == -1:
            title_start = header_lower.find("title")

        next_after_title = -1
        for marker in ["wt", "ot", "rtg", "rating", "gms"]:
            pos = header_lower.find(marker, title_start + 1)
            if pos != -1:
                next_after_title = pos
                break
        if next_after_title == -1:
            next_after_title = title_start + 5

        flag_start = header_lower.find("flag")
        
        for line in all_lines[header_idx + 1:]:
            if len(line) < title_start:
                continue
            
            name = line[name_start:fed_start].strip()
            fed = line[fed_start:fed_end].strip()
            title = line[title_start:next_after_title].strip()
            
            flag = ""
            if flag_start != -1 and len(line) > flag_start:
                flag = line[flag_start:flag_start+4].strip()

            if title == 'GM' and flag != 'i' and name:
                gms.append((name, fed if fed else "UNKNOWN"))

    return gms

def build_folders(gms, base_output_dir):
    created_count = 0
    for name, fed in gms:
        # Sanitize names and federations to prevent file-system errors
        clean_name = sanitize_name(name)
        clean_fed = sanitize_name(fed)
        
        if not clean_name:
            continue
            
        # Target folder: individual_profiles/COUNTRY/Player Name/
        player_folder_path = os.path.join(base_output_dir, clean_fed, clean_name)
        
        # Create directories
        os.makedirs(player_folder_path, exist_ok=True)
        
        # Target empty file: individual_profiles/COUNTRY/Player Name/Player Name.txt
        player_file_path = os.path.join(player_folder_path, f"{clean_name}.txt")
        
        # Create the empty .txt file
        with open(player_file_path, 'w', encoding='utf-8') as f:
            pass # Keep it empty as requested
            
        created_count += 1

    print(f"Folder generation complete. Structured profiles for {created_count} Grandmasters in: {base_output_dir}")

# Setup paths
home_directory = os.path.expanduser("~")
file_path = os.path.join(home_directory, "Desktop", "Chess Database", "standard_rating_list_2.txt")
profiles_dir = os.path.join(home_directory, "Desktop", "Chess Database", "individual_profiles")

# Execute
diagnose_and_build(file_path, profiles_dir)