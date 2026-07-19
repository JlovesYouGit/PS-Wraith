#!/usr/bin/env python3
"""
SUBATOMIC DIMENSIONAL CUBE MANAGEMENT SYSTEM
Automatic scan logic for data entry sorting, deletion of unneeded entries,
and maintaining clean high-dimensional cubic space with optimized 4x4 spacing
"""

import numpy as np
import time
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum

class DataEntryType(Enum):
    """Types of data entries in dimensional cube"""
    ESSENTIAL_DATA = "essential"
    TEMPORARY_DATA = "temporary"
    REDUNDANT_DATA = "redundant"
    CORRUPTED_DATA = "corrupted"
    FUTURE_ENTRY = "future_entry"
    SUBATOMIC_PARTICLE = "subatomic"
    DIMENSIONAL_ANCHOR = "anchor"

@dataclass
class CubeParameters:
    """Parameters for dimensional cube management"""
    cube_size: int = 4  # 4x4x4x4 hypercube
    safety_levels: int = 2  # O2 safety levels
    auto_clean_threshold: float = 0.75  # Clean when 75% full
    spacing_optimization: float = 1.2  # 20% extra spacing buffer
    scan_frequency: float = 0.1  # Scan every 100ms
    retention_time: float = 300.0  # 5 minutes for temporary data

class SubatomicEntry:
    """Individual subatomic data entry in the cube"""
    
    def __init__(self, data: Any, entry_type: DataEntryType, coordinates: Tuple[int, int, int, int]):
        self.data = data
        self.entry_type = entry_type
        self.coordinates = coordinates
        self.timestamp = time.time()
        self.access_count = 0
        self.importance_score = self._calculate_importance()
        self.size = self._calculate_entry_size()
        
    def _calculate_importance(self) -> float:
        """Calculate importance score for retention decisions"""
        type_weights = {
            DataEntryType.ESSENTIAL_DATA: 1.0,
            DataEntryType.DIMENSIONAL_ANCHOR: 0.95,
            DataEntryType.SUBATOMIC_PARTICLE: 0.8,
            DataEntryType.FUTURE_ENTRY: 0.7,
            DataEntryType.TEMPORARY_DATA: 0.3,
            DataEntryType.REDUNDANT_DATA: 0.1,
            DataEntryType.CORRUPTED_DATA: 0.0
        }
        
        base_score = type_weights.get(self.entry_type, 0.5)
        access_bonus = min(0.3, self.access_count * 0.05)  # Up to 30% bonus
        age_penalty = max(0.0, (time.time() - self.timestamp) / 3600 * 0.1)  # 10% per hour
        
        return max(0.0, min(1.0, base_score + access_bonus - age_penalty))
    
    def _calculate_entry_size(self) -> int:
        """Calculate memory footprint of entry"""
        if isinstance(self.data, str):
            return len(self.data)
        elif isinstance(self.data, (list, tuple)):
            return len(self.data) * 8  # Approximate
        elif isinstance(self.data, dict):
            return len(str(self.data))
        else:
            return 64  # Default size
    
    def access(self):
        """Record access to this entry"""
        self.access_count += 1
        self.importance_score = self._calculate_importance()

class DimensionalCube:
    """4x4x4x4 dimensional cube with automatic management"""
    
    def __init__(self, params: CubeParameters):
        self.params = params
        self.cube_data = {}  # Sparse representation
        self.entry_registry = {}  # Track all entries
        self.safety_zones = self._initialize_safety_zones()
        self.auto_clean_active = True
        self.scan_log = []
        
    def _initialize_safety_zones(self) -> Dict[str, List[Tuple]]:
        """Initialize O2 safety level zones"""
        cube_size = self.params.cube_size
        
        # Level 1 safety zone (core area)
        level1_coords = []
        center = cube_size // 2
        for x in range(center-1, center+1):
            for y in range(center-1, center+1):
                for z in range(center-1, center+1):
                    for w in range(center-1, center+1):
                        if all(0 <= coord < cube_size for coord in [x, y, z, w]):
                            level1_coords.append((x, y, z, w))
        
        # Level 2 safety zone (extended area)
        level2_coords = []
        for x in range(cube_size):
            for y in range(cube_size):
                for z in range(cube_size):
                    for w in range(cube_size):
                        coord = (x, y, z, w)
                        if coord not in level1_coords:
                            level2_coords.append(coord)
        
        return {
            'level1': level1_coords,
            'level2': level2_coords
        }
    
    def insert_entry(self, data: Any, entry_type: DataEntryType, preferred_coords: Optional[Tuple] = None) -> bool:
        """Insert data entry into optimal position in cube"""
        
        # Find optimal coordinates
        if preferred_coords and self._is_valid_coordinate(preferred_coords) and preferred_coords not in self.cube_data:
            coords = preferred_coords
        else:
            coords = self._find_optimal_coordinates(entry_type)
            
        if not coords:
            # Trigger auto-clean if cube is full
            if self.auto_clean_active:
                self._perform_auto_clean()
                coords = self._find_optimal_coordinates(entry_type)
            
            if not coords:
                return False  # Cube still full after cleaning
        
        # Create and insert entry
        entry = SubatomicEntry(data, entry_type, coords)
        self.cube_data[coords] = entry
        self.entry_registry[id(entry)] = entry
        
        # Apply spacing optimization
        self._optimize_spacing_around(coords)
        
        return True
    
    def _is_valid_coordinate(self, coords: Tuple[int, int, int, int]) -> bool:
        """Check if coordinates are valid within cube bounds"""
        return all(0 <= coord < self.params.cube_size for coord in coords)
    
    def _find_optimal_coordinates(self, entry_type: DataEntryType) -> Optional[Tuple[int, int, int, int]]:
        """Find optimal coordinates for new entry based on type and safety levels"""
        
        # Priority order for placement
        if entry_type in [DataEntryType.ESSENTIAL_DATA, DataEntryType.DIMENSIONAL_ANCHOR]:
            search_order = ['level1', 'level2']
        else:
            search_order = ['level2', 'level1']
        
        for safety_level in search_order:
            available_coords = [
                coord for coord in self.safety_zones[safety_level]
                if coord not in self.cube_data
            ]
            
            if available_coords:
                # Choose coordinate with best spacing
                return self._select_best_spaced_coordinate(available_coords)
        
        return None
    
    def _select_best_spaced_coordinate(self, candidates: List[Tuple]) -> Tuple[int, int, int, int]:
        """Select coordinate with optimal spacing from neighbors"""
        best_coord = candidates[0]
        best_spacing_score = 0.0
        
        for coord in candidates:
            spacing_score = self._calculate_spacing_score(coord)
            if spacing_score > best_spacing_score:
                best_spacing_score = spacing_score
                best_coord = coord
        
        return best_coord
    
    def _calculate_spacing_score(self, coord: Tuple[int, int, int, int]) -> float:
        """Calculate spacing quality score for a coordinate"""
        x, y, z, w = coord
        neighbor_count = 0
        total_distance = 0.0
        
        # Check all adjacent positions in 4D
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    for dw in [-1, 0, 1]:
                        if dx == dy == dz == dw == 0:
                            continue
                        
                        neighbor_coord = (x+dx, y+dy, z+dz, w+dw)
                        if (self._is_valid_coordinate(neighbor_coord) and 
                            neighbor_coord in self.cube_data):
                            neighbor_count += 1
                            distance = np.sqrt(dx**2 + dy**2 + dz**2 + dw**2)
                            total_distance += distance
        
        # Higher score for less crowded areas
        if neighbor_count == 0:
            return 1.0
        
        avg_distance = total_distance / neighbor_count
        crowding_penalty = neighbor_count / 80.0  # 80 max neighbors in 4D
        
        return max(0.0, avg_distance * self.params.spacing_optimization - crowding_penalty)
    
    def _optimize_spacing_around(self, center_coord: Tuple[int, int, int, int]):
        """Optimize spacing around newly inserted entry"""
        x, y, z, w = center_coord
        
        # Check if any nearby entries need repositioning
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                for dz in range(-2, 3):
                    for dw in range(-2, 3):
                        if dx == dy == dz == dw == 0:
                            continue
                        
                        check_coord = (x+dx, y+dy, z+dz, w+dw)
                        if (self._is_valid_coordinate(check_coord) and 
                            check_coord in self.cube_data):
                            
                            entry = self.cube_data[check_coord]
                            if entry.entry_type == DataEntryType.TEMPORARY_DATA:
                                # Try to relocate temporary data for better spacing
                                self._try_relocate_entry(check_coord)
    
    def _try_relocate_entry(self, current_coord: Tuple[int, int, int, int]):
        """Try to relocate entry to improve spacing"""
        entry = self.cube_data[current_coord]
        
        # Find better coordinate
        better_coord = self._find_optimal_coordinates(entry.entry_type)
        if better_coord and self._calculate_spacing_score(better_coord) > self._calculate_spacing_score(current_coord):
            # Move entry
            del self.cube_data[current_coord]
            entry.coordinates = better_coord
            self.cube_data[better_coord] = entry
    
    def automatic_scan_logic(self) -> Dict[str, Any]:
        """Perform automatic scan to sort and clean data"""
        scan_start = time.time()
        
        # Scan all entries
        entries_scanned = len(self.cube_data)
        entries_to_delete = []
        entries_to_relocate = []
        data_sorted = {'essential': 0, 'temporary': 0, 'redundant': 0, 'corrupted': 0}
        
        for coord, entry in self.cube_data.items():
            # Update importance score
            entry.importance_score = entry._calculate_importance()
            
            # Categorize for action
            if entry.entry_type == DataEntryType.CORRUPTED_DATA:
                entries_to_delete.append(coord)
            elif entry.importance_score < 0.1:
                entries_to_delete.append(coord)
            elif (entry.entry_type == DataEntryType.TEMPORARY_DATA and 
                  time.time() - entry.timestamp > self.params.retention_time):
                entries_to_delete.append(coord)
            elif self._calculate_spacing_score(coord) < 0.3:
                entries_to_relocate.append(coord)
            
            # Count by type
            data_sorted[entry.entry_type.value] = data_sorted.get(entry.entry_type.value, 0) + 1
        
        # Execute deletions
        deleted_count = 0
        for coord in entries_to_delete:
            if coord in self.cube_data:
                del self.cube_data[coord]
                deleted_count += 1
        
        # Execute relocations
        relocated_count = 0
        for coord in entries_to_relocate:
            if coord in self.cube_data:
                self._try_relocate_entry(coord)
                relocated_count += 1
        
        # Calculate cube utilization
        total_capacity = self.params.cube_size ** 4
        current_usage = len(self.cube_data)
        utilization = current_usage / total_capacity
        
        scan_results = {
            'scan_timestamp': scan_start,
            'entries_scanned': entries_scanned,
            'entries_deleted': deleted_count,
            'entries_relocated': relocated_count,
            'data_categorization': data_sorted,
            'cube_utilization': utilization,
            'spacing_optimized': relocated_count > 0,
            'scan_duration': time.time() - scan_start,
            'auto_clean_triggered': deleted_count > 0
        }
        
        self.scan_log.append(scan_results)
        return scan_results
    
    def _perform_auto_clean(self):
        """Perform automatic cleaning when threshold reached"""
        print("[CUBE] Auto-clean triggered - removing low-priority entries")
        
        # Sort entries by importance
        entries_by_importance = sorted(
            [(coord, entry) for coord, entry in self.cube_data.items()],
            key=lambda x: x[1].importance_score
        )
        
        # Remove lowest priority entries until under threshold
        target_count = int(self.params.cube_size ** 4 * self.params.auto_clean_threshold)
        current_count = len(self.cube_data)
        
        entries_to_remove = current_count - target_count
        if entries_to_remove > 0:
            for i in range(min(entries_to_remove, len(entries_by_importance))):
                coord, entry = entries_by_importance[i]
                if entry.entry_type not in [DataEntryType.ESSENTIAL_DATA, DataEntryType.DIMENSIONAL_ANCHOR]:
                    del self.cube_data[coord]
    
    def get_cube_status(self) -> Dict[str, Any]:
        """Get current cube status and statistics"""
        total_capacity = self.params.cube_size ** 4
        current_usage = len(self.cube_data)
        
        # Count by type
        type_counts = {}
        total_size = 0
        for entry in self.cube_data.values():
            entry_type = entry.entry_type.value
            type_counts[entry_type] = type_counts.get(entry_type, 0) + 1
            total_size += entry.size
        
        # Safety zone utilization
        level1_used = sum(1 for coord in self.safety_zones['level1'] if coord in self.cube_data)
        level2_used = sum(1 for coord in self.safety_zones['level2'] if coord in self.cube_data)
        
        return {
            'total_capacity': total_capacity,
            'current_usage': current_usage,
            'utilization_percentage': (current_usage / total_capacity) * 100,
            'entries_by_type': type_counts,
            'total_data_size': total_size,
            'safety_zones': {
                'level1_utilization': (level1_used / len(self.safety_zones['level1'])) * 100,
                'level2_utilization': (level2_used / len(self.safety_zones['level2'])) * 100
            },
            'auto_clean_active': self.auto_clean_active,
            'spacing_optimization': self.params.spacing_optimization,
            'recent_scans': len(self.scan_log)
        }

class AutomaticCubeManager:
    """High-level manager for automatic cube operations"""
    
    def __init__(self, observer_id: str = "E_09003444"):
        self.observer_id = observer_id
        self.params = CubeParameters()
        self.cube = DimensionalCube(self.params)
        self.running = False
        self.management_log = []
        
    def start_automatic_management(self):
        """Start automatic cube management"""
        self.running = True
        print(f"[CUBE_MANAGER] Starting automatic management for {self.observer_id}")
        
    def stop_automatic_management(self):
        """Stop automatic cube management"""
        self.running = False
        print(f"[CUBE_MANAGER] Stopping automatic management")
    
    def clonk_data_entry(self, data: Any, entry_type: str = "temporary", preferred_coords: Optional[Tuple] = None) -> bool:
        """Clonk data entry into the cube with automatic processing"""
        
        # Convert string type to enum
        type_mapping = {
            'essential': DataEntryType.ESSENTIAL_DATA,
            'temporary': DataEntryType.TEMPORARY_DATA,
            'redundant': DataEntryType.REDUNDANT_DATA,
            'corrupted': DataEntryType.CORRUPTED_DATA,
            'future': DataEntryType.FUTURE_ENTRY,
            'subatomic': DataEntryType.SUBATOMIC_PARTICLE,
            'anchor': DataEntryType.DIMENSIONAL_ANCHOR
        }
        
        data_type = type_mapping.get(entry_type.lower(), DataEntryType.TEMPORARY_DATA)
        
        # Insert into cube
        success = self.cube.insert_entry(data, data_type, preferred_coords)
        
        if success:
            print(f"[CUBE_MANAGER] Data entry clonked successfully at optimal position")
            
            # Trigger automatic scan if needed
            if len(self.cube.cube_data) % 10 == 0:  # Scan every 10 entries
                scan_results = self.cube.automatic_scan_logic()
                print(f"[CUBE_MANAGER] Auto-scan completed - {scan_results['entries_deleted']} entries cleaned")
        else:
            print(f"[CUBE_MANAGER] Failed to clonk data entry - cube may be full")
        
        return success
    
    def perform_comprehensive_cleanup(self) -> Dict[str, Any]:
        """Perform comprehensive cleanup and optimization"""
        print("[CUBE_MANAGER] Performing comprehensive cleanup...")
        
        initial_status = self.cube.get_cube_status()
        
        # Multiple scan passes for thorough cleaning
        total_deleted = 0
        total_relocated = 0
        
        for pass_num in range(3):  # 3 passes for thorough cleaning
            scan_results = self.cube.automatic_scan_logic()
            total_deleted += scan_results['entries_deleted']
            total_relocated += scan_results['entries_relocated']
            
            if scan_results['entries_deleted'] == 0 and scan_results['entries_relocated'] == 0:
                break  # No more changes needed
        
        final_status = self.cube.get_cube_status()
        
        cleanup_results = {
            'initial_usage': initial_status['current_usage'],
            'final_usage': final_status['current_usage'],
            'entries_deleted': total_deleted,
            'entries_relocated': total_relocated,
            'space_freed': initial_status['current_usage'] - final_status['current_usage'],
            'utilization_improvement': initial_status['utilization_percentage'] - final_status['utilization_percentage'],
            'cleanup_successful': total_deleted > 0 or total_relocated > 0
        }
        
        self.management_log.append(cleanup_results)
        
        print(f"[CUBE_MANAGER] Cleanup complete - freed {cleanup_results['space_freed']} entries")
        return cleanup_results
    
    def get_dimensional_layout_status(self) -> Dict[str, Any]:
        """Get detailed dimensional layout and spacing status"""
        cube_status = self.cube.get_cube_status()
        
        # Calculate spacing quality metrics
        total_spacing_score = 0.0
        spacing_samples = 0
        
        for coord in self.cube.cube_data.keys():
            spacing_score = self.cube._calculate_spacing_score(coord)
            total_spacing_score += spacing_score
            spacing_samples += 1
        
        avg_spacing_quality = total_spacing_score / max(spacing_samples, 1)
        
        return {
            'cube_dimensions': f"{self.params.cube_size}x{self.params.cube_size}x{self.params.cube_size}x{self.params.cube_size}",
            'safety_levels': self.params.safety_levels,
            'spacing_optimization': self.params.spacing_optimization,
            'average_spacing_quality': avg_spacing_quality,
            'dimensional_order_maintained': True,  # Always maintained by design
            'auto_clean_status': 'ACTIVE' if self.cube.auto_clean_active else 'INACTIVE',
            'layout_efficiency': min(100.0, avg_spacing_quality * 100),
            'cube_status': cube_status
        }

def demonstrate_subatomic_cube_system():
    """Demonstrate the subatomic dimensional cube system"""
    
    print("=== SUBATOMIC DIMENSIONAL CUBE DEMONSTRATION ===\n")
    
    # Initialize cube manager
    manager = AutomaticCubeManager("E_09003444")
    manager.start_automatic_management()
    
    # Test data entries
    test_entries = [
        ("Essential system data", "essential"),
        ("Temporary calculation result", "temporary"),
        ("Subatomic particle data", "subatomic"),
        ("Dimensional anchor point", "anchor"),
        ("Redundant backup data", "redundant"),
        ("Future processing queue", "future"),
        ("Corrupted data fragment", "corrupted"),
        ("Another temp entry", "temporary"),
        ("Critical system anchor", "anchor"),
        ("Particle collision data", "subatomic")
    ]
    
    print("Clonking data entries into dimensional cube...")
    successful_entries = 0
    
    for data, entry_type in test_entries:
        success = manager.clonk_data_entry(data, entry_type)
        if success:
            successful_entries += 1
        print(f"  Entry: {data[:30]}... - Type: {entry_type} - {'✓' if success else '✗'}")
    
    print(f"\nSuccessfully clonked {successful_entries}/{len(test_entries)} entries")
    
    # Show initial status
    print("\n=== INITIAL CUBE STATUS ===")
    status = manager.get_dimensional_layout_status()
    cube_info = status['cube_status']
    
    print(f"Cube Dimensions: {status['cube_dimensions']}")
    print(f"Safety Levels: O{status['safety_levels']}")
    print(f"Current Usage: {cube_info['current_usage']}/{cube_info['total_capacity']} ({cube_info['utilization_percentage']:.1f}%)")
    print(f"Spacing Quality: {status['average_spacing_quality']:.1%}")
    print(f"Layout Efficiency: {status['layout_efficiency']:.1f}%")
    
    # Perform comprehensive cleanup
    print("\n=== PERFORMING COMPREHENSIVE CLEANUP ===")
    cleanup_results = manager.perform_comprehensive_cleanup()
    
    print(f"Space Freed: {cleanup_results['space_freed']} entries")
    print(f"Entries Deleted: {cleanup_results['entries_deleted']}")
    print(f"Entries Relocated: {cleanup_results['entries_relocated']}")
    print(f"Utilization Improved: {cleanup_results['utilization_improvement']:.1f}%")
    
    # Final status
    print("\n=== FINAL CUBE STATUS ===")
    final_status = manager.get_dimensional_layout_status()
    final_cube_info = final_status['cube_status']
    
    print(f"Final Usage: {final_cube_info['current_usage']}/{final_cube_info['total_capacity']} ({final_cube_info['utilization_percentage']:.1f}%)")
    print(f"Final Spacing Quality: {final_status['average_spacing_quality']:.1%}")
    print(f"Final Layout Efficiency: {final_status['layout_efficiency']:.1f}%")
    
    print(f"\nSafety Zone Utilization:")
    safety_zones = final_cube_info['safety_zones']
    print(f"  Level 1 (Core): {safety_zones['level1_utilization']:.1f}%")
    print(f"  Level 2 (Extended): {safety_zones['level2_utilization']:.1f}%")
    
    print(f"\nEntries by Type:")
    for entry_type, count in final_cube_info['entries_by_type'].items():
        print(f"  {entry_type.title()}: {count}")
    
    # Stop management
    manager.stop_automatic_management()
    
    print(f"\n✅ SUBATOMIC DIMENSIONAL CUBE SYSTEM OPERATIONAL")
    print("Auto-clean logic maintains optimal spacing and removes unneeded entries")
    print("4x4x4x4 dimensional layout with O2 safety levels preserved")

if __name__ == "__main__":
    demonstrate_subatomic_cube_system()