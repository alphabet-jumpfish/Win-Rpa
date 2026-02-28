"""
流程调度服务
使用 APScheduler 实现流程的定时执行
"""
import os
import json
from datetime import datetime
from typing import Callable, Optional, List, Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger

from service.flow.FlowParserService import FlowParserService
from service.flow.FlowExecutorService import FlowExecutorService


class FlowSchedulerService:
    """流程调度服务"""

    def __init__(self):
        """初始化调度器"""
        self.scheduler = BackgroundScheduler()
        self.tasks_file = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'scheduled_tasks.json')
        self.tasks: List[Dict[str, Any]] = []
        self.load_tasks()

    def start(self):
        """启动调度器"""
        if not self.scheduler.running:
            self.scheduler.start()

    def stop(self):
        """停止调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown()

    def load_tasks(self):
        """从文件加载任务"""
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
            except Exception as e:
                print(f"加载任务失败: {e}")
                self.tasks = []
        else:
            self.tasks = []

    def save_tasks(self):
        """保存任务到文件"""
        os.makedirs(os.path.dirname(self.tasks_file), exist_ok=True)
        try:
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存任务失败: {e}")

    def add_task(
        self,
        task_id: str,
        flow_config_path: str,
        trigger_type: str,
        trigger_params: Dict[str, Any],
        enabled: bool = True,
        callback: Optional[Callable] = None
    ) -> bool:
        """
        添加定时任务

        Args:
            task_id: 任务ID
            flow_config_path: 流程配置文件路径
            trigger_type: 触发器类型 (cron, interval, date)
            trigger_params: 触发器参数
            enabled: 是否启用
            callback: 执行回调函数

        Returns:
            是否添加成功
        """
        # 检查任务是否已存在
        if any(task['task_id'] == task_id for task in self.tasks):
            return False

        # 创建任务记录
        task_info = {
            'task_id': task_id,
            'flow_config_path': flow_config_path,
            'trigger_type': trigger_type,
            'trigger_params': trigger_params,
            'enabled': enabled,
            'created_at': datetime.now().isoformat(),
            'last_run': None,
            'next_run': None,
        }

        self.tasks.append(task_info)
        self.save_tasks()

        # 如果启用，添加到调度器
        if enabled:
            self._schedule_task(task_id, flow_config_path, trigger_type, trigger_params, callback)

        return True

    def remove_task(self, task_id: str) -> bool:
        """
        移除任务

        Args:
            task_id: 任务ID

        Returns:
            是否移除成功
        """
        # 从调度器中移除
        try:
            self.scheduler.remove_job(task_id)
        except:
            pass

        # 从任务列表中移除
        self.tasks = [task for task in self.tasks if task['task_id'] != task_id]
        self.save_tasks()
        return True

    def update_task(
        self,
        task_id: str,
        flow_config_path: Optional[str] = None,
        trigger_type: Optional[str] = None,
        trigger_params: Optional[Dict[str, Any]] = None,
        enabled: Optional[bool] = None,
        callback: Optional[Callable] = None
    ) -> bool:
        """
        更新任务

        Args:
            task_id: 任务ID
            flow_config_path: 流程配置文件路径
            trigger_type: 触发器类型
            trigger_params: 触发器参数
            enabled: 是否启用
            callback: 执行回调函数

        Returns:
            是否更新成功
        """
        # 查找任务
        task = next((t for t in self.tasks if t['task_id'] == task_id), None)
        if not task:
            return False

        # 更新任务信息
        if flow_config_path is not None:
            task['flow_config_path'] = flow_config_path
        if trigger_type is not None:
            task['trigger_type'] = trigger_type
        if trigger_params is not None:
            task['trigger_params'] = trigger_params
        if enabled is not None:
            task['enabled'] = enabled

        self.save_tasks()

        # 重新调度
        try:
            self.scheduler.remove_job(task_id)
        except:
            pass

        if task['enabled']:
            self._schedule_task(
                task_id,
                task['flow_config_path'],
                task['trigger_type'],
                task['trigger_params'],
                callback
            )

        return True

    def _schedule_task(
        self,
        task_id: str,
        flow_config_path: str,
        trigger_type: str,
        trigger_params: Dict[str, Any],
        callback: Optional[Callable] = None
    ):
        """
        将任务添加到调度器

        Args:
            task_id: 任务ID
            flow_config_path: 流程配置文件路径
            trigger_type: 触发器类型
            trigger_params: 触发器参数
            callback: 执行回调函数
        """
        # 创建执行函数
        def job_func():
            self._execute_flow(task_id, flow_config_path, callback)

        # 创建触发器
        trigger = None
        if trigger_type == 'cron':
            trigger = CronTrigger(**trigger_params)
        elif trigger_type == 'interval':
            trigger = IntervalTrigger(**trigger_params)
        elif trigger_type == 'date':
            trigger = DateTrigger(**trigger_params)

        if trigger:
            self.scheduler.add_job(
                job_func,
                trigger=trigger,
                id=task_id,
                replace_existing=True
            )

    def _execute_flow(self, task_id: str, flow_config_path: str, callback: Optional[Callable] = None):
        """
        执行流程

        Args:
            task_id: 任务ID
            flow_config_path: 流程配置文件路径
            callback: 执行回调函数
        """
        try:
            # 更新最后执行时间
            task = next((t for t in self.tasks if t['task_id'] == task_id), None)
            if task:
                task['last_run'] = datetime.now().isoformat()
                self.save_tasks()

            # 执行流程
            parser_service = FlowParserService()
            flow_data = parser_service.parse_from_file(flow_config_path)

            executor_service = FlowExecutorService(parser_service)
            result = executor_service.execute(flow_data)

            # 调用回调
            if callback:
                callback(task_id, result)

        except Exception as e:
            print(f"任务 {task_id} 执行失败: {e}")
            if callback:
                callback(task_id, {'success': False, 'error': str(e)})

    def get_tasks(self) -> List[Dict[str, Any]]:
        """获取所有任务"""
        # 更新下次运行时间
        for task in self.tasks:
            if task['enabled']:
                try:
                    job = self.scheduler.get_job(task['task_id'])
                    if job and job.next_run_time:
                        task['next_run'] = job.next_run_time.isoformat()
                except:
                    task['next_run'] = None

        return self.tasks

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取指定任务"""
        return next((t for t in self.tasks if t['task_id'] == task_id), None)

    def enable_task(self, task_id: str, callback: Optional[Callable] = None) -> bool:
        """启用任务"""
        return self.update_task(task_id, enabled=True, callback=callback)

    def disable_task(self, task_id: str) -> bool:
        """禁用任务"""
        try:
            self.scheduler.remove_job(task_id)
        except:
            pass
        return self.update_task(task_id, enabled=False)


# 兼容性：保持原有的 TaskScheduler 类名
TaskScheduler = FlowSchedulerService
