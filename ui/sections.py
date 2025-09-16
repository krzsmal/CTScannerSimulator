"""
Main UI sections for CT Scanner Simulator
"""

import streamlit as st
import datetime
import matplotlib.pyplot as plt
import time
from typing import List, Tuple
from config.constants import SessionKeys, ANIMATION_DELAY
from ui.components import (
    ViewModeSelector, ImageDisplay, MetadataDisplay, 
    AnimationControls, ProgressIndicators
)
from core.image_processing import ImageProcessor
from core.ct_scanner import CTScanner
from dicom.dicom_handler import DICOMHandler
from utils.file_utils import FileNameGenerator
from utils.session_state import SessionStateManager


class InputImageSection:
    """Handles input image display section"""
    
    def __init__(self):
        self.image_processor = ImageProcessor()
        self.metadata_display = MetadataDisplay()

    def render(self):
        """Render input image section"""
        st.subheader("Input Image")
        
        grayscale_image = st.session_state.get(SessionKeys.GRAYSCALE_IMAGE)
        filename = st.session_state.get(SessionKeys.UPLOADED_IMAGE_FILENAME)
        
        if grayscale_image is not None:
            st.image(
                self.image_processor.normalize_image_to_0_255(grayscale_image),
                caption=f"Input: {filename}",
                use_container_width=True
            )
        else:
            st.info("Upload an image using the sidebar.")
        
        # Display DICOM metadata if available
        if filename and filename.endswith(".dcm"):
            self._render_dicom_metadata()

    def _render_dicom_metadata(self):
        """Render DICOM metadata information"""
        metadata_fields = self.metadata_display.get_dicom_metadata_fields()
        self.metadata_display.render_dicom_metadata_fields(metadata_fields)


class SinogramSection:
    """Handles sinogram display and generation"""
    
    def __init__(self):
        self.ct_scanner = CTScanner()
        self.session_manager = SessionStateManager()
        self.progress = ProgressIndicators()
        self.view_selector = ViewModeSelector()
        self.image_display = ImageDisplay()
        self.animation_controls = AnimationControls()

    def render(self, generate_button: bool, angular_step: float, detector_count: int, detector_span: float) -> bool:
        """Render sinogram section and return if animation rerun is required"""
        st.subheader("Sinogram")
        animation_rerun_required = False
        
        if generate_button:
            animation_rerun_required = self._handle_sinogram_generation(
                angular_step, detector_count, detector_span
            )
        
        # Display sinogram if available
        generated_sinogram = st.session_state.get(SessionKeys.GENERATED_SINOGRAM)
        if generated_sinogram is not None:
            animation_rerun_required = self._render_sinogram_display() or animation_rerun_required
        elif st.session_state.get(SessionKeys.GRAYSCALE_IMAGE) is not None:
            st.info("Click 'Generate Sinogram' in the sidebar.")
        
        return animation_rerun_required

    def _handle_sinogram_generation(self, angular_step: float, detector_count: int, detector_span: float) -> bool:
        """Handle sinogram generation process"""
        current_params = {
            'step': angular_step,
            'detectors': detector_count,
            'span': detector_span
        }
        
        grayscale_image = st.session_state.get(SessionKeys.GRAYSCALE_IMAGE)
        if grayscale_image is None:
            st.warning("Please upload an image first.")
            return False

        expected_steps = round(360 / angular_step)
        with self.progress.show_processing_spinner(f"Calculating Sinogram ({expected_steps} steps)..."):
            # Set timestamps
            current_time = datetime.datetime.now()
            st.session_state[SessionKeys.STUDY_DATE] = current_time.strftime("%Y%m%d")
            st.session_state[SessionKeys.STUDY_TIME] = current_time.strftime("%H%M%S")
            
            # Generate sinogram
            generated_sinogram, projection_steps = self.ct_scanner.generate_cone_beam_sinogram(
                grayscale_image, angular_step, float(detector_span), detector_count
            )
            
            if generated_sinogram is not None:
                # Apply filter if enabled
                if st.session_state.get(SessionKeys.USE_RAMP_FILTER, False):
                    generated_sinogram = self.ct_scanner.apply_filter_to_sinogram(generated_sinogram)
                #     plt.imsave("sinogram_filtered.png", ImageProcessor.normalize_image_to_0_255(generated_sinogram), cmap="gray")
                # else:
                #     plt.imsave("sinogram.png", ImageProcessor.normalize_image_to_0_255(generated_sinogram), cmap="gray")

                # Update session state
                st.session_state[SessionKeys.GENERATED_SINOGRAM] = generated_sinogram
                st.session_state[SessionKeys.TOTAL_PROJECTION_STEPS] = projection_steps
                st.session_state[SessionKeys.SINOGRAM_GENERATION_PARAMS] = current_params
                
                # Reset states
                self.session_manager.reset_reconstruction_state()
                st.session_state[SessionKeys.SINOGRAM_CURRENT_FRAME_INDEX] = projection_steps - 1
                st.session_state[SessionKeys.SINOGRAM_VIEW_MODE_SELECTION] = "Full"
                st.rerun()
            else:
                st.error("Failed to generate sinogram. Check parameters/image.")
                self.session_manager.reset_sinogram_state()
                
        return False

    def _render_sinogram_display(self) -> bool:
        """Render sinogram display with view modes"""
        total_steps = st.session_state.get(SessionKeys.TOTAL_PROJECTION_STEPS, 0)
        generation_params = st.session_state.get(SessionKeys.SINOGRAM_GENERATION_PARAMS, {})
        
        # View mode selection
        self.view_selector.render_view_mode_radio(
            st.session_state.get(SessionKeys.SINOGRAM_VIEW_MODE_SELECTION, "Full"),
            "sinogram_view_mode_radio",
            self._handle_sinogram_view_mode_change
        )
        
        # Handle iterative vs full display
        if (st.session_state.get(SessionKeys.SINOGRAM_VIEW_MODE_SELECTION) == "Iterative" 
            and total_steps > 0):
            return self._render_sinogram_animation(total_steps)
        else:
            self._render_static_sinogram(total_steps, generation_params)
            return False

    def _render_sinogram_animation(self, total_steps: int) -> bool:
        """Render sinogram animation controls and display"""
        animation_rerun_required = False
        
        # Animation controls
        animation_rerun_required = self.animation_controls.render_play_pause_controls(
            "play_sinogram_animation",
            "pause_sinogram_animation",
            st.session_state.get(SessionKeys.IS_ANIMATING_SINOGRAM, False),
            total_steps,
            st.session_state.get(SessionKeys.SINOGRAM_CURRENT_FRAME_INDEX, 0),
            lambda: total_steps - 1,
            self._handle_sinogram_animation_control
        ) or animation_rerun_required
        
        # Frame slider
        self.animation_controls.render_frame_slider(
            "Show up to step:",
            total_steps,
            st.session_state.get(SessionKeys.SINOGRAM_CURRENT_FRAME_INDEX, 0),
            "sinogram_slider_widget",
            self._handle_sinogram_slider_change
        )
        
        # Display current frame
        current_frame = st.session_state.get(SessionKeys.SINOGRAM_CURRENT_FRAME_INDEX, 0)
        if 0 <= current_frame < total_steps:
            partial_sinogram = self._create_partial_sinogram(current_frame)
            caption = f"Iterative View (Steps 1 to {current_frame + 1}/{total_steps})"
            self.image_display.render_image_with_caption(partial_sinogram, caption, ImageProcessor.normalize_image_to_0_255)
        else:
            st.session_state[SessionKeys.SINOGRAM_CURRENT_FRAME_INDEX] = 0
            animation_rerun_required = True
        
        # Handle animation progression
        if st.session_state.get(SessionKeys.IS_ANIMATING_SINOGRAM, False):
            if current_frame < total_steps - 1:
                st.session_state[SessionKeys.SINOGRAM_CURRENT_FRAME_INDEX] += 1
                animation_rerun_required = True
            else:
                st.session_state[SessionKeys.IS_ANIMATING_SINOGRAM] = False
                animation_rerun_required = True
        
        return animation_rerun_required

    def _render_static_sinogram(self, total_steps: int, generation_params: dict):
        """Render static sinogram display"""
        sinogram = st.session_state.get(SessionKeys.GENERATED_SINOGRAM)
        caption = (f"Final Sinogram ({total_steps} steps @ "
                  f"{generation_params.get('step', '?')}° x {generation_params.get('detectors', '?')} det.)")

        self.image_display.render_image_with_caption(sinogram, caption, ImageProcessor.normalize_image_to_0_255)

    def _create_partial_sinogram(self, frame_index: int):
        """Create partial sinogram for animation"""
        partial_sinogram = st.session_state[SessionKeys.GENERATED_SINOGRAM].copy()
        partial_sinogram[frame_index + 1:, :] = 0
        return partial_sinogram

    def _handle_sinogram_view_mode_change(self):
        """Handle sinogram view mode change"""
        st.session_state[SessionKeys.SINOGRAM_VIEW_MODE_SELECTION] = st.session_state.sinogram_view_mode_radio
        if st.session_state[SessionKeys.SINOGRAM_VIEW_MODE_SELECTION] != "Iterative":
            st.session_state[SessionKeys.IS_ANIMATING_SINOGRAM] = False

    def _handle_sinogram_slider_change(self):
        """Handle sinogram slider change"""
        new_frame_index = st.session_state.sinogram_slider_widget - 1
        st.session_state[SessionKeys.SINOGRAM_CURRENT_FRAME_INDEX] = new_frame_index
        if st.session_state.get(SessionKeys.IS_ANIMATING_SINOGRAM, False):
            st.session_state[SessionKeys.IS_ANIMATING_SINOGRAM] = False

    def _handle_sinogram_animation_control(self, action):
        """Handle sinogram animation control actions"""
        if isinstance(action, bool):
            st.session_state[SessionKeys.IS_ANIMATING_SINOGRAM] = action
        elif isinstance(action, int):
            st.session_state[SessionKeys.SINOGRAM_CURRENT_FRAME_INDEX] = action


class ReconstructionSection:
    """Handles image reconstruction display"""
    
    def __init__(self):
        self.ct_scanner = CTScanner()
        self.session_manager = SessionStateManager()
        self.progress = ProgressIndicators()
        self.view_selector = ViewModeSelector()
        self.image_display = ImageDisplay()
        self.animation_controls = AnimationControls()

    def render(self, reconstruct_button: bool, angular_step: float, detector_count: int, detector_span: float) -> bool:
        """Render reconstruction section"""
        st.subheader("Reconstruction")
        animation_rerun_required = False

        if reconstruct_button:
            animation_rerun_required = self._handle_reconstruction_request(angular_step, detector_count, detector_span)

        reconstruction_frames = st.session_state.get(SessionKeys.RECONSTRUCTION_FRAME_LIST, [])
        if reconstruction_frames:
            animation_rerun_required = self._render_reconstruction_display(reconstruction_frames) or animation_rerun_required
        elif st.session_state.get(SessionKeys.GENERATED_SINOGRAM) is not None:
            st.info("Click 'Reconstruct Image' to perform backprojection.")
        elif st.session_state.get(SessionKeys.GRAYSCALE_IMAGE) is not None:
            st.info("Generate a sinogram first to enable reconstruction.")

        return animation_rerun_required

    def _handle_reconstruction_request(self, angular_step: float, detector_count: int, detector_span: float) -> bool:
        """Handle reconstruction button click"""
        generated_sinogram = st.session_state.get(SessionKeys.GENERATED_SINOGRAM)
        grayscale_image = st.session_state.get(SessionKeys.GRAYSCALE_IMAGE)
        sinogram_params = st.session_state.get(SessionKeys.SINOGRAM_GENERATION_PARAMS, {})

        if generated_sinogram is None:
            st.warning("Cannot reconstruct: Generate a sinogram first.")
            return False
        elif grayscale_image is None:
            st.warning("Cannot reconstruct: Original image is missing.")
            return False
        elif not sinogram_params:
            st.warning("Cannot reconstruct: Sinogram parameters are missing.")
            return False

        with self.progress.show_processing_spinner("Reconstructing image using backprojection..."):
            reconstructed_frames = self.ct_scanner.reconstruct_image_backprojection_frames(
                generated_sinogram, grayscale_image.shape,
                sinogram_params['step'], sinogram_params['span'], sinogram_params['detectors']
            )

            if reconstructed_frames:
                # Set timestamps
                current_time = datetime.datetime.now()
                st.session_state[SessionKeys.CONTENT_DATE] = current_time.strftime("%Y%m%d")
                st.session_state[SessionKeys.CONTENT_TIME] = current_time.strftime("%H%M%S")
                
                # Update session state
                st.session_state[SessionKeys.RECONSTRUCTION_FRAME_LIST] = reconstructed_frames
                st.session_state[SessionKeys.RECONSTRUCTION_CURRENT_FRAME_INDEX] = len(reconstructed_frames) - 1
                st.session_state[SessionKeys.IS_ANIMATING_RECONSTRUCTION] = False
                
                # Save reconstruction image
                # final_image = reconstructed_frames[-1]
                # filename = ("reconstruction_filtered.png" if st.session_state.get(SessionKeys.USE_RAMP_FILTER) else "reconstruction.png")
                # plt.imsave(filename, ImageProcessor.normalize_image_to_0_255(final_image), cmap="gray")

                # Calculate RMSE values
                rmse_values = self.ct_scanner.calculate_reconstruction_quality(grayscale_image, reconstructed_frames)
                st.session_state[SessionKeys.RMSE_ERROR_VALUES] = rmse_values
                
                return True
            else:
                st.error("Reconstruction failed.")
                self.session_manager.reset_reconstruction_state()
                return False

    def _render_reconstruction_display(self, reconstruction_frames: List) -> bool:
        """Render reconstruction display with view modes"""
        total_steps = len(reconstruction_frames)
        
        # View mode selection
        self.view_selector.render_view_mode_radio(
            st.session_state.get(SessionKeys.RECONSTRUCTION_VIEW_MODE_SELECTION, "Full"),
            "reconstruction_view_mode_radio",
            self._handle_reconstruction_view_mode_change
        )

        # Handle iterative vs full display
        if st.session_state.get(SessionKeys.RECONSTRUCTION_VIEW_MODE_SELECTION) == "Iterative":
            return self._render_reconstruction_animation(total_steps)
        else:
            self._render_static_reconstruction(reconstruction_frames)
            return False

    def _render_reconstruction_animation(self, total_steps: int) -> bool:
        """Render reconstruction animation"""
        animation_rerun_required = False
        
        # Animation controls
        animation_rerun_required = self.animation_controls.render_play_pause_controls(
            "play_reconstruction_animation",
            "pause_reconstruction_animation",
            st.session_state.get(SessionKeys.IS_ANIMATING_RECONSTRUCTION, False),
            total_steps,
            st.session_state.get(SessionKeys.RECONSTRUCTION_CURRENT_FRAME_INDEX, 0),
            lambda: st.session_state.get(SessionKeys.TOTAL_PROJECTION_STEPS, 0) - 1,
            self._handle_reconstruction_animation_control
        ) or animation_rerun_required
        
        # Frame slider
        self.animation_controls.render_frame_slider(
            "Step",
            total_steps,
            st.session_state.get(SessionKeys.RECONSTRUCTION_CURRENT_FRAME_INDEX, 0),
            "reconstruction_slider_widget",
            self._handle_reconstruction_slider_change
        )
        
        # Display current frame
        current_frame = st.session_state.get(SessionKeys.RECONSTRUCTION_CURRENT_FRAME_INDEX, 0)
        if 0 <= current_frame < total_steps:
            current_image = st.session_state[SessionKeys.RECONSTRUCTION_FRAME_LIST][current_frame]
            current_rmse = st.session_state[SessionKeys.RMSE_ERROR_VALUES][current_frame]
            caption = f"Reconstruction Step {current_frame + 1}/{total_steps}"
            
            self.image_display.render_image_with_caption(
                current_image, caption, ImageProcessor.normalize_image_to_0_255
            )
            self.image_display.render_rmse_display(current_rmse)
        else:
            st.session_state[SessionKeys.RECONSTRUCTION_CURRENT_FRAME_INDEX] = 0
            animation_rerun_required = True

        # Handle animation progression
        if st.session_state.get(SessionKeys.IS_ANIMATING_RECONSTRUCTION, False):
            if current_frame < total_steps - 1:
                st.session_state[SessionKeys.RECONSTRUCTION_CURRENT_FRAME_INDEX] += 1
                animation_rerun_required = True
            else:
                st.session_state[SessionKeys.IS_ANIMATING_RECONSTRUCTION] = False
                animation_rerun_required = True

        return animation_rerun_required

    def _render_static_reconstruction(self, reconstruction_frames: List):
        """Render static reconstruction display"""
        total_steps = len(reconstruction_frames)
        final_image = reconstruction_frames[-1]
        final_rmse = st.session_state[SessionKeys.RMSE_ERROR_VALUES][-1]
        caption = f"Full Reconstruction (after {total_steps} steps)"
        
        self.image_display.render_image_with_caption(
            final_image, caption, ImageProcessor.normalize_image_to_0_255
        )
        self.image_display.render_rmse_display(final_rmse)

    def _handle_reconstruction_view_mode_change(self):
        """Handle reconstruction view mode change"""
        st.session_state[SessionKeys.RECONSTRUCTION_VIEW_MODE_SELECTION] = st.session_state.reconstruction_view_mode_radio
        if st.session_state[SessionKeys.RECONSTRUCTION_VIEW_MODE_SELECTION] != "Iterative":
            st.session_state[SessionKeys.IS_ANIMATING_RECONSTRUCTION] = False

    def _handle_reconstruction_slider_change(self):
        """Handle reconstruction slider change"""
        new_frame_index = st.session_state.reconstruction_slider_widget - 1
        st.session_state[SessionKeys.RECONSTRUCTION_CURRENT_FRAME_INDEX] = new_frame_index
        if st.session_state.get(SessionKeys.IS_ANIMATING_RECONSTRUCTION, False):
            st.session_state[SessionKeys.IS_ANIMATING_RECONSTRUCTION] = False

    def _handle_reconstruction_animation_control(self, action):
        """Handle reconstruction animation control actions"""
        if isinstance(action, bool):
            st.session_state[SessionKeys.IS_ANIMATING_RECONSTRUCTION] = action
        elif isinstance(action, int):
            st.session_state[SessionKeys.RECONSTRUCTION_CURRENT_FRAME_INDEX] = action


class DICOMSaveHandler:
    """Handles DICOM save operations"""
    
    def __init__(self):
        self.dicom_handler = DICOMHandler()
        self.file_generator = FileNameGenerator()
        self.progress = ProgressIndicators()

    def handle_dicom_save(
        self, 
        patient_name: str, 
        patient_id: str, 
        study_description: str,
        birth_date: str, 
        sex: str, 
        age: str, 
        filename: str
    ):
        """Handle DICOM save operation with custom filename"""
        required_fields = [SessionKeys.STUDY_DATE, SessionKeys.STUDY_TIME, 
                          SessionKeys.CONTENT_DATE, SessionKeys.CONTENT_TIME]
        
        if all(st.session_state.get(field) for field in required_fields):
            final_reconstruction = st.session_state[SessionKeys.RECONSTRUCTION_FRAME_LIST][-1]
            
            # Sanitize filename
            sanitized_filename = self.file_generator.sanitize_filename(filename)
            
            try:
                saved_path = self.dicom_handler.save_image_as_dicom(
                    final_reconstruction, patient_name, patient_id, study_description,
                    st.session_state[SessionKeys.STUDY_DATE], 
                    st.session_state[SessionKeys.STUDY_TIME],
                    st.session_state[SessionKeys.CONTENT_DATE], 
                    st.session_state[SessionKeys.CONTENT_TIME],
                    birth_date, sex, age, sanitized_filename
                )
                
                self.progress.show_success_message(f"DICOM file saved as: {saved_path}")
                
                with open(saved_path, "rb") as file:
                    st.download_button(
                        label="Download DICOM file",
                        data=file,
                        file_name=sanitized_filename,
                        mime="application/dicom"
                    )
                    
            except Exception as e:
                self.progress.show_error_message(f"Error saving DICOM file: {str(e)}")
                
        else:
            self.progress.show_error_message("Missing DICOM metadata. Please generate sinogram first.")