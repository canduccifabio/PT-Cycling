"""Performance Analyzer & Auto-Adaptive FTP Engine.

Evaluates indoor training sessions recorded via MyWhoosh / Garmin Edge 850:
1. Calculates compliance: compares planned vs actual TSS and duration.
2. Evaluates Efficiency Factor (EF = NP / Avg HR) and Aerobic Decoupling (Pw:Hr).
3. Drives the 3:1 Mesocycle State Machine:
   - Week 1: Base Time-in-Zone (TiZ)
   - Week 2: Density (+15% TiZ, reduced rest)
   - Week 3: Peak Density
   - Week 4: Deload & Neuromuscular Openers -> Auto-FTP evaluation:
     If block success >= 85% and cardiovascular drift is controlled,
     automatically increments FTP by +2% (e.g. 205W -> 209-210W).
"""

from dataclasses import asdict, dataclass
from datetime import datetime
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("pt_cycling.analyzer")


@dataclass
class SessionEvaluation:
    date: str
    activity_id: str
    activity_name: str
    planned_tss: float
    actual_tss: float
    planned_duration_min: float
    actual_duration_min: float
    compliance_score: float
    normalized_power: float
    average_hr: float
    efficiency_factor: float
    decoupling_pct: float
    completed: bool


@dataclass
class BlockEvaluationResult:
    current_ftp: int
    next_ftp: int
    current_week: int
    next_week: int
    ftp_increased: bool
    advancement_decision: str
    average_compliance: float
    average_efficiency_factor: float
    average_decoupling: float
    evaluated_sessions_count: int
    summary_message: str


class PerformanceAnalyzer:
    """Analyzes athlete telemetry and drives progressive overload."""

    def __init__(
        self,
        min_compliance_to_advance: float = 0.85,
        max_decoupling_pct: float = 6.5,
        auto_ftp_increase_pct: float = 0.02
    ):
        self.min_compliance = min_compliance_to_advance
        self.max_decoupling = max_decoupling_pct
        self.ftp_increase_pct = auto_ftp_increase_pct

    def analyze_completed_activities(
        self,
        activities: List[Dict[str, Any]],
        planned_events: List[Dict[str, Any]]
    ) -> List[SessionEvaluation]:
        """Match activities against planned workouts and calculate compliance metrics."""
        evaluations: List[SessionEvaluation] = []

        # Index planned events by ID and date
        events_by_id = {str(e.get("id")): e for e in planned_events if e.get("id")}
        events_by_date = {}
        for e in planned_events:
            date_str = (e.get("start_date_local") or "")[:10]
            if date_str:
                events_by_date[date_str] = e

        for act in activities:
            act_id = str(act.get("id", ""))
            act_date = (act.get("start_date_local") or "")[:10]
            act_name = act.get("name", "Indoor Ride")

            # Match planned event
            paired_id = str(act.get("paired_event_id") or "")
            matched_event = events_by_id.get(paired_id) or events_by_date.get(act_date)

            actual_tss = float(act.get("icu_training_load") or 0.0)
            actual_sec = float(act.get("moving_time") or act.get("elapsed_time") or 0.0)
            actual_min = round(actual_sec / 60.0, 1)

            np_watts = float(act.get("icu_weighted_avg_watts") or act.get("average_watts") or 0.0)
            avg_hr = float(act.get("average_heartrate") or 0.0)

            # Efficiency Factor: NP / HR
            ef = float(act.get("icu_efficiency_factor") or (np_watts / avg_hr if avg_hr > 0 else 0.0))

            # Decoupling (Pw:Hr)
            decoupling = act.get("icu_aerobic_decoupling")
            if decoupling is None:
                decoupling_val = 0.0
            else:
                try:
                    decoupling_val = float(decoupling)
                    # Intervals.icu may report decoupling as percentage (e.g. 3.5%) or ratio (0.035)
                    if 0 < abs(decoupling_val) < 1.0:
                        decoupling_val *= 100.0
                except (ValueError, TypeError):
                    decoupling_val = 0.0

            if matched_event:
                planned_tss = float(matched_event.get("icu_training_load") or 50.0)
                planned_min = float(matched_event.get("icu_duration") or (45.0 * 60)) / 60.0
            else:
                # Default baseline if no matched event
                planned_tss = actual_tss if actual_tss > 0 else 50.0
                planned_min = actual_min if actual_min > 0 else 45.0

            # Compliance calculation
            tss_ratio = min(1.2, actual_tss / planned_tss) if planned_tss > 0 else 1.0
            dur_ratio = min(1.2, actual_min / planned_min) if planned_min > 0 else 1.0
            compliance = round((tss_ratio * 0.6) + (dur_ratio * 0.4), 2)
            completed = compliance >= 0.70

            evaluations.append(
                SessionEvaluation(
                    date=act_date,
                    activity_id=act_id,
                    activity_name=act_name,
                    planned_tss=planned_tss,
                    actual_tss=actual_tss,
                    planned_duration_min=planned_min,
                    actual_duration_min=actual_min,
                    compliance_score=compliance,
                    normalized_power=round(np_watts, 1),
                    average_hr=round(avg_hr, 1),
                    efficiency_factor=round(ef, 2),
                    decoupling_pct=round(decoupling_val, 1),
                    completed=completed
                )
            )

        return evaluations

    def evaluate_progression(
        self,
        current_state: Dict[str, Any],
        recent_evaluations: List[SessionEvaluation],
        override_ftp: Optional[int] = None
    ) -> BlockEvaluationResult:
        """Evaluate progression based on 3:1 mesocycle state machine and recent sessions."""
        current_ftp = int(current_state.get("current_ftp", 205))
        current_week = int(current_state.get("mesocycle_week", 1))

        # Handle manual override first if provided
        if override_ftp and override_ftp > 50:
            logger.info(f"Manual FTP override provided: {override_ftp}W (was {current_ftp}W)")
            return BlockEvaluationResult(
                current_ftp=current_ftp,
                next_ftp=override_ftp,
                current_week=current_week,
                next_week=current_week,
                ftp_increased=(override_ftp > current_ftp),
                advancement_decision="MANUAL_OVERRIDE",
                average_compliance=1.0,
                average_efficiency_factor=0.0,
                average_decoupling=0.0,
                evaluated_sessions_count=len(recent_evaluations),
                summary_message=f"FTP aggiornato manualmente a {override_ftp}W."
            )

        # Baseline evaluation metrics
        if not recent_evaluations:
            logger.info("No completed activities recorded in the evaluation window. Advancing default week.")
            next_week = 1 if current_week >= 4 else current_week + 1
            return BlockEvaluationResult(
                current_ftp=current_ftp,
                next_ftp=current_ftp,
                current_week=current_week,
                next_week=next_week,
                ftp_increased=False,
                advancement_decision="NO_DATA_DEFAULT_ADVANCE",
                average_compliance=1.0,
                average_efficiency_factor=0.0,
                average_decoupling=0.0,
                evaluated_sessions_count=0,
                summary_message=f"Nessuna attività registrata; passaggio pianificato da Settimana {current_week} a {next_week}."
            )

        avg_compliance = sum(e.compliance_score for e in recent_evaluations) / len(recent_evaluations)
        valid_efs = [e.efficiency_factor for e in recent_evaluations if e.efficiency_factor > 0]
        avg_ef = (sum(valid_efs) / len(valid_efs)) if valid_efs else 0.0

        valid_decouplings = [e.decoupling_pct for e in recent_evaluations if e.decoupling_pct != 0]
        avg_decoupling = (sum(valid_decouplings) / len(valid_decouplings)) if valid_decouplings else 3.0

        success_count = sum(1 for e in recent_evaluations if e.completed)
        success_rate = success_count / len(recent_evaluations)

        logger.info(
            f"Evaluation Summary: Week {current_week}, Sessions: {len(recent_evaluations)}, "
            f"Success Rate: {success_rate:.0%}, Avg Compliance: {avg_compliance:.2f}, "
            f"Avg EF: {avg_ef:.2f}, Avg Decoupling: {avg_decoupling:.1f}%"
        )

        ftp_increased = False
        next_ftp = current_ftp

        # State Machine: Mesocycle 3:1 (Weeks 1-3 load, Week 4 deload + auto FTP assessment)
        if current_week in [1, 2]:
            if avg_compliance >= self.min_compliance and success_rate >= 0.70:
                next_week = current_week + 1
                decision = f"ADVANCE_TO_WEEK_{next_week}"
                msg = (
                    f"Ottimo completamento ({avg_compliance:.0%}) e tenuta cardiovascolare "
                    f"(Decoupling: {avg_decoupling:.1f}%). Avanzamento a Settimana {next_week}."
                )
            else:
                next_week = current_week
                decision = f"REPEAT_WEEK_{current_week}"
                msg = (
                    f"Completamento parziale ({avg_compliance:.0%}, {success_count}/{len(recent_evaluations)} completati). "
                    f"Consolidamento del carico: ripetizione Settimana {current_week}."
                )

        elif current_week == 3:
            # Week 3 peak always leads to Week 4 deload
            next_week = 4
            decision = "ADVANCE_TO_DELOAD_WEEK_4"
            msg = "Completato il blocco di picco ad alta densità. Settimana 4: Scarico attivo e test di recupero."

        elif current_week >= 4:
            # Week 4: Deload completed -> Evaluate entire 4-week mesocycle for Auto-Adaptive FTP increase
            if success_rate >= 0.85 and avg_decoupling <= self.max_decoupling:
                # Promote FTP: +2% (minimum +4 Watts)
                calculated_increase = round(current_ftp * self.ftp_increase_pct)
                step_watts = max(4, calculated_increase)
                next_ftp = current_ftp + step_watts
                ftp_increased = True
                next_week = 1
                decision = "AUTO_FTP_INCREASE"
                msg = (
                    f"🏆 PROGRESSIONE COMPLETATA CON SUCCESSO! "
                    f"Tasso di successo del blocco: {success_rate:.0%}, Decoupling medio: {avg_decoupling:.1f}%. "
                    f"Nuovo FTP calcolato: {next_ftp}W (+{step_watts}W, +{self.ftp_increase_pct*100:.1f}%). "
                    f"Inizio nuovo mesocycle 3:1 (Settimana 1 - Base)."
                )
            else:
                next_ftp = current_ftp
                ftp_increased = False
                next_week = 1
                decision = "MAINTAIN_FTP_RESET_CYCLE"
                msg = (
                    f"Blocco 3:1 terminato con tasso successo {success_rate:.0%} "
                    f"(decoupling: {avg_decoupling:.1f}%). FTP mantenuto invariato a {current_ftp}W per "
                    f"rafforzare la base aerobica nel prossimo mesociclo."
                )

        return BlockEvaluationResult(
            current_ftp=current_ftp,
            next_ftp=next_ftp,
            current_week=current_week,
            next_week=next_week,
            ftp_increased=ftp_increased,
            advancement_decision=decision,
            average_compliance=round(avg_compliance, 2),
            average_efficiency_factor=round(avg_ef, 2),
            average_decoupling=round(avg_decoupling, 1),
            evaluated_sessions_count=len(recent_evaluations),
            summary_message=msg
        )
