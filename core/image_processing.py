"""
Image processing utilities for CT Scanner Simulator
"""

import numpy as np
import skimage as sk
from typing import List, Tuple
from config.constants import FILTER_KERNEL_SIZE, NORMALIZATION_PERCENTILE


class ImageProcessor:
    """Handles image processing operations"""
    
    @staticmethod
    def load_image_from_file(image_path: str) -> np.ndarray:
        """Load and normalize image from file path"""
        image = sk.io.imread(image_path, as_gray=True)
        return sk.util.img_as_float64(image)

    @staticmethod
    def normalize_array(array: np.ndarray) -> np.ndarray:
        """Normalize array to 0-1 range"""
        array_min = array.min()
        array_max = array.max()
        
        array = array - array_min
        if array_max != array_min:
            array = array / (array_max - array_min)
        
        return array

    @staticmethod
    def normalize_image_to_0_255(image: np.ndarray) -> np.ndarray:
        """Normalize image to 0-255 range"""
        normalized = ImageProcessor.normalize_array(image.copy())
        return (normalized * 255).astype(np.uint8)

    @staticmethod
    def calculate_rmse(original_image: np.ndarray, reconstructed_image: np.ndarray) -> float:
        """Calculate Root Mean Square Error between two images"""
        normalized_original = ImageProcessor.normalize_array(original_image.copy())
        normalized_reconstructed = ImageProcessor.normalize_array(reconstructed_image.copy())
        return np.sqrt(np.mean((normalized_original - normalized_reconstructed) ** 2))


class FilterProcessor:
    """Handles filtering operations for CT reconstruction"""
    
    @staticmethod
    def create_ramp_filter_kernel(kernel_size: int = FILTER_KERNEL_SIZE) -> np.ndarray:
        """Create ramp filter kernel for filtered backprojection"""
        kernel_center = kernel_size // 2
        ramp_filter_kernel = np.zeros(kernel_size)

        for i in range(kernel_size):
            n = i - kernel_center
            if n == 0:
                ramp_filter_kernel[i] = 1
            elif n % 2 == 0:
                ramp_filter_kernel[i] = 0
            else:
                ramp_filter_kernel[i] = -4 / (np.pi ** 2 * n ** 2)

        return ramp_filter_kernel

    @staticmethod
    def apply_ramp_filter_to_sinogram(sinogram: np.ndarray) -> np.ndarray:
        """Apply ramp filter to sinogram for filtered backprojection"""
        ramp_filter_kernel = FilterProcessor.create_ramp_filter_kernel()
        filtered_sinogram = np.zeros_like(sinogram)

        # Apply filter to each projection
        for projection_index in range(sinogram.shape[0]):
            filtered_sinogram[projection_index, :] = np.convolve(
                sinogram[projection_index, :], 
                ramp_filter_kernel, 
                mode='same'
            )

        # Clip negative values and normalize
        filtered_sinogram = np.clip(
            filtered_sinogram, 
            0, 
            np.percentile(filtered_sinogram, NORMALIZATION_PERCENTILE)
        )
        return filtered_sinogram


class RayTracer:
    """Handles ray tracing operations using Bresenham's algorithm"""
    
    @staticmethod
    def calculate_bresenham_line_points(
        image_height: int, 
        image_width: int, 
        start_x: int, 
        start_y: int, 
        end_x: int, 
        end_y: int
    ) -> List[Tuple[int, int]]:
        """Calculate points along a line using Bresenham's algorithm"""
        line_points = []
        
        delta_x = abs(end_x - start_x)
        delta_y = abs(end_y - start_y)
        step_x = 1 if start_x < end_x else -1
        step_y = 1 if start_y < end_y else -1
        error = delta_x - delta_y

        current_x, current_y = start_x, start_y

        while True:
            # Only add valid points within image bounds
            if 0 <= current_x < image_width and 0 <= current_y < image_height:
                line_points.append((current_x, current_y))
            
            if current_x == end_x and current_y == end_y:
                break
                
            error_doubled = error * 2
            if error_doubled > -delta_y:
                error -= delta_y
                current_x += step_x
            if error_doubled < delta_x:
                error += delta_x
                current_y += step_y

        return line_points

    @staticmethod
    def calculate_average_brightness_along_line(
        image: np.ndarray, 
        line_points: List[Tuple[int, int]]
    ) -> float:
        """Calculate average brightness along a line of points"""
        if not line_points:
            return 0.0
        
        brightness_sum = 0.0
        valid_point_count = 0

        for x, y in line_points:
            if 0 <= x < image.shape[1] and 0 <= y < image.shape[0]:
                brightness_sum += image[y, x]
                valid_point_count += 1

        return brightness_sum / valid_point_count if valid_point_count > 0 else 0.0