"""
Tests for Genetic Algorithm
"""

import pytest
from ct_x.genetic_orchestrator import GAController
import torch
import torch.nn as nn


class DummyModel(nn.Module):
    """Dummy model for testing"""
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(10, 10)

    def parameters(self):
        return self.linear.parameters()


def dummy_fitness(model, phi, efficiency):
    """Dummy fitness function"""
    return phi * 0.5 + efficiency * 0.5


@pytest.fixture
def ga_controller():
    """Create GA controller"""
    return GAController(
        population_size=10,
        fitness_function=dummy_fitness,
        mutation_rate=0.1
    )


def test_ga_initialization(ga_controller):
    """Test GA initializes correctly"""
    assert len(ga_controller.population) == 10
    assert ga_controller.generation == 0


def test_population_has_valid_genomes(ga_controller):
    """Test population contains valid genomes"""
    for genome in ga_controller.population:
        assert "mamba_ratio" in genome
        assert "quantum_depth" in genome
        assert "sparsity_ratio" in genome
        assert 0.06 <= genome["mamba_ratio"] <= 0.12
        assert genome["quantum_depth"] in [4, 6, 8, 10]


def test_evaluate_and_evolve(ga_controller):
    """Test evaluation and evolution"""
    model = DummyModel()

    # Run several evaluations
    for i in range(15):
        ga_controller.evaluate_and_evolve(model, phi=0.5 + i*0.01)

    assert ga_controller.generation == 15


def test_crossover(ga_controller):
    """Test crossover operation"""
    parent1 = ga_controller.population[0]
    parent2 = ga_controller.population[1]

    child = ga_controller._crossover(parent1, parent2)

    # Child should have keys from parents
    assert "mamba_ratio" in child
    assert "quantum_depth" in child


def test_mutation(ga_controller):
    """Test mutation operation"""
    original = ga_controller.population[0].copy()
    mutated = ga_controller._mutate(original)

    # Some values may have changed (probabilistic)
    # At minimum, structure should be preserved
    assert "mamba_ratio" in mutated
    assert 0.06 <= mutated["mamba_ratio"] <= 0.12


def test_get_best_genome(ga_controller):
    """Test retrieving best genome"""
    # Set some fitness values
    for i, genome in enumerate(ga_controller.population):
        genome["fitness"] = i * 0.1

    best = ga_controller.get_best_genome()
    assert best["fitness"] == (len(ga_controller.population) - 1) * 0.1


def test_population_stats(ga_controller):
    """Test population statistics"""
    # Set fitness values
    for i, genome in enumerate(ga_controller.population):
        genome["fitness"] = i * 0.1

    stats = ga_controller.get_population_stats()

    assert "mean_fitness" in stats
    assert "max_fitness" in stats
    assert "min_fitness" in stats
    assert "generation" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
