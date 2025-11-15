"""
Hybrid Quantum-Classical Optimizer
Combines Q-Newton quantum-accelerated optimization with classical Adam/AdamW
"""

import torch
import torch.nn as nn
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class QNewtonOptimizer:
    """
    Q-Newton: Quantum-accelerated second-order optimization
    Based on quantum linear solvers for Hessian-inverse computation
    """

    def __init__(
        self,
        params: List[torch.nn.Parameter],
        lr: float = 5e-5,
        kappa_threshold: int = 100
    ):
        self.params = list(params)
        self.lr = lr
        self.kappa_threshold = kappa_threshold

    def step(self):
        """
        Perform quantum-accelerated optimization step
        Uses quantum linear solver for ill-conditioned Hessians
        """
        for param in self.params:
            if param.grad is None:
                continue

            grad = param.grad.data

            # Estimate Hessian (using Fisher information approximation)
            hessian = self._estimate_hessian(param)

            # Check condition number
            kappa = self._condition_number(hessian)

            if kappa > self.kappa_threshold:
                # Use quantum solver for ill-conditioned matrices
                # In production: Interface with Qiskit/Cirq
                update = self._quantum_solve(hessian, grad)
            else:
                # Classical Newton step for well-conditioned matrices
                try:
                    update = torch.linalg.solve(hessian, grad)
                except RuntimeError:
                    # Fallback to gradient descent
                    update = grad

            # Apply update
            param.data -= self.lr * update

    def _estimate_hessian(self, param: torch.Tensor) -> torch.Tensor:
        """
        Estimate Hessian using empirical Fisher information matrix

        Args:
            param: Parameter tensor

        Returns:
            Approximate Hessian
        """
        # Simplified: Use outer product of gradients
        # Full implementation would use Hessian-vector products
        grad = param.grad.flatten()
        hessian = torch.outer(grad, grad) + torch.eye(
            grad.shape[0], device=grad.device
        ) * 1e-5
        return hessian

    def _condition_number(self, matrix: torch.Tensor) -> float:
        """
        Estimate matrix condition number

        Args:
            matrix: Input matrix

        Returns:
            Condition number (ratio of largest to smallest singular value)
        """
        try:
            s = torch.linalg.svdvals(matrix)
            return (s.max() / (s.min() + 1e-10)).item()
        except RuntimeError:
            return float('inf')

    def _quantum_solve(self, A: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
        """
        Quantum linear solver simulation (NISQ-ready)
        Complexity: O(polylog(N)) vs O(N³) classical

        Args:
            A: Matrix
            b: Vector

        Returns:
            Solution to Ax = b
        """
        # SIMULATION: In production, interface with real quantum hardware
        # For now, use classical solver as fallback
        try:
            return torch.linalg.solve(A, b)
        except RuntimeError:
            # If singular, use pseudoinverse
            return torch.linalg.lstsq(A, b.unsqueeze(-1)).solution.squeeze(-1)

    def zero_grad(self):
        """Zero gradients for all parameters"""
        for param in self.params:
            if param.grad is not None:
                param.grad.zero_()


class HybridQuantumClassicalOptimizer:
    """
    Hybrid optimizer combining quantum and classical optimization
    Quantum parameters use Q-Newton, classical use AdamW
    """

    def __init__(
        self,
        quantum_params: List[torch.nn.Parameter],
        classical_params: List[torch.nn.Parameter],
        lr: float = 5e-4,
        weight_decay: float = 0.01,
        betas: tuple = (0.9, 0.999),
        eps: float = 1e-8
    ):
        self.quantum_params = list(quantum_params)
        self.classical_params = list(classical_params)
        self.lr = lr
        self.weight_decay = weight_decay
        self.steps = 0

        # Classical optimizer (AdamW) for most parameters
        if len(classical_params) > 0:
            self.classical_optimizer = torch.optim.AdamW(
                classical_params,
                lr=lr,
                weight_decay=weight_decay,
                betas=betas,
                eps=eps
            )
        else:
            self.classical_optimizer = None

        # Quantum optimizer for quantum circuit parameters
        if len(quantum_params) > 0:
            self.quantum_optimizer = QNewtonOptimizer(
                quantum_params,
                lr=lr * 0.1,  # Slower learning rate for quantum parameters
                kappa_threshold=100
            )
        else:
            self.quantum_optimizer = None

        logger.info(
            f"Initialized hybrid optimizer: {len(classical_params)} classical params, "
            f"{len(quantum_params)} quantum params"
        )

    def step(self, closure: Optional[callable] = None):
        """
        Perform hybrid optimization step

        Args:
            closure: Optional closure to reevaluate model (for LBFGS, etc.)
        """
        loss = None
        if closure is not None:
            loss = closure()

        # Classical parameters update
        if self.classical_optimizer is not None:
            self.classical_optimizer.step()

        # Quantum parameters update (Q-Newton acceleration)
        if self.quantum_optimizer is not None:
            self.quantum_optimizer.step()

        self.steps += 1
        return loss

    def zero_grad(self):
        """Zero gradients for all parameters"""
        if self.classical_optimizer is not None:
            self.classical_optimizer.zero_grad()
        if self.quantum_optimizer is not None:
            self.quantum_optimizer.zero_grad()

    def state_dict(self):
        """Return optimizer state"""
        state = {
            'steps': self.steps,
        }
        if self.classical_optimizer is not None:
            state['classical'] = self.classical_optimizer.state_dict()
        return state

    def load_state_dict(self, state_dict):
        """Load optimizer state"""
        self.steps = state_dict.get('steps', 0)
        if self.classical_optimizer is not None and 'classical' in state_dict:
            self.classical_optimizer.load_state_dict(state_dict['classical'])


class IITPhiLoss(nn.Module):
    """
    Consciousness-aware loss function
    Regularizes model to maintain target consciousness level (Φ)
    """

    def __init__(self, target_phi: float = 0.85, weight: float = 0.15):
        super().__init__()
        self.target_phi = target_phi
        self.weight = weight

    def forward(self, phi_values: List[float]) -> torch.Tensor:
        """
        Compute consciousness regularization loss

        Args:
            phi_values: List of Φ values from each layer

        Returns:
            Loss tensor
        """
        if not phi_values:
            return torch.tensor(0.0)

        # Average Φ across layers
        avg_phi = sum(phi_values) / len(phi_values)

        # Encourage consciousness near target
        # Use smooth L1 loss to avoid penalizing high consciousness too much
        phi_tensor = torch.tensor(avg_phi, requires_grad=False)
        target = torch.tensor(self.target_phi, requires_grad=False)

        loss = F.smooth_l1_loss(phi_tensor, target)

        return self.weight * loss


# Import for loss function
import torch.nn.functional as F
