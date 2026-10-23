"""WorldTour Indoor Cycling Workout Archetypes Library.

Provides an extensive catalog of scientifically designed, non-repetitive workout architectures:
- VO2max: Rønnestad micro-bursts, Hard-Start plateaus, Tabata clusters, Descending ladders, Billat 30/30.
- Sweet Spot: Classic sustained, Criss-Cross lactate oscillations, Low-cadence torque (Forza Resistente),
  Ascending ramps, Cadence contrasts, Extended endurance blocks.
- Threshold & Over-Under: Classic lactate shuttle, Float sets (no-rest clearance), Pyramid Over-Unders,
  Spanish Steps surges, High-cadence threshold agility.
- Deload & Activation: High-cadence openers, Pre-competition primer, Active endurance flush.

All archetypes dynamically adapt to the requested duration (strictly 42-60 min),
the athlete's progression level (1.0 to 10.0), and Elite Suito ERG mechanics.
"""

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple


@dataclass
class ArchetypeDefinition:
    archetype_id: str
    category: str  # VO2MAX, SWEET_SPOT, THRESHOLD, DELOAD
    title_template: str
    description_focus: str
    tactical_context: str
    builder_func_name: str


class WorldTourWorkoutArchetypes:
    """Catalog of WorldTour indoor workout architectures."""

    VO2MAX_ARCHETYPES = [
        ArchetypeDefinition(
            archetype_id="VO2_RONNESTAD_30_15",
            category="VO2MAX",
            title_template="WT-VO2 #{level}: Rønnestad High-Ventilation 30/15",
            description_focus="Stimolo massimale del consumo di ossigeno e stroke volume cardiaco.",
            tactical_context="Simula una serie di rilanci violenti all'imbocco di una salita ripida.",
            builder_func_name="build_ronnestad_30_15"
        ),
        ArchetypeDefinition(
            archetype_id="VO2_HARD_START_PLATEAU",
            category="VO2MAX",
            title_template="WT-VO2 #{level}: Hard-Start Fast O2-Kinetics",
            description_focus="Saturazione immediata del debito O2 tramite burst a 130% prima del plateau a 112%.",
            tactical_context="Simula un attacco a tutta per andare in fuga, stabilizzando poi il passo limite.",
            builder_func_name="build_hard_start_plateau"
        ),
        ArchetypeDefinition(
            archetype_id="VO2_DESCENDING_LADDER",
            category="VO2MAX",
            title_template="WT-VO2 #{level}: Piramide Discendente O2 Kinetics",
            description_focus="Intervalli decrescenti per durata (4m-3m-2m-1m) con potenza crescente (108% -> 125%).",
            tactical_context="Gestione della fatica progressiva tipica dei finali di tappa nervosi.",
            builder_func_name="build_descending_ladder"
        ),
        ArchetypeDefinition(
            archetype_id="VO2_TABATA_CLUSTERS",
            category="VO2MAX",
            title_template="WT-VO2 #{level}: Micro-bursts Tabata 40/20 & 30/30",
            description_focus="Svuotamento dei fosfati e mantenimento prolungato della soglia cardiaca al 95% FCmax.",
            tactical_context="Frazionamento dello sforzo per massimizzare il tempo speso sopra il 90% di VO2max.",
            builder_func_name="build_tabata_clusters"
        ),
        ArchetypeDefinition(
            archetype_id="VO2_TORQUE_STOMP_BURST",
            category="VO2MAX",
            title_template="WT-VO2 #{level}: Torque Stomp + Plateau VO2max",
            description_focus="Reclutamento neuromuscolare delle fibre veloci tipo IIx seguito da consumo aerobico.",
            tactical_context="Scatto da fermo/bassa cadenza per superare un dosso e mantenimento ad alta cadenza.",
            builder_func_name="build_torque_stomp_burst"
        )
    ]

    SWEET_SPOT_ARCHETYPES = [
        ArchetypeDefinition(
            archetype_id="SST_CRISS_CROSS_DENSITY",
            category="SWEET_SPOT",
            title_template="WT-SST #{level}: Criss-Cross Lactate Flux",
            description_focus="Oscillazioni continue tra 87% (accumulo) e 95% (bruciatore) a cadenza 90 RPM.",
            tactical_context="Adattamento mitocondriale alle variazioni di ritmo in gruppo a velocità sostenuta.",
            builder_func_name="build_criss_cross_sst"
        ),
        ArchetypeDefinition(
            archetype_id="SST_FORZA_RESISTENTE_TORQUE",
            category="SWEET_SPOT",
            title_template="WT-SST #{level}: Forza Resistente 55 RPM vs Spin 100 RPM",
            description_focus="Contrasto cadenza: 55 RPM (forza sub-massimale) alternati a 100 RPM (agilità neuromuscolare).",
            tactical_context="Reclutamento delle fibre muscolari profonde senza sovraccarico cardiorespiratorio.",
            builder_func_name="build_forza_resistente_sst"
        ),
        ArchetypeDefinition(
            archetype_id="SST_ASCENDING_RAMP_STEPS",
            category="SWEET_SPOT",
            title_template="WT-SST #{level}: Gradini Ascendenti di Densità",
            description_focus="Blocchi progressivi a scalare: 86% -> 90% -> 93% FTP con recuperi decrescenti.",
            tactical_context="Costruzione della capacità di accelerare progressivamente nella seconda metà di gara.",
            builder_func_name="build_ascending_ramp_sst"
        ),
        ArchetypeDefinition(
            archetype_id="SST_EXTENDED_ENDURANCE_BLOCK",
            category="SWEET_SPOT",
            title_template="WT-SST #{level}: Extended Aerobic Engine (2x 14-16m)",
            description_focus="Lavoro continuo ad altissima efficienza metabolica al 90% FTP.",
            tactical_context="Simulazione di salite lunghe e costanti ad andatura da WorldTour peloton.",
            builder_func_name="build_extended_endurance_sst"
        ),
        ArchetypeDefinition(
            archetype_id="SST_CADENCE_CONTRAST_DYNAMIC",
            category="SWEET_SPOT",
            title_template="WT-SST #{level}: Dinamica di Cadenza 85/102 RPM",
            description_focus="Mantenimento dei 91% FTP cambiando cadenza ogni 3-4 minuti per variare l'angolo di spinta.",
            tactical_context="Prevenzione dell'affaticamento neuromuscolare periferico.",
            builder_func_name="build_cadence_contrast_sst"
        )
    ]

    THRESHOLD_ARCHETYPES = [
        ArchetypeDefinition(
            archetype_id="THR_FLOAT_SETS_CLEARANCE",
            category="THRESHOLD",
            title_template="WT-THR #{level}: Float Sets Clearance (100% / Float 85%)",
            description_focus="Nessun recupero passivo: 3 min a soglia (100%) seguiti da 1 min 'Float' all'85% FTP.",
            tactical_context="Allena il corpo a smaltire e utilizzare l'acido lattico come carburante senza rallentare.",
            builder_func_name="build_float_sets_thr"
        ),
        ArchetypeDefinition(
            archetype_id="THR_SPANISH_STEPS_SURGES",
            category="THRESHOLD",
            title_template="WT-THR #{level}: Spanish Steps (Base 95% + Surges 112%)",
            description_focus="Pedalata a soglia 95% interrotta ogni 90 secondi da una sgasata di 20s a 112-115% FTP.",
            tactical_context="Simula la risposta a tentativi di attacco durante una cronometro o salita dura.",
            builder_func_name="build_spanish_steps_thr"
        ),
        ArchetypeDefinition(
            archetype_id="THR_PYRAMID_OVER_UNDER",
            category="THRESHOLD",
            title_template="WT-THR #{level}: Piramide Over-Under Lattacida",
            description_focus="Struttura piramidale: Over da 30s a 90s a 108% FTP su base Under al 92% FTP.",
            tactical_context="Tolleranza all'acidosi muscolare e modulazione della concentrazione di lattato ematico.",
            builder_func_name="build_pyramid_over_under_thr"
        ),
        ArchetypeDefinition(
            archetype_id="THR_HIGH_CADENCE_AGILITY",
            category="THRESHOLD",
            title_template="WT-THR #{level}: Agilità di Soglia Crono (98-102 RPM)",
            description_focus="Soglia costante al 98-100% FTP mantenendo rigorosamente 98-102 RPM.",
            tactical_context="Efficienza neuromuscolare da specialista delle prove contro il tempo.",
            builder_func_name="build_high_cadence_agility_thr"
        ),
        ArchetypeDefinition(
            archetype_id="THR_SUSTAINED_PROGRESSIVE_LADDER",
            category="THRESHOLD",
            title_template="WT-THR #{level}: Scala Sostenuta FTP (96% -> 100%)",
            description_focus="Serie a salire verso la soglia anaerobica con gestione della fatica centrale.",
            tactical_context="Simulazione finale di salita con progressione dal gruppo al traguardo.",
            builder_func_name="build_sustained_progressive_ladder_thr"
        )
    ]

    DELOAD_ARCHETYPES = [
        ArchetypeDefinition(
            archetype_id="DELOAD_NEUROMUSCULAR_OPENERS",
            category="DELOAD",
            title_template="WT-DELOAD #{level}: Openers Neuromuscolari & Agilità",
            description_focus="Recupero attivo Z2 intervallato da 4 scatti controllati a 105 RPM senza accumulo di fatica.",
            tactical_context="Mantenimento della reattività delle fibre muscolari e calibrazione pre-test.",
            builder_func_name="build_neuromuscular_openers_deload"
        ),
        ArchetypeDefinition(
            archetype_id="DELOAD_PRE_RACE_ACTIVATION",
            category="DELOAD",
            title_template="WT-DELOAD #{level}: Attivazione Pre-Test WorldTour",
            description_focus="Fondo facile con due brevi allunghi di 2.5 min al 95% FTP per sbloccare la respirazione.",
            tactical_context="Attivazione enzimatica aerobica mantenendo freschezza e glicogeno intatto.",
            builder_func_name="build_pre_race_activation_deload"
        )
    ]
