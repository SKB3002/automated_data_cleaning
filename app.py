import streamlit as st
import pandas as pd
from pathlib import Path
import tempfile
from data_cleaner import run_cleaning_pipeline   

st.markdown(
    """
    <style>

    /* -----------------------------
       GLOBAL THEME
    ----------------------------- */
    html, body, [class*="css"] {
        background-color: #0e1117;
        color: #d1f7c4;
    }
    
    /* ---------------------------
       GREEN BUTTONS ONLY
    --------------------------- */
    .stButton > button {
        background-color: #2e8b57 !important;
        color: white !important;
        border: none !important;
        border-radius: 6px;
        font-weight: 500;
    }

    div[data-testid="stDownloadButton"] > button {
        background-color: #2e7d32;
        color: white;
        border-radius: 6px;
        border: none;
        font-weight: 600;
    }
    
    div[data-testid="stDownloadButton"] > button:hover {
        background-color: #256428;
        color: white;
    }

    .stButton > button:hover {
        background-color: #3cb371 !important;
        color: white !important;
    }


    /* -----------------------------
       SELECTBOX / INPUTS
    ----------------------------- */
    .stSelectbox div[data-baseweb="select"],
    .stTextInput input,
    .stDateInput input {
        background-color: #0e1117;
        color: #eafff3;
        border: 1px solid #3ddc84;
    }

    /* -----------------------------
       DATAFRAME
    ----------------------------- */
    .stDataFrame {
        background-color: #0e1117;
        border: 1px solid #3ddc84;
    }
    

    /* ---------------------------
       SUBTLE GREEN ACCENT (TITLE)
    --------------------------- */
    h1 {
        border-bottom: 3px solid #2e8b57;
        padding-bottom: 6px;
    }

    /* -----------------------------
       DIVIDERS
    ----------------------------- */
    hr {
        border: 1px solid #3ddc84;
    }
    
    </style>
    """,
    unsafe_allow_html=True
)


st.set_page_config(page_title="Unified Data Cleaner", layout="centered")

st.title("📊Unified Data Cleaner Dashboard")

# --------------------------------------------------
# REQUIRED OUTPUT COLUMNS
# --------------------------------------------------
REQUIRED_FIELDS = [
    "Name",
    "Mobile Number",
    "Email",
    "Institute Name",
    "Board",
    "City",
    "State",
    "Source of Data",
    "Stakeholder Category",
    "Date of Data Addition"
]

AUTO_ALIASES = {
    "Name" : ["name of the teacher", "name of teacher", "name of participant","name of the participant", "participant name", "teacher name", "name"],
    "Mobile Number": ["mobile", "phone", "phone number", "phone no", "contact","contact number", "mobile/contact number"],
    "Email": ["email", "email id", "email address"],
    "Institute Name": ["name of school", "name of the school", "school","school/college", "college", "institution" "institution"],
    "Board": ["board", "medium"],
    "City": ["city", "district","city/district"],
    "State": ["state"],
    "Date of Data Addition": ["date", "timestamp", "registered"]
}

SOURCE_OPTIONS = ["Event", "Sales Team", "Retailer", "Website", "Form", "Other"]
STAKEHOLDER_OPTIONS = ["Teacher", "School", "Student", "Retailer", "Other"]

# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------
uploaded_files = st.file_uploader(
    "Upload CSV / Excel Files",
    type=["csv", "xlsx", "xls"],
    accept_multiple_files=True
)

if not uploaded_files:
    st.stop()

# --------------------------------------------------
# SAVE FILES TEMPORARILY
# --------------------------------------------------
temp_dir = Path(tempfile.mkdtemp())
input_paths = []

for f in uploaded_files:
    path = temp_dir / f.name
    with open(path, "wb") as fp:
        fp.write(f.getbuffer())
    input_paths.append(path)

# --------------------------------------------------
# RUN EXISTING CLEANING PIPELINE
# --------------------------------------------------
with st.spinner("Running cleaning pipeline..."):
    cleaned_df = run_cleaning_pipeline(input_paths)

st.success("Cleaning completed")

st.subheader("Preview Cleaned Data")
st.dataframe(cleaned_df.head(10))

# --------------------------------------------------
# COLUMN MAPPING UI
# --------------------------------------------------
st.subheader("🧩 Column Mapping")

final_df = pd.DataFrame()
available_cols = ["<No Column>"] + list(cleaned_df.columns)

mapping = {}

for field in REQUIRED_FIELDS:
    st.markdown(f"**{field}**")

    auto_match = None
    for col in cleaned_df.columns:
        for a in AUTO_ALIASES.get(field, []):
            if a in col.lower():
                auto_match = col
                break

    if field in ["Source of Data", "Stakeholder Category"]:
        col1, col2 = st.columns(2)

        with col1:
            mapping[field] = st.selectbox(
                "Select Column (optional)",
                available_cols,
                index=available_cols.index(auto_match) if auto_match else 0,
                key=f"{field}_col"
            )

        with col2:
            if field == "Source of Data":
                mapping[field + "_static"] = st.selectbox(
                    "Or select value",
                    ["<None>"] + SOURCE_OPTIONS,
                    key=f"{field}_static"
                )
            else:
                mapping[field + "_static"] = st.selectbox(
                    "Or select value",
                    ["<None>"] + STAKEHOLDER_OPTIONS,
                    key=f"{field}_static"
                )
    else:
        mapping[field] = st.selectbox(
            "Select Column",
            available_cols,
            index=available_cols.index(auto_match) if auto_match else 0,
            key=field
        )


def split_name(name):
    if pd.isna(name) or str(name).strip() == "":
        return "", ""
    parts = str(name).strip().split()
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[-1]


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


def normalize_date(val):
    if pd.isna(val) or str(val).strip() == "":
        return ""

    try:
        # Case 1: already datetime-like
        if hasattr(val, "date"):
            return val.date()

        s = str(val).strip()

        # Try pandas intelligent parser FIRST (handles Nov, timestamps, ISO, etc.)
        dt = pd.to_datetime(s, errors="coerce", dayfirst=False)
        if not pd.isna(dt):
            return dt.date()

        # Manual fallback for numeric ambiguity
        parts = re.split(r"[\/\-]", s.split()[0])
        if len(parts) < 3:
            return ""

        a, b, c = parts

        if not (a.isdigit() and b.isdigit() and c.isdigit()):
            return ""

        a, b, c = int(a), int(b), int(c)

        # Detect format
        if a > 12:
            day, month = a, b
        elif b > 12:
            month, day = a, b
        else:
            day, month = a, b  # default dd/mm

        year = c if c > 31 else c + 2000

        return pd.Timestamp(year=year, month=month, day=day).date()

    except Exception:
        return ""




# --------------------------------------------------
# BUILD FINAL DATASET
# --------------------------------------------------

FINAL_SCHEMA = [
    "First Name",
    "Last Name",
    "Mobile Number",
    "Email",
    "Institute Name",
    "Board",
    "City",
    "State",
    "Source of Data",
    "Stakeholder Category",
    "Date of Data Addition",
]


if st.button("✅ Generate Final Dataset"):

    temp_df = {}

    for field in REQUIRED_FIELDS:
        if field in ["Source of Data", "Stakeholder Category"]:
            col_choice = mapping.get(field)
            static_choice = mapping.get(field + "_static")

            if col_choice and col_choice != "<No Column>":
                temp_df[field] = cleaned_df[col_choice]
            elif static_choice and static_choice != "<None>":
                temp_df[field] = static_choice
            else:
                temp_df[field] = ""

        else:
            col_choice = mapping.get(field)
            if col_choice and col_choice != "<No Column>":
                temp_df[field] = cleaned_df[col_choice]
            else:
                temp_df[field] = ""

    temp_df = pd.DataFrame(temp_df)

    # ---- NAME SPLIT ----
    first_last = temp_df["Name"].apply(split_name)
    temp_df["First Name"] = first_last.apply(lambda x: x[0])
    temp_df["Last Name"] = first_last.apply(lambda x: x[1])
    temp_df.drop(columns=["Name"], inplace=True)

    # ---- DATE NORMALIZATION ----
    temp_df["Date of Data Addition"] = temp_df["Date of Data Addition"].apply(normalize_date)

    # ---- FINAL COLUMN ORDER ----
    final_df = temp_df[
        [
            "First Name",
            "Last Name",
            "Mobile Number",
            "Email",
            "Institute Name",
            "Board",
            "City",
            "State",
            "Source of Data",
            "Stakeholder Category",
            "Date of Data Addition",
        ]
    ]

    final_df = final_df.drop_duplicates(subset=["Mobile Number"], keep="last")
    st.session_state["final_df"] = final_df.copy()


    st.success("Final dataset ready")

    st.subheader("📁 Final Preview")
    st.dataframe(final_df.head(10))

    st.download_button(
        "⬇️ Download Final CSV",
        final_df.to_csv(index=False),
        file_name="final_cleaned_dataset.csv",
        mime="text/csv"
    )


st.divider()
st.header("➕ Master File Merger (Row-wise)")

append_file = st.file_uploader(
    "Upload file to append to the cleaned dataset",
    type=["csv", "xlsx", "xls"],
    key="append_file"
)

if append_file is not None:

    # -----------------------------
    # LOAD FILE
    # -----------------------------
    try:
        if append_file.name.endswith(".csv"):
            append_df = pd.read_csv(append_file)
        else:
            append_df = pd.read_excel(append_file)
    except Exception as e:
        st.error(f"Failed to read file: {e}")
        st.stop()

    st.subheader("Preview File to Append")
    st.dataframe(append_df.head(5))

    # -----------------------------
    # COLUMN ALIGNMENT CHECK
    # -----------------------------
    if "final_df" not in st.session_state:
        st.error("Please generate the final dataset before appending.")
        st.stop()

    final_df = st.session_state["final_df"]
    cleaned_cols = set(FINAL_SCHEMA)
    append_cols = set(append_df.columns)

    missing_in_append = cleaned_cols - append_cols
    extra_in_append = append_cols - cleaned_cols

    if missing_in_append:
        st.warning(
            f"Missing columns in appended file (will be created empty): {missing_in_append}"
        )

    if extra_in_append:
        st.warning(
            f"Extra columns in appended file (will be retained): {extra_in_append}"
        )

    # -----------------------------
    # ALIGN COLUMNS
    # -----------------------------
    for col in missing_in_append:
        append_df[col] = ""

    append_df = append_df[final_df.columns.union(append_df.columns)]

    # -----------------------------
    # APPEND
    # -----------------------------
    if st.button("➕ Merge Rows"):

        combined_df = pd.concat(
            [final_df, append_df],
            ignore_index=True
        )

        st.success(f"Rows appended successfully. Total rows: {len(combined_df)}")

        st.subheader("📄 Combined Dataset Preview")
        st.dataframe(combined_df.head(10))

        st.download_button(
            "⬇️ Download Combined Dataset",
            combined_df.to_csv(index=False),
            file_name="combined_appended_dataset.csv",
            mime="text/csv"
        )

