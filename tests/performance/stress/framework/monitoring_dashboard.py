#!/usr/bin/env python3
"""
Real-time Monitoring Dashboard for Stress Testing
Provides live visualization of test metrics and system resources
"""

import asyncio
import json
import time
import sys
import os
from datetime import datetime
import threading
import queue
from typing import Dict, List, Optional, Any
import psutil
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collect and store metrics for visualization"""
    
    def __init__(self, max_points: int = 1000):
        self.max_points = max_points
        self.metrics_lock = threading.Lock()
        
        # Time series data
        self.timestamps: List[datetime] = []
        self.throughput: List[float] = []
        self.response_times_p50: List[float] = []
        self.response_times_p95: List[float] = []
        self.response_times_p99: List[float] = []
        self.error_rates: List[float] = []
        self.active_clients: List[int] = []
        
        # Resource metrics
        self.cpu_usage: List[float] = []
        self.memory_usage: List[float] = []
        self.connections: List[int] = []
        
        # Error distribution
        self.error_types: Dict[str, int] = {}
        
        # Current test info
        self.current_scenario: Optional[str] = None
        self.test_start_time: Optional[datetime] = None
        
    def add_metrics(self, metrics: Dict[str, Any]):
        """Add new metrics data point"""
        with self.metrics_lock:
            # Add timestamp
            self.timestamps.append(datetime.now())
            
            # Add performance metrics
            self.throughput.append(metrics.get("throughput", 0))
            
            response_times = metrics.get("response_times", {})
            self.response_times_p50.append(response_times.get("p50", 0))
            self.response_times_p95.append(response_times.get("p95", 0))
            self.response_times_p99.append(response_times.get("p99", 0))
            
            self.error_rates.append(metrics.get("error_rate", 0))
            self.active_clients.append(metrics.get("active_clients", 0))
            
            # Add resource metrics
            resources = metrics.get("resources", {})
            self.cpu_usage.append(resources.get("cpu", 0))
            self.memory_usage.append(resources.get("memory", 0))
            self.connections.append(resources.get("connections", 0))
            
            # Update error types
            for error_type, count in metrics.get("error_types", {}).items():
                self.error_types[error_type] = self.error_types.get(error_type, 0) + count
            
            # Trim old data
            if len(self.timestamps) > self.max_points:
                self.timestamps = self.timestamps[-self.max_points:]
                self.throughput = self.throughput[-self.max_points:]
                self.response_times_p50 = self.response_times_p50[-self.max_points:]
                self.response_times_p95 = self.response_times_p95[-self.max_points:]
                self.response_times_p99 = self.response_times_p99[-self.max_points:]
                self.error_rates = self.error_rates[-self.max_points:]
                self.active_clients = self.active_clients[-self.max_points:]
                self.cpu_usage = self.cpu_usage[-self.max_points:]
                self.memory_usage = self.memory_usage[-self.max_points:]
                self.connections = self.connections[-self.max_points:]
    
    def get_dataframe(self) -> pd.DataFrame:
        """Get metrics as pandas DataFrame"""
        with self.metrics_lock:
            if not self.timestamps:
                return pd.DataFrame()
            
            return pd.DataFrame({
                "timestamp": self.timestamps,
                "throughput": self.throughput,
                "response_p50": self.response_times_p50,
                "response_p95": self.response_times_p95,
                "response_p99": self.response_times_p99,
                "error_rate": self.error_rates,
                "active_clients": self.active_clients,
                "cpu_usage": self.cpu_usage,
                "memory_usage": self.memory_usage,
                "connections": self.connections
            })
    
    def get_error_distribution(self) -> Dict[str, int]:
        """Get error type distribution"""
        with self.metrics_lock:
            return self.error_types.copy()
    
    def reset(self):
        """Reset all metrics"""
        with self.metrics_lock:
            self.timestamps.clear()
            self.throughput.clear()
            self.response_times_p50.clear()
            self.response_times_p95.clear()
            self.response_times_p99.clear()
            self.error_rates.clear()
            self.active_clients.clear()
            self.cpu_usage.clear()
            self.memory_usage.clear()
            self.connections.clear()
            self.error_types.clear()
            self.current_scenario = None
            self.test_start_time = None


class MonitoringDashboard:
    """Real-time monitoring dashboard using Dash and Plotly"""
    
    def __init__(self, collector: MetricsCollector, port: int = 8050):
        self.collector = collector
        self.port = port
        self.app = dash.Dash(__name__)
        self.setup_layout()
        self.setup_callbacks()
        
    def setup_layout(self):
        """Setup dashboard layout"""
        self.app.layout = html.Div([
            html.Div([
                html.H1("VoidLight MarkItDown MCP Server - Stress Test Monitor", 
                       style={'textAlign': 'center', 'marginBottom': 30}),
                
                # Test info row
                html.Div([
                    html.Div([
                        html.H3("Current Scenario:", style={'display': 'inline-block', 'marginRight': 10}),
                        html.Span(id='current-scenario', children='None', 
                                style={'fontSize': 20, 'fontWeight': 'bold'})
                    ], style={'width': '50%', 'display': 'inline-block'}),
                    
                    html.Div([
                        html.H3("Test Duration:", style={'display': 'inline-block', 'marginRight': 10}),
                        html.Span(id='test-duration', children='00:00:00', 
                                style={'fontSize': 20, 'fontWeight': 'bold'})
                    ], style={'width': '50%', 'display': 'inline-block', 'textAlign': 'right'})
                ], style={'marginBottom': 20}),
                
                # Key metrics cards
                html.Div([
                    self.create_metric_card("Active Clients", "active-clients", "0"),
                    self.create_metric_card("Throughput", "throughput", "0 req/s"),
                    self.create_metric_card("Error Rate", "error-rate", "0%"),
                    self.create_metric_card("P95 Response", "p95-response", "0ms"),
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': 20}),
                
                # Main charts
                dcc.Graph(id='performance-chart', style={'height': '400px'}),
                dcc.Graph(id='resource-chart', style={'height': '400px'}),
                
                # Error distribution and response time histogram
                html.Div([
                    dcc.Graph(id='error-distribution', style={'width': '48%', 'display': 'inline-block'}),
                    dcc.Graph(id='response-histogram', style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
                ], style={'marginTop': 20}),
                
                # Update interval
                dcc.Interval(id='interval-component', interval=1000, n_intervals=0),
                
                # Hidden div to store data
                html.Div(id='intermediate-value', style={'display': 'none'})
                
            ], style={'padding': '20px', 'backgroundColor': '#f8f9fa'})
        ])
    
    def create_metric_card(self, title: str, id_suffix: str, default_value: str) -> html.Div:
        """Create a metric display card"""
        return html.Div([
            html.H4(title, style={'margin': 0, 'color': '#666'}),
            html.H2(id=f'metric-{id_suffix}', children=default_value, 
                   style={'margin': 0, 'color': '#333'})
        ], style={
            'backgroundColor': 'white',
            'padding': '20px',
            'borderRadius': '8px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            'width': '23%',
            'textAlign': 'center'
        })
    
    def setup_callbacks(self):
        """Setup dashboard callbacks"""
        
        @self.app.callback(
            [Output('current-scenario', 'children'),
             Output('test-duration', 'children'),
             Output('metric-active-clients', 'children'),
             Output('metric-throughput', 'children'),
             Output('metric-error-rate', 'children'),
             Output('metric-p95-response', 'children'),
             Output('performance-chart', 'figure'),
             Output('resource-chart', 'figure'),
             Output('error-distribution', 'figure'),
             Output('response-histogram', 'figure')],
            [Input('interval-component', 'n_intervals')]
        )
        def update_dashboard(n):
            """Update all dashboard components"""
            df = self.collector.get_dataframe()
            
            # Update scenario and duration
            scenario = self.collector.current_scenario or "None"
            
            if self.collector.test_start_time:
                duration = datetime.now() - self.collector.test_start_time
                duration_str = str(duration).split('.')[0]
            else:
                duration_str = "00:00:00"
            
            # Update metrics
            if not df.empty:
                latest = df.iloc[-1]
                active_clients = f"{int(latest['active_clients'])}"
                throughput = f"{latest['throughput']:.1f} req/s"
                error_rate = f"{latest['error_rate']:.1f}%"
                p95_response = f"{latest['response_p95']*1000:.0f}ms"
            else:
                active_clients = "0"
                throughput = "0 req/s"
                error_rate = "0%"
                p95_response = "0ms"
            
            # Create performance chart
            perf_fig = self.create_performance_chart(df)
            
            # Create resource chart
            resource_fig = self.create_resource_chart(df)
            
            # Create error distribution chart
            error_fig = self.create_error_distribution()
            
            # Create response time histogram
            hist_fig = self.create_response_histogram(df)
            
            return (scenario, duration_str, active_clients, throughput, error_rate, p95_response,
                   perf_fig, resource_fig, error_fig, hist_fig)
    
    def create_performance_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create performance metrics chart"""
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            subplot_titles=('Throughput', 'Response Times', 'Error Rate'),
            row_heights=[0.33, 0.33, 0.34]
        )
        
        if not df.empty:
            # Throughput
            fig.add_trace(
                go.Scatter(x=df['timestamp'], y=df['throughput'], 
                          name='Throughput', line=dict(color='blue')),
                row=1, col=1
            )
            
            # Response times
            fig.add_trace(
                go.Scatter(x=df['timestamp'], y=df['response_p50']*1000,
                          name='P50', line=dict(color='green')),
                row=2, col=1
            )
            fig.add_trace(
                go.Scatter(x=df['timestamp'], y=df['response_p95']*1000,
                          name='P95', line=dict(color='orange')),
                row=2, col=1
            )
            fig.add_trace(
                go.Scatter(x=df['timestamp'], y=df['response_p99']*1000,
                          name='P99', line=dict(color='red')),
                row=2, col=1
            )
            
            # Error rate with active clients
            fig.add_trace(
                go.Scatter(x=df['timestamp'], y=df['error_rate'],
                          name='Error Rate', line=dict(color='red')),
                row=3, col=1
            )
            
            # Add active clients on secondary y-axis
            fig.add_trace(
                go.Scatter(x=df['timestamp'], y=df['active_clients'],
                          name='Active Clients', line=dict(color='purple', dash='dash'),
                          yaxis='y2'),
                row=3, col=1
            )
        
        # Update layout
        fig.update_yaxes(title_text="Req/s", row=1, col=1)
        fig.update_yaxes(title_text="Response (ms)", row=2, col=1)
        fig.update_yaxes(title_text="Error %", row=3, col=1)
        fig.update_xaxes(title_text="Time", row=3, col=1)
        
        fig.update_layout(
            height=400,
            showlegend=True,
            title_text="Performance Metrics",
            hovermode='x unified'
        )
        
        return fig
    
    def create_resource_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create resource usage chart"""
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            subplot_titles=('CPU Usage', 'Memory Usage', 'Active Connections'),
            row_heights=[0.33, 0.33, 0.34]
        )
        
        if not df.empty:
            # CPU usage
            fig.add_trace(
                go.Scatter(x=df['timestamp'], y=df['cpu_usage'],
                          name='CPU %', fill='tozeroy', line=dict(color='blue')),
                row=1, col=1
            )
            
            # Memory usage
            fig.add_trace(
                go.Scatter(x=df['timestamp'], y=df['memory_usage'],
                          name='Memory MB', fill='tozeroy', line=dict(color='green')),
                row=2, col=1
            )
            
            # Connections
            fig.add_trace(
                go.Scatter(x=df['timestamp'], y=df['connections'],
                          name='Connections', fill='tozeroy', line=dict(color='orange')),
                row=3, col=1
            )
        
        # Update layout
        fig.update_yaxes(title_text="CPU %", row=1, col=1)
        fig.update_yaxes(title_text="Memory MB", row=2, col=1)
        fig.update_yaxes(title_text="Connections", row=3, col=1)
        fig.update_xaxes(title_text="Time", row=3, col=1)
        
        fig.update_layout(
            height=400,
            showlegend=True,
            title_text="Resource Usage",
            hovermode='x unified'
        )
        
        return fig
    
    def create_error_distribution(self) -> go.Figure:
        """Create error distribution pie chart"""
        error_dist = self.collector.get_error_distribution()
        
        if error_dist:
            fig = go.Figure(data=[
                go.Pie(labels=list(error_dist.keys()), 
                      values=list(error_dist.values()),
                      hole=.3)
            ])
            fig.update_layout(
                title_text="Error Distribution",
                height=300
            )
        else:
            fig = go.Figure()
            fig.add_annotation(
                text="No errors recorded",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            fig.update_layout(
                title_text="Error Distribution",
                height=300
            )
        
        return fig
    
    def create_response_histogram(self, df: pd.DataFrame) -> go.Figure:
        """Create response time histogram"""
        fig = go.Figure()
        
        if not df.empty and len(df) > 10:
            # Get last 1000 response times
            recent_p50 = df['response_p50'].tail(1000) * 1000  # Convert to ms
            recent_p95 = df['response_p95'].tail(1000) * 1000
            
            fig.add_trace(go.Histogram(
                x=recent_p50,
                name='P50 Distribution',
                opacity=0.7,
                nbinsx=30
            ))
            
            fig.add_trace(go.Histogram(
                x=recent_p95,
                name='P95 Distribution',
                opacity=0.7,
                nbinsx=30
            ))
            
            fig.update_layout(
                title_text="Response Time Distribution (last 1000 samples)",
                xaxis_title="Response Time (ms)",
                yaxis_title="Count",
                barmode='overlay',
                height=300
            )
        else:
            fig.add_annotation(
                text="Insufficient data",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            fig.update_layout(
                title_text="Response Time Distribution",
                height=300
            )
        
        return fig
    
    def run(self):
        """Run the dashboard"""
        logger.info(f"Starting dashboard on http://localhost:{self.port}")
        self.app.run_server(host='0.0.0.0', port=self.port, debug=False)


class MetricsSimulator:
    """Simulate metrics for testing the dashboard"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self.running = False
        
    def start(self):
        """Start simulating metrics"""
        self.running = True
        self.collector.current_scenario = "Simulated Load Test"
        self.collector.test_start_time = datetime.now()
        
        thread = threading.Thread(target=self._simulate_loop)
        thread.daemon = True
        thread.start()
        
    def stop(self):
        """Stop simulation"""
        self.running = False
        
    def _simulate_loop(self):
        """Main simulation loop"""
        time_elapsed = 0
        
        while self.running:
            # Simulate varying load
            phase = (time_elapsed // 60) % 4  # 4 phases, 1 minute each
            
            if phase == 0:  # Ramp up
                active_clients = min(100, 10 + time_elapsed)
                base_error_rate = 1
            elif phase == 1:  # Sustained high
                active_clients = 100
                base_error_rate = 2
            elif phase == 2:  # Spike
                active_clients = 200
                base_error_rate = 5
            else:  # Ramp down
                active_clients = max(10, 200 - (time_elapsed % 60) * 3)
                base_error_rate = 3
            
            # Generate metrics
            throughput = active_clients * (10 + np.random.normal(0, 2))
            error_rate = max(0, base_error_rate + np.random.normal(0, 1))
            
            metrics = {
                "throughput": max(0, throughput),
                "response_times": {
                    "p50": 0.05 + np.random.exponential(0.02),
                    "p95": 0.2 + np.random.exponential(0.1),
                    "p99": 0.5 + np.random.exponential(0.3)
                },
                "error_rate": error_rate,
                "active_clients": active_clients,
                "resources": {
                    "cpu": min(100, 20 + active_clients * 0.3 + np.random.normal(0, 5)),
                    "memory": 100 + active_clients * 2 + np.random.normal(0, 10),
                    "connections": active_clients + np.random.randint(-5, 5)
                },
                "error_types": {
                    "Timeout": int(error_rate * throughput * 0.5 / 100),
                    "Connection Error": int(error_rate * throughput * 0.3 / 100),
                    "Invalid Response": int(error_rate * throughput * 0.2 / 100)
                }
            }
            
            self.collector.add_metrics(metrics)
            
            time.sleep(1)
            time_elapsed += 1


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Real-time monitoring dashboard for stress testing")
    parser.add_argument("--port", type=int, default=8050, help="Dashboard port")
    parser.add_argument("--simulate", action="store_true", help="Run with simulated data")
    
    args = parser.parse_args()
    
    # Create metrics collector
    collector = MetricsCollector()
    
    # Create and run dashboard
    dashboard = MonitoringDashboard(collector, port=args.port)
    
    if args.simulate:
        # Start metrics simulation
        simulator = MetricsSimulator(collector)
        simulator.start()
        logger.info("Running with simulated metrics")
    
    try:
        dashboard.run()
    except KeyboardInterrupt:
        logger.info("Shutting down dashboard")
        if args.simulate:
            simulator.stop()


if __name__ == "__main__":
    main()