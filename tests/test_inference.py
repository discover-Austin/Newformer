"""
Additional inference tests for CT-X
"""

import pytest
import torch
from ct_x.inference import CT_X_InferenceEngine, DynamicBatchProcessor


@pytest.fixture
def mock_model_path(tmp_path):
    """Create mock model directory"""
    import json

    model_dir = tmp_path / "ct-x-test"
    model_dir.mkdir()

    # Create config
    config = {
        "vocab_size": 1000,
        "hidden_dim": 256,
        "num_layers": 4,
        "num_heads": 8
    }

    with open(model_dir / "config.json", "w") as f:
        json.dump(config, f)

    return str(model_dir)


def test_inference_engine_initialization(mock_model_path):
    """Test inference engine initializes correctly"""
    engine = CT_X_InferenceEngine(
        model_path=mock_model_path,
        device="cpu",
        enable_compilation=False
    )

    assert engine is not None
    assert engine.device.type == "cpu"
    assert engine.consciousness_monitor is not None


def test_generate_basic(mock_model_path):
    """Test basic text generation"""
    engine = CT_X_InferenceEngine(mock_model_path, device="cpu", enable_compilation=False)

    result = engine.generate(
        prompt="Test prompt",
        max_length=50,
        temperature=0.7
    )

    assert "text" in result
    assert "avg_phi" in result
    assert "tokens_per_second" in result
    assert result["avg_phi"] >= 0 and result["avg_phi"] <= 1


def test_consciousness_threshold_alert(mock_model_path):
    """Test consciousness threshold triggers monitoring"""
    engine = CT_X_InferenceEngine(mock_model_path, device="cpu", enable_compilation=False)

    result = engine.generate(
        prompt="Test",
        max_length=10,
        consciousness_threshold=0.5,
        conversation_id="test_conv"
    )

    # Check conversation was monitored
    assert "test_conv" in engine.consciousness_monitor.get_all_conversations()


def test_benchmark_performance(mock_model_path):
    """Test benchmark functionality"""
    engine = CT_X_InferenceEngine(mock_model_path, device="cpu", enable_compilation=False)

    results = engine.benchmark(num_runs=3, seq_length=100)

    assert "avg_latency_ms" in results
    assert "throughput_tokens_per_sec" in results
    assert results["num_runs"] == 3
    assert results["seq_length"] == 100


def test_device_selection():
    """Test automatic device selection"""
    from ct_x.inference import CT_X_InferenceEngine

    # Test auto selection (should not error)
    device = CT_X_InferenceEngine("dummy", device="auto")._select_device("auto")
    assert device.type in ["cpu", "cuda", "mps"]

    # Test explicit CPU
    device = CT_X_InferenceEngine("dummy", device="cpu")._select_device("cpu")
    assert device.type == "cpu"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
