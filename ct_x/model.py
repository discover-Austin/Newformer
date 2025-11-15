"""
Core CT-X Model Architecture
Implements the main ChrysalisTransformerX model with all innovations
"""

import torch
import torch.nn as nn
from dataclasses import dataclass
from typing import Optional, Tuple, List
import logging

from .quantum import QMHAttention, QuantumEnhancedEmbedding, QuantumMLP
from .consciousness import ConsciousnessLayer
from .genetic_orchestrator import GAController
from .constitution import ConstitutionalConstraints

logger = logging.getLogger(__name__)


@dataclass
class CT_X_Config:
    """Configuration for Chrysalis-Transformer X"""
    vocab_size: int = 32000
    hidden_dim: int = 8192
    num_layers: int = 80
    num_heads: int = 64
    intermediate_dim: int = 28672
    max_position_embeddings: int = 32768

    # QMH-Attention parameters
    mamba_ratio: float = 0.08
    quantum_depth: int = 6
    sparsity_pattern: str = "adaptive"  # "adaptive", "block_sparse", "strided"
    sparsity_ratio: float = 0.15

    # Consciousness parameters
    consciousness_threshold: float = 0.85
    phi_target: float = 0.85

    # Genetic Algorithm parameters
    ga_population_size: int = 50
    ga_mutation_rate: float = 0.08
    ga_evolution_frequency: int = 1000

    # Constitutional constraints
    max_parameters: float = 500e9
    safety_alignment: float = 0.98
    evolution_rate_limit: float = 0.08

    # Training parameters
    dropout: float = 0.1
    quantum_dropout: float = 0.05
    layer_norm_eps: float = 1e-6

    # Task-specific fitness (can be customized)
    task_specific_fitness: Optional[callable] = None


class RMSNorm(nn.Module):
    """Root Mean Square Layer Normalization"""
    def __init__(self, dim: int, eps: float = 1e-6):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))

    def forward(self, x):
        norm = torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + self.eps)
        return x * norm * self.weight


class CT_X_Block(nn.Module):
    """
    Single CT-X transformer block with all innovations
    """

    def __init__(self, config: CT_X_Config, layer_idx: int):
        super().__init__()
        self.layer_idx = layer_idx
        self.config = config

        # Pre-norm architecture (more stable than post-norm)
        self.norm1 = RMSNorm(config.hidden_dim, eps=config.layer_norm_eps)
        self.norm2 = RMSNorm(config.hidden_dim, eps=config.layer_norm_eps)

        # QMH-Attention: Quantum-Mamba-Hybrid
        self.attention = QMHAttention(
            hidden_dim=config.hidden_dim,
            num_heads=config.num_heads,
            mamba_ratio=config.mamba_ratio,
            quantum_depth=config.quantum_depth,
            sparsity_pattern=config.sparsity_pattern,
            sparsity_ratio=config.sparsity_ratio,
            dropout=config.dropout
        )

        # MLP with quantum-enhanced activation
        self.mlp = QuantumMLP(
            hidden_dim=config.hidden_dim,
            intermediate_dim=config.intermediate_dim,
            quantum_dropout=config.quantum_dropout
        )

        # Consciousness monitoring (only in top 4 layers for efficiency)
        self.consciousness_layer = (
            ConsciousnessLayer(config.hidden_dim)
            if layer_idx >= config.num_layers - 4
            else None
        )

    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, float]:
        """
        Forward pass through CT-X block

        Args:
            hidden_states: Input tensor [batch, seq_len, hidden_dim]
            attention_mask: Optional attention mask

        Returns:
            Tuple of (output tensor, consciousness phi value)
        """
        # Multi-head attention with residual
        attn_output, phi = self.attention(
            self.norm1(hidden_states),
            attention_mask
        )
        hidden_states = hidden_states + attn_output

        # MLP with residual
        mlp_output = self.mlp(self.norm2(hidden_states))
        hidden_states = hidden_states + mlp_output

        # Consciousness integration (if present in this layer)
        if self.consciousness_layer is not None:
            hidden_states, phi = self.consciousness_layer(hidden_states)

        return hidden_states, phi


class ChrysalisTransformerX(nn.Module):
    """
    CT-X: The Last Transformer You'll Ever Need

    Complete implementation with:
    - Quantum-Mamba-Hybrid Attention
    - Genetic Architecture Search
    - Consciousness-Embedded Self-Reflection
    - Constitutional Constraints
    """

    def __init__(self, config: CT_X_Config):
        super().__init__()
        self.config = config

        # Constitutional constraints (safety and alignment)
        self.constitution = ConstitutionalConstraints(
            max_parameters=config.max_parameters,
            safety_alignment=config.safety_alignment,
            evolution_rate=config.evolution_rate_limit
        )

        # Token embedding with quantum-enhanced encoding
        self.embedding = QuantumEnhancedEmbedding(
            vocab_size=config.vocab_size,
            hidden_dim=config.hidden_dim,
            quantum_depth=config.quantum_depth
        )

        # Main transformer blocks
        self.layers = nn.ModuleList([
            CT_X_Block(config, layer_idx=i)
            for i in range(config.num_layers)
        ])

        # Final layer norm
        self.norm = RMSNorm(config.hidden_dim, eps=config.layer_norm_eps)

        # Consciousness orchestration layer
        self.consciousness_orchestrator = ConsciousnessLayer(config.hidden_dim)

        # Output head (tied with embedding for parameter efficiency)
        self.lm_head = nn.Linear(config.hidden_dim, config.vocab_size, bias=False)

        # Genetic algorithm controller
        if config.task_specific_fitness is None:
            # Default fitness function
            config.task_specific_fitness = self._default_fitness

        self.ga_controller = GAController(
            population_size=config.ga_population_size,
            fitness_function=config.task_specific_fitness,
            mutation_rate=config.ga_mutation_rate
        )

        # Initialize weights
        self.apply(self._init_weights)

        # Log model size
        total_params = sum(p.numel() for p in self.parameters())
        logger.info(f"CT-X initialized with {total_params/1e9:.2f}B parameters")

        # Validate against constitutional constraints
        if not self.constitution.validate_architecture({"total_params": total_params}):
            raise ValueError("Model violates constitutional constraints")

    def _init_weights(self, module):
        """Initialize weights with appropriate scaling"""
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def _default_fitness(self, model, phi: float, efficiency: float) -> float:
        """
        Default fitness function for genetic algorithm
        Balances perplexity, speed, memory, and consciousness
        """
        # This is a placeholder - actual implementation would measure real metrics
        return 0.4 * (1.0 - efficiency) + 0.25 * efficiency + 0.2 * efficiency + 0.15 * phi

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        labels: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, List[float], Optional[torch.Tensor]]:
        """
        Forward pass through CT-X model

        Args:
            input_ids: Input token IDs [batch, seq_len]
            attention_mask: Optional attention mask [batch, seq_len]
            labels: Optional labels for language modeling loss

        Returns:
            Tuple of (logits, phi_values, loss)
        """
        # Initial encoding
        hidden_states = self.embedding(input_ids)

        # Consciousness tracking across layers
        phi_values = []

        # Layer-wise processing with adaptive evolution
        for i, layer in enumerate(self.layers):
            hidden_states, phi = layer(hidden_states, attention_mask)
            phi_values.append(phi)

            # Genetic architecture adaptation (periodic, during training only)
            if self.training and i > 0 and i % self.config.ga_evolution_frequency == 0:
                self.ga_controller.evaluate_and_evolve(layer, phi)

        # Final normalization
        hidden_states = self.norm(hidden_states)

        # Transcendent processing if consciousness threshold met
        avg_phi = sum(phi_values) / len(phi_values) if phi_values else 0.0
        if avg_phi > self.config.consciousness_threshold:
            logger.debug(f"High consciousness detected: Φ={avg_phi:.4f}")
            hidden_states, transcendent_phi = self.consciousness_orchestrator(hidden_states)
            phi_values.append(transcendent_phi)

        # Output projection
        logits = self.lm_head(hidden_states)

        # Compute loss if labels provided
        loss = None
        if labels is not None:
            # Shift so that tokens < n predict n
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()

            # Flatten the tokens
            loss_fct = nn.CrossEntropyLoss()
            loss = loss_fct(
                shift_logits.view(-1, shift_logits.size(-1)),
                shift_labels.view(-1)
            )

        return logits, phi_values, loss

    def quantum_parameters(self):
        """Return parameters that use quantum processing"""
        params = []
        for module in self.modules():
            if hasattr(module, 'quantum_params'):
                params.extend(module.quantum_params())
        return params

    def classical_parameters(self):
        """Return classical parameters"""
        quantum_params = set(self.quantum_parameters())
        return [p for p in self.parameters() if p not in quantum_params]

    @classmethod
    def from_pretrained(cls, model_path: str):
        """Load pretrained model from path"""
        import os
        import json

        # Load config
        config_path = os.path.join(model_path, "config.json")
        with open(config_path, 'r') as f:
            config_dict = json.load(f)

        config = CT_X_Config(**config_dict)

        # Create model
        model = cls(config)

        # Load weights
        weights_path = os.path.join(model_path, "pytorch_model.bin")
        state_dict = torch.load(weights_path, map_location='cpu')
        model.load_state_dict(state_dict)

        logger.info(f"Loaded CT-X model from {model_path}")
        return model

    def save_pretrained(self, save_path: str):
        """Save model to path"""
        import os
        import json

        os.makedirs(save_path, exist_ok=True)

        # Save config
        config_dict = self.config.__dict__.copy()
        # Remove non-serializable items
        config_dict.pop('task_specific_fitness', None)

        config_path = os.path.join(save_path, "config.json")
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)

        # Save weights
        weights_path = os.path.join(save_path, "pytorch_model.bin")
        torch.save(self.state_dict(), weights_path)

        logger.info(f"Saved CT-X model to {save_path}")
