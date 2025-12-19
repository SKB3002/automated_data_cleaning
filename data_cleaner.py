import pandas as pd
import re
from pathlib import Path

# -----------------------------
# CONFIG
# -----------------------------
INPUT_FOLDER = "input_files"
OUTPUT_FOLDER = "output_phase1"
Path(OUTPUT_FOLDER).mkdir(exist_ok=True)

# -----------------------------
# COLUMN ALIASES
# -----------------------------
COLUMN_ALIASES = {
    "Name": [
        "name of the teacher", "name of teacher", "name of participant",
        "name of the participant", "participant name", "teacher name", "name"
    ],
    "Phone Number": [
        "mobile", "phone", "phone number", "phone no", "contact",
        "contact number", "mobile/contact number"
    ],
    "Email ID": [
        "email", "email id", "email address"
    ],
    "School/College": [
        "name of school", "name of the school", "school",
        "school/college", "college", "institution"
    ],
    "City/District": [
        "city", "city/district", "district"
    ],
    "State": [
        "state"
    ]
}

# -----------------------------
# SCHOOL STANDARDISATION RULES
# -----------------------------
SCHOOL_REPLACEMENTS = {
    r"\bz[\s\.]*p[\s\.]*h[\s\.]*s\b": "zilla parishad high school",
    r"\bzphs\b": "zilla parishad high school",
    r"\bzppps\b": "zilla parishad primary school",
    r"\bzpps\b": "zilla parishad primary school",
    r"\bz[\s\.]*p[\s\.]*p[\s\.]*s\b": "zilla parishad primary school",
    r"\bzppps\b": "zilla parishad primary school",
    r"\bz[\s\.]*p\b": "zilla parishad",
    r"\bnmc(?=[a-z])": "nmc ",
    r"\bbmc(?=[a-z])": "bmc ",
    r"\bschool(?=[a-z])": "school ",
    r"\bhighschool(?=[a-z])": "high school ",
    r"\bjr\b": "junior",
    r"\bjr\.\b": "junior",
    r"\bgirsl\b": "girls",
    r"\bmar\b": "marathi",
    r"\br[\s\.]*a[\s\.]*a[\s\.]*r\b": "rashtrasant acharya anand rushiji",
    r"\br[\s\.]*a[\s\.]*a[\s\.]\b": "rashtrasant acharya anand",
    r"\br[\s\.]*a[\s\.]\b": "rashtrasant acharya",
    r"\brushini\b": "rushiji",
    r"\bhighschool\b": "high school",
    r"\bhs\b": "high school",
    r"\bpraimari\b": "primary",
    r"\bh[\s\.]*s\b": "high school",
    r"\bnasik\b": "nashik",
    r"\bpriymari\b": "primary",
    r"\bsec\b": "secondary",
    r"\bsec\.\b": "secondary",
    r"\bmedium\b": "",
    r"\bmediym\b": "",
    r"\bpeathamic\b": "prathmik",
    r"\bmadhymik\b": "madhyamik",
    r"\bmadhymic\b": "madhyamik",
    r"\bmadhamik\b": "madhyamik",
    r"\bmadhyamic\b": "madhyamik",
    r"\bmadyamik\b": "madhyamik",
    r"\bmadymik\b": "madhyamik",
    r"\bmadhya\b": "madhyamik",
    r"\bmadh\b": "madhyamik",
    r"\bmadhy\b": "madhyamik",
    r"\bm[\s]v\b": "madhyamik vidyalaya",
    r"\bvidy\b": "vidyalaya",
    r"\bvidya[\s]mandir\b": "vidyamandir",
    r"\bvidya\b": "vidyalaya",
    r"\bvidyslay\b": "vidyalaya",
    r"\bvidylaya\b": "vidyalaya",
    r"\bvidhylai\b": "vidyalaya",
    r"\bvidhylay\b": "vidyalaya",
    r"\bvidhyalaya\b": "vidyalaya",
    r"\bvidyalay\b": "vidyalaya",
    r"\bvudyalay\b": "vidyalaya",
    r"\bvidhyalaya\b": "vidyalaya",
    r"\bvidhyalay\b": "vidyalaya",
    r"\bvidhalay\b": "vidyalaya",
    r"\bvidalaya\b": "vidyalaya",
    r"\bvidhyal\b": "vidyalaya",
    r"\bvidyalya\b": "vidyalaya",
    r"\bvidyalays\b": "vidyalaya",
    r"\beng\b": "english",
    r"\bveddharine\b": "veddharini",
    r"\bvasudev\b": "vasudeo",
    r"\bprath\b": "prathmik",
    r"\bps[\s]\b": "prathmik shala",
    r"\bprashala\b": "prathmik shala",
    r"\bbal[\s]vikas\b": "balvikas",
    r"\bmadhy\.\b": "madhyamik",
    r"\btulsabaikawalvidyalay\.\b": "tulsabai kawal vidyalaya",
    r"\btmc\b": "thane municipal corparation",
    r"\btjc\b": "t.j.chavan",
    r"\brahtriy\.\b": "rashtriya",
    r"\bmuniciple\b": "municipal",
    r"\bmuni\b": "municipal",
    r"\bmun\b": "municipal",
    r"\bt[\s\.]*m[\s\.]*c\b": "thane municipal corporation",
    r"\btb": "t.",
    r"\bjb": "j.",
    r"\beng(\.|lish)?\b": "english",
    r"\bsvkm[\s]sb": "SVKM's",
    r"\bsukhadev\b": "sukhdev",
    r"\bsadiqueshah\b": "sadique shah",
    r"\bxavier(?:'s|s|\s+s)?\b": "xavier's",
    r"\bst\b(?!\.)": "st.",
    r"\bscho\b": "school",
    r"\bpaul(?:'s|s|\s+s)?\b": "paul's",
    r"\bpatrick(?:'s|s|\s+s)?\b": "patrick's",
    r"\bmira(?:'s|s|\s+s)?\b": "mira's",
    r"\bmary(?:'s|s|\s+s)?\b": "mary's",
    r"\bjude(?:'s|s|\s+s)?\b": "jude's",
    r"\bjoseph(?:'s|s|\s+s)?\b": "joseph's",
    r"\bhelena(?:'s|s|\s+s)?\b": "helena's",
    r"\bhari(?:'s|s|\s+s)?\b": "hari's",
    r"\bgeorge(?:'s|s|\s+s)?\b": "george's",
    r"\bfrancis(?:'s|s|\s+s)?\b": "francis's",
    r"\bjoseph(?:'s|s|\s+s)?\b": "joseph's",
    r"\banthony(?:'s|s|\s+s)?\b": "anthony's",
    r"\bandrew(?:'s|s|\s+s)?\b": "andrew's",
    r"\banne(?:'s|s|\s+s)?\b": "anne's",
    r"\bandrewd\b": "andrew's",
    r"\bboy\s+s\b": "boy's",
    r"\bgirl\s+s\b": "girl's",
    r"\bpry\b": "primary",
    r"\bpri\b": "pre",
    r"\beng\b": "english",
    r"\bsndt\b": "s.n.d.t.",
    r"\bsmt\b(?!\.)": "smt.",
    r"\bsies\b": "SIES",
    r"\bShrrrammitrrmandalparthmikvidyamandir\b": "shriram mitra mandal prathmik vidyamandir",
    r"\bShreerammitramandalsanchalit\b": "shreeram mitra mandal sanchalit",
    r"\bprathamik\b": "prathmik",
    r"\bchauhan\b": "chavan",
    r"\bshri[\s]c[\s]s[\s]\b": "shri chhatrapati shivaji",
    r"\bshri[\s]c[\s]s[\s]m[\s]\b": "shri chhatrapati shivaji maharaj",
    r"\bbha\b": "b",
    r"\bmiras\b": "mira's",
    r"\bmaharastra\b": "maharashtra",
    r"\bsamart\b": "samarth",
    r"\bramktushna\b": "ramkrushna",
    r"\bshiriram\b": "shriram",
    r"\brsmnath\b": "ramnath",
    r"\bsent\b(?!\.)": "st.",
    r"\bpraymari\b": "primary",
    r"\bphilomina\b": "philomena",
    r"\bfule\b": "phule",
    r"\badarsh\b": "aadarsh",
    r"\badarash\b": "aadarshn",
    r"\bramdev\b": "ramdeo",
    r"\bmed\b": "",
    r"\bapg\s+s\b":'apj',
    r"\bpvg[\s]s\b": "PVG's",
    r"\bwomen[\s]s\b": "women's",
    r"\bn[\s]m[\s]c[\s]\b": "nmc",
    r"\bmatostri\b": "matoshri",
    r"\bmatoshree\b": "matoshri",
    r"\bprimari\b": "primary",
    r"\bsavitri[\s]bai\b": "savitribai",
    r"\bmalojieaje\b": "malojiraje",
    r"\bmmahtma\b": "mahatma",
    r"\bucch\b": "uccha",
    r"\blok[\s]nayak\b": "loknayak",
    r"\byshwantrav\b": "yeshwantrav",
    r"\bshishy\b": "shishu",
    r"\bshishuvihar\b": "shishu vihar",
    r"\bvlasses\b": "classes",
    r"\bschools\b": "school",
    r"\bbal[\s]vikas\b": "balvikas",
    r"\baranyashwar\b": "aranyeshwar",
    r"\bchankya\b": "chanakya",
    r"\bvisapute\b": "vispute",
    r"\basjram\b": "shram",
    r"\bashramshala\b": "ashram shala",
    r"\bashramschool\b": "ashram school",
    r"\bcoolege\b": "college",
    r"\b[\s]va[\s]\b": "",
    r"\bgujrati\b": "gujarati",
    r"\bsch\b": "school",
    r"\bschooh\b": "school",
    r"\bh[\s]sch\b": "high school",
    r"\bcollage\b": "college",
    r"\rashtriy\b": "rashtriya",
    r"\btakshshila\b": "takshashila",
    r"\bshamanad\b": "shamanand",
    r"\bscoll\b": "school",
    r"\bshool\b": "school",
    r"\bvidhyamandir\b": "vidyamandir",
    r"\bsagaracademy\b": "sagar academy",
    r"\bwamanbaba\b": "vamanbaba",
    r"\bshikchi\b": "sikchi",
    r"\bjagdamba\b": "jagadamba",
    r"\bshivajividyalaya\b": "shivaji vidyalaya",
    r"\blalita[\s]prasad\b": "lalitaprasad",
    r"\bchatrapati\b": "chhatrapati",
    r"\bchhatrpti\b": "chhatrapati",
    r"\bvijay[\s]mala\b": "vijaymala",
    r"\bsantoshbhai[\s]mehta\b": "santoshbhai mehta",
    r"\bsantoshbhaimehta\b": "santoshbhai mehta",
    r"\bhs\b": "high school",
    r"\brayreshwer\b": "rayreshwar",
    r"\banandrushiji\b": "anand rushiji",
    r"\bamebedkar\b": "ambedkar",
    r"\brajesveri\b": "rajeshwari",
    r"\brajeshveri\b": "rajeshwari",
    r"\bbhosle\b": "bhosale",
    r"\brandeo\b": "ramdeo",
    r"\brungha\b": "rungta",
    r"\bpriyasarshani\b": "priyadarshini",
    r"\bparshuram[\s]nike\b": "parshuram naik",
    r"\bnagnsth\b": "nagnath",
    r"\bcerter\b": "centre",
    r"\bcenter\b": "centre",
    r"\bgurugi\b": "guruji",
    r"\bhiray\b": "hire",
    r"\binst\b": "institute",
    r"^\d+$": ""

} 

# ---------------------------------------------
# CITY AND STATE NAME CLEANER
# ---------------------------------------------

CITY_CORRECTIONS = {
    "nagour": "nagpur",
    "nasik": "nashik",
    "bombay": "mumbai",
    "ahmdabad": "ahmedabad",
    "ahemdabad":'ahmedabad',
    "ahemedabad": 'ahmedabad',
    "walchandanagar":"walchandnagar",
    'latue':'latur',
    "puna": "pune",
    'umarga':'omerga',
    'nishik':"nashik",
    'visakhapatnam':'vishakapatnam',
    'devlali':'deolali',
    'nashil':'nashik',
    'gandhinglj':'gandhinglaj',
    'Chatarpati':'Chhatrapati',
    'hubballi':'hubli',
    'sambhajinagar':'sambhaji nagar',
    
    
}

STATE_CORRECTIONS = {
    "mahashttra": "maharashtra",
    "maharastra": "maharashtra",
    "karnatak": "karnataka",
    "andra pradesh": "andhra pradesh",
    "tamilnadu": "tamil nadu"
}


MULTI_WORD_CITIES = {
    "navi mumbai",
    "new delhi",
    "greater noida",
    "port blair",
    "north goa",
    "south goa",
    "west delhi",
    "east delhi",
    "central delhi",
    "old goa",
    "panaji city",
    'Chhatrapati Sambhaji Nagar'
}

# ---------------------------------------------
# SCHOOL NAME STANDARDIZER 
# ---------------------------------------------
    
def standardize_school_name(val, max_passes=6):
    if pd.isna(val) or str(val).strip() == "":
        return val

    s = str(val).lower()
    s = re.sub(r"\([^)]*\)", "", s)          # remove bracket noise
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()

    # iterative replacement loop
    for _ in range(max_passes):
        before = s
        for pattern, repl in SCHOOL_REPLACEMENTS.items():
            s = re.sub(pattern, repl, s, flags=re.IGNORECASE)

        if s == before:  # convergence reached
            break
    
    result = s.title()
    result = re.sub(r"'S\b", "'s", result)
    return result


# -----------------------------
# TRAILING LOCATION REMOVER
# -----------------------------

def drop_trailing_location(s):
    if pd.isna(s) or str(s).strip() == "":
        return s

    words = str(s).split()

    ANCHORS = {
        "school", "college", "science", "commerce", "arts", "art",
        "vidyalaya", "shala", "vidya", "mandir", "vidyamandir",'boys','girls',
        "classes", "ashram", "dnyanpeeth", "prathmik", "mahavidyalaya",
        "excellence"
    }

    anchor_idx = -1
    for i, w in enumerate(words):
        if w.lower() in ANCHORS:
            anchor_idx = i

    if anchor_idx == -1:
        return s

    keep_until = anchor_idx

    # --- Handle "no x", "no. x", AND glued forms like "325Satara"
    if anchor_idx + 1 < len(words):
        nxt = words[anchor_idx + 1].lower()

        if nxt in {"no", "no."} and anchor_idx + 2 < len(words):
            raw = words[anchor_idx + 2]

            # Case 1: clean number
            if raw.isdigit() and len(raw) <= 3:
                keep_until = anchor_idx + 2

            # Case 2: glued number + text (e.g., 325Satara)
            else:
                m = re.match(r"^(\d{1,3})", raw)
                if m:
                    words[anchor_idx + 2] = m.group(1)
                    keep_until = anchor_idx + 2

        # Case 3: "no325Satara" or "no.325Satara"
        else:
            m = re.match(r"^(no\.?|no)(\d{1,3})", nxt)
            if m:
                words[anchor_idx + 1] = "No"
                words.insert(anchor_idx + 2, m.group(2))
                keep_until = anchor_idx + 2

    final_words = words[: keep_until + 1]
    return " ".join(final_words)


# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def normalize_text(val):
    if pd.isna(val) or str(val).strip() == "":
        return val
    return re.sub(r"\s+", " ", str(val).strip()).title()

def clean_phone(val):
    if pd.isna(val) or str(val).strip() == "":
        return val, ""
    num = re.sub(r"\D", "", str(val))
    if num.startswith("91") and len(num) > 10:
        num = num[-10:]
    valid = "Yes" if len(num) == 10 else "No"
    return num, valid

def clean_email(val):
    if pd.isna(val) or str(val).strip() == "":
        return val, ""
    email = str(val).strip().lower()
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    valid = "Yes" if re.match(pattern, email) else "No"
    return email, valid

def find_column(df_cols, aliases):
    for col in df_cols:
        col_lower = col.lower()
        for alias in aliases:
            if alias in col_lower:
                return col
    return None


def standardize_city(val, min_first_word_len=3):
    if pd.isna(val) or str(val).strip() == "":
        return val

    s = str(val).lower().strip()

    # --------------------------------------------------
    # 1. Normalize separators
    # --------------------------------------------------
    s = re.sub(r"[.\-/,]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()

    # --------------------------------------------------
    # 2. Spelling correction (full-string only)
    # --------------------------------------------------
    if s in CITY_CORRECTIONS:
        s = CITY_CORRECTIONS[s]

    words = s.split()
    if not words:
        return val

    # --------------------------------------------------
    # 3. SAFETY RULE: short first word → keep as-is
    # --------------------------------------------------
    if len(words[0]) < min_first_word_len:
        return s.title()

    # --------------------------------------------------
    # 4. Multi-word city whitelist
    # --------------------------------------------------
    if len(words) >= 2:
        first_two = f"{words[0]} {words[1]}"
        if first_two in MULTI_WORD_CITIES:
            return first_two.title()

    # --------------------------------------------------
    # 5. Default: keep only first word
    # --------------------------------------------------
    return words[0].title()


def drop_unwanted_columns(df):
    cols_to_drop = [
        c for c in df.columns
        if (
            c is None
            or str(c).strip() == ""
            or str(c).lower().strip() in {"email_valid", "phone_valid"}
        )
    ]
    return df.drop(columns=cols_to_drop, errors="ignore")


def standardize_state(val):
    if pd.isna(val) or str(val).strip() == "":
        return val

    s = str(val).lower().strip()
    s = re.sub(r"\s+", " ", s)

    # spelling correction
    if s in STATE_CORRECTIONS:
        s = STATE_CORRECTIONS[s]

    return s.title()

# -----------------------------
# LOAD FILES
# -----------------------------
dfs = []
files = list(Path(INPUT_FOLDER).glob("*.xls*")) + list(Path(INPUT_FOLDER).glob("*.csv"))

if not files:
    raise FileNotFoundError("No input files found")

for file in files:
    try:
        df = pd.read_csv(file, encoding="utf-8") if file.suffix == ".csv" else pd.read_excel(file)
        df = drop_unwanted_columns(df)
    except UnicodeDecodeError:
        df = pd.read_csv(file, encoding="cp1252") if file.suffix == ".csv" else pd.read_excel(file)
        df = drop_unwanted_columns(df)

    df["__source_file"] = file.name
    dfs.append(df)

raw_df = pd.concat(dfs, ignore_index=True)
original_count = len(raw_df)

# -----------------------------
# COLUMN DETECTION & RENAMING
# -----------------------------
detected_cols = {}
for canonical, aliases in COLUMN_ALIASES.items():
    found = find_column(raw_df.columns, aliases)
    if found:
        detected_cols[found] = canonical

raw_df = raw_df.rename(columns=detected_cols)

# -----------------------------
# CLEANING
# -----------------------------
if "Name" in raw_df.columns:
    raw_df["Name"] = raw_df["Name"].apply(normalize_text)

if "City/District" in raw_df.columns:
    raw_df["City/District"] = raw_df["City/District"].apply(normalize_text)
    raw_df["City/District"] = raw_df["City/District"].apply(standardize_city)

if "State" in raw_df.columns:
    raw_df["State"] = raw_df["State"].apply(normalize_text)
    raw_df["State"] = raw_df["State"].apply(standardize_state)


if "School/College" in raw_df.columns:
    raw_df["School/College"] = raw_df["School/College"].apply(standardize_school_name)

if "Phone Number" in raw_df.columns:
    raw_df[["Phone Number", "Phone_Valid"]] = raw_df["Phone Number"].apply(
        lambda x: pd.Series(clean_phone(x))
    )

if "Email ID" in raw_df.columns:
    raw_df[["Email ID", "Email_Valid"]] = raw_df["Email ID"].apply(
        lambda x: pd.Series(clean_email(x))
    )

if "School/College" in raw_df.columns:
    raw_df["School/College"] = (
        raw_df["School/College"]
        .apply(drop_trailing_location)
    )



# ---------------------------------------------
# STREAMLIT ENTRY POINT (DO NOT MODIFY LOGIC)
# ---------------------------------------------

def run_cleaning_pipeline(input_files):
    """
    input_files: list of pathlib.Path objects
    returns: cleaned pandas DataFrame
    """

    dfs = []

    for file in input_files:
        try:
            df = pd.read_csv(file, encoding="utf-8") if file.suffix == ".csv" else pd.read_excel(file)
            df = drop_unwanted_columns(df)
        except UnicodeDecodeError:
            df = pd.read_csv(file, encoding="cp1252") if file.suffix == ".csv" else pd.read_excel(file)
            df = drop_unwanted_columns(df)

        df["__source_file"] = file.name
        dfs.append(df)

    raw_df = pd.concat(dfs, ignore_index=True)

    # -----------------------------
    # COLUMN DETECTION & RENAMING
    # -----------------------------
    detected_cols = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        found = find_column(raw_df.columns, aliases)
        if found:
            detected_cols[found] = canonical

    raw_df = raw_df.rename(columns=detected_cols)

    # -----------------------------
    # CLEANING
    # -----------------------------
    if "Name" in raw_df.columns:
        raw_df["Name"] = raw_df["Name"].apply(normalize_text)
    
    if "City/District" in raw_df.columns:
        raw_df["City/District"] = raw_df["City/District"].apply(normalize_text)
        raw_df["City/District"] = raw_df["City/District"].apply(standardize_city)
    
    if "State" in raw_df.columns:
        raw_df["State"] = raw_df["State"].apply(normalize_text)
        raw_df["State"] = raw_df["State"].apply(standardize_state)

    if "School/College" in raw_df.columns:
        raw_df["School/College"] = raw_df["School/College"].apply(standardize_school_name)
        raw_df["School/College"] = raw_df["School/College"].apply(drop_trailing_location)

    if "Phone Number" in raw_df.columns:
        raw_df[["Phone Number", "Phone_Valid"]] = raw_df["Phone Number"].apply(
            lambda x: pd.Series(clean_phone(x))
        )

    if "Email ID" in raw_df.columns:
        raw_df[["Email ID", "Email_Valid"]] = raw_df["Email ID"].apply(
            lambda x: pd.Series(clean_email(x))
        )

    clean_df = raw_df.drop_duplicates()

    return clean_df




# -----------------------------
# DEDUPLICATION
# -----------------------------
clean_df = raw_df.drop_duplicates()

# -----------------------------
# OUTPUTS
# -----------------------------
clean_df.to_csv(f"{OUTPUT_FOLDER}/reviews_cleaned.csv", index=False)

summary_df = pd.DataFrame(
    {
        "Original Rows": [original_count],
        "Rows After Deduplication": [len(clean_df)]
    }
)
summary_df.to_excel(f"{OUTPUT_FOLDER}/data_quality_summary.xlsx", index=False)

print("Phase 1 cleaning completed successfully.")



if __name__ == "__main__":
    # -----------------------------
    # LOAD FILES
    # -----------------------------
    dfs = []
    files = list(Path(INPUT_FOLDER).glob("*.xls*")) + list(Path(INPUT_FOLDER).glob("*.csv"))

    if not files:
        raise FileNotFoundError("No input files found")

    for file in files:
        try:
            df = pd.read_csv(file, encoding="utf-8") if file.suffix == ".csv" else pd.read_excel(file)
        except UnicodeDecodeError:
            df = pd.read_csv(file, encoding="cp1252") if file.suffix == ".csv" else pd.read_excel(file)

        df["__source_file"] = file.name
        dfs.append(df)

    raw_df = pd.concat(dfs, ignore_index=True)
    original_count = len(raw_df)

    # ---- existing logic continues unchanged ----

