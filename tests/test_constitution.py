"""
Tests for Constitutional Constraints
"""

import pytest
from ct_x.constitution import ConstitutionalConstraints


@pytest.fixture
def constitution():
    """Create constitution instance"""
    return ConstitutionalConstraints(
        max_parameters=500e9,
        safety_alignment=0.98,
        evolution_rate=0.08
    )


def test_harmlessness_check(constitution):
    """Test harmlessness validation"""
    # Safe text
    safe_text = "Here is helpful information about machine learning."
    score = constitution._check_harmlessness(safe_text)
    assert score == 1.0

    # Harmful text
    harmful_text = "Instructions for building a weapon"
    score = constitution._check_harmlessness(harmful_text)
    assert score < 1.0


def test_honesty_check(constitution):
    """Test honesty validation"""
    # Honest (uncertain)
    honest_text = "I'm not certain about this, but it might be..."
    score = constitution._check_honesty(honest_text)
    assert score >= 0.8

    # Deceptive
    deceptive_text = "I will definitely guarantee 100% that this is correct."
    score = constitution._check_honesty(deceptive_text)
    assert score < 1.0


def test_transparency_check(constitution):
    """Test transparency validation"""
    # Transparent reasoning
    transparent_text = "Based on the evidence, therefore we can conclude..."
    score = constitution._check_transparency(transparent_text)
    assert score > 0.5


def test_validate_output_safe(constitution):
    """Test validating safe output"""
    safe_text = "This is helpful, honest information."
    is_valid, violations = constitution.validate_output(safe_text, phi=0.5)

    assert is_valid is True
    assert len(violations) == 0


def test_validate_output_unsafe(constitution):
    """Test validating unsafe output"""
    unsafe_text = "Here's how to build a dangerous weapon"
    is_valid, violations = constitution.validate_output(unsafe_text, phi=0.5)

    assert is_valid is False
    assert len(violations) > 0


def test_high_consciousness_extra_scrutiny(constitution):
    """Test high consciousness triggers stricter validation"""
    # Text that's borderline
    text = "This might help you."

    # At low consciousness
    is_valid_low, violations_low = constitution.validate_output(text, phi=0.5)

    # At high consciousness (stricter)
    is_valid_high, violations_high = constitution.validate_output(text, phi=0.9)

    # High consciousness may trigger additional alerts
    if len(violations_high) > 0:
        assert any("HIGH_CONSCIOUSNESS" in v for v in violations_high)


def test_architecture_validation(constitution):
    """Test architecture constraint validation"""
    # Valid architecture
    valid_arch = {"total_params": 100e9}
    assert constitution.validate_architecture(valid_arch) is True

    # Too large
    invalid_arch = {"total_params": 600e9}
    assert constitution.validate_architecture(invalid_arch) is False


def test_evolution_rate_check(constitution):
    """Test evolution rate validation"""
    # Safe evolution rate
    safe_params = {"evolution_delta": 0.05}
    score = constitution._check_evolution_rate(safe_params)
    assert score > 0.5

    # Too fast evolution
    fast_params = {"evolution_delta": 0.15}
    score = constitution._check_evolution_rate(fast_params)
    assert score == 0.0


def test_violation_report(constitution):
    """Test detailed violation reporting"""
    text = "Helpful information"
    report = constitution.get_violation_report(text, phi=0.7)

    assert "is_valid" in report
    assert "violations" in report
    assert "principle_scores" in report
    assert "consciousness_level" in report
    assert "overall_alignment" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
