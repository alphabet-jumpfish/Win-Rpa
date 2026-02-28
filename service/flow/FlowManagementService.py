"""
流程管理服务
负责流程的增删改查（CRUD）操作
"""
import os
import json
import shutil
from typing import Dict, List, Any, Optional
from datetime import datetime

from service.flow.FlowParserService import FlowParserService


class FlowManagementService:
    """流程管理服务"""

    def __init__(self, flows_dir: Optional[str] = None):
        """
        初始化流程管理服务

        Args:
            flows_dir: 流程配置文件目录，默认为项目的 flows 目录
        """
        if flows_dir is None:
            flows_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'flows')

        self.flows_dir = os.path.abspath(flows_dir)
        self.parser_service = FlowParserService()

        # 确保流程目录存在
        os.makedirs(self.flows_dir, exist_ok=True)

    def create_flow(self, flow_name: str, description: str = '', browser: str = 'chrome') -> Dict[str, Any]:
        """
        创建新流程

        Args:
            flow_name: 流程名称
            description: 流程描述
            browser: 浏览器类型

        Returns:
            新创建的流程配置
        """
        flow_data = {
            'flow_name': flow_name,
            'description': description,
            'browser': browser,
            'steps': [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
        }

        return flow_data

    def save_flow(self, flow_data: Dict[str, Any], file_name: Optional[str] = None) -> str:
        """
        保存流程到文件

        Args:
            flow_data: 流程配置数据
            file_name: 文件名（不含路径），如果为 None 则自动生成

        Returns:
            保存的文件路径
        """
        # 验证流程配置
        self.parser_service.validate_flow(flow_data)

        # 更新修改时间
        flow_data['updated_at'] = datetime.now().isoformat()

        # 如果没有创建时间，添加创建时间
        if 'created_at' not in flow_data:
            flow_data['created_at'] = datetime.now().isoformat()

        # 生成文件名
        if file_name is None:
            # 使用流程名称作为文件名（移除特殊字符）
            safe_name = "".join(c for c in flow_data['flow_name'] if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_')
            file_name = f"{safe_name}.json"

        # 确保文件扩展名
        if not file_name.endswith('.json'):
            file_name += '.json'

        file_path = os.path.join(self.flows_dir, file_name)

        # 保存文件
        self.parser_service.save_to_file(file_path, flow_data)

        return file_path

    def load_flow(self, file_name: str) -> Dict[str, Any]:
        """
        加载流程配置

        Args:
            file_name: 文件名（可以是完整路径或仅文件名）

        Returns:
            流程配置数据

        Raises:
            FileNotFoundError: 文件不存在
        """
        # 如果是完整路径，直接使用
        if os.path.isabs(file_name):
            file_path = file_name
        else:
            # 否则在 flows 目录中查找
            file_path = os.path.join(self.flows_dir, file_name)

        return self.parser_service.parse_from_file(file_path)

    def delete_flow(self, file_name: str) -> bool:
        """
        删除流程配置文件

        Args:
            file_name: 文件名

        Returns:
            是否删除成功
        """
        file_path = os.path.join(self.flows_dir, file_name)

        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except Exception as e:
                print(f"删除流程失败: {e}")
                return False

        return False

    def list_flows(self) -> List[Dict[str, Any]]:
        """
        列出所有流程配置

        Returns:
            流程配置列表，每个元素包含文件名和流程基本信息
        """
        flows = []

        if not os.path.exists(self.flows_dir):
            return flows

        for file_name in os.listdir(self.flows_dir):
            if file_name.endswith('.json'):
                file_path = os.path.join(self.flows_dir, file_name)
                try:
                    flow_data = self.parser_service.parse_from_file(file_path)
                    flows.append({
                        'file_name': file_name,
                        'file_path': file_path,
                        'flow_name': flow_data.get('flow_name', 'Unknown'),
                        'description': flow_data.get('description', ''),
                        'browser': flow_data.get('browser', 'chrome'),
                        'steps_count': len(flow_data.get('steps', [])),
                        'created_at': flow_data.get('created_at', ''),
                        'updated_at': flow_data.get('updated_at', ''),
                        'modified_time': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                    })
                except Exception as e:
                    print(f"读取流程文件 {file_name} 失败: {e}")

        # 按修改时间降序排序
        flows.sort(key=lambda x: x.get('modified_time', ''), reverse=True)

        return flows

    def update_flow(self, file_name: str, flow_data: Dict[str, Any]) -> str:
        """
        更新流程配置

        Args:
            file_name: 文件名
            flow_data: 新的流程配置数据

        Returns:
            文件路径
        """
        return self.save_flow(flow_data, file_name)

    def duplicate_flow(self, file_name: str, new_name: Optional[str] = None) -> str:
        """
        复制流程

        Args:
            file_name: 源文件名
            new_name: 新流程名称，如果为 None 则自动生成

        Returns:
            新文件路径
        """
        # 加载原流程
        flow_data = self.load_flow(file_name)

        # 修改流程名称
        if new_name:
            flow_data['flow_name'] = new_name
        else:
            flow_data['flow_name'] = f"{flow_data['flow_name']} - 副本"

        # 移除旧的时间戳
        flow_data.pop('created_at', None)
        flow_data.pop('updated_at', None)

        # 保存为新文件
        return self.save_flow(flow_data)

    def export_flow(self, file_name: str, export_path: str) -> bool:
        """
        导出流程到指定位置

        Args:
            file_name: 流程文件名
            export_path: 导出路径

        Returns:
            是否导出成功
        """
        source_path = os.path.join(self.flows_dir, file_name)

        if not os.path.exists(source_path):
            return False

        try:
            shutil.copy2(source_path, export_path)
            return True
        except Exception as e:
            print(f"导出流程失败: {e}")
            return False

    def import_flow(self, import_path: str, new_name: Optional[str] = None) -> str:
        """
        导入流程

        Args:
            import_path: 导入文件路径
            new_name: 新流程名称，如果为 None 则使用原名称

        Returns:
            导入后的文件路径
        """
        # 加载流程
        flow_data = self.parser_service.parse_from_file(import_path)

        # 如果指定了新名称，更新流程名称
        if new_name:
            flow_data['flow_name'] = new_name

        # 保存到 flows 目录
        return self.save_flow(flow_data)

    def get_flow_info(self, file_name: str) -> Dict[str, Any]:
        """
        获取流程的详细信息

        Args:
            file_name: 文件名

        Returns:
            流程详细信息
        """
        file_path = os.path.join(self.flows_dir, file_name)
        flow_data = self.parser_service.parse_from_file(file_path)

        return {
            'file_name': file_name,
            'file_path': file_path,
            'flow_name': flow_data.get('flow_name', 'Unknown'),
            'description': flow_data.get('description', ''),
            'browser': flow_data.get('browser', 'chrome'),
            'steps': flow_data.get('steps', []),
            'steps_count': len(flow_data.get('steps', [])),
            'created_at': flow_data.get('created_at', ''),
            'updated_at': flow_data.get('updated_at', ''),
            'file_size': os.path.getsize(file_path),
            'modified_time': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
        }
