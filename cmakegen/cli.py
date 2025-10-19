"""
Command-line interface for CMake Generator
"""

import os
import sys
import click

from cmakegen.scanner import ProjectScanner
from cmakegen.dependency import DependencyAnalyzer
from cmakegen.generator import CMakeGenerator
from cmakegen.config import Config


def print_success(message):
    """Print success message"""
    click.echo(f"[cmakeGen] {message}")


def print_info(message):
    """Print info message"""
    click.echo(f"[cmakeGen] {message}")


def print_warning(message):
    """Print warning message"""
    click.echo(f"[cmakeGen] {message}")


def print_error(message):
    """Print error message"""
    click.echo(f"[cmakeGen] {message}")


@click.group()
@click.version_option()
def cli():
    """CMake Generator for C/C++ Projects"""
    pass


@cli.command()
@click.argument('project_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--project-name', '-n', help='Project name (defaults to directory name)')
@click.option('--min-version', '-v', default='3.10', help='Minimum CMake version')
@click.option('--force', '-f', is_flag=True, help='Overwrite existing CMakeLists.txt files')
def generate(project_path, project_name=None, min_version='3.10', force=False):
    """Generate CMakeLists.txt files for a C/C++ project"""
    project_path = os.path.abspath(project_path)
    project_name = project_name or os.path.basename(project_path)
    
    # Check if CMakeLists.txt already exists
    root_cmake = os.path.join(project_path, 'CMakeLists.txt')
    if os.path.exists(root_cmake) and not force:
        print_error(f"CMakeLists.txt already exists in {project_path}")
        print_info("Use --force to overwrite existing files")
        sys.exit(1)
    
    print_info(f"Scanning project structure in {project_path}...")
    scanner = ProjectScanner(project_path)
    project_info = scanner.scan_project()
    
    print_info(f"Found {len(project_info['source_files'])} source files and {len(project_info['header_files'])} header files")
    print_info(f"Detected {len(project_info['modules'])} modules")
    
    # Generate CMakeLists.txt files
    print_info("Generating CMakeLists.txt files...")
    config = Config()
    generator = CMakeGenerator(project_path, project_name, config)
    generated_files = generator.write_cmake_files(project_info['modules'])
    
    print_success(f"Generated {len(generated_files)} CMakeLists.txt files:")
    for file_path in generated_files:
        click.echo(f"  - {file_path}")


@cli.command()
@click.argument('project_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
def scan(project_path):
    """Scan and display project structure"""
    project_path = os.path.abspath(project_path)
    
    print_info(f"Scanning project structure in {project_path}...")
    scanner = ProjectScanner(project_path)
    project_info = scanner.scan_project()
    
    print_success(f"Found {len(project_info['source_files'])} source files and {len(project_info['header_files'])} header files")
    print_success(f"Detected {len(project_info['modules'])} modules")
    
    # Display modules
    click.echo("\nModules:")
    for module_path, module_info in project_info['modules'].items():
        module_name = module_path if module_path else "(root)"
        click.echo(f"  - {module_name}: {len(module_info['source_files'])} source files, {len(module_info['header_files'])} header files")


@cli.command()
@click.argument('project_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
def analyze(project_path):
    """Analyze dependencies between source files"""
    project_path = os.path.abspath(project_path)

    print_info(f"Scanning project structure in {project_path}...")
    scanner = ProjectScanner(project_path)
    project_info = scanner.scan_project()

    print_info("Analyzing dependencies...")
    analyzer = DependencyAnalyzer(project_path)
    dependencies = analyzer.analyze_dependencies(
        project_info['source_files'],
        project_info['header_files']
    )

    # Display dependencies
    click.echo("\nDependencies:")
    for source, deps in dependencies.items():
        if deps:
            click.echo(f"  - {source} depends on:")
            for dep in deps:
                click.echo(f"    - {dep}")
        else:
            click.echo(f"  - {source} has no dependencies")


@cli.group()
def config():
    """Configuration management"""
    pass


@config.command('show')
def config_show():
    """Show current configuration"""
    config = Config()
    config.print_config()


@config.command('set-mingw')
@click.argument('path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
def config_set_mingw(path):
    """Set MinGW root path"""
    config = Config()
    config.set_mingw_path(os.path.abspath(path))
    print_success(f"MinGW path set to: {os.path.abspath(path)}")


@config.command('set-generator')
@click.argument('generator')
def config_set_generator(generator):
    """Set CMake generator (e.g., 'MinGW Makefiles', 'Visual Studio 17 2022')"""
    config = Config()
    config.set_generator(generator)
    print_success(f"CMake generator set to: {generator}")


@config.command('set-cpp-standard')
@click.argument('standard', type=click.Choice(['11', '14', '17', '20', '23']))
def config_set_cpp_standard(standard):
    """Set C++ standard"""
    config = Config()
    config.set_cpp_standard(standard)
    print_success(f"C++ standard set to: {standard}")


@config.command('init')
def config_init():
    """Initialize default configuration file"""
    config = Config()
    config.save()
    print_success(f"Configuration initialized at: {config.config_file}")
    print_info("You can now edit the configuration file or use 'cmakegen config set-*' commands")


@cli.command()
@click.argument('project_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--clean', '-c', is_flag=True, help='Clean build directory before building')
def build(project_path, clean=False):
    """Build a C/C++ project using CMake"""
    project_path = os.path.abspath(project_path)
    config = Config()

    build_dir = os.path.join(project_path, 'build')

    # Clean build directory if requested
    if clean and os.path.exists(build_dir):
        print_info(f"Cleaning build directory: {build_dir}")
        import shutil
        shutil.rmtree(build_dir)

    # Create build directory
    os.makedirs(build_dir, exist_ok=True)

    # Get CMake arguments from config
    cmake_args = config.get_cmake_args()

    print_info(f"Configuring project in {build_dir}...")
    cmake_cmd = ['cmake', '..'] + cmake_args

    try:
        import subprocess

        # Set up environment variables for MinGW
        env = os.environ.copy()
        mingw_bin = config.config["paths"]["mingw_root"]
        if mingw_bin:
            mingw_bin_path = os.path.join(mingw_bin, "bin")
            # Ensure MinGW bin directory is first in PATH
            current_path = env.get('PATH', '')
            if mingw_bin_path not in current_path:
                env['PATH'] = mingw_bin_path + ';' + current_path

        # Configure project
        print_info(f"Using CMake command: {' '.join(cmake_cmd)}")
        result = subprocess.run(cmake_cmd, cwd=build_dir, capture_output=True, text=True, env=env)
        if result.returncode != 0:
            print_error(f"CMake configuration failed:")
            print_error(f"Return code: {result.returncode}")
            print_error(f"Stdout: {result.stdout}")
            print_error(f"Stderr: {result.stderr}")
            sys.exit(1)
        print_success("Project configured successfully")

        # Build project
        print_info("Building project...")
        make_cmd = config.get_make_command()
        print_info(f"Using make command: {make_cmd}")
        result = subprocess.run([make_cmd], cwd=build_dir, capture_output=True, text=True, env=env)
        if result.returncode != 0:
            print_error(f"Build failed:")
            print_error(f"Return code: {result.returncode}")
            print_error(f"Stdout: {result.stdout}")
            print_error(f"Stderr: {result.stderr}")
            sys.exit(1)
        print_success("Project built successfully")

        # Try to run the executable
        project_name = os.path.basename(project_path)
        executable_path = os.path.join(build_dir, f"{project_name}.exe")
        if os.path.exists(executable_path):
            print_info(f"Running {project_name}...")
            result = subprocess.run([executable_path], cwd=build_dir, env=env)
            if result.returncode == 0:
                print_success("Program executed successfully")
            else:
                print_warning(f"Program exited with code: {result.returncode}")
        else:
            print_warning("No executable found to run")

    except subprocess.SubprocessError as e:
        print_error(f"Build process failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    cli()