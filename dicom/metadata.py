"""
DICOM metadata handling utilities
"""

import datetime
from typing import Dict, Any, Callable


class DICOMMetadataExtractor:
    """Extracts and processes DICOM metadata"""
    
    @staticmethod
    def safe_extract_attr(dataset, attr_name: str, formatter: Callable = str):
        """Safely extract attribute from DICOM dataset"""
        if hasattr(dataset, attr_name):
            return formatter(getattr(dataset, attr_name))
        return None

    @staticmethod
    def format_dicom_date(date_str: str) -> str:
        """Format DICOM date string to DD-MM-YYYY"""
        return datetime.datetime.strptime(date_str, '%Y%m%d').strftime('%d-%m-%Y')

    @staticmethod
    def format_dicom_time(time_str: str) -> str:
        """Format DICOM time string to HH:MM:SS"""
        return datetime.datetime.strptime(time_str, "%H%M%S").strftime('%H:%M:%S')

    @staticmethod
    def extract_patient_name(patient_name_field) -> str:
        """Extract and format patient name from DICOM field"""
        if patient_name_field:
            full_name = f"{patient_name_field.given_name} {patient_name_field.family_name}".strip()
            return full_name
        return ""

    def extract_metadata_from_dataset(self, dicom_dataset) -> Dict[str, Any]:
        """Extract all relevant metadata from DICOM dataset"""
        metadata = {}

        # Patient information
        if hasattr(dicom_dataset, 'PatientName'):
            metadata['patient_name'] = self.extract_patient_name(dicom_dataset.PatientName)

        metadata['patient_id'] = self.safe_extract_attr(dicom_dataset, 'PatientID')
        metadata['patient_sex'] = self.safe_extract_attr(dicom_dataset, 'PatientSex')
        metadata['patient_age'] = self.safe_extract_attr(dicom_dataset, 'PatientAge')

        # Dates and times
        birth_date = self.safe_extract_attr(dicom_dataset, 'PatientBirthDate')
        if birth_date:
            metadata['patient_birth_date'] = self.format_dicom_date(birth_date)

        study_date = self.safe_extract_attr(dicom_dataset, 'StudyDate')
        if study_date:
            metadata['study_date'] = self.format_dicom_date(study_date)

        study_time = self.safe_extract_attr(dicom_dataset, 'StudyTime')
        if study_time:
            metadata['study_time'] = self.format_dicom_time(study_time)

        content_date = self.safe_extract_attr(dicom_dataset, 'ContentDate')
        if content_date:
            metadata['content_date'] = self.format_dicom_date(content_date)

        content_time = self.safe_extract_attr(dicom_dataset, 'ContentTime')
        if content_time:
            metadata['content_time'] = self.format_dicom_time(content_time)

        # Study information
        metadata['study_description'] = self.safe_extract_attr(dicom_dataset, 'StudyDescription')
        metadata['image_comments'] = self.safe_extract_attr(dicom_dataset, 'ImageComments')

        return metadata


class DICOMAgeCalculator:
    """Calculates patient age in DICOM format"""
    
    @staticmethod
    def calculate_patient_age_dicom_format(birth_date: datetime.date, reference_date: datetime.date) -> str:
        """Calculate patient age in DICOM format (XXXD/XXXW/XXXM/XXXY)"""
        age_timedelta = reference_date - birth_date
        total_days = age_timedelta.days

        if total_days < 7:
            return f"{total_days:03d}D"
        elif total_days < 30:
            weeks = total_days // 7
            return f"{weeks:03d}W"
        elif total_days < 365:
            months = total_days // 30
            return f"{months:03d}M"
        else:
            years = reference_date.year - birth_date.year
            if (reference_date.month, reference_date.day) < (birth_date.month, birth_date.day):
                years -= 1
            return f"{years:03d}Y"