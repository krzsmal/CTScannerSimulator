"""
Geometry calculations for CT Scanner Simulator
"""

import numpy as np
from typing import Tuple


class CTGeometry:
    """Handles CT scanner geometry calculations"""
    
    @staticmethod
    def calculate_geometry_parameters(image_shape: Tuple[int, int]) -> Tuple[float, float, float]:
        """Calculate geometry parameters for cone beam CT"""
        image_height, image_width = image_shape
        image_center_x = image_width / 2
        image_center_y = image_height / 2
        rotation_radius = np.sqrt(image_center_x**2 + image_center_y**2)
        
        return image_center_x, image_center_y, rotation_radius

    @staticmethod
    def calculate_source_position(center_x: float, center_y: float, radius: float, angle_rad: float) -> Tuple[float, float]:
        """Calculate X-ray source position for given angle"""
        source_x = center_x + radius * np.cos(angle_rad)
        source_y = center_y + radius * np.sin(angle_rad)
        return source_x, source_y

    @staticmethod
    def calculate_detector_position(
        center_x: float, 
        center_y: float, 
        radius: float, 
        base_angle: float, 
        detector_index: int,
        detector_span_rad: float, 
        detector_count: int
    ) -> Tuple[float, float]:
        """Calculate detector position for given parameters"""
        detector_angular_spacing = detector_span_rad / (detector_count - 1)
        detector_angle = (base_angle - (detector_span_rad / 2) + detector_index * detector_angular_spacing)
        
        detector_x = center_x + radius * np.cos(detector_angle)
        detector_y = center_y + radius * np.sin(detector_angle)
        
        return detector_x, detector_y

    @staticmethod
    def degrees_to_radians(degrees: float) -> float:
        """Convert degrees to radians"""
        return np.deg2rad(degrees)

    @staticmethod
    def calculate_detector_base_angle(source_angle_rad: float) -> float:
        """Calculate base detector angle (opposite to source)"""
        return source_angle_rad + np.pi