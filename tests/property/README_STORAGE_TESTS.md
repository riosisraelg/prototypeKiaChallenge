# Property Tests for Data Storage

This document describes the property-based tests for data storage functionality in the KIA Paint Shop IoT prototype.

## Overview

These tests validate two critical correctness properties:
- **Property 7**: TTL (Time-To-Live) calculation correctness
- **Property 8**: DynamoDB key structure compliance

## Test File

`test_properties_storage.py`

## Property 7: Almacenamiento con TTL correcto

**Validates**: Requirements 3.1

**Property Statement**: Para cualquier dato almacenado en DynamoDB tabla sensor-data, el campo ttl debe ser igual al timestamp de creación más N días (en epoch seconds).

### Tests

1. **test_property_7_ttl_calculation_is_correct**
   - Verifies TTL is calculated as current time + N days
   - Tests with random day values (1-365)
   - 100 examples per run

2. **test_property_7_ttl_is_in_future**
   - Ensures TTL is always in the future
   - Validates minimum offset matches requested days
   - 100 examples per run

3. **test_property_7_default_ttl_is_30_days**
   - Confirms default TTL is 30 days when not specified
   - Single deterministic test

4. **test_property_7_ttl_ordering_is_consistent**
   - Verifies that more days results in larger TTL
   - Tests ordering consistency
   - 100 examples per run

## Property 8: Estructura de keys en DynamoDB

**Validates**: Requirements 3.2

**Property Statement**: Para cualquier item almacenado en sensor-data, la partition key (PK) debe tener formato `{area}#{variable_id}` y la sort key (SK) debe tener formato `DATA#{timestamp_ms}` donde timestamp_ms es un número entero positivo.

### Tests

1. **test_property_8_partition_key_format**
   - Validates PK format: `{area}#{variable_id}`
   - 100 examples per run

2. **test_property_8_sort_key_format**
   - Validates SK format: `DATA#{timestamp_ms}`
   - Ensures timestamp_ms is a positive integer
   - 100 examples per run

3. **test_property_8_timestamp_ms_is_reasonable**
   - Verifies timestamp is within reasonable range (2020-2030)
   - Prevents invalid timestamps
   - 100 examples per run

4. **test_property_8_item_contains_required_fields**
   - Ensures all required fields are present
   - Fields: PK, SK, variable_id, area, timestamp, value, unit, ttl
   - 100 examples per run

5. **test_property_8_item_preserves_original_data**
   - Validates that original message data is preserved exactly
   - No data corruption during transformation
   - 100 examples per run

6. **test_property_8_pk_contains_no_special_characters**
   - Ensures PK only contains ASCII alphanumeric, hyphen, underscore, and '#'
   - Prevents DynamoDB key issues
   - 100 examples per run

7. **test_property_8_pk_uniquely_identifies_variable**
   - Verifies same variable has same PK across different timestamps
   - Different timestamps have different SKs
   - 100 examples per run

8. **test_property_8_sk_allows_time_range_queries**
   - Validates SKs are lexicographically sortable by time
   - Enables efficient time-range queries
   - 100 examples per run

9. **test_property_8_metadata_is_preserved**
   - Ensures metadata (ranges, thresholds) is preserved
   - 100 examples per run

10. **test_property_8_quality_defaults_to_good**
    - Validates default quality value is 'good'
    - 50 examples per run

## Running the Tests

```bash
# Run all storage property tests
python -m pytest tests/property/test_properties_storage.py -v

# Run with coverage
python -m pytest tests/property/test_properties_storage.py --cov=lambdas/ingest --cov-report=html

# Run specific property test
python -m pytest tests/property/test_properties_storage.py::test_property_7_ttl_calculation_is_correct -v
```

## Test Statistics

- **Total tests**: 14
- **Total examples generated**: ~1,400 per full run
- **Execution time**: ~0.7 seconds
- **Coverage**: TTL calculation and DynamoDB item construction

## Key Insights

1. **TTL Correctness**: All TTL calculations are verified to be exactly N days in the future, ensuring proper data expiration.

2. **Key Structure**: DynamoDB keys follow the exact format specified in the design document, enabling efficient queries.

3. **Data Preservation**: Original sensor data is preserved without corruption during storage transformation.

4. **Query Efficiency**: Sort keys are lexicographically sortable, enabling efficient time-range queries.

## Dependencies

- `hypothesis`: Property-based testing framework
- `pytest`: Test runner
- `boto3`: AWS SDK (for handler imports)

## Notes

- Tests use hypothesis strategies to generate diverse inputs
- Each test runs 50-100 examples by default
- Tests validate both positive and negative cases
- All tests follow the property-based testing methodology
