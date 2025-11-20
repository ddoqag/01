#!/usr/bin/env python3
"""
Flow系统集成处理器
连接现有的Flow系统和83个专业Agent
"""

import json
import sys
import os
import subprocess
import re
from pathlib import Path

class FlowConnector:
    def __init__(self):
        self.flow_bin_path = "/mnt/d/flow/bin/flow"
        self.flow_project_path = "/mnt/d/flow"
        self.available_agents = self._get_available_agents()

    def _get_available_agents(self):
        """获取可用的Agent列表"""
        # 基于已知的83个专业Agent
        return {
            'development': [
                'python-pro', 'java-pro', 'web-developer', 'mobile-developer',
                'csharp-pro', 'cpp-pro', 'go-pro', 'rust-pro'
            ],
            'analysis': [
                'data-scientist', 'quant-analyst', 'database-analyst',
                'data-engineer', 'business-analyst', 'market-researcher'
            ],
            'architecture': [
                'cloud-architect', 'database-architect', 'backend-architect',
                'frontend-architect', 'system-architect', 'security-architect'
            ],
            'security': [
                'security-auditor', 'backend-security-coder', 'frontend-security-coder',
                'penetration-tester', 'security-consultant', 'compliance-auditor'
            ],
            'devops': [
                'devops-engineer', 'performance-engineer', 'monitoring-specialist',
                'site-reliability-engineer', 'infrastructure-engineer', 'cloud-engineer'
            ],
            'testing': [
                'test-automator', 'quality-assurance', 'integration-tester',
                'performance-tester', 'usability-tester', 'security-tester'
            ],
            'business': [
                'business-analyst', 'content-marketer', 'hr-pro',
                'project-manager', 'product-manager', 'sales-automator'
            ],
            'design': [
                'ui-ux-designer', 'graphic-designer', 'product-designer',
                'interaction-designer', 'visual-designer', 'motion-designer'
            ],
            'finance': [
                'quant-analyst', 'financial-analyst', 'risk-manager',
                'investment-advisor', 'portfolio-manager', 'trading-developer'
            ],
            'research': [
                'research-scientist', 'data-analyst', 'market-researcher',
                'academic-researcher', 'technical-writer', 'knowledge-engineer'
            ]
        }

    def is_flow_available(self):
        """检查Flow系统是否可用"""
        try:
            result = subprocess.run(
                [self.flow_bin_path, "status"],
                cwd=self.flow_project_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False

    def find_agent_category(self, agent_name):
        """查找Agent所属类别"""
        for category, agents in self.available_agents.items():
            if agent_name in agents:
                return category
        return None

    def suggest_agents(self, task_description):
        """根据任务描述推荐合适的Agent"""
        task_lower = task_description.lower()
        suggestions = []

        # 基于关键词匹配推荐Agent
        if any(keyword in task_lower for keyword in ['python', 'code', '编程', '开发']):
            suggestions.extend(['python-pro', 'web-developer'])

        if any(keyword in task_lower for keyword in ['数据', '分析', '统计', '模型']):
            suggestions.extend(['data-scientist', 'quant-analyst'])

        if any(keyword in task_lower for keyword in ['安全', '审计', '漏洞', '防护']):
            suggestions.extend(['security-auditor', 'penetration-tester'])

        if any(keyword in task_lower for keyword in ['架构', '设计', '系统']):
            suggestions.extend(['cloud-architect', 'backend-architect'])

        if any(keyword in task_lower for keyword in ['测试', '质量', '验证']):
            suggestions.extend(['test-automator', 'quality-assurance'])

        return list(set(suggestions))  # 去重

    def call_agent(self, agent_name, task):
        """调用指定的Agent执行任务"""
        if not self.is_flow_available():
            return {
                "success": False,
                "error": "Flow系统不可用，请检查系统状态"
            }

        # 检查Agent是否存在
        category = self.find_agent_category(agent_name)
        if not category:
            return {
                "success": False,
                "error": f"未找到Agent: {agent_name}",
                "suggestions": self.suggest_agents(task)
            }

        try:
            # 构建Flow命令
            flow_command = f'agent {agent_name} "{task}"'

            result = subprocess.run(
                [self.flow_bin_path, "agent", agent_name, task],
                cwd=self.flow_project_path,
                capture_output=True,
                text=True,
                timeout=120  # 2分钟超时
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "agent": agent_name,
                    "category": category,
                    "task": task,
                    "result": result.stdout,
                    "execution_time": "completed"
                }
            else:
                return {
                    "success": False,
                    "agent": agent_name,
                    "category": category,
                    "task": task,
                    "error": result.stderr or "执行失败",
                    "execution_time": "failed"
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "agent": agent_name,
                "task": task,
                "error": "Agent执行超时",
                "execution_time": "timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "agent": agent_name,
                "task": task,
                "error": f"执行异常: {str(e)}",
                "execution_time": "error"
            }

    def parse_agent_request(self, user_input):
        """解析用户输入中的Agent请求"""
        # 匹配模式: 使用[agent名称]执行[任务]
        patterns = [
            r'使用\s*([a-zA-Z0-9\-]+)\s*(?:执行|进行|处理|分析|设计|开发|实现)\s*(.+)',
            r'调用\s*([a-zA-Z0-9\-]+)\s*(?:执行|进行|处理|分析|设计|开发|实现)\s*(.+)',
            r'让\s*([a-zA-Z0-9\-]+)\s*(?:执行|进行|处理|分析|设计|开发|实现)\s*(.+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, user_input)
            if match:
                agent_name = match.group(1)
                task = match.group(2)
                return agent_name, task

        return None, None

def main():
    """主处理函数"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "缺少参数"}))
        return

    action = sys.argv[1]
    connector = FlowConnector()

    if action == "status":
        status = connector.is_flow_available()
        print(json.dumps({
            "flow_available": status,
            "agents_count": len(connector.available_agents),
            "categories": list(connector.available_agents.keys())
        }, ensure_ascii=False, indent=2))

    elif action == "call":
        if len(sys.argv) < 4:
            print(json.dumps({"error": "缺少agent名称或任务描述"}))
            return

        agent_name = sys.argv[2]
        task = " ".join(sys.argv[3:])
        result = connector.call_agent(agent_name, task)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif action == "suggest":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "缺少任务描述"}))
            return

        task = " ".join(sys.argv[2:])
        suggestions = connector.suggest_agents(task)
        print(json.dumps({
            "task": task,
            "suggestions": suggestions
        }, ensure_ascii=False, indent=2))

    elif action == "parse":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "缺少用户输入"}))
            return

        user_input = " ".join(sys.argv[2:])
        agent_name, task = connector.parse_agent_request(user_input)
        print(json.dumps({
            "user_input": user_input,
            "agent_name": agent_name,
            "task": task
        }, ensure_ascii=False, indent=2))

    else:
        print(json.dumps({"error": "未知操作"}))

if __name__ == "__main__":
    main()