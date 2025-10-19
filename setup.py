from setuptools import setup, find_packages

setup(
    name="cmakegen",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "cmakegen=cmakegen.cli:cli",
        ],
    },
    author="Cook Copilot",
    description="Automatic CMake generator for C/C++ projects",
    keywords="cmake, c++, generator",
    python_requires=">=3.6",
)