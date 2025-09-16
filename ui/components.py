"""
Reusable UI components for CT Scanner Simulator
"""

import streamlit as st
from typing import Tuple, List
from config.constants import VIEW_MODE_OPTIONS, SessionKeys


class AnimationControls:
    """Animation control components"""
    
    @staticmethod
    def render_play_pause_controls(
        play_key: str,
        pause_key: str,
        is_animating: bool,
        total_steps: int,
        current_frame: int,
        max_frame_callback,
        play_callback
    ) -> bool:
        """Render play/pause button controls"""
        animation_rerun_required = False
        
        control_columns = st.columns([1, 0.01, 1, 2])
        
        with control_columns[0]:
            is_play_disabled = is_animating or total_steps <= 1
            if st.button("▶", key=play_key, use_container_width=True, disabled=is_play_disabled):
                if current_frame >= max_frame_callback():
                    play_callback(0)  # Reset to beginning
                play_callback(True)  # Start animation
                animation_rerun_required = True

        with control_columns[2]:
            if st.button("⏸", key=pause_key, use_container_width=True, disabled=not is_animating):
                play_callback(False)  # Stop animation
                
        return animation_rerun_required

    @staticmethod
    def render_frame_slider(
        label: str,
        max_value: int,
        current_value: int,
        slider_key: str,
        on_change_callback
    ):
        """Render frame selection slider"""
        st.slider(
            label,
            min_value=1,
            max_value=max_value,
            value=current_value + 1,
            key=slider_key,
            on_change=on_change_callback
        )


class ViewModeSelector:
    """View mode selection component"""
    
    @staticmethod
    def render_view_mode_radio(
        current_selection: str,
        radio_key: str,
        on_change_callback,
        options: Tuple[str, ...] = VIEW_MODE_OPTIONS
    ) -> None:
        """Render view mode selection radio buttons"""
        current_index = 0
        try:
            current_index = options.index(current_selection)
        except ValueError:
            pass
            
        st.radio(
            "View Mode:",
            options=options,
            horizontal=True,
            key=radio_key,
            index=current_index,
            on_change=on_change_callback
        )


class ImageDisplay:
    """Image display components"""
    
    @staticmethod
    def render_image_with_caption(image_array, caption: str, normalize_func):
        """Render image with caption"""
        st.image(
            normalize_func(image_array),
            caption=caption,
            use_container_width=True
        )

    @staticmethod
    def render_rmse_display(rmse_value: float):
        """Render RMSE value display"""
        st.write(f"RMSE: {rmse_value:.6f}")


class MetadataDisplay:
    """DICOM metadata display components"""
    
    @staticmethod
    def render_dicom_metadata_fields(metadata_fields: List[Tuple[str, str]]):
        """Render DICOM metadata fields"""
        for session_key, display_name in metadata_fields:
            value = st.session_state.get(session_key)
            if value:
                st.write(f"{display_name}: {value}")

    @staticmethod
    def get_dicom_metadata_fields() -> List[Tuple[str, str]]:
        """Get list of DICOM metadata fields for display"""
        return [
            (SessionKeys.PATIENT_NAME, "Patient Name"),
            (SessionKeys.PATIENT_ID, "Patient ID"),
            (SessionKeys.PATIENT_BIRTH_DATE, "Birth Date"),
            (SessionKeys.PATIENT_SEX, "Sex"),
            (SessionKeys.PATIENT_AGE, "Age"),
            (SessionKeys.STUDY_DATE, "Study Date"),
            (SessionKeys.STUDY_TIME, "Study Time"),
            (SessionKeys.CONTENT_DATE, "Content Date"),
            (SessionKeys.CONTENT_TIME, "Content Time"),
            (SessionKeys.STUDY_DESCRIPTION, "Study Description"),
            (SessionKeys.IMAGE_COMMENTS, "Image Comments"),
        ]


class ProgressIndicators:
    """Progress and status indicators"""
    
    @staticmethod
    def show_processing_spinner(message: str):
        """Show processing spinner with message"""
        return st.spinner(message)

    @staticmethod
    def show_info_message(message: str):
        """Show info message"""
        st.info(message)

    @staticmethod
    def show_success_message(message: str):
        """Show success message"""
        st.success(message)

    @staticmethod
    def show_error_message(message: str):
        """Show error message"""
        st.error(message)

    @staticmethod
    def show_warning_message(message: str):
        """Show warning message"""
        st.warning(message)