"""
MQTT Publisher module for KIA Paint Shop IoT Prototype.

This module handles MQTT communication with AWS IoT Core, including:
- TLS connection with X.509 certificates
- Publishing to hierarchical topics (kia/paintshop/{area}/{variable_id})
- Automatic reconnection with exponential backoff
- Connection and publication error handling

Requirements: 2.1, 2.2, 2.4, 10.5
"""

import json
import logging
import time
import ssl
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass

import paho.mqtt.client as mqtt

from data_generator import DataPoint

logger = logging.getLogger(__name__)


@dataclass
class MQTTConfig:
    """MQTT connection configuration."""
    
    endpoint: str
    port: int
    cert_path: str
    key_path: str
    ca_path: str
    client_id: str
    topic_prefix: str
    qos: int = 1
    keep_alive: int = 60


class MQTTPublisher:
    """
    MQTT publisher with TLS authentication and automatic reconnection.
    
    Features:
    - X.509 certificate authentication
    - Hierarchical topic structure: kia/paintshop/{area}/{variable_id}
    - Exponential backoff for reconnection
    - Connection and publication error handling
    """
    
    def __init__(
        self,
        config: MQTTConfig,
        max_retry_attempts: int = 5,
        initial_retry_delay: float = 1.0,
        max_retry_delay: float = 60.0,
        backoff_multiplier: float = 2.0
    ):
        """
        Initialize MQTT publisher.
        
        Args:
            config: MQTT connection configuration
            max_retry_attempts: Maximum number of reconnection attempts
            initial_retry_delay: Initial delay between retries (seconds)
            max_retry_delay: Maximum delay between retries (seconds)
            backoff_multiplier: Multiplier for exponential backoff
        """
        self.config = config
        self.max_retry_attempts = max_retry_attempts
        self.initial_retry_delay = initial_retry_delay
        self.max_retry_delay = max_retry_delay
        self.backoff_multiplier = backoff_multiplier
        
        # Connection state
        self.client: Optional[mqtt.Client] = None
        self.connected = False
        self.retry_count = 0
        self.current_retry_delay = initial_retry_delay
        
        # Metrics
        self.messages_published = 0
        self.messages_failed = 0
        self.connection_attempts = 0
        self.last_publish_time: Optional[float] = None
        
        # Callbacks
        self.on_connect_callback: Optional[Callable] = None
        self.on_disconnect_callback: Optional[Callable] = None
        self.on_publish_callback: Optional[Callable] = None
        
    def connect(self) -> bool:
        """
        Connect to AWS IoT Core with TLS authentication.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            logger.info(f"Connecting to AWS IoT Core at {self.config.endpoint}:{self.config.port}")
            
            # Create MQTT client
            self.client = mqtt.Client(client_id=self.config.client_id)
            
            # Set callbacks
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_publish = self._on_publish
            
            # Configure TLS with X.509 certificates
            self._configure_tls()
            
            # Connect to broker
            self.connection_attempts += 1
            self.client.connect(
                self.config.endpoint,
                self.config.port,
                self.config.keep_alive
            )
            
            # Start network loop in background thread
            self.client.loop_start()
            
            # Wait for connection (with timeout)
            timeout = 10.0
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if self.connected:
                logger.info("Successfully connected to AWS IoT Core")
                self.retry_count = 0
                self.current_retry_delay = self.initial_retry_delay
                return True
            else:
                logger.error("Connection timeout")
                return False
                
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    def _configure_tls(self) -> None:
        """Configure TLS with X.509 certificates."""
        try:
            # Validate certificate paths
            cert_path = Path(self.config.cert_path)
            key_path = Path(self.config.key_path)
            ca_path = Path(self.config.ca_path)
            
            if not cert_path.exists():
                raise FileNotFoundError(f"Certificate not found: {cert_path}")
            if not key_path.exists():
                raise FileNotFoundError(f"Private key not found: {key_path}")
            if not ca_path.exists():
                raise FileNotFoundError(f"CA certificate not found: {ca_path}")
            
            # Configure TLS
            self.client.tls_set(
                ca_certs=str(ca_path),
                certfile=str(cert_path),
                keyfile=str(key_path),
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLSv1_2,
                ciphers=None
            )
            
            # Disable hostname verification (AWS IoT uses custom endpoints)
            self.client.tls_insecure_set(False)
            
            logger.debug("TLS configured successfully")
            
        except Exception as e:
            logger.error(f"TLS configuration error: {e}")
            raise
    
    def disconnect(self) -> None:
        """Disconnect from MQTT broker."""
        if self.client:
            logger.info("Disconnecting from AWS IoT Core")
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
    
    def publish_data_point(self, data_point: DataPoint) -> bool:
        """
        Publish a data point to the appropriate MQTT topic.
        
        Topic structure: kia/paintshop/{area}/{variable_id}
        
        Args:
            data_point: DataPoint to publish
            
        Returns:
            True if publish successful, False otherwise
        """
        if not self.connected:
            logger.warning("Not connected to MQTT broker, attempting reconnection...")
            if not self._reconnect_with_backoff():
                logger.error("Failed to reconnect, message not published")
                self.messages_failed += 1
                return False
        
        try:
            # Build topic
            topic = self._build_topic(data_point.area, data_point.variable_id)
            
            # Convert data point to JSON payload
            payload = json.dumps(data_point.to_dict())
            
            # Publish message
            result = self.client.publish(
                topic,
                payload,
                qos=self.config.qos
            )
            
            # Check if publish was queued successfully
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.messages_published += 1
                self.last_publish_time = time.time()
                logger.debug(f"Published to {topic}: {data_point.variable_id}={data_point.value}")
                return True
            else:
                logger.error(f"Publish failed with code {result.rc}")
                self.messages_failed += 1
                return False
                
        except Exception as e:
            logger.error(f"Error publishing data point: {e}")
            self.messages_failed += 1
            return False
    
    def publish_batch(self, data_points: list[DataPoint]) -> Dict[str, int]:
        """
        Publish multiple data points.
        
        Args:
            data_points: List of DataPoint objects to publish
            
        Returns:
            Dictionary with 'success' and 'failed' counts
        """
        success_count = 0
        failed_count = 0
        
        for data_point in data_points:
            if self.publish_data_point(data_point):
                success_count += 1
            else:
                failed_count += 1
        
        logger.info(f"Batch publish complete: {success_count} success, {failed_count} failed")
        
        return {
            'success': success_count,
            'failed': failed_count
        }
    
    def _build_topic(self, area: str, variable_id: str) -> str:
        """
        Build MQTT topic with hierarchical structure.
        
        Format: kia/paintshop/{area}/{variable_id}
        
        Args:
            area: Area name (pre-treatment, e-coat, production-control)
            variable_id: Variable ID (e.g., PT-001)
            
        Returns:
            Complete MQTT topic string
        """
        return f"{self.config.topic_prefix}/{area}/{variable_id}"
    
    def _reconnect_with_backoff(self) -> bool:
        """
        Attempt to reconnect with exponential backoff.
        
        Returns:
            True if reconnection successful, False otherwise
        """
        while self.retry_count < self.max_retry_attempts:
            self.retry_count += 1
            
            logger.info(
                f"Reconnection attempt {self.retry_count}/{self.max_retry_attempts} "
                f"(delay: {self.current_retry_delay:.1f}s)"
            )
            
            # Wait before retry
            time.sleep(self.current_retry_delay)
            
            # Attempt connection
            if self.connect():
                logger.info("Reconnection successful")
                return True
            
            # Increase delay with exponential backoff
            self.current_retry_delay = min(
                self.current_retry_delay * self.backoff_multiplier,
                self.max_retry_delay
            )
        
        logger.error(f"Failed to reconnect after {self.max_retry_attempts} attempts")
        return False
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connection is established."""
        if rc == 0:
            self.connected = True
            logger.info("MQTT connection established")
            
            if self.on_connect_callback:
                self.on_connect_callback()
        else:
            self.connected = False
            error_messages = {
                1: "Connection refused - incorrect protocol version",
                2: "Connection refused - invalid client identifier",
                3: "Connection refused - server unavailable",
                4: "Connection refused - bad username or password",
                5: "Connection refused - not authorized"
            }
            error_msg = error_messages.get(rc, f"Unknown error code: {rc}")
            logger.error(f"Connection failed: {error_msg}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when connection is lost."""
        self.connected = False
        
        if rc == 0:
            logger.info("Disconnected cleanly")
        else:
            logger.warning(f"Unexpected disconnection (code: {rc})")
            
            # Attempt automatic reconnection
            logger.info("Attempting automatic reconnection...")
            self._reconnect_with_backoff()
        
        if self.on_disconnect_callback:
            self.on_disconnect_callback(rc)
    
    def _on_publish(self, client, userdata, mid):
        """Callback when message is published."""
        logger.debug(f"Message {mid} published successfully")
        
        if self.on_publish_callback:
            self.on_publish_callback(mid)
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get publisher metrics.
        
        Returns:
            Dictionary with metrics
        """
        return {
            'connected': self.connected,
            'messages_published': self.messages_published,
            'messages_failed': self.messages_failed,
            'connection_attempts': self.connection_attempts,
            'retry_count': self.retry_count,
            'last_publish_time': self.last_publish_time
        }
    
    def reset_metrics(self) -> None:
        """Reset metrics counters."""
        self.messages_published = 0
        self.messages_failed = 0
        self.connection_attempts = 0
        self.last_publish_time = None
        logger.info("Metrics reset")


def main():
    """Test the MQTT publisher."""
    import sys
    import yaml
    from pathlib import Path
    
    # Add simulator to path
    sys.path.insert(0, str(Path(__file__).parent))
    
    from config_loader import ConfigLoader
    from data_generator import DataGenerator
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print(f"\n{'='*60}")
    print(f"MQTT Publisher Test")
    print(f"{'='*60}\n")
    
    # Load configuration
    config_path = Path(__file__).parent / "config.yaml"
    
    if not config_path.exists():
        print("ERROR: config.yaml not found")
        print("Please create config.yaml with MQTT endpoint and certificate paths")
        return
    
    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f)
    
    mqtt_config_data = config_data.get('mqtt', {})
    
    # Check if endpoint is configured
    if not mqtt_config_data.get('endpoint'):
        print("ERROR: MQTT endpoint not configured in config.yaml")
        print("Please set mqtt.endpoint to your AWS IoT Core endpoint")
        return
    
    # Create MQTT config
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
    
    # Create publisher
    retry_config = config_data.get('retry', {})
    publisher = MQTTPublisher(
        config=mqtt_config,
        max_retry_attempts=retry_config.get('max_attempts', 5),
        initial_retry_delay=retry_config.get('initial_delay', 1.0),
        max_retry_delay=retry_config.get('max_delay', 60.0),
        backoff_multiplier=retry_config.get('backoff_multiplier', 2.0)
    )
    
    # Connect
    print("Connecting to AWS IoT Core...")
    if not publisher.connect():
        print("ERROR: Failed to connect to AWS IoT Core")
        print("Please check your configuration and certificates")
        return
    
    print("✓ Connected successfully\n")
    
    # Load variables
    print("Loading variables...")
    loader = ConfigLoader()
    variables = loader.load_all()
    print(f"✓ Loaded {len(variables)} variables\n")
    
    # Create data generator
    generator = DataGenerator(anomaly_probability=0.1)
    
    # Test publishing
    print("Publishing test messages...\n")
    
    # Get first 5 variables for testing
    test_vars = list(variables.values())[:5]
    
    for i in range(3):
        print(f"Round {i+1}:")
        print("-" * 60)
        
        # Generate data
        data_points = generator.generate_batch(test_vars)
        
        # Publish batch
        results = publisher.publish_batch(data_points)
        
        print(f"Published {results['success']} messages, {results['failed']} failed")
        
        # Show metrics
        metrics = publisher.get_metrics()
        print(f"Total published: {metrics['messages_published']}")
        print(f"Total failed: {metrics['messages_failed']}")
        print()
        
        # Wait before next round
        if i < 2:
            time.sleep(2)
    
    # Disconnect
    print("\nDisconnecting...")
    publisher.disconnect()
    print("✓ Disconnected\n")
    
    # Final metrics
    print("Final Metrics:")
    print("-" * 60)
    metrics = publisher.get_metrics()
    for key, value in metrics.items():
        print(f"{key}: {value}")
    
    print(f"\n{'='*60}")
    print("Test complete!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
