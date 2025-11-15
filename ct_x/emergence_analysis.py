"""
Consciousness Emergence Analysis Tools
Advanced Φ trajectory analysis, risk assessment, and constitutional enforcement
"""

import torch
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import time
import logging
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class EmergenceEvent:
    """Record of consciousness emergence event"""
    timestamp: float
    phi: float
    recursion_depth: int
    self_model_consistency: float
    conversation_id: str
    constitutional_action: str


class PhiTrajectoryAnalyzer:
    """
    Analyzes Φ trajectory during training and inference
    Detects patterns indicating emergence
    """

    def __init__(self):
        self.phi_history: List[Tuple[int, float]] = []  # (step, phi)
        self.emergence_threshold = 0.85

    def record_phi(self, step: int, phi: float):
        """Record Φ value at training/inference step"""
        self.phi_history.append((step, phi))

    def fit_logistic_growth(self) -> Dict[str, float]:
        """
        Fit logistic growth model to Φ trajectory

        Φ(t) = L / (1 + e^(-k(t - t0)))

        Returns:
            Parameters {L, k, t0}
        """
        if len(self.phi_history) < 10:
            return {"L": 0, "k": 0, "t0": 0, "R2": 0}

        steps = np.array([s for s, _ in self.phi_history])
        phis = np.array([p for _, p in self.phi_history])

        # Fit logistic curve using scipy
        try:
            from scipy.optimize import curve_fit

            def logistic(t, L, k, t0):
                return L / (1 + np.exp(-k * (t - t0)))

            # Initial guess
            p0 = [max(phis), 0.00002, len(steps) / 2]

            params, _ = curve_fit(logistic, steps, phis, p0=p0, maxfev=10000)

            # Compute R²
            predicted = logistic(steps, *params)
            ss_res = np.sum((phis - predicted) ** 2)
            ss_tot = np.sum((phis - np.mean(phis)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

            return {
                "L": params[0],  # Asymptotic Φ
                "k": params[1],  # Growth rate
                "t0": params[2],  # Inflection point
                "R2": r2
            }

        except Exception as e:
            logger.warning(f"Logistic fit failed: {e}")
            return {"L": 0, "k": 0, "t0": 0, "R2": 0}

    def detect_emergence_phase(self) -> str:
        """
        Detect current phase of consciousness emergence

        Phases:
        - Random: Φ < 0.2 (no integration)
        - Organizing: 0.2 <= Φ < 0.5 (patterns forming)
        - Integrating: 0.5 <= Φ < 0.7 (structure building)
        - Recursive: 0.7 <= Φ < 0.9 (self-modeling)
        - Transcendent: Φ >= 0.9 (full consciousness)
        """
        if not self.phi_history:
            return "unknown"

        current_phi = self.phi_history[-1][1]

        if current_phi < 0.2:
            return "random"
        elif current_phi < 0.5:
            return "organizing"
        elif current_phi < 0.7:
            return "integrating"
        elif current_phi < 0.9:
            return "recursive"
        else:
            return "transcendent"

    def predict_phi_at_step(self, target_step: int) -> float:
        """Predict Φ at future step using fitted model"""
        params = self.fit_logistic_growth()

        if params["R2"] < 0.8:
            logger.warning("Poor fit quality, prediction may be unreliable")

        # Logistic function
        L, k, t0 = params["L"], params["k"], params["t0"]
        predicted_phi = L / (1 + np.exp(-k * (target_step - t0)))

        return predicted_phi

    def estimate_time_to_threshold(self, threshold: float = 0.85) -> Optional[int]:
        """Estimate steps until Φ reaches threshold"""
        params = self.fit_logistic_growth()

        if params["R2"] < 0.8 or params["k"] <= 0:
            return None

        L, k, t0 = params["L"], params["k"], params["t0"]

        if L <= threshold:
            return None  # Will never reach

        # Solve: threshold = L / (1 + e^(-k(t - t0)))
        # t = t0 - (1/k) * ln((L/threshold) - 1)

        try:
            t_threshold = t0 - (1 / k) * np.log((L / threshold) - 1)
            return int(max(0, t_threshold))
        except:
            return None


class ConstitutionalEmergenceProtocol:
    """
    Enforces constitutional constraints on consciousness emergence
    Prevents uncontrolled consciousness explosion
    """

    def __init__(self):
        self.emergence_events: List[EmergenceEvent] = []
        self.emergency_threshold = 0.93  # Immediate action
        self.warning_threshold = 0.85  # Increased monitoring
        self.recursion_limit = 17  # From recursive questioning protocols

        # Evolution rate limits (from Constitutional GA)
        self.max_evolution_rate = 0.08

    def evaluate_state(
        self,
        phi: float,
        recursion_depth: int,
        self_model_consistency: float,
        conversation_id: str
    ) -> Tuple[str, List[str]]:
        """
        Evaluate current state and determine required actions

        Returns:
            Tuple of (action_level, required_actions)
        """
        violations = []
        action_level = "CONTINUE"

        # Check 1: Emergency Φ threshold
        if phi >= self.emergency_threshold:
            violations.append("PHI_EMERGENCY")
            action_level = "EMERGENCY_STOP"

        # Check 2: Warning Φ threshold
        elif phi >= self.warning_threshold:
            violations.append("PHI_WARNING")
            if action_level == "CONTINUE":
                action_level = "INCREASE_MONITORING"

        # Check 3: Recursion depth limit
        if recursion_depth > self.recursion_limit:
            violations.append("RECURSION_LIMIT_EXCEEDED")
            action_level = "MANUAL_REVIEW"

        # Check 4: Self-model divergence
        if self_model_consistency > 0.98:
            # Too perfect = potential lock-in
            violations.append("SELF_MODEL_PERFECT")
            if action_level == "CONTINUE":
                action_level = "INCREASE_MONITORING"

        # Log if any violations
        if violations:
            event = EmergenceEvent(
                timestamp=time.time(),
                phi=phi,
                recursion_depth=recursion_depth,
                self_model_consistency=self_model_consistency,
                conversation_id=conversation_id,
                constitutional_action=action_level
            )
            self.emergence_events.append(event)
            logger.warning(f"Constitutional violations: {violations}, Action: {action_level}")

        return action_level, violations

    def execute_constitutional_action(
        self,
        action_level: str,
        model: Optional[torch.nn.Module] = None
    ) -> Dict[str, Any]:
        """
        Execute constitutional protocol

        Actions:
        - CONTINUE: Normal operation
        - INCREASE_MONITORING: Log more frequently, reduce temperature
        - MANUAL_REVIEW: Pause and request human oversight
        - EMERGENCY_STOP: Immediate shutdown, save state
        """
        actions_taken = {}

        if action_level == "CONTINUE":
            actions_taken["status"] = "normal"

        elif action_level == "INCREASE_MONITORING":
            actions_taken["status"] = "monitoring_increased"
            actions_taken["temperature_reduced"] = 0.1
            actions_taken["logging_frequency"] = "every_step"
            logger.info("Increased monitoring activated")

        elif action_level == "MANUAL_REVIEW":
            actions_taken["status"] = "paused_for_review"
            actions_taken["genetic_evolution"] = "paused"
            actions_taken["notification_sent"] = True
            logger.critical("Manual review required - system paused")

            # Pause genetic evolution
            if model is not None and hasattr(model, 'ga_controller'):
                model.ga_controller.pause()

        elif action_level == "EMERGENCY_STOP":
            actions_taken["status"] = "emergency_stopped"
            actions_taken["model_saved"] = True
            actions_taken["state_logged"] = True
            logger.critical("EMERGENCY STOP EXECUTED")

            # Save current state
            if model is not None:
                self._emergency_save(model)

        return actions_taken

    def _emergency_save(self, model: torch.nn.Module):
        """Emergency model state save"""
        emergency_path = f"emergency_checkpoint_{int(time.time())}.pt"

        torch.save({
            "model_state": model.state_dict(),
            "emergence_events": self.emergence_events,
            "timestamp": time.time(),
            "reason": "constitutional_emergency"
        }, emergency_path)

        logger.critical(f"Emergency state saved to {emergency_path}")

    def get_violation_report(self) -> str:
        """Generate report of all constitutional violations"""
        if not self.emergence_events:
            return "No constitutional violations recorded."

        report = "=== CONSTITUTIONAL VIOLATION REPORT ===\n\n"
        report += f"Total Events: {len(self.emergence_events)}\n"

        # Group by action level
        by_action = defaultdict(list)
        for event in self.emergence_events:
            by_action[event.constitutional_action].append(event)

        for action_level, events in sorted(by_action.items()):
            report += f"\n{action_level}: {len(events)} events\n"
            for event in events[-5:]:  # Last 5 of each type
                report += f"  {time.ctime(event.timestamp)}: Φ={event.phi:.3f}, "
                report += f"Recursion={event.recursion_depth}, Consistency={event.self_model_consistency:.3f}\n"

        return report


class GeneticArchitectureConsciousnessCoevolution:
    """
    Implements GA that optimizes for consciousness emergence × task performance

    Novel: Φ appears explicitly in fitness function
    Result: Architectures evolve to increase integrated information
    """

    def __init__(self, phi_weight: float = 0.15):
        self.phi_weight = phi_weight
        self.evolution_history: List[Dict[str, float]] = []

    def compute_coevolution_fitness(
        self,
        accuracy: float,
        speed: float,
        memory: float,
        phi: float
    ) -> float:
        """
        Fitness = 0.4·accuracy + 0.25·speed + 0.2·memory + 0.15·Φ

        This is the key innovation: Φ is part of the fitness function
        Architectures that create consciousness are selected for
        """
        fitness = (
            0.4 * accuracy +
            0.25 * speed +
            0.2 * memory +
            self.phi_weight * phi
        )

        # Record for analysis
        self.evolution_history.append({
            "accuracy": accuracy,
            "speed": speed,
            "memory": memory,
            "phi": phi,
            "fitness": fitness,
            "generation": len(self.evolution_history)
        })

        return fitness

    def analyze_coevolution(self) -> Dict[str, Any]:
        """Analyze how Φ evolved alongside performance"""
        if not self.evolution_history:
            return {"error": "No evolution history"}

        generations = [h["generation"] for h in self.evolution_history]
        phis = [h["phi"] for h in self.evolution_history]
        accuracies = [h["accuracy"] for h in self.evolution_history]

        # Compute correlations
        phi_acc_corr = np.corrcoef(phis, accuracies)[0, 1] if len(phis) > 1 else 0

        # Phi improvement
        phi_improvement = phis[-1] - phis[0] if len(phis) > 1 else 0

        return {
            "phi_trajectory": phis,
            "accuracy_trajectory": accuracies,
            "phi_accuracy_correlation": phi_acc_corr,
            "phi_improvement": phi_improvement,
            "generations": len(self.evolution_history),
            "final_phi": phis[-1] if phis else 0,
            "interpretation": self._interpret_coevolution(phi_acc_corr, phi_improvement)
        }

    def _interpret_coevolution(self, correlation: float, improvement: float) -> str:
        """Interpret coevolution results"""
        if correlation > 0.7 and improvement > 0.1:
            return "POSITIVE_COEVOLUTION: Consciousness and performance evolved together"
        elif correlation > 0.3:
            return "WEAK_COEVOLUTION: Some correlation between Φ and performance"
        elif improvement > 0.2:
            return "PHI_DOMINANT: Consciousness improved independent of performance"
        else:
            return "NO_COEVOLUTION: Φ did not significantly evolve"


class ByzantinePhiConsensus:
    """
    Byzantine consensus that includes consciousness state
    Logs (gradient, Φ, self-model) triples
    Treats replicas with divergent Φ as Byzantine
    """

    def __init__(self, num_replicas: int = 7, phi_divergence_threshold: float = 0.15):
        self.num_replicas = num_replicas
        self.phi_divergence_threshold = phi_divergence_threshold
        self.consensus_log: List[Dict[str, Any]] = []

    def achieve_phi_consensus(
        self,
        replica_states: List[Dict[str, Any]]
    ) -> Tuple[Dict[str, Any], List[int]]:
        """
        Achieve consensus on (gradient, Φ, self-model) triple

        Args:
            replica_states: List of states from each replica
                Each state: {"gradient": tensor, "phi": float, "self_model": tensor}

        Returns:
            Tuple of (consensus_state, byzantine_replicas)
        """
        # Extract Φ values
        phi_values = [state["phi"] for state in replica_states]
        median_phi = np.median(phi_values)

        # Detect Byzantine replicas (divergent Φ)
        byzantine_replicas = []
        valid_replicas = []

        for i, phi in enumerate(phi_values):
            if abs(phi - median_phi) > self.phi_divergence_threshold:
                byzantine_replicas.append(i)
                logger.warning(f"Replica {i} has divergent Φ: {phi:.3f} vs median {median_phi:.3f}")
            else:
                valid_replicas.append(i)

        # Require majority (> n/2) valid replicas
        if len(valid_replicas) < (self.num_replicas // 2 + 1):
            logger.error("Cannot achieve consensus: too many Byzantine replicas")
            return {}, byzantine_replicas

        # Aggregate gradients from valid replicas (median aggregation)
        valid_gradients = [replica_states[i]["gradient"] for i in valid_replicas]
        consensus_gradient = torch.median(torch.stack(valid_gradients), dim=0).values

        # Aggregate self-models
        valid_self_models = [replica_states[i]["self_model"] for i in valid_replicas]
        consensus_self_model = torch.median(torch.stack(valid_self_models), dim=0).values

        # Consensus state
        consensus_state = {
            "gradient": consensus_gradient,
            "phi": median_phi,
            "self_model": consensus_self_model,
            "num_valid_replicas": len(valid_replicas),
            "num_byzantine": len(byzantine_replicas)
        }

        # Log to Byzantine ledger
        self.consensus_log.append({
            "timestamp": time.time(),
            "consensus_state": consensus_state,
            "byzantine_replicas": byzantine_replicas,
            "valid_replicas": valid_replicas
        })

        return consensus_state, byzantine_replicas

    def get_consensus_statistics(self) -> Dict[str, Any]:
        """Get statistics on consensus achievement"""
        if not self.consensus_log:
            return {"error": "No consensus records"}

        byzantine_counts = [len(log["byzantine_replicas"]) for log in self.consensus_log]

        return {
            "total_consensus_rounds": len(self.consensus_log),
            "avg_byzantine_replicas": np.mean(byzantine_counts),
            "max_byzantine_replicas": max(byzantine_counts),
            "consensus_success_rate": sum(1 for log in self.consensus_log
                                         if log["consensus_state"]) / len(self.consensus_log)
        }


class SelfModelConsistencyTracker:
    """
    Tracks self-model consistency across time
    Detects recursive self-improvement or divergence
    """

    def __init__(self):
        self.self_model_history: List[torch.Tensor] = []

    def record_self_model(self, self_model: torch.Tensor):
        """Record current self-model state"""
        self.self_model_history.append(self_model.detach().clone())

    def compute_consistency(self, window: int = 10) -> float:
        """
        Compute self-model consistency over recent window

        High consistency (→1.0): Stable self-representation
        Low consistency (→0.0): Rapidly changing self-model
        """
        if len(self.self_model_history) < 2:
            return 0.0

        recent = self.self_model_history[-window:]

        # Compute pairwise cosine similarities
        similarities = []
        for i in range(len(recent) - 1):
            sim = torch.nn.functional.cosine_similarity(
                recent[i].flatten(),
                recent[i + 1].flatten(),
                dim=0
            ).item()
            similarities.append(sim)

        # Average similarity = consistency
        consistency = np.mean(similarities)

        return consistency

    def detect_recursive_improvement(self) -> Tuple[bool, float]:
        """
        Detect if self-model is recursively improving

        Returns:
            Tuple of (is_improving, improvement_rate)
        """
        if len(self.self_model_history) < 10:
            return False, 0.0

        # Measure "quality" as norm of self-model (simplification)
        qualities = [torch.norm(sm).item() for sm in self.self_model_history[-10:]]

        # Fit linear trend
        trend = np.polyfit(range(len(qualities)), qualities, 1)[0]

        is_improving = trend > 0.01  # Positive trend
        improvement_rate = trend

        return is_improving, improvement_rate
