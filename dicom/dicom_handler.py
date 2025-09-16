"""
DICOM file handling operations
"""

import pydicom
import numpy as np
from pydicom.dataset import FileDataset
from typing import Dict, Any
from core.image_processing import ImageProcessor
from dicom.metadata import DICOMMetadataExtractor
from config.constants import (
    DICOM_MODALITY, DICOM_PHOTOMETRIC_INTERPRETATION, DICOM_BITS_STORED,
    DICOM_BITS_ALLOCATED, DICOM_SAMPLES_PER_PIXEL, DICOM_HIGH_BIT,
    DICOM_PIXEL_REPRESENTATION, DICOM_CHARACTER_SET
)


class DICOMHandler:
    """Handles DICOM file operations"""
    
    def __init__(self):
        self.metadata_extractor = DICOMMetadataExtractor()
        self.image_processor = ImageProcessor()

    def load_dicom_file(self, dicom_file_path: str) -> Dict[str, Any]:
        """Load DICOM file and extract metadata and image data"""
        dicom_dataset = pydicom.dcmread(dicom_file_path)
        
        # Extract metadata
        metadata = self.metadata_extractor.extract_metadata_from_dataset(dicom_dataset)
        
        # Process pixel array
        pixel_array = dicom_dataset.pixel_array.astype(np.float64)
        normalized_pixels = self.image_processor.normalize_array(pixel_array)
        metadata['grayscale_image'] = normalized_pixels
        
        return metadata

    def save_image_as_dicom(
        self,
        image: np.ndarray,
        patient_name: str,
        patient_id: str,
        study_description: str,
        study_date: str,
        study_time: str,
        content_date: str,
        content_time: str,
        birth_date: str = "",
        sex: str = "",
        age: str = "",
        output_filename: str = "output.dcm"
    ) -> str:
        """Save image as DICOM file with proper metadata"""
        
        # Normalize and convert image
        normalized_image = self.image_processor.normalize_image_to_0_255(image)
        pixel_array = normalized_image.astype(np.uint16)

        # Create file metadata
        file_meta = pydicom.dataset.FileMetaDataset()
        file_meta.MediaStorageSOPClassUID = pydicom.uid.generate_uid()
        file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
        file_meta.ImplementationClassUID = pydicom.uid.generate_uid()

        # Create DICOM dataset
        dicom_dataset = FileDataset(
            output_filename, {}, 
            file_meta=file_meta, 
            preamble=b"\0" * 128
        )

        # Set DICOM attributes
        self._set_dicom_attributes(
            dicom_dataset, patient_name, patient_id, study_description,
            study_date, study_time, content_date, content_time,
            birth_date, sex, age, pixel_array
        )

        # Save file
        dicom_dataset.save_as(output_filename, write_like_original=False)
        return output_filename

    def _set_dicom_attributes(
        self, 
        dataset: FileDataset, 
        patient_name: str, 
        patient_id: str, 
        study_description: str,
        study_date: str, 
        study_time: str, 
        content_date: str, 
        content_time: str,
        birth_date: str, 
        sex: str, 
        age: str, 
        pixel_array: np.ndarray
    ) -> None:
        """Set all DICOM attributes for the dataset"""
        
        # Patient information
        dataset.PatientName = patient_name
        dataset.PatientID = patient_id
        dataset.PatientBirthDate = birth_date
        dataset.PatientSex = sex
        dataset.PatientAge = age
        
        # Study information
        dataset.StudyDate = study_date
        dataset.StudyTime = study_time
        dataset.ContentDate = content_date
        dataset.ContentTime = content_time
        dataset.StudyDescription = study_description
        
        # Technical parameters
        dataset.Modality = DICOM_MODALITY
        dataset.PhotometricInterpretation = DICOM_PHOTOMETRIC_INTERPRETATION
        dataset.BitsStored = DICOM_BITS_STORED
        dataset.BitsAllocated = DICOM_BITS_ALLOCATED
        dataset.SamplesPerPixel = DICOM_SAMPLES_PER_PIXEL
        dataset.HighBit = DICOM_HIGH_BIT
        dataset.PixelRepresentation = DICOM_PIXEL_REPRESENTATION
        dataset.SpecificCharacterSet = DICOM_CHARACTER_SET
        
        # Image dimensions and pixel data
        dataset.Rows, dataset.Columns = pixel_array.shape
        dataset.PixelData = pixel_array.tobytes()