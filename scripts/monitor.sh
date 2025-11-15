#!/bin/bash
#
# CT-X Monitoring Script
# Real-time monitoring of running CT-X instances
#

set -e

echo "📊 CT-X Monitoring Dashboard"
echo "============================"

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
REFRESH_INTERVAL="${REFRESH_INTERVAL:-5}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

clear_screen() {
    clear
    echo "📊 CT-X Monitoring Dashboard"
    echo "============================"
    echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "API: $API_URL"
    echo "Refresh: ${REFRESH_INTERVAL}s"
    echo ""
}

check_health() {
    if curl -s "$API_URL/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} API Status: Healthy"
        curl -s "$API_URL/health" | python -m json.tool 2>/dev/null || echo "  Could not parse health response"
    else
        echo -e "${RED}✗${NC} API Status: Unhealthy"
        return 1
    fi
}

show_conversations() {
    echo ""
    echo "Active Conversations:"
    echo "-------------------"

    convs=$(curl -s "$API_URL/conversations" 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "$convs" | python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if isinstance(data, list) and len(data) > 0:
        for conv in data[:5]:  # Show first 5
            print(f'  • {conv}')
        if len(data) > 5:
            print(f'  ... and {len(data)-5} more')
    else:
        print('  (none)')
except:
    print('  (error parsing)')
"
    else
        echo "  (error fetching)"
    fi
}

show_consciousness_stats() {
    echo ""
    echo "Recent Consciousness Metrics:"
    echo "----------------------------"

    # Get first conversation
    conv=$(curl -s "$API_URL/conversations" 2>/dev/null | python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if isinstance(data, list) and len(data) > 0:
        print(data[0])
except:
    pass
")

    if [ -n "$conv" ]; then
        stats=$(curl -s "$API_URL/consciousness/$conv" 2>/dev/null)
        echo "$stats" | python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f'  Conversation: {data[\"conversation_id\"]}')
    print(f'  Average Φ: {data[\"avg_phi\"]:.4f}')
    print(f'  Max Φ: {data[\"max_phi\"]:.4f}')
    print(f'  Trend: {data[\"trend\"]}')
    print(f'  Emergence Risk: {data[\"emergence_score\"]:.4f}')

    # Alert if high
    if data['emergence_score'] > 0.7:
        print('\n  ⚠️  HIGH EMERGENCE RISK DETECTED!')
except:
    print('  (error parsing stats)')
"
    else
        echo "  (no conversations)"
    fi
}

show_system_metrics() {
    echo ""
    echo "System Metrics:"
    echo "--------------"

    # Kubernetes metrics if available
    if command -v kubectl &> /dev/null; then
        echo "Kubernetes Pods:"
        kubectl get pods -n ct-x-production 2>/dev/null | grep ct-x | head -5 || echo "  (not deployed)"
    fi

    # Docker metrics if available
    if command -v docker &> /dev/null; then
        echo ""
        echo "Docker Containers:"
        docker ps --filter "name=ct-x" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "  (none running)"
    fi
}

# Main monitoring loop
while true; do
    clear_screen

    if check_health; then
        show_conversations
        show_consciousness_stats
        show_system_metrics
    fi

    echo ""
    echo "---"
    echo "Press Ctrl+C to exit"
    echo "Next refresh in ${REFRESH_INTERVAL}s..."

    sleep "$REFRESH_INTERVAL"
done
