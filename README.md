# FIDE Chess Invitation Analysis (2015–2026)

## Dataset Description
* 138 monthly FIDE classical rating lists spanning **January 2015 to July 2026**.
* **Active GM Registry:** Parsed from the latest active FIDE classical database containing players holding the Grandmaster (GM) title who are active.

### Download Instructions (Mac)
1. Download and extract your FIDE monthly rating databases into the `txt_files` folder inside your `Chess Database` directory.
2. Save your current reference list as `standard_rating_list_2.txt` in the root `Chess Database` folder.
3. Execute the pipeline from your terminal:
<pre>python3 historical_enrich_profiles.py</pre>
4. If Python is not installed:
<pre>$ brew install python</pre>

### Download Instructions (Windows)
1. Download and extract your FIDE monthly rating databases into the `txt_files` folder inside your `Chess Database` directory.
2. Save your current reference list as `standard_rating_list_2.txt` in the root `Chess Database` folder.
3. Execute the pipeline from your cmd line:
<pre>C:\> py -3 historical_enrich_profiles.py</pre>
4. If Python is not installed, download Python: https://www.python.org/downloads/windows/
