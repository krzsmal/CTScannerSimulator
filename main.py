import streamlit as st
import time
from config.constants import ANIMATION_DELAY, SessionKeys
from utils.session_state import SessionStateManager
from utils.file_utils import FileValidator
from ui.sidebar import SidebarController
from ui.sections import InputImageSection, SinogramSection, ReconstructionSection
from core.image_processing import ImageProcessor
from dicom.dicom_handler import DICOMHandler


class CTScannerApp:
    """Main application class for CT Scanner Simulator"""
    
    def __init__(self):
        self.session_manager = SessionStateManager()
        self.sidebar_controller = SidebarController()
        self.input_section = InputImageSection()
        self.sinogram_section = SinogramSection()
        self.reconstruction_section = ReconstructionSection()
        self.image_processor = ImageProcessor()
        self.dicom_handler = DICOMHandler()
        self.file_validator = FileValidator()

    def setup_page_config(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="CT Scanner Simulator",
            layout="wide",
            initial_sidebar_state="expanded",
        )

    def initialize_app(self):
        """Initialize application state and UI"""
        self.session_manager.initialize()
        st.title("CT scanner simulator")

    def handle_file_upload(self, uploaded_file):
        """Handle new file upload and processing"""
        if uploaded_file is None:
            return False

        current_filename = st.session_state.get(SessionKeys.UPLOADED_IMAGE_FILENAME)
        
        # Check if new file uploaded
        if uploaded_file.name != current_filename:
            self.session_manager.reset_on_new_image()
            
            # Process file based on type
            if self.file_validator.is_dicom_file(uploaded_file.name):
                self._process_dicom_file(uploaded_file)
            else:
                self._process_regular_image(uploaded_file)
                
            st.session_state[SessionKeys.UPLOADED_IMAGE_FILENAME] = uploaded_file.name
            return True  # Indicates rerun needed
        
        return False

    def _process_dicom_file(self, uploaded_file):
        """Process DICOM file"""
        dicom_metadata = self.dicom_handler.load_dicom_file(uploaded_file)
        self.session_manager.update_with_dicom_data(dicom_metadata)

    def _process_regular_image(self, uploaded_file):
        """Process regular image file"""
        image = self.image_processor.load_image_from_file(uploaded_file)
        st.session_state[SessionKeys.GRAYSCALE_IMAGE] = image

    def render_main_content(self, uploaded_file, sidebar_params):
        """Render main application content"""
        if uploaded_file is None:
            st.info("Upload an image to start the simulation.")
            return False

        angular_step, detector_count, detector_span, use_filter = sidebar_params
        animation_rerun_required = False

        # Check for button presses
        generate_button = st.session_state.get('generate_sinogram', False)
        reconstruct_button = st.session_state.get('reconstruct_image', False)

        # Create main content columns
        col1, col2, col3 = st.columns(3)

        # Render sections
        with col1:
            self.input_section.render()

        with col2:
            animation_rerun_required = self.sinogram_section.render(
                generate_button, angular_step, detector_count, detector_span
            ) or animation_rerun_required

        with col3:
            animation_rerun_required = self.reconstruction_section.render(
                reconstruct_button, angular_step, detector_count, detector_span
            ) or animation_rerun_required

        return animation_rerun_required

    def run(self):
        """Main application run method"""
        # Setup
        self.setup_page_config()
        self.initialize_app()
        
        # Render sidebar and get parameters
        uploaded_file, angular_step, detector_count, detector_span, use_filter = self.sidebar_controller.render_sidebar()
        
        # Handle file upload
        if self.handle_file_upload(uploaded_file):
            st.rerun()
        
        # Render main content
        animation_rerun_required = self.render_main_content(
            uploaded_file, 
            (angular_step, detector_count, detector_span, use_filter)
        )
        
        # Handle animation rerun
        if animation_rerun_required:
            time.sleep(ANIMATION_DELAY)
            st.rerun()


def main():
    """Application entry point"""
    app = CTScannerApp()
    app.run()


if __name__ == "__main__":
    main()