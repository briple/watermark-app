import PyInstaller.__main__
import os
import shutil

def build_mac_app():
    # PyInstaller 配置参数
    args = [
        'src/main.py',  # 你的主程序文件
        '--name=WatermarkApp',
        '--windowed',  # 不显示命令行窗口（对于 GUI 应用）
        '--onefile',   # 打包成单个文件
        '--icon=assets/icon.icns',  # 可选：应用图标
        '--add-data=src/resources:resources',  # 添加资源文件
        '--target-arch=arm64',  # 对于 Apple Silicon Mac，或 x86_64 对于 Intel Mac
        '--osx-bundle-identifier=com.lalala.watermarkapp',
    ]
    
    # 运行 PyInstaller
    PyInstaller.__main__.run(args)
    
    print("应用程序已构建在 dist/WatermarkApp.app")

if __name__ == '__main__':
    build_mac_app()
