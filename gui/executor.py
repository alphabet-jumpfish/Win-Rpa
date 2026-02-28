"""
流程执行器界面
用于运行 RPA 自动化流程并显示执行状态
"""
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QGroupBox, QProgressBar, QMessageBox
)
from PyQt5.QtCore import pyqtSignal, QThread, Qt
from PyQt5.QtGui import QTextCursor, QColor

from service.flow import FlowParserService, FlowExecutorService


class ExecutorThread(QThread):
    """执行器线程"""

    status_update = pyqtSignal(str, str)  # (status_type, message)
    finished = pyqtSignal(dict)  # 执行结果

    def __init__(self, flow_config):
        super().__init__()
        self.flow_config = flow_config
        self.is_running = False

    def run(self):
        """执行流程"""
        self.is_running = True

        try:
            # 创建解析器和执行器
            parser = FlowParserService()
            parser.parse_from_dict(self.flow_config)

            executor = FlowExecutorService(parser)
            executor.set_status_callback(self.emit_status)

            # 执行流程
            result = executor.execute()

            # 发送完成信号
            self.finished.emit(result)

        except Exception as e:
            self.emit_status('error', f'执行异常: {str(e)}')
            self.finished.emit({
                'success': False,
                'error': str(e)
            })

        self.is_running = False

    def emit_status(self, status, message):
        """发送状态更新"""
        if self.is_running:
            self.status_update.emit(status, message)

    def stop(self):
        """停止执行"""
        self.is_running = False
        self.terminate()


class ExecutorWidget(QWidget):
    """流程执行器组件"""

    status_changed = pyqtSignal(str)  # 状态变化信号
    execution_finished = pyqtSignal(dict)  # 执行完成信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.executor_thread = None
        self.current_flow = None
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()

        # 流程信息显示
        info_group = QGroupBox('当前流程')
        info_layout = QVBoxLayout()

        self.flow_name_label = QLabel('未加载流程')
        self.flow_name_label.setStyleSheet('font-size: 14pt; font-weight: bold;')
        info_layout.addWidget(self.flow_name_label)

        self.flow_desc_label = QLabel('')
        self.flow_desc_label.setWordWrap(True)
        info_layout.addWidget(self.flow_desc_label)

        self.steps_count_label = QLabel('步骤数: 0')
        info_layout.addWidget(self.steps_count_label)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # 控制按钮
        btn_layout = QHBoxLayout()

        self.run_btn = QPushButton('运行流程')
        self.run_btn.setStyleSheet('''
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14pt;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        ''')
        self.run_btn.clicked.connect(self.start_execution)
        btn_layout.addWidget(self.run_btn)

        self.stop_btn = QPushButton('停止执行')
        self.stop_btn.setStyleSheet('''
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 14pt;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        ''')
        self.stop_btn.clicked.connect(self.stop_execution)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_btn)

        layout.addLayout(btn_layout)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 执行日志
        log_group = QGroupBox('执行日志')
        log_layout = QVBoxLayout()

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet('''
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: Consolas, Monaco, monospace;
                font-size: 10pt;
            }
        ''')
        log_layout.addWidget(self.log_text)

        # 清空日志按钮
        clear_btn = QPushButton('清空日志')
        clear_btn.clicked.connect(self.clear_log)
        log_layout.addWidget(clear_btn)

        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        self.setLayout(layout)

    def run_flow(self, flow_config):
        """运行流程"""
        self.current_flow = flow_config

        # 更新界面显示
        self.flow_name_label.setText(flow_config.get('flow_name', '未命名流程'))
        self.flow_desc_label.setText(flow_config.get('description', ''))
        self.steps_count_label.setText(f"步骤数: {len(flow_config.get('steps', []))}")

        # 清空日志
        self.clear_log()

        # 提示用户
        if not flow_config.get('steps'):
            QMessageBox.warning(self, '警告', '流程没有任何步骤，无法执行')
            return

        # 自动开始执行
        self.start_execution()

    def start_execution(self):
        """开始执行"""
        if not self.current_flow:
            QMessageBox.warning(self, '警告', '请先加载流程')
            return

        if self.executor_thread and self.executor_thread.isRunning():
            QMessageBox.warning(self, '警告', '流程正在执行中')
            return

        # 更新界面状态
        self.run_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)

        # 添加开始执行日志
        self.append_log('info', '=' * 60)
        self.append_log('info', f"开始执行流程: {self.current_flow.get('flow_name')}")
        self.append_log('info', '=' * 60)

        # 创建并启动执行线程
        self.executor_thread = ExecutorThread(self.current_flow)
        self.executor_thread.status_update.connect(self.on_status_update)
        self.executor_thread.finished.connect(self.on_execution_finished)
        self.executor_thread.start()

        # 发送状态变化信号
        self.status_changed.emit('执行中...')

    def stop_execution(self):
        """停止执行"""
        if self.executor_thread and self.executor_thread.isRunning():
            self.append_log('warning', '正在停止执行...')
            self.executor_thread.stop()
            self.executor_thread.wait()

            # 更新界面状态
            self.run_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.progress_bar.setVisible(False)

            self.append_log('warning', '执行已停止')
            self.status_changed.emit('已停止')

    def on_status_update(self, status, message):
        """处理状态更新"""
        self.append_log(status, message)
        self.status_changed.emit(message)

    def on_execution_finished(self, result):
        """执行完成回调"""
        # 更新界面状态
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)

        # 显示执行结果
        self.append_log('info', '=' * 60)
        if result.get('success'):
            self.append_log('success', '执行成功!')
            self.append_log('info', f"执行时间: {result.get('execution_time', 0)} 秒")

            if 'statistics' in result:
                stats = result['statistics']
                self.append_log('info', f"总用例数: {stats.get('total', 0)}")
                self.append_log('info', f"通过: {stats.get('passed', 0)}")
                self.append_log('info', f"失败: {stats.get('failed', 0)}")

            if 'log_file' in result:
                self.append_log('info', f"详细报告: {result['log_file']}")

            # 显示成功消息
            QMessageBox.information(
                self,
                '执行成功',
                f"流程执行成功!\n\n"
                f"执行时间: {result.get('execution_time', 0)} 秒\n"
                f"详细报告: {result.get('log_file', 'N/A')}"
            )
        else:
            error_msg = result.get('error', result.get('message', '未知错误'))
            self.append_log('error', f'执行失败: {error_msg}')

            # 显示错误消息
            QMessageBox.critical(
                self,
                '执行失败',
                f"流程执行失败!\n\n错误: {error_msg}"
            )

        self.append_log('info', '=' * 60)

        # 发送完成信号
        self.execution_finished.emit(result)

    def append_log(self, level, message):
        """添加日志"""
        # 颜色映射
        color_map = {
            'info': '#d4d4d4',      # 白色
            'success': '#4ec9b0',   # 青绿色
            'error': '#f48771',     # 红色
            'warning': '#ce9178',   # 橙色
        }

        color = color_map.get(level, '#d4d4d4')

        # 添加带颜色的日志
        self.log_text.moveCursor(QTextCursor.End)
        self.log_text.insertHtml(
            f'<span style="color: {color};">[{level.upper()}] {message}</span><br>'
        )
        self.log_text.moveCursor(QTextCursor.End)

    def clear_log(self):
        """清空日志"""
        self.log_text.clear()

    def stop_flow(self):
        """停止流程（外部调用）"""
        self.stop_execution()
