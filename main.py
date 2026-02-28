"""
Win-RPA 主程序入口
基于 Robot Framework 的 Windows RPA 自动化平台
"""
import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from gui.main_window import MainWindow


def main():
    """主函数"""
    # 创建应用
    app = QApplication(sys.argv)

    # 设置应用信息
    app.setApplicationName('Win-RPA')
    app.setOrganizationName('RPA Solutions')
    app.setApplicationVersion('1.0.0')

    # 使用 Fusion 风格（现代化界面）
    app.setStyle('Fusion')

    # 启用高DPI支持
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # 创建主窗口
    window = MainWindow()
    window.show()

    # 运行应用
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
