"""
ADB路径自动扫描工具
扫描常见的ADB安装位置
"""
import os
import platform
from pathlib import Path
from typing import List, Dict

def scan_adb_paths() -> List[Dict[str, str]]:
    """
    扫描系统中可能的ADB路径
    返回格式: [{"label": "环境名称", "path": "ADB路径"}]
    """
    adb_paths = []
    system = platform.system()
    
    if system == "Windows":
        adb_paths = scan_windows_adb()
    elif system == "Darwin":  # macOS
        adb_paths = scan_macos_adb()
    elif system == "Linux":
        adb_paths = scan_linux_adb()
    
    # 验证路径是否存在
    valid_paths = []
    for item in adb_paths:
        if os.path.exists(item["path"]):
            valid_paths.append(item)
    
    return valid_paths

def scan_windows_adb() -> List[Dict[str, str]]:
    """扫描Windows系统的ADB路径"""
    paths = []
    
    # 常见的Android SDK安装位置
    common_locations = [
        # Android Studio默认位置
        os.path.expanduser("~/AppData/Local/Android/Sdk/platform-tools/adb.exe"),
        # 用户自定义位置
        "C:/Android/Sdk/platform-tools/adb.exe",
        "C:/Android/platform-tools/adb.exe",
        "C:/platform-tools/adb.exe",
        # Program Files
        "C:/Program Files/Android/Sdk/platform-tools/adb.exe",
        "C:/Program Files (x86)/Android/Sdk/platform-tools/adb.exe",
        # 其他常见位置
        "D:/Android/Sdk/platform-tools/adb.exe",
        "E:/Android/Sdk/platform-tools/adb.exe",
    ]
    
    # 检查环境变量
    android_home = os.environ.get("ANDROID_HOME")
    if android_home:
        env_path = os.path.join(android_home, "platform-tools", "adb.exe")
        paths.append({
            "label": "环境变量 (ANDROID_HOME)",
            "path": env_path
        })
    
    # 检查PATH环境变量
    path_env = os.environ.get("PATH", "")
    for path_dir in path_env.split(";"):
        adb_path = os.path.join(path_dir, "adb.exe")
        if os.path.exists(adb_path) and adb_path not in [p["path"] for p in paths]:
            paths.append({
                "label": f"系统PATH ({path_dir})",
                "path": adb_path
            })
    
    # 添加常见位置
    for i, location in enumerate(common_locations):
        expanded_path = os.path.expanduser(location)
        if expanded_path not in [p["path"] for p in paths]:
            # 提取盘符和主要路径
            drive = Path(expanded_path).drive or "C:"
            if "AppData" in expanded_path:
                label = "Android Studio (默认)"
            elif "Program Files" in expanded_path:
                label = f"Program Files ({drive})"
            else:
                label = f"自定义位置 ({drive})"
            
            paths.append({
                "label": label,
                "path": expanded_path
            })
    
    return paths

def scan_macos_adb() -> List[Dict[str, str]]:
    """扫描macOS系统的ADB路径"""
    paths = []
    
    common_locations = [
        # Android Studio默认位置
        os.path.expanduser("~/Library/Android/sdk/platform-tools/adb"),
        # Homebrew安装
        "/usr/local/bin/adb",
        "/opt/homebrew/bin/adb",
        # 其他常见位置
        "/Applications/Android Studio.app/Contents/sdk/platform-tools/adb",
    ]
    
    # 检查环境变量
    android_home = os.environ.get("ANDROID_HOME")
    if android_home:
        env_path = os.path.join(android_home, "platform-tools", "adb")
        paths.append({
            "label": "环境变量 (ANDROID_HOME)",
            "path": env_path
        })
    
    # 添加常见位置
    for location in common_locations:
        expanded_path = os.path.expanduser(location)
        if expanded_path not in [p["path"] for p in paths]:
            if "Library" in expanded_path:
                label = "Android Studio (默认)"
            elif "homebrew" in expanded_path or "local/bin" in expanded_path:
                label = "Homebrew"
            else:
                label = "自定义位置"
            
            paths.append({
                "label": label,
                "path": expanded_path
            })
    
    return paths

def scan_linux_adb() -> List[Dict[str, str]]:
    """扫描Linux系统的ADB路径"""
    paths = []
    
    common_locations = [
        # Android Studio默认位置
        os.path.expanduser("~/Android/Sdk/platform-tools/adb"),
        # 系统安装
        "/usr/bin/adb",
        "/usr/local/bin/adb",
        # Snap安装
        "/snap/bin/adb",
    ]
    
    # 检查环境变量
    android_home = os.environ.get("ANDROID_HOME")
    if android_home:
        env_path = os.path.join(android_home, "platform-tools", "adb")
        paths.append({
            "label": "环境变量 (ANDROID_HOME)",
            "path": env_path
        })
    
    # 添加常见位置
    for location in common_locations:
        expanded_path = os.path.expanduser(location)
        if expanded_path not in [p["path"] for p in paths]:
            if "Android/Sdk" in expanded_path:
                label = "Android Studio (默认)"
            elif "/usr/bin" in expanded_path or "/usr/local/bin" in expanded_path:
                label = "系统安装"
            elif "snap" in expanded_path:
                label = "Snap"
            else:
                label = "自定义位置"
            
            paths.append({
                "label": label,
                "path": expanded_path
            })
    
    return paths

def scan_python_paths() -> List[Dict[str, str]]:
    """扫描系统中可能的Python路径"""
    paths = []
    system = platform.system()
    
    if system == "Windows":
        common_locations = [
            # Python官方安装
            "C:/Python39/python.exe",
            "C:/Python310/python.exe",
            "C:/Python311/python.exe",
            "C:/Python312/python.exe",
            # AppData安装
            os.path.expanduser("~/AppData/Local/Programs/Python/Python39/python.exe"),
            os.path.expanduser("~/AppData/Local/Programs/Python/Python310/python.exe"),
            os.path.expanduser("~/AppData/Local/Programs/Python/Python311/python.exe"),
            os.path.expanduser("~/AppData/Local/Programs/Python/Python312/python.exe"),
            # Anaconda
            os.path.expanduser("~/anaconda3/python.exe"),
            "C:/ProgramData/Anaconda3/python.exe",
        ]
    elif system == "Darwin":  # macOS
        common_locations = [
            "/usr/local/bin/python3",
            "/opt/homebrew/bin/python3",
            "/usr/bin/python3",
            os.path.expanduser("~/anaconda3/bin/python"),
        ]
    else:  # Linux
        common_locations = [
            "/usr/bin/python3",
            "/usr/local/bin/python3",
            os.path.expanduser("~/anaconda3/bin/python"),
        ]
    
    # 检查PATH环境变量
    path_env = os.environ.get("PATH", "")
    separator = ";" if system == "Windows" else ":"
    for path_dir in path_env.split(separator):
        python_name = "python.exe" if system == "Windows" else "python3"
        python_path = os.path.join(path_dir, python_name)
        if os.path.exists(python_path):
            paths.append({
                "label": f"系统PATH ({path_dir})",
                "path": python_path
            })
    
    # 添加常见位置
    for location in common_locations:
        expanded_path = os.path.expanduser(location)
        if os.path.exists(expanded_path) and expanded_path not in [p["path"] for p in paths]:
            if "anaconda" in expanded_path.lower():
                label = "Anaconda"
            elif "AppData" in expanded_path:
                label = "Python (用户安装)"
            elif "homebrew" in expanded_path:
                label = "Homebrew"
            else:
                label = "Python (系统)"
            
            paths.append({
                "label": label,
                "path": expanded_path
            })
    
    return paths

if __name__ == "__main__":
    """测试扫描功能"""
    print("="*80)
    print("ADB路径扫描")
    print("="*80)
    
    adb_paths = scan_adb_paths()
    if adb_paths:
        print(f"\n找到 {len(adb_paths)} 个ADB路径：")
        for i, item in enumerate(adb_paths, 1):
            print(f"{i}. {item['label']}")
            print(f"   路径: {item['path']}")
    else:
        print("\n未找到ADB路径")
    
    print("\n" + "="*80)
    print("Python路径扫描")
    print("="*80)
    
    python_paths = scan_python_paths()
    if python_paths:
        print(f"\n找到 {len(python_paths)} 个Python路径：")
        for i, item in enumerate(python_paths, 1):
            print(f"{i}. {item['label']}")
            print(f"   路径: {item['path']}")
    else:
        print("\n未找到Python路径")
