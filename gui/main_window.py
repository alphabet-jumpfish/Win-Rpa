"""
PyQt5 主窗口
RPA 桌面应用的主界面
"""
import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QAction,
    QMessageBox, QStatusBar, QToolBar
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize


class MainWindow(QMainWindow):
    """主窗口类"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        # 设置窗口属性
        self.setWindowTitle('Win-RPA - Robot Framework 自动化平台')
        self.setGeometry(100, 100, 1200, 800)

        # 创建中心标签页组件
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # 延迟导入避免循环依赖
        from gui.flow_editor import FlowEditorWidget
        from gui.executor import ExecutorWidget
        from gui.log_viewer import LogViewerWidget

        # 创建各个功能页面
        self.flow_editor = FlowEditorWidget(self)
        self.executor = ExecutorWidget(self)
        self.log_viewer = LogViewerWidget(self)

        # 添加标签页
        self.tabs.addTab(self.flow_editor, "流程编辑器")
        self.tabs.addTab(self.executor, "流程执行器")
        self.tabs.addTab(self.log_viewer, "执行日志")

        # 创建菜单栏
        self.create_menu_bar()

        # 创建工具栏
        self.create_tool_bar()

        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('就绪')

        # 连接信号
        self.connect_signals()

    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')

        new_action = QAction('新建流程(&N)', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_flow)
        file_menu.addAction(new_action)

        open_action = QAction('打开流程(&O)', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_flow)
        file_menu.addAction(open_action)

        save_action = QAction('保存流程(&S)', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_flow)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction('退出(&X)', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 执行菜单
        run_menu = menubar.addMenu('执行(&R)')

        run_action = QAction('运行流程(&R)', self)
        run_action.setShortcut('F5')
        run_action.triggered.connect(self.run_flow)
        run_menu.addAction(run_action)

        stop_action = QAction('停止执行(&S)', self)
        stop_action.setShortcut('Shift+F5')
        stop_action.triggered.connect(self.stop_flow)
        run_menu.addAction(stop_action)

        # 视图菜单
        view_menu = menubar.addMenu('视图(&V)')

        editor_action = QAction('流程编辑器(&E)', self)
        editor_action.triggered.connect(lambda: self.tabs.setCurrentIndex(0))
        view_menu.addAction(editor_action)

        executor_action = QAction('流程执行器(&X)', self)
        executor_action.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
        view_menu.addAction(executor_action)

        log_action = QAction('执行日志(&L)', self)
        log_action.triggered.connect(lambda: self.tabs.setCurrentIndex(2))
        view_menu.addAction(log_action)

        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')

        about_action = QAction('关于(&A)', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_tool_bar(self):
        """创建工具栏"""
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(toolbar)

        # 新建
        new_btn = QAction('新建', self)
        new_btn.triggered.connect(self.new_flow)
        toolbar.addAction(new_btn)

        # 打开
        open_btn = QAction('打开', self)
        open_btn.triggered.connect(self.open_flow)
        toolbar.addAction(open_btn)

        # 保存
        save_btn = QAction('保存', self)
        save_btn.triggered.connect(self.save_flow)
        toolbar.addAction(save_btn)

        toolbar.addSeparator()

        # 运行
        run_btn = QAction('运行', self)
        run_btn.triggered.connect(self.run_flow)
        toolbar.addAction(run_btn)

        # 停止
        stop_btn = QAction('停止', self)
        stop_btn.triggered.connect(self.stop_flow)
        toolbar.addAction(stop_btn)

    def connect_signals(self):
        """连接信号与槽"""
        # 编辑器和执行器之间的通信
        self.flow_editor.flow_saved.connect(self.on_flow_saved)
        self.executor.execution_finished.connect(self.on_execution_finished)
        self.executor.status_changed.connect(self.update_status_bar)

    def new_flow(self):
        """新建流程"""
        self.flow_editor.new_flow()
        self.tabs.setCurrentIndex(0)
        self.update_status_bar('已创建新流程')

    def open_flow(self):
        """打开流程"""
        self.flow_editor.open_flow()
        self.tabs.setCurrentIndex(0)

    def save_flow(self):
        """保存流程"""
        result = self.flow_editor.save_flow()
        if result:
            self.update_status_bar('流程已保存')

    def run_flow(self):
        """运行流程"""
        # 先保存当前流程
        if self.flow_editor.has_unsaved_changes():
            reply = QMessageBox.question(
                self,
                '保存确认',
                '流程已修改，是否保存后执行？',
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if reply == QMessageBox.Yes:
                if not self.save_flow():
                    return
            elif reply == QMessageBox.Cancel:
                return

        # 切换到执行器标签页
        self.tabs.setCurrentIndex(1)

        # 获取当前流程配置
        flow_config = self.flow_editor.get_flow_config()
        if flow_config:
            self.executor.run_flow(flow_config)
        else:
            QMessageBox.warning(self, '警告', '请先创建或加载流程配置')

    def stop_flow(self):
        """停止执行"""
        self.executor.stop_flow()
        self.update_status_bar('已停止执行')

    def on_flow_saved(self, file_path):
        """流程保存完成的回调"""
        self.update_status_bar(f'流程已保存: {file_path}')

    def on_execution_finished(self, result):
        """执行完成的回调"""
        if result.get('success'):
            self.update_status_bar(
                f"执行成功! 耗时: {result.get('execution_time', 0)}秒"
            )
            # 刷新日志视图
            self.log_viewer.refresh_logs()
        else:
            self.update_status_bar('执行失败')

    def update_status_bar(self, message):
        """更新状态栏"""
        self.status_bar.showMessage(message)

    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            '关于 Win-RPA',
            '<h2>Win-RPA 自动化平台</h2>'
            '<p>版本: 1.0.0</p>'
            '<p>基于 Robot Framework 和 Selenium 的 Windows RPA 解决方案</p>'
            '<p>用于智能体网站的自动化操作和数据提取</p>'
            '<br>'
            '<p>技术栈:</p>'
            '<ul>'
            '<li>Python 3.x</li>'
            '<li>Robot Framework</li>'
            '<li>Selenium WebDriver</li>'
            '<li>PyQt5</li>'
            '</ul>'
        )

    def closeEvent(self, event):
        """关闭事件处理"""
        if self.flow_editor.has_unsaved_changes():
            reply = QMessageBox.question(
                self,
                '确认退出',
                '流程未保存，确定要退出吗？',
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用现代化风格

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
