"""Workout Builder for Indoor Cycling (WorldTour Dynamic Engine & Elite Suito ERG).

Generates scientifically varied, non-repetitive structured workouts formatted in
official Intervals.icu textual syntax.
Every workout:
- Is strictly bounded between 42 and 60 minutes down to the second.
- Implements Elite Suito direct-drive ERG protections:
  1. 7.5-8m reactive warm-up with 3x 15s bursts @ 105% (calibrates magnetic brake & primes neuromuscular pathways)
  2. Anti-spiral-of-death cues ("Aumenta la cadenza a 95-100 RPM prima dello step!")
  3. Precise cool-down ramp (55% -> 40%)
- Rotates dynamically across diverse WorldTour archetypes based on progression levels (1.0 to 10.0),
  ensuring workouts are ALWAYS FRESH, varied, and progressively challenging.
"""

from dataclasses import dataclass
import random
from typing import Any, Dict, List, Optional, Tuple

from workout_archetypes import ArchetypeDefinition, WorldTourWorkoutArchetypes


@dataclass
class WorkoutSpec:
    title: str
    session_code: str
    archetype_id: str
    category: str
    progression_level: float
    target_duration_minutes: int
    ftp_watts: int
    estimated_tss: int
    intensity_factor: float
    description: str


class WorkoutBuilder:
    """WorldTour workout generator with dynamic archetype selection and Suito ERG optimizations."""

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
        """7.5-8 min (480s) reactive warm-up for Elite Suito ERG."""
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

    def _finalize_workout(
        self,
        title: str,
        session_code: str,
        archetype_id: str,
        category: str,
        level: float,
        duration_min: int,
        main_lines: List[str],
        main_sec: int,
        if_est: float,
        tactical_context: str
    ) -> WorkoutSpec:
        """Compose warm-up, main sets, aerobic bridge, and cool-down to exact target minutes."""
        total_target_sec = duration_min * 60
        warmup_lines, warmup_sec = self._generate_warmup()

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
            f"# {title}",
            f"Livello Preparazione WorldTour: {level:.1f} • FTP Target: {self.ftp_watts}W",
            f"Contesto Tattico: {tactical_context}",
            "Ottimizzato per Elite Suito ERG: prevenzione spiral-of-death e controllo cadenza.",
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
            title=title,
            session_code=session_code,
            archetype_id=archetype_id,
            category=category,
            progression_level=level,
            target_duration_minutes=duration_min,
            ftp_watts=self.ftp_watts,
            estimated_tss=est_tss,
            intensity_factor=if_est,
            description=description
        )

    # --------------------------------------------------------------------------
    # VO2MAX ARCHETYPES
    # --------------------------------------------------------------------------
    def build_ronnestad_30_15(self, level: float, duration_min: int) -> WorkoutSpec:
        """Rønnestad 30/15 micro-bursts (high ventilation and stroke volume)."""
        duration_min = self._clamp_duration(duration_min)
        num_sets = 2 if duration_min <= 45 else 3
        reps_per_set = 8 if level < 3.0 else (9 if level < 6.0 else 10)
        power_pct = 118 if level < 4.0 else 120

        main_lines = [
            "Aumenta la cadenza a 95-100 RPM prima dello step! (Anti-Spiral Suito)"
        ]
        main_sec = 0
        for s in range(1, num_sets + 1):
            main_lines.append(f"Serie {s} - Micro-intervalli Rønnestad 30/15")
            main_lines.append(f"{reps_per_set}x")
            main_lines.append(f"- 30s {power_pct}% 100-105rpm VO2 Bursts ({self._watts(power_pct)}W)")
            main_lines.append(f"- 15s 50% 85rpm Recupero attivo ({self._watts(50)}W)")
            set_dur = reps_per_set * 45
            main_sec += set_dur
            if s < num_sets:
                rec_sec = 180
                main_lines.append(f"- 3m 55% 85rpm Recupero tra le serie ({self._watts(55)}W)")
                main_sec += rec_sec

        return self._finalize_workout(
            title=f"WT-VO2 #{level:.1f}: Rønnestad 30/15 [{duration_min}m]",
            session_code="VO2_RONNESTAD",
            archetype_id="VO2_RONNESTAD_30_15",
            category="VO2MAX",
            level=level,
            duration_min=duration_min,
            main_lines=main_lines,
            main_sec=main_sec,
            if_est=0.88,
            tactical_context="Simulazione attacchi ripetuti all'imbocco di uno strappo in salita."
        )

    def build_hard_start_plateau(self, level: float, duration_min: int) -> WorkoutSpec:
        """Hard-Start VO2: 30s @ 125-130% into 2m30s plateau @ 110-112%."""
        duration_min = self._clamp_duration(duration_min)
        reps = 3 if duration_min <= 48 else 4
        burst_pct = 125 if level < 4.0 else 130
        plateau_pct = 110 if level < 4.0 else 112

        main_lines = [
            "Aumenta la cadenza a 95-100 RPM prima dello step! (Anti-Spiral Suito)",
            "Blocco Hard-Start: scatto iniziale per forzare i cinetismi O2, poi stabilizzazione"
        ]
        main_sec = 0
        for i in range(1, reps + 1):
            main_lines.append(f"Ripetuta {i} Hard-Start VO2max")
            main_lines.append(f"- 30s {burst_pct}% 105rpm Hard-Start Burst ({self._watts(burst_pct)}W)")
            main_lines.append(f"- 2m30s {plateau_pct}% 96-100rpm Plateau VO2max ({self._watts(plateau_pct)}W)")
            main_sec += 180  # 3 min work
            if i < reps:
                main_lines.append(f"- 3m 50% 85rpm Recupero ({self._watts(50)}W)")
                main_sec += 180

        return self._finalize_workout(
            title=f"WT-VO2 #{level:.1f}: Hard-Start Fast Kinetics [{duration_min}m]",
            session_code="VO2_HARD_START",
            archetype_id="VO2_HARD_START_PLATEAU",
            category="VO2MAX",
            level=level,
            duration_min=duration_min,
            main_lines=main_lines,
            main_sec=main_sec,
            if_est=0.89,
            tactical_context="Simula un attacco deciso per staccare il gruppo e tenere la velocità in fuga."
        )

    def build_descending_ladder(self, level: float, duration_min: int) -> WorkoutSpec:
        """Descending VO2 ladder: 4m (108%) -> 3m (112%) -> 2m (118%) -> 1m (125%)."""
        duration_min = self._clamp_duration(duration_min)
        main_lines = [
            "Aumenta la cadenza a 95-100 RPM prima dello step! (Anti-Spiral Suito)",
            "Scala Discendente: durata decrescente e potenza crescente",
            f"- 4m 108% 95-98rpm Passo VO2 Sostenuto ({self._watts(108)}W)",
            f"- 2m30s 50% 85rpm Recupero ({self._watts(50)}W)",
            f"- 3m 112% 98-100rpm VO2 Solido ({self._watts(112)}W)",
            f"- 2m30s 50% 85rpm Recupero ({self._watts(50)}W)",
            f"- 2m 118% 100-102rpm Alta Intensità ({self._watts(118)}W)",
            f"- 2m 50% 85rpm Recupero ({self._watts(50)}W)",
            f"- 1m 125% 105rpm Finale Massimale ({self._watts(125)}W)"
        ]
        main_sec = 240 + 150 + 180 + 150 + 120 + 120 + 60  # 1020s = 17 min work/rec
        return self._finalize_workout(
            title=f"WT-VO2 #{level:.1f}: Piramide Discendente O2 [{duration_min}m]",
            session_code="VO2_LADDER",
            archetype_id="VO2_DESCENDING_LADDER",
            category="VO2MAX",
            level=level,
            duration_min=duration_min,
            main_lines=main_lines,
            main_sec=main_sec,
            if_est=0.87,
            tactical_context="Gestione progressiva del debito d'ossigeno nei finali di corsa."
        )

    def build_tabata_clusters(self, level: float, duration_min: int) -> WorkoutSpec:
        """Tabata clusters 40/20 and 30/30."""
        duration_min = self._clamp_duration(duration_min)
        num_clusters = 2 if duration_min <= 50 else 3
        reps = 7 if level < 4.0 else 8
        main_lines = [
            "Aumenta la cadenza a 95-100 RPM prima dello step! (Anti-Spiral Suito)"
        ]
        main_sec = 0
        for c in range(1, num_clusters + 1):
            main_lines.append(f"Cluster {c} - Micro-bursts 40/20")
            main_lines.append(f"{reps}x")
            main_lines.append(f"- 40s 116% 102-105rpm VO2 Burst ({self._watts(116)}W)")
            main_lines.append(f"- 20s 50% 85rpm Rec Breve ({self._watts(50)}W)")
            main_sec += reps * 60
            if c < num_clusters:
                main_lines.append(f"- 3m 55% 85rpm Recupero tra cluster ({self._watts(55)}W)")
                main_sec += 180

        return self._finalize_workout(
            title=f"WT-VO2 #{level:.1f}: Tabata Clusters 40/20 [{duration_min}m]",
            session_code="VO2_TABATA",
            archetype_id="VO2_TABATA_CLUSTERS",
            category="VO2MAX",
            level=level,
            duration_min=duration_min,
            main_lines=main_lines,
            main_sec=main_sec,
            if_est=0.89,
            tactical_context="Saturazione del debito di ossigeno con recuperi brevissimi."
        )

    def build_torque_stomp_burst(self, level: float, duration_min: int) -> WorkoutSpec:
        """Torque stomp (60 RPM) into VO2 plateau (100 RPM)."""
        duration_min = self._clamp_duration(duration_min)
        reps = 3 if duration_min <= 48 else 4
        main_lines = [
            "Aumenta la cadenza subito dopo lo stomp! (Anti-Spiral Suito)"
        ]
        main_sec = 0
        for i in range(1, reps + 1):
            main_lines.append(f"Ripetuta {i} Torque Stomp + VO2")
            main_lines.append(f"- 15s 130% 60rpm Stomp Bassa Cadenza ({self._watts(130)}W)")
            main_lines.append(f"- 2m15s 112% 100-104rpm Accelerazione e Passo ({self._watts(112)}W)")
            main_sec += 150  # 2.5 min work
            if i < reps:
                main_lines.append(f"- 2m45s 50% 85rpm Recupero attivo ({self._watts(50)}W)")
                main_sec += 165

        return self._finalize_workout(
            title=f"WT-VO2 #{level:.1f}: Torque Stomp + VO2 [{duration_min}m]",
            session_code="VO2_TORQUE",
            archetype_id="VO2_TORQUE_STOMP_BURST",
            category="VO2MAX",
            level=level,
            duration_min=duration_min,
            main_lines=main_lines,
            main_sec=main_sec,
            if_est=0.88,
            tactical_context="Reclutamento neuromuscolare da bassa cadenza seguito da regime aerobico elevato."
        )

    # --------------------------------------------------------------------------
    # SWEET SPOT ARCHETYPES
    # --------------------------------------------------------------------------
    def build_criss_cross_sst(self, level: float, duration_min: int) -> WorkoutSpec:
        """Criss-Cross Sweet Spot: 87% base with 95% surges."""
        duration_min = self._clamp_duration(duration_min)
        blocks = 3
        block_min = 8 if duration_min <= 45 else (9 if duration_min <= 52 else 10)
        cycles_per_block = block_min // 3

        main_lines = [
            "Sweet Spot Criss-Cross: oscillazioni continue tra base 87% e picco 95%"
        ]
        main_sec = 0
        for b in range(1, blocks + 1):
            main_lines.append(f"Blocco {b} - Criss-Cross ({block_min} min)")
            main_lines.append(f"{cycles_per_block}x")
            main_lines.append(f"- 2m 87% 90rpm Base Sweet Spot ({self._watts(87)}W)")
            main_lines.append(f"- 1m 95% 94rpm Salita di Tensione ({self._watts(95)}W)")
            main_sec += cycles_per_block * 180
            if b < blocks:
                main_lines.append(f"- 2m30s 55% 85rpm Recupero ({self._watts(55)}W)")
                main_sec += 150

        return self._finalize_workout(
            title=f"WT-SST #{level:.1f}: Criss-Cross Lactate Flux [{duration_min}m]",
            session_code="SST_CRISS_CROSS",
            archetype_id="SST_CRISS_CROSS_DENSITY",
            category="SWEET_SPOT",
            level=level,
            duration_min=duration_min,
            main_lines=main_lines,
            main_sec=main_sec,
            if_est=0.85,
            tactical_context="Adattamento mitocondriale alle oscillazioni di ritmo sostenute."
        )

    def build_forza_resistente_sst(self, level: float, duration_min: int) -> WorkoutSpec:
        """Forza Resistente: 55-60 RPM torque contrasted with 100 RPM spin at Sweet Spot."""
        duration_min = self._clamp_duration(duration_min)
        blocks = 3
        main_lines = [
            "Contrasto di Cadenza Forza Resistente (55 RPM) vs Agilità (100 RPM)"
        ]
        main_sec = 0
        for b in range(1, blocks + 1):
            main_lines.append(f"Serie {b} Forza Resistente Sweet Spot")
            main_lines.append("2x")
            main_lines.append(f"- 2m30s 90% 55-60rpm Forza Submassimale ({self._watts(90)}W)")
            main_lines.append(f"- 1m30s 88% 98-102rpm Spin Agile ({self._watts(88)}W)")
            main_sec += 2 * 240  # 8 min per block
            if b < blocks:
                main_lines.append(f"- 2m 55% 85rpm Recupero ({self._watts(55)}W)")
                main_sec += 120

        return self._finalize_workout(
            title=f"WT-SST #{level:.1f}: Forza Resistente 55/100 RPM [{duration_min}m]",
            session_code="SST_TORQUE",
            archetype_id="SST_FORZA_RESISTENTE_TORQUE",
            category="SWEET_SPOT",
            level=level,
            duration_min=duration_min,
            main_lines=main_lines,
            main_sec=main_sec,
            if_est=0.84,
            tactical_context="Reclutamento delle fibre muscolari profonde senza stress cardiaco."
        )

    def build_ascending_ramp_sst(self, level: float, duration_min: int) -> WorkoutSpec:
        """Ascending steps: 86% -> 90% -> 93%."""
        duration_min = self._clamp_duration(duration_min)
        blocks = 3
        main_lines = ["Gradini Ascendenti di Densità Aerobica (86% -> 90% -> 93%)"]
        main_sec = 0
        for b in range(1, blocks + 1):
            main_lines.append(f"Blocco {b} Gradini Ascendenti")
            main_lines.append(f"- 3m 86% 90rpm Gradino 1 ({self._watts(86)}W)")
            main_lines.append(f"- 3m 90% 90rpm Gradino 2 ({self._watts(90)}W)")
            main_lines.append(f"- 3m 93% 92rpm Gradino 3 ({self._watts(93)}W)")
            main_sec += 540  # 9 min
            if b < blocks:
                main_lines.append(f"- 2m 55% 85rpm Recupero ({self._watts(55)}W)")
                main_sec += 120

        return self._finalize_workout(
            title=f"WT-SST #{level:.1f}: Gradini Ascendenti SST [{duration_min}m]",
            session_code="SST_RAMP",
            archetype_id="SST_ASCENDING_RAMP_STEPS",
            category="SWEET_SPOT",
            level=level,
            duration_min=duration_min,
            main_lines=main_lines,
            main_sec=main_sec,
            if_est=0.86,
            tactical_context="Costruzione della capacità di accelerare nella seconda parte della salita."
        )

    def build_extended_endurance_sst(self, level: float, duration_min: int) -> WorkoutSpec:
        """2x 14-16 min extended continuous blocks."""
        duration_min = self._clamp_duration(duration_min)
        block_dur_min = 12 if duration_min <= 45 else (14 if duration_min <= 52 else 16)
        main_lines = [
            f"Blocchi Estesi Sweet Spot (2x {block_dur_min} min @ 90% FTP)",
            f"- {block_dur_min}m 90% 90-92rpm Blocco 1 ({self._watts(90)}W)",
            f"- 3m 55% 85rpm Recupero ({self._watts(55)}W)",
            f"- {block_dur_min}m 91% 90-92rpm Blocco 2 ({self._watts(91)}W)"
        ]
        main_sec = (block_dur_min * 60 * 2) + 180
        return self._finalize_workout(
            title=f"WT-SST #{level:.1f}: Extended Engine (2x{block_dur_min}m) [{duration_min}m]",
            session_code="SST_EXTENDED",
            archetype_id="SST_EXTENDED_ENDURANCE_BLOCK",
            category="SWEET_SPOT",
            level=level,
            duration_min=duration_min,
            main_lines=main_lines,
            main_sec=main_sec,
            if_est=0.85,
            tactical_context="Simulazione di salite lunghe e costanti ad andatura da WorldTour peloton."
        )

    def build_cadence_contrast_sst(self, level: float, duration_min: int) -> WorkoutSpec:
        """Cadence Contrast: alternating 85 RPM and 102 RPM inside Sweet Spot."""
        duration_min = self._clamp_duration(duration_min)
        blocks = 3
        main_lines = ["Dinamica di Cadenza Sweet Spot (85 RPM vs 102 RPM)"]
        main_sec = 0
        for b in range(1, blocks + 1):
            main_lines.append(f"Serie {b} - Contrasto Dinamico")
            main_lines.append(f"- 4m 90% 85rpm Cadenza Passo ({self._watts(90)}W)")
            main_lines.append(f"- 4m 90% 102rpm Cadenza Agilità ({self._watts(90)}W)")
            main_sec += 480  # 8 min
            if b < blocks:
                main_lines.append(f"- 2m 55% 85rpm Recupero ({self._watts(55)}W)")
                main_sec += 120

        return self._finalize_workout(
            title=f"WT-SST #{level:.1f}: Dinamica Cadenza 85/102 RPM [{duration_min}m]",
            session_code="SST_CADENCE",
            archetype_id="SST_CADENCE_CONTRAST_DYNAMIC",
            category="SWEET_SPOT",
            level=level,
            duration_min=duration_min,
            main_lines=main_lines,
            main_sec=main_sec,
            if_est=0.85,
            tactical_context="Prevenzione dell'affaticamento neuromuscolare variando gli angoli di trazione."
        )

    # --------------------------------------------------------------------------
    # THRESHOLD & OVER-UNDER ARCHETYPES
    # --------------------------------------------------------------------------
    def build_float_sets_thr(self, level: float, duration_min: int) -> WorkoutSpec:
        """Float Sets: 100% threshold followed by 85% float (no full recovery)."""
        duration_min = self._clamp_duration(duration_min)
        blocks = 3
        main_lines = [
            "Float Sets: clearance del lattato senza recupero passivo (100% soglia / 85% float)"
        ]
        main_sec = 0
        for b in range(1, blocks + 1):
            main_lines.append(f"Serie {b} Float Sets (9 min)")
            main_lines.append("3x")
            main_lines.append(f"- 2m 100% 92rpm Tocco di Soglia FTP ({self._watts(100)}W)")
            main_lines.append(f"- 1m 85% 90rpm Float Clearance ({self._watts(85)}W)")
            main_sec += 3 * 180  # 9 min
            if b < blocks:
                main_lines.append(f"- 2m30s 55% 85rpm Recupero ({self._watts(55)}W)")
                main_sec += 150

        return self._finalize_workout(
            title=f"WT-THR #{level:.1f}: Float Sets Clearance [{duration_min}m]",
            session_code="THR_FLOAT",
            archetype_id="THR_FLOAT_SETS_CLEARANCE",
            category="THRESHOLD",
            level=level,
            duration_min=duration_min,
            main_lines=main_lines,
            main_sec=main_sec,
            if_est=0.89,
            tactical_context="Allena il corpo a smaltire e utilizzare l'acido lattico come carburante senza rallentare."
        )

    def build_spanish_steps_thr(self, level: float, duration_min: int) -> WorkoutSpec:
        """Spanish Steps: Base 95% FTP with sharp 112-115% surges every 90 seconds."""
        duration_min = self._clamp_duration(duration_min)
        blocks = 3
        surge_pct = 112 if level < 4.0 else 115
        main_lines = [
            "Aumenta la cadenza a 98-102 RPM prima dello spike! (Anti-Spiral Suito)",
            "Spanish Steps: Base 95% FTP con sgasate a 115% ogni 90 secondi"
        ]
        main_sec = 0
        for b in range(1, blocks + 1):
            main_lines.append(f"Blocco {b} Spanish Steps (8m30s)")
            main_lines.append("5x")
            main_lines.append(f"- 1m20s 95% 90-92rpm Base Soglia ({self._watts(95)}W)")
            main_lines.append(f"- 20s {surge_pct}% 100-105rpm Sgasata Spanish Step ({self._watts(surge_pct)}W)")
            main_sec += 5 * 100  # 500s (8.3m)
            if b < blocks:
                main_lines.append(f"- 2m30s 55% 85rpm Recupero ({self._watts(55)}W)")
                main_sec += 150

        return self._finalize_workout(
            title=f"WT-THR #{level:.1f}: Spanish Steps Surges [{duration_min}m]",
            session_code="THR_SPANISH",
            archetype_id="THR_SPANISH_STEPS_SURGES",
            category="THRESHOLD",
            level=level,
            duration_min=duration_min,
            main_lines=main_lines,
            main_sec=main_sec,
            if_est=0.90,
            tactical_context="Simula la risposta immediata a tentativi di attacco durante una cronometro o salita."
        )

    def build_pyramid_over_under_thr(self, level: float, duration_min: int) -> WorkoutSpec:
        """Pyramid Over-Under: progressive Over lengths (30s -> 45s -> 60s -> 30s)."""
        duration_min = self._clamp_duration(duration_min)
        blocks = 3
        main_lines = [
            "Aumenta la cadenza a 95-100 RPM prima dello step Over! (Anti-Spiral Suito)",
            "Piramide Over-Under Lattacida (Under 92% / Over 108%)"
        ]
        main_sec = 0
        for b in range(1, blocks + 1):
            main_lines.append(f"Serie {b} Piramide Over-Under")
            main_lines.append(f"- 1m30s 92% 90rpm Under ({self._watts(92)}W)")
            main_lines.append(f"- 30s 108% 100rpm Over 1 ({self._watts(108)}W)")
            main_lines.append(f"- 1m30s 92% 90rpm Under ({self._watts(92)}W)")
            main_lines.append(f"- 45s 108% 100rpm Over 2 ({self._watts(108)}W)")
            main_lines.append(f"- 1m30s 92% 90rpm Under ({self._watts(92)}W)")
            main_lines.append(f"- 1m 108% 100rpm Over 3 ({self._watts(108)}W)")
            main_lines.append(f"- 1m30s 92% 90rpm Under Finale ({self._watts(92)}W)")
            main_sec += 90 + 30 + 90 + 45 + 90 + 60 + 90  # 495s (8.25 min)
            if b < blocks:
                main_lines.append(f"- 2m30s 55% 85rpm Recupero ({self._watts(55)}W)")
                main_sec += 150

        return self._finalize_workout(
            title=f"WT-THR #{level:.1f}: Piramide Over-Under [{duration_min}m]",
            session_code="THR_PYRAMID",
            archetype_id="THR_PYRAMID_OVER_UNDER",
            category="THRESHOLD",
            level=level,
            duration_min=duration_min,
            main_lines=main_lines,
            main_sec=main_sec,
            if_est=0.88,
            tactical_context="Tolleranza all'acidosi muscolare e modulazione della concentrazione di lattato ematico."
        )

    def build_high_cadence_agility_thr(self, level: float, duration_min: int) -> WorkoutSpec:
        """High cadence threshold agility: 100% FTP @ 98-102 RPM."""
        duration_min = self._clamp_duration(duration_min)
        blocks = 3
        block_dur = 8 if duration_min <= 48 else 9
        main_lines = [
            "Agilità di Soglia Cronometro: mantieni rigorosamente 98-102 RPM a 100% FTP"
        ]
        main_sec = 0
        for b in range(1, blocks + 1):
            main_lines.append(f"Blocco {b} - Agilità di Soglia ({block_dur}m)")
            main_lines.append(f"- {block_dur}m 100% 98-102rpm Soglia Aerobica Agile ({self._watts(100)}W)")
            main_sec += block_dur * 60
            if b < blocks:
                main_lines.append(f"- 2m30s 55% 85rpm Recupero ({self._watts(55)}W)")
                main_sec += 150

        return self._finalize_workout(
            title=f"WT-THR #{level:.1f}: Agilità Soglia Crono (100 RPM) [{duration_min}m]",
            session_code="THR_AGILITY",
            archetype_id="THR_HIGH_CADENCE_AGILITY",
            category="THRESHOLD",
            level=level,
            duration_min=duration_min,
            main_lines=main_lines,
            main_sec=main_sec,
            if_est=0.89,
            tactical_context="Efficienza neuromuscolare da specialista delle prove contro il tempo."
        )

    def build_sustained_progressive_ladder_thr(self, level: float, duration_min: int) -> WorkoutSpec:
        """Sustained ladder: 96% -> 98% -> 100%."""
        duration_min = self._clamp_duration(duration_min)
        main_lines = [
            "Scala Sostenuta verso la Soglia Anaerobica (96% -> 98% -> 100%)",
            f"- 8m 96% 90rpm Passo Sub-Soglia ({self._watts(96)}W)",
            f"- 2m30s 55% 85rpm Recupero ({self._watts(55)}W)",
            f"- 8m 98% 92rpm Piena Soglia ({self._watts(98)}W)",
            f"- 2m30s 55% 85rpm Recupero ({self._watts(55)}W)",
            f"- 8m 100% 92-94rpm Tocco Soglia Anaerobica ({self._watts(100)}W)"
        ]
        main_sec = (3 * 480) + (2 * 150)  # 1440 + 300 = 1740s (29 min)
        return self._finalize_workout(
            title=f"WT-THR #{level:.1f}: Scala Sostenuta FTP [{duration_min}m]",
            session_code="THR_LADDER",
            archetype_id="THR_SUSTAINED_PROGRESSIVE_LADDER",
            category="THRESHOLD",
            level=level,
            duration_min=duration_min,
            main_lines=main_lines,
            main_sec=main_sec,
            if_est=0.88,
            tactical_context="Simulazione finale di salita con progressione dal gruppo al traguardo."
        )

    # --------------------------------------------------------------------------
    # DELOAD & ACTIVATION ARCHETYPES
    # --------------------------------------------------------------------------
    def build_neuromuscular_openers_deload(self, level: float, duration_min: int) -> WorkoutSpec:
        """Deload week: active Z2 flush with 4 high cadence openers."""
        duration_min = self._clamp_duration(duration_min)
        main_lines = [
            "Fase Rigenerativa & Openers Neuromuscolari",
            f"- 12m 60% 90rpm Fondo Z2 Recupero Attivo ({self._watts(60)}W)",
            "Aumenta la cadenza a 105 RPM! (Anti-Spiral Suito)",
            "4x",
            f"- 15s 115% 105-110rpm Sprint Agilità ({self._watts(115)}W)",
            f"- 1m45s 50% 85rpm Recupero fluido ({self._watts(50)}W)"
        ]
        main_sec = 720 + (4 * 120)  # 1200s (20 min)
        return self._finalize_workout(
            title=f"WT-DELOAD #{level:.1f}: Openers & Agilità [{duration_min}m]",
            session_code="DELOAD_OPENERS",
            archetype_id="DELOAD_NEUROMUSCULAR_OPENERS",
            category="DELOAD",
            level=level,
            duration_min=duration_min,
            main_lines=main_lines,
            main_sec=main_sec,
            if_est=0.68,
            tactical_context="Mantenimento della reattività delle fibre muscolari e calibrazione pre-test."
        )

    def build_pre_race_activation_deload(self, level: float, duration_min: int) -> WorkoutSpec:
        """Deload week: activation with two short threshold touches."""
        duration_min = self._clamp_duration(duration_min)
        main_lines = [
            "Attivazione Pre-Test WorldTour",
            f"- 10m 60% 90rpm Fondo Z2 Recupero ({self._watts(60)}W)",
            f"- 3m 95% 92rpm Attivazione Respiratoria ({self._watts(95)}W)",
            f"- 3m 50% 85rpm Recupero ({self._watts(50)}W)",
            "Aumenta la cadenza a 95-100 RPM prima dello step!",
            f"- 3m 100% 94rpm Tocco di Soglia ({self._watts(100)}W)"
        ]
        main_sec = 600 + 180 + 180 + 180  # 1140s (19 min)
        return self._finalize_workout(
            title=f"WT-DELOAD #{level:.1f}: Attivazione Pre-Test [{duration_min}m]",
            session_code="DELOAD_ACTIVATION",
            archetype_id="DELOAD_PRE_RACE_ACTIVATION",
            category="DELOAD",
            level=level,
            duration_min=duration_min,
            main_lines=main_lines,
            main_sec=main_sec,
            if_est=0.69,
            tactical_context="Attivazione enzimatica aerobica mantenendo freschezza e glicogeno intatto."
        )

    # --------------------------------------------------------------------------
    # DYNAMIC SELECTION & ROTATION
    # --------------------------------------------------------------------------
    def select_next_archetype(
        self,
        category: str,
        used_archetype_ids: List[str]
    ) -> ArchetypeDefinition:
        """Select an unrepeated archetype from the library to ensure non-repetitive workouts."""
        if category == "VO2MAX":
            catalog = WorldTourWorkoutArchetypes.VO2MAX_ARCHETYPES
        elif category == "SWEET_SPOT":
            catalog = WorldTourWorkoutArchetypes.SWEET_SPOT_ARCHETYPES
        elif category == "THRESHOLD":
            catalog = WorldTourWorkoutArchetypes.THRESHOLD_ARCHETYPES
        else:
            catalog = WorldTourWorkoutArchetypes.DELOAD_ARCHETYPES

        available = [a for a in catalog if a.archetype_id not in used_archetype_ids]
        if not available:
            # If all have been used, reset and pick any
            available = catalog

        return random.choice(available)

    def build_dynamic_session(
        self,
        category: str,
        level: float,
        duration_min: int,
        used_archetype_ids: Optional[List[str]] = None
    ) -> WorkoutSpec:
        """Build a dynamically selected, non-repetitive workout for the requested category."""
        used = used_archetype_ids or []
        archetype = self.select_next_archetype(category, used)
        builder_fn = getattr(self, archetype.builder_func_name)
        return builder_fn(level=level, duration_min=duration_min)

    def build_weekly_schedule(
        self,
        week: int,
        training_days: List[str],
        weekday_duration: int = 50,
        friday_duration: int = 60,
        progression_levels: Optional[Dict[str, float]] = None,
        used_archetypes: Optional[List[str]] = None
    ) -> List[Tuple[str, WorkoutSpec]]:
        """Map training days to fresh, non-repetitive WorldTour workouts."""
        valid_days = [d.strip().upper() for d in training_days if d.strip()]
        if not valid_days:
            valid_days = ["MON", "WED", "FRI"]

        levels = progression_levels or {
            "vo2max": 1.0,
            "sweet_spot": 1.0,
            "threshold": 1.0
        }
        recent_used = list(used_archetypes or [])

        schedule: List[Tuple[str, WorkoutSpec]] = []

        if week == 4:
            # Week 4 is the Deload & Pre-Test Assessment week
            categories = ["DELOAD", "DELOAD", "DELOAD"]
        else:
            # Weeks 1-3: Monday VO2, Wednesday Sweet Spot, Friday Threshold
            categories = ["VO2MAX", "SWEET_SPOT", "THRESHOLD"]

        for idx, day in enumerate(valid_days):
            dur = friday_duration if day in ["FRI", "SAT", "SUN"] else weekday_duration

            if idx < len(categories):
                cat = categories[idx]
            else:
                cat = "SWEET_SPOT"

            # Determine progression level for this category
            if cat == "VO2MAX":
                lvl = levels.get("vo2max", 1.0)
            elif cat == "SWEET_SPOT":
                lvl = levels.get("sweet_spot", 1.0)
            elif cat == "THRESHOLD":
                lvl = levels.get("threshold", 1.0)
            else:
                lvl = 1.0

            spec = self.build_dynamic_session(
                category=cat,
                level=lvl,
                duration_min=dur,
                used_archetype_ids=recent_used
            )
            recent_used.append(spec.archetype_id)
            schedule.append((day, spec))

        return schedule
