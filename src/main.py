"""Main Orchestrator for Serverless Indoor Cycling Training System.

WorldTour Indoor Coach & Scheduler:
- Evaluates recent athlete telemetry from Intervals.icu (MyWhoosh / Garmin Edge).
- Executes 3:1 mesocycle state machine and auto-adaptive FTP progression.
- Cleans up previously scheduled managed workouts for the incoming week.
- Generates structured, Elite Suito ERG optimized workouts (strictly 42-60m).
- Publishes workouts to Intervals.icu calendar.
- Updates and persists athlete state in state/athlete_state.json.
"""

import argparse
from datetime import datetime, timedelta
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

from intervals_client import IntervalsClient
from performance_analyzer import PerformanceAnalyzer
from workout_builder import WorkoutBuilder

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("pt_cycling.orchestrator")

DAY_OFFSET_MAP = {
    "MON": 0,
    "TUE": 1,
    "WED": 2,
    "THU": 3,
    "FRI": 4,
    "SAT": 5,
    "SUN": 6,
    "LUN": 0,
    "MAR": 1,
    "MER": 2,
    "GIO": 3,
    "VEN": 4,
    "SAB": 5,
    "DOM": 6
}


def load_json_file(file_path: str, default: Dict[str, Any]) -> Dict[str, Any]:
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
    return default


def save_json_file(file_path: str, data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"Persisted updated state to {file_path}")


def get_next_week_dates(start_from: Optional[datetime] = None) -> Tuple[datetime, datetime]:
    """Calculate date of next Monday and the full incoming week (Monday to Sunday)."""
    now = start_from or datetime.now()
    days_until_next_monday = (7 - now.weekday()) % 7
    if days_until_next_monday == 0:
        days_until_next_monday = 7
    next_monday = (now + timedelta(days=days_until_next_monday)).replace(
        hour=7, minute=0, second=0, microsecond=0
    )
    next_sunday = next_monday + timedelta(days=6, hours=16)
    return next_monday, next_sunday



def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PT Cycling - Serverless WorldTour Indoor Training Orchestrator"
    )
    parser.add_argument(
        "--training-days",
        type=str,
        default="",
        help="Comma-separated training days (e.g. 'MON,WED,FRI' or 'TUE,THU,FRI')"
    )
    parser.add_argument(
        "--max-duration-min",
        type=int,
        default=0,
        help="Max duration in minutes (enforced between 42 and 60 min)"
    )
    parser.add_argument(
        "--weekday-duration-min",
        type=int,
        default=0,
        help="Target duration for weekday sessions (42-60 min)"
    )
    parser.add_argument(
        "--friday-duration-min",
        type=int,
        default=0,
        help="Target duration for weekend/Friday sessions (42-60 min)"
    )
    parser.add_argument(
        "--override-ftp",
        type=int,
        default=0,
        help="Manual FTP override in Watts (optional)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without calling external Intervals.icu mutations"
    )
    parser.add_argument(
        "--state-file",
        type=str,
        default="state/athlete_state.json",
        help="Path to persistent athlete state JSON"
    )
    parser.add_argument(
        "--config-file",
        type=str,
        default="config/athlete_profile.json",
        help="Path to athlete configuration JSON"
    )
    return parser.parse_args()


def write_github_step_summary(markdown_text: str) -> None:
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_path:
        try:
            with open(summary_path, "a", encoding="utf-8") as f:
                f.write(markdown_text + "\n")
        except Exception as e:
            logger.warning(f"Could not write to GITHUB_STEP_SUMMARY: {e}")


def main() -> int:
    args = parse_arguments()
    logger.info("🚴 Starting PT Cycling WorldTour Serverless Indoor Coach...")

    athlete_id = os.getenv("INTERVALS_ATHLETE_ID", "")
    api_key = os.getenv("INTERVALS_API_KEY", "")

    # Load persistent state and profile
    state = load_json_file(
        args.state_file,
        {
            "current_ftp": 205,
            "mesocycle_week": 1,
            "preferred_days": ["MON", "WED", "FRI"],
            "min_duration": 42,
            "max_duration": 60,
            "weekday_duration": 50,
            "friday_duration": 60,
            "history": []
        }
    )

    profile = load_json_file(args.config_file, {})

    # Determine training days
    if args.training_days.strip():
        days_input = [d.strip().upper() for d in args.training_days.split(",") if d.strip()]
    else:
        days_input = state.get("preferred_days", ["MON", "WED", "FRI"])

    normalized_days: List[str] = []
    for d in days_input:
        if d in DAY_OFFSET_MAP:
            # Normalize to English 3-letter representation
            idx = DAY_OFFSET_MAP[d]
            english_names = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
            normalized_days.append(english_names[idx])
    if not normalized_days:
        normalized_days = ["MON", "WED", "FRI"]

    # Determine session durations (strictly 42-60 minutes)
    if args.max_duration_min > 0:
        base_dur = max(42, min(60, args.max_duration_min))
        weekday_dur = base_dur
        friday_dur = base_dur
    else:
        weekday_dur = max(
            42, min(60, args.weekday_duration_min or state.get("weekday_duration", 50))
        )
        friday_dur = max(
            42, min(60, args.friday_duration_min or state.get("friday_duration", 60))
        )

    # Initialize API Client
    client = IntervalsClient(athlete_id=athlete_id, api_key=api_key)
    if not client.is_configured():
        logger.warning(
            "⚠️ INTERVALS_ATHLETE_ID or INTERVALS_API_KEY missing. Running in DRY-RUN simulation mode."
        )

    # Date calculations
    today = datetime.now()
    seven_days_ago = (today - timedelta(days=7)).strftime("%Y-%m-%d")
    today_str = today.strftime("%Y-%m-%d")

    # Fetch past activities and events for evaluation
    past_activities = client.get_activities(oldest=seven_days_ago, newest=today_str)
    past_events = client.get_events(oldest=seven_days_ago, newest=today_str)

    # Evaluate performance and progression
    analyzer = PerformanceAnalyzer(
        min_compliance_to_advance=0.85,
        max_decoupling_pct=6.5,
        auto_ftp_increase_pct=0.02
    )

    evaluations = analyzer.analyze_completed_activities(past_activities, past_events)
    eval_result = analyzer.evaluate_progression(
        current_state=state,
        recent_evaluations=evaluations,
        override_ftp=args.override_ftp if args.override_ftp > 0 else None
    )

    effective_ftp = eval_result.next_ftp
    effective_week = eval_result.next_week

    # Sync FTP to Intervals.icu if changed or overridden
    if eval_result.ftp_increased or (args.override_ftp and args.override_ftp > 0):
        logger.info(f"Synchronizing new FTP ({effective_ftp}W) to Intervals.icu...")
        if not args.dry_run:
            client.update_ftp(effective_ftp)

    # Incoming week planning window
    next_monday, next_sunday = get_next_week_dates(today)
    window_start_str = next_monday.strftime("%Y-%m-%d")
    window_end_str = next_sunday.strftime("%Y-%m-%d")

    logger.info(f"Target Incoming Week: {window_start_str} to {window_end_str}")

    # Remove any existing managed workouts for next week
    if not args.dry_run:
        client.cleanup_managed_events(window_start_str, window_end_str)

    # Telegram notification helper
    def send_telegram_notification(msg: str) -> None:
        tg_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        tg_chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
        if tg_token and tg_chat_id:
            try:
                tg_url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
                payload = {
                    "chat_id": tg_chat_id,
                    "text": msg,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": True
                }
                resp = requests.post(tg_url, json=payload, timeout=10)
                if resp.status_code == 200:
                    logger.info("📱 Telegram push notification delivered successfully!")
                else:
                    logger.warning(f"Telegram notification returned status {resp.status_code}")
            except Exception as e:
                logger.warning(f"Could not send Telegram notification: {e}")

    # Build structured workouts with progression levels and archetype rotation
    current_levels = eval_result.updated_progression_levels
    recent_used = state.get("used_archetypes", [])

    builder = WorkoutBuilder(ftp_watts=effective_ftp)
    weekly_schedule = builder.build_weekly_schedule(
        week=effective_week,
        training_days=normalized_days,
        weekday_duration=weekday_dur,
        friday_duration=friday_dur,
        progression_levels=current_levels,
        used_archetypes=recent_used
    )

    created_events: List[Dict[str, Any]] = []
    day_to_offset = {"MON": 0, "TUE": 1, "WED": 2, "THU": 3, "FRI": 4, "SAT": 5, "SUN": 6}
    newly_used_archetypes = list(recent_used)

    for day_code, workout_spec in weekly_schedule:
        offset = day_to_offset.get(day_code, 0)
        session_date = next_monday + timedelta(days=offset)
        session_iso = session_date.strftime("%Y-%m-%dT07:00:00")

        logger.info(
            f"Scheduling {workout_spec.title} for {day_code} ({session_date.strftime('%Y-%m-%d')}) "
            f"[{workout_spec.target_duration_minutes} min, Est TSS: {workout_spec.estimated_tss}]"
        )

        if workout_spec.archetype_id not in newly_used_archetypes:
            newly_used_archetypes.append(workout_spec.archetype_id)

        if not args.dry_run:
            ev = client.create_workout_event(
                date_iso=session_iso,
                name=workout_spec.title,
                description=workout_spec.description,
                indoor=True,
                load_tss=workout_spec.estimated_tss
            )
            if ev:
                created_events.append(ev)

    # Keep only last 15 archetypes in history to allow natural cyclic rotation
    if len(newly_used_archetypes) > 15:
        newly_used_archetypes = newly_used_archetypes[-15:]

    # Update State
    state["current_ftp"] = effective_ftp
    state["mesocycle_week"] = effective_week
    state["preferred_days"] = normalized_days
    state["weekday_duration"] = weekday_dur
    state["friday_duration"] = friday_dur
    state["progression_levels"] = current_levels
    state["used_archetypes"] = newly_used_archetypes
    state["last_evaluation_date"] = today.strftime("%Y-%m-%dT%H:%M:%SZ")
    state["last_scheduled_week_start"] = window_start_str
    if eval_result.ftp_increased and effective_week == 1:
        state["total_blocks_completed"] = state.get("total_blocks_completed", 0) + 1

    history_entry = {
        "evaluated_at": today.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "evaluated_week": eval_result.current_week,
        "scheduled_next_week": effective_week,
        "previous_ftp": eval_result.current_ftp,
        "current_ftp": effective_ftp,
        "ftp_increased": eval_result.ftp_increased,
        "decision": eval_result.advancement_decision,
        "compliance": eval_result.average_compliance,
        "efficiency_factor": eval_result.average_efficiency_factor,
        "decoupling_pct": eval_result.average_decoupling,
        "evaluated_sessions": eval_result.evaluated_sessions_count,
        "scheduled_sessions_count": len(weekly_schedule),
        "training_days": normalized_days,
        "progression_levels": current_levels,
        "summary": eval_result.summary_message
    }
    state.setdefault("history", []).append(history_entry)

    save_json_file(args.state_file, state)

    # Generate Markdown Summary for GitHub Actions and mobile viewing
    summary_md = f"""# 🚴 WorldTour Indoor Training Report
**Settimana Programmata:** {window_start_str} -> {window_end_str}  
**Stato Mesociclo:** Settimana **{effective_week}** di 4 (Ciclo 3:1)  
**FTP Attuale:** **{effective_ftp} Watt** {'🚀 *(Auto-Incremento +2%!)*' if eval_result.ftp_increased else ''}  
**Livelli WorldTour:** VO2max `{current_levels.get('vo2max', 1.0):.1f}` | SweetSpot `{current_levels.get('sweet_spot', 1.0):.1f}` | Soglia `{current_levels.get('threshold', 1.0):.1f}`  
**Rullo Target:** Elite Suito (Modalità ERG con protezione anti-spiral)  
**Sincronizzazione:** Intervals.icu ➡️ MyWhoosh (Tablet Android) & Garmin Edge 850  

---

### 📊 Valutazione Sessioni Precedenti
- **Attività Analizzate:** {eval_result.evaluated_sessions_count}
- **Compliance Media:** {eval_result.average_compliance * 100:.1f}%
- **Decoupling Aerobico (Pw:Hr):** {eval_result.average_decoupling:.1f}%
- **Efficiency Factor (EF):** {eval_result.average_efficiency_factor:.2f}
- **Decisione Tecnico-Sportiva:** `{eval_result.advancement_decision}`
- **Nota del Coach:** {eval_result.summary_message}

---

### 🗓️ Programma Settimana Entrante ({', '.join(normalized_days)})
| Giorno | Sessione | Durata | Est. TSS | IF | Target Principale |
| :--- | :--- | :---: | :---: | :---: | :--- |
"""
    for day_code, spec in weekly_schedule:
        summary_md += f"| **{day_code}** | {spec.title} | **{spec.target_duration_minutes} min** | {spec.estimated_tss} | {spec.intensity_factor:.2f} | {spec.session_code} |\n"

    summary_md += """
---
> 💡 **Nota Ergomeccanica Elite Suito:**
> - Nei tratti ad alta intensità (>110% FTP), mantieni una cadenza fluida (95-105 RPM) prima dell'innesco dell'intervallo per prevenire il blocco del freno magnetico (Anti-Spiral-of-Death).
> - Riscaldamento rapido di 7.5 min con 3 accelerazioni a 105% per calibrare il freno.
"""

    logger.info("\n" + summary_md)
    write_github_step_summary(summary_md)
    send_telegram_notification(summary_md)
    logger.info("✅ Training Orchestration Completed Successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
