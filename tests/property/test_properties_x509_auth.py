"""
Property-based tests for X.509 authentication in IoT Core.

Feature: kia-paint-shop-iot-prototype
Property 19: Autenticación X.509 para dispositivos IoT

**Validates: Requirements 10.1**

These tests verify that:
1. MQTT connections without valid X.509 certificates are rejected
2. MQTT connections with valid certificates are accepted
3. Certificate validation is enforced before allowing message publication
4. TLS 1.2+ is required for all connections
"""

import pytest
import ssl
import socket
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from hypothesis import given, strategies as st, settings, assume, HealthCheck
import paho.mqtt.client as mqtt

# Add simulator to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "simulator"))

from mqtt_publisher import MQTTPublisher, MQTTConfig


# ============================================================================
# Property 19: X.509 Authentication Required
# ============================================================================

class TestX509Authentication:
    """
    Property 19: Para cualquier intento de conexión MQTT a IoT Core sin 
    certificado X.509 válido, la conexión debe ser rechazada antes de 
    permitir publicación de mensajes.
    """
    
    @pytest.fixture
    def mock_mqtt_config(self):
        """Create a mock MQTT configuration."""
        return MQTTConfig(
            endpoint="test-endpoint.iot.us-east-1.amazonaws.com",
            port=8883,
            cert_path="certs/device.crt",
            key_path="certs/device.key",
            ca_path="certs/AmazonRootCA1.pem",
            client_id="test-client",
            topic_prefix="kia/paintshop",
            qos=1,
            keep_alive=60
        )
    
    def test_connection_requires_certificate_files(self, mock_mqtt_config):
        """
        Property 19.1: Connection attempt without certificate files should fail.
        
        Validates that the system checks for certificate file existence
        before attempting connection.
        """
        # Create publisher with non-existent certificate paths
        invalid_config = MQTTConfig(
            endpoint=mock_mqtt_config.endpoint,
            port=mock_mqtt_config.port,
            cert_path="nonexistent/device.crt",
            key_path="nonexistent/device.key",
            ca_path="nonexistent/AmazonRootCA1.pem",
            client_id=mock_mqtt_config.client_id,
            topic_prefix=mock_mqtt_config.topic_prefix
        )
        
        publisher = MQTTPublisher(config=invalid_config)
        
        # Connection should fail due to missing certificates
        with pytest.raises(FileNotFoundError):
            publisher.connect()
    
    @patch('paho.mqtt.client.Client')
    def test_tls_configuration_enforces_cert_required(self, mock_client_class, mock_mqtt_config):
        """
        Property 19.2: TLS configuration must enforce certificate validation.
        
        Validates that cert_reqs is set to CERT_REQUIRED, ensuring that
        the server's certificate is validated.
        """
        # Create mock client instance
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Create temporary certificate files for testing
        cert_dir = Path("certs")
        cert_dir.mkdir(exist_ok=True)
        
        cert_file = cert_dir / "test_device.crt"
        key_file = cert_dir / "test_device.key"
        ca_file = cert_dir / "test_AmazonRootCA1.pem"
        
        try:
            # Create dummy certificate files
            cert_file.write_text("DUMMY CERT")
            key_file.write_text("DUMMY KEY")
            ca_file.write_text("DUMMY CA")
            
            # Update config to use test certificates
            test_config = MQTTConfig(
                endpoint=mock_mqtt_config.endpoint,
                port=mock_mqtt_config.port,
                cert_path=str(cert_file),
                key_path=str(key_file),
                ca_path=str(ca_file),
                client_id=mock_mqtt_config.client_id,
                topic_prefix=mock_mqtt_config.topic_prefix
            )
            
            publisher = MQTTPublisher(config=test_config)
            
            # Mock the connection to succeed
            mock_client.connect.return_value = 0
            
            # Attempt connection (will fail but we can check tls_set call)
            try:
                publisher.connect()
            except:
                pass  # We expect this to fail, we just want to check tls_set
            
            # Verify that tls_set was called with CERT_REQUIRED
            mock_client.tls_set.assert_called_once()
            call_kwargs = mock_client.tls_set.call_args[1]
            
            assert call_kwargs['cert_reqs'] == ssl.CERT_REQUIRED, \
                "Certificate validation must be required (CERT_REQUIRED)"
            
        finally:
            # Cleanup test files
            if cert_file.exists():
                cert_file.unlink()
            if key_file.exists():
                key_file.unlink()
            if ca_file.exists():
                ca_file.unlink()
    
    @patch('paho.mqtt.client.Client')
    def test_tls_version_is_1_2_or_higher(self, mock_client_class, mock_mqtt_config):
        """
        Property 19.3: TLS version must be 1.2 or higher.
        
        Validates that the MQTT publisher enforces TLS 1.2+ for all connections.
        """
        # Create mock client instance
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Create temporary certificate files
        cert_dir = Path("certs")
        cert_dir.mkdir(exist_ok=True)
        
        cert_file = cert_dir / "test_device.crt"
        key_file = cert_dir / "test_device.key"
        ca_file = cert_dir / "test_AmazonRootCA1.pem"
        
        try:
            cert_file.write_text("DUMMY CERT")
            key_file.write_text("DUMMY KEY")
            ca_file.write_text("DUMMY CA")
            
            test_config = MQTTConfig(
                endpoint=mock_mqtt_config.endpoint,
                port=mock_mqtt_config.port,
                cert_path=str(cert_file),
                key_path=str(key_file),
                ca_path=str(ca_file),
                client_id=mock_mqtt_config.client_id,
                topic_prefix=mock_mqtt_config.topic_prefix
            )
            
            publisher = MQTTPublisher(config=test_config)
            
            # Mock connection
            mock_client.connect.return_value = 0
            
            try:
                publisher.connect()
            except:
                pass
            
            # Verify TLS version
            mock_client.tls_set.assert_called_once()
            call_kwargs = mock_client.tls_set.call_args[1]
            
            # Check that TLS version is 1.2 or higher
            tls_version = call_kwargs['tls_version']
            
            # ssl.PROTOCOL_TLSv1_2 is the minimum acceptable version
            assert tls_version == ssl.PROTOCOL_TLSv1_2, \
                f"TLS version must be 1.2 or higher, got {tls_version}"
            
        finally:
            if cert_file.exists():
                cert_file.unlink()
            if key_file.exists():
                key_file.unlink()
            if ca_file.exists():
                ca_file.unlink()
    
    @patch('paho.mqtt.client.Client')
    def test_publish_fails_when_not_connected(self, mock_client_class, mock_mqtt_config):
        """
        Property 19.4: Message publication must fail if not connected with valid certificate.
        
        Validates that the system prevents message publication when not
        properly authenticated.
        """
        # Create mock client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Create temporary certificate files
        cert_dir = Path("certs")
        cert_dir.mkdir(exist_ok=True)
        
        cert_file = cert_dir / "test_device.crt"
        key_file = cert_dir / "test_device.key"
        ca_file = cert_dir / "test_AmazonRootCA1.pem"
        
        try:
            cert_file.write_text("DUMMY CERT")
            key_file.write_text("DUMMY KEY")
            ca_file.write_text("DUMMY CA")
            
            test_config = MQTTConfig(
                endpoint=mock_mqtt_config.endpoint,
                port=mock_mqtt_config.port,
                cert_path=str(cert_file),
                key_path=str(key_file),
                ca_path=str(ca_file),
                client_id=mock_mqtt_config.client_id,
                topic_prefix=mock_mqtt_config.topic_prefix
            )
            
            publisher = MQTTPublisher(config=test_config)
            
            # Don't connect - publisher.connected should be False
            assert not publisher.connected, "Publisher should not be connected initially"
            
            # Create a mock data point
            from data_generator import DataPoint
            from datetime import datetime
            
            data_point = DataPoint(
                variable_id="TEST-001",
                area="pre-treatment",
                timestamp=datetime.now(),
                value=65.5,
                unit="°C",
                quality="good",
                metadata={}
            )
            
            # Mock reconnection to fail
            mock_client.connect.return_value = 1  # Connection refused
            
            # Attempt to publish without being connected
            result = publisher.publish_data_point(data_point)
            
            # Publication should fail
            assert result is False, \
                "Message publication must fail when not authenticated"
            
            # Verify that failed message counter increased
            metrics = publisher.get_metrics()
            assert metrics['messages_failed'] > 0, \
                "Failed publication should be tracked in metrics"
            
        finally:
            if cert_file.exists():
                cert_file.unlink()
            if key_file.exists():
                key_file.unlink()
            if ca_file.exists():
                ca_file.unlink()
    
    @given(
        client_id=st.text(min_size=1, max_size=128, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='-_'
        ))
    )
    @settings(
        max_examples=50,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_client_id_used_in_connection(self, client_id, mock_mqtt_config):
        """
        Property 19.5: Client ID must be used for connection identification.
        
        For any valid client ID, the MQTT client must be initialized with
        that ID for proper authentication and tracking.
        """
        # Skip invalid client IDs
        assume(len(client_id) > 0)
        assume(client_id.strip() == client_id)  # No leading/trailing whitespace
        
        with patch('paho.mqtt.client.Client') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            
            # Create config with generated client ID
            test_config = MQTTConfig(
                endpoint=mock_mqtt_config.endpoint,
                port=mock_mqtt_config.port,
                cert_path="certs/device.crt",
                key_path="certs/device.key",
                ca_path="certs/AmazonRootCA1.pem",
                client_id=client_id,
                topic_prefix=mock_mqtt_config.topic_prefix
            )
            
            # Create temporary certificate files
            cert_dir = Path("certs")
            cert_dir.mkdir(exist_ok=True)
            
            cert_file = cert_dir / "test_device.crt"
            key_file = cert_dir / "test_device.key"
            ca_file = cert_dir / "test_AmazonRootCA1.pem"
            
            try:
                cert_file.write_text("DUMMY CERT")
                key_file.write_text("DUMMY KEY")
                ca_file.write_text("DUMMY CA")
                
                test_config.cert_path = str(cert_file)
                test_config.key_path = str(key_file)
                test_config.ca_path = str(ca_file)
                
                publisher = MQTTPublisher(config=test_config)
                
                # Mock connection
                mock_client.connect.return_value = 0
                
                try:
                    publisher.connect()
                except:
                    pass
                
                # Verify that Client was initialized with the correct client_id
                mock_client_class.assert_called_once_with(client_id=client_id)
                
            finally:
                if cert_file.exists():
                    cert_file.unlink()
                if key_file.exists():
                    key_file.unlink()
                if ca_file.exists():
                    ca_file.unlink()
    
    def test_certificate_paths_must_be_absolute_or_relative(self, mock_mqtt_config):
        """
        Property 19.6: Certificate paths must be valid file paths.
        
        Validates that certificate paths are properly validated before
        attempting TLS configuration.
        """
        # Test with various invalid path formats
        invalid_paths = [
            "",  # Empty path
            " ",  # Whitespace only
            "\x00",  # Null character
        ]
        
        for invalid_path in invalid_paths:
            invalid_config = MQTTConfig(
                endpoint=mock_mqtt_config.endpoint,
                port=mock_mqtt_config.port,
                cert_path=invalid_path,
                key_path=invalid_path,
                ca_path=invalid_path,
                client_id=mock_mqtt_config.client_id,
                topic_prefix=mock_mqtt_config.topic_prefix
            )
            
            publisher = MQTTPublisher(config=invalid_config)
            
            # Connection should fail due to invalid paths
            with pytest.raises((FileNotFoundError, ValueError, OSError)):
                publisher.connect()


# ============================================================================
# Integration Tests (require actual AWS IoT Core endpoint)
# ============================================================================

@pytest.mark.integration
@pytest.mark.skipif(
    not Path("simulator/certs/device.crt").exists(),
    reason="Requires actual IoT certificates"
)
class TestX509AuthenticationIntegration:
    """
    Integration tests for X.509 authentication with real AWS IoT Core.
    
    These tests require:
    - Valid AWS IoT Core endpoint configured
    - Valid X.509 certificates in simulator/certs/
    - Active IoT Thing and Policy
    """
    
    def test_connection_with_valid_certificates(self):
        """
        Integration test: Connection succeeds with valid certificates.
        """
        import yaml
        
        config_path = Path("simulator/config.yaml")
        if not config_path.exists():
            pytest.skip("config.yaml not found")
        
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        mqtt_config_data = config_data.get('mqtt', {})
        
        if not mqtt_config_data.get('endpoint'):
            pytest.skip("MQTT endpoint not configured")
        
        mqtt_config = MQTTConfig(
            endpoint=mqtt_config_data['endpoint'],
            port=mqtt_config_data.get('port', 8883),
            cert_path=mqtt_config_data.get('cert_path', 'simulator/certs/device.crt'),
            key_path=mqtt_config_data.get('key_path', 'simulator/certs/device.key'),
            ca_path=mqtt_config_data.get('ca_path', 'simulator/certs/AmazonRootCA1.pem'),
            client_id=mqtt_config_data.get('client_id', 'test-client'),
            topic_prefix=mqtt_config_data.get('topic_prefix', 'kia/paintshop')
        )
        
        publisher = MQTTPublisher(config=mqtt_config)
        
        # Connection should succeed with valid certificates
        result = publisher.connect()
        
        assert result is True, "Connection should succeed with valid certificates"
        assert publisher.connected is True, "Publisher should be in connected state"
        
        # Cleanup
        publisher.disconnect()
    
    def test_connection_with_invalid_certificates_fails(self):
        """
        Integration test: Connection fails with invalid certificates.
        """
        import yaml
        
        config_path = Path("simulator/config.yaml")
        if not config_path.exists():
            pytest.skip("config.yaml not found")
        
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        mqtt_config_data = config_data.get('mqtt', {})
        
        if not mqtt_config_data.get('endpoint'):
            pytest.skip("MQTT endpoint not configured")
        
        # Create temporary invalid certificate files
        cert_dir = Path("certs")
        cert_dir.mkdir(exist_ok=True)
        
        invalid_cert = cert_dir / "invalid_device.crt"
        invalid_key = cert_dir / "invalid_device.key"
        
        try:
            invalid_cert.write_text("INVALID CERTIFICATE")
            invalid_key.write_text("INVALID KEY")
            
            mqtt_config = MQTTConfig(
                endpoint=mqtt_config_data['endpoint'],
                port=mqtt_config_data.get('port', 8883),
                cert_path=str(invalid_cert),
                key_path=str(invalid_key),
                ca_path=mqtt_config_data.get('ca_path', 'simulator/certs/AmazonRootCA1.pem'),
                client_id='invalid-test-client',
                topic_prefix='kia/paintshop'
            )
            
            publisher = MQTTPublisher(config=mqtt_config)
            
            # Connection should fail with invalid certificates
            result = publisher.connect()
            
            assert result is False, \
                "Connection must fail with invalid certificates"
            assert publisher.connected is False, \
                "Publisher should not be in connected state"
            
        finally:
            if invalid_cert.exists():
                invalid_cert.unlink()
            if invalid_key.exists():
                invalid_key.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
