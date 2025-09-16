"""
Main CT Scanner simulation logic
"""

import numpy as np
from typing import List, Tuple
from core.geometry import CTGeometry
from core.image_processing import ImageProcessor, RayTracer, FilterProcessor


class CTScanner:
    """Main CT Scanner class that handles sinogram generation and reconstruction"""
    
    def __init__(self):
        self.geometry = CTGeometry()
        self.ray_tracer = RayTracer()
        self.image_processor = ImageProcessor()
        self.filter_processor = FilterProcessor()

    def generate_cone_beam_sinogram(
        self, 
        image: np.ndarray, 
        angular_step_degrees: float, 
        detector_span_degrees: float, 
        detector_count: int
    ) -> Tuple[np.ndarray, int]:
        """Generate sinogram using cone beam CT model"""
        
        image_center_x, image_center_y, rotation_radius = self.geometry.calculate_geometry_parameters(image.shape)
        
        detector_span_radians = self.geometry.degrees_to_radians(detector_span_degrees)
        sinogram_projections = []
        current_angle_degrees = 0.0
        total_projection_steps = 0

        while current_angle_degrees < 360.0:
            current_angle_radians = self.geometry.degrees_to_radians(current_angle_degrees)
            current_projection = []

            # Calculate source position
            source_x, source_y = self.geometry.calculate_source_position(
                image_center_x, image_center_y, rotation_radius, current_angle_radians
            )

            detector_base_angle = self.geometry.calculate_detector_base_angle(current_angle_radians)

            for detector_index in range(detector_count):
                # Calculate detector position
                detector_x, detector_y = self.geometry.calculate_detector_position(
                    image_center_x, image_center_y, rotation_radius,
                    detector_base_angle, detector_index, detector_span_radians, detector_count
                )

                # Calculate ray path
                ray_points = self.ray_tracer.calculate_bresenham_line_points(
                    image.shape[0], image.shape[1],
                    int(round(source_x)), int(round(source_y)),
                    int(round(detector_x)), int(round(detector_y))
                )

                # Calculate ray intensity
                ray_intensity = self.ray_tracer.calculate_average_brightness_along_line(image, ray_points)
                current_projection.append(ray_intensity)

            sinogram_projections.append(current_projection)
            total_projection_steps += 1
            current_angle_degrees += angular_step_degrees

        # Normalize sinogram
        sinogram_array = np.array(sinogram_projections)
        normalized_sinogram = self.image_processor.normalize_array(sinogram_array)
        
        return normalized_sinogram, total_projection_steps

    def reconstruct_image_backprojection_frames(
        self, 
        sinogram: np.ndarray, 
        original_image_shape: Tuple[int, int], 
        angular_step_degrees: float,
        detector_span_degrees: float, 
        detector_count: int
    ) -> List[np.ndarray]:
        """Reconstruct image using backprojection, returning frames for animation"""
        
        image_height, image_width = original_image_shape
        image_center_x, image_center_y, rotation_radius = self.geometry.calculate_geometry_parameters(original_image_shape)
        
        detector_span_radians = self.geometry.degrees_to_radians(detector_span_degrees)
        reconstruction_frames = []
        reconstruction_image = np.zeros((image_height, image_width), dtype=np.float32)

        current_angle_degrees = 0.0
        total_steps = sinogram.shape[0]

        for step_index in range(total_steps):
            current_angle_radians = self.geometry.degrees_to_radians(current_angle_degrees)

            # Calculate source position
            source_x, source_y = self.geometry.calculate_source_position(
                image_center_x, image_center_y, rotation_radius, current_angle_radians
            )

            detector_base_angle = self.geometry.calculate_detector_base_angle(current_angle_radians)

            for detector_index in range(detector_count):
                # Calculate detector position
                detector_x, detector_y = self.geometry.calculate_detector_position(
                    image_center_x, image_center_y, rotation_radius,
                    detector_base_angle, detector_index, detector_span_radians, detector_count
                )

                # Calculate ray path
                ray_points = self.ray_tracer.calculate_bresenham_line_points(
                    image_height, image_width,
                    int(round(source_x)), int(round(source_y)),
                    int(round(detector_x)), int(round(detector_y))
                )

                # Backproject sinogram value
                sinogram_value = sinogram[step_index, detector_index]
                for x, y in ray_points:
                    reconstruction_image[y, x] += sinogram_value

            reconstruction_frames.append(reconstruction_image.copy())
            current_angle_degrees += angular_step_degrees

        return reconstruction_frames

    def apply_filter_to_sinogram(self, sinogram: np.ndarray) -> np.ndarray:
        """Apply ramp filter to sinogram"""
        return self.filter_processor.apply_ramp_filter_to_sinogram(sinogram)

    def calculate_reconstruction_quality(
        self, 
        original_image: np.ndarray, 
        reconstructed_frames: List[np.ndarray]
    ) -> List[float]:
        """Calculate RMSE for all reconstruction frames"""
        rmse_values = []
        for frame in reconstructed_frames:
            rmse_value = self.image_processor.calculate_rmse(original_image, frame)
            rmse_values.append(rmse_value)
        return rmse_values