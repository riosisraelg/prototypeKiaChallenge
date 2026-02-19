#!/usr/bin/env python3
"""
Main simulator script for KIA Paint Shop IoT Prototype.

This script orchestrates the entire simulation:
- Loads variable configurations from CSV files
- Generates realistic data values with anomalies
- Detects alarm conditions
- Publishes data to AWS IoT Core via MQTT

Requirements: 1.3, 1.6
"""

import sys
import signal
import time
import logging
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

import yaml

from config_loader import ConfigLoader
from data_generator import DataGenerator
from mqtt_publisher import MQTTPublisher, MQTTConfig
from alarm_simulator import AlarmSimulator


class SimulatorError(Exception):
    """Base exception for simulator errors."""
    pass


class ConfigurationError(SimulatorError):
    """Error in configuration or setup."""
    pass


class Simulator:
    """
    Main simulator orchestrator.
    
    Coordinates all simulator components to generate and publish
    realistic IoT data for the KIA Paint Shop prototype.
    """
    
    def __init__(self, config_path: Path):
        """
        Initialize the simulator.
        
        Args:
            config_path: Path to configuration YAML file
        """
        self.config_path = config_path
        self.config: Optional[Dict[str, Any]] = None
        self.running = False
        self.shutdown_requested = False
        
        # Components
        self.config_loader: Optional[ConfigLoader] = None
        self.data_generator: Optional[DataGenerator] = None
        self.mqtt_publisher: Optional[MQTTPublisher] = None
        self.alarm_simulator: Optional[AlarmSimulator] = None
        
        # Variables
        self.variables = {}
        self.active_variables = []
        
        # Metrics
        self.cycles_completed = 0
        self.total_messages_sent = 0
        self.total_alarms_generated = 0
        self.start_time: Optional[float] = None
        
        # Logger
        self.logger = logging.getLogger(__name__)
    
    def load_configuration(self) -> None:
        """Load configuration from YAML file."""
        self.logger.info(f"Loading configuration from {self.config_path}")
        
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            
            # Validate required sections
            required_sections = ['mqtt', 'simulation']
            for section in required_sections:
                if section not in self.config:
                    raise ConfigurationError(f"Missing required section: {section}")
            
            # Validate MQTT endpoint
            if not self.config['mqtt'].get('endpoint'):
                raise ConfigurationError(
                    "MQTT endpoint not configured. "
                    "Please set mqtt.endpoint in config.yaml"
                )
            
            self.logger.info("Configuration loaded successfully")
            
        except FileNotFoundError:
            raise ConfigurationError(f"Configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in configuration file: {e}")
    
    def setup_logging(self) -> None:
        """Configure logging based on configuration."""
        log_config = self.config.get('logging', {})
        log_level = log_config.get('level', 'INFO')
        log_format = log_config.get('format', 'text')
        log_file = log_config.get('file')
        
        # Set log level
        level = getattr(logging, log_level.upper(), logging.INFO)
        
        # Configure format
        if log_format == 'json':
            formatter = logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
                '"logger": "%(name)s", "message": "%(message)s"}'
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        # Configure handlers
        handlers = []
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)
        
        # File handler (if configured)
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        
        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Add new handlers
        for handler in handlers:
            root_logger.addHandler(handler)
        
        self.logger.info(f"Logging configured: level={log_level}, format={log_format}")
    
    def initialize_components(self) -> None:
        """Initialize all simulator components."""
        self.logger.info("Initializing simulator components...")
        
        # 1. Load variables
        self.logger.info("Loading variable configurations...")
        self.config_loader = ConfigLoader(base_path=self.config_path.parent)
        self.variables = self.config_loader.load_all()
        
        # Get active variables (limit to max_variables if configured)
        max_vars = self.config['simulation'].get('max_variables', 100)
        all_active = self.config_loader.get_active_variables()
        self.active_variables = all_active[:max_vars]
        
        self.logger.info(
            f"Loaded {len(self.variables)} variables, "
            f"using {len(self.active_variables)} active variables"
        )
        
        # 2. Create data generator
        anomaly_prob = self.config['simulation'].get('anomaly_probability', 0.05)
        self.data_generator = DataGenerator(anomaly_probability=anomaly_prob)
        self.logger.info(f"Data generator initialized (anomaly_probability={anomaly_prob})")
        
        # 3. Create alarm simulator
        if self.config['simulation'].get('enable_alarms', True):
            self.alarm_simulator = AlarmSimulator()
            self.logger.info("Alarm simulator initialized")
        else:
            self.logger.info("Alarm detection disabled")
        
        # 4. Create MQTT publisher
        mqtt_config_data = self.config['mqtt']
        mqtt_config = MQTTConfig(
            endpoint=mqtt_config_data['endpoint'],
            port=mqtt_config_data.get('port', 8883),
            cert_path=mqtt_config_data.get('cert_path', 'certs/device.crt'),
            key_path=mqtt_config_data.get('key_path', 'certs/device.key'),
            ca_path=mqtt_config_data.get('ca_path', 'certs/AmazonRootCA1.pem'),
            client_id=mqtt_config_data.get('client_id', 'kia-paintshop-simulator'),
            topic_prefix=mqtt_config_data.get('topic_prefix', 'kia/paintshop'),
            qos=mqtt_config_data.get('qos', 1),
            keep_alive=mqtt_config_data.get('keep_alive', 60)
        )
        
        retry_config = self.config.get('retry', {})
        self.mqtt_publisher = MQTTPublisher(
            config=mqtt_config,
            max_retry_attempts=retry_config.get('max_attempts', 5),
            initial_retry_delay=retry_config.get('initial_delay', 1.0),
            max_retry_delay=retry_config.get('max_delay', 60.0),
            backoff_multiplier=retry_config.get('backoff_multiplier', 2.0)
        )
        
        self.logger.info("MQTT publisher initialized")
        
        self.logger.info("All components initialized successfully")
    
    def connect_mqtt(self) -> None:
        """Connect to AWS IoT Core."""
        self.logger.info("Connecting to AWS IoT Core...")
        
        if not self.mqtt_publisher.connect():
            raise SimulatorError("Failed to connect to AWS IoT Core")
        
        self.logger.info("Connected to AWS IoT Core successfully")
    
    def run(self) -> None:
        """
        Run the main simulation loop.
        
        Generates data for all active variables at configured intervals
        and publishes to AWS IoT Core.
        """
        self.logger.info("Starting simulator...")
        
        # Load configuration
        self.load_configuration()
        
        # Setup logging
        self.setup_logging()
        
        # Initialize components
        self.initialize_components()
        
        # Connect to MQTT
        self.connect_mqtt()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Start simulation
        self.running = True
        self.start_time = time.time()
        interval = self.config['simulation'].get('interval_seconds', 30)
        
        self.logger.info(
            f"Simulation started: {len(self.active_variables)} variables, "
            f"interval={interval}s"
        )
        
        print(f"\n{'='*60}")
        print(f"KIA Paint Shop IoT Simulator")
        print(f"{'='*60}")
        print(f"Variables: {len(self.active_variables)}")
        print(f"Interval: {interval} seconds")
        print(f"Anomaly probability: {self.config['simulation'].get('anomaly_probability', 0.05)}")
        print(f"MQTT endpoint: {self.config['mqtt']['endpoint']}")
        print(f"{'='*60}\n")
        print("Press Ctrl+C to stop\n")
        
        try:
            while self.running and not self.shutdown_requested:
                cycle_start = time.time()
                
                # Run simulation cycle
                self._run_cycle()
                
                # Calculate sleep time to maintain interval
                cycle_duration = time.time() - cycle_start
                sleep_time = max(0, interval - cycle_duration)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    self.logger.warning(
                        f"Cycle took longer than interval: {cycle_duration:.2f}s > {interval}s"
                    )
        
        except Exception as e:
            self.logger.error(f"Error in simulation loop: {e}", exc_info=True)
            raise
        
        finally:
            self.shutdown()
    
    def _run_cycle(self) -> None:
        """Run a single simulation cycle."""
        cycle_num = self.cycles_completed + 1
        
        self.logger.info(f"Starting cycle {cycle_num}")
        
        # Generate data for all active variables
        data_points = self.data_generator.generate_batch(self.active_variables)
        
        # Enrich with alarm information if enabled
        if self.alarm_simulator:
            enriched_payloads = []
            alarm_count = 0
            
            for dp in data_points:
                var = self.variables[dp.variable_id]
                enriched = self.alarm_simulator.enrich_data_point(dp, var)
                enriched_payloads.append(enriched)
                
                if enriched['alarm']['is_alarm']:
                    alarm_count += 1
            
            if alarm_count > 0:
                self.logger.info(f"Cycle {cycle_num}: {alarm_count} alarms detected")
                self.total_alarms_generated += alarm_count
        else:
            # No alarm enrichment
            enriched_payloads = [dp.to_dict() for dp in data_points]
        
        # Publish to MQTT
        # Note: We need to convert enriched payloads back to DataPoint-like objects
        # for the publisher, or modify publisher to accept dicts
        results = self.mqtt_publisher.publish_batch(data_points)
        
        self.total_messages_sent += results['success']
        self.cycles_completed += 1
        
        # Log cycle summary
        self.logger.info(
            f"Cycle {cycle_num} complete: "
            f"{results['success']} published, {results['failed']} failed"
        )
        
        # Print progress every 10 cycles
        if cycle_num % 10 == 0:
            self._print_progress()
    
    def _print_progress(self) -> None:
        """Print progress summary."""
        uptime = time.time() - self.start_time if self.start_time else 0
        uptime_str = self._format_duration(uptime)
        
        mqtt_metrics = self.mqtt_publisher.get_metrics()
        alarm_stats = self.alarm_simulator.get_statistics() if self.alarm_simulator else {}
        
        print(f"\n{'='*60}")
        print(f"Progress Report - Cycle {self.cycles_completed}")
        print(f"{'='*60}")
        print(f"Uptime: {uptime_str}")
        print(f"Messages sent: {self.total_messages_sent}")
        print(f"Messages failed: {mqtt_metrics.get('messages_failed', 0)}")
        
        if alarm_stats:
            print(f"Alarms generated: {alarm_stats.get('total_alarms', 0)}")
            print(f"  - Warnings: {alarm_stats.get('warnings', 0)}")
            print(f"  - Critical: {alarm_stats.get('critical', 0)}")
        
        print(f"{'='*60}\n")
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in seconds to human-readable string."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        signal_name = signal.Signals(signum).name
        self.logger.info(f"Received signal {signal_name}, initiating shutdown...")
        print(f"\n\nReceived {signal_name}, shutting down gracefully...")
        self.shutdown_requested = True
    
    def shutdown(self) -> None:
        """Shutdown the simulator gracefully."""
        if not self.running:
            return
        
        self.logger.info("Shutting down simulator...")
        self.running = False
        
        # Disconnect MQTT
        if self.mqtt_publisher:
            self.mqtt_publisher.disconnect()
            self.logger.info("MQTT connection closed")
        
        # Print final statistics
        self._print_final_statistics()
        
        self.logger.info("Simulator shutdown complete")
    
    def _print_final_statistics(self) -> None:
        """Print final statistics."""
        uptime = time.time() - self.start_time if self.start_time else 0
        uptime_str = self._format_duration(uptime)
        
        mqtt_metrics = self.mqtt_publisher.get_metrics() if self.mqtt_publisher else {}
        alarm_stats = self.alarm_simulator.get_statistics() if self.alarm_simulator else {}
        
        print(f"\n{'='*60}")
        print(f"Final Statistics")
        print(f"{'='*60}")
        print(f"Total uptime: {uptime_str}")
        print(f"Cycles completed: {self.cycles_completed}")
        print(f"Messages sent: {self.total_messages_sent}")
        print(f"Messages failed: {mqtt_metrics.get('messages_failed', 0)}")
        print(f"Connection attempts: {mqtt_metrics.get('connection_attempts', 0)}")
        
        if alarm_stats:
            print(f"\nAlarm Statistics:")
            print(f"  Total alarms: {alarm_stats.get('total_alarms', 0)}")
            print(f"  Warnings: {alarm_stats.get('warnings', 0)}")
            print(f"  Critical: {alarm_stats.get('critical', 0)}")
        
        if self.cycles_completed > 0:
            avg_messages_per_cycle = self.total_messages_sent / self.cycles_completed
            print(f"\nAverage messages per cycle: {avg_messages_per_cycle:.1f}")
        
        print(f"{'='*60}\n")


def main():
    """Main entry point."""
    # Determine config path
    if len(sys.argv) > 1:
        config_path = Path(sys.argv[1])
    else:
        config_path = Path(__file__).parent / "config.yaml"
    
    # Create and run simulator
    try:
        simulator = Simulator(config_path)
        simulator.run()
        sys.exit(0)
    
    except ConfigurationError as e:
        print(f"\n❌ Configuration Error: {e}\n", file=sys.stderr)
        sys.exit(1)
    
    except SimulatorError as e:
        print(f"\n❌ Simulator Error: {e}\n", file=sys.stderr)
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}\n", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
