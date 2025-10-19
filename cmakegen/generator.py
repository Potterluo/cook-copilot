"""
CMakeLists.txt generator for C/C++ projects
"""

import os
from typing import Dict, List, Set, Optional, Tuple
from .config import Config


class CMakeGenerator:
    """Generator for CMakeLists.txt files"""
    
    def __init__(self, project_root: str, project_name: str = None, config: Optional[Config] = None):
        """Initialize generator with project root directory

        Args:
            project_root: Path to the project root directory
            project_name: Name of the project (defaults to directory name)
            config: Configuration object (optional)
        """
        self.project_root = os.path.abspath(project_root)
        self.project_name = project_name or os.path.basename(self.project_root)
        self.config = config or Config()
        
    def generate_root_cmake(self, modules: Dict[str, Dict], min_version: str = "3.10") -> str:
        """Generate root CMakeLists.txt content

        Args:
            modules: Dictionary of module information
            min_version: Minimum CMake version

        Returns:
            Content of root CMakeLists.txt
        """
        cpp_standard = self.config.config["project"]["cpp_standard"]
        cxx_required = self.config.config["project"]["cxx_required"]
        cxx_extensions = self.config.config["project"]["cxx_extensions"]

        lines = [
            f"cmake_minimum_required(VERSION {min_version})",
            f"project({self.project_name} C CXX)\n",
            "# Set C++ standard",
            f"set(CMAKE_CXX_STANDARD {cpp_standard})",
            f"set(CMAKE_CXX_STANDARD_REQUIRED {'ON' if cxx_required else 'OFF'})",
            f"set(CMAKE_CXX_EXTENSIONS {'ON' if cxx_extensions else 'OFF'})\n",
            "# Include directories",
        ]

        # Add include directories
        include_dirs = set()
        # Add parent directories of modules with headers to support hierarchical includes
        parent_include_dirs = set()
        
        for module_path, module_info in modules.items():
            # Add directory for modules with header files
            if module_info.get('header_files'):
                module_dir = module_path if module_path else "."
                include_dirs.add(module_dir)
                
                # Also add parent directory to support includes like "subdir/header.h"
                if module_path and module_path != ".":
                    parent_dir = os.path.dirname(module_path)
                    if parent_dir:
                        parent_include_dirs.add(parent_dir)
                        
            # Also add directory for modules with source files (they might have local headers)
            if module_info.get('source_files'):
                module_dir = module_path if module_path else "."
                include_dirs.add(module_dir)
                
                # Also add parent directory to support includes like "subdir/header.h"
                if module_path and module_path != ".":
                    parent_dir = os.path.dirname(module_path)
                    if parent_dir:
                        parent_include_dirs.add(parent_dir)

        # Combine include directories, prioritizing parent directories
        all_include_dirs = parent_include_dirs | include_dirs
        
        if all_include_dirs:
            lines.append("include_directories(")
            for include_dir in sorted(all_include_dirs):
                # 使用正斜杠替换反斜杠，确保CMake路径兼容性
                # 确保路径格式正确，相对于项目根目录
                if include_dir == ".":
                    lines.append("    .")
                else:
                    lines.append(f"    {include_dir.replace(os.path.sep, '/')}")
            lines.append(")\n")

        # Determine if there's a main file to identify the executable target
        main_module = self._find_main_module(modules)

        # Add subdirectories for modules
        non_root_modules = [path for path in modules.keys() if path]
        if non_root_modules:
            lines.append("# Add subdirectories")
            for module_path in sorted(non_root_modules):
                # 使用正斜杠替换反斜杠，确保CMake路径兼容性
                lines.append(f"add_subdirectory({module_path.replace(os.path.sep, '/')})")
            lines.append("")

        # Handle executable target
        if main_module:
            module_path, module_info = main_module
            if module_path == "":
                # Root module is executable
                lines.append("# Main executable")
                lines.extend(self._generate_target("${PROJECT_NAME}", module_info, "executable"))
                
                # Link with library modules
                library_targets = []
                for path, info in modules.items():
                    if path and (info.get('source_files') or info.get('header_files')):
                        lib_name = os.path.basename(path) if path else self.project_name
                        library_targets.append(lib_name)

                if library_targets:
                    lines.append(f"target_link_libraries(${{PROJECT_NAME}} {' '.join(library_targets)})")
            else:
                # Create executable that links to library modules
                module_name = os.path.basename(module_path) if module_path else self.project_name
                lines.append("# Main executable")
                source_files = module_info.get('source_files', [])
                if source_files:
                    lines.append(f"add_executable({self.project_name})")
                    for source in source_files:
                        lines.append(f"target_sources({self.project_name} PRIVATE {source.replace(os.path.sep, '/')})")

                    # Link with library modules
                    library_targets = []
                    for path, info in modules.items():
                        if path != module_path and (info.get('source_files') or info.get('header_files')):
                            lib_name = os.path.basename(path) if path else self.project_name
                            library_targets.append(lib_name)

                    if library_targets:
                        lines.append(f"target_link_libraries({self.project_name} {' '.join(library_targets)})")
                else:
                    # If main module has no source files, create executable with main.cpp
                    lines.append(f"add_executable({self.project_name} main.cpp)")

                    # Link with library modules
                    library_targets = []
                    for path, info in modules.items():
                        if info.get('source_files'):
                            lib_name = os.path.basename(path) if path else self.project_name
                            library_targets.append(lib_name)

                    if library_targets:
                        lines.append(f"target_link_libraries({self.project_name} {' '.join(library_targets)})")

        return "\n".join(lines)
    
    def generate_module_cmake(self, module_path: str, module_info: Dict,
                             target_type: str = "library") -> str:
        """Generate CMakeLists.txt content for a module

        Args:
            module_path: Path to the module
            module_info: Module information
            target_type: Type of target (library or executable)

        Returns:
            Content of module CMakeLists.txt
        """
        module_name = os.path.basename(module_path) if module_path else self.project_name

        # Adjust file paths to be relative to module directory
        adjusted_module_info = {
            'source_files': [os.path.relpath(f, module_path) if module_path else f for f in module_info.get('source_files', [])],
            'header_files': [os.path.relpath(f, module_path) if module_path else f for f in module_info.get('header_files', [])]
        }

        lines = []
        lines.extend(self._generate_target(module_name, adjusted_module_info, target_type))

        return "\n".join(lines)
    
    def _find_main_module(self, modules: Dict[str, Dict]) -> Optional[Tuple[str, Dict]]:
        """Find the module containing the main function

        Args:
            modules: Dictionary of module information

        Returns:
            Tuple of (module_path, module_info) or None if not found
        """
        import re

        main_pattern = re.compile(r'int\s+main\s*\(')

        for module_path, module_info in modules.items():
            source_files = module_info.get('source_files', [])
            for source_file in source_files:
                file_path = os.path.join(self.project_root, source_file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if main_pattern.search(content):
                            return module_path, module_info
                except (IOError, UnicodeDecodeError):
                    continue

        # If no main function found, return the first module with source files
        for module_path, module_info in modules.items():
            if module_info.get('source_files'):
                return module_path, module_info

        return None

    def _generate_target(self, target_name: str, module_info: Dict,
                        target_type: str = "library") -> List[str]:
        """Generate CMake target definition

        Args:
            target_name: Name of the target
            module_info: Module information
            target_type: Type of target (library or executable)

        Returns:
            List of CMake commands for the target
        """
        lines = []

        # Add source files
        if module_info.get('source_files'):
            lines.append(f"set({target_name}_SOURCES")
            for source in sorted(module_info['source_files']):
                # 使用正斜杠替换反斜杠，确保CMake路径兼容性
                lines.append(f"    {source.replace(os.path.sep, '/')}")
            lines.append(")")

            # Add header files if available
            if module_info.get('header_files'):
                lines.append(f"\nset({target_name}_HEADERS")
                for header in sorted(module_info['header_files']):
                    # 使用正斜杠替换反斜杠，确保CMake路径兼容性
                    lines.append(f"    {header.replace(os.path.sep, '/')}")
                lines.append(")")
                lines.append(f"\nsource_group(\"Header Files\" FILES ${{{target_name}_HEADERS}})")
                lines.append(f"source_group(\"Source Files\" FILES ${{{target_name}_SOURCES}})")

            # Create target
            if target_type.lower() == "executable":
                lines.append(f"\nadd_executable({target_name} ${{{target_name}_SOURCES}})")
            else:
                lines.append(f"\nadd_library({target_name} ${{{target_name}_SOURCES}})")

        return lines
    
    def write_cmake_files(self, modules: Dict[str, Dict]) -> List[str]:
        """Write CMakeLists.txt files for all modules
        
        Args:
            modules: Dictionary of module information
            
        Returns:
            List of generated CMakeLists.txt file paths
        """
        generated_files = []
        
        # Generate root CMakeLists.txt
        root_cmake_path = os.path.join(self.project_root, "CMakeLists.txt")
        root_content = self.generate_root_cmake(modules)
        with open(root_cmake_path, 'w') as f:
            f.write(root_content)
        generated_files.append(os.path.relpath(root_cmake_path, self.project_root))
        
        # Generate CMakeLists.txt for each non-root module
        for module_path, module_info in modules.items():
            if not module_path:  # Skip root module
                continue
                
            # For modules without source files (header-only modules), 
            # we still generate a CMakeLists.txt file with an INTERFACE library
            module_dir = os.path.join(self.project_root, module_path)
            os.makedirs(module_dir, exist_ok=True)
            
            module_cmake_path = os.path.join(module_dir, "CMakeLists.txt")
            
            if module_info.get('source_files'):
                # Regular module with source files
                module_content = self.generate_module_cmake(module_path, module_info)
            else:
                # Header-only module
                module_name = os.path.basename(module_path)
                module_content = f"# Header-only library\nadd_library({module_name} INTERFACE)\n"
                
                # Add header files to the interface library
                if module_info.get('header_files'):
                    module_content += f"target_sources({module_name} INTERFACE\n"
                    for header in module_info['header_files']:
                        rel_header_path = os.path.relpath(os.path.join(self.project_root, header), module_dir)
                        module_content += f"    ${{CMAKE_CURRENT_SOURCE_DIR}}/{rel_header_path.replace(os.path.sep, '/')}\n"
                    module_content += ")\n"
            
            with open(module_cmake_path, 'w') as f:
                f.write(module_content)
            generated_files.append(os.path.relpath(module_cmake_path, self.project_root))
        
        return generated_files