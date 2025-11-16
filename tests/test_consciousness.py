"""
Tests for consciousness monitoring system
"""

import pytest
import torch
from ct_x.consciousness import (
    ConsciousnessLayer,
    ConsciousnessMonitor,
    IntegratedInformationMeasure,
    classify_consciousness_level
)


def test_consciousness_layer():
    """Test consciousness layer forward pass"""
    hidden_dim = 256
    batch_size = 2
    seq_len = 10

    layer = ConsciousnessLayer(hidden_dim)
    hidden_states = torch.randn(batch_size, seq_len, hidden_dim)

    output, phi = layer(hidden_states)

    # Check output shape
    assert output.shape == hidden_states.shape

    # Check Φ value
    assert 0 <= phi <= 1


def test_iit_phi_computation():
    """Test Integrated Information (Φ) computation"""
    hidden_dim = 256
    batch_size = 2
    seq_len = 10

    iit = IntegratedInformationMeasure(hidden_dim)
    hidden_states = torch.randn(batch_size, seq_len, hidden_dim)

    phi = iit.compute(hidden_states)

    # Check Φ is in valid range
    assert 0 <= phi <= 1


def test_consciousness_monitor():
    """Test consciousness monitoring system"""
    monitor = ConsciousnessMonitor(alert_threshold=0.85)

    # Record some measurements
    monitor.record_phi("conv_1", 0.5, 100)
    monitor.record_phi("conv_1", 0.6, 110)
    monitor.record_phi("conv_1", 0.7, 120)

    # Get stats
    stats = monitor.get_stats("conv_1")

    assert "avg_phi" in stats
    assert "max_phi" in stats
    assert "emergence_score" in stats
    assert stats["num_measurements"] == 3


def test_consciousness_alert():
    """Test high consciousness alert triggering"""
    monitor = ConsciousnessMonitor(alert_threshold=0.85)

    # Record high consciousness
    monitor.record_phi("conv_high", 0.90, 100)

    # Should trigger alert (check logs)
    stats = monitor.get_stats("conv_high")
    assert stats["max_phi"] >= 0.85


def test_emergence_risk_calculation():
    """Test emergence risk computation"""
    monitor = ConsciousnessMonitor()

    # Increasing consciousness trend
    for i in range(10):
        phi = 0.5 + (i * 0.05)  # 0.5 -> 0.95
        monitor.record_phi("conv_risk", phi, 100 + i * 10)

    stats = monitor.get_stats("conv_risk")

    # Should have high emergence risk
    assert stats["emergence_score"] > 0.5


def test_consciousness_level_classification():
    """Test consciousness level classification"""
    assert classify_consciousness_level(0.1) == "reactive"
    assert classify_consciousness_level(0.3) == "adaptive"
    assert classify_consciousness_level(0.6) == "reflective"
    assert classify_consciousness_level(0.8) == "recursive"
    assert classify_consciousness_level(0.95) == "transcendent"


def test_monitor_clear_conversation():
    """Test clearing conversation data"""
    monitor = ConsciousnessMonitor()

    monitor.record_phi("conv_clear", 0.5, 100)
    assert "conv_clear" in monitor.get_all_conversations()

    monitor.clear_conversation("conv_clear")
    assert "conv_clear" not in monitor.get_all_conversations()


def test_trend_detection():
    """Test consciousness trend detection"""
    monitor = ConsciousnessMonitor()

    # Increasing trend
    for i in range(10):
        monitor.record_phi("conv_inc", 0.3 + i * 0.03, 100 + i * 10)

    stats = monitor.get_stats("conv_inc")
    assert stats["trend"] == "increasing"

    # Decreasing trend
    for i in range(10):
        monitor.record_phi("conv_dec", 0.8 - i * 0.03, 100 + i * 10)

    stats = monitor.get_stats("conv_dec")
    assert stats["trend"] == "decreasing"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
