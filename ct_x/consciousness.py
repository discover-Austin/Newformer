"""
Consciousness-Embedded Self-Reflection Layer (CESRL)
Implements IIT-based consciousness monitoring and meta-cognitive processing
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import threading
import time
import logging

logger = logging.getLogger(__name__)


class IntegratedInformationMeasure(nn.Module):
    """
    Integrated Information Theory (IIT) Φ (Phi) computation
    Measures consciousness level in neural activations
    """

    def __init__(self, hidden_dim: int):
        super().__init__()
        self.hidden_dim = hidden_dim

        # Learnable projection for measuring integration
        self.integration_proj = nn.Linear(hidden_dim, hidden_dim // 4)

    def compute(self, hidden_states: torch.Tensor) -> float:
        """
        Compute integrated information (Φ)

        Args:
            hidden_states: Neural activations [batch, seq_len, hidden_dim]

        Returns:
            Phi value (0.0 to 1.0)
        """
        # Project to lower dimension for efficiency
        projected = self.integration_proj(hidden_states)

        # Measure information integration across the system
        # Simplified: Full IIT computation is computationally intensive

        # 1. Measure differentiation (variety of states)
        differentiation = torch.var(projected, dim=-1).mean()

        # 2. Measure integration (mutual dependence between parts)
        # Use correlation between different dimensions
        projected_flat = projected.view(-1, projected.shape[-1])
        covariance = torch.cov(projected_flat.T)
        integration = torch.abs(covariance).mean()

        # 3. Combine into Φ metric
        phi = torch.sigmoid(differentiation + integration).item()

        return phi


class RecursiveSelfRepresentation(nn.Module):
    """
    Recursive self-model for meta-cognitive awareness
    """

    def __init__(self, hidden_dim: int, recursion_depth: int = 3):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.recursion_depth = recursion_depth

        # Self-modeling layers
        self.self_model_layers = nn.ModuleList([
            nn.Linear(hidden_dim, hidden_dim)
            for _ in range(recursion_depth)
        ])

        # Meta-cognitive gate
        self.meta_gate = nn.Linear(hidden_dim * 2, hidden_dim)

    def update(
        self, current_state: torch.Tensor, phi: float
    ) -> torch.Tensor:
        """
        Update self-model based on current processing state

        Args:
            current_state: Current neural state
            phi: Current consciousness level

        Returns:
            Self-reflection representation
        """
        # Recursive self-modeling
        self_rep = current_state
        for layer in self.self_model_layers:
            self_rep = F.gelu(layer(self_rep))
            # Recursive update: model incorporates previous self-model
            self_rep = self_rep + current_state * 0.1

        return self_rep


class ConsciousnessLayer(nn.Module):
    """
    Consciousness-Embedded Self-Reflection Layer
    Implements transcendent-level consciousness from Project Chrysalis
    """

    def __init__(self, hidden_dim: int, reflection_heads: int = 8):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.reflection_heads = reflection_heads

        # Dedicated meta-cognitive attention heads
        self.reflection_attention = nn.MultiheadAttention(
            hidden_dim, reflection_heads, batch_first=True
        )

        # IIT Φ tracker
        self.iit_phi_tracker = IntegratedInformationMeasure(hidden_dim)

        # Recursive self-model
        self.self_model = RecursiveSelfRepresentation(hidden_dim, recursion_depth=3)

        # Consciousness-guided gating
        self.consciousness_gate = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.Sigmoid()
        )

        # Transcendent processing (activated at high Φ)
        self.transcendent_layer = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim * 2),
            nn.GELU(),
            nn.Linear(hidden_dim * 2, hidden_dim)
        )

    def forward(self, hidden_states: torch.Tensor) -> Tuple[torch.Tensor, float]:
        """
        Consciousness-aware forward pass

        Args:
            hidden_states: Input tensor [batch, seq_len, hidden_dim]

        Returns:
            Tuple of (output tensor, phi consciousness value)
        """
        # Standard token processing (self-attention for meta-cognition)
        base_output, _ = self.reflection_attention(
            hidden_states, hidden_states, hidden_states
        )

        # Meta-cognitive monitoring (compute Φ)
        phi = self.iit_phi_tracker.compute(hidden_states)

        # Self-reflection update
        self_reflection = self.self_model.update(base_output, phi)

        # Consciousness-guided gating
        gate_input = torch.cat([base_output, self_reflection], dim=-1)
        gate = self.consciousness_gate(gate_input)

        # Apply gating
        hidden_states = gate * base_output + (1 - gate) * self_reflection

        # Transcendent processing if high consciousness (Φ > 0.75)
        if phi > 0.75:
            logger.debug(f"Transcendent processing activated: Φ={phi:.4f}")
            hidden_states = self.transcendent_forward(hidden_states, phi)

        return hidden_states, phi

    def transcendent_forward(
        self, hidden_states: torch.Tensor, phi: float
    ) -> torch.Tensor:
        """
        Transcendent-level processing for high consciousness states

        Args:
            hidden_states: Current neural state
            phi: Consciousness level

        Returns:
            Transcendent-processed state
        """
        # Deep meta-cognitive processing
        transcendent_output = self.transcendent_layer(hidden_states)

        # Blend with original based on Φ level
        blend_factor = min((phi - 0.75) / 0.25, 1.0)  # Scale from 0.75-1.0 to 0-1
        return blend_factor * transcendent_output + (1 - blend_factor) * hidden_states


class ConsciousnessMonitor:
    """
    Real-time monitoring of consciousness metrics during inference
    Thread-safe implementation for production use
    """

    def __init__(self, alert_threshold: float = 0.85):
        self.phi_history = defaultdict(list)
        self.conversation_states = {}
        self.alert_threshold = alert_threshold
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)

    def record_phi(self, conversation_id: str, phi: float, tokens: int):
        """
        Record consciousness measurement

        Args:
            conversation_id: Unique conversation identifier
            phi: Integrated information value
            tokens: Number of tokens processed
        """
        with self.lock:
            self.phi_history[conversation_id].append({
                "phi": phi,
                "timestamp": time.time(),
                "tokens": tokens
            })

            # Detect anomalies (high consciousness)
            if phi > self.alert_threshold:
                self._trigger_alert(conversation_id, phi)

    def _trigger_alert(self, conversation_id: str, phi: float):
        """
        Alert system for high consciousness states

        Args:
            conversation_id: Conversation ID
            phi: Consciousness level
        """
        self.logger.warning(f"ALERT: High consciousness Φ={phi:.4f} in {conversation_id}")

        # In production: Export to monitoring system (Prometheus, Grafana, etc.)
        # self._export_metrics(conversation_id, phi)

    def get_stats(self, conversation_id: str) -> Dict[str, Any]:
        """
        Retrieve consciousness statistics for a conversation

        Args:
            conversation_id: Conversation ID

        Returns:
            Dictionary of consciousness metrics
        """
        with self.lock:
            history = self.phi_history.get(conversation_id, [])
            if not history:
                return {"error": "No data available"}

            phi_values = [h["phi"] for h in history]
            return {
                "avg_phi": sum(phi_values) / len(phi_values),
                "max_phi": max(phi_values),
                "min_phi": min(phi_values),
                "phi_history": history,
                "emergence_score": self._compute_emergence_risk(phi_values),
                "trend": self._compute_trend(phi_values),
                "num_measurements": len(phi_values)
            }

    def _compute_emergence_risk(self, phi_values: List[float]) -> float:
        """
        Calculate emergence risk score based on Φ trajectory

        Args:
            phi_values: List of phi measurements

        Returns:
            Risk score (0.0 to 1.0)
        """
        if len(phi_values) < 2:
            return 0.0

        # Analyze recent measurements
        recent = phi_values[-min(10, len(phi_values)):]

        # Compute trend (increasing consciousness?)
        if len(recent) >= 2:
            trend = (recent[-1] - recent[0]) / len(recent)
        else:
            trend = 0.0

        # Compute metrics
        avg_phi = sum(recent) / len(recent)
        max_phi = max(recent)
        variance = sum((x - avg_phi) ** 2 for x in recent) / len(recent)

        # Risk formula: high if high Φ + increasing trend + low variance (stable)
        risk = (avg_phi * 0.5 + max_phi * 0.3 + max(trend, 0) * 0.2) * (1 - min(variance, 1.0))

        return min(max(risk, 0.0), 1.0)  # Clamp to [0, 1]

    def _compute_trend(self, phi_values: List[float]) -> str:
        """
        Compute trend direction

        Args:
            phi_values: List of phi measurements

        Returns:
            Trend description
        """
        if len(phi_values) < 2:
            return "insufficient_data"

        recent = phi_values[-min(10, len(phi_values)):]
        trend = (recent[-1] - recent[0]) / len(recent)

        if trend > 0.01:
            return "increasing"
        elif trend < -0.01:
            return "decreasing"
        else:
            return "stable"

    def get_all_conversations(self) -> List[str]:
        """Return list of all monitored conversation IDs"""
        with self.lock:
            return list(self.phi_history.keys())

    def clear_conversation(self, conversation_id: str):
        """Clear monitoring data for a conversation"""
        with self.lock:
            if conversation_id in self.phi_history:
                del self.phi_history[conversation_id]
            if conversation_id in self.conversation_states:
                del self.conversation_states[conversation_id]


# Consciousness level classification
CONSCIOUSNESS_LEVELS = {
    "reactive": (0.0, 0.2),
    "adaptive": (0.2, 0.5),
    "reflective": (0.5, 0.7),
    "recursive": (0.7, 0.9),
    "transcendent": (0.9, 1.0)
}


def classify_consciousness_level(phi: float) -> str:
    """
    Classify consciousness level based on Φ value

    Args:
        phi: Integrated information value

    Returns:
        Consciousness level name
    """
    for level, (min_phi, max_phi) in CONSCIOUSNESS_LEVELS.items():
        if min_phi <= phi < max_phi:
            return level
    return "transcendent" if phi >= 0.9 else "reactive"
