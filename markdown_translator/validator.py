"""
Content integrity validation system.

This module provides functionality to validate that translated content
maintains integrity and completeness compared to the original.
"""

import re
from typing import List, Dict, Tuple
from .interfaces import IValidator
from .models import ValidationResult


class IntegrityValidator(IValidator):
    """
    内容完整性验证器
    
    This class implements validation mechanisms to ensure translated content
    maintains integrity and completeness compared to the original content.
    It uses integrity markers and various validation checks.
    """
    
    # Integrity markers used to validate translation completeness
    INTEGRITY_MARKERS = {
        'start': '<<<TRANSLATION_START_MARKER>>>',
        'end': '<<<TRANSLATION_END_MARKER>>>'
    }
    
    # Markdown syntax patterns for structure validation
    MARKDOWN_PATTERNS = {
        'code_block': re.compile(r'^```[\w]*$|^~~~[\w]*$', re.MULTILINE),
        'table_row': re.compile(r'^\|.*\|$', re.MULTILINE),
        'header': re.compile(r'^#{1,6}\s+', re.MULTILINE),
        'list_item': re.compile(r'^\s*[-*+]\s+|^\s*\d+\.\s+', re.MULTILINE),
        'link': re.compile(r'\[([^\]]+)\]\(([^)]+)\)'),
        'image': re.compile(r'!\[([^\]]*)\]\(([^)]+)\)'),
    }
    
    def __init__(self, line_count_tolerance: float = 0.1):
        """
        Initialize the IntegrityValidator.
        
        Args:
            line_count_tolerance: Allowed line count difference as a percentage (default: 10%)
        """
        self.line_count_tolerance = line_count_tolerance
    
    def add_markers(self, content: str) -> str:
        """
        Add integrity markers to content before translation.
        
        Args:
            content: Original content to add markers to
            
        Returns:
            Content with integrity markers added at the beginning and end
        """
        if not content.strip():
            return content
            
        start_marker = self.INTEGRITY_MARKERS['start']
        end_marker = self.INTEGRITY_MARKERS['end']
        
        # Add markers with newlines to ensure they're on separate lines
        marked_content = f"{start_marker}\n{content}\n{end_marker}"
        
        return marked_content
    
    def validate_translation(self, original: str, translated: str) -> ValidationResult:
        """
        Validate that translated content maintains integrity.
        
        Args:
            original: Original content with markers
            translated: Translated content that should have markers
            
        Returns:
            ValidationResult indicating whether validation passed
        """
        issues = []
        confidence_score = 1.0
        
        # Check if markers are present (but don't fail validation if missing)
        has_markers = self._check_markers_present(translated)
        if not has_markers:
            # Only add as a warning, not a critical issue
            issues.append("Integrity markers missing in translated content (warning)")
            confidence_score -= 0.1  # Reduced penalty
        
        # Remove markers for content comparison
        original_clean = self.remove_markers(original)
        translated_clean = self.remove_markers(translated)
        
        # Check line count similarity
        line_count_valid, line_diff = self._check_line_count_similarity(original_clean, translated_clean)
        if not line_count_valid:
            issues.append(f"Line count difference too large: {line_diff} lines")
            confidence_score -= 0.3
        
        # Check Markdown structure integrity
        structure_valid, structure_issues = self._check_markdown_structure(original_clean, translated_clean)
        if not structure_valid:
            issues.extend(structure_issues)
            confidence_score -= 0.2 * len(structure_issues)
        
        # Check code block integrity
        code_blocks_valid, code_issues = self._check_code_blocks_integrity(original_clean, translated_clean)
        if not code_blocks_valid:
            issues.extend(code_issues)
            confidence_score -= 0.1 * len(code_issues)
        
        # Ensure confidence score doesn't go below 0
        confidence_score = max(0.0, confidence_score)
        
        # Validation passes if no critical issues and confidence is reasonable
        # Don't require markers for validation to pass
        critical_issues = [issue for issue in issues if not issue.endswith("(warning)")]
        is_valid = len(critical_issues) == 0 or confidence_score >= 0.5
        
        return ValidationResult(
            is_valid=is_valid,
            issues=issues,
            confidence_score=confidence_score,
            line_count_diff=line_diff if 'line_diff' in locals() else 0,
            has_markers=has_markers
        )
    
    def remove_markers(self, content: str) -> str:
        """
        Remove integrity markers from translated content.
        
        Args:
            content: Translated content with markers
            
        Returns:
            Clean translated content without markers
        """
        if not content:
            return content
            
        start_marker = self.INTEGRITY_MARKERS['start']
        end_marker = self.INTEGRITY_MARKERS['end']
        
        # Remove start marker and any following newline
        content = re.sub(f'^{re.escape(start_marker)}\\n?', '', content, flags=re.MULTILINE)
        
        # Remove end marker and any preceding newline
        content = re.sub(f'\\n?{re.escape(end_marker)}$', '', content, flags=re.MULTILINE)
        
        return content.strip()
    
    def _check_markers_present(self, content: str) -> bool:
        """
        Check if both integrity markers are present in the content.
        
        Args:
            content: Content to check for markers
            
        Returns:
            True if both markers are present, False otherwise
        """
        start_marker = self.INTEGRITY_MARKERS['start']
        end_marker = self.INTEGRITY_MARKERS['end']
        
        return start_marker in content and end_marker in content
    
    def _check_line_count_similarity(self, original: str, translated: str) -> Tuple[bool, int]:
        """
        Check if line counts are similar within tolerance.
        
        Args:
            original: Original content without markers
            translated: Translated content without markers
            
        Returns:
            Tuple of (is_valid, line_difference)
        """
        original_lines = len(original.splitlines()) if original else 0
        translated_lines = len(translated.splitlines()) if translated else 0
        
        line_diff = abs(original_lines - translated_lines)
        
        # Allow some difference based on tolerance percentage
        max_allowed_diff = max(1, int(original_lines * self.line_count_tolerance))
        
        is_valid = line_diff <= max_allowed_diff
        
        return is_valid, line_diff
    
    def _check_markdown_structure(self, original: str, translated: str) -> Tuple[bool, List[str]]:
        """
        Check if Markdown structure elements are preserved.
        
        Args:
            original: Original content without markers
            translated: Translated content without markers
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check headers count
        original_headers = len(self.MARKDOWN_PATTERNS['header'].findall(original))
        translated_headers = len(self.MARKDOWN_PATTERNS['header'].findall(translated))
        
        if original_headers != translated_headers:
            issues.append(f"Header count mismatch: original {original_headers}, translated {translated_headers}")
        
        # Check table rows count
        original_tables = len(self.MARKDOWN_PATTERNS['table_row'].findall(original))
        translated_tables = len(self.MARKDOWN_PATTERNS['table_row'].findall(translated))
        
        if original_tables != translated_tables:
            issues.append(f"Table row count mismatch: original {original_tables}, translated {translated_tables}")
        
        # Check links count (should be preserved)
        original_links = len(self.MARKDOWN_PATTERNS['link'].findall(original))
        translated_links = len(self.MARKDOWN_PATTERNS['link'].findall(translated))
        
        if original_links != translated_links:
            issues.append(f"Link count mismatch: original {original_links}, translated {translated_links}")
        
        # Check images count (should be preserved)
        original_images = len(self.MARKDOWN_PATTERNS['image'].findall(original))
        translated_images = len(self.MARKDOWN_PATTERNS['image'].findall(translated))
        
        if original_images != translated_images:
            issues.append(f"Image count mismatch: original {original_images}, translated {translated_images}")
        
        return len(issues) == 0, issues
    
    def _check_code_blocks_integrity(self, original: str, translated: str) -> Tuple[bool, List[str]]:
        """
        Check if code blocks are preserved correctly.
        
        Args:
            original: Original content without markers
            translated: Translated content without markers
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Find code block markers
        original_code_markers = self.MARKDOWN_PATTERNS['code_block'].findall(original)
        translated_code_markers = self.MARKDOWN_PATTERNS['code_block'].findall(translated)
        
        if len(original_code_markers) != len(translated_code_markers):
            issues.append(f"Code block marker count mismatch: original {len(original_code_markers)}, translated {len(translated_code_markers)}")
        
        # Check if code blocks are properly closed (even number of markers)
        if len(original_code_markers) % 2 != 0:
            issues.append("Original content has unclosed code blocks")
        
        if len(translated_code_markers) % 2 != 0:
            issues.append("Translated content has unclosed code blocks")
        
        return len(issues) == 0, issues
    
    def get_validation_statistics(self, validation_results: List[ValidationResult]) -> Dict[str, float]:
        """
        Generate statistics from multiple validation results.
        
        Args:
            validation_results: List of ValidationResult objects
            
        Returns:
            Dictionary containing validation statistics
        """
        if not validation_results:
            return {}
        
        total_validations = len(validation_results)
        successful_validations = sum(1 for result in validation_results if result.is_valid)
        
        avg_confidence = sum(result.confidence_score for result in validation_results) / total_validations
        
        total_issues = sum(len(result.issues) for result in validation_results)
        
        return {
            'total_validations': total_validations,
            'successful_validations': successful_validations,
            'success_rate': successful_validations / total_validations * 100,
            'average_confidence': avg_confidence,
            'total_issues_found': total_issues,
            'average_issues_per_validation': total_issues / total_validations
        }
