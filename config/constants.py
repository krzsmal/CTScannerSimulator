"""
Configuration constants for CT Scanner Simulator
"""

# Default simulation parameters
DEFAULT_ANGULAR_STEP = 1.0
DEFAULT_DETECTOR_COUNT = 360
DEFAULT_DETECTOR_SPAN = 270

# Filter parameters
FILTER_KERNEL_SIZE = 21
NORMALIZATION_PERCENTILE = 99

# Animation settings
ANIMATION_DELAY = 0.075

# DICOM constants
DICOM_MODALITY = 'CT'
DICOM_PHOTOMETRIC_INTERPRETATION = "MONOCHROME2"
DICOM_BITS_STORED = 16
DICOM_BITS_ALLOCATED = 16
DICOM_SAMPLES_PER_PIXEL = 1
DICOM_HIGH_BIT = 15
DICOM_PIXEL_REPRESENTATION = 0
DICOM_CHARACTER_SET = "ISO_IR 100"

# File settings
MAX_FILENAME_LENGTH = 50
INVALID_FILENAME_CHARS = '<>:"/\\|?*'

# Session state keys
class SessionKeys:
    """Centralized session state keys"""
    GENERATED_SINOGRAM = 'generated_sinogram'
    TOTAL_PROJECTION_STEPS = 'total_projection_steps'
    SINOGRAM_GENERATION_PARAMS = 'sinogram_generation_params'
    GRAYSCALE_IMAGE = 'grayscale_image'
    UPLOADED_IMAGE_FILENAME = 'uploaded_image_filename'
    RECONSTRUCTION_FRAME_LIST = 'reconstruction_frame_list'
    RECONSTRUCTION_CURRENT_FRAME_INDEX = 'reconstruction_current_frame_index'
    IS_ANIMATING_RECONSTRUCTION = 'is_animating_reconstruction'
    RECONSTRUCTION_VIEW_MODE_SELECTION = 'reconstruction_view_mode_selection'
    SINOGRAM_CURRENT_FRAME_INDEX = 'sinogram_current_frame_index'
    IS_ANIMATING_SINOGRAM = 'is_animating_sinogram'
    SINOGRAM_VIEW_MODE_SELECTION = 'sinogram_view_mode_selection'
    RMSE_ERROR_VALUES = 'rmse_error_values'
    USE_RAMP_FILTER = 'use_ramp_filter'
    PATIENT_NAME = 'patient_name'
    PATIENT_ID = 'patient_id'
    PATIENT_BIRTH_DATE = 'patient_birth_date'
    PATIENT_SEX = 'patient_sex'
    PATIENT_AGE = 'patient_age'
    STUDY_DATE = 'study_date'
    STUDY_TIME = 'study_time'
    CONTENT_DATE = 'content_date'
    CONTENT_TIME = 'content_time'
    STUDY_DESCRIPTION = 'study_description'
    IMAGE_COMMENTS = 'image_comments'

# UI constants
VIEW_MODE_OPTIONS = ("Full", "Iterative")
SUPPORTED_IMAGE_TYPES = ["jpg", "jpeg", "png", "dcm"]
PATIENT_SEX_OPTIONS = ["F", "M"]
