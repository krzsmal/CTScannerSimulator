"""
File handling utilities
"""

import datetime
from config.constants import INVALID_FILENAME_CHARS, MAX_FILENAME_LENGTH


class FileNameGenerator:
    """Generates and sanitizes filenames"""
    
    @staticmethod
    def generate_default_dicom_filename(patient_name: str, patient_id: str) -> str:
        """Generate a default filename for DICOM file based on patient information"""
        # Clean and format patient name for filename
        if patient_name:
            clean_name = FileNameGenerator._clean_string_for_filename(patient_name, 20)
        else:
            clean_name = ""
        
        # Clean patient ID
        if patient_id:
            clean_id = FileNameGenerator._clean_string_for_filename(patient_id, 15)
        else:
            clean_id = ""
        
        # Generate timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Construct filename
        filename_parts = []
        if clean_name:
            filename_parts.append(clean_name)
        if clean_id:
            filename_parts.append(clean_id)
        filename_parts.append(timestamp)
        
        if not filename_parts[:-1]:  # Only timestamp available
            filename_parts = ["CT_reconstruction", timestamp]
        
        return "_".join(filename_parts)

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to remove invalid characters and ensure .dcm extension"""
        # Remove or replace invalid filename characters
        sanitized = ''.join(c if c not in INVALID_FILENAME_CHARS else '_' for c in filename)
        
        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip('. ')
        
        # Limit filename length
        if len(sanitized) > MAX_FILENAME_LENGTH:
            sanitized = sanitized[:MAX_FILENAME_LENGTH]
        
        # Ensure filename is not empty
        if not sanitized:
            sanitized = "output"
        
        # Add .dcm extension if not present
        if not sanitized.lower().endswith('.dcm'):
            sanitized += '.dcm'
        
        return sanitized

    @staticmethod
    def _clean_string_for_filename(input_string: str, max_length: int) -> str:
        """Clean string for use in filename"""
        # Remove special characters and replace spaces with underscores
        clean_string = ''.join(c for c in input_string if c.isalnum() or c in ' -_').strip()
        clean_string = clean_string.replace(' ', '_')
        
        # Limit length
        if len(clean_string) > max_length:
            clean_string = clean_string[:max_length]
        
        return clean_string


class FileValidator:
    """Validates file operations"""
    
    @staticmethod
    def is_supported_image_type(filename: str) -> bool:
        """Check if file type is supported"""
        from config.constants import SUPPORTED_IMAGE_TYPES
        return any(filename.lower().endswith(f".{ext}") for ext in SUPPORTED_IMAGE_TYPES)
    
    @staticmethod
    def is_dicom_file(filename: str) -> bool:
        """Check if file is a DICOM file"""
        return filename.lower().endswith('.dcm')