"""
Configuration management for CMake Generator
"""

import os
import json
from typing import Dict, Optional


class Config:
    """Configuration manager for cmakegen"""

    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration

        Args:
            config_file: Path to config file, defaults to ~/.cmakegen/config.json
        """
        if config_file is None:
            home_dir = os.path.expanduser("~")
            config_dir = os.path.join(home_dir, ".cmakegen")
            os.makedirs(config_dir, exist_ok=True)
            config_file = os.path.join(config_dir, "config.json")

        self.config_file = config_file
        self.config = self._load_default_config()
        self.load()

    def _load_default_config(self) -> Dict:
        """Load default configuration"""
        return {
            "cmake": {
                "min_version": "3.10",
                "generator": "MinGW Makefiles",
                "build_type": "Release"
            },
            "compilers": {
                "c_compiler": "gcc",
                "cxx_compiler": "g++",
                "make_program": "mingw32-make"
            },
            "paths": {
                "mingw_root": "D:/Coding/RedPanda-Cpp/MinGW64",
                "visual_studio": "",
                "msbuild": ""
            },
            "project": {
                "cpp_standard": "11",
                "cxx_extensions": False,
                "cxx_required": True
            }
        }

    def load(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                # Merge with defaults
                self._merge_config(self.config, loaded_config)
            except (json.JSONDecodeError, IOError):
                print(f"Warning: Could not load config from {self.config_file}, using defaults")

    def save(self):
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except IOError:
            print(f"Warning: Could not save config to {self.config_file}")

    def _merge_config(self, default: Dict, loaded: Dict):
        """Recursively merge loaded config with defaults"""
        for key, value in loaded.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_config(default[key], value)
            else:
                default[key] = value

    def get_cmake_args(self) -> list:
        """Get CMake configuration arguments"""
        args = []

        # Generator
        if self.config["cmake"]["generator"]:
            args.extend(["-G", self.config["cmake"]["generator"]])

        # Build type
        if self.config["cmake"]["build_type"]:
            args.extend(["-DCMAKE_BUILD_TYPE=" + self.config["cmake"]["build_type"]])

        # Compilers
        mingw_root = self.config["paths"]["mingw_root"]
        if mingw_root and self.config["compilers"]["c_compiler"]:
            c_compiler_path = os.path.join(mingw_root, "bin", self.config["compilers"]["c_compiler"] + ".exe")
            if os.path.exists(c_compiler_path):
                args.extend(["-DCMAKE_C_COMPILER=" + c_compiler_path])

        if mingw_root and self.config["compilers"]["cxx_compiler"]:
            cxx_compiler_path = os.path.join(mingw_root, "bin", self.config["compilers"]["cxx_compiler"] + ".exe")
            if os.path.exists(cxx_compiler_path):
                args.extend(["-DCMAKE_CXX_COMPILER=" + cxx_compiler_path])

        if mingw_root and self.config["compilers"]["make_program"]:
            make_path = os.path.join(mingw_root, "bin", self.config["compilers"]["make_program"] + ".exe")
            if os.path.exists(make_path):
                args.extend(["-DCMAKE_MAKE_PROGRAM=" + make_path])

        return args

    def get_make_command(self) -> str:
        """Get make command path"""
        mingw_root = self.config["paths"]["mingw_root"]
        if mingw_root and self.config["compilers"]["make_program"]:
            make_path = os.path.join(mingw_root, "bin", self.config["compilers"]["make_program"] + ".exe")
            if os.path.exists(make_path):
                return make_path
        return self.config["compilers"]["make_program"]

    def set_mingw_path(self, path: str):
        """Set MinGW root path"""
        self.config["paths"]["mingw_root"] = path
        self.save()

    def set_generator(self, generator: str):
        """Set CMake generator"""
        self.config["cmake"]["generator"] = generator
        self.save()

    def set_cpp_standard(self, standard: str):
        """Set C++ standard"""
        self.config["project"]["cpp_standard"] = standard
        self.save()

    def print_config(self):
        """Print current configuration"""
        print("[cmakeGen] Current Configuration:")
        print("[cmakeGen] " + "=" * 40)
        print(f"[cmakeGen] CMake Generator: {self.config['cmake']['generator']}")
        print(f"[cmakeGen] CMake Min Version: {self.config['cmake']['min_version']}")
        print(f"[cmakeGen] Build Type: {self.config['cmake']['build_type']}")
        print(f"[cmakeGen] C++ Standard: {self.config['project']['cpp_standard']}")
        print(f"[cmakeGen] MinGW Root: {self.config['paths']['mingw_root']}")
        print(f"[cmakeGen] C Compiler: {self.config['compilers']['c_compiler']}")
        print(f"[cmakeGen] CXX Compiler: {self.config['compilers']['cxx_compiler']}")
        print(f"[cmakeGen] Make Program: {self.config['compilers']['make_program']}")
        print("[cmakeGen] " + "=" * 40)