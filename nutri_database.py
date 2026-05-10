"""
nutri_database.py — NutriScanner SQLite Database Layer
=======================================================
Handles:
  • User account creation with full profile (name, age, gender, activity,
    weight, height, daily water consumption)
  • Per-scan nutritional log (every food scanned → stored with timestamp)
  • End-of-day nutritional aggregation → feeds the risk prediction model
  • Historical trend queries
"""

import sqlite3
import hashlib
import os
import json
from pathlib import Path
from datetime import datetime, date, timedelta
from contextlib import contextmanager
from typing import Optional

# ── Database file lives next to this module ──────────────────────────────────
DB_PATH = Path(__file__).resolve().parent / "nutriscanner.db"


# ─────────────────────────────────────────────────────────────────────────────
# Connection helper
# ─────────────────────────────────────────────────────────────────────────────
@contextmanager
def get_db():
    """Yield a connected, WAL-mode SQLite connection and commit/close cleanly."""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row          # access columns by name
    conn.execute("PRAGMA journal_mode=WAL") # safe for Streamlit multi-thread
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# Schema bootstrap  (run once at app start)
# ─────────────────────────────────────────────────────────────────────────────
def _migrate_db():
    """
    Safe migration: add any columns that exist in the schema but are missing
    from an older on-disk database. ALTER TABLE ADD COLUMN is safe here —
    we catch the OperationalError for duplicate columns.
    """
    migrations = [
        # (table, column, definition)
        ("users", "daily_water_l",  "REAL NOT NULL DEFAULT 2.0"),
        ("users", "activity_level", "TEXT NOT NULL DEFAULT \'Moderately Active\'"),
        ("users", "goal",           "TEXT DEFAULT \'Maintenance\'"),
        ("users", "conditions",     "TEXT DEFAULT \'[]\'"),
        ("users", "diet_type",      "TEXT DEFAULT \'No Restriction\'"),
        ("users", "updated_at",     "TEXT NOT NULL DEFAULT (datetime(\'now\'))"),
        ("daily_summaries", "physical_activity_min", "REAL DEFAULT 0"),
        ("daily_summaries", "total_added_sugar_g",   "REAL DEFAULT 0"),
        ("daily_summaries", "total_trans_fat_g",     "REAL DEFAULT 0"),
        ("food_logs", "added_sugar_g",   "REAL DEFAULT 0"),
        ("food_logs", "trans_fat_g",     "REAL DEFAULT 0"),
        ("food_logs", "potassium_mg",    "REAL DEFAULT 0"),
        ("food_logs", "zinc_mg",         "REAL DEFAULT 0"),
        ("food_logs", "vitamin_c_mg",    "REAL DEFAULT 0"),
        ("food_logs", "magnesium_mg",    "REAL DEFAULT 0"),
        ("food_logs", "mufa_g",          "REAL DEFAULT 0"),
        ("food_logs", "pufa_g",          "REAL DEFAULT 0"),
        ("food_logs", "extras", "TEXT DEFAULT '{}'"),
    ]
    with get_db() as conn:
        for table, col, defn in migrations:
            try:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {defn}")
            except sqlite3.OperationalError:
                pass  # column already exists — fine


def init_db():
    """Create all tables if they don't already exist. Then migrate older DBs."""
    with get_db() as conn:
        conn.executescript("""
        -- ── Users table ──────────────────────────────────────────────────
        CREATE TABLE IF NOT EXISTS users (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            username        TEXT    UNIQUE NOT NULL,
            password_hash   TEXT    NOT NULL,

            -- Personal info (collected at sign-up)
            full_name       TEXT    NOT NULL,
            email           TEXT    UNIQUE NOT NULL,
            age             INTEGER NOT NULL,
            gender          TEXT    NOT NULL,          -- 'Male' | 'Female' | 'Other'
            weight_kg       REAL    NOT NULL,
            height_cm       REAL    NOT NULL,
            activity_level  TEXT    NOT NULL,          -- Sedentary / Lightly / Moderately / Very / Super
            daily_water_l   REAL    NOT NULL DEFAULT 2.0,

            -- Optional health extras
            goal            TEXT    DEFAULT 'Maintenance',
            conditions      TEXT    DEFAULT '[]',      -- JSON list
            diet_type       TEXT    DEFAULT 'No Restriction',

            created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
            updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        -- ── Food scan log ─────────────────────────────────────────────────
        -- One row per food item scanned (whether via photo, label, or search).
        CREATE TABLE IF NOT EXISTS food_logs (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            scan_date       TEXT    NOT NULL,          -- 'YYYY-MM-DD'
            scan_time       TEXT    NOT NULL,          -- 'HH:MM:SS'
            food_name       TEXT    NOT NULL,
            source          TEXT    DEFAULT 'manual',  -- 'photo' | 'label' | 'search' | 'manual'

            -- Core macros
            calories_kcal   REAL    DEFAULT 0,
            protein_g       REAL    DEFAULT 0,
            carbs_g         REAL    DEFAULT 0,
            fat_g           REAL    DEFAULT 0,
            fiber_g         REAL    DEFAULT 0,
            sugar_g         REAL    DEFAULT 0,
            added_sugar_g   REAL    DEFAULT 0,
            saturated_fat_g REAL    DEFAULT 0,
            trans_fat_g     REAL    DEFAULT 0,

            -- Micronutrients
            sodium_mg       REAL    DEFAULT 0,
            potassium_mg    REAL    DEFAULT 0,
            calcium_mg      REAL    DEFAULT 0,
            iron_mg         REAL    DEFAULT 0,
            zinc_mg         REAL    DEFAULT 0,
            vitamin_d_iu    REAL    DEFAULT 0,
            vitamin_b12_mcg REAL    DEFAULT 0,
            vitamin_c_mg    REAL    DEFAULT 0,
            magnesium_mg    REAL    DEFAULT 0,

            -- Fats breakdown
            mufa_g          REAL    DEFAULT 0,
            pufa_g          REAL    DEFAULT 0,

            -- Raw extras stored as JSON for extensibility
            extras          TEXT    DEFAULT '{}'
        );

        -- ── Daily summaries (computed & cached per day) ───────────────────
        -- Rebuilt each time a new scan is added for that day.
        CREATE TABLE IF NOT EXISTS daily_summaries (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            summary_date    TEXT    NOT NULL,          -- 'YYYY-MM-DD'

            -- Aggregated totals (summed from food_logs for that day)
            total_calories  REAL    DEFAULT 0,
            total_protein_g REAL    DEFAULT 0,
            total_carbs_g   REAL    DEFAULT 0,
            total_fat_g     REAL    DEFAULT 0,
            total_fiber_g   REAL    DEFAULT 0,
            total_sugar_g   REAL    DEFAULT 0,
            total_added_sugar_g  REAL DEFAULT 0,
            total_saturated_fat_g REAL DEFAULT 0,
            total_trans_fat_g    REAL DEFAULT 0,
            total_sodium_mg      REAL DEFAULT 0,
            total_potassium_mg   REAL DEFAULT 0,
            total_calcium_mg     REAL DEFAULT 0,
            total_iron_mg        REAL DEFAULT 0,
            total_vitamin_d_iu   REAL DEFAULT 0,
            total_vitamin_b12_mcg REAL DEFAULT 0,
            total_water_l        REAL DEFAULT 0,       -- from user profile (constant per day)
            physical_activity_min REAL DEFAULT 0,      -- user can update this

            item_count      INTEGER DEFAULT 0,
            last_updated    TEXT    NOT NULL DEFAULT (datetime('now')),

            UNIQUE(user_id, summary_date)
        );

        -- ── Risk prediction history ───────────────────────────────────────
        -- Stores each time we ran the prediction model so trends can be shown.
        CREATE TABLE IF NOT EXISTS risk_history (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            assessed_date   TEXT    NOT NULL,          -- 'YYYY-MM-DD'
            assessed_at     TEXT    NOT NULL DEFAULT (datetime('now')),
            source          TEXT    DEFAULT 'daily_summary', -- or 'manual'

            -- Risk probabilities (0.0 – 1.0)
            diabetes_risk   REAL    DEFAULT 0,
            hypertension_risk REAL  DEFAULT 0,
            heart_disease_risk REAL DEFAULT 0,
            obesity_risk    REAL    DEFAULT 0,
            anemia_risk     REAL    DEFAULT 0,
            kidney_disease_risk REAL DEFAULT 0,

            bmi             REAL    DEFAULT 0,

            -- Full input snapshot (JSON) so we can audit/replay
            input_snapshot  TEXT    DEFAULT '{}'
        );

        -- ── Indexes for fast date-range queries ───────────────────────────
        CREATE INDEX IF NOT EXISTS idx_food_logs_user_date
            ON food_logs(user_id, scan_date);

        CREATE INDEX IF NOT EXISTS idx_daily_summaries_user_date
            ON daily_summaries(user_id, summary_date);

        CREATE INDEX IF NOT EXISTS idx_risk_history_user_date
            ON risk_history(user_id, assessed_date);
        """)


# ─────────────────────────────────────────────────────────────────────────────
# Password helpers
# ─────────────────────────────────────────────────────────────────────────────
def _hash_password(password: str) -> str:
    """SHA-256 hash (bcrypt preferred for production; kept simple here)."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, stored_hash: str) -> bool:
    return _hash_password(password) == stored_hash


# ─────────────────────────────────────────────────────────────────────────────
# User management
# ─────────────────────────────────────────────────────────────────────────────
def create_user(
    username: str,
    password: str,
    full_name: str,
    email: str,
    age: int,
    gender: str,
    weight_kg: float,
    height_cm: float,
    activity_level: str,
    daily_water_l: float,
    goal: str = "Maintenance",
    conditions: list = None,
    diet_type: str = "No Restriction",
) -> tuple[bool, str]:
    """
    Register a new user.
    Returns (True, "ok") on success or (False, error_message) on failure.
    """
    if conditions is None:
        conditions = ["None"]
    try:
        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO users
                    (username, password_hash, full_name, email, age, gender,
                     weight_kg, height_cm, activity_level, daily_water_l,
                     goal, conditions, diet_type)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    username.strip().lower(),
                    _hash_password(password),
                    full_name.strip(),
                    email.strip().lower(),
                    int(age),
                    gender,
                    float(weight_kg),
                    float(height_cm),
                    activity_level,
                    float(daily_water_l),
                    goal,
                    json.dumps(conditions),
                    diet_type,
                ),
            )
        return True, "ok"
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "Username already taken."
        if "email" in str(e):
            return False, "Email already registered."
        return False, str(e)
    except Exception as e:
        return False, str(e)


def login_user(username: str, password: str) -> tuple[bool, Optional[dict]]:
    """
    Authenticate a user.
    Returns (True, user_dict) or (False, None).
    Always returns a plain Python dict — never a sqlite3.Row.
    """
    user_dict = None
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username.strip().lower(),)
        ).fetchone()
        if row is not None:
            # Must convert INSIDE the with-block while connection is alive
            user_dict = {k: row[k] for k in row.keys()}

    if user_dict is None:
        return False, None
    if not verify_password(password, user_dict["password_hash"]):
        return False, None

    return True, user_dict


def get_user_by_id(user_id: int) -> Optional[dict]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if row is None:
            return None
        return {k: row[k] for k in row.keys()}


def update_user_profile(user_id: int, **fields) -> bool:
    """Update any subset of profile fields."""
    allowed = {
        "full_name", "email", "age", "gender", "weight_kg", "height_cm",
        "activity_level", "daily_water_l", "goal", "conditions", "diet_type"
    }
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return False
    if "conditions" in updates and isinstance(updates["conditions"], list):
        updates["conditions"] = json.dumps(updates["conditions"])
    updates["updated_at"] = datetime.now().isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [user_id]
    with get_db() as conn:
        conn.execute(f"UPDATE users SET {set_clause} WHERE id = ?", values)
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Food log  (one row per scanned item)
# ─────────────────────────────────────────────────────────────────────────────
def log_food(
    user_id: int,
    food_name: str,
    nutrition: dict,
    source: str = "manual",
    scan_datetime: datetime = None,
) -> int:
    """
    Insert one food-scan row and refresh the daily summary.

    `nutrition` keys (all optional, default 0):
        calories_kcal, protein_g, carbs_g, fat_g, fiber_g, sugar_g,
        added_sugar_g, saturated_fat_g, trans_fat_g, sodium_mg, potassium_mg,
        calcium_mg, iron_mg, zinc_mg, vitamin_d_iu, vitamin_b12_mcg,
        vitamin_c_mg, magnesium_mg, mufa_g, pufa_g
    Returns the new row id.
    """
    if scan_datetime is None:
        scan_datetime = datetime.now()

    scan_date = scan_datetime.strftime("%Y-%m-%d")
    scan_time = scan_datetime.strftime("%H:%M:%S")

    def _f(key):
        return float(nutrition.get(key, 0) or 0)

    known_keys = {
        "calories_kcal", "protein_g", "carbs_g", "fat_g", "fiber_g",
        "sugar_g", "added_sugar_g", "saturated_fat_g", "trans_fat_g",
        "sodium_mg", "potassium_mg", "calcium_mg", "iron_mg", "zinc_mg",
        "vitamin_d_iu", "vitamin_b12_mcg", "vitamin_c_mg", "magnesium_mg",
        "mufa_g", "pufa_g",
    }
    extras = {k: v for k, v in nutrition.items() if k not in known_keys}

    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO food_logs (
                user_id, scan_date, scan_time, food_name, source,
                calories_kcal, protein_g, carbs_g, fat_g, fiber_g,
                sugar_g, added_sugar_g, saturated_fat_g, trans_fat_g,
                sodium_mg, potassium_mg, calcium_mg, iron_mg, zinc_mg,
                vitamin_d_iu, vitamin_b12_mcg, vitamin_c_mg, magnesium_mg,
                mufa_g, pufa_g, extras
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                user_id, scan_date, scan_time, food_name, source,
                _f("calories_kcal"), _f("protein_g"), _f("carbs_g"), _f("fat_g"), _f("fiber_g"),
                _f("sugar_g"), _f("added_sugar_g"), _f("saturated_fat_g"), _f("trans_fat_g"),
                _f("sodium_mg"), _f("potassium_mg"), _f("calcium_mg"), _f("iron_mg"), _f("zinc_mg"),
                _f("vitamin_d_iu"), _f("vitamin_b12_mcg"), _f("vitamin_c_mg"), _f("magnesium_mg"),
                _f("mufa_g"), _f("pufa_g"), json.dumps(extras),
            ),
        )
        new_id = cursor.lastrowid

    # Always keep daily summary in sync
    _refresh_daily_summary(user_id, scan_date)
    return new_id


def delete_food_log(log_id: int, user_id: int) -> bool:
    """Remove a food log entry and refresh the summary for that day."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT scan_date FROM food_logs WHERE id = ? AND user_id = ?",
            (log_id, user_id)
        ).fetchone()
        if not row:
            return False
        scan_date = row["scan_date"]
        conn.execute(
            "DELETE FROM food_logs WHERE id = ? AND user_id = ?",
            (log_id, user_id)
        )
    _refresh_daily_summary(user_id, scan_date)
    return True


def get_food_logs_for_day(user_id: int, day: str = None) -> list[dict]:
    """
    Return all food logs for a specific day.
    `day` is 'YYYY-MM-DD'; defaults to today.
    """
    if day is None:
        day = date.today().isoformat()
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM food_logs WHERE user_id = ? AND scan_date = ? ORDER BY scan_time",
            (user_id, day)
        ).fetchall()
        return [dict(r) for r in rows]


# ─────────────────────────────────────────────────────────────────────────────
# Daily summary  (aggregated nutritional totals for one day)
# ─────────────────────────────────────────────────────────────────────────────
def _refresh_daily_summary(user_id: int, day: str):
    """
    Recompute and upsert the daily_summaries row for (user_id, day).
    Also pulls water intake from the user profile.
    """
    with get_db() as conn:
        # Aggregate food logs
        agg = conn.execute(
            """
            SELECT
                COUNT(*)              AS item_count,
                SUM(calories_kcal)    AS cal,
                SUM(protein_g)        AS pro,
                SUM(carbs_g)          AS carb,
                SUM(fat_g)            AS fat,
                SUM(fiber_g)          AS fib,
                SUM(sugar_g)          AS sug,
                SUM(added_sugar_g)    AS asug,
                SUM(saturated_fat_g)  AS sfat,
                SUM(trans_fat_g)      AS tfat,
                SUM(sodium_mg)        AS sod,
                SUM(potassium_mg)     AS pot,
                SUM(calcium_mg)       AS cal_m,
                SUM(iron_mg)          AS iron,
                SUM(vitamin_d_iu)     AS vitd,
                SUM(vitamin_b12_mcg)  AS b12
            FROM food_logs
            WHERE user_id = ? AND scan_date = ?
            """,
            (user_id, day)
        ).fetchone()

        # Pull water intake from user profile
        user_row = conn.execute(
            "SELECT daily_water_l FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        water_l = float(user_row["daily_water_l"]) if user_row else 2.0

        def _v(val):
            return float(val) if val is not None else 0.0

        conn.execute(
            """
            INSERT INTO daily_summaries (
                user_id, summary_date,
                total_calories, total_protein_g, total_carbs_g, total_fat_g,
                total_fiber_g, total_sugar_g, total_added_sugar_g,
                total_saturated_fat_g, total_trans_fat_g,
                total_sodium_mg, total_potassium_mg, total_calcium_mg,
                total_iron_mg, total_vitamin_d_iu, total_vitamin_b12_mcg,
                total_water_l, item_count, last_updated
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(user_id, summary_date) DO UPDATE SET
                total_calories         = excluded.total_calories,
                total_protein_g        = excluded.total_protein_g,
                total_carbs_g          = excluded.total_carbs_g,
                total_fat_g            = excluded.total_fat_g,
                total_fiber_g          = excluded.total_fiber_g,
                total_sugar_g          = excluded.total_sugar_g,
                total_added_sugar_g    = excluded.total_added_sugar_g,
                total_saturated_fat_g  = excluded.total_saturated_fat_g,
                total_trans_fat_g      = excluded.total_trans_fat_g,
                total_sodium_mg        = excluded.total_sodium_mg,
                total_potassium_mg     = excluded.total_potassium_mg,
                total_calcium_mg       = excluded.total_calcium_mg,
                total_iron_mg          = excluded.total_iron_mg,
                total_vitamin_d_iu     = excluded.total_vitamin_d_iu,
                total_vitamin_b12_mcg  = excluded.total_vitamin_b12_mcg,
                total_water_l          = excluded.total_water_l,
                item_count             = excluded.item_count,
                last_updated           = excluded.last_updated
            """,
            (
                user_id, day,
                _v(agg["cal"]), _v(agg["pro"]), _v(agg["carb"]), _v(agg["fat"]),
                _v(agg["fib"]), _v(agg["sug"]), _v(agg["asug"]),
                _v(agg["sfat"]), _v(agg["tfat"]),
                _v(agg["sod"]), _v(agg["pot"]), _v(agg["cal_m"]),
                _v(agg["iron"]), _v(agg["vitd"]), _v(agg["b12"]),
                water_l, int(agg["item_count"] or 0),
                datetime.now().isoformat(),
            )
        )


def get_daily_summary(user_id: int, day: str = None) -> Optional[dict]:
    """Return the daily summary row for a given day (today by default)."""
    if day is None:
        day = date.today().isoformat()
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM daily_summaries WHERE user_id = ? AND summary_date = ?",
            (user_id, day)
        ).fetchone()
        return dict(row) if row else None


def get_daily_summary_as_model_input(user_id: int, day: str = None) -> Optional[dict]:
    """
    Return the daily summary formatted as the exact 19-feature dict
    that run_prediction() expects. Also includes weight/height for BMI.
    """
    if day is None:
        day = date.today().isoformat()

    summary = get_daily_summary(user_id, day)
    user    = get_user_by_id(user_id)

    if summary is None or user is None:
        return None

    activity_min_map = {
        "Sedentary":         5,
        "Lightly Active":    20,
        "Moderately Active": 45,
        "Very Active":       75,
        "Super Active":      120,
    }
    activity_min = activity_min_map.get(user.get("activity_level", "Moderately Active"), 45)

    return {
        # From daily summary
        "Daily_Calories_kcal":   summary["total_calories"],
        "Carbohydrates_g":       summary["total_carbs_g"],
        "Protein_g":             summary["total_protein_g"],
        "Total_Fat_g":           summary["total_fat_g"],
        "Saturated_Fat_g":       summary["total_saturated_fat_g"],
        "Trans_Fat_g":           summary["total_trans_fat_g"],
        "Total_Sugar_g":         summary["total_sugar_g"],
        "Added_Sugar_g":         summary["total_added_sugar_g"],
        "Fiber_g":               summary["total_fiber_g"],
        "Sodium_mg":             summary["total_sodium_mg"],
        "Potassium_mg":          summary["total_potassium_mg"],
        "Calcium_mg":            summary["total_calcium_mg"],
        "Iron_mg":               summary["total_iron_mg"],
        "Vitamin_D_IU":          summary["total_vitamin_d_iu"],
        "Vitamin_B12_mcg":       summary["total_vitamin_b12_mcg"],
        "Water_Intake_L":        summary["total_water_l"],
        "Physical_Activity_min": summary.get("physical_activity_min") or activity_min,
        # From user profile
        "Age":    user["age"],
        "Gender": 1 if user["gender"] == "Male" else 0,
        # For BMI calculation inside run_prediction()
        "weight_kg":  user["weight_kg"],
        "height_cm":  user["height_cm"],
    }


def update_daily_activity(user_id: int, activity_min: float, day: str = None):
    """Let the user log today's physical activity minutes."""
    if day is None:
        day = date.today().isoformat()
    # Ensure summary row exists first
    _refresh_daily_summary(user_id, day)
    with get_db() as conn:
        conn.execute(
            """
            UPDATE daily_summaries
            SET physical_activity_min = ?, last_updated = ?
            WHERE user_id = ? AND summary_date = ?
            """,
            (float(activity_min), datetime.now().isoformat(), user_id, day)
        )


# ─────────────────────────────────────────────────────────────────────────────
# Risk history
# ─────────────────────────────────────────────────────────────────────────────
def save_risk_assessment(
    user_id: int,
    predictions: dict,
    bmi: float,
    input_snapshot: dict = None,
    source: str = "daily_summary",
    assessed_date: str = None,
):
    """
    Persist a risk prediction result.
    `predictions` is the dict returned by run_prediction().
    """
    if assessed_date is None:
        assessed_date = date.today().isoformat()

    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO risk_history (
                user_id, assessed_date, source,
                diabetes_risk, hypertension_risk, heart_disease_risk,
                obesity_risk, anemia_risk, kidney_disease_risk,
                bmi, input_snapshot
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                user_id, assessed_date, source,
                predictions.get("Diabetes_Risk",      {}).get("prob", 0),
                predictions.get("Hypertension_Risk",  {}).get("prob", 0),
                predictions.get("Heart_Disease_Risk", {}).get("prob", 0),
                predictions.get("Obesity_Risk",       {}).get("prob", 0),
                predictions.get("Anemia_Risk",        {}).get("prob", 0),
                predictions.get("Kidney_Disease_Risk",{}).get("prob", 0),
                bmi,
                json.dumps(input_snapshot or {}),
            )
        )


def get_risk_history(user_id: int, days: int = 30) -> list[dict]:
    """Return the last N days of risk assessments (most recent first)."""
    since = (date.today() - timedelta(days=days)).isoformat()
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT * FROM risk_history
            WHERE user_id = ? AND assessed_date >= ?
            ORDER BY assessed_at DESC
            """,
            (user_id, since)
        ).fetchall()
        return [dict(r) for r in rows]


# ─────────────────────────────────────────────────────────────────────────────
# Trend helpers  (for the Trends & Insights page)
# ─────────────────────────────────────────────────────────────────────────────
def get_nutrition_trend(user_id: int, days: int = 14) -> list[dict]:
    """
    Return daily summaries for the last N days (chronological).
    Empty days are NOT included (only days with logged food).
    """
    since = (date.today() - timedelta(days=days)).isoformat()
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT * FROM daily_summaries
            WHERE user_id = ? AND summary_date >= ?
            ORDER BY summary_date ASC
            """,
            (user_id, since)
        ).fetchall()
        return [dict(r) for r in rows]


# ─────────────────────────────────────────────────────────────────────────────
# Utility: map comp2 / label-scanner nutrition dict → log_food nutrition dict
# ─────────────────────────────────────────────────────────────────────────────
def map_comp2_to_log(comp2_data: dict) -> dict:
    """
    Convert a Comp2 (Nutrition DB) result dict to the format log_food expects.
    comp2_data keys: Calories, Proteins (g), Carbohydrates (g), Fats (g),
                     Sodium (mg), Calcium (mg), Iron (mg), Zinc (mg),
                     Vitamin D (µg), Vitamin B12 (µg), SFA (g), MUFA (g), PUFA (g) …
    """
    def _f(key):
        return float(comp2_data.get(key, 0) or 0)

    return {
        "calories_kcal":    _f("Calories"),
        "protein_g":        _f("Proteins (g)"),
        "carbs_g":          _f("Carbohydrates (g)"),
        "fat_g":            _f("Fats (g)"),
        "sodium_mg":        _f("Sodium (mg)"),
        "calcium_mg":       _f("Calcium (mg)"),
        "iron_mg":          _f("Iron (mg)"),
        "zinc_mg":          _f("Zinc (mg)"),
        "vitamin_c_mg":     _f("Vitamin C (mg)"),
        "vitamin_d_iu":     _f("Vitamin D (µg)") * 40,   # µg → IU approx
        "vitamin_b12_mcg":  _f("Vitamin B12 (µg)"),
        "magnesium_mg":     _f("Magnesium (mg)"),
        "saturated_fat_g":  _f("SFA (g)"),
        "mufa_g":           _f("MUFA (g)"),
        "pufa_g":           _f("PUFA (g)"),
    }


def map_label_to_log(label_data: dict) -> dict:
    """
    Convert a label-scanner result dict to the format log_food expects.
    label_data keys: energy_kcal_per_100g, protein_g, carbohydrates_g,
                     total_fat_g, saturated_fat_g, trans_fat_g, fiber_g,
                     sugar_g, sodium_mg, mufa_g, pufa_g …
    """
    def _f(key):
        return float(label_data.get(key, 0) or 0)

    return {
        "calories_kcal":    _f("energy_kcal_per_100g"),
        "protein_g":        _f("protein_g"),
        "carbs_g":          _f("carbohydrates_g"),
        "fat_g":            _f("total_fat_g"),
        "saturated_fat_g":  _f("saturated_fat_g"),
        "trans_fat_g":      _f("trans_fat_g"),
        "fiber_g":          _f("fiber_g"),
        "sugar_g":          _f("sugar_g"),
        "sodium_mg":        _f("sodium_mg"),
        "mufa_g":           _f("mufa_g"),
        "pufa_g":           _f("pufa_g"),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Bootstrap on import
# ─────────────────────────────────────────────────────────────────────────────
init_db()
_migrate_db()