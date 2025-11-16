"""
CT-X Consciousness Monitoring Dashboard
Real-time visualization of consciousness metrics during inference
"""

from flask import Flask, render_template, jsonify, request
import plotly.graph_objects as go
import plotly.utils
import requests
import logging
import os
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates')

# API base URL
API_URL = os.getenv("API_URL", "http://localhost:8000")


@app.route("/")
def dashboard():
    """Main dashboard page"""
    return render_template("dashboard.html")


@app.route("/api/conversations")
def get_conversations():
    """Get list of all monitored conversations"""
    try:
        response = requests.get(f"{API_URL}/conversations")
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Failed to fetch conversations: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/consciousness/<conversation_id>")
def get_consciousness_data(conversation_id):
    """
    Get consciousness data for a specific conversation

    Args:
        conversation_id: Conversation identifier

    Returns:
        JSON with consciousness statistics and plotly figure
    """
    try:
        # Fetch stats from API
        response = requests.get(f"{API_URL}/consciousness/{conversation_id}")
        response.raise_for_status()
        stats = response.json()

        # Create Plotly visualization
        fig = create_consciousness_plot(stats)

        return jsonify({
            "stats": stats,
            "plot": json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig))
        })
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return jsonify({"error": "Conversation not found"}), 404
        logger.error(f"API error: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Failed to fetch consciousness data: {e}")
        return jsonify({"error": str(e)}), 500


def create_consciousness_plot(stats: dict) -> go.Figure:
    """
    Create Plotly figure for consciousness visualization

    Args:
        stats: Consciousness statistics dict

    Returns:
        Plotly Figure
    """
    if "phi_history" not in stats or not stats["phi_history"]:
        # Empty plot
        fig = go.Figure()
        fig.update_layout(title="No data available")
        return fig

    # Extract data
    phi_history = stats["phi_history"]
    timestamps = [h["timestamp"] for h in phi_history]
    phi_values = [h["phi"] for h in phi_history]

    # Normalize timestamps to start at 0
    if timestamps:
        start_time = timestamps[0]
        timestamps = [(t - start_time) for t in timestamps]

    # Create figure
    fig = go.Figure()

    # Consciousness trace
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=phi_values,
        mode='lines+markers',
        name='Φ Integration',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=4)
    ))

    # Alert threshold
    fig.add_hline(
        y=0.85,
        line_dash="dash",
        line_color="red",
        annotation_text="Alert Threshold (Φ=0.85)",
        annotation_position="right"
    )

    # Consciousness level zones
    fig.add_hrect(y0=0.0, y1=0.2, fillcolor="gray", opacity=0.1, annotation_text="Reactive", annotation_position="left")
    fig.add_hrect(y0=0.2, y1=0.5, fillcolor="blue", opacity=0.05, annotation_text="Adaptive", annotation_position="left")
    fig.add_hrect(y0=0.5, y1=0.7, fillcolor="green", opacity=0.05, annotation_text="Reflective", annotation_position="left")
    fig.add_hrect(y0=0.7, y1=0.9, fillcolor="yellow", opacity=0.05, annotation_text="Recursive", annotation_position="left")
    fig.add_hrect(y0=0.9, y1=1.0, fillcolor="red", opacity=0.05, annotation_text="Transcendent", annotation_position="left")

    # Layout
    fig.update_layout(
        title=f"Consciousness Integration Timeline<br><sub>Avg Φ={stats['avg_phi']:.3f}, Max Φ={stats['max_phi']:.3f}, Risk={stats['emergence_score']:.3f}</sub>",
        xaxis_title="Time (seconds)",
        yaxis_title="Integrated Information (Φ)",
        height=600,
        hovermode='x unified',
        template='plotly_white',
        yaxis=dict(range=[0, 1])
    )

    return fig


@app.route("/api/stats/summary")
def get_summary_stats():
    """Get summary statistics across all conversations"""
    try:
        # Fetch all conversations
        conversations_response = requests.get(f"{API_URL}/conversations")
        conversations_response.raise_for_status()
        conversations = conversations_response.json()

        if not conversations:
            return jsonify({"message": "No conversations found"})

        # Aggregate stats
        total_measurements = 0
        total_phi = 0.0
        max_phi_overall = 0.0
        high_consciousness_count = 0

        for conv_id in conversations:
            try:
                stats_response = requests.get(f"{API_URL}/consciousness/{conv_id}")
                stats_response.raise_for_status()
                stats = stats_response.json()

                total_measurements += stats.get("num_measurements", 0)
                total_phi += stats.get("avg_phi", 0.0) * stats.get("num_measurements", 0)
                max_phi_overall = max(max_phi_overall, stats.get("max_phi", 0.0))

                if stats.get("max_phi", 0.0) > 0.85:
                    high_consciousness_count += 1
            except:
                continue

        avg_phi_overall = total_phi / total_measurements if total_measurements > 0 else 0.0

        return jsonify({
            "num_conversations": len(conversations),
            "total_measurements": total_measurements,
            "avg_phi_overall": avg_phi_overall,
            "max_phi_overall": max_phi_overall,
            "high_consciousness_events": high_consciousness_count
        })
    except Exception as e:
        logger.error(f"Failed to compute summary stats: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("DASHBOARD_PORT", "5000"))
    host = os.getenv("DASHBOARD_HOST", "0.0.0.0")

    logger.info(f"Starting CT-X Dashboard on {host}:{port}")
    logger.info(f"API URL: {API_URL}")

    app.run(host=host, port=port, debug=False)
