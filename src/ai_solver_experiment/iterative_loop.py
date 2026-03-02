"""
Iterative Loop — Propose / Evaluate / Feedback / Refine cycle.

Runs a fixed number of iterations:
  1. AI proposes a VRP solution
  2. Python evaluator scores it
  3. Feedback is formatted and sent back
  4. AI refines the solution
  5. Repeat

Logs every proposal, every score, every violation, every feedback prompt.
No black boxes.
"""

import time
from typing import Dict, Any, List, Optional

from .vrp_instance import VRPInstance
from .ai_proposal_engine import AIProposalEngine
from .evaluator import evaluate_solution, format_feedback

# Max conversation history rounds to keep (each round = 1 assistant + 1 user msg)
# Prevents context window overflow at iteration 30+ with n=200 instances
MAX_HISTORY_TURNS = 5  # keeps last 10 messages


def run_ai_loop(
    instance: VRPInstance,
    engine: AIProposalEngine,
    max_iterations: int = 50,
    calibrated: bool = False,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Run the iterative AI proposal loop.

    Args:
        instance: VRP instance to solve
        engine: AI proposal engine (handles LLM calls)
        max_iterations: fixed iteration budget
        calibrated: whether to use ECP calibration
        verbose: print progress

    Returns:
        dict with:
          - iteration_log: list of per-iteration records
          - best_result: best evaluation seen
          - best_routes: routes of best solution
          - best_iteration: which iteration found the best
          - total_time_s: wall clock time
          - engine_stats: LLM call statistics
          - parse_failures: count of unparseable LLM responses
          - condition: "calibrated" or "uncalibrated"
    """
    mode_label = "calibrated" if calibrated else "uncalibrated"
    if verbose:
        print(f"\n{'='*60}")
        print(f"  AI Loop: {mode_label} | {instance.name} | {max_iterations} iterations")
        print(f"{'='*60}")

    iteration_log = []
    conversation_history = []
    best_result = None
    best_routes = None
    best_iteration = -1
    parse_failures = 0

    t_start = time.time()

    for it in range(1, max_iterations + 1):
        # Build feedback from previous iteration
        feedback = ""
        if iteration_log:
            last = iteration_log[-1]
            feedback = format_feedback(last["eval"], it - 1)

        # Get AI proposal
        proposal = engine.propose(
            instance=instance,
            iteration=it,
            feedback=feedback,
            calibrated=calibrated,
            conversation_history=conversation_history if it > 1 else None,
        )

        routes = proposal["routes"]

        if routes is None:
            parse_failures += 1
            if verbose:
                print(f"  iter {it:3d}: PARSE FAILURE")

            # Log the failure
            iteration_log.append({
                "iteration": it,
                "routes": [],
                "eval": {
                    "distance": float("inf"),
                    "feasible": False,
                    "fitness": float("inf"),
                    "overload": 0,
                    "loads": [],
                    "violations": [{"type": "parse_failure"}],
                    "served_customers": 0,
                    "missing_customers": list(range(instance.n_customers)),
                    "duplicate_customers": [],
                },
                "fitness": float("inf"),
                "raw_response": proposal["raw_response"],
                "latency_s": proposal["latency_s"],
                "parse_success": False,
            })

            # Add failed attempt to conversation for context
            conversation_history.append(
                {"role": "assistant", "content": proposal["raw_response"]}
            )
            conversation_history.append(
                {"role": "user", "content": (
                    "Your previous response could not be parsed as valid JSON. "
                    "Please output ONLY a JSON object with the key 'routes' "
                    "containing a list of lists of 0-indexed customer IDs."
                )}
            )
            # Cooldown after parse failure to avoid 429 death spiral
            time.sleep(30)
            continue

        # Evaluate
        eval_result = evaluate_solution(
            routes=routes,
            depot=instance.depot,
            locations=instance.locations,
            demands=instance.demands,
            capacity=instance.capacity,
            n_customers=instance.n_customers,
        )

        fitness = eval_result["fitness"]

        # Track best
        if best_result is None or fitness < best_result["fitness"]:
            best_result = eval_result
            best_routes = routes
            best_iteration = it

        if verbose:
            feas = "✓" if eval_result["feasible"] else "✗"
            dist = eval_result["distance"]
            print(
                f"  iter {it:3d}: dist={dist:10.2f}  "
                f"fit={fitness:10.2f}  feas={feas}  "
                f"latency={proposal['latency_s']:.1f}s"
            )

        # Log
        iteration_log.append({
            "iteration": it,
            "routes": routes,
            "eval": eval_result,
            "fitness": fitness,
            "raw_response": proposal["raw_response"],
            "latency_s": proposal["latency_s"],
            "parse_success": True,
        })

        # Update conversation history for next iteration
        conversation_history.append(
            {"role": "assistant", "content": proposal["raw_response"]}
        )
        # Trim to sliding window (keep last MAX_HISTORY_TURNS rounds)
        max_msgs = MAX_HISTORY_TURNS * 2
        if len(conversation_history) > max_msgs:
            conversation_history = conversation_history[-max_msgs:]

    total_time = time.time() - t_start

    if verbose:
        best_dist = f"{best_result['distance']:.2f}" if best_result else "N/A"
        best_feas = best_result['feasible'] if best_result else "N/A"
        print(f"\n  Best: iter {best_iteration}, dist={best_dist}, feasible={best_feas}")
        print(f"  Parse failures: {parse_failures}/{max_iterations}")
        print(f"  Total time: {total_time:.1f}s")

    return {
        "iteration_log": iteration_log,
        "best_result": best_result,
        "best_routes": best_routes,
        "best_iteration": best_iteration,
        "total_time_s": total_time,
        "engine_stats": engine.get_stats(),
        "parse_failures": parse_failures,
        "condition": mode_label,
        "instance_name": instance.name,
        "max_iterations": max_iterations,
    }
