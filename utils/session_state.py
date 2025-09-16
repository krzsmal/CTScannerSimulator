"""
Session state management utilities
"""

import streamlit as st
from typing import Dict, Any
from config.constants import SessionKeys


class SessionStateManager:
    """Manages Streamlit session state for CT Scanner Simulator"""
    
    @staticmethod
    def initialize() -> None:
        """Initialize all session state variables with default values"""
        default_values = {
            SessionKeys.GENERATED_SINOGRAM: None,
            SessionKeys.TOTAL_PROJECTION_STEPS: 0,
            SessionKeys.SINOGRAM_GENERATION_PARAMS: {},
            SessionKeys.GRAYSCALE_IMAGE: None,
            SessionKeys.UPLOADED_IMAGE_FILENAME: None,
            SessionKeys.RECONSTRUCTION_FRAME_LIST: [],
            SessionKeys.RECONSTRUCTION_CURRENT_FRAME_INDEX: 0,
            SessionKeys.IS_ANIMATING_RECONSTRUCTION: False,
            SessionKeys.RECONSTRUCTION_VIEW_MODE_SELECTION: "Full",
            SessionKeys.SINOGRAM_CURRENT_FRAME_INDEX: 10,
            SessionKeys.IS_ANIMATING_SINOGRAM: False,
            SessionKeys.SINOGRAM_VIEW_MODE_SELECTION: "Full",
            SessionKeys.RMSE_ERROR_VALUES: [],
            SessionKeys.USE_RAMP_FILTER: False,
        }
        
        for key, default_value in default_values.items():
            if key not in st.session_state:
                st.session_state[key] = default_value

    @staticmethod
    def reset_on_new_image() -> None:
        """Reset relevant session state when new image is uploaded"""
        reset_keys = [
            SessionKeys.PATIENT_NAME,
            SessionKeys.PATIENT_ID,
            SessionKeys.PATIENT_BIRTH_DATE,
            SessionKeys.PATIENT_SEX,
            SessionKeys.PATIENT_AGE,
            SessionKeys.STUDY_DATE,
            SessionKeys.STUDY_TIME,
            SessionKeys.CONTENT_DATE,
            SessionKeys.CONTENT_TIME,
            SessionKeys.STUDY_DESCRIPTION,
            SessionKeys.IMAGE_COMMENTS,
            SessionKeys.GENERATED_SINOGRAM,
            SessionKeys.TOTAL_PROJECTION_STEPS,
            SessionKeys.SINOGRAM_GENERATION_PARAMS,
            SessionKeys.RECONSTRUCTION_FRAME_LIST,
            SessionKeys.IS_ANIMATING_RECONSTRUCTION,
            SessionKeys.RECONSTRUCTION_CURRENT_FRAME_INDEX,
            SessionKeys.IS_ANIMATING_SINOGRAM,
            SessionKeys.SINOGRAM_CURRENT_FRAME_INDEX,
            SessionKeys.RMSE_ERROR_VALUES,
        ]
        
        for key in reset_keys:
            if key in [SessionKeys.GENERATED_SINOGRAM, SessionKeys.TOTAL_PROJECTION_STEPS,
                       SessionKeys.SINOGRAM_GENERATION_PARAMS, SessionKeys.RECONSTRUCTION_FRAME_LIST,
                       SessionKeys.RMSE_ERROR_VALUES]:
                st.session_state[key] = [] if 'list' in key.lower() else None if 'sinogram' in key.lower() else 0
            else:
                st.session_state[key] = None
        
        # Reset view modes
        st.session_state[SessionKeys.RECONSTRUCTION_VIEW_MODE_SELECTION] = "Full"
        st.session_state[SessionKeys.SINOGRAM_VIEW_MODE_SELECTION] = "Full"
        st.session_state[SessionKeys.IS_ANIMATING_RECONSTRUCTION] = False
        st.session_state[SessionKeys.IS_ANIMATING_SINOGRAM] = False

    @staticmethod
    def reset_sinogram_state() -> None:
        """Reset sinogram-related session state"""
        st.session_state[SessionKeys.GENERATED_SINOGRAM] = None
        st.session_state[SessionKeys.TOTAL_PROJECTION_STEPS] = 0
        st.session_state[SessionKeys.SINOGRAM_GENERATION_PARAMS] = {}

    @staticmethod
    def reset_reconstruction_state() -> None:
        """Reset reconstruction-related session state"""
        st.session_state[SessionKeys.RECONSTRUCTION_FRAME_LIST] = []
        st.session_state[SessionKeys.IS_ANIMATING_RECONSTRUCTION] = False
        st.session_state[SessionKeys.RECONSTRUCTION_CURRENT_FRAME_INDEX] = 0
        st.session_state[SessionKeys.IS_ANIMATING_SINOGRAM] = False
        st.session_state[SessionKeys.SINOGRAM_CURRENT_FRAME_INDEX] = 0
        st.session_state[SessionKeys.RMSE_ERROR_VALUES] = []

    @staticmethod
    def update_with_dicom_data(metadata: Dict[str, Any]) -> None:
        """Update session state with DICOM metadata"""
        metadata_mapping = {
            'patient_name': SessionKeys.PATIENT_NAME,
            'patient_id': SessionKeys.PATIENT_ID,
            'patient_birth_date': SessionKeys.PATIENT_BIRTH_DATE,
            'patient_sex': SessionKeys.PATIENT_SEX,
            'patient_age': SessionKeys.PATIENT_AGE,
            'study_date': SessionKeys.STUDY_DATE,
            'study_time': SessionKeys.STUDY_TIME,
            'content_date': SessionKeys.CONTENT_DATE,
            'content_time': SessionKeys.CONTENT_TIME,
            'study_description': SessionKeys.STUDY_DESCRIPTION,
            'image_comments': SessionKeys.IMAGE_COMMENTS,
            'grayscale_image': SessionKeys.GRAYSCALE_IMAGE,
        }
        
        for metadata_key, session_key in metadata_mapping.items():
            st.session_state[session_key] = metadata.get(metadata_key, None)

    @staticmethod
    def get(key: str, default=None):
        """Safe getter for session state values"""
        return st.session_state.get(key, default)

    @staticmethod
    def set(key: str, value: Any) -> None:
        """Safe setter for session state values"""
        st.session_state[key] = value