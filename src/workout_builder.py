"""Workout Builder for Indoor Cycling (Elite Suito ERG Optimized).

Generates structured workouts formatted using official Intervals.icu textual syntax.
Every workout is strictly calibrated between 42 and 60 minutes, adapts to the 3:1
mesocycle progression, and respects the biomechanical characteristics of the
Elite Suito direct-drive magnetic smart trainer in ERG mode:
1. Compact & reactive 7.5-min warm-up (progressive ramp + 3x 15s bursts @ 105% to warm magnetic coil)
2. Anti-spiral-of-death transitions with high-cadence alerts (95-105 RPM) before high-power steps
3. Accurate cool-down ramp (55% -> 40%) guaranteeing exact target duration to the second
"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class WorkoutSpec:
    title: str
    session_code: str
    week: int
    target_duration_minutes: int
    ftp_watts: int
    estimated_tss: int
    intensity_factor: float
    description: str


class WorkoutBuilder:
    """Builder for Elite Suito ERG structured workouts."""

    def __init__(self, ftp_watts: int = 205):
        self.ftp_watts = max(100, int(ftp_watts))

    def _watts(self, pct: float) -> int:
        """Calculate absolute Watts for a given percentage of FTP."""
        return round(self.ftp_watts * (pct / 100.0))

    def _clamp_duration(self, duration_min: int) -> int:
        """Enforce strict 42 to 60 minute duration bounds."""
        return max(42, min(60, int(duration_min)))

    def _format_time_sec(self, seconds: int) -> str:
        """Format seconds into intervals.icu syntax (e.g. 90s, 4m, 4m30s)."""
        seconds = int(seconds)
        if seconds < 60:
            return f"{seconds}s"
        m = seconds // 60
        s = seconds % 60
        if s == 0:
            return f"{m}m"
        return f"{m}m{s}s"

    def _generate_warmup(self) -> Tuple[List[str], int]:
        """Generate 7.5 min (450s) reactive warm-up optimized for Elite Suito ERG.

        - 3m30s progressive ramp 50-65% (85-90 rpm)
        - 2m00s ramp 65-75% (90-95 rpm)
        - 30s easy spin 55% (85 rpm)
        - 3x [15s @ 105% (100-105 rpm) / 15s @ 50% (85 rpm)]
          (Calibrates Suito magnetic brake and primes neuromuscular pathways)
        """
        lines = [
            "Warmup - Reattivo Elite Suito ERG",
            f"- 3m30s ramp 50-65% 85-90rpm Riscaldamento graduale ({self._watts(50)}-{self._watts(65)}W)",
            f"- 2m ramp 65-75% 90-95rpm Incremento cadenza ({self._watts(65)}-{self._watts(75)}W)",
            f"- 30s 55% 85rpm Spin agile ({self._watts(55)}W)",
            "Attivazione freno Suito (anti-blocco coppia)",
            "3x",
            f"- 15s 105% 100-105rpm Scatto controllato ({self._watts(105)}W)",
            f"- 15s 50% 85rpm Recupero attivo ({self._watts(50)}W)",
            f"- 30s 55% 85rpm Transizione finale ({self._watts(55)}W)"
        ]
        duration_sec = 210 + 120 + 30 + (3 * 30) + 30  # 480 seconds = 8 minutes
        return lines, duration_sec

    def _generate_cooldown(self, remaining_sec: int) -> Tuple[List[str], int]:
        """Generate cool-down ramp matching remaining seconds to exact target budget."""
        cooldown_sec = max(180, remaining_sec)
        time_str = self._format_time_sec(cooldown_sec)
        lines = [
            "Defaticamento e Ritorno alla Calma",
            f"- {time_str} ramp 55-40% 85-90rpm Defaticamento progressivo ({self._watts(55)}-{self._watts(40)}W)"
        ]
        return lines, cooldown_sec

    # --------------------------------------------------------------------------
    # SESSION 1: VO2MAX & MICRO-BURSTS (Monday)
    # --------------------------------------------------------------------------
    def build_vo2max_session(self, week: int, duration_min: int = 45) -> WorkoutSpec:
        duration_min = self._clamp_duration(duration_min)
        total_target_sec = duration_min * 60
        warmup_lines, warmup_sec = self._generate_warmup()

        main_lines: List[str] = []
        main_sec = 0

        # Spiral of death prevention banner
        spiral_alert = (
            "Aumenta la cadenza a 95-100 RPM prima dello step! "
            "(Anti-Spiral-of-Death Suito ERG)"
        )

        if week == 1:
            # Base VO2: 2 sets of 8x (30s @ 115% / 30s @ 50%), 3.5m recovery between
            w_pct = 115
            main_lines.append(spiral_alert)
            main_lines.append("Set 1 - Micro-intervalli VO2max 30/30")
            main_lines.append("8x")
            main_lines.append(f"- 30s {w_pct}% 100-105rpm VO2 ({self._watts(w_pct)}W)")
            main_lines.append(f"- 30s 50% 85rpm Rec ({self._watts(50)}W)")
            main_lines.append(f"- 3m30s 55% 85rpm Recupero tra le serie ({self._watts(55)}W)")
            main_lines.append(spiral_alert)
            main_lines.append("Set 2 - Micro-intervalli VO2max 30/30")
            main_lines.append("8x")
            main_lines.append(f"- 30s {w_pct}% 100-105rpm VO2 ({self._watts(w_pct)}W)")
            main_lines.append(f"- 30s 50% 85rpm Rec ({self._watts(50)}W)")
            main_sec = (8 * 60) + 210 + (8 * 60)  # 480 + 210 + 480 = 1170s (19.5 min)
            if_est = 0.84

        elif week == 2:
            # Density (+15% TiZ / reduced recovery): 2 sets of 9x (35s @ 118% / 25s @ 50%)
            w_pct = 118
            main_lines.append(spiral_alert)
            main_lines.append("Set 1 - Micro-intervalli Densita 35/25")
            main_lines.append("9x")
            main_lines.append(f"- 35s {w_pct}% 100-105rpm VO2 Densità ({self._watts(w_pct)}W)")
            main_lines.append(f"- 25s 50% 85rpm Rec ({self._watts(50)}W)")
            main_lines.append(f"- 3m 55% 85rpm Recupero tra le serie ({self._watts(55)}W)")
            main_lines.append(spiral_alert)
            main_lines.append("Set 2 - Micro-intervalli Densita 35/25")
            main_lines.append("9x")
            main_lines.append(f"- 35s {w_pct}% 100-105rpm VO2 Densità ({self._watts(w_pct)}W)")
            main_lines.append(f"- 25s 50% 85rpm Rec ({self._watts(50)}W)")
            main_sec = (9 * 60) + 180 + (9 * 60)  # 540 + 180 + 540 = 1260s (21 min)
            if_est = 0.87

        elif week == 3:
            # Peak: 2 sets of 10x (40s @ 120% / 20s @ 50%), high density
            w_pct = 120
            main_lines.append(spiral_alert)
            main_lines.append("Set 1 - Picco VO2max 40/20 High Density")
            main_lines.append("10x")
            main_lines.append(f"- 40s {w_pct}% 102-108rpm Picco VO2 ({self._watts(w_pct)}W)")
            main_lines.append(f"- 20s 50% 85rpm Rec Breve ({self._watts(50)}W)")
            main_lines.append(f"- 3m30s 55% 85rpm Recupero tra le serie ({self._watts(55)}W)")
            main_lines.append(spiral_alert)
            main_lines.append("Set 2 - Picco VO2max 40/20 High Density")
            main_lines.append("10x")
            main_lines.append(f"- 40s {w_pct}% 102-108rpm Picco VO2 ({self._watts(w_pct)}W)")
            main_lines.append(f"- 20s 50% 85rpm Rec Breve ({self._watts(50)}W)")
            main_sec = (10 * 60) + 210 + (10 * 60)  # 600 + 210 + 600 = 1410s (23.5 min)
            if_est = 0.90

        else:
            # Week 4: Deload & Neuromuscular Openers (42-45 min total)
            main_lines.append("Fase Rigenerativa & Openers Neuromuscolari")
            main_lines.append(f"- 10m 60% 90rpm Aerobico Z2 Recupero ({self._watts(60)}W)")
            main_lines.append(spiral_alert)
            main_lines.append("4x")
            main_lines.append(f"- 15s 115% 105-110rpm Sprint Agilita ({self._watts(115)}W)")
            main_lines.append(f"- 1m45s 50% 85rpm Recupero fluido ({self._watts(50)}W)")
            main_sec = 600 + (4 * 120)  # 600 + 480 = 1080s (18 min)
            if_est = 0.68

        # Calculate time budget for aerobic buffer and cooldown
        elapsed_sec = warmup_sec + main_sec
        remaining_sec = total_target_sec - elapsed_sec

        inter_lines: List[str] = []
        if remaining_sec > 300:  # If more than 5 min remains, insert an endurance spin block
            aerobic_filler_sec = remaining_sec - 240
            inter_lines.append(
                f"- {self._format_time_sec(aerobic_filler_sec)} 62% 90rpm Fondo Aerobico Z2 ({self._watts(62)}W)"
            )
            cooldown_sec = 240
        else:
            cooldown_sec = max(180, remaining_sec)

        cooldown_lines, _ = self._generate_cooldown(cooldown_sec)

        description_lines = [
            f"# W{week}D1 - VO2max Micro-bursts ({duration_min} min)",
            f"Obiettivo: Stimolo cardiorespiratorio e densità neuromuscolare (FTP: {self.ftp_watts}W).",
            "Ottimizzato per Elite Suito ERG: cadenza agile per evitare stallo freno.",
            "",
            *warmup_lines,
            "",
            *main_lines,
            "",
            *(inter_lines if inter_lines else []),
            "",
            *cooldown_lines
        ]

        description = "\n".join(description_lines)
        est_tss = int((duration_min / 60.0) * (if_est ** 2) * 100)

        return WorkoutSpec(
            title=f"W{week}D1 - VO2max Micro-bursts [{duration_min}m]",
            session_code="S1_VO2MAX",
            week=week,
            target_duration_minutes=duration_min,
            ftp_watts=self.ftp_watts,
            estimated_tss=est_tss,
            intensity_factor=if_est,
            description=description
        )

    # --------------------------------------------------------------------------
    # SESSION 2: SWEET SPOT (Wednesday)
    # --------------------------------------------------------------------------
    def build_sweet_spot_session(self, week: int, duration_min: int = 50) -> WorkoutSpec:
        duration_min = self._clamp_duration(duration_min)
        total_target_sec = duration_min * 60
        warmup_lines, warmup_sec = self._generate_warmup()

        main_lines: List[str] = []
        main_sec = 0

        if week == 1:
            # Base Sweet Spot: 3x 8 min @ 90% FTP (rec. 2.5 min @ 55%) = 24 min TiZ
            main_lines.append("Blocco Sweet Spot (3x 8 min @ 90% FTP)")
            main_lines.append("3x")
            main_lines.append(f"- 8m 90% 90-92rpm Sweet Spot ({self._watts(90)}W)")
            main_lines.append(f"- 2m30s 55% 85rpm Recupero attivo ({self._watts(55)}W)")
            main_sec = 3 * (480 + 150)  # 3 * 630 = 1890s (31.5 min)
            if_est = 0.83

        elif week == 2:
            # Density (+15% TiZ): 3x 9.5 min @ 91% FTP (rec. 2m15s @ 55%) = 28.5 min TiZ
            main_lines.append("Blocco Sweet Spot Densità (3x 9m30s @ 91% FTP)")
            main_lines.append("3x")
            main_lines.append(f"- 9m30s 91% 90-92rpm Sweet Spot Alta Densità ({self._watts(91)}W)")
            main_lines.append(f"- 2m15s 55% 85rpm Recupero compatto ({self._watts(55)}W)")
            main_sec = 3 * (570 + 135)  # 3 * 705 = 2115s (35.25 min)
            if_est = 0.85

        elif week == 3:
            # Peak: 2x 14 min or 3x 10 min @ 92% FTP (rec. 2m @ 55%) = 30 min TiZ
            main_lines.append("Blocco Sweet Spot Picco (3x 10 min @ 92% FTP)")
            main_lines.append("3x")
            main_lines.append(f"- 10m 92% 90-94rpm Sweet Spot Picco ({self._watts(92)}W)")
            main_lines.append(f"- 2m 55% 85rpm Recupero breve ({self._watts(55)}W)")
            main_sec = 3 * (600 + 120)  # 3 * 720 = 2160s (36 min)
            if_est = 0.87

        else:
            # Week 4: Deload & Tempo Activation (42-45 min total)
            main_lines.append("Scarico Attivo & Attivazione Muscolare")
            main_lines.append(f"- 8m 85% 90rpm Richiamo Tempo ({self._watts(85)}W)")
            main_lines.append(f"- 3m 55% 85rpm Recupero fluido ({self._watts(55)}W)")
            main_lines.append(f"- 6m 88% 90rpm Sweet Spot Leggero ({self._watts(88)}W)")
            main_sec = 480 + 180 + 360  # 1020s (17 min)
            if_est = 0.69

        elapsed_sec = warmup_sec + main_sec
        remaining_sec = total_target_sec - elapsed_sec

        inter_lines: List[str] = []
        if remaining_sec > 300:
            aerobic_filler_sec = remaining_sec - 240
            inter_lines.append(
                f"- {self._format_time_sec(aerobic_filler_sec)} 63% 90rpm Fondo Aerobico Z2 ({self._watts(63)}W)"
            )
            cooldown_sec = 240
        else:
            cooldown_sec = max(180, remaining_sec)

        cooldown_lines, _ = self._generate_cooldown(cooldown_sec)

        description_lines = [
            f"# W{week}D2 - Sweet Spot Aerobic Engine ({duration_min} min)",
            f"Obiettivo: Costruzione del motore aerobico e tolleranza al carico a 88-93% FTP ({self.ftp_watts}W).",
            "Elite Suito ERG: mantieni cadenza costante a 90-92 RPM per fluidità magnetica.",
            "",
            *warmup_lines,
            "",
            *main_lines,
            "",
            *(inter_lines if inter_lines else []),
            "",
            *cooldown_lines
        ]

        description = "\n".join(description_lines)
        est_tss = int((duration_min / 60.0) * (if_est ** 2) * 100)

        return WorkoutSpec(
            title=f"W{week}D2 - Sweet Spot Power [{duration_min}m]",
            session_code="S2_SWEETSPOT",
            week=week,
            target_duration_minutes=duration_min,
            ftp_watts=self.ftp_watts,
            estimated_tss=est_tss,
            intensity_factor=if_est,
            description=description
        )

    # --------------------------------------------------------------------------
    # SESSION 3: THRESHOLD & OVER-UNDER (Friday)
    # --------------------------------------------------------------------------
    def build_threshold_over_under_session(self, week: int, duration_min: int = 60) -> WorkoutSpec:
        duration_min = self._clamp_duration(duration_min)
        total_target_sec = duration_min * 60
        warmup_lines, warmup_sec = self._generate_warmup()

        main_lines: List[str] = []
        main_sec = 0

        anti_spiral_note = (
            "Aumenta la cadenza a 95-100 RPM prima dello step Over! "
            "(Anti-Spiral Suito)"
        )

        if week == 1:
            # Base Over-Under: 3x 8 min (4x [1m30s @ 92% / 30s @ 105%]), rec. 3m @ 55%
            main_lines.append("Blocco Over-Under Soglia 3x 8m (4x 1m30s Under / 30s Over)")
            for i in range(1, 4):
                main_lines.append(f"Serie {i} Over-Under")
                main_lines.append(anti_spiral_note)
                main_lines.append("4x")
                main_lines.append(f"- 1m30s 92% 90rpm Under ({self._watts(92)}W)")
                main_lines.append(f"- 30s 105% 98-102rpm Over ({self._watts(105)}W)")
                if i < 3:
                    main_lines.append(f"- 3m 55% 85rpm Recupero lattato ({self._watts(55)}W)")
            main_sec = (3 * 480) + (2 * 180)  # 1440 + 360 = 1800s (30 min)
            if_est = 0.86

        elif week == 2:
            # Density (+15% TiZ): 3x 9 min (3x [2m @ 94% / 1m @ 108%]), rec. 2.5m @ 55%
            main_lines.append("Blocco Over-Under Densità 3x 9m (3x 2m Under / 1m Over)")
            for i in range(1, 4):
                main_lines.append(f"Serie {i} Over-Under Densità")
                main_lines.append(anti_spiral_note)
                main_lines.append("3x")
                main_lines.append(f"- 2m 94% 90-92rpm Under Sostenuto ({self._watts(94)}W)")
                main_lines.append(f"- 1m 108% 98-104rpm Over Spinta ({self._watts(108)}W)")
                if i < 3:
                    main_lines.append(f"- 2m30s 55% 85rpm Recupero ({self._watts(55)}W)")
            main_sec = (3 * 540) + (2 * 150)  # 1620 + 300 = 1920s (32 min)
            if_est = 0.88

        elif week == 3:
            # Peak: 3x 10.5 min (3x [2m15s @ 95% / 1m15s @ 110%]), rec. 2.5m @ 55%
            main_lines.append("Blocco Over-Under Picco 3x 10m30s (3x 2m15s Under / 1m15s Over)")
            for i in range(1, 4):
                main_lines.append(f"Serie {i} Over-Under Picco Clearance")
                main_lines.append(anti_spiral_note)
                main_lines.append("3x")
                main_lines.append(f"- 2m15s 95% 92rpm Under Alta Soglia ({self._watts(95)}W)")
                main_lines.append(f"- 1m15s 110% 100-105rpm Over Clearance ({self._watts(110)}W)")
                if i < 3:
                    main_lines.append(f"- 2m30s 55% 85rpm Recupero ({self._watts(55)}W)")
            main_sec = (3 * 630) + (2 * 150)  # 1890 + 300 = 2190s (36.5 min)
            if_est = 0.91

        else:
            # Week 4: Deload & Threshold Touch (42-45 min total)
            main_lines.append("Scarico con Attivazione di Soglia Controllata")
            main_lines.append(f"- 3m 95% 90rpm Attivazione enzimatica ({self._watts(95)}W)")
            main_lines.append(f"- 3m 55% 85rpm Recupero ({self._watts(55)}W)")
            main_lines.append(anti_spiral_note)
            main_lines.append(f"- 3m 100% 92rpm Tocco di Soglia FTP ({self._watts(100)}W)")
            main_sec = 180 + 180 + 180  # 540s (9 min)
            if_est = 0.70

        elapsed_sec = warmup_sec + main_sec
        remaining_sec = total_target_sec - elapsed_sec

        inter_lines: List[str] = []
        if remaining_sec > 300:
            aerobic_filler_sec = remaining_sec - 240
            inter_lines.append(
                f"- {self._format_time_sec(aerobic_filler_sec)} 62% 90rpm Fondo Aerobico Z2 ({self._watts(62)}W)"
            )
            cooldown_sec = 240
        else:
            cooldown_sec = max(180, remaining_sec)

        cooldown_lines, _ = self._generate_cooldown(cooldown_sec)

        description_lines = [
            f"# W{week}D3 - Threshold Over-Under Clearance ({duration_min} min)",
            f"Obiettivo: Clearance del lattato e tolleranza all'acidosi (FTP: {self.ftp_watts}W).",
            "Elite Suito ERG: alza la cadenza a 98-102 RPM subito prima dell'Over per evitare stallo.",
            "",
            *warmup_lines,
            "",
            *main_lines,
            "",
            *(inter_lines if inter_lines else []),
            "",
            *cooldown_lines
        ]

        description = "\n".join(description_lines)
        est_tss = int((duration_min / 60.0) * (if_est ** 2) * 100)

        return WorkoutSpec(
            title=f"W{week}D3 - Threshold Over-Under [{duration_min}m]",
            session_code="S3_THRESHOLD_OU",
            week=week,
            target_duration_minutes=duration_min,
            ftp_watts=self.ftp_watts,
            estimated_tss=est_tss,
            intensity_factor=if_est,
            description=description
        )

    def build_weekly_schedule(
        self,
        week: int,
        training_days: List[str],
        weekday_duration: int = 50,
        friday_duration: int = 60
    ) -> List[Tuple[str, WorkoutSpec]]:
        """Map planned days of the week to structured workouts.

        Ensures that 3 days get appropriate workouts:
        - Day 1: VO2max Microbursts
        - Day 2: Sweet Spot
        - Day 3: Threshold Over-Under
        Any extra days fall back to Zone 2 Aerobic flush.
        """
        valid_days = [d.strip().upper() for d in training_days if d.strip()]
        if not valid_days:
            valid_days = ["MON", "WED", "FRI"]

        schedule: List[Tuple[str, WorkoutSpec]] = []
        builders = [
            lambda dur: self.build_vo2max_session(week, dur),
            lambda dur: self.build_sweet_spot_session(week, dur),
            lambda dur: self.build_threshold_over_under_session(week, dur),
        ]

        for idx, day in enumerate(valid_days):
            # Target duration: Friday / weekend gets standard/longer duration, weekdays get weekday_duration
            if day in ["FRI", "SAT", "SUN"]:
                duration = friday_duration
            else:
                duration = weekday_duration

            if idx < len(builders):
                spec = builders[idx](duration)
            else:
                # Extra day: Sweet Spot or aerobic recovery
                spec = self.build_sweet_spot_session(week, duration)
            schedule.append((day, spec))

        return schedule
