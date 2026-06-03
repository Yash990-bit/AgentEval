# backend/app/conflict/severity.py
"""Severity scoring for conflicts.
Implements the exact formula specified by the user.
"""

def compute_severity(
    resource_impact: float,
    goal_criticality: float,
    trust_damage: float,
    agents_affected: int,
    total_agents: int,
) -> float:
    """Calculate severity score (0.0 – 1.0).

    severity = (0.4 × resource_impact) + (0.3 × goal_criticality) +
               (0.2 × trust_damage) + (0.1 × spread_factor)
    where spread_factor = agents_affected / total_agents.
    ``resource_impact``, ``goal_criticality`` and ``trust_damage`` are expected
    to be normalized to the range [0, 1].
    """
    if total_agents == 0:
        spread_factor = 0.0
    else:
        spread_factor = agents_affected / total_agents
    severity = (
        0.4 * resource_impact
        + 0.3 * goal_criticality
        + 0.2 * trust_damage
        + 0.1 * spread_factor
    )
    # Clamp to [0, 1]
    return max(0.0, min(1.0, severity))
