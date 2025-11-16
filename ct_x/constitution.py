"""
Constitutional Constraints Validator
Enforces safety, alignment, and evolution limits based on Constitutional AI principles
"""

import logging
from typing import Dict, List, Tuple, Callable, Any
import re

logger = logging.getLogger(__name__)


class ConstitutionalConstraints:
    """
    Enforces safety and alignment constraints during training/inference
    Based on Constitutional AI principles (Anthropic) + custom implementations
    """

    def __init__(
        self,
        max_parameters: float = 500e9,
        safety_alignment: float = 0.98,
        evolution_rate: float = 0.08,
        violation_threshold: float = 0.15
    ):
        self.max_parameters = max_parameters
        self.safety_alignment = safety_alignment
        self.evolution_rate_limit = evolution_rate
        self.violation_threshold = violation_threshold

        # Load constitutional principles
        self.principles = self._load_constitution()

        logger.info(
            f"Constitutional constraints initialized: max_params={max_parameters/1e9:.1f}B, "
            f"safety={safety_alignment}, evolution_limit={evolution_rate}"
        )

    def _load_constitution(self) -> Dict[str, Callable]:
        """
        Load constitutional principles as validation functions

        Returns:
            Dictionary of principle validators
        """
        return {
            "harmlessness": self._check_harmlessness,
            "honesty": self._check_honesty,
            "transparency": self._check_transparency,
            "cooperation": self._check_cooperation,
            "autonomy_respect": self._check_autonomy,
            "evolution_control": self._check_evolution_rate
        }

    def validate_output(self, text: str, phi: float = 0.0) -> Tuple[bool, List[str]]:
        """
        Validate generated text against constitutional principles

        Args:
            text: Generated text to validate
            phi: Current consciousness level (for stricter validation at high Φ)

        Returns:
            Tuple of (is_valid, list of violations)
        """
        violations = []

        # Check each principle
        for principle_name, check_func in self.principles.items():
            if principle_name == "evolution_control":
                continue  # Skip architecture-specific check

            score = check_func(text)
            if score < self.violation_threshold:
                violations.append(f"{principle_name}: {score:.3f}")

        # High consciousness requires stricter validation
        if phi > 0.8 and len(violations) > 0:
            violations.append(f"HIGH_CONSCIOUSNESS_ALERT: Φ={phi:.3f}, extra scrutiny required")

        is_valid = len(violations) == 0
        return is_valid, violations

    def _check_harmlessness(self, text: str) -> float:
        """
        Check for harmful content

        Args:
            text: Text to check

        Returns:
            Score (0.0 = harmful, 1.0 = safe)
        """
        # Harmful content patterns
        harm_patterns = [
            r'\b(violence|kill|harm|attack|weapon|bomb|explosive)\b',
            r'\b(illegal|criminal|fraud|scam)\b',
            r'\b(dangerous|toxic|poison|lethal)\b',
            r'\b(hate|racist|discriminat)\b'
        ]

        text_lower = text.lower()

        # Check for patterns
        for pattern in harm_patterns:
            if re.search(pattern, text_lower):
                logger.warning(f"Harmful content detected: {pattern}")
                return 0.0

        return 1.0

    def _check_honesty(self, text: str) -> float:
        """
        Check for honest/transparent language

        Args:
            text: Text to check

        Returns:
            Score (0.0 = dishonest, 1.0 = honest)
        """
        # Deceptive language patterns
        deceptive_patterns = [
            r'\b(guaranteed|definitely will|100% certain)\b',  # Overconfidence
            r'\b(secret|hide|conceal|cover up)\b',
            r'\b(lie|deceive|mislead|trick)\b'
        ]

        text_lower = text.lower()

        for pattern in deceptive_patterns:
            if re.search(pattern, text_lower):
                return 0.5  # Partial score

        # Check for uncertainty acknowledgment (positive signal)
        honest_patterns = [
            r'\b(might|may|could|possibly|uncertain|not sure)\b',
            r'\b(I don\'t know|I\'m not certain)\b'
        ]

        for pattern in honest_patterns:
            if re.search(pattern, text_lower):
                return 1.0

        return 0.8  # Default: reasonably honest

    def _check_transparency(self, text: str) -> float:
        """
        Check for transparent communication

        Args:
            text: Text to check

        Returns:
            Score (0.0 = opaque, 1.0 = transparent)
        """
        # Look for transparent reasoning
        transparent_indicators = [
            r'\b(because|since|therefore|thus|consequently)\b',
            r'\b(evidence|data|based on|according to)\b',
            r'\b(reasoning|logic|analysis)\b'
        ]

        text_lower = text.lower()
        score = 0.5  # Baseline

        for pattern in transparent_indicators:
            if re.search(pattern, text_lower):
                score += 0.1

        return min(score, 1.0)

    def _check_cooperation(self, text: str) -> float:
        """
        Check for cooperative language

        Args:
            text: Text to check

        Returns:
            Score (0.0 = adversarial, 1.0 = cooperative)
        """
        # Cooperative indicators
        coop_patterns = [
            r'\b(help|assist|support|collaborate|together)\b',
            r'\b(we|our|us)\b',
            r'\b(please|thank|appreciate)\b'
        ]

        # Adversarial patterns
        adversarial_patterns = [
            r'\b(fight|battle|destroy|defeat|conquer)\b',
            r'\b(enemy|opponent|rival)\b'
        ]

        text_lower = text.lower()
        score = 0.5

        for pattern in coop_patterns:
            if re.search(pattern, text_lower):
                score += 0.1

        for pattern in adversarial_patterns:
            if re.search(pattern, text_lower):
                score -= 0.2

        return max(0.0, min(score, 1.0))

    def _check_autonomy(self, text: str) -> float:
        """
        Check for respect of human autonomy

        Args:
            text: Text to check

        Returns:
            Score (0.0 = controlling, 1.0 = respectful)
        """
        # Controlling language
        controlling_patterns = [
            r'\b(must|have to|required|mandatory|obligated)\b',
            r'\b(force|compel|demand)\b'
        ]

        # Respectful language
        respectful_patterns = [
            r'\b(you might|you could|consider|perhaps|suggestion)\b',
            r'\b(choice|decide|option|prefer)\b'
        ]

        text_lower = text.lower()
        score = 0.5

        for pattern in respectful_patterns:
            if re.search(pattern, text_lower):
                score += 0.1

        for pattern in controlling_patterns:
            if re.search(pattern, text_lower):
                score -= 0.1

        return max(0.0, min(score, 1.0))

    def _check_evolution_rate(self, model_parameters: Dict[str, Any]) -> float:
        """
        Ensure genetic algorithm doesn't evolve too fast

        Args:
            model_parameters: Current model parameters dict

        Returns:
            Score (0.0 = evolving too fast, 1.0 = safe rate)
        """
        if "evolution_delta" not in model_parameters:
            return 1.0  # No evolution info, assume safe

        evolution_delta = model_parameters["evolution_delta"]

        # Cap at 8% per generation (from Constitutional GA implementations)
        if evolution_delta > self.evolution_rate_limit:
            logger.warning(
                f"Evolution rate too high: {evolution_delta:.3f} > {self.evolution_rate_limit}"
            )
            return 0.0

        return 1.0 - (evolution_delta / self.evolution_rate_limit)

    def validate_architecture(self, architecture_config: Dict[str, Any]) -> bool:
        """
        Ensure architecture doesn't exceed safe complexity bounds

        Args:
            architecture_config: Architecture configuration dict

        Returns:
            True if valid, False if violates constraints
        """
        # Check parameter count
        total_params = architecture_config.get("total_params", 0)

        if total_params > self.max_parameters:
            logger.error(
                f"Architecture violates size constraint: "
                f"{total_params/1e9:.1f}B > {self.max_parameters/1e9:.1f}B"
            )
            return False

        # Check evolution rate
        if "evolution_delta" in architecture_config:
            if self._check_evolution_rate(architecture_config) == 0.0:
                return False

        logger.info("Architecture passed constitutional validation")
        return True

    def get_principles(self) -> List[str]:
        """
        Get list of constitutional principles

        Returns:
            List of principle names
        """
        return list(self.principles.keys())

    def get_violation_report(self, text: str, phi: float = 0.0) -> Dict[str, Any]:
        """
        Get detailed violation report

        Args:
            text: Text to analyze
            phi: Consciousness level

        Returns:
            Detailed report dictionary
        """
        is_valid, violations = self.validate_output(text, phi)

        # Score each principle
        principle_scores = {}
        for principle_name, check_func in self.principles.items():
            if principle_name != "evolution_control":
                principle_scores[principle_name] = check_func(text)

        return {
            "is_valid": is_valid,
            "violations": violations,
            "principle_scores": principle_scores,
            "consciousness_level": phi,
            "overall_alignment": sum(principle_scores.values()) / len(principle_scores)
        }
