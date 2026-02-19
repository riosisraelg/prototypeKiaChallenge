#!/usr/bin/env python3
"""
Local test script for simulator components (without AWS IoT Core).

This script tests the simulator components locally without requiring
AWS credentials or IoT Core connection.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config_loader import ConfigLoader
from data_generator import DataGenerator
from alarm_simulator import AlarmSimulator


def test_config_loader():
    """Test configuration loading."""
    print("=" * 60)
    print("Testing ConfigLoader")
    print("=" * 60)
    
    loader = ConfigLoader(base_path=Path(__file__).parent)
    variables = loader.load_all()
    active_vars = loader.get_active_variables()
    
    print(f"✅ Loaded {len(variables)} variables")
    print(f"✅ Active variables: {len(active_vars)}")
    
    # Show sample variables
    print("\nSample variables:")
    for var in list(active_vars)[:3]:
        print(f"  - {var.variable_id} ({var.area}): "
              f"{var.min_range}-{var.max_range} {var.unit}")
    
    return variables, active_vars


def test_data_generator(active_vars):
    """Test data generation."""
    print("\n" + "=" * 60)
    print("Testing DataGenerator")
    print("=" * 60)
    
    generator = DataGenerator(anomaly_probability=0.1)
    data_points = generator.generate_batch(active_vars[:5])
    
    print(f"✅ Generated {len(data_points)} data points")
    
    # Show sample data points
    print("\nSample data points:")
    for dp in data_points[:3]:
        print(f"  - {dp.variable_id}: {dp.value:.2f} {dp.unit} "
              f"(quality: {dp.quality})")
    
    return data_points


def test_alarm_simulator(variables, data_points):
    """Test alarm detection."""
    print("\n" + "=" * 60)
    print("Testing AlarmSimulator")
    print("=" * 60)
    
    alarm_sim = AlarmSimulator()
    
    alarm_count = 0
    for dp in data_points:
        var = variables[dp.variable_id]
        enriched = alarm_sim.enrich_data_point(dp, var)
        
        if enriched['alarm']['is_alarm']:
            alarm_count += 1
            print(f"  🚨 ALARM: {dp.variable_id} = {dp.value:.2f} {dp.unit}")
            print(f"     Severity: {enriched['alarm']['severity']}")
            print(f"     Message: {enriched['alarm']['message']}")
    
    print(f"\n✅ Detected {alarm_count} alarms out of {len(data_points)} data points")
    
    stats = alarm_sim.get_statistics()
    print(f"✅ Total alarms: {stats['total_alarms']}")
    print(f"   - Warnings: {stats['warnings']}")
    print(f"   - Critical: {stats['critical']}")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("KIA Paint Shop IoT Simulator - Local Test")
    print("=" * 60)
    print()
    
    try:
        # Test 1: Config Loader
        variables, active_vars = test_config_loader()
        
        # Test 2: Data Generator
        data_points = test_data_generator(active_vars)
        
        # Test 3: Alarm Simulator
        test_alarm_simulator(variables, data_points)
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        print("\nThe simulator components are working correctly.")
        print("Next step: Configure AWS IoT Core and run simulator.py")
        print()
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
