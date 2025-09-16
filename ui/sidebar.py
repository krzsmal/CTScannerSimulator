"""
Sidebar UI components for CT Scanner Simulator
"""

import streamlit as st
import datetime
from typing import Tuple, Optional, Any
from config.constants import (
    DEFAULT_ANGULAR_STEP, DEFAULT_DETECTOR_COUNT, DEFAULT_DETECTOR_SPAN,
    SUPPORTED_IMAGE_TYPES, PATIENT_SEX_OPTIONS, SessionKeys
)
from utils.file_utils import FileNameGenerator
from ui.components import ProgressIndicators
from dicom.metadata import DICOMAgeCalculator


class SidebarController:
    """Controls sidebar UI elements"""
    
    def __init__(self):
        self.file_generator = FileNameGenerator()
        self.age_calculator = DICOMAgeCalculator()
        self.progress = ProgressIndicators()

    def render_sidebar(self) -> Tuple[Optional[Any], float, int, float, bool]:
        """Render complete sidebar and return parameter values"""
        st.sidebar.header("Simulation Parameters")
        
        # File upload
        uploaded_file = self._render_file_uploader()
        
        # CT scanner parameters
        angular_step, detector_count, detector_span, use_filter = self._render_ct_parameters()
        
        # Action buttons
        self._render_action_buttons()
        
        # DICOM save section
        if st.session_state.get(SessionKeys.RECONSTRUCTION_FRAME_LIST):
            self._render_dicom_save_section()
        
        return uploaded_file, angular_step, detector_count, detector_span, use_filter

    def _render_file_uploader(self):
        """Render file upload component"""
        return st.sidebar.file_uploader(
            "1. Choose an image", 
            type=SUPPORTED_IMAGE_TYPES
        )

    def _render_ct_parameters(self) -> Tuple[float, int, float, bool]:
        """Render CT scanner parameter inputs"""
        angular_step = st.sidebar.number_input(
            "2. Step Angle (Δα degrees)",
            min_value=0.1,
            max_value=360.0,
            value=DEFAULT_ANGULAR_STEP,
            step=0.1,
            format="%.1f",
            help="Angular increment between emitter/detector rotations"
        )

        detector_count = st.sidebar.number_input(
            "3. Number of Detectors (n)",
            min_value=1,
            value=DEFAULT_DETECTOR_COUNT,
            step=1,
            help="Number of detectors in the array for each projection"
        )

        detector_span = st.sidebar.number_input(
            "4. Detector Span (Φ)",
            min_value=1,
            max_value=360,
            value=DEFAULT_DETECTOR_SPAN,
            step=5,
            help="Angular width covered by the detector array in degrees"
        )

        use_filter = st.sidebar.checkbox(
            "Use Filtered Backprojection",
            value=st.session_state.get(SessionKeys.USE_RAMP_FILTER, False),
            help="Enable filtered backprojection for reconstruction"
        )

        st.session_state[SessionKeys.USE_RAMP_FILTER] = use_filter
        
        return angular_step, detector_count, detector_span, use_filter

    def _render_action_buttons(self):
        """Render main action buttons"""
        st.sidebar.button(
            "Generate Sinogram",
            disabled=(st.session_state.get(SessionKeys.GRAYSCALE_IMAGE) is None),
            key="generate_sinogram"
        )
        
        st.sidebar.button(
            "Reconstruct Image",
            disabled=(st.session_state.get(SessionKeys.GENERATED_SINOGRAM) is None),
            key="reconstruct_image"
        )

    def _render_dicom_save_section(self):
        """Render DICOM save section"""
        with st.sidebar.expander("💾 Save as DICOM", expanded=False):
            # Patient information inputs
            patient_inputs = self._render_patient_inputs()
            
            # File name input
            filename_input = self._render_filename_input(
                patient_inputs['patient_name'],
                patient_inputs['patient_id']
            )
            
            # Save button
            if st.button("Save as DICOM"):
                self._handle_dicom_save(patient_inputs, filename_input)

    def _render_patient_inputs(self) -> dict:
        """Render patient information input fields"""
        patient_name = st.text_input(
            "Patient Name",
            value=st.session_state.get(SessionKeys.PATIENT_NAME, "") or ""
        )
        
        patient_id = st.text_input(
            "Patient ID",
            value=st.session_state.get(SessionKeys.PATIENT_ID, "") or ""
        )
        
        # Birth date handling
        birth_date = self._get_birth_date_input()
        
        patient_sex = st.selectbox(
            "Sex",
            options=PATIENT_SEX_OPTIONS,
            help="F = Female, M = Male",
            index=0 if st.session_state.get(SessionKeys.PATIENT_SEX) == "F" else 1
        )
        
        study_description = st.text_input(
            "Description",
            value=st.session_state.get(SessionKeys.STUDY_DESCRIPTION, "") or ""
        )
        
        return {
            'patient_name': patient_name,
            'patient_id': patient_id,
            'birth_date': birth_date,
            'patient_sex': patient_sex,
            'study_description': study_description
        }

    def _get_birth_date_input(self) -> datetime.date:
        """Get birth date input with proper handling"""
        default_birth_date = datetime.date.today()
        birth_date_str = st.session_state.get(SessionKeys.PATIENT_BIRTH_DATE)
        
        if birth_date_str:
            try:
                default_birth_date = datetime.datetime.strptime(birth_date_str, "%d-%m-%Y").date()
            except ValueError:
                pass
                
        return st.date_input(
            "Birth Date",
            min_value=datetime.date(1900, 1, 1),
            max_value=datetime.date.today(),
            value=default_birth_date,
        )

    def _render_filename_input(self, patient_name: str, patient_id: str) -> str:
        """Render filename input with default suggestion"""
        default_filename = self.file_generator.generate_default_dicom_filename(patient_name, patient_id)
        
        return st.text_input(
            "File name",
            value=default_filename,
            help="Enter filename without extension (.dcm will be added automatically)"
        )

    def _handle_dicom_save(self, patient_inputs: dict, filename: str):
        """Handle DICOM save operation"""
        from ui.sections import DICOMSaveHandler
        
        # Calculate age
        patient_age_dicom = ""
        study_date_str = st.session_state.get(SessionKeys.STUDY_DATE)
        if study_date_str:
            try:
                study_date_obj = datetime.datetime.strptime(study_date_str, "%Y%m%d").date()
                patient_age_dicom = self.age_calculator.calculate_patient_age_dicom_format(patient_inputs['birth_date'], study_date_obj)
            except ValueError:
                pass
        
        # Format birth date for DICOM
        birth_date_dicom = patient_inputs['birth_date'].strftime("%Y%m%d")
        
        # Create save handler and execute
        save_handler = DICOMSaveHandler()
        save_handler.handle_dicom_save(
            patient_inputs['patient_name'],
            patient_inputs['patient_id'],
            patient_inputs['study_description'],
            birth_date_dicom,
            patient_inputs['patient_sex'],
            patient_age_dicom,
            filename
        )