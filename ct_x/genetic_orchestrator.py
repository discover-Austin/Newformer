"""
Genetic Algorithm Controller for Architecture Evolution
Implements genetic optimization for CT-X hyperparameters
"""

import torch
import random
import logging
from typing import List, Dict, Callable, Any
from copy import deepcopy

logger = logging.getLogger(__name__)


class GAController:
    """
    Genetic Algorithm for architecture evolution
    Optimizes CT-X hyperparameters based on task-specific fitness
    """

    def __init__(
        self,
        population_size: int = 50,
        fitness_function: Callable = None,
        mutation_rate: float = 0.08,
        selection_pressure: float = 0.85,
        crossover_points: int = 3
    ):
        self.population_size = population_size
        self.fitness_function = fitness_function or self._default_fitness
        self.mutation_rate = mutation_rate
        self.selection_pressure = selection_pressure
        self.crossover_points = crossover_points
        self.generation = 0

        # Initialize population
        self.population = self._initialize_population()

        logger.info(
            f"GA Controller initialized: pop_size={population_size}, "
            f"mutation_rate={mutation_rate}"
        )

    def _initialize_population(self) -> List[Dict[str, Any]]:
        """
        Create initial population of architecture configurations

        Returns:
            List of genome dictionaries
        """
        population = []
        for _ in range(self.population_size):
            genome = {
                "mamba_ratio": random.uniform(0.06, 0.12),
                "quantum_depth": random.choice([4, 6, 8, 10]),
                "sparsity_ratio": random.uniform(0.10, 0.20),
                "hidden_dim": random.choice([4096, 6144, 8192, 10240]),
                "num_layers": random.choice([60, 70, 80, 90]),
                "num_heads": random.choice([32, 64, 128]),
                "fitness": 0.0
            }
            population.append(genome)
        return population

    def _default_fitness(
        self, model: torch.nn.Module, phi: float, efficiency: float
    ) -> float:
        """
        Default fitness function

        Args:
            model: The model being evaluated
            phi: Consciousness level
            efficiency: Computational efficiency metric

        Returns:
            Fitness score
        """
        # Weighted combination of objectives
        # In production: measure real perplexity, speed, memory
        fitness = (
            0.4 * (1.0 - efficiency) +  # Perplexity proxy
            0.25 * efficiency +  # Inference speed
            0.20 * efficiency +  # Memory efficiency
            0.15 * phi  # Consciousness
        )
        return fitness

    def evaluate_and_evolve(self, model: torch.nn.Module, current_phi: float):
        """
        Evaluate current architecture and evolve if needed

        Args:
            model: Current model
            current_phi: Current consciousness level
        """
        # Compute efficiency (simplified)
        efficiency = self._measure_efficiency(model)

        # Compute fitness
        fitness = self.fitness_function(model, current_phi, efficiency)

        # Store in population
        idx = self.generation % self.population_size
        self.population[idx]["fitness"] = fitness

        # Evolve every full generation
        if self.generation > 0 and self.generation % self.population_size == 0:
            self._evolve_population()

        self.generation += 1

    def _measure_efficiency(self, model: torch.nn.Module) -> float:
        """
        Measure model efficiency

        Args:
            model: Model to evaluate

        Returns:
            Efficiency score (0-1)
        """
        # Simplified efficiency metric
        # In production: measure actual FLOPS, memory usage, latency
        total_params = sum(p.numel() for p in model.parameters())
        # Normalize by max params (500B)
        param_efficiency = 1.0 - min(total_params / 500e9, 1.0)
        return param_efficiency

    def _evolve_population(self):
        """
        Perform genetic evolution: selection, crossover, mutation
        """
        logger.info(f"Evolving population at generation {self.generation}")

        # Selection: Keep top performers
        sorted_pop = sorted(
            self.population,
            key=lambda x: x.get("fitness", 0.0),
            reverse=True
        )

        # Selection pressure: top 20% survive
        num_survivors = max(1, int(self.selection_pressure * 0.2 * self.population_size))
        survivors = sorted_pop[:num_survivors]

        logger.info(
            f"Generation {self.generation}: Best fitness = {survivors[0]['fitness']:.4f}"
        )

        # Crossover: Create offspring
        offspring = []
        while len(offspring) < self.population_size - len(survivors):
            # Select two random parents from survivors
            parent1, parent2 = random.sample(survivors, 2)

            # Crossover
            child = self._crossover(parent1, parent2)

            # Mutation
            if random.random() < self.mutation_rate:
                child = self._mutate(child)

            offspring.append(child)

        # New generation
        self.population = survivors + offspring

    def _crossover(self, parent1: Dict, parent2: Dict) -> Dict:
        """
        Multi-point crossover for architecture parameters

        Args:
            parent1: First parent genome
            parent2: Second parent genome

        Returns:
            Child genome
        """
        child = {}
        keys = [k for k in parent1.keys() if k != "fitness"]

        # Multi-point crossover
        for i, key in enumerate(keys):
            # Switch parents at crossover points
            use_parent1 = (i % (len(keys) // self.crossover_points + 1)) % 2 == 0
            child[key] = parent1[key] if use_parent1 else parent2[key]

        child["fitness"] = 0.0  # Reset fitness
        return child

    def _mutate(self, individual: Dict) -> Dict:
        """
        Gaussian mutation with bounded ranges

        Args:
            individual: Genome to mutate

        Returns:
            Mutated genome
        """
        mutation_strength = 0.05

        # Mutate continuous parameters
        if "mamba_ratio" in individual:
            individual["mamba_ratio"] = max(0.06, min(0.12,
                individual["mamba_ratio"] + random.gauss(0, mutation_strength)
            ))

        if "sparsity_ratio" in individual:
            individual["sparsity_ratio"] = max(0.10, min(0.20,
                individual["sparsity_ratio"] + random.gauss(0, mutation_strength)
            ))

        # Mutate discrete parameters
        if random.random() < 0.1:  # 10% chance
            individual["quantum_depth"] = random.choice([4, 6, 8, 10])

        if random.random() < 0.1:
            individual["num_heads"] = random.choice([32, 64, 128])

        return individual

    def get_best_genome(self) -> Dict:
        """
        Get the best genome from current population

        Returns:
            Best genome dictionary
        """
        return max(self.population, key=lambda x: x.get("fitness", 0.0))

    def get_population_stats(self) -> Dict[str, float]:
        """
        Get statistics about current population

        Returns:
            Statistics dictionary
        """
        fitnesses = [ind.get("fitness", 0.0) for ind in self.population]
        return {
            "mean_fitness": sum(fitnesses) / len(fitnesses) if fitnesses else 0.0,
            "max_fitness": max(fitnesses) if fitnesses else 0.0,
            "min_fitness": min(fitnesses) if fitnesses else 0.0,
            "generation": self.generation
        }

    def epoch_end(self):
        """
        Hook called at end of training epoch
        Can trigger population-wide evolution
        """
        stats = self.get_population_stats()
        logger.info(
            f"GA Stats - Gen {stats['generation']}: "
            f"Mean={stats['mean_fitness']:.4f}, Max={stats['max_fitness']:.4f}"
        )
