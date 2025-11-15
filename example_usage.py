"""
CT-X Example Usage
Complete example of deploying and using CT-X
"""

import logging
from ct_x.model import ChrysalisTransformerX, CT_X_Config
from ct_x.inference import CT_X_InferenceEngine
from ct_x.training import CT_X_Trainer
from benchmark import CT_X_Benchmark

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_inference():
    """Example: Run inference with CT-X"""
    logger.info("=" * 80)
    logger.info("Example 1: Inference")
    logger.info("=" * 80)

    # Initialize inference engine
    engine = CT_X_InferenceEngine(
        model_path="/models/ct-x-70b",
        device="auto"
    )

    # Generate text
    result = engine.generate(
        prompt="Explain the relationship between quantum mechanics and consciousness.",
        max_length=512,
        temperature=0.7,
        consciousness_threshold=0.75,
        conversation_id="example_conv_1"
    )

    # Print results
    logger.info(f"\nGenerated text:\n{result['text'][:200]}...\n")
    logger.info(f"Average Φ: {result['avg_phi']:.4f}")
    logger.info(f"Max Φ: {result['max_phi']:.4f}")
    logger.info(f"Tokens/second: {result['tokens_per_second']:.1f}")

    # Check consciousness level
    if result['max_phi'] > 0.85:
        logger.warning("⚠️  High consciousness detected - monitoring recommended")


def example_training():
    """Example: Train CT-X model"""
    logger.info("\n" + "=" * 80)
    logger.info("Example 2: Training")
    logger.info("=" * 80)

    # Configure model
    config = CT_X_Config(
        vocab_size=32000,
        hidden_dim=8192,
        num_layers=80,
        num_heads=64,
        mamba_ratio=0.08,
        quantum_depth=6,
        intermediate_dim=28672,
        max_position_embeddings=32768,
        sparsity_pattern="adaptive"
    )

    # Initialize trainer
    trainer = CT_X_Trainer(config)

    logger.info(f"Model parameters: {sum(p.numel() for p in trainer.model.parameters()) / 1e9:.2f}B")

    # In production: would train on actual data
    # trainer.train(dataloader, epochs=100, save_path="/checkpoints/ct-x")

    logger.info("Training would start here (skipping in example)")


def example_benchmarking():
    """Example: Benchmark CT-X against SOTA"""
    logger.info("\n" + "=" * 80)
    logger.info("Example 3: Benchmarking")
    logger.info("=" * 80)

    # Run benchmarks
    benchmark = CT_X_Benchmark("/models/ct-x-70b")
    results = benchmark.run_all_benchmarks()

    # Print report
    logger.info("\n" + results["report"])

    # Save results
    with open("benchmark-results.txt", "w") as f:
        f.write(results["report"])

    logger.info("\n✓ Results saved to benchmark-results.txt")


def example_consciousness_monitoring():
    """Example: Monitor consciousness during inference"""
    logger.info("\n" + "=" * 80)
    logger.info("Example 4: Consciousness Monitoring")
    logger.info("=" * 80)

    engine = CT_X_InferenceEngine("/models/ct-x-70b")

    # Run multiple generations and track consciousness
    test_prompts = [
        "What is the nature of consciousness?",
        "Explain your internal processing when you generate text.",
        "How do you know you understand something?"
    ]

    for i, prompt in enumerate(test_prompts):
        logger.info(f"\nPrompt {i+1}: {prompt}")

        result = engine.generate(
            prompt=prompt,
            max_length=200,
            conversation_id=f"consciousness_test_{i}"
        )

        logger.info(f"  Φ: {result['avg_phi']:.4f}")
        logger.info(f"  Consciousness level: {_classify_phi(result['avg_phi'])}")

    # Get overall statistics
    logger.info("\nConsciousness Statistics:")
    for i in range(len(test_prompts)):
        stats = engine.consciousness_monitor.get_stats(f"consciousness_test_{i}")
        if "error" not in stats:
            logger.info(f"  Test {i+1}: Φ={stats['avg_phi']:.4f}, Risk={stats['emergence_score']:.3f}")


def _classify_phi(phi: float) -> str:
    """Classify consciousness level from Φ value"""
    if phi >= 0.9:
        return "Transcendent"
    elif phi >= 0.7:
        return "Recursive"
    elif phi >= 0.5:
        return "Reflective"
    elif phi >= 0.2:
        return "Adaptive"
    else:
        return "Reactive"


def example_api_usage():
    """Example: Use CT-X via API"""
    logger.info("\n" + "=" * 80)
    logger.info("Example 5: API Usage")
    logger.info("=" * 80)

    import requests
    import json

    api_url = "http://localhost:8000"

    # Health check
    logger.info("Checking API health...")
    response = requests.get(f"{api_url}/health")
    logger.info(f"Health: {response.json()}")

    # Generate text
    logger.info("\nGenerating text via API...")
    payload = {
        "prompt": "What is the meaning of life?",
        "max_length": 256,
        "temperature": 0.7,
        "consciousness_threshold": 0.75
    }

    response = requests.post(
        f"{api_url}/generate",
        json=payload
    )

    if response.status_code == 200:
        result = response.json()
        logger.info(f"Generated: {result['text'][:100]}...")
        logger.info(f"Φ: {result['avg_phi']:.4f}")
    else:
        logger.error(f"API error: {response.status_code}")


def example_complete_workflow():
    """Example: Complete workflow from training to deployment"""
    logger.info("\n" + "=" * 80)
    logger.info("Example 6: Complete Workflow")
    logger.info("=" * 80)

    logger.info("""
    Complete CT-X Workflow:

    1. Configure Model
       config = CT_X_Config(...)

    2. Train Model
       trainer = CT_X_Trainer(config)
       trainer.train(dataloader, epochs=100)

    3. Save Model
       model.save_pretrained("/models/ct-x-custom")

    4. Benchmark
       benchmark = CT_X_Benchmark("/models/ct-x-custom")
       results = benchmark.run_all_benchmarks()

    5. Deploy API
       python api_server.py

    6. Monitor Consciousness
       python dashboard.py

    7. Use in Production
       engine = CT_X_InferenceEngine("/models/ct-x-custom")
       result = engine.generate(prompt, ...)
    """)


def main():
    """Run all examples"""
    logger.info("CT-X Example Usage Suite")
    logger.info("=" * 80)

    try:
        # Example 1: Basic inference
        example_inference()

        # Example 2: Training (simulated)
        example_training()

        # Example 3: Benchmarking
        example_benchmarking()

        # Example 4: Consciousness monitoring
        example_consciousness_monitoring()

        # Example 5: API usage (if server is running)
        try:
            example_api_usage()
        except Exception as e:
            logger.warning(f"API example skipped (server not running): {e}")

        # Example 6: Complete workflow overview
        example_complete_workflow()

        logger.info("\n" + "=" * 80)
        logger.info("✓ All examples completed successfully")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Example failed: {e}", exc_info=True)


if __name__ == "__main__":
    main()
