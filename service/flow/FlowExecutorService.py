"""
流程执行服务
负责将流程配置转换为 Robot Framework 测试用例并执行
"""
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from robot import run
from robot.api import ExecutionResult

from service.flow.FlowParserService import FlowParserService


class FlowExecutorService:
    """流程执行服务"""

    def __init__(self, parser_service: Optional[FlowParserService] = None):
        """
        初始化执行服务

        Args:
            parser_service: 流程解析服务实例（也可以传入旧版的 flow_parser，向后兼容）
        """
        self.parser_service = parser_service or FlowParserService()
        # 向后兼容：添加 flow_parser 属性别名
        self.flow_parser = self.parser_service

        self.robot_file_path: Optional[str] = None
        self.output_dir: str = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
        self.status_callback: Optional[Callable] = None

        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)

    def set_status_callback(self, callback: Callable[[str, str], None]) -> None:
        """
        设置状态回调函数

        Args:
            callback: 回调函数，接收 (status, message) 参数
        """
        self.status_callback = callback

    def _emit_status(self, status: str, message: str) -> None:
        """
        发送状态更新

        Args:
            status: 状态类型 (info, success, error, warning)
            message: 状态消息
        """
        if self.status_callback:
            self.status_callback(status, message)

    def generate_robot_file(self, flow_data: Dict[str, Any]) -> str:
        """
        将流程配置转换为 Robot Framework 测试用例文件

        Args:
            flow_data: 流程配置数据

        Returns:
            生成的 .robot 文件路径
        """
        flow_name = self.parser_service.get_flow_name(flow_data)
        browser = self.parser_service.get_browser(flow_data)
        steps = self.parser_service.get_steps(flow_data)

        # 生成时间戳文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"flow_{timestamp}.robot"
        self.robot_file_path = os.path.join(self.output_dir, filename)

        # 生成 Robot Framework 测试用例内容
        robot_content = self._build_robot_content(flow_name, browser, steps)

        # 写入文件
        with open(self.robot_file_path, 'w', encoding='utf-8') as f:
            f.write(robot_content)

        self._emit_status('info', f'生成测试用例文件: {self.robot_file_path}')
        return self.robot_file_path

    def _build_robot_content(self, flow_name: str, browser: str, steps: List[Dict[str, Any]]) -> str:
        """
        构建 Robot Framework 测试用例内容

        Args:
            flow_name: 流程名称
            browser: 浏览器类型
            steps: 步骤列表

        Returns:
            Robot Framework 测试用例内容
        """
        # 资源文件路径
        resources_path = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'keywords.robot')
        resources_path = os.path.abspath(resources_path)
        # 在 Windows 上，将反斜杠转换为正斜杠，Robot Framework 更兼容
        resources_path = resources_path.replace('\\', '/')

        lines = [
            "*** Settings ***",
            f"Documentation     {flow_name}",
            "Library           SeleniumLibrary",
            f"Resource          {resources_path}",
            "Suite Teardown    Close All Browsers",
            "",
            "*** Variables ***",
            f"${{BROWSER}}      {browser}",
            "",
            "*** Test Cases ***",
            f"{flow_name}",
            "    [Documentation]    自动化执行流程",
        ]

        # 转换每个步骤为 Robot Framework 关键字
        for idx, step in enumerate(steps, 1):
            keyword = self._step_to_keyword(step, idx)
            if keyword:
                lines.append(f"    {keyword}")

        return "\n".join(lines)

    def _step_to_keyword(self, step: Dict[str, Any], step_num: int) -> str:
        """
        将单个步骤转换为 Robot Framework 关键字

        Args:
            step: 步骤配置
            step_num: 步骤编号

        Returns:
            Robot Framework 关键字语句
        """
        action = step['action']

        # 映射配置操作到 Robot Framework 关键字
        action_mapping = {
            'open_browser': lambda s: f"打开智能体网站    {s['url']}    ${{BROWSER}}",
            'close_browser': lambda s: "Close Browser",
            'click': lambda s: f"安全点击元素    {s['locator']}",
            'input_text': lambda s: f"智能输入文本    {s['locator']}    {s['text']}",
            'get_text': lambda s: f"${{result_{step_num}}}=    提取元素文本    {s['locator']}",
            'get_element_text': lambda s: f"${{result_{step_num}}}=    提取元素文本    {s['locator']}",
            'get_attribute': lambda s: f"${{result_{step_num}}}=    提取元素属性值    {s['locator']}    {s['attribute']}",
            'wait': lambda s: f"Sleep    {s['seconds']}s",
            'wait_until_element_visible': lambda s: f"Wait Until Element Is Visible    {s['locator']}    {s.get('timeout', '10s')}",
            'screenshot': lambda s: f"截图保存    {s['filename']}",
            'scroll_to_element': lambda s: f"滚动到元素位置    {s['locator']}",
            'select_from_list': lambda s: f"从下拉框选择    {s['locator']}    {s['value']}",
            'execute_javascript': lambda s: f"执行JavaScript并获取结果    {s['script']}",
            'search': lambda s: f"执行搜索    {s['search_box_locator']}    {s['search_text']}    {s['search_button_locator']}",
        }

        if action in action_mapping:
            try:
                return action_mapping[action](step)
            except KeyError as e:
                self._emit_status('warning', f"步骤 {step_num} 缺少必需参数: {e}")
                return f"Log    步骤 {step_num} 配置错误: 缺少参数 {e}"
        else:
            self._emit_status('warning', f"步骤 {step_num} 的操作 '{action}' 未实现")
            return f"Log    未实现的操作: {action}"

    def execute(self, flow_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        执行流程

        Args:
            flow_data: 流程配置数据（可选）。如果不提供，将使用 parser_service 中已加载的数据

        Returns:
            执行结果字典，包含状态、日志等信息
        """
        # 如果没有提供 flow_data，从 parser_service 获取
        if flow_data is None:
            flow_data = self.parser_service.flow_data
            if flow_data is None:
                raise ValueError("没有可执行的流程配置。请先加载流程或提供 flow_data 参数。")

        # 验证流程配置
        self.parser_service.validate_flow(flow_data)

        # 生成 Robot 文件
        self.generate_robot_file(flow_data)

        self._emit_status('info', '开始执行自动化流程...')

        # 生成输出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"output_{timestamp}"

        # 执行参数
        options = {
            'outputdir': self.output_dir,
            'output': f'{output_name}.xml',
            'log': f'{output_name}.html',
            'report': f'{output_name}.html',
            'debugfile': f'{output_name}_debug.txt',
        }

        try:
            # 执行测试
            start_time = time.time()
            return_code = run(self.robot_file_path, **options)
            execution_time = time.time() - start_time

            # 解析执行结果
            result_file = os.path.join(self.output_dir, f'{output_name}.xml')
            result = ExecutionResult(result_file)

            # 安全获取统计信息（兼容不同版本的 Robot Framework）
            try:
                # 尝试使用新版本 API
                stats = result.suite.statistics.total
                if hasattr(stats, 'total'):
                    # RF 旧版本
                    total = stats.total
                    passed = stats.passed
                    failed = stats.failed
                else:
                    # RF 新版本，total 本身就是数字
                    total = stats if isinstance(stats, int) else 0
                    passed = result.suite.statistics.passed if hasattr(result.suite.statistics, 'passed') else 0
                    failed = result.suite.statistics.failed if hasattr(result.suite.statistics, 'failed') else 0
            except Exception:
                # 如果获取失败，使用默认值
                total = 1
                passed = 1 if return_code == 0 else 0
                failed = 0 if return_code == 0 else 1

            # 构建结果字典
            execution_result = {
                'success': return_code == 0,
                'return_code': return_code,
                'execution_time': round(execution_time, 2),
                'test_name': result.suite.name,
                'status': result.suite.status,
                'message': result.suite.message,
                'statistics': {
                    'total': total,
                    'passed': passed,
                    'failed': failed,
                },
                'log_file': os.path.join(self.output_dir, f'{output_name}.html'),
                'output_file': result_file,
            }

            if return_code == 0:
                self._emit_status('success', f'执行成功! 耗时: {execution_time:.2f}秒')
            else:
                self._emit_status('error', f'执行失败! 返回码: {return_code}')

            return execution_result

        except Exception as e:
            self._emit_status('error', f'执行出错: {str(e)}')
            return {
                'success': False,
                'error': str(e),
                'execution_time': 0,
            }

    def execute_from_file(self, config_file: str) -> Dict[str, Any]:
        """
        从配置文件加载并执行流程

        Args:
            config_file: 配置文件路径

        Returns:
            执行结果字典
        """
        self._emit_status('info', f'加载配置文件: {config_file}')
        flow_data = self.parser_service.parse_from_file(config_file)
        return self.execute(flow_data)


# 兼容性：保持原有的 RFRunner 类名
RFRunner = FlowExecutorService
