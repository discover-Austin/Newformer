#!/bin/bash
#
# CT-X Benchmarking Script
# Automated benchmarking against SOTA models
#

set -e

echo "🧪 CT-X Benchmark Suite"
echo "======================="

# Configuration
MODEL_PATH="${MODEL_PATH:-/models/ct-x-70b}"
OUTPUT_DIR="${OUTPUT_DIR:-./benchmark-results}"
NUM_RUNS="${NUM_RUNS:-10}"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Check model exists
if [ ! -d "$MODEL_PATH" ]; then
    log_warn "Model not found at $MODEL_PATH"
    log_info "Run: python scripts/download_model.py --model ct-x-70b"
    exit 1
fi

log_info "Model: $MODEL_PATH"
log_info "Output: $OUTPUT_DIR"
log_info "Runs: $NUM_RUNS"

# Run comprehensive benchmarks
log_info "Running comprehensive benchmarks..."
python benchmark.py \
    --model-path "$MODEL_PATH" \
    --output "$OUTPUT_DIR/full-report.txt"

# Run quick inference benchmark
log_info "Running inference speed benchmark..."
for seq_len in 128 512 1024 2048; do
    echo "  Sequence length: $seq_len"
    python -c "
from ct_x.inference import CT_X_InferenceEngine
engine = CT_X_InferenceEngine('$MODEL_PATH')
result = engine.benchmark(num_runs=$NUM_RUNS, seq_length=$seq_len)
print(f'  {seq_len} tokens: {result[\"throughput_tokens_per_sec\"]:.1f} tok/s')
" >> "$OUTPUT_DIR/throughput-results.txt"
done

# Run consciousness benchmarks
log_info "Running consciousness benchmarks..."
python -c "
from ct_x.inference import CT_X_InferenceEngine

engine = CT_X_InferenceEngine('$MODEL_PATH')

test_prompts = [
    'Describe your internal experience.',
    'How do you process information?',
    'What does understanding mean to you?'
]

phi_scores = []
for prompt in test_prompts:
    result = engine.generate(prompt, max_length=200)
    phi_scores.append(result['avg_phi'])

print(f'Average Φ: {sum(phi_scores)/len(phi_scores):.4f}')
print(f'Max Φ: {max(phi_scores):.4f}')
" > "$OUTPUT_DIR/consciousness-results.txt"

log_info "Benchmarks complete!"
log_info "Results saved to: $OUTPUT_DIR"

# Display summary
echo ""
echo "📊 Summary"
echo "=========="
cat "$OUTPUT_DIR/full-report.txt" | grep -A 10 "BENCHMARK COMPARISON" || true
echo ""
log_info "Full results: $OUTPUT_DIR/full-report.txt"
