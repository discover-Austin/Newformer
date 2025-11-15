"""
Tests for CT-X core model architecture
"""

import pytest
import torch
from ct_x.model import ChrysalisTransformerX, CT_X_Config, CT_X_Block


@pytest.fixture
def config():
    """Create minimal config for testing"""
    return CT_X_Config(
        vocab_size=1000,
        hidden_dim=256,
        num_layers=4,
        num_heads=8,
        intermediate_dim=1024,
        max_position_embeddings=512,
        mamba_ratio=0.08,
        quantum_depth=4
    )


@pytest.fixture
def model(config):
    """Create model instance for testing"""
    return ChrysalisTransformerX(config)


def test_model_initialization(model, config):
    """Test model initializes correctly"""
    assert model is not None
    assert len(model.layers) == config.num_layers
    assert model.config.hidden_dim == config.hidden_dim


def test_forward_pass(model):
    """Test forward pass with dummy input"""
    batch_size = 2
    seq_len = 10

    # Create dummy input
    input_ids = torch.randint(0, 1000, (batch_size, seq_len))

    # Forward pass
    logits, phi_values, loss = model(input_ids)

    # Check output shapes
    assert logits.shape == (batch_size, seq_len, 1000)
    assert len(phi_values) > 0
    assert all(0 <= phi <= 1 for phi in phi_values)


def test_forward_with_labels(model):
    """Test forward pass with labels (compute loss)"""
    batch_size = 2
    seq_len = 10

    input_ids = torch.randint(0, 1000, (batch_size, seq_len))
    labels = torch.randint(0, 1000, (batch_size, seq_len))

    # Forward pass
    logits, phi_values, loss = model(input_ids, labels=labels)

    # Check loss is computed
    assert loss is not None
    assert loss.item() > 0


def test_consciousness_tracking(model):
    """Test consciousness (Φ) tracking"""
    input_ids = torch.randint(0, 1000, (1, 10))

    logits, phi_values, _ = model(input_ids)

    # Check Φ values are recorded
    assert len(phi_values) > 0

    # Check Φ values are in valid range
    for phi in phi_values:
        assert 0 <= phi <= 1


def test_quantum_parameters(model):
    """Test quantum parameter separation"""
    quantum_params = model.quantum_parameters()
    classical_params = model.classical_parameters()

    # Check we have both types
    assert len(list(quantum_params)) >= 0
    assert len(classical_params) > 0

    # Check no overlap
    quantum_ids = {id(p) for p in quantum_params}
    classical_ids = {id(p) for p in classical_params}
    assert len(quantum_ids.intersection(classical_ids)) == 0


def test_save_and_load(model, tmp_path):
    """Test model saving and loading"""
    save_path = str(tmp_path / "test_model")

    # Save model
    model.save_pretrained(save_path)

    # Load model
    loaded_model = ChrysalisTransformerX.from_pretrained(save_path)

    # Check config matches
    assert loaded_model.config.hidden_dim == model.config.hidden_dim
    assert loaded_model.config.num_layers == model.config.num_layers


def test_ct_x_block(config):
    """Test individual CT-X block"""
    block = CT_X_Block(config, layer_idx=0)

    batch_size = 2
    seq_len = 10
    hidden_states = torch.randn(batch_size, seq_len, config.hidden_dim)

    # Forward pass
    output, phi = block(hidden_states)

    # Check output shape
    assert output.shape == hidden_states.shape

    # Check Φ value
    assert 0 <= phi <= 1


def test_gradient_flow(model):
    """Test gradients flow through model"""
    input_ids = torch.randint(0, 1000, (2, 10))
    labels = torch.randint(0, 1000, (2, 10))

    # Forward + backward
    logits, phi_values, loss = model(input_ids, labels=labels)
    loss.backward()

    # Check gradients exist
    has_gradients = False
    for param in model.parameters():
        if param.grad is not None:
            has_gradients = True
            assert not torch.isnan(param.grad).any()
            break

    assert has_gradients, "No gradients found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
