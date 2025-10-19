# CMake Generator

自动读取C/C++项目并生成CMakeLists.txt文件的工具。

## 功能特点

- 自动扫描C/C++项目结构
- 识别源文件和头文件
- 分析文件依赖关系
- 按模块生成CMakeLists.txt文件
- 支持多级目录结构
- 配置文件管理（编译器路径、CMake生成器等）
- 一键构建功能
- 跨平台支持

## 安装

### 方式1：通过wheel包安装（推荐）

```bash
# 安装预编译的wheel包
pip install cmakegen-*.whl

# 或者从PyPI安装（如果已发布）
pip install cmakegen
```

### 方式2：从源码安装

```bash
# 克隆仓库并安装
git clone <repository-url>
cd cook-copilot
pip install -e .
```

### 生成wheel包

如果你想自己构建wheel包：

```bash
# 克隆仓库
git clone <repository-url>
cd cook-copilot

# 构建wheel包
python setup.py bdist_wheel

# 安装生成的wheel包
pip install dist/cmakegen-*.whl
```

构建完成后，wheel包会生成在 `dist/` 目录下。

## 配置

### 初始化配置

```bash
# 初始化默认配置文件（创建 ~/.cmakegen/config.json）
cmakegen config init
```

### 配置管理

```bash
# 显示当前配置
cmakegen config show

# 设置MinGW路径
cmakegen config set-mingw "D:/Coding/RedPanda-Cpp/MinGW64"

# 设置CMake生成器
cmakegen config set-generator "MinGW Makefiles"

# 设置C++标准
cmakegen config set-cpp-standard 14
```

### 配置文件示例

配置文件位置：`~/.cmakegen/config.json`

```json
{
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
    "mingw_root": "D:/Coding/RedPanda-Cpp/MinGW64"
  },
  "project": {
    "cpp_standard": "11",
    "cxx_extensions": false,
    "cxx_required": true
  }
}
```

## 使用方法

### 生成CMakeLists.txt

```bash
# 为指定项目生成CMakeLists.txt
cmakegen generate /path/to/project

# 指定项目名称
cmakegen generate /path/to/project --project-name MyProject

# 指定CMake最低版本
cmakegen generate /path/to/project --min-version 3.15

# 强制覆盖已存在的CMakeLists.txt
cmakegen generate /path/to/project --force
```

### 扫描项目结构

```bash
# 扫描并显示项目结构
cmakegen scan /path/to/project
```

### 分析依赖关系

```bash
# 分析并显示源文件依赖关系
cmakegen analyze /path/to/project
```

### 构建项目

```bash
# 构建项目（使用配置文件中的设置）
cmakegen build /path/to/project

# 清理并重新构建
cmakegen build /path/to/project --clean
```

### 完整工作流程

```bash
# 1. 初始化配置
cmakegen config init
cmakegen config set-mingw "D:/Coding/RedPanda-Cpp/MinGW64"

# 2. 生成CMakeLists.txt
cmakegen generate examples/simple_project --force

# 3. 构建项目
cmakegen build examples/simple_project --clean
```

## 编译和执行详解

### 1. 配置编译环境

首次使用需要配置编译器路径：

```bash
# 初始化配置文件（创建 ~/.cmakegen/config.json）
cmakegen config init

# 设置MinGW路径（根据实际路径调整）
cmakegen config set-mingw "D:/Coding/RedPanda-Cpp/MinGW64"

# 设置CMake生成器
cmakegen config set-generator "MinGW Makefiles"

# 设置C++标准（可选）
cmakegen config set-cpp-standard 17

# 查看当前配置
cmakegen config show
```

### 2. 项目扫描和生成

扫描项目结构：
```bash
cmakegen scan /path/to/your/project
```

输出示例：
```
[cmakeGen] Scanning project structure in /path/to/your/project...
[cmakeGen] Found 3 source files and 2 header files
[cmakeGen] Detected 2 modules

Modules:
  - (root): 1 source files, 1 header files
  - src: 2 source files, 1 header files
```

生成CMakeLists.txt文件：
```bash
cmakegen generate /path/to/your/project
```

输出示例：
```
[cmakeGen] Scanning project structure in /path/to/your/project...
[cmakeGen] Found 3 source files and 2 header files
[cmakeGen] Detected 2 modules
[cmakeGen] Generating CMakeLists.txt files...
[cmakeGen] Generated 3 CMakeLists.txt files:
  - CMakeLists.txt
  - src\CMakeLists.txt
```

### 3. 构建项目

使用cmakegen自动构建：
```bash
# 构建项目（自动创建build目录）
cmakegen build /path/to/your/project

# 清理并重新构建
cmakegen build /path/to/your/project --clean
```

构建过程输出：
```
[cmakeGen] Configuring project in /path/to/your/project/build...
[cmakeGen] Project configured successfully
[cmakeGen] Building project...
[cmakeGen] Project built successfully
[cmakeGen] Running your_project...
[cmakeGen] Program executed successfully
```

### 4. 手动构建（可选）

如果需要手动构建，也可以使用生成的CMakeLists.txt：

```bash
cd /path/to/your/project
mkdir build && cd build
cmake .. -G "MinGW Makefiles" -DCMAKE_C_COMPILER="D:/Coding/RedPanda-Cpp/MinGW64/bin/gcc.exe" -DCMAKE_CXX_COMPILER="D:/Coding/RedPanda-Cpp/MinGW64/bin/g++.exe"
"D:/Coding/RedPanda-Cpp/MinGW64/bin/mingw32-make.exe"
./your_project.exe
```

![效果图](/docs/pic1.png)

### 5. 依赖分析

分析项目依赖关系：
```bash
cmakegen analyze /path/to/your/project
```

输出示例：
```
[cmakeGen] Scanning project structure in /path/to/your/project...
[cmakeGen] Analyzing dependencies...

Dependencies:
  - main.cpp depends on:
    - utils.h
  - utils.c has no dependencies
```

### 6. 支持的项目类型

cmakegen支持多种项目结构：

- **单文件项目**：仅包含main.cpp的简单项目
- **简单目录结构**：源文件和头文件在同一目录
- **多模块项目**：不同功能的代码放在不同子目录
- **头文件库项目**：主要包含头文件和少量实现文件
- **复杂嵌套结构**：多层目录结构的项目

### 7. 常见问题解决

#### 编译器找不到
```bash
# 检查MinGW路径是否正确
cmakegen config set-mingw "D:/你的实际路径/MinGW64"
```

#### CMake配置失败
```bash
# 清理build目录重新构建
cmakegen build /path/to/project --clean
```

#### 程序运行错误
生成的CMakeLists.txt可能需要手动调整，特别是：
- 复杂的库依赖关系
- 特殊的编译选项
- 第三方库链接

### 8. 输出格式说明

cmakegen使用统一的输出格式，所有消息都以`[cmakeGen]`开头，便于在日志中过滤和识别。

输出示例：
```
[cmakeGen] Scanning project structure in /path/to/project...
[cmakeGen] Found 3 source files and 2 header files
[cmakeGen] Generated 3 CMakeLists.txt files:
[cmakeGen] No executable found to run
[cmakeGen] Build process failed: error details
```

## 示例项目

在`examples`目录下提供了多个示例项目：

1. **simple_project** - 简单的C项目示例
2. **multi_module** - 多模块的C++项目示例

### 测试所有示例项目

```bash
# 测试简单项目
cmakegen build examples/simple_project --clean

# 测试多模块项目
cmakegen build examples/multi_module --clean
```

## 开发

### 依赖

- Python 3.6+
- click
- colorama

### 项目结构

```
cook-copilot/
├── cmakegen/                    # 主要功能包
│   ├── __init__.py             # 包初始化和版本信息
│   ├── scanner.py              # 项目结构扫描
│   ├── dependency.py           # 依赖关系分析
│   ├── generator.py            # CMakeLists.txt生成
│   ├── config.py               # 配置管理
│   └── cli.py                  # 命令行接口
├── examples/                   # 示例项目
│   ├── simple_project/         # 简单C项目
│   ├── multi_module/           # 多模块C++项目
├── build/                      # 构建输出目录
├── dist/                       # 分发包目录
├── setup.py                    # 安装脚本
├── README.md                   # 项目说明文档
└── LICENSE                     # 许可证文件
```

### 核心模块说明

- **scanner.py**: 扫描项目目录结构，识别源文件、头文件和模块
- **dependency.py**: 分析源文件之间的include依赖关系
- **generator.py**: 根据扫描结果生成CMakeLists.txt文件
- **config.py**: 管理编译器路径、CMake生成器等配置信息
- **cli.py**: 提供命令行接口，整合所有功能模块

## 支持的项目结构

- 单文件项目
- 简单目录结构
- 多模块项目（每个子目录一个模块）
- 头文件库项目
- 复杂嵌套目录结构

## 支持的编译器

- GCC (MinGW)
- Clang
- MSVC (Visual Studio)

## 支持的CMake生成器

- MinGW Makefiles
- Visual Studio (2017, 2019, 2022)
- Unix Makefiles
- Ninja