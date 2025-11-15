"""
Quantum Backend Integration for CT-X
Interfaces with real quantum hardware (IBM Quantum, AWS Braket)
Implements quantum-classical hybrid execution
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Optional, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class QuantumBackend:
    """
    Interface to real quantum hardware and classical simulation
    Supports: IBM Quantum (Qiskit), AWS Braket, Classical simulation
    """

    def __init__(
        self,
        provider: str = "simulator",
        backend_name: Optional[str] = None,
        shots: int = 1000
    ):
        self.provider = provider
        self.shots = shots
        self.backend = None

        if provider == "ibmq":
            self._initialize_ibmq(backend_name)
        elif provider == "aws":
            self._initialize_aws_braket(backend_name)
        elif provider == "simulator":
            logger.info("Using classical quantum simulation")
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def _initialize_ibmq(self, backend_name: Optional[str] = None):
        """Initialize IBM Quantum backend"""
        try:
            from qiskit_ibm_runtime import QiskitRuntimeService

            self.service = QiskitRuntimeService(channel="ibm_quantum")

            if backend_name:
                self.backend = self.service.backend(backend_name)
            else:
                # Get least busy backend
                self.backend = self.service.least_busy(simulator=False, operational=True)

            logger.info(f"Connected to IBM Quantum backend: {self.backend.name}")

        except ImportError:
            logger.warning("Qiskit not installed, falling back to simulator")
            self.provider = "simulator"
        except Exception as e:
            logger.error(f"Failed to connect to IBM Quantum: {e}")
            self.provider = "simulator"

    def _initialize_aws_braket(self, backend_name: Optional[str] = None):
        """Initialize AWS Braket backend"""
        try:
            from braket.aws import AwsDevice

            device_arn = backend_name or "arn:aws:braket:::device/quantum-simulator/amazon/sv1"
            self.backend = AwsDevice(device_arn)

            logger.info(f"Connected to AWS Braket device: {device_arn}")

        except ImportError:
            logger.warning("AWS Braket SDK not installed, falling back to simulator")
            self.provider = "simulator"
        except Exception as e:
            logger.error(f"Failed to connect to AWS Braket: {e}")
            self.provider = "simulator"

    def execute_quantum_attention(
        self,
        num_qubits: int,
        circuit_depth: int,
        input_tensor: torch.Tensor
    ) -> torch.Tensor:
        """
        Execute quantum attention circuit

        Args:
            num_qubits: Number of qubits to use
            circuit_depth: Depth of quantum circuit
            input_tensor: Classical input to encode

        Returns:
            Quantum-processed attention weights
        """
        if self.provider == "ibmq":
            return self._execute_ibmq_circuit(num_qubits, circuit_depth, input_tensor)
        elif self.provider == "aws":
            return self._execute_aws_circuit(num_qubits, circuit_depth, input_tensor)
        else:
            return self._simulate_quantum_circuit(num_qubits, circuit_depth, input_tensor)

    def _execute_ibmq_circuit(
        self,
        num_qubits: int,
        circuit_depth: int,
        input_tensor: torch.Tensor
    ) -> torch.Tensor:
        """Execute on IBM Quantum hardware"""
        try:
            from qiskit import QuantumCircuit
            from qiskit.circuit.library import EfficientSU2
            from qiskit_ibm_runtime import Sampler

            # Build parameterized circuit
            circuit = EfficientSU2(num_qubits, entanglement="circular", reps=circuit_depth)

            # Bind parameters from input tensor
            param_values = input_tensor.flatten().cpu().numpy()[:circuit.num_parameters]
            bound_circuit = circuit.assign_parameters(param_values)

            # Add measurements
            bound_circuit.measure_all()

            # Execute on quantum hardware
            sampler = Sampler(self.backend)
            job = sampler.run(bound_circuit, shots=self.shots)
            result = job.result()

            # Convert measurement distribution to tensor
            quasi_dists = result.quasi_dists[0]
            attention_weights = self._counts_to_tensor(quasi_dists, input_tensor.shape[0])

            return attention_weights

        except Exception as e:
            logger.error(f"IBM Quantum execution failed: {e}, falling back to simulation")
            return self._simulate_quantum_circuit(num_qubits, circuit_depth, input_tensor)

    def _execute_aws_circuit(
        self,
        num_qubits: int,
        circuit_depth: int,
        input_tensor: torch.Tensor
    ) -> torch.Tensor:
        """Execute on AWS Braket"""
        try:
            from braket.circuits import Circuit

            # Build circuit
            circuit = Circuit()

            # Encode input as rotation angles
            param_values = input_tensor.flatten().cpu().numpy()

            # Apply parameterized rotations
            for depth in range(circuit_depth):
                for qubit in range(num_qubits):
                    idx = (depth * num_qubits + qubit) % len(param_values)
                    circuit.rx(qubit, param_values[idx])
                    circuit.ry(qubit, param_values[idx] * 0.5)

                # Entanglement layer
                for qubit in range(num_qubits - 1):
                    circuit.cnot(qubit, qubit + 1)

            # Execute
            task = self.backend.run(circuit, shots=self.shots)
            result = task.result()

            # Convert to tensor
            measurements = result.measurement_counts
            attention_weights = self._counts_to_tensor(measurements, input_tensor.shape[0])

            return attention_weights

        except Exception as e:
            logger.error(f"AWS Braket execution failed: {e}, falling back to simulation")
            return self._simulate_quantum_circuit(num_qubits, circuit_depth, input_tensor)

    def _simulate_quantum_circuit(
        self,
        num_qubits: int,
        circuit_depth: int,
        input_tensor: torch.Tensor
    ) -> torch.Tensor:
        """
        Classical simulation of quantum circuit
        Complexity: O(2^n) - only feasible for n < 20
        """
        # Limit qubits for classical simulation
        num_qubits = min(num_qubits, 14)

        state_dim = 2 ** num_qubits
        device = input_tensor.device

        # Initialize quantum state |00...0>
        quantum_state = torch.zeros(state_dim, dtype=torch.complex64, device=device)
        quantum_state[0] = 1.0 + 0.0j

        # Apply parameterized layers
        param_values = input_tensor.flatten()
        param_idx = 0

        for depth in range(circuit_depth):
            # Rotation layer
            for qubit in range(num_qubits):
                if param_idx < len(param_values):
                    angle = param_values[param_idx].item()
                    quantum_state = self._apply_rx_rotation(quantum_state, qubit, angle, num_qubits)
                    param_idx += 1

            # Entanglement layer (circular)
            quantum_state = self._apply_entanglement_circular(quantum_state, num_qubits)

        # Measure expectation values
        probabilities = torch.abs(quantum_state) ** 2

        # Map to attention space
        output_size = input_tensor.shape[0]
        attention_weights = probabilities[:output_size]
        attention_weights = attention_weights / (attention_weights.sum() + 1e-10)

        return attention_weights

    def _apply_rx_rotation(
        self,
        state: torch.Tensor,
        qubit: int,
        angle: float,
        num_qubits: int
    ) -> torch.Tensor:
        """Apply RX rotation on specified qubit"""
        # RX(θ) = cos(θ/2)I - i*sin(θ/2)X
        cos_half = np.cos(angle / 2)
        sin_half = np.sin(angle / 2)

        # Build rotation matrix for full Hilbert space
        state_dim = 2 ** num_qubits
        new_state = torch.zeros_like(state)

        # Apply rotation using bitwise operations
        for i in range(state_dim):
            # Check if qubit is |0> or |1>
            if (i >> qubit) & 1 == 0:  # Qubit is |0>
                # |0> -> cos(θ/2)|0> - i*sin(θ/2)|1>
                new_state[i] += cos_half * state[i]
                flipped_i = i | (1 << qubit)
                new_state[flipped_i] += -1j * sin_half * state[i]
            else:  # Qubit is |1>
                # |1> -> -i*sin(θ/2)|0> + cos(θ/2)|1>
                flipped_i = i & ~(1 << qubit)
                new_state[flipped_i] += -1j * sin_half * state[i]
                new_state[i] += cos_half * state[i]

        return new_state

    def _apply_entanglement_circular(
        self,
        state: torch.Tensor,
        num_qubits: int
    ) -> torch.Tensor:
        """Apply CNOT gates in circular pattern"""
        for qubit in range(num_qubits):
            target = (qubit + 1) % num_qubits
            state = self._apply_cnot(state, qubit, target, num_qubits)
        return state

    def _apply_cnot(
        self,
        state: torch.Tensor,
        control: int,
        target: int,
        num_qubits: int
    ) -> torch.Tensor:
        """Apply CNOT gate"""
        state_dim = 2 ** num_qubits
        new_state = state.clone()

        for i in range(state_dim):
            # If control qubit is 1, flip target qubit
            if (i >> control) & 1:
                flipped_i = i ^ (1 << target)
                new_state[i], new_state[flipped_i] = state[flipped_i], state[i]

        return new_state

    def _counts_to_tensor(
        self,
        counts: Dict[str, int],
        output_size: int
    ) -> torch.Tensor:
        """Convert measurement counts to attention weights"""
        # Extract probabilities from counts
        total = sum(counts.values())

        # Create tensor from binary measurement outcomes
        tensor = torch.zeros(output_size)

        for bitstring, count in counts.items():
            # Convert bitstring to index
            if isinstance(bitstring, str):
                idx = int(bitstring, 2) % output_size
            else:
                idx = bitstring % output_size

            tensor[idx] += count / total

        # Normalize
        tensor = tensor / (tensor.sum() + 1e-10)

        return tensor

    def get_backend_info(self) -> Dict[str, Any]:
        """Get information about quantum backend"""
        info = {
            "provider": self.provider,
            "shots": self.shots,
            "backend_name": None,
            "num_qubits": 0,
            "quantum_volume": 0
        }

        if self.backend is not None:
            if self.provider == "ibmq":
                info["backend_name"] = self.backend.name
                info["num_qubits"] = self.backend.num_qubits
                info["quantum_volume"] = getattr(self.backend, "quantum_volume", 0)
            elif self.provider == "aws":
                info["backend_name"] = str(self.backend)

        return info


class QuantumEnhancedAttentionWithBackend(nn.Module):
    """
    Quantum attention using real quantum backend
    Drop-in replacement for standard attention
    """

    def __init__(
        self,
        hidden_dim: int,
        num_heads: int,
        quantum_backend: QuantumBackend,
        fallback_to_classical: bool = True
    ):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_heads = num_heads
        self.head_dim = hidden_dim // num_heads
        self.quantum_backend = quantum_backend
        self.fallback_to_classical = fallback_to_classical

        # Q, K, V projections
        self.q_proj = nn.Linear(hidden_dim, hidden_dim)
        self.k_proj = nn.Linear(hidden_dim, hidden_dim)
        self.v_proj = nn.Linear(hidden_dim, hidden_dim)
        self.out_proj = nn.Linear(hidden_dim, hidden_dim)

    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Forward pass with quantum-enhanced attention

        Args:
            hidden_states: [batch, seq_len, hidden_dim]
            attention_mask: Optional mask

        Returns:
            Output tensor [batch, seq_len, hidden_dim]
        """
        batch_size, seq_len, _ = hidden_states.shape

        # Project to Q, K, V
        Q = self.q_proj(hidden_states)
        K = self.k_proj(hidden_states)
        V = self.v_proj(hidden_states)

        # Reshape for multi-head attention
        Q = Q.view(batch_size, seq_len, self.num_heads, self.head_dim)
        K = K.view(batch_size, seq_len, self.num_heads, self.head_dim)
        V = V.view(batch_size, seq_len, self.num_heads, self.head_dim)

        # Compute attention scores
        scores = torch.einsum("bqhd,bkhd->bhqk", Q, K) / np.sqrt(self.head_dim)

        # Quantum-enhanced softmax
        if self.training or not self.fallback_to_classical:
            # Use classical during training for speed
            attention_weights = torch.softmax(scores, dim=-1)
        else:
            # Use quantum backend for inference
            try:
                attention_weights = self._quantum_softmax(scores)
            except Exception as e:
                logger.warning(f"Quantum execution failed: {e}, using classical softmax")
                attention_weights = torch.softmax(scores, dim=-1)

        # Apply attention mask if provided
        if attention_mask is not None:
            attention_weights = attention_weights.masked_fill(
                attention_mask.unsqueeze(1).unsqueeze(2) == 0,
                0.0
            )

        # Compute output
        output = torch.einsum("bhqk,bkhd->bqhd", attention_weights, V)
        output = output.reshape(batch_size, seq_len, self.hidden_dim)
        output = self.out_proj(output)

        return output

    def _quantum_softmax(self, scores: torch.Tensor) -> torch.Tensor:
        """Apply quantum-enhanced softmax"""
        batch_size, num_heads, seq_len, _ = scores.shape

        quantum_weights = torch.zeros_like(scores)

        # Process each head with quantum backend
        for b in range(batch_size):
            for h in range(num_heads):
                # Get scores for this head
                head_scores = scores[b, h]  # [seq_len, seq_len]

                # Flatten and normalize for quantum circuit
                input_tensor = head_scores.flatten()
                input_tensor = (input_tensor - input_tensor.min()) / (input_tensor.max() - input_tensor.min() + 1e-10)
                input_tensor = input_tensor * np.pi  # Scale to [0, π]

                # Execute quantum circuit
                quantum_output = self.quantum_backend.execute_quantum_attention(
                    num_qubits=min(14, int(np.ceil(np.log2(len(input_tensor))))),
                    circuit_depth=6,
                    input_tensor=input_tensor
                )

                # Reshape back
                quantum_weights[b, h] = quantum_output[:seq_len * seq_len].reshape(seq_len, seq_len)

        # Normalize
        quantum_weights = quantum_weights / (quantum_weights.sum(dim=-1, keepdim=True) + 1e-10)

        return quantum_weights
