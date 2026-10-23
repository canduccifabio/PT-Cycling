"""Comprehensive Unit Tests for PT Cycling WorldTour Serverless Engine."""

from datetime import datetime
import os
import sys
import pytest

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from intervals_client import IntervalsClient, MANAGED_TAG
from performance_analyzer import PerformanceAnalyzer, SessionEvaluation
from workout_archetypes import WorldTourWorkoutArchetypes
from workout_builder import WorkoutBuilder


class TestWorkoutBuilder:
    """Tests for workout generation, durations, and Elite Suito ERG optimizations."""

    def test_duration_bounds_enforced(self):
        builder = WorkoutBuilder(ftp_watts=205)

        # Below 42m must clamp to 42m
        w_short = builder.build_ronnestad_30_15(level=1.0, duration_min=30)
        assert w_short.target_duration_minutes == 42

        # Above 60m must clamp to 60m
        w_long = builder.build_criss_cross_sst(level=2.0, duration_min=90)
        assert w_long.target_duration_minutes == 60

        # Exact durations within [42, 60] are preserved
        for d in [42, 45, 50, 55, 60]:
            w = builder.build_float_sets_thr(level=1.5, duration_min=d)
            assert w.target_duration_minutes == d

    def test_elite_suito_erg_biomechanics(self):
        builder = WorkoutBuilder(ftp_watts=205)

        vo2 = builder.build_ronnestad_30_15(level=1.0, duration_min=45)
        sst = builder.build_criss_cross_sst(level=1.0, duration_min=50)
        thr = builder.build_float_sets_thr(level=1.0, duration_min=60)
        delo = builder.build_neuromuscular_openers_deload(level=1.0, duration_min=42)

        for w in [vo2, sst, thr, delo]:
            desc = w.description
            # 1. Warm-up reactive bursts present (Elite Suito brake activation)
            assert "105% 100-105rpm" in desc
            assert "3x" in desc
            # 2. Cool-down ramp present
            assert "ramp 55-40%" in desc
            # 3. Formatted for Intervals.icu
            assert "- " in desc

        # Anti-spiral cue present in high intensity workouts
        assert "Anti-Spiral" in vo2.description or "cadenza a 95-100 RPM" in vo2.description
        assert "cadenza" in thr.description

    def test_wattage_calculation_from_ftp(self):
        builder = WorkoutBuilder(ftp_watts=205)
        # 105% of 205 = 215.25 -> 215W
        assert builder._watts(105) == 215
        # 90% of 205 = 184.5 -> 184 or 185W
        assert builder._watts(90) in [184, 185]
        # 50% of 205 = 102.5 -> 102 or 103W
        assert builder._watts(50) in [102, 103]

    def test_worldtour_dynamic_rotation_and_freshness(self):
        """Verifies that the builder rotates archetypes and produces different workouts."""
        builder = WorkoutBuilder(ftp_watts=205)
        days = ["MON", "WED", "FRI"]

        # Run 1
        schedule_1 = builder.build_weekly_schedule(
            week=1,
            training_days=days,
            weekday_duration=50,
            friday_duration=60,
            used_archetypes=[]
        )
        assert len(schedule_1) == 3
        used_first = [w[1].archetype_id for w in schedule_1]

        # Run 2 with previous used archetypes passed
        schedule_2 = builder.build_weekly_schedule(
            week=2,
            training_days=days,
            weekday_duration=50,
            friday_duration=60,
            used_archetypes=used_first
        )
        used_second = [w[1].archetype_id for w in schedule_2]

        # Ensure that at least for VO2max and Sweet Spot, the archetype rotated
        assert used_second[0] != used_first[0] or used_second[1] != used_first[1]


class TestPerformanceAnalyzer:
    """Tests for compliance metrics, cardiovascular decoupling, and 3:1 mesocycle state machine."""

    def test_analyze_completed_activities_matching(self):
        analyzer = PerformanceAnalyzer()

        activities = [
            {
                "id": "12345",
                "start_date_local": "2026-10-19T08:00:00Z",
                "name": "MyWhoosh - W1D1 VO2max",
                "icu_training_load": 60,
                "moving_time": 3000,  # 50 min
                "icu_weighted_avg_watts": 190,
                "average_heartrate": 142,
                "icu_efficiency_factor": 1.34,
                "icu_aerobic_decoupling": 2.1,
                "paired_event_id": "999"
            }
        ]

        planned_events = [
            {
                "id": "999",
                "start_date_local": "2026-10-19T07:00:00Z",
                "name": f"W1D1 - VO2max Micro-bursts [50m] {MANAGED_TAG}",
                "icu_training_load": 62,
                "icu_duration": 3000
            }
        ]

        evals = analyzer.analyze_completed_activities(activities, planned_events)
        assert len(evals) == 1
        ev = evals[0]
        assert ev.activity_id == "12345"
        assert ev.compliance_score >= 0.90
        assert ev.efficiency_factor == 1.34
        assert ev.decoupling_pct == 2.1
        assert ev.completed is True

    def test_advancement_from_week_1_to_2_with_level_up(self):
        analyzer = PerformanceAnalyzer(min_compliance_to_advance=0.85)
        current_state = {
            "current_ftp": 205,
            "mesocycle_week": 1,
            "progression_levels": {"vo2max": 1.0, "sweet_spot": 1.0, "threshold": 1.0}
        }

        successful_evals = [
            SessionEvaluation(
                date="2026-10-19",
                activity_id="1",
                activity_name="S1",
                planned_tss=60,
                actual_tss=59,
                planned_duration_min=50,
                actual_duration_min=50,
                compliance_score=0.98,
                normalized_power=195,
                average_hr=145,
                efficiency_factor=1.34,
                decoupling_pct=2.5,
                completed=True
            ),
            SessionEvaluation(
                date="2026-10-21",
                activity_id="2",
                activity_name="S2",
                planned_tss=65,
                actual_tss=64,
                planned_duration_min=50,
                actual_duration_min=50,
                compliance_score=0.97,
                normalized_power=190,
                average_hr=140,
                efficiency_factor=1.35,
                decoupling_pct=3.1,
                completed=True
            )
        ]

        result = analyzer.evaluate_progression(current_state, successful_evals)
        assert result.next_week == 2
        assert result.next_ftp == 205
        assert result.ftp_increased is False
        assert "ADVANCE_TO_WEEK_2" in result.advancement_decision
        # Progression levels incremented!
        assert result.updated_progression_levels["vo2max"] > 1.0
        assert result.updated_progression_levels["sweet_spot"] > 1.0

    def test_auto_adaptive_ftp_increase_end_of_block(self):
        """At end of Week 4 (deload), if block success is high, auto-increase FTP by +2%."""
        analyzer = PerformanceAnalyzer(
            min_compliance_to_advance=0.85,
            max_decoupling_pct=6.5,
            auto_ftp_increase_pct=0.02
        )
        current_state = {
            "current_ftp": 205,
            "mesocycle_week": 4,
            "progression_levels": {"vo2max": 2.2, "sweet_spot": 2.2, "threshold": 2.2}
        }

        evals_week_4 = [
            SessionEvaluation(
                date="2026-10-26",
                activity_id="10",
                activity_name="W4D1 Deload",
                planned_tss=38,
                actual_tss=38,
                planned_duration_min=42,
                actual_duration_min=42,
                compliance_score=1.0,
                normalized_power=145,
                average_hr=122,
                efficiency_factor=1.19,
                decoupling_pct=1.8,
                completed=True
            )
        ]

        result = analyzer.evaluate_progression(current_state, evals_week_4)
        assert result.ftp_increased is True
        # 205 * 1.02 = 209.1 -> +4W minimum step -> 209W
        assert result.next_ftp == 209
        assert result.next_week == 1  # Reset to week 1 of new mesocycle
        assert result.advancement_decision == "AUTO_FTP_INCREASE"
        assert "PROGRESSIONE COMPLETATA" in result.summary_message
        # Levels reset to 1.0 for new higher FTP baseline
        assert result.updated_progression_levels["vo2max"] == 1.0

    def test_manual_override_ftp(self):
        analyzer = PerformanceAnalyzer()
        current_state = {"current_ftp": 205, "mesocycle_week": 2}

        result = analyzer.evaluate_progression(
            current_state=current_state,
            recent_evaluations=[],
            override_ftp=215
        )
        assert result.next_ftp == 215
        assert result.advancement_decision == "MANUAL_OVERRIDE"
        assert result.ftp_increased is True


class TestIntervalsClient:
    """Tests for intervals client header generation and managed tag."""

    def test_headers_and_auth(self):
        client = IntervalsClient(athlete_id="i12345", api_key="secret_token_abc")
        assert client.is_configured() is True
        auth_header = client.session.headers.get("Authorization", "")
        assert auth_header.startswith("Basic ")

    def test_unconfigured_dry_run_safety(self):
        client = IntervalsClient(athlete_id="", api_key="")
        assert client.is_configured() is False
        assert client.get_activities("2026-10-01", "2026-10-07") == []
        assert client.cleanup_managed_events("2026-10-01", "2026-10-07") == 0
        workout = client.create_workout_event("2026-10-26T07:00:00", "Test Ride", "- 10m 50%")
        assert workout is not None
        assert workout["name"].startswith("Test Ride")
