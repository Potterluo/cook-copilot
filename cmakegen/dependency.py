"""
Dependency analyzer for C/C++ source files
"""

import os
import re
from typing import Dict, List, Set, Tuple


class DependencyAnalyzer:
    """Analyzer for C/C++ source file dependencies"""
    
    # Regular expression for #include directives
    INCLUDE_PATTERN = re.compile(r'#\s*include\s*[<"]([^>"]+)[>"]')
    
    def __init__(self, project_root: str):
        """Initialize analyzer with project root directory
        
        Args:
            project_root: Path to the project root directory
        """
        self.project_root = os.path.abspath(project_root)
        
    def parse_includes(self, file_path: str) -> List[str]:
        """Parse include directives from a source file
        
        Args:
            file_path: Path to the source file
            
        Returns:
            List of included header files
        """
        includes = []
        
        try:
            with open(os.path.join(self.project_root, file_path), 'r', encoding='utf-8') as f:
                for line in f:
                    match = self.INCLUDE_PATTERN.search(line)
                    if match:
                        includes.append(match.group(1))
        except (IOError, UnicodeDecodeError):
            # Skip files that can't be read
            pass
            
        return includes
    
    def analyze_dependencies(self, source_files: List[str], header_files: List[str]) -> Dict[str, List[str]]:
        """Analyze dependencies between source files
        
        Args:
            source_files: List of source file paths
            header_files: List of header file paths
            
        Returns:
            Dictionary mapping source files to their dependencies
        """
        dependencies = {}
        header_to_source = self._map_headers_to_sources(source_files, header_files)
        
        for source_file in source_files:
            dependencies[source_file] = []
            includes = self.parse_includes(source_file)
            
            for include in includes:
                # Check if this is a project header (not a system header)
                if include in header_to_source:
                    for dep_source in header_to_source[include]:
                        if dep_source != source_file and dep_source not in dependencies[source_file]:
                            dependencies[source_file].append(dep_source)
        
        return dependencies
    
    def _map_headers_to_sources(self, source_files: List[str], header_files: List[str]) -> Dict[str, List[str]]:
        """Map header files to their corresponding source files
        
        Args:
            source_files: List of source file paths
            header_files: List of header file paths
            
        Returns:
            Dictionary mapping header file names to source files
        """
        header_to_source = {}
        
        # Create mapping of header base names to their full paths
        header_map = {}
        for header in header_files:
            header_name = os.path.basename(header)
            if header_name not in header_map:
                header_map[header_name] = []
            header_map[header_name].append(header)
        
        # For each source file, find its corresponding header
        for source in source_files:
            source_base = os.path.basename(source)
            source_name, _ = os.path.splitext(source_base)
            
            # Check for headers with matching name
            for ext in ['.h', '.hpp', '.hh', '.hxx', '.h++']:
                header_name = source_name + ext
                if header_name in header_map:
                    for header_path in header_map[header_name]:
                        if header_name not in header_to_source:
                            header_to_source[header_name] = []
                        header_to_source[header_name].append(source)
        
        return header_to_source
    
    def build_dependency_graph(self, source_files: List[str], header_files: List[str]) -> Dict[str, Set[str]]:
        """Build dependency graph for source files
        
        Args:
            source_files: List of source file paths
            header_files: List of header file paths
            
        Returns:
            Dictionary representing the dependency graph
        """
        direct_deps = self.analyze_dependencies(source_files, header_files)
        graph = {src: set(deps) for src, deps in direct_deps.items()}
        
        # Resolve transitive dependencies
        for src in source_files:
            if src not in graph:
                graph[src] = set()
            
            # Use depth-first search to find all transitive dependencies
            visited = set()
            stack = list(graph[src])
            
            while stack:
                dep = stack.pop()
                if dep not in visited and dep != src:
                    visited.add(dep)
                    if dep in graph:
                        stack.extend(d for d in graph[dep] if d not in visited)
            
            graph[src] = visited
        
        return graph