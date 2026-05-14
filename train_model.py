"""
train_model.py
אימון מודל סיווג לנבא סטטוס אישור בקשות חקלאיות
"""

import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report

# ── 1. טעינת נתונים ──────────────────────────────────────────────────────────
BASE = os.path.dirname(__file__)
CSV  = os.path.join(BASE, "agricultural_permits_dataset_fixed.csv")

df = pd.read_csv(CSV)
print(f"נטענו {len(df):,} שורות, {len(df.columns)} עמודות")

# ── 2. הגדרת X ו-y ───────────────────────────────────────────────────────────
# מושמטים: מזהה_בקשה (ID), סיבת_ההחלטה (data leakage)
DROP_COLS = ["מזהה_בקשה", "סיבת_ההחלטה"]
TARGET    = "סטטוס_אישור"

X = df.drop(columns=DROP_COLS + [TARGET])
y = df[TARGET]

print(f"\nחלוקת target:\n{y.value_counts().to_string()}")

# ── 3. הגדרת עמודות ──────────────────────────────────────────────────────────
NUM_COLS = [
    "שטח_מבוקש_מ2", "שטח_חקלאי_דונם", "מספר_בעלי_חיים",
    "מרחק_מכביש_מטר", "מרחק_ממגורים_מטר", "גובה_מבנה_מטר",
]
CAT_COLS = [
    "מחוז", "אזור", "סוג_מבנה",
    "פנלים_סולאריים", "ייעוד_חקלאי", "עמידה_בתמא", "מכתב_המלצה",
]

# ── 4. חלוקה לאימון ובדיקה ───────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y,      # שמירה על פרופורציות ה-target
)
print(f"\nאימון: {len(X_train)} שורות | בדיקה: {len(X_test)} שורות")

# ── 5. Pipeline עיבוד מקדים + מודל ──────────────────────────────────────────
num_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
])

cat_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
])

preprocessor = ColumnTransformer([
    ("num", num_transformer, NUM_COLS),
    ("cat", cat_transformer, CAT_COLS),
])

model_pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier",   RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        random_state=42,
        class_weight="balanced",
    )),
])

# ── 6. אימון ─────────────────────────────────────────────────────────────────
print("\nמאמן את המודל...")
model_pipeline.fit(X_train, y_train)

# ── 7. הערכה ─────────────────────────────────────────────────────────────────
y_pred = model_pipeline.predict(X_test)
acc    = accuracy_score(y_test, y_pred)

print(f"\n{'='*45}")
print(f"  דיוק כולל (Accuracy): {acc:.1%}")
print(f"{'='*45}")
print("\nדוח מפורט:")
print(classification_report(y_test, y_pred, zero_division=0))

# ── 8. שמירת המודל ───────────────────────────────────────────────────────────
MODEL_PATH = os.path.join(BASE, "model.pkl")
joblib.dump(model_pipeline, MODEL_PATH)
print(f"המודל נשמר: {MODEL_PATH}")
