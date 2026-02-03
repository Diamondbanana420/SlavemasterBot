"""Scheduled Tasks for Automation"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Callable, List
import logging

logger = logging.getLogger(__name__)

class TaskScheduler:
    """Simple task scheduler for automation"""
    
    def __init__(self):
        self.tasks: Dict[str, Dict] = {}
        self.running = False
        self._task_handle = None
        
    def schedule_task(self, name: str, func: Callable, interval_hours: float, 
                      run_immediately: bool = False):
        """Schedule a recurring task"""
        self.tasks[name] = {
            'func': func,
            'interval_hours': interval_hours,
            'last_run': None if run_immediately else datetime.utcnow(),
            'next_run': datetime.utcnow() if run_immediately else datetime.utcnow() + timedelta(hours=interval_hours),
            'run_count': 0,
            'last_result': None,
            'enabled': True
        }
        logger.info(f"Scheduled task: {name} every {interval_hours} hours")
    
    def remove_task(self, name: str):
        """Remove a scheduled task"""
        if name in self.tasks:
            del self.tasks[name]
    
    def enable_task(self, name: str, enabled: bool = True):
        """Enable or disable a task"""
        if name in self.tasks:
            self.tasks[name]['enabled'] = enabled
    
    async def run_task(self, name: str) -> Dict[str, Any]:
        """Run a specific task immediately"""
        if name not in self.tasks:
            return {'error': f'Task {name} not found'}
        
        task = self.tasks[name]
        try:
            if asyncio.iscoroutinefunction(task['func']):
                result = await task['func']()
            else:
                result = task['func']()
            
            task['last_run'] = datetime.utcnow()
            task['next_run'] = datetime.utcnow() + timedelta(hours=task['interval_hours'])
            task['run_count'] += 1
            task['last_result'] = {'success': True, 'data': result}
            
            return {'task': name, 'status': 'completed', 'result': result}
        except Exception as e:
            task['last_result'] = {'success': False, 'error': str(e)}
            return {'task': name, 'status': 'error', 'error': str(e)}
    
    async def _run_loop(self):
        """Main scheduler loop"""
        while self.running:
            now = datetime.utcnow()
            
            for name, task in self.tasks.items():
                if task['enabled'] and task['next_run'] <= now:
                    logger.info(f"Running scheduled task: {name}")
                    await self.run_task(name)
            
            await asyncio.sleep(60)  # Check every minute
    
    def start(self):
        """Start the scheduler"""
        if not self.running:
            self.running = True
            self._task_handle = asyncio.create_task(self._run_loop())
            logger.info("Task scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self._task_handle:
            self._task_handle.cancel()
        logger.info("Task scheduler stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            'running': self.running,
            'tasks': {
                name: {
                    'interval_hours': t['interval_hours'],
                    'enabled': t['enabled'],
                    'last_run': t['last_run'].isoformat() if t['last_run'] else None,
                    'next_run': t['next_run'].isoformat() if t['next_run'] else None,
                    'run_count': t['run_count'],
                    'last_success': t['last_result']['success'] if t['last_result'] else None
                }
                for name, t in self.tasks.items()
            }
        }
