"""
Intelligent Markdown file splitter.

This module provides functionality to split large Markdown files into smaller chunks
while preserving Markdown syntax integrity. The splitter is aware of code blocks,
tables, lists, and other Markdown structures to ensure clean splits.
"""

import os
import uuid
from typing import List, Optional
from .interfaces import ISplitter
from .models import FileChunk


class MarkdownSplitter(ISplitter):
    """
    Intelligent Markdown file splitter that preserves syntax integrity.
    
    This splitter analyzes Markdown content to find safe split points that don't
    break syntax structures like code blocks, tables, or lists.
    """
    
    def __init__(self, chunk_size: int = 500):
        """
        Initialize the splitter with a target chunk size.
        
        Args:
            chunk_size: Target number of lines per chunk (default: 500)
        """
        self.chunk_size = chunk_size
        self._validate_chunk_size()
    
    def _validate_chunk_size(self) -> None:
        """Validate that chunk size is reasonable."""
        if self.chunk_size < 10:
            raise ValueError("Chunk size must be at least 10 lines")
        if self.chunk_size > 10000:
            raise ValueError("Chunk size should not exceed 10000 lines for performance reasons")
    
    def get_chunk_size(self) -> int:
        """Get the configured chunk size."""
        return self.chunk_size
    
    def set_chunk_size(self, size: int) -> None:
        """Set the chunk size for splitting."""
        self.chunk_size = size
        self._validate_chunk_size()
    
    def split_file(self, file_path: str) -> List[FileChunk]:
        """
        Split a Markdown file into chunks for translation.
        
        Args:
            file_path: Path to the Markdown file to split
            
        Returns:
            List of FileChunk objects representing the split content
            
        Raises:
            FileNotFoundError: If the input file doesn't exist
            IOError: If there's an error reading the file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Input file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        except IOError as e:
            raise IOError(f"Error reading file {file_path}: {e}")
        
        if not lines:
            return []
        
        chunks = []
        current_start = 0
        
        while current_start < len(lines):
            # Calculate the target end line for this chunk
            target_end = min(current_start + self.chunk_size, len(lines))
            
            # Find a safe split point near the target
            actual_end = self._find_safe_split_point(lines, current_start, target_end)
            
            # Create the chunk with sequential ID and sequence number
            chunk_content = ''.join(lines[current_start:actual_end])
            chunk_index = len(chunks)  # 0-based index
            chunk_id = f"chunk_{chunk_index:03d}_{str(uuid.uuid4())[:8]}"  # e.g., "chunk_000_a1b2c3d4"
            
            chunk = FileChunk(
                id=chunk_id,
                content=chunk_content,
                start_line=current_start + 1,  # 1-based line numbering
                end_line=actual_end,           # 1-based line numbering
                original_file=file_path,
                sequence_number=chunk_index
            )
            
            chunks.append(chunk)
            current_start = actual_end
        
        return chunks
    
    def _find_safe_split_point(self, lines: List[str], start: int, target_end: int) -> int:
        """
        Find a safe point to split the content that doesn't break Markdown syntax.
        
        Args:
            lines: List of all lines in the file
            start: Starting line index for this chunk
            target_end: Target ending line index
            
        Returns:
            Actual ending line index that's safe for splitting
        """
        # If we're at the end of the file, return the target
        if target_end >= len(lines):
            return len(lines)
        
        # If the chunk would be very small, just use the target
        if target_end - start < 10:
            return target_end
        
        # Look for a safe split point within a reasonable range
        search_range = min(50, (target_end - start) // 4)  # Search within 25% of chunk size or 50 lines
        
        # Start from the target and work backwards to find a safe point
        for i in range(target_end, max(start + 10, target_end - search_range), -1):
            if self._is_safe_split_point(lines, i):
                return i
        
        # If no safe point found, use the target (basic fallback)
        return target_end
    
    def _is_safe_split_point(self, lines: List[str], line_index: int) -> bool:
        """
        Check if a given line index is a safe point to split the content.
        
        This method implements a comprehensive algorithm to find safe split points
        that preserve Markdown syntax integrity.
        
        Args:
            lines: List of all lines in the file
            line_index: Line index to check
            
        Returns:
            True if it's safe to split at this point, False otherwise
        """
        if line_index >= len(lines):
            return True
        
        # Check if we're in the middle of a code block
        if self._is_in_code_block(lines, line_index):
            return False
        
        # Check if we're in the middle of a table
        if self._is_in_table(lines, line_index):
            return False
        
        # Check if we're in the middle of a list
        if self._is_in_list_continuation(lines, line_index):
            return False
        
        # Check if we're in the middle of a blockquote
        if self._is_in_blockquote(lines, line_index):
            return False
        
        # Check if we're breaking a link reference definition
        if self._is_in_link_reference(lines, line_index):
            return False
        
        current_line = lines[line_index].strip()
        
        # Excellent split points: after empty lines
        if line_index > 0 and not lines[line_index - 1].strip():
            return True
        
        # Excellent split points: before headers (but not setext headers)
        if current_line.startswith('#') and not self._is_setext_header_underline(lines, line_index):
            return True
        
        # Good split points: before horizontal rules
        if self._is_horizontal_rule(current_line):
            return True
        
        # Good split points: before new sections or major blocks
        if self._is_section_boundary(lines, line_index):
            return True
        
        # Avoid splitting right after headers
        if line_index > 0:
            prev_line = lines[line_index - 1].strip()
            if prev_line.startswith('#') or self._is_setext_header_underline(lines, line_index - 1):
                return False
        
        # Avoid splitting in the middle of paragraphs (prefer paragraph boundaries)
        if self._is_paragraph_continuation(lines, line_index):
            return False
        
        return True
    
    def _is_in_blockquote(self, lines: List[str], line_index: int) -> bool:
        """
        Check if the line is part of a blockquote structure.
        
        Args:
            lines: List of all lines in the file
            line_index: Line index to check
            
        Returns:
            True if the line is part of a blockquote
        """
        if line_index >= len(lines):
            return False
        
        current_line = lines[line_index].strip()
        
        # Check if current line is a blockquote
        if current_line.startswith('>'):
            return True
        
        # Check if we're in a multi-line blockquote
        # Look backwards for blockquote context
        for i in range(line_index - 1, max(-1, line_index - 5), -1):
            prev_line = lines[i].strip()
            if not prev_line:  # Empty line might be part of blockquote
                continue
            if prev_line.startswith('>'):
                # Check if current line could be a continuation
                if current_line and not current_line.startswith('#'):
                    return True
            else:
                break
        
        return False
    
    def _is_in_link_reference(self, lines: List[str], line_index: int) -> bool:
        """
        Check if the line is part of a link reference definition.
        
        Args:
            lines: List of all lines in the file
            line_index: Line index to check
            
        Returns:
            True if the line is part of a link reference
        """
        if line_index >= len(lines):
            return False
        
        # Look for link reference patterns: [label]: url "title"
        for i in range(max(0, line_index - 2), min(len(lines), line_index + 3)):
            line = lines[i].strip()
            if line.startswith('[') and ']:' in line:
                return True
        
        return False
    
    def _is_setext_header_underline(self, lines: List[str], line_index: int) -> bool:
        """
        Check if the line is a setext header underline (=== or ---).
        
        Args:
            lines: List of all lines in the file
            line_index: Line index to check
            
        Returns:
            True if the line is a setext header underline
        """
        if line_index >= len(lines) or line_index == 0:
            return False
        
        current_line = lines[line_index].strip()
        prev_line = lines[line_index - 1].strip()
        
        # Check if current line is all = or all -
        if (current_line and 
            (all(c == '=' for c in current_line) or all(c == '-' for c in current_line)) and
            prev_line and not prev_line.startswith('#')):
            return True
        
        return False
    
    def _is_horizontal_rule(self, line: str) -> bool:
        """
        Check if the line is a horizontal rule.
        
        Args:
            line: Line to check
            
        Returns:
            True if the line is a horizontal rule
        """
        line = line.strip()
        
        # Must be at least 3 characters
        if len(line) < 3:
            return False
        
        # Check for different horizontal rule patterns
        if (all(c in '- ' for c in line) and line.count('-') >= 3) or \
           (all(c in '* ' for c in line) and line.count('*') >= 3) or \
           (all(c in '_ ' for c in line) and line.count('_') >= 3):
            return True
        
        return False
    
    def _is_section_boundary(self, lines: List[str], line_index: int) -> bool:
        """
        Check if this is a natural section boundary.
        
        Args:
            lines: List of all lines in the file
            line_index: Line index to check
            
        Returns:
            True if this is a good place to split sections
        """
        if line_index >= len(lines):
            return True
        
        current_line = lines[line_index].strip()
        
        # Before HTML comments
        if current_line.startswith('<!--'):
            return True
        
        # Before YAML front matter
        if current_line == '---' and line_index == 0:
            return True
        
        return False
    
    def _is_paragraph_continuation(self, lines: List[str], line_index: int) -> bool:
        """
        Check if the line is a continuation of a paragraph.
        
        Args:
            lines: List of all lines in the file
            line_index: Line index to check
            
        Returns:
            True if the line continues a paragraph
        """
        if line_index >= len(lines) or line_index == 0:
            return False
        
        current_line = lines[line_index].strip()
        prev_line = lines[line_index - 1].strip()
        
        # If either line is empty, not a continuation
        if not current_line or not prev_line:
            return False
        
        # If previous line is a special markdown element, not a continuation
        if (prev_line.startswith('#') or 
            prev_line.startswith('>') or 
            prev_line.startswith('- ') or 
            prev_line.startswith('* ') or 
            prev_line.startswith('+ ') or
            self._is_list_item_line(prev_line) or
            self._is_horizontal_rule(prev_line)):
            return False
        
        # If current line is a special markdown element, not a continuation
        if (current_line.startswith('#') or 
            current_line.startswith('>') or 
            current_line.startswith('- ') or 
            current_line.startswith('* ') or 
            current_line.startswith('+ ') or
            self._is_list_item_line(current_line) or
            self._is_horizontal_rule(current_line)):
            return False
        
        # Both lines are regular text, likely a paragraph continuation
        return True
    
    def _is_in_code_block(self, lines: List[str], line_index: int) -> bool:
        """
        Check if the given line is inside a code block.
        
        This method detects both fenced code blocks (``` and ~~~) and indented code blocks.
        It properly handles nested structures and different code block syntaxes.
        
        Args:
            lines: List of all lines in the file
            line_index: Line index to check
            
        Returns:
            True if the line is inside a code block, False otherwise
        """
        # Track different types of code blocks
        triple_backtick_count = 0
        triple_tilde_count = 0
        
        # Count code block markers from the beginning up to the current line
        for i in range(line_index):
            line = lines[i].strip()
            
            # Check for fenced code blocks with triple backticks
            if line.startswith('```'):
                triple_backtick_count += 1
            
            # Check for fenced code blocks with triple tildes
            elif line.startswith('~~~'):
                triple_tilde_count += 1
        
        # If we have an odd number of opening markers, we're inside a block
        in_backtick_block = triple_backtick_count % 2 == 1
        in_tilde_block = triple_tilde_count % 2 == 1
        
        # Also check for indented code blocks (4+ spaces or 1+ tabs at start of line)
        in_indented_block = False
        if line_index < len(lines):
            current_line = lines[line_index]
            # Check if this line and surrounding lines suggest an indented code block
            if (current_line.startswith('    ') or current_line.startswith('\t')) and current_line.strip():
                # Look at context to confirm it's a code block, not just indented text
                in_indented_block = self._is_indented_code_block(lines, line_index)
        
        return in_backtick_block or in_tilde_block or in_indented_block
    
    def _is_indented_code_block(self, lines: List[str], line_index: int) -> bool:
        """
        Check if the current line is part of an indented code block.
        
        Args:
            lines: List of all lines in the file
            line_index: Line index to check
            
        Returns:
            True if the line is part of an indented code block
        """
        if line_index >= len(lines):
            return False
        
        current_line = lines[line_index]
        
        # Must be indented with 4+ spaces or 1+ tabs
        if not (current_line.startswith('    ') or current_line.startswith('\t')):
            return False
        
        # Look for context clues - check previous and next lines
        indented_lines = 0
        total_checked = 0
        
        # Check a small window around the current line
        for i in range(max(0, line_index - 2), min(len(lines), line_index + 3)):
            line = lines[i]
            total_checked += 1
            
            # Skip empty lines
            if not line.strip():
                continue
                
            # Count indented lines
            if line.startswith('    ') or line.startswith('\t'):
                indented_lines += 1
        
        # If most non-empty lines in the window are indented, likely a code block
        return indented_lines >= 2 and total_checked > 0
    
    def _is_in_table(self, lines: List[str], line_index: int) -> bool:
        """
        Check if the given line is part of a table structure.
        
        This method detects Markdown tables by looking for table separator lines
        and consistent pipe (|) usage across multiple lines.
        
        Args:
            lines: List of all lines in the file
            line_index: Line index to check
            
        Returns:
            True if the line is part of a table, False otherwise
        """
        if line_index >= len(lines):
            return False
        
        current_line = lines[line_index].strip()
        
        # Quick check: if no pipes, definitely not a table
        if '|' not in current_line:
            return False
        
        # Look for table structure in a reasonable range
        search_range = 5
        start_search = max(0, line_index - search_range)
        end_search = min(len(lines), line_index + search_range + 1)
        
        # Look for table separator line (header separator)
        separator_found = False
        table_lines = 0
        
        for i in range(start_search, end_search):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check for table separator line (contains |, :, and -)
            if self._is_table_separator_line(line):
                separator_found = True
            
            # Count lines that look like table rows
            elif '|' in line and self._is_table_row_line(line):
                table_lines += 1
        
        # A table needs a separator and at least 2 table rows (header + data)
        return separator_found and table_lines >= 2
    
    def _is_table_separator_line(self, line: str) -> bool:
        """
        Check if a line is a table separator (header separator).
        
        Args:
            line: Line to check
            
        Returns:
            True if the line is a table separator
        """
        line = line.strip()
        
        # Must contain pipes and dashes
        if '|' not in line or '-' not in line:
            return False
        
        # Remove pipes and check if remaining content is mostly dashes and colons
        content = line.replace('|', '').strip()
        if not content:
            return False
        
        # Split by spaces and check each segment
        segments = [seg.strip() for seg in content.split() if seg.strip()]
        
        for segment in segments:
            # Each segment should be dashes with optional colons for alignment
            if not all(c in '-:' for c in segment):
                return False
            # Must have at least one dash
            if '-' not in segment:
                return False
        
        return len(segments) > 0
    
    def _is_table_row_line(self, line: str) -> bool:
        """
        Check if a line looks like a table row.
        
        Args:
            line: Line to check
            
        Returns:
            True if the line looks like a table row
        """
        line = line.strip()
        
        # Must contain pipes
        if '|' not in line:
            return False
        
        # Count pipes to ensure reasonable table structure
        pipe_count = line.count('|')
        
        # Should have at least 2 pipes for a meaningful table (| col1 | col2 |)
        if pipe_count < 2:
            return False
        
        # Check if it's not just a line of pipes (which would be weird)
        non_pipe_content = line.replace('|', '').replace(' ', '').replace('\t', '')
        
        return len(non_pipe_content) > 0
    
    def _is_in_list_continuation(self, lines: List[str], line_index: int) -> bool:
        """
        Check if the given line is a continuation of a list item.
        
        This method detects both simple list continuations and nested list structures.
        It handles unordered lists (-, *, +) and ordered lists (1., 2., etc.).
        
        Args:
            lines: List of all lines in the file
            line_index: Line index to check
            
        Returns:
            True if the line continues a list item, False otherwise
        """
        if line_index >= len(lines) or line_index == 0:
            return False
        
        # Check if we're in the middle of a list structure
        return self._is_in_list_structure(lines, line_index)
    
    def _is_in_list_structure(self, lines: List[str], line_index: int) -> bool:
        """
        Check if the current line is part of a list structure.
        
        Args:
            lines: List of all lines in the file
            line_index: Line index to check
            
        Returns:
            True if the line is part of a list structure
        """
        current_line = lines[line_index]
        
        # Look backwards to find list context
        list_context_found = False
        current_indent = self._get_line_indent(current_line)
        
        # Search backwards for list items
        for i in range(line_index - 1, max(-1, line_index - 10), -1):
            prev_line = lines[i].strip()
            
            # Skip empty lines
            if not prev_line:
                continue
            
            # Check if this is a list item
            if self._is_list_item_line(lines[i]):
                list_context_found = True
                prev_indent = self._get_line_indent(lines[i])
                
                # If current line is indented more than the list item, it's a continuation
                if current_indent > prev_indent:
                    return True
                
                # If current line is at same level and looks like a list item itself
                if current_indent == prev_indent and self._is_list_item_line(current_line):
                    return True
                
                break
            
            # If we hit a non-list, non-empty line with less indentation, stop searching
            line_indent = self._get_line_indent(lines[i])
            if line_indent < current_indent:
                break
        
        return False
    
    def _is_list_item_line(self, line: str) -> bool:
        """
        Check if a line is a list item (ordered or unordered).
        
        Args:
            line: Line to check
            
        Returns:
            True if the line is a list item
        """
        stripped = line.strip()
        
        # Unordered list markers
        if (stripped.startswith('- ') or 
            stripped.startswith('* ') or 
            stripped.startswith('+ ')):
            return True
        
        # Ordered list markers (1. 2. 10. etc.)
        if len(stripped) > 2:
            # Find the first space
            space_index = stripped.find(' ')
            if space_index > 0:
                prefix = stripped[:space_index]
                # Check if it's a number followed by a dot
                if prefix.endswith('.') and prefix[:-1].isdigit():
                    return True
        
        return False
    
    def _get_line_indent(self, line: str) -> int:
        """
        Get the indentation level of a line.
        
        Args:
            line: Line to check
            
        Returns:
            Number of spaces of indentation (tabs count as 4 spaces)
        """
        indent = 0
        for char in line:
            if char == ' ':
                indent += 1
            elif char == '\t':
                indent += 4
            else:
                break
        return indent


def create_splitter(chunk_size: int = 500) -> MarkdownSplitter:
    """
    Factory function to create a MarkdownSplitter instance.
    
    Args:
        chunk_size: Target number of lines per chunk
        
    Returns:
        Configured MarkdownSplitter instance
    """
    return MarkdownSplitter(chunk_size=chunk_size)
