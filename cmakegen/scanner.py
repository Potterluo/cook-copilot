"""
Project structure scanner for C/C++ projects
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple


class ProjectScanner:
    """Scanner for C/C++ project structure"""
    
    # C/C++ source file extensions
    SOURCE_EXTENSIONS = {'.c', '.cpp', '.cc', '.cxx', '.c++'}
    
    # C/C++ header file extensions
    HEADER_EXTENSIONS = {'.h', '.hpp', '.hh', '.hxx', '.h++'}
    
    # Files to ignore during scanning
    IGNORE_PATTERNS = [
        r'.*\.git.*',
        r'.*\.vs.*',
        r'.*\.vscode.*',
        r'.*build.*',
        r'.*CMakeFiles.*',
        r'.*\.cmake$',
        r'.*CMakeCache\.txt$',
    ]
    
    def __init__(self, project_root: str):
        """Initialize scanner with project root directory
        
        Args:
            project_root: Path to the project root directory
        """
        self.project_root = os.path.abspath(project_root)
        self.ignore_patterns = [re.compile(pattern) for pattern in self.IGNORE_PATTERNS]
        
    def should_ignore(self, path: str) -> bool:
        """Check if a path should be ignored
        
        Args:
            path: Path to check
            
        Returns:
            True if path should be ignored, False otherwise
        """
        for pattern in self.ignore_patterns:
            if pattern.match(path):
                return True
        return False
    
    def scan_project(self) -> Dict[str, Dict]:
        """Scan project structure
        
        Returns:
            Dictionary containing project structure information
        """
        project_info = {
            'root': self.project_root,
            'modules': {},
            'source_files': [],
            'header_files': [],
            'include_dirs': set(),
        }
        
        # Walk through project directory
        for root, dirs, files in os.walk(self.project_root):
            # Skip ignored directories
            if self.should_ignore(root):
                continue
                
            # Process files in current directory
            source_files = []
            header_files = []
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.project_root)
                
                # Skip ignored files
                if self.should_ignore(file_path):
                    continue
                
                # Check file extension
                _, ext = os.path.splitext(file)
                
                if ext.lower() in self.SOURCE_EXTENSIONS:
                    source_files.append(rel_path)
                    project_info['source_files'].append(rel_path)
                    
                elif ext.lower() in self.HEADER_EXTENSIONS:
                    header_files.append(rel_path)
                    project_info['header_files'].append(rel_path)
                    
                    # Add directory to include dirs if it contains headers
                    include_dir = os.path.dirname(file_path)
                    if include_dir:
                        project_info['include_dirs'].add(
                            os.path.relpath(include_dir, self.project_root)
                        )
            
            # Consider all directories with header files as modules, not just those with source files
            module_path = os.path.relpath(root, self.project_root)
            if module_path == '.':
                module_path = ''

            if source_files or header_files:
                project_info['modules'][module_path] = {
                    'path': module_path,
                    'source_files': source_files,
                    'header_files': header_files,
                }
        
        # Convert include_dirs set to list for JSON serialization
        project_info['include_dirs'] = list(project_info['include_dirs'])
        
        return project_info
    
    def get_module_structure(self) -> Dict[str, List[str]]:
        """Get module structure with source files
        
        Returns:
            Dictionary mapping module paths to lists of source files
        """
        project_info = self.scan_project()
        module_structure = {}
        
        for module_path, module_info in project_info['modules'].items():
            if module_info['source_files']:
                module_structure[module_path] = module_info['source_files']
        
        return module_structure
    
    def get_include_directories(self) -> List[str]:
        """Get list of include directories
        
        Returns:
            List of include directories
        """
        project_info = self.scan_project()
        return project_info['include_dirs']