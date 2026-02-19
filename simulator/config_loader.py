"""
Configuration loader module for KIA Paint Shop IoT Prototype.

This module loads variable configurations from CSV files and validates
their ranges, units, and alarm thresholds.

Supports:
- Pre-Treatment (PT): 48 variables from KMX-PA-PT-F-001.csv
- E-Coat (ED): 18 variables from KMX-PA-PE-F-001.csv  
- Production Control: 34 variables from configuration
"""

import csv
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class Variable:
    """Represents a process variable with its configuration."""
    
    variable_id: str
    name: str
    area: str  # pre-treatment, e-coat, production-control
    unit: str
    min_range: float
    max_range: float
    alarm_low: float
    alarm_high: float
    description: str = ""
    source_file: str = ""
    active: bool = True
    
    def validate(self) -> Tuple[bool, Optional[str]]:
        """
        Validate variable configuration.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check that ranges make sense
        if self.min_range >= self.max_range:
            return False, f"{self.variable_id}: min_range must be less than max_range"
        
        # Check that alarm thresholds are within ranges
        if self.alarm_low < self.min_range:
            return False, f"{self.variable_id}: alarm_low must be >= min_range"
        
        if self.alarm_high > self.max_range:
            return False, f"{self.variable_id}: alarm_high must be <= max_range"
        
        if self.alarm_low >= self.alarm_high:
            return False, f"{self.variable_id}: alarm_low must be < alarm_high"
        
        # Check required fields
        if not self.variable_id or not self.name:
            return False, f"variable_id and name are required"
        
        if not self.area or self.area not in ['pre-treatment', 'e-coat', 'production-control']:
            return False, f"{self.variable_id}: area must be one of: pre-treatment, e-coat, production-control"
        
        return True, None


class ConfigLoader:
    """Loads and manages variable configurations from CSV files."""
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize the config loader.
        
        Args:
            base_path: Base path for CSV files. Defaults to workspace root.
        """
        self.base_path = base_path or Path.cwd()
        self.variables: Dict[str, Variable] = {}
        
    def load_all(self) -> Dict[str, Variable]:
        """
        Load all variable configurations.
        
        Returns:
            Dictionary of variable_id -> Variable
        """
        logger.info("Loading all variable configurations...")
        
        # Load Pre-Treatment variables
        pt_vars = self.load_pre_treatment()
        logger.info(f"Loaded {len(pt_vars)} Pre-Treatment variables")
        
        # Load E-Coat variables
        ed_vars = self.load_e_coat()
        logger.info(f"Loaded {len(ed_vars)} E-Coat variables")
        
        # Load Production Control variables
        pc_vars = self.load_production_control()
        logger.info(f"Loaded {len(pc_vars)} Production Control variables")
        
        # Combine all variables
        self.variables = {**pt_vars, **ed_vars, **pc_vars}
        
        # Validate all variables
        self._validate_all()
        
        logger.info(f"Total variables loaded: {len(self.variables)}")
        return self.variables
    
    def load_pre_treatment(self) -> Dict[str, Variable]:
        """
        Load Pre-Treatment variables from KMX-PA-PT-F-001.csv.
        
        Returns:
            Dictionary of variable_id -> Variable
        """
        csv_path = self.base_path / "data" / "KMX-PA-PT-F-001.csv"
        logger.info(f"Loading Pre-Treatment variables from {csv_path}")
        
        variables = {}
        
        try:
            with open(csv_path, 'r', encoding='latin1') as f:
                # Read all lines
                lines = f.readlines()
                
                # Find the header row (row 8 contains: Num, ETAPA, VARIABLE, RANGO, etc.)
                # Data starts at row 11
                data_start_row = 11
                
                # Parse each variable row
                reader = csv.reader(lines[data_start_row:], delimiter=',')
                
                var_counter = 1
                current_stage = None
                
                for row in reader:
                    # Skip empty rows
                    if not row or all(cell.strip() == '' for cell in row if cell):
                        continue
                    
                    # Check if this is a stage header (has number in first column)
                    if row[0].strip().isdigit():
                        current_stage = row[1].strip() if len(row) > 1 else "Unknown"
                        continue
                    
                    # Parse variable data
                    # Format: [empty, empty, VARIABLE, RANGO, VOLUMEN, ...]
                    if len(row) > 3 and row[2].strip():
                        variable_name = row[2].strip()
                        range_str = row[3].strip() if len(row) > 3 else ""
                        
                        # Skip if no range
                        if not range_str:
                            continue
                        
                        # Parse range (e.g., "31 - 35", "240-290", "5.0 - 6.2")
                        min_val, max_val = self._parse_range(range_str)
                        
                        if min_val is None or max_val is None:
                            logger.warning(f"Could not parse range for {variable_name}: {range_str}")
                            continue
                        
                        # Generate variable ID
                        var_id = f"PT-{var_counter:03d}"
                        
                        # Extract unit from variable name if present
                        unit = self._extract_unit(variable_name)
                        
                        # Calculate alarm thresholds (10% from edges)
                        range_span = max_val - min_val
                        alarm_low = min_val + (range_span * 0.1)
                        alarm_high = max_val - (range_span * 0.1)
                        
                        variable = Variable(
                            variable_id=var_id,
                            name=variable_name,
                            area="pre-treatment",
                            unit=unit,
                            min_range=min_val,
                            max_range=max_val,
                            alarm_low=alarm_low,
                            alarm_high=alarm_high,
                            description=f"{current_stage} - {variable_name}" if current_stage else variable_name,
                            source_file="KMX-PA-PT-F-001.csv",
                            active=True
                        )
                        
                        variables[var_id] = variable
                        var_counter += 1
                        
                        # Stop after 48 variables
                        if var_counter > 48:
                            break
                
        except FileNotFoundError:
            logger.error(f"CSV file not found: {csv_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading Pre-Treatment variables: {e}")
            raise
        
        return variables
    
    def load_e_coat(self) -> Dict[str, Variable]:
        """
        Load E-Coat variables from KMX-PA-PE-F-001.csv.
        
        Returns:
            Dictionary of variable_id -> Variable
        """
        csv_path = self.base_path / "data" / "KMX-PA-PE-F-001.csv"
        logger.info(f"Loading E-Coat variables from {csv_path}")
        
        variables = {}
        
        try:
            with open(csv_path, 'r', encoding='latin1') as f:
                # Read all lines
                lines = f.readlines()
                
                # Data starts at row 11 (same structure as PT file)
                data_start_row = 11
                
                # Parse each variable row
                reader = csv.reader(lines[data_start_row:], delimiter=',')
                
                var_counter = 1
                current_stage = None
                
                for row in reader:
                    # Skip empty rows
                    if not row or all(cell.strip() == '' for cell in row if cell):
                        continue
                    
                    # Check if this is a stage header
                    if row[0].strip().isdigit():
                        current_stage = row[1].strip() if len(row) > 1 else "Unknown"
                        continue
                    
                    # Parse variable data
                    if len(row) > 3 and row[2].strip():
                        variable_name = row[2].strip()
                        range_str = row[3].strip() if len(row) > 3 else ""
                        
                        if not range_str:
                            continue
                        
                        # Parse range
                        min_val, max_val = self._parse_range(range_str)
                        
                        if min_val is None or max_val is None:
                            logger.warning(f"Could not parse range for {variable_name}: {range_str}")
                            continue
                        
                        # Generate variable ID
                        var_id = f"ED-{var_counter:03d}"
                        
                        # Extract unit
                        unit = self._extract_unit(variable_name)
                        
                        # Calculate alarm thresholds
                        range_span = max_val - min_val
                        alarm_low = min_val + (range_span * 0.1)
                        alarm_high = max_val - (range_span * 0.1)
                        
                        variable = Variable(
                            variable_id=var_id,
                            name=variable_name,
                            area="e-coat",
                            unit=unit,
                            min_range=min_val,
                            max_range=max_val,
                            alarm_low=alarm_low,
                            alarm_high=alarm_high,
                            description=f"{current_stage} - {variable_name}" if current_stage else variable_name,
                            source_file="KMX-PA-PE-F-001.csv",
                            active=True
                        )
                        
                        variables[var_id] = variable
                        var_counter += 1
                        
                        # Stop after 18 variables
                        if var_counter > 18:
                            break
                
        except FileNotFoundError:
            logger.error(f"CSV file not found: {csv_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading E-Coat variables: {e}")
            raise
        
        return variables
    
    def load_production_control(self) -> Dict[str, Variable]:
        """
        Load Production Control variables from configuration.
        
        These are synthetic variables for production monitoring.
        
        Returns:
            Dictionary of variable_id -> Variable
        """
        logger.info("Loading Production Control variables")
        
        variables = {}
        
        # Define 34 production control variables
        pc_config = [
            # Line speed and throughput
            ("Line Speed", "m/min", 10.0, 30.0),
            ("Throughput Rate", "units/hr", 20.0, 60.0),
            ("Cycle Time", "seconds", 60.0, 180.0),
            
            # Quality metrics
            ("Paint Thickness", "microns", 15.0, 35.0),
            ("Surface Roughness", "Ra", 0.5, 2.5),
            ("Gloss Level", "%", 70.0, 95.0),
            ("Color Delta E", "dE", 0.0, 2.0),
            
            # Environmental conditions
            ("Booth Temperature", "°C", 20.0, 28.0),
            ("Booth Humidity", "%RH", 40.0, 70.0),
            ("Air Velocity", "m/s", 0.2, 0.5),
            
            # Energy consumption
            ("Power Consumption", "kW", 100.0, 500.0),
            ("Compressed Air Pressure", "bar", 5.0, 8.0),
            ("Water Flow Rate", "L/min", 50.0, 200.0),
            
            # Process monitoring
            ("Conveyor Speed", "m/min", 8.0, 25.0),
            ("Oven Temperature Zone 1", "°C", 140.0, 180.0),
            ("Oven Temperature Zone 2", "°C", 160.0, 200.0),
            ("Oven Temperature Zone 3", "°C", 150.0, 190.0),
            
            # Chemical consumption
            ("Paint Consumption", "L/hr", 10.0, 50.0),
            ("Solvent Consumption", "L/hr", 5.0, 25.0),
            ("Cleaner Consumption", "L/hr", 3.0, 15.0),
            
            # Waste and emissions
            ("VOC Emissions", "ppm", 0.0, 100.0),
            ("Waste Water Flow", "L/hr", 20.0, 100.0),
            ("Sludge Production", "kg/hr", 1.0, 10.0),
            
            # Equipment status
            ("Pump Pressure", "bar", 2.0, 6.0),
            ("Filter Differential Pressure", "bar", 0.1, 1.0),
            ("Tank Level", "%", 30.0, 90.0),
            
            # Production counts
            ("Units Painted", "count", 0.0, 1000.0),
            ("Defect Count", "count", 0.0, 50.0),
            ("Rework Count", "count", 0.0, 20.0),
            
            # Efficiency metrics
            ("OEE", "%", 60.0, 95.0),
            ("First Pass Yield", "%", 85.0, 99.0),
            ("Downtime", "minutes", 0.0, 60.0),
            
            # Material tracking
            ("Paint Batch Number", "batch", 1000.0, 9999.0),
            ("Material Temperature", "°C", 18.0, 25.0),
        ]
        
        for idx, (name, unit, min_val, max_val) in enumerate(pc_config, start=1):
            var_id = f"PC-{idx:03d}"
            
            # Calculate alarm thresholds
            range_span = max_val - min_val
            alarm_low = min_val + (range_span * 0.1)
            alarm_high = max_val - (range_span * 0.1)
            
            variable = Variable(
                variable_id=var_id,
                name=name,
                area="production-control",
                unit=unit,
                min_range=min_val,
                max_range=max_val,
                alarm_low=alarm_low,
                alarm_high=alarm_high,
                description=f"Production Control - {name}",
                source_file="config",
                active=True
            )
            
            variables[var_id] = variable
        
        return variables
    
    def _parse_range(self, range_str: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Parse a range string like "31 - 35", "240-290", "<0.8", ">95", "4.5 ~ 6.4", etc.
        
        Args:
            range_str: Range string to parse
            
        Returns:
            Tuple of (min_value, max_value) or (None, None) if parsing fails
        """
        try:
            # Remove extra spaces
            range_str = range_str.strip()
            
            # Handle special cases like "<0.8" (less than)
            if range_str.startswith('<'):
                max_val = float(range_str[1:].strip())
                # Assume min is 0 or 80% of max
                min_val = max(0.0, max_val * 0.8)
                return min_val, max_val
            
            # Handle special cases like ">95" (greater than)
            if range_str.startswith('>'):
                min_val = float(range_str[1:].strip())
                # Assume max is 120% of min
                max_val = min_val * 1.2
                return min_val, max_val
            
            # Handle ranges with percentage at the end like "30-80 %"
            if '%' in range_str:
                range_str = range_str.replace('%', '').strip()
            
            # Try different separators
            if ' - ' in range_str:
                parts = range_str.split(' - ')
            elif ' ~ ' in range_str:
                parts = range_str.split(' ~ ')
            elif '-' in range_str:
                # Be careful with negative numbers
                parts = range_str.split('-')
                # Filter out empty strings from leading dash
                parts = [p for p in parts if p.strip()]
            else:
                # Single value - create a small range around it
                val = float(range_str)
                return val * 0.9, val * 1.1
            
            if len(parts) != 2:
                return None, None
            
            min_val = float(parts[0].strip())
            max_val = float(parts[1].strip())
            
            return min_val, max_val
            
        except (ValueError, IndexError):
            return None, None
    
    def _extract_unit(self, variable_name: str) -> str:
        """
        Extract unit from variable name.
        
        Args:
            variable_name: Variable name that may contain unit in parentheses
            
        Returns:
            Extracted unit or empty string
        """
        # Look for units in parentheses
        if '(' in variable_name and ')' in variable_name:
            start = variable_name.rfind('(')
            end = variable_name.rfind(')')
            if start < end:
                unit = variable_name[start+1:end].strip()
                return unit
        
        # Common units to look for
        common_units = ['°C', 'C¡', '%', 'V', 'A', 'pH', 'µS/cm', '_/cm', 'l/min', 'L/min', 'ppm', 'bar', 'kW']
        
        for unit in common_units:
            if unit in variable_name:
                return unit
        
        return ""
    
    def _validate_all(self) -> None:
        """Validate all loaded variables."""
        logger.info("Validating all variables...")
        
        invalid_count = 0
        for var_id, variable in self.variables.items():
            is_valid, error_msg = variable.validate()
            if not is_valid:
                logger.error(f"Validation failed for {var_id}: {error_msg}")
                invalid_count += 1
        
        if invalid_count > 0:
            raise ValueError(f"{invalid_count} variables failed validation")
        
        logger.info("All variables validated successfully")
    
    def get_variable(self, variable_id: str) -> Optional[Variable]:
        """
        Get a variable by ID.
        
        Args:
            variable_id: Variable ID to retrieve
            
        Returns:
            Variable object or None if not found
        """
        return self.variables.get(variable_id)
    
    def get_variables_by_area(self, area: str) -> List[Variable]:
        """
        Get all variables for a specific area.
        
        Args:
            area: Area name (pre-treatment, e-coat, production-control)
            
        Returns:
            List of Variable objects
        """
        return [v for v in self.variables.values() if v.area == area]
    
    def get_active_variables(self) -> List[Variable]:
        """
        Get all active variables.
        
        Returns:
            List of active Variable objects
        """
        return [v for v in self.variables.values() if v.active]


def main():
    """Test the config loader."""
    logging.basicConfig(level=logging.INFO)
    
    loader = ConfigLoader()
    variables = loader.load_all()
    
    print(f"\n{'='*60}")
    print(f"Loaded {len(variables)} variables")
    print(f"{'='*60}\n")
    
    # Print summary by area
    for area in ['pre-treatment', 'e-coat', 'production-control']:
        area_vars = loader.get_variables_by_area(area)
        print(f"{area.upper()}: {len(area_vars)} variables")
        
        # Show first 3 variables as examples
        for var in area_vars[:3]:
            print(f"  {var.variable_id}: {var.name}")
            print(f"    Range: {var.min_range} - {var.max_range} {var.unit}")
            print(f"    Alarms: {var.alarm_low:.2f} - {var.alarm_high:.2f}")
        
        if len(area_vars) > 3:
            print(f"  ... and {len(area_vars) - 3} more")
        print()


if __name__ == "__main__":
    main()
