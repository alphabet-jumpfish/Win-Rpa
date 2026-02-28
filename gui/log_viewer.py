"""
日志查看器界面
用于查看历史执行记录和日志
"""
import os
import webbrowser
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QGroupBox, QMessageBox,
    QTextEdit, QSplitter
)
from PyQt5.QtCore import Qt


class LogViewerWidget(QWidget):
    """日志查看器组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        os.makedirs(self.logs_dir, exist_ok=True)
        self.init_ui()
        self.refresh_logs()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()

        # 使用分割器分隔日志列表和详情
        splitter = QSplitter(Qt.Horizontal)

        # 左侧：日志文件列表
        left_widget = QWidget()
        left_layout = QVBoxLayout()

        list_group = QGroupBox('执行记录')
        list_layout = QVBoxLayout()

        self.log_list = QListWidget()
        self.log_list.itemClicked.connect(self.on_log_selected)
        list_layout.addWidget(self.log_list)

        # 按钮组
        btn_layout = QHBoxLayout()

        refresh_btn = QPushButton('刷新')
        refresh_btn.clicked.connect(self.refresh_logs)
        btn_layout.addWidget(refresh_btn)

        open_btn = QPushButton('打开报告')
        open_btn.clicked.connect(self.open_html_report)
        btn_layout.addWidget(open_btn)

        open_folder_btn = QPushButton('打开目录')
        open_folder_btn.clicked.connect(self.open_logs_folder)
        btn_layout.addWidget(open_folder_btn)

        delete_btn = QPushButton('删除')
        delete_btn.clicked.connect(self.delete_log)
        btn_layout.addWidget(delete_btn)

        list_layout.addLayout(btn_layout)
        list_group.setLayout(list_layout)
        left_layout.addWidget(list_group)
        left_widget.setLayout(left_layout)

        # 右侧：日志详情
        right_widget = QWidget()
        right_layout = QVBoxLayout()

        details_group = QGroupBox('日志详情')
        details_layout = QVBoxLayout()

        self.log_details = QTextEdit()
        self.log_details.setReadOnly(True)
        self.log_details.setStyleSheet('''
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: Consolas, Monaco, monospace;
                font-size: 10pt;
            }
        ''')
        details_layout.addWidget(self.log_details)

        details_group.setLayout(details_layout)
        right_layout.addWidget(details_group)
        right_widget.setLayout(right_layout)

        # 添加到分割器
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def refresh_logs(self):
        """刷新日志列表"""
        self.log_list.clear()

        if not os.path.exists(self.logs_dir):
            return

        # 获取所有日志文件
        log_files = []

        for filename in os.listdir(self.logs_dir):
            if filename.endswith('.html') or filename.endswith('.xml'):
                file_path = os.path.join(self.logs_dir, filename)
                # 获取文件修改时间
                mtime = os.path.getmtime(file_path)
                log_files.append((filename, file_path, mtime))

        # 按修改时间降序排序
        log_files.sort(key=lambda x: x[2], reverse=True)

        # 去重：只显示每个时间戳的 HTML 文件
        displayed_files = set()
        for filename, file_path, mtime in log_files:
            # 提取时间戳（假设格式为 output_20240228_153000.html）
            if filename.startswith('output_') and filename.endswith('.html'):
                timestamp = filename.replace('output_', '').replace('.html', '')
                if timestamp not in displayed_files:
                    displayed_files.add(timestamp)

                    # 格式化时间显示
                    try:
                        dt = datetime.strptime(timestamp, '%Y%m%d_%H%M%S')
                        display_name = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        display_name = timestamp

                    # 添加到列表
                    item = QListWidgetItem(display_name)
                    item.setData(Qt.UserRole, {
                        'timestamp': timestamp,
                        'html_file': file_path,
                        'xml_file': file_path.replace('.html', '.xml'),
                        'debug_file': os.path.join(self.logs_dir, f'output_{timestamp}_debug.txt')
                    })
                    self.log_list.addItem(item)

        # 更新显示
        if self.log_list.count() == 0:
            self.log_details.setPlainText('暂无执行记录')
        else:
            self.log_details.setPlainText('请从左侧选择一条记录查看详情')

    def on_log_selected(self, item):
        """日志选择事件"""
        data = item.data(Qt.UserRole)
        if not data:
            return

        # 读取并显示调试日志
        debug_file = data.get('debug_file', '')
        if os.path.exists(debug_file):
            try:
                with open(debug_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.log_details.setPlainText(content)
            except Exception as e:
                self.log_details.setPlainText(f'读取日志失败: {str(e)}')
        else:
            # 如果没有调试文件，显示基本信息
            info = f"""
执行时间: {data.get('timestamp', 'N/A')}
HTML报告: {data.get('html_file', 'N/A')}
XML输出: {data.get('xml_file', 'N/A')}

点击 "打开报告" 按钮查看详细的HTML报告
            """.strip()
            self.log_details.setPlainText(info)

    def open_html_report(self):
        """打开 HTML 报告"""
        current_item = self.log_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, '警告', '请先选择一条执行记录')
            return

        data = current_item.data(Qt.UserRole)
        html_file = data.get('html_file', '')

        if os.path.exists(html_file):
            try:
                webbrowser.open(html_file)
            except Exception as e:
                QMessageBox.critical(self, '错误', f'打开报告失败: {str(e)}')
        else:
            QMessageBox.warning(self, '警告', '报告文件不存在')

    def open_logs_folder(self):
        """打开日志目录"""
        try:
            os.startfile(self.logs_dir)
        except Exception as e:
            QMessageBox.critical(self, '错误', f'打开目录失败: {str(e)}')

    def delete_log(self):
        """删除日志"""
        current_item = self.log_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, '警告', '请先选择要删除的记录')
            return

        reply = QMessageBox.question(
            self,
            '确认删除',
            '确定要删除这条执行记录吗？\n相关的所有文件都将被删除。',
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            data = current_item.data(Qt.UserRole)
            timestamp = data.get('timestamp', '')

            # 删除相关文件
            files_to_delete = [
                data.get('html_file', ''),
                data.get('xml_file', ''),
                data.get('debug_file', ''),
                os.path.join(self.logs_dir, f'flow_{timestamp}.robot')
            ]

            deleted_count = 0
            for file_path in files_to_delete:
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                    except Exception as e:
                        QMessageBox.warning(
                            self,
                            '警告',
                            f'删除文件失败: {file_path}\n错误: {str(e)}'
                        )

            # 刷新列表
            self.refresh_logs()

            if deleted_count > 0:
                QMessageBox.information(
                    self,
                    '成功',
                    f'已删除 {deleted_count} 个相关文件'
                )
