"""
流程解析服务
负责流程配置文件的解析、验证和转换
"""
import json
import yaml
import os
from typing import Dict, List, Any, Optional


class FlowParserService:
    """流程解析服务"""

    # 支持的操作类型
    SUPPORTED_ACTIONS = [
        'open_browser',              # 打开浏览器
        'close_browser',             # 关闭浏览器
        'click',                     # 点击元素
        'input_text',                # 输入文本
        'get_text',                  # 获取文本内容
        'get_element_text',          # 获取元素文本
        'get_attribute',             # 获取元素属性
        'wait',                      # 等待
        'wait_until_element_visible', # 等待元素可见
        'screenshot',                # 截图
        'scroll_to_element',         # 滚动到元素
        'select_from_list',          # 下拉选择
        'execute_javascript',        # 执行JS
        'search',                    # 搜索操作（输入关键词并点击搜索）
    ]

    def __init__(self):
        """初始化服务"""
        self.flow_data: Optional[Dict[str, Any]] = None

    def parse_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        从文件解析流程配置

        Args:
            file_path: 配置文件路径

        Returns:
            解析后的流程配置字典

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 文件格式不支持或解析失败
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"配置文件不存在: {file_path}")

        file_ext = os.path.splitext(file_path)[1].lower()

        with open(file_path, 'r', encoding='utf-8') as f:
            if file_ext == '.json':
                self.flow_data = json.load(f)
            elif file_ext in ['.yaml', '.yml']:
                self.flow_data = yaml.safe_load(f)
            else:
                raise ValueError(f"不支持的文件格式: {file_ext}，仅支持 .json, .yaml, .yml")

        # 验证配置
        self.validate_flow(self.flow_data)
        return self.flow_data

    def parse_from_dict(self, flow_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        从字典解析流程配置

        Args:
            flow_dict: 流程配置字典

        Returns:
            解析后的流程配置字典
        """
        self.flow_data = flow_dict
        self.validate_flow(self.flow_data)
        return self.flow_data

    def validate_flow(self, flow_data: Dict[str, Any]) -> None:
        """
        验证流程配置的有效性

        Args:
            flow_data: 流程配置字典

        Raises:
            ValueError: 配置格式不正确
        """
        if not flow_data:
            raise ValueError("流程配置为空")

        # 检查必需字段
        if 'flow_name' not in flow_data:
            raise ValueError("缺少必需字段: flow_name")

        if 'steps' not in flow_data:
            raise ValueError("缺少必需字段: steps")

        if not isinstance(flow_data['steps'], list):
            raise ValueError("steps 必须是列表类型")

        # 验证每个步骤
        for idx, step in enumerate(flow_data['steps']):
            self._validate_step(step, idx)

    def _validate_step(self, step: Dict[str, Any], step_index: int) -> None:
        """
        验证单个步骤的有效性

        Args:
            step: 步骤配置
            step_index: 步骤索引

        Raises:
            ValueError: 步骤配置不正确
        """
        if 'action' not in step:
            raise ValueError(f"步骤 {step_index} 缺少 action 字段")

        action = step['action']
        if action not in self.SUPPORTED_ACTIONS:
            raise ValueError(
                f"步骤 {step_index} 的 action '{action}' 不支持。"
                f"支持的操作: {', '.join(self.SUPPORTED_ACTIONS)}"
            )

        # 验证特定操作的必需参数
        self._validate_action_params(action, step, step_index)

    def _validate_action_params(self, action: str, step: Dict[str, Any], step_index: int) -> None:
        """
        验证操作的必需参数

        Args:
            action: 操作类型
            step: 步骤配置
            step_index: 步骤索引

        Raises:
            ValueError: 缺少必需参数
        """
        required_params = {
            'open_browser': ['url'],
            'click': ['locator'],
            'input_text': ['locator', 'text'],
            'get_text': ['locator'],
            'get_element_text': ['locator'],
            'get_attribute': ['locator', 'attribute'],
            'wait': ['seconds'],
            'wait_until_element_visible': ['locator'],
            'screenshot': ['filename'],
            'scroll_to_element': ['locator'],
            'select_from_list': ['locator', 'value'],
            'search': ['search_box_locator', 'search_text', 'search_button_locator'],
        }

        if action in required_params:
            for param in required_params[action]:
                if param not in step:
                    raise ValueError(
                        f"步骤 {step_index} 的 action '{action}' 缺少必需参数: {param}"
                    )

    def get_flow_name(self, flow_data: Optional[Dict[str, Any]] = None) -> str:
        """获取流程名称"""
        data = flow_data or self.flow_data
        return data.get('flow_name', 'Unnamed Flow') if data else 'Unnamed Flow'

    def get_browser(self, flow_data: Optional[Dict[str, Any]] = None) -> str:
        """获取浏览器类型，默认为 chrome"""
        data = flow_data or self.flow_data
        return data.get('browser', 'chrome') if data else 'chrome'

    def get_steps(self, flow_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """获取流程步骤列表"""
        data = flow_data or self.flow_data
        return data.get('steps', []) if data else []

    def get_description(self, flow_data: Optional[Dict[str, Any]] = None) -> str:
        """获取流程描述"""
        data = flow_data or self.flow_data
        return data.get('description', '') if data else ''

    def save_to_file(self, file_path: str, flow_data: Optional[Dict[str, Any]] = None) -> None:
        """
        保存流程配置到文件

        Args:
            file_path: 保存路径
            flow_data: 流程配置数据，如果为None则使用当前数据
        """
        data = flow_data or self.flow_data
        if not data:
            raise ValueError("没有可保存的流程配置")

        file_ext = os.path.splitext(file_path)[1].lower()

        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            if file_ext == '.json':
                json.dump(data, f, ensure_ascii=False, indent=2)
            elif file_ext in ['.yaml', '.yml']:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
            else:
                raise ValueError(f"不支持的文件格式: {file_ext}")

    @staticmethod
    def create_empty_flow(flow_name: str = "新建流程") -> Dict[str, Any]:
        """
        创建一个空流程配置

        Args:
            flow_name: 流程名称

        Returns:
            空流程配置字典
        """
        return {
            'flow_name': flow_name,
            'description': '',
            'browser': 'chrome',
            'steps': []
        }

    # ==================== 向后兼容性方法 ====================
    # 以下方法是为了保持与旧版本 FlowParser 的兼容性

    def load_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        从文件加载流程配置（兼容旧版本）

        Args:
            file_path: 配置文件路径

        Returns:
            解析后的流程配置字典
        """
        return self.parse_from_file(file_path)

    def load_from_dict(self, flow_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        从字典加载流程配置（兼容旧版本）

        Args:
            flow_dict: 流程配置字典

        Returns:
            解析后的流程配置字典
        """
        return self.parse_from_dict(flow_dict)


# 兼容性：保持原有的 FlowParser 类名
FlowParser = FlowParserService
