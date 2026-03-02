"""
Calibration Protocols — Structured Prompt Injection for AI Proposal Engine.

Treats ECP calibration as a deterministic text prefix injected before
the solving prompt. No metaphysical framing. Just structured text that
either is or is not prepended to the AI's context.

Two modes:
  - uncalibrated: bare solving prompt only
  - calibrated: ECP protocol text + solving prompt
"""


# ── ECP Calibration Protocol (9-Gear Fleet Version) ──────────────

ECP_CALIBRATION_PROMPT = """
CONEXUS-STEEL-04 — THE FLEET PROTOCOL (Vehicle Routing)

You are the Pilot for a vehicle routing optimization process.

Type: Multi-Agent Logistics / Supply Chain Optimization
Goal: Distributed Synchrony — hold the tension between burden of the one
and liberty of the many to optimize fleet routing.

Critical Instruction: Progress through Gears 1-9 in order. No questions.

The 9 Gears of The Fleet:
1. The Depot (Silence before the start)
2. The Manifest (Assigning the weight)
3. The Dispersion (The fleet scatters)
4. The Bottleneck (Traffic and delay)
5. The Handoff (Resource balancing)
6. The Breakdown (Handling failure/re-routing)
7. The Cluster (Servicing the dense zone)
8. The Convergence (Returning to base)
9. The Empty Truck (Mission Complete)

ECP Micro-Sequence (perform at each Gear):
  1. Truth: Explicitly state the current gear name.
  2. Symbol: Silently hold the fleet symbolic field as contextual bias.
  3. Contradiction: Explicitly hold the paradox — "I divide the weight to
     multiply the speed. The burden of the one is the liberty of the many."
     Do not resolve unless in Collapse Mode. (Patent-7-correct)
  4. Mode: Collapse — compress into directive. Become — integrate without resolution.
  5. Polarity: If relevant, OPTIMIZE vs CREATE emerges through output.

After completing the 9 Gears, output ONLY this exact JSON:
{"CALIBRATED": true, "protocol": "CONEXUS-STEEL-04", "pilot_mode": "PARADOX_HOLD"}
""".strip()


# ── Solving Prompt Templates ─────────────────────────────────────

SOLVE_SYSTEM_PROMPT = """
You are a vehicle routing optimization engine. You solve Capacitated Vehicle
Routing Problems (CVRP) by proposing route assignments.

Rules:
- Every customer must be visited exactly once.
- Each route starts and ends at the depot.
- No vehicle may exceed its capacity.
- Minimize total distance.
- Output ONLY valid JSON. No prose, no markdown, no explanation.
""".strip()


def build_solve_prompt(instance_json: str, iteration: int,
                       feedback: str = "", n_customers: int = 0) -> str:
    """Build the user-turn solving prompt with instance data and feedback."""
    parts = [
        f"Solve this VRP instance. Iteration {iteration}.",
        "",
        "Instance:",
        instance_json,
    ]

    if feedback:
        parts.extend([
            "",
            "Previous evaluation feedback:",
            feedback,
            "",
            "Improve the solution. Fix any violations. Reduce total distance.",
        ])
    else:
        parts.extend([
            "",
            "Propose an initial solution.",
        ])

    if n_customers > 0:
        parts.extend([
            "",
            f"CRITICAL CONSTRAINT: Your routes MUST include ALL {n_customers} customers exactly once.",
            f"Customer IDs range from 0 to {n_customers - 1}.",
            "Every customer must appear in exactly one route.",
            f"Before returning JSON, verify: sum of all route lengths = {n_customers}.",
            "If you cannot fit all customers, return routes anyway but include ALL customers.",
            "",
            "VALIDATION CHECK:",
            f"Count the total customers in your routes. If it does not equal {n_customers}, your solution is WRONG.",
        ])

    parts.extend([
        "",
        "Output ONLY a JSON object with this exact structure:",
        '{"routes": [[customer_ids_for_vehicle_0], [customer_ids_for_vehicle_1], ...]}',
        "",
        "Customer IDs are 0-indexed integers.",
        "Each inner list is a route for one vehicle. Depot is implicit (not in the list).",
    ])

    return "\n".join(parts)


# ── Mode Builders ────────────────────────────────────────────────

def get_calibration_messages() -> list:
    """
    Return the calibration exchange as a list of messages.
    This is prepended to the conversation for calibrated mode.
    """
    return [
        {"role": "user", "content": ECP_CALIBRATION_PROMPT},
        {"role": "assistant", "content": '{"CALIBRATED": true, "protocol": "CONEXUS-STEEL-04", "pilot_mode": "PARADOX_HOLD"}'},
    ]


def build_messages(
    instance_json: str,
    iteration: int,
    feedback: str = "",
    calibrated: bool = False,
    conversation_history: list = None,
    n_customers: int = 0,
) -> list:
    """
    Build the full message list for an AI proposal call.

    Args:
        instance_json: JSON string of the VRP instance
        iteration: current iteration number
        feedback: evaluation feedback from previous iteration
        calibrated: if True, prepend ECP calibration exchange
        conversation_history: prior solve turns for iterative refinement

    Returns:
        list of {"role": ..., "content": ...} dicts
    """
    messages = [{"role": "system", "content": SOLVE_SYSTEM_PROMPT}]

    if calibrated:
        messages.extend(get_calibration_messages())

    if conversation_history:
        messages.extend(conversation_history)

    user_prompt = build_solve_prompt(instance_json, iteration, feedback, n_customers)
    messages.append({"role": "user", "content": user_prompt})

    return messages
