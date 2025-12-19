# 📊 Unified Data Cleaning & Standardization Dashboard

A production-grade Streamlit application for **cleaning, standardizing, normalizing, and appending large-scale educational datasets** (teachers, schools, colleges, institutions) into a **single, high-quality master dataset**.

This system is designed to handle **real-world messy data**: inconsistent column names, spelling errors, malformed dates, mixed file formats, and partial information.

---

## 🚀 Key Capabilities

### ✅ Automated Data Cleaning
- Name normalization
- Mobile number validation & standardization
- Email validation
- School / College name normalization (rule-based)
- City & State spelling correction (rule-based, deterministic)
- Trailing location removal from institution names
- Removal of unnamed and system-generated columns

### 🧠 Intelligent Column Mapping
- Auto-detects relevant columns using alias matching
- Manual override via UI when auto-detection fails
- Supports static values for:
  - **Source of Data**
  - **Stakeholder Category**

### 📅 Robust Date Normalization
- Handles:
  - `dd/mm/yyyy`
  - `mm/dd/yyyy`
  - `dd-mm-yyyy`
  - `18-Nov-2025 14:43:08`
  - Timestamp formats
- Outputs **date only** (no time)
- Resolves ambiguity using logical heuristics

### 👤 Name Splitting
- Extracts:
  - First Name
  - Last Name
- Ignores middle names safely

### ➕ Row-wise Appending
- Append cleaned data to an existing master file
- Automatically:
  - Aligns columns
  - Creates missing columns
  - Preserves extra columns
- No joins. No accidental overwrites.

---

## 🧱 Final Output Schema

The system always produces data in this exact order:

| Column |
|------|
| First Name |
| Last Name |
| Mobile Number *(Unique Identifier)* |
| Email |
| Institute Name |
| Board |
| City |
| State |
| Source of Data |
| Stakeholder Category |
| Date of Data Addition |

---

## 🖥️ User Interface (Streamlit)

- Clean, white UI
- Green accent for primary actions
- Interactive column selection
- Preview before download
- CSV export
- Safe append workflow

---

## 📂 Project Structure

├── app.py # Streamlit UI

├── data_cleaner.py # Cleaning & normalization engine

├── input_files/ # Raw uploaded files (optional)

├── output_phase1/ # Intermediate outputs (optional)

├── requirements.txt
└── README.md

---

## ⚙️ Installation & Setup

### 1️⃣ Create virtual environment
```bash
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

---

## 🛠️ Tech Stack

- Python 3.9+

- Pandas

- Streamlit

- Regex-based normalization

- Heuristic date parsing

