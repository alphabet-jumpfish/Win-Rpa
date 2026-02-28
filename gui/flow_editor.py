"""
流程编辑器界面
用于创建和编辑 RPA 自动化流程
"""
import os
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
    QTextEdit, QGroupBox, QFileDialog, QMessageBox, QDialog,
    QFormLayout, QDialogButtonBox
)
from PyQt5.QtCore import pyqtSignal, Qt


class StepEditorDialog(QDialog):
    """步骤编辑对话框"""

    def __init__(self, step_data=None, parent=None):
        super().__init__(parent)
        self.step_data = step_data or {}
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle('编辑步骤')
        self.setModal(True)
        self.resize(500, 400)

        layout = QVBoxLayout()

        # 操作类型选择
        form_layout = QFormLayout()

        self.action_combo = QComboBox()
        self.action_combo.addItems([
            'open_browser',
            'close_browser',
            'click',
            'input_text',
            'get_text',
            'get_element_text',
            'get_attribute',
            'wait',
            'wait_until_element_visible',
            'screenshot',
            'scroll_to_element',
            'select_from_list',
            'execute_javascript',
        ])
        self.action_combo.currentTextChanged.connect(self.on_action_changed)
        form_layout.addRow('操作类型:', self.action_combo)

        # 参数输入区域
        self.param_group = QGroupBox('参数')
        self.param_layout = QFormLayout()
        self.param_group.setLayout(self.param_layout)

        # 创建参数输入控件（先创建所有可能的控件）
        self.url_input = QLineEdit()
        self.locator_input = QLineEdit()
        self.text_input = QLineEdit()
        self.attribute_input = QLineEdit()
        self.seconds_input = QLineEdit()
        self.timeout_input = QLineEdit()
        self.timeout_input.setPlaceholderText('默认 10s')
        self.filename_input = QLineEdit()
        self.value_input = QLineEdit()
        self.script_input = QTextEdit()
        self.script_input.setMaximumHeight(100)

        layout.addLayout(form_layout)
        layout.addWidget(self.param_group)

        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

        # 如果有现有数据，填充表单
        if self.step_data:
            self.load_step_data()
        else:
            self.on_action_changed(self.action_combo.currentText())

    def on_action_changed(self, action):
        """操作类型变化时更新参数表单"""
        # 清空参数布局
        while self.param_layout.count():
            child = self.param_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)

        # 根据操作类型显示相应的参数输入框
        if action == 'open_browser':
            self.param_layout.addRow('网址(URL):', self.url_input)
        elif action in ['click', 'scroll_to_element']:
            self.param_layout.addRow('元素定位(locator):', self.locator_input)
        elif action == 'input_text':
            self.param_layout.addRow('元素定位(locator):', self.locator_input)
            self.param_layout.addRow('输入文本(text):', self.text_input)
        elif action in ['get_text', 'get_element_text']:
            self.param_layout.addRow('元素定位(locator):', self.locator_input)
        elif action == 'get_attribute':
            self.param_layout.addRow('元素定位(locator):', self.locator_input)
            self.param_layout.addRow('属性名(attribute):', self.attribute_input)
        elif action == 'wait':
            self.param_layout.addRow('等待秒数(seconds):', self.seconds_input)
        elif action == 'wait_until_element_visible':
            self.param_layout.addRow('元素定位(locator):', self.locator_input)
            self.param_layout.addRow('超时时间(timeout):', self.timeout_input)
        elif action == 'screenshot':
            self.param_layout.addRow('文件名(filename):', self.filename_input)
        elif action == 'select_from_list':
            self.param_layout.addRow('元素定位(locator):', self.locator_input)
            self.param_layout.addRow('选项值(value):', self.value_input)
        elif action == 'execute_javascript':
            self.param_layout.addRow('JS代码(script):', self.script_input)

    def load_step_data(self):
        """加载步骤数据到表单"""
        action = self.step_data.get('action', '')
        self.action_combo.setCurrentText(action)

        # 填充参数
        self.url_input.setText(self.step_data.get('url', ''))
        self.locator_input.setText(self.step_data.get('locator', ''))
        self.text_input.setText(self.step_data.get('text', ''))
        self.attribute_input.setText(self.step_data.get('attribute', ''))
        self.seconds_input.setText(str(self.step_data.get('seconds', '')))
        self.timeout_input.setText(self.step_data.get('timeout', ''))
        self.filename_input.setText(self.step_data.get('filename', ''))
        self.value_input.setText(self.step_data.get('value', ''))
        self.script_input.setText(self.step_data.get('script', ''))

    def get_step_data(self):
        """获取步骤数据"""
        action = self.action_combo.currentText()
        step = {'action': action}

        # 根据操作类型获取参数
        if action == 'open_browser':
            step['url'] = self.url_input.text()
        elif action in ['click', 'scroll_to_element', 'get_text', 'get_element_text']:
            step['locator'] = self.locator_input.text()
        elif action == 'input_text':
            step['locator'] = self.locator_input.text()
            step['text'] = self.text_input.text()
        elif action == 'get_attribute':
            step['locator'] = self.locator_input.text()
            step['attribute'] = self.attribute_input.text()
        elif action == 'wait':
            step['seconds'] = self.seconds_input.text()
        elif action == 'wait_until_element_visible':
            step['locator'] = self.locator_input.text()
            if self.timeout_input.text():
                step['timeout'] = self.timeout_input.text()
        elif action == 'screenshot':
            step['filename'] = self.filename_input.text()
        elif action == 'select_from_list':
            step['locator'] = self.locator_input.text()
            step['value'] = self.value_input.text()
        elif action == 'execute_javascript':
            step['script'] = self.script_input.toPlainText()

        return step


class FlowEditorWidget(QWidget):
    """流程编辑器组件"""

    flow_saved = pyqtSignal(str)  # 流程保存信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = None
        self.unsaved_changes = False
        self.flow_config = {
            'flow_name': '新建流程',
            'description': '',
            'browser': 'chrome',
            'steps': []
        }
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()

        # 流程基本信息
        info_group = QGroupBox('流程信息')
        info_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setText(self.flow_config['flow_name'])
        self.name_input.textChanged.connect(self.mark_unsaved)
        info_layout.addRow('流程名称:', self.name_input)

        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(60)
        self.desc_input.textChanged.connect(self.mark_unsaved)
        info_layout.addRow('流程描述:', self.desc_input)

        self.browser_combo = QComboBox()
        self.browser_combo.addItems(['chrome', 'firefox', 'edge'])
        self.browser_combo.setCurrentText(self.flow_config['browser'])
        self.browser_combo.currentTextChanged.connect(self.mark_unsaved)
        info_layout.addRow('浏览器:', self.browser_combo)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # 步骤列表
        steps_group = QGroupBox('流程步骤')
        steps_layout = QVBoxLayout()

        # 步骤表格
        self.steps_table = QTableWidget()
        self.steps_table.setColumnCount(3)
        self.steps_table.setHorizontalHeaderLabels(['序号', '操作', '参数'])
        self.steps_table.setColumnWidth(0, 60)
        self.steps_table.setColumnWidth(1, 200)
        self.steps_table.setColumnWidth(2, 600)
        steps_layout.addWidget(self.steps_table)

        # 步骤操作按钮
        btn_layout = QHBoxLayout()

        add_btn = QPushButton('添加步骤')
        add_btn.clicked.connect(self.add_step)
        btn_layout.addWidget(add_btn)

        edit_btn = QPushButton('编辑步骤')
        edit_btn.clicked.connect(self.edit_step)
        btn_layout.addWidget(edit_btn)

        delete_btn = QPushButton('删除步骤')
        delete_btn.clicked.connect(self.delete_step)
        btn_layout.addWidget(delete_btn)

        move_up_btn = QPushButton('上移')
        move_up_btn.clicked.connect(self.move_step_up)
        btn_layout.addWidget(move_up_btn)

        move_down_btn = QPushButton('下移')
        move_down_btn.clicked.connect(self.move_step_down)
        btn_layout.addWidget(move_down_btn)

        btn_layout.addStretch()

        steps_layout.addLayout(btn_layout)
        steps_group.setLayout(steps_layout)
        layout.addWidget(steps_group)

        self.setLayout(layout)

    def add_step(self):
        """添加步骤"""
        dialog = StepEditorDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            step_data = dialog.get_step_data()
            self.flow_config['steps'].append(step_data)
            self.refresh_steps_table()
            self.mark_unsaved()

    def edit_step(self):
        """编辑步骤"""
        current_row = self.steps_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, '警告', '请先选择要编辑的步骤')
            return

        step_data = self.flow_config['steps'][current_row]
        dialog = StepEditorDialog(step_data=step_data, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            updated_step = dialog.get_step_data()
            self.flow_config['steps'][current_row] = updated_step
            self.refresh_steps_table()
            self.mark_unsaved()

    def delete_step(self):
        """删除步骤"""
        current_row = self.steps_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, '警告', '请先选择要删除的步骤')
            return

        reply = QMessageBox.question(
            self, '确认删除',
            '确定要删除这个步骤吗？',
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            del self.flow_config['steps'][current_row]
            self.refresh_steps_table()
            self.mark_unsaved()

    def move_step_up(self):
        """上移步骤"""
        current_row = self.steps_table.currentRow()
        if current_row <= 0:
            return

        steps = self.flow_config['steps']
        steps[current_row], steps[current_row - 1] = steps[current_row - 1], steps[current_row]
        self.refresh_steps_table()
        self.steps_table.setCurrentCell(current_row - 1, 0)
        self.mark_unsaved()

    def move_step_down(self):
        """下移步骤"""
        current_row = self.steps_table.currentRow()
        if current_row < 0 or current_row >= len(self.flow_config['steps']) - 1:
            return

        steps = self.flow_config['steps']
        steps[current_row], steps[current_row + 1] = steps[current_row + 1], steps[current_row]
        self.refresh_steps_table()
        self.steps_table.setCurrentCell(current_row + 1, 0)
        self.mark_unsaved()

    def refresh_steps_table(self):
        """刷新步骤表格"""
        self.steps_table.setRowCount(len(self.flow_config['steps']))

        for idx, step in enumerate(self.flow_config['steps']):
            # 序号
            self.steps_table.setItem(idx, 0, QTableWidgetItem(str(idx + 1)))

            # 操作
            action = step.get('action', '')
            self.steps_table.setItem(idx, 1, QTableWidgetItem(action))

            # 参数（简化显示）
            params = {k: v for k, v in step.items() if k != 'action'}
            params_str = ', '.join([f'{k}={v}' for k, v in params.items()])
            self.steps_table.setItem(idx, 2, QTableWidgetItem(params_str))

    def new_flow(self):
        """新建流程"""
        if self.unsaved_changes:
            reply = QMessageBox.question(
                self, '保存确认',
                '当前流程未保存，是否保存？',
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if reply == QMessageBox.Yes:
                self.save_flow()
            elif reply == QMessageBox.Cancel:
                return

        self.flow_config = {
            'flow_name': '新建流程',
            'description': '',
            'browser': 'chrome',
            'steps': []
        }
        self.current_file = None
        self.name_input.setText(self.flow_config['flow_name'])
        self.desc_input.clear()
        self.browser_combo.setCurrentText('chrome')
        self.refresh_steps_table()
        self.unsaved_changes = False

    def open_flow(self):
        """打开流程"""
        flows_dir = os.path.join(os.path.dirname(__file__), '..', 'flows')
        os.makedirs(flows_dir, exist_ok=True)

        file_path, _ = QFileDialog.getOpenFileName(
            self, '打开流程', flows_dir,
            'JSON Files (*.json);;All Files (*)'
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.flow_config = json.load(f)

                self.current_file = file_path
                self.name_input.setText(self.flow_config.get('flow_name', ''))
                self.desc_input.setText(self.flow_config.get('description', ''))
                self.browser_combo.setCurrentText(self.flow_config.get('browser', 'chrome'))
                self.refresh_steps_table()
                self.unsaved_changes = False
                QMessageBox.information(self, '成功', f'已加载流程: {file_path}')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'加载流程失败: {str(e)}')

    def save_flow(self):
        """保存流程"""
        # 更新配置
        self.flow_config['flow_name'] = self.name_input.text()
        self.flow_config['description'] = self.desc_input.toPlainText()
        self.flow_config['browser'] = self.browser_combo.currentText()

        if not self.current_file:
            return self.save_flow_as()

        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                json.dump(self.flow_config, f, ensure_ascii=False, indent=2)

            self.unsaved_changes = False
            self.flow_saved.emit(self.current_file)
            return True
        except Exception as e:
            QMessageBox.critical(self, '错误', f'保存失败: {str(e)}')
            return False

    def save_flow_as(self):
        """另存为流程"""
        flows_dir = os.path.join(os.path.dirname(__file__), '..', 'flows')
        os.makedirs(flows_dir, exist_ok=True)

        file_path, _ = QFileDialog.getSaveFileName(
            self, '保存流程', flows_dir,
            'JSON Files (*.json)'
        )

        if file_path:
            self.current_file = file_path
            return self.save_flow()

        return False

    def get_flow_config(self):
        """获取当前流程配置"""
        self.flow_config['flow_name'] = self.name_input.text()
        self.flow_config['description'] = self.desc_input.toPlainText()
        self.flow_config['browser'] = self.browser_combo.currentText()
        return self.flow_config

    def mark_unsaved(self):
        """标记为未保存"""
        self.unsaved_changes = True

    def has_unsaved_changes(self):
        """是否有未保存的修改"""
        return self.unsaved_changes
