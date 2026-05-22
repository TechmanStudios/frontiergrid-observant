"""Repeatable unclassified synthetic scenarios for Phase I demos."""

from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta

from frontiergrid_observant.schemas.events import GroundTruth, Location, ObservantEvent

SCENARIOS = {
    "scenario_01": "scenario_01_maritime_shadowing",
    "scenario_02": "scenario_02_littoral_hazard",
    "scenario_03": "scenario_03_degraded_comms_decoy",
    "scenario_04": "scenario_04_cross_domain_ambiguity",
    "scenario_05": "scenario_05_unknown_unknown_injection",
}

CROSS_DOMAIN_SEQUENCE = ("maritime", "space", "air", "land", "cyber_network")


def _timestamp(tick: int) -> datetime:
    return datetime(2026, 5, 20, 13, 0, tzinfo=UTC) + timedelta(minutes=4 * tick)


def _event(
    event_id: str,
    scenario_id: str,
    tick: int,
    domain: str,
    modality: str,
    source_id: str,
    reliability: float,
    entity_refs: list[str],
    attributes: dict[str, float | str | bool],
    text: str,
    anomaly: bool,
    risk_type: str,
    severity: float,
    location: Location | None = None,
) -> ObservantEvent:
    return ObservantEvent(
        event_id=event_id,
        scenario_id=scenario_id,
        tick=tick,
        timestamp=_timestamp(tick),
        domain=domain,
        modality=modality,
        source_id=source_id,
        source_reliability=reliability,
        classification="unclassified_synthetic",
        entity_refs=entity_refs,
        location=location,
        attributes=attributes,
        text=text,
        ground_truth=GroundTruth(is_anomaly=anomaly, risk_type=risk_type, severity=severity),
    )


def _cycle_domain(tick: int) -> str:
    return CROSS_DOMAIN_SEQUENCE[tick % len(CROSS_DOMAIN_SEQUENCE)]


def _alignment(rng: random.Random, anomaly: bool, base: float = 0.64) -> float:
    if anomaly:
        return round(min(0.84, base + rng.uniform(-0.05, 0.08)), 2)
    return round(rng.uniform(0.16, 0.30), 2)


def _quality(rng: random.Random, anomaly: bool, nominal: float = 0.82, degraded: float = 0.72) -> float:
    center = degraded if anomaly else nominal
    return round(max(0.35, min(0.94, center + rng.uniform(-0.06, 0.05))), 2)


def _location_for(tick: int, *, lat: float, lon: float, confidence: float) -> Location:
    return Location(lat=lat + tick * 0.006, lon=lon + tick * 0.007, confidence=confidence)


def generate_maritime_shadowing(seed: int = 149, ticks: int = 30) -> list[ObservantEvent]:
    rng = random.Random(seed)
    scenario_id = SCENARIOS["scenario_01"]
    events: list[ObservantEvent] = []
    for tick in range(ticks):
        anomaly = tick >= max(8, ticks // 3)
        severity = min(0.86, 0.18 + 0.035 * tick) if anomaly else rng.uniform(0.03, 0.16)
        distance_nm = max(0.4, 8.5 - 0.22 * tick + rng.uniform(-0.3, 0.3))
        speed = 10.0 + rng.uniform(-1.2, 1.2)
        behavior_tag = "route_parallel" if anomaly else "routine_transit"
        domain = _cycle_domain(tick)
        data_quality = _quality(rng, anomaly, degraded=0.74)
        alignment_score = _alignment(rng, anomaly, base=0.68)

        if domain == "maritime":
            modality = "track"
            source_id = "synthetic_ais_feed"
            reliability = 0.82
            attributes = {
                "speed_knots": round(speed, 2),
                "distance_nm": round(distance_nm, 2),
                "behavior_tag": behavior_tag,
                "alignment_score": alignment_score,
                "data_quality": data_quality,
            }
            text = (
                "Synthetic vessel alpha remains parallel to route segment."
                if anomaly
                else "Synthetic vessel alpha follows expected transit lane."
            )
        elif domain == "space":
            modality = "imagery_metadata"
            source_id = "synthetic_overhead_cue"
            reliability = 0.76
            attributes = {
                "overhead_revisit_minutes": 38.0 if anomaly else 72.0,
                "route_corridor_overlap": round(0.64 + rng.uniform(-0.05, 0.08), 2)
                if anomaly
                else 0.24,
                "alignment_score": alignment_score,
                "data_quality": data_quality,
            }
            text = (
                "Synthetic overhead metadata places the contact near the same route corridor."
                if anomaly
                else "Synthetic overhead metadata shows no route-focused activity."
            )
        elif domain == "air":
            modality = "isr_availability"
            source_id = "synthetic_air_isr_scheduler"
            reliability = 0.72
            attributes = {
                "sensor_coverage_gap": anomaly,
                "track_continuity": round(0.58 + rng.uniform(-0.04, 0.06), 2)
                if anomaly
                else 0.82,
                "alignment_score": alignment_score,
                "data_quality": data_quality,
            }
            text = (
                "Synthetic air ISR availability introduces a gap along the observed transit path."
                if anomaly
                else "Synthetic air ISR availability remains adequate for routine transit."
            )
        elif domain == "land":
            modality = "logistics_note"
            source_id = "synthetic_port_liaison"
            reliability = 0.70
            attributes = {
                "logistics_route_relevance": 0.76 if anomaly else 0.28,
                "port_departure_correlation": 0.66 if anomaly else 0.18,
                "alignment_score": alignment_score,
                "data_quality": data_quality,
            }
            text = (
                "Synthetic port note links the contact to a protected route window."
                if anomaly
                else "Synthetic port note indicates routine commercial movement."
            )
        else:
            modality = "network_status"
            source_id = "synthetic_comms_monitor"
            reliability = 0.68 if anomaly else 0.78
            attributes = {
                "message_latency_ms": 420.0 + tick * 12 if anomaly else 140.0 + tick,
                "relay_anomaly_score": 0.61 if anomaly else 0.16,
                "alignment_score": alignment_score,
                "data_quality": data_quality,
            }
            text = (
                "Synthetic relay behavior weakly aligns with the shadowing timeline."
                if anomaly
                else "Synthetic relay behavior remains within nominal range."
            )
        events.append(
            _event(
                event_id=f"evt-s01-{tick:04d}",
                scenario_id=scenario_id,
                tick=tick,
                domain=domain,
                modality=modality,
                source_id=source_id,
                reliability=reliability,
                entity_refs=["vessel_alpha", "route_corridor_a"],
                location=_location_for(tick, lat=30.0, lon=-80.0, confidence=0.76),
                attributes=attributes,
                text=text,
                anomaly=anomaly,
                risk_type="shadowing_pattern" if anomaly else "nominal",
                severity=severity,
            )
        )
    return events


def generate_littoral_hazard(seed: int = 223, ticks: int = 30) -> list[ObservantEvent]:
    rng = random.Random(seed)
    scenario_id = SCENARIOS["scenario_02"]
    events: list[ObservantEvent] = []
    for tick in range(ticks):
        anomaly = tick >= max(10, ticks // 2)
        severity = min(0.82, 0.12 + 0.04 * (tick - 6)) if anomaly else rng.uniform(0.02, 0.14)
        domain = _cycle_domain(tick + 3)
        data_quality = _quality(rng, anomaly, degraded=0.70)
        alignment_score = _alignment(rng, anomaly, base=0.66)
        if domain == "maritime":
            modality = "surface_sensor"
            source_id = "synthetic_navigation_sensor"
            reliability = 0.76
            attributes = {
                "sea_state": "moderate" if anomaly else "calm",
                "cluster_density": round(0.18 + 0.03 * tick, 2) if anomaly else 0.12,
                "logistics_route_relevance": 0.78 if anomaly else 0.28,
                "alignment_score": alignment_score,
                "data_quality": data_quality,
            }
            text = (
                "Synthetic surface sensor indicates obstruction-like clutter near route delta."
                if anomaly
                else "Synthetic surface sensor reports normal route conditions."
            )
        elif domain == "space":
            modality = "imagery_metadata"
            source_id = "synthetic_littoral_imagery"
            reliability = 0.73
            attributes = {
                "shoreline_change_score": 0.62 if anomaly else 0.14,
                "cluster_density": round(0.16 + 0.025 * tick, 2) if anomaly else 0.10,
                "alignment_score": alignment_score,
                "data_quality": data_quality,
            }
            text = (
                "Synthetic imagery metadata shows a forming cluster near the littoral route."
                if anomaly
                else "Synthetic imagery metadata shows no relevant littoral change."
            )
        elif domain == "air":
            modality = "weather_context"
            source_id = "synthetic_weather_feed"
            reliability = 0.79
            attributes = {
                "visibility_nm": 3.6 if anomaly else 8.4,
                "weather_route_impact": 0.58 if anomaly else 0.18,
                "alignment_score": alignment_score,
                "data_quality": data_quality,
            }
            text = (
                "Synthetic weather context reduces route-clearance confidence."
                if anomaly
                else "Synthetic weather context supports normal route clearance."
            )
        elif domain == "land":
            modality = "hazard_report"
            source_id = "synthetic_littoral_feed"
            reliability = 0.74 if tick % 5 else 0.62
            attributes = {
                "shore_access_disruption": anomaly,
                "cluster_density": round(0.18 + 0.03 * tick, 2) if anomaly else 0.12,
                "logistics_route_relevance": 0.80 if anomaly else 0.26,
                "alignment_score": alignment_score,
                "data_quality": data_quality,
            }
            text = (
                "Synthetic littoral report indicates a forming obstruction cluster."
                if anomaly
                else "Synthetic littoral route checks remain within expected conditions."
            )
        else:
            modality = "network_status"
            source_id = "synthetic_buoy_network"
            reliability = 0.69 if anomaly else 0.80
            attributes = {
                "missing_sensor_window": anomaly and tick % 2 == 0,
                "message_latency_ms": 520.0 + tick * 18 if anomaly else 125.0 + tick,
                "alignment_score": alignment_score,
                "data_quality": data_quality,
            }
            text = (
                "Synthetic buoy network gaps align with the hazard-cluster interval."
                if anomaly
                else "Synthetic buoy network telemetry is stable."
            )
        events.append(
            _event(
                event_id=f"evt-s02-{tick:04d}",
                scenario_id=scenario_id,
                tick=tick,
                domain=domain,
                modality=modality,
                source_id=source_id,
                reliability=reliability,
                entity_refs=["route_delta", "littoral_zone_k"],
                location=_location_for(tick, lat=26.4, lon=-77.2, confidence=0.68),
                attributes=attributes,
                text=text,
                anomaly=anomaly,
                risk_type="littoral_hazard_cluster" if anomaly else "nominal",
                severity=severity,
            )
        )
    return events


def generate_degraded_comms_decoy(seed: int = 317, ticks: int = 30) -> list[ObservantEvent]:
    rng = random.Random(seed)
    scenario_id = SCENARIOS["scenario_03"]
    events: list[ObservantEvent] = []
    for tick in range(ticks):
        anomaly = tick >= max(7, ticks // 4)
        domain = _cycle_domain(tick + 4)
        intermittent = anomaly and (tick % 2 == 0 or domain == "cyber_network")
        false_positive_pressure = 0.58 if anomaly and tick % 5 == 0 else 0.18
        severity = min(0.78, 0.16 + 0.025 * tick) if anomaly else rng.uniform(0.02, 0.12)
        data_quality = _quality(rng, anomaly, nominal=0.80, degraded=0.56)
        alignment_score = _alignment(rng, anomaly, base=0.60)
        if domain == "cyber_network":
            modality = "network_status"
            source_id = "synthetic_comms_monitor"
            reliability = 0.56 if intermittent else 0.66
            attributes = {
                "message_latency_ms": 900.0 + tick * 40 if anomaly else 120.0 + tick,
                "missing_message_window": intermittent,
                "false_positive_pressure": false_positive_pressure,
                "alignment_score": alignment_score,
                "data_quality": min(data_quality, 0.52 if anomaly else data_quality),
            }
            text = (
                "Synthetic degraded communications and decoy-like reports reduce context quality."
                if anomaly
                else "Synthetic communications remain stable."
            )
        elif domain == "maritime":
            modality = "track_report"
            source_id = "synthetic_track_relay"
            reliability = 0.64 if anomaly else 0.77
            attributes = {
                "track_fragmentation": 0.62 if anomaly else 0.14,
                "false_positive_pressure": false_positive_pressure,
                "alignment_score": alignment_score,
                "data_quality": data_quality,
            }
            text = (
                "Synthetic track relay fragments support the degraded-comms timeline."
                if anomaly
                else "Synthetic track relay remains coherent."
            )
        elif domain == "space":
            modality = "imagery_metadata"
            source_id = "synthetic_overhead_metadata"
            reliability = 0.62 if anomaly else 0.76
            attributes = {
                "identity_mismatch_score": 0.56 if anomaly else 0.12,
                "false_positive_pressure": false_positive_pressure,
                "alignment_score": alignment_score,
                "data_quality": data_quality,
            }
            text = (
                "Synthetic overhead metadata cannot resolve a decoy-like identity mismatch."
                if anomaly
                else "Synthetic overhead metadata is consistent with nominal identity."
            )
        elif domain == "air":
            modality = "relay_coverage"
            source_id = "synthetic_air_relay"
            reliability = 0.60 if anomaly else 0.78
            attributes = {
                "relay_coverage_gap": intermittent,
                "message_latency_ms": 760.0 + tick * 24 if anomaly else 118.0 + tick,
                "false_positive_pressure": false_positive_pressure,
                "alignment_score": alignment_score,
                "data_quality": data_quality,
            }
            text = (
                "Synthetic relay coverage gap increases uncertainty in the decoy assessment."
                if anomaly
                else "Synthetic relay coverage supports nominal communications."
            )
        else:
            modality = "operator_note"
            source_id = "synthetic_operations_log"
            reliability = 0.66 if anomaly else 0.81
            attributes = {
                "ambiguous_report": anomaly,
                "false_positive_pressure": min(0.62, false_positive_pressure + 0.10)
                if anomaly
                else 0.12,
                "alignment_score": alignment_score,
                "data_quality": data_quality,
            }
            text = (
                "Synthetic operator note flags ambiguity and requests human review."
                if anomaly
                else "Synthetic operator note reports routine communications posture."
            )
        events.append(
            _event(
                event_id=f"evt-s03-{tick:04d}",
                scenario_id=scenario_id,
                tick=tick,
                domain=domain,
                modality=modality,
                source_id=source_id,
                reliability=reliability,
                entity_refs=["task_group_echo", "relay_node_3"],
                attributes=attributes,
                text=text,
                anomaly=anomaly,
                risk_type="degraded_comms_decoy" if anomaly else "nominal",
                severity=severity,
            )
        )
    return events


def generate_cross_domain_ambiguity(seed: int = 401, ticks: int = 30) -> list[ObservantEvent]:
    rng = random.Random(seed)
    scenario_id = SCENARIOS["scenario_04"]
    events: list[ObservantEvent] = []
    for tick in range(ticks):
        anomaly = tick >= max(9, ticks // 3)
        domain = _cycle_domain(tick + 1)
        severity = min(0.80, 0.10 + 0.028 * tick) if anomaly else rng.uniform(0.03, 0.13)
        data_quality = _quality(rng, anomaly, degraded=0.68)
        alignment_score = _alignment(rng, anomaly, base=0.58)
        if domain == "maritime":
            modality = "track"
            source_id = "synthetic_surface_track"
            reliability = 0.76
            attributes = {
                "distance_nm": max(1.6, 7.6 - 0.16 * tick),
                "route_shadow_score": 0.57 if anomaly else 0.16,
                "alignment_score": alignment_score,
                "data_quality": data_quality,
            }
            text = (
                "Synthetic vessel behavior is weak alone but aligns with wider mission context."
                if anomaly
                else "Synthetic vessel behavior remains routine."
            )
        elif domain == "space":
            modality = "imagery_metadata"
            source_id = "synthetic_overhead_queue"
            reliability = 0.73
            attributes = {
                "overhead_revisit_minutes": 44.0 if anomaly else 88.0,
                "object_persistence_score": 0.55 if anomaly else 0.12,
                "alignment_score": alignment_score,
                "data_quality": data_quality,
            }
            text = (
                "Synthetic overhead cue is ambiguous but temporally aligned with other domains."
                if anomaly
                else "Synthetic overhead cue has no persistent mission relevance."
            )
        elif domain == "air":
            modality = "weather_isr_context"
            source_id = "synthetic_air_tasking"
            reliability = 0.71
            attributes = {
                "isr_tasking_gap": anomaly,
                "weather_route_impact": 0.52 if anomaly else 0.14,
                "alignment_score": alignment_score,
                "data_quality": data_quality,
            }
            text = (
                "Synthetic air and weather context creates an observation gap along the route."
                if anomaly
                else "Synthetic air and weather context remains favorable."
            )
        elif domain == "land":
            modality = "logistics_report"
            source_id = "synthetic_port_status"
            reliability = 0.69 if anomaly else 0.80
            attributes = {
                "port_activity_shift": anomaly,
                "logistics_route_relevance": 0.61 if anomaly else 0.22,
                "alignment_score": alignment_score,
                "data_quality": data_quality,
            }
            text = (
                "Synthetic logistics report adds weak support to the cross-domain ambiguity."
                if anomaly
                else "Synthetic logistics report remains routine."
            )
        else:
            modality = "network_status"
            source_id = "synthetic_edge_network"
            reliability = 0.67 if anomaly else 0.78
            attributes = {
                "message_latency_ms": 620.0 + tick * 18 if anomaly else 132.0 + tick,
                "relay_anomaly_score": 0.54 if anomaly else 0.13,
                "alignment_score": alignment_score,
                "data_quality": data_quality,
            }
            text = (
                "Synthetic edge-network latency aligns with the ambiguous cross-domain pattern."
                if anomaly
                else "Synthetic edge-network latency remains normal."
            )
        events.append(
            _event(
                event_id=f"evt-s04-{tick:04d}",
                scenario_id=scenario_id,
                tick=tick,
                domain=domain,
                modality=modality,
                source_id=source_id,
                reliability=reliability,
                entity_refs=["mission_thread_zeta", "route_corridor_c"],
                location=_location_for(tick, lat=28.1, lon=-76.4, confidence=0.64),
                attributes=attributes,
                text=text,
                anomaly=anomaly,
                risk_type="cross_domain_ambiguity" if anomaly else "nominal",
                severity=severity,
            )
        )
    return events


def generate_unknown_unknown_injection(seed: int = 509, ticks: int = 30) -> list[ObservantEvent]:
    rng = random.Random(seed)
    scenario_id = SCENARIOS["scenario_05"]
    events: list[ObservantEvent] = []
    injection_tick = max(11, ticks // 3)
    for tick in range(ticks):
        anomaly = tick >= injection_tick
        domain = _cycle_domain(tick + 2)
        time_since_injection = max(0, tick - injection_tick)
        severity = min(0.82, 0.34 + 0.026 * time_since_injection) if anomaly else rng.uniform(0.02, 0.12)
        data_quality = _quality(rng, anomaly, nominal=0.83, degraded=0.59)
        alignment_score = round(rng.uniform(0.42, 0.52), 2) if anomaly else round(rng.uniform(0.12, 0.24), 2)
        novelty_score = round(min(0.94, 0.72 + 0.015 * time_since_injection), 2) if anomaly else round(rng.uniform(0.04, 0.12), 2)
        injection_marker = anomaly and tick == injection_tick

        if domain == "maritime":
            modality = "unclassified_surface_anomaly"
            source_id = "synthetic_surface_watch"
            reliability = 0.62 if anomaly else 0.80
            attributes = {
                "unknown_unknown_marker": injection_marker,
                "novelty_score": novelty_score,
                "schema_surprise": 0.88 if injection_marker else 0.66 if anomaly else 0.10,
                "distance_nm": 5.4 if anomaly else 8.8,
                "alignment_score": alignment_score,
                "data_quality": data_quality,
            }
            text = (
                "Synthetic surface observation carries a novel signature outside known route patterns."
                if anomaly
                else "Synthetic surface observation remains within known route patterns."
            )
        elif domain == "space":
            modality = "novel_overhead_signature"
            source_id = "synthetic_space_anomaly_feed"
            reliability = 0.61 if anomaly else 0.78
            attributes = {
                "unknown_unknown_marker": injection_marker,
                "novelty_score": novelty_score,
                "spectral_residual": 0.69 if anomaly else 0.09,
                "object_persistence_score": 0.49 if anomaly else 0.11,
                "alignment_score": alignment_score,
                "data_quality": data_quality,
            }
            text = (
                "Synthetic overhead metadata records an unmodeled residual near the mission thread."
                if anomaly
                else "Synthetic overhead metadata remains explainable by known signatures."
            )
        elif domain == "air":
            modality = "unexpected_isr_state"
            source_id = "synthetic_air_state_monitor"
            reliability = 0.63 if anomaly else 0.79
            attributes = {
                "unknown_unknown_marker": injection_marker,
                "novelty_score": novelty_score,
                "sensor_residual": 0.67 if anomaly else 0.08,
                "isr_tasking_gap": False,
                "alignment_score": alignment_score,
                "data_quality": data_quality,
            }
            text = (
                "Synthetic air-state telemetry deviates without matching a known degraded-coverage pattern."
                if anomaly
                else "Synthetic air-state telemetry remains inside expected operating bands."
            )
        elif domain == "land":
            modality = "operator_observation"
            source_id = "synthetic_watch_floor"
            reliability = 0.60 if anomaly else 0.81
            attributes = {
                "unknown_unknown_marker": injection_marker,
                "novelty_score": novelty_score,
                "operator_uncertainty": 0.71 if anomaly else 0.12,
                "logistics_route_relevance": 0.46 if anomaly else 0.18,
                "alignment_score": alignment_score,
                "data_quality": data_quality,
            }
            text = (
                "Synthetic operator note flags an observation that does not fit current playbooks."
                if anomaly
                else "Synthetic operator note describes routine context."
            )
        else:
            modality = "edge_network_residual"
            source_id = "synthetic_edge_residual_monitor"
            reliability = 0.59 if anomaly else 0.80
            attributes = {
                "unknown_unknown_marker": injection_marker,
                "novelty_score": novelty_score,
                "protocol_residual": 0.68 if anomaly else 0.10,
                "message_latency_ms": 450.0 if anomaly else 125.0 + tick,
                "alignment_score": alignment_score,
                "data_quality": data_quality,
            }
            text = (
                "Synthetic edge-network residual appears after the novel state-space injection."
                if anomaly
                else "Synthetic edge-network residual remains nominal."
            )
        events.append(
            _event(
                event_id=f"evt-s05-{tick:04d}",
                scenario_id=scenario_id,
                tick=tick,
                domain=domain,
                modality=modality,
                source_id=source_id,
                reliability=reliability,
                entity_refs=["unknown_thread_eta", "mission_state_space"],
                location=_location_for(tick, lat=27.3, lon=-75.9, confidence=0.58),
                attributes=attributes,
                text=text,
                anomaly=anomaly,
                risk_type="unknown_unknown_injection" if anomaly else "nominal",
                severity=severity,
            )
        )
    return events


def generate_scenario(scenario: str, seed: int = 149, ticks: int = 30) -> list[ObservantEvent]:
    key = scenario if scenario in SCENARIOS else None
    if key is None:
        key = next((item for item, scenario_id in SCENARIOS.items() if scenario == scenario_id), None)
    if key in {"scenario_01", SCENARIOS["scenario_01"]}:
        return generate_maritime_shadowing(seed=seed, ticks=ticks)
    if key in {"scenario_02", SCENARIOS["scenario_02"]}:
        return generate_littoral_hazard(seed=seed, ticks=ticks)
    if key in {"scenario_03", SCENARIOS["scenario_03"]}:
        return generate_degraded_comms_decoy(seed=seed, ticks=ticks)
    if key in {"scenario_04", SCENARIOS["scenario_04"]}:
        return generate_cross_domain_ambiguity(seed=seed, ticks=ticks)
    if key in {"scenario_05", SCENARIOS["scenario_05"]}:
        return generate_unknown_unknown_injection(seed=seed, ticks=ticks)
    raise ValueError(f"Unknown scenario: {scenario}")


def generate_all(seed: int = 149, ticks: int = 30) -> dict[str, list[ObservantEvent]]:
    return {
        SCENARIOS["scenario_01"]: generate_maritime_shadowing(seed=seed, ticks=ticks),
        SCENARIOS["scenario_02"]: generate_littoral_hazard(seed=seed + 1, ticks=ticks),
        SCENARIOS["scenario_03"]: generate_degraded_comms_decoy(seed=seed + 2, ticks=ticks),
        SCENARIOS["scenario_04"]: generate_cross_domain_ambiguity(seed=seed + 3, ticks=ticks),
        SCENARIOS["scenario_05"]: generate_unknown_unknown_injection(seed=seed + 4, ticks=ticks),
    }
