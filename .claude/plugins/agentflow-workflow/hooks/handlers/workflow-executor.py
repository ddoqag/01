#!/usr/bin/env python3
"""
AgentFlow工作流执行器
实现多Agent协调工作流的核心逻辑
"""

import json
import sys
import os
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Any

class AgentFlowExecutor:
    def __init__(self):
        self.flow_bin_path = "/mnt/d/flow/bin/flow"
        self.flow_project_path = "/mnt/d/flow"
        self.workflow_state_file = os.path.expanduser("~/.claude/agentflow_workflow.json")
        self.workflows = self._get_predefined_workflows()

    def _get_predefined_workflows(self):
        """获取预定义的工作流模板"""
        return {
            "system_development": {
                "name": "系统开发工作流",
                "description": "完整的软件开发流程",
                "phases": [
                    {
                        "name": "需求分析",
                        "agents": ["business-analyst", "system-architect"],
                        "description": "分析用户需求，制定技术规格"
                    },
                    {
                        "name": "架构设计",
                        "agents": ["cloud-architect", "backend-architect", "database-architect"],
                        "description": "设计系统架构，选择技术栈"
                    },
                    {
                        "name": "开发实施",
                        "agents": ["python-pro", "web-developer", "test-automator"],
                        "description": "编码实现，单元测试"
                    },
                    {
                        "name": "测试验证",
                        "agents": ["quality-assurance", "security-auditor", "performance-engineer"],
                        "description": "集成测试，性能优化"
                    },
                    {
                        "name": "部署上线",
                        "agents": ["devops-engineer", "monitoring-specialist"],
                        "description": "环境部署，监控配置"
                    }
                ]
            },
            "data_analysis": {
                "name": "数据分析工作流",
                "description": "端到端数据分析流程",
                "phases": [
                    {
                        "name": "数据收集",
                        "agents": ["data-engineer", "database-analyst"],
                        "description": "收集原始数据，数据源连接"
                    },
                    {
                        "name": "数据清洗",
                        "agents": ["data-scientist", "python-pro"],
                        "description": "数据预处理，异常值处理"
                    },
                    {
                        "name": "分析建模",
                        "agents": ["data-scientist", "quant-analyst", "statistician"],
                        "description": "统计分析，机器学习建模"
                    },
                    {
                        "name": "结果可视化",
                        "agents": ["data-analyst", "ui-ux-designer"],
                        "description": "图表制作，报告生成"
                    },
                    {
                        "name": "报告生成",
                        "agents": ["technical-writer", "business-analyst"],
                        "description": "撰写分析报告，提供决策建议"
                    }
                ]
            },
            "security_audit": {
                "name": "安全审计工作流",
                "description": "全面的安全评估和加固",
                "phases": [
                    {
                        "name": "安全评估",
                        "agents": ["security-architect", "risk-manager"],
                        "description": "安全风险评估，威胁建模"
                    },
                    {
                        "name": "漏洞扫描",
                        "agents": ["security-auditor", "penetration-tester"],
                        "description": "自动化扫描，手动渗透测试"
                    },
                    {
                        "name": "风险分析",
                        "agents": ["risk-manager", "compliance-auditor"],
                        "description": "风险等级评估，合规检查"
                    },
                    {
                        "name": "安全加固",
                        "agents": ["backend-security-coder", "devops-engineer"],
                        "description": "代码安全修复，基础设施加固"
                    },
                    {
                        "name": "合规检查",
                        "agents": ["compliance-auditor", "legal-advisor"],
                        "description": "合规性验证，文档更新"
                    }
                ]
            },
            "devops_automation": {
                "name": "DevOps自动化工作流",
                "description": "CI/CD和运维自动化实施",
                "phases": [
                    {
                        "name": "环境搭建",
                        "agents": ["infrastructure-engineer", "cloud-engineer"],
                        "description": "基础设施准备，云环境配置"
                    },
                    {
                        "name": "CI/CD配置",
                        "agents": ["devops-engineer", "test-automator"],
                        "description": "构建流水线，自动化测试"
                    },
                    {
                        "name": "监控部署",
                        "agents": ["monitoring-specialist", "site-reliability-engineer"],
                        "description": "监控系统搭建，告警配置"
                    },
                    {
                        "name": "性能优化",
                        "agents": ["performance-engineer", "backend-architect"],
                        "description": "性能调优，资源优化"
                    },
                    {
                        "name": "运维维护",
                        "agents": ["devops-engineer", "monitoring-specialist"],
                        "description": "日常运维，故障处理"
                    }
                ]
            }
        }

    def save_workflow_state(self, workflow_id: str, state: Dict[str, Any]):
        """保存工作流状态"""
        try:
            os.makedirs(os.path.dirname(self.workflow_state_file), exist_ok=True)

            # 读取现有状态
            if os.path.exists(self.workflow_state_file):
                with open(self.workflow_state_file, 'r') as f:
                    all_states = json.load(f)
            else:
                all_states = {}

            all_states[workflow_id] = state

            with open(self.workflow_state_file, 'w') as f:
                json.dump(all_states, f)

            return True
        except Exception:
            return False

    def load_workflow_state(self, workflow_id: str):
        """加载工作流状态"""
        try:
            if os.path.exists(self.workflow_state_file):
                with open(self.workflow_state_file, 'r') as f:
                    all_states = json.load(f)
                return all_states.get(workflow_id, {})
            return {}
        except Exception:
            return {}

    def parse_workflow_request(self, user_input: str):
        """解析用户输入中的工作流请求"""
        # 匹配工作流请求模式
        patterns = [
            r'协调工作流[：:]\s*([^\s-]+)\s*-\s*(.+)',
            r'启动AgentFlow.*执行\s*(.+)',
            r'使用工作流管理器处理\s*(.+)',
            r'执行工作流[：:]\s*([^\s-]+)\s*-\s*(.+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, user_input)
            if match:
                workflow_type = match.group(1) if len(match.groups()) > 1 else "system_development"
                project_desc = match.group(2) if len(match.groups()) > 1 else match.group(1)
                return workflow_type, project_desc

        return None, None

    def execute_phase(self, workflow_id: str, phase: Dict[str, Any], project_context: str):
        """执行工作流阶段"""
        phase_name = phase["name"]
        agents = phase["agents"]
        phase_description = phase["description"]

        results = []
        start_time = time.time()

        for agent in agents:
            agent_result = {
                "agent": agent,
                "phase": phase_name,
                "start_time": datetime.now().isoformat(),
                "task": f"{phase_description} - {agent}专项任务",
                "status": "running"
            }

            try:
                # 调用Flow系统执行Agent任务
                flow_result = self._call_flow_agent(
                    agent,
                    f"{phase_description} - {agent}专项任务，项目背景：{project_context}"
                )

                agent_result.update({
                    "status": "completed" if flow_result.get("success") else "failed",
                    "result": flow_result,
                    "end_time": datetime.now().isoformat(),
                    "execution_time": time.time() - start_time
                })

            except Exception as e:
                agent_result.update({
                    "status": "error",
                    "error": str(e),
                    "end_time": datetime.now().isoformat(),
                    "execution_time": time.time() - start_time
                })

            results.append(agent_result)

        return {
            "phase": phase_name,
            "results": results,
            "total_time": time.time() - start_time,
            "status": "completed"
        }

    def _call_flow_agent(self, agent_name: str, task: str):
        """调用Flow系统中的Agent"""
        try:
            result = subprocess.run(
                [self.flow_bin_path, "agent", agent_name, task],
                cwd=self.flow_project_path,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Agent执行超时"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"执行异常: {str(e)}"
            }

    def execute_workflow(self, workflow_type: str, project_description: str):
        """执行完整工作流"""
        workflow_id = f"workflow_{int(time.time())}"

        if workflow_type not in self.workflows:
            # 尝试智能匹配
            workflow_type = self._match_workflow_type(workflow_type)
            if not workflow_type:
                return {
                    "success": False,
                    "error": f"未找到工作流类型: {workflow_type}",
                    "available_types": list(self.workflows.keys())
                }

        workflow = self.workflows[workflow_type]

        # 初始化工作流状态
        workflow_state = {
            "workflow_id": workflow_id,
            "type": workflow_type,
            "name": workflow["name"],
            "description": workflow["description"],
            "project": project_description,
            "start_time": datetime.now().isoformat(),
            "status": "running",
            "current_phase": 0,
            "phases_completed": []
        }

        self.save_workflow_state(workflow_id, workflow_state)

        # 执行各个阶段
        all_results = []

        for i, phase in enumerate(workflow["phases"]):
            workflow_state["current_phase"] = i
            self.save_workflow_state(workflow_id, workflow_state)

            phase_result = self.execute_phase(workflow_id, phase, project_description)
            all_results.append(phase_result)

            workflow_state["phases_completed"].append(phase["name"])
            self.save_workflow_state(workflow_id, workflow_state)

        # 完成工作流
        workflow_state.update({
            "status": "completed",
            "end_time": datetime.now().isoformat(),
            "total_execution_time": time.time() - time.mktime(
                datetime.fromisoformat(workflow_state["start_time"]).timetuple()
            ),
            "all_results": all_results
        })

        self.save_workflow_state(workflow_id, workflow_state)

        return {
            "success": True,
            "workflow_id": workflow_id,
            "workflow_type": workflow_type,
            "project": project_description,
            "results": all_results,
            "summary": self._generate_workflow_summary(all_results)
        }

    def _match_workflow_type(self, user_input: str):
        """智能匹配工作流类型"""
        user_lower = user_input.lower()

        if any(keyword in user_lower for keyword in ['开发', '系统', '软件', '应用']):
            return "system_development"
        elif any(keyword in user_lower for keyword in ['数据', '分析', '统计', '建模']):
            return "data_analysis"
        elif any(keyword in user_lower for keyword in ['安全', '审计', '漏洞', '合规']):
            return "security_audit"
        elif any(keyword in user_lower for keyword in ['运维', 'devops', '自动化', '部署']):
            return "devops_automation"

        return None

    def _generate_workflow_summary(self, all_results: List[Dict[str, Any]]):
        """生成工作流执行摘要"""
        total_phases = len(all_results)
        completed_phases = sum(1 for r in all_results if r.get("status") == "completed")

        agent_results = []
        for phase_result in all_results:
            agent_results.extend(phase_result.get("results", []))

        total_agents = len(agent_results)
        successful_agents = sum(1 for r in agent_results if r.get("status") == "completed")

        return {
            "total_phases": total_phases,
            "completed_phases": completed_phases,
            "total_agents": total_agents,
            "successful_agents": successful_agents,
            "success_rate": successful_agents / total_agents if total_agents > 0 else 0,
            "completion_rate": completed_phases / total_phases if total_phases > 0 else 0
        }

def main():
    """主处理函数"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "缺少参数"}))
        return

    action = sys.argv[1]
    executor = AgentFlowExecutor()

    if action == "execute":
        if len(sys.argv) < 4:
            print(json.dumps({"error": "缺少工作流类型或项目描述"}))
            return

        workflow_type = sys.argv[2]
        project_description = " ".join(sys.argv[3:])
        result = executor.execute_workflow(workflow_type, project_description)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif action == "parse":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "缺少用户输入"}))
            return

        user_input = " ".join(sys.argv[2:])
        workflow_type, project_desc = executor.parse_workflow_request(user_input)
        print(json.dumps({
            "user_input": user_input,
            "workflow_type": workflow_type,
            "project_description": project_desc
        }, ensure_ascii=False, indent=2))

    elif action == "workflows":
        print(json.dumps({
            "available_workflows": list(executor.workflows.keys()),
            "workflows": executor.workflows
        }, ensure_ascii=False, indent=2))

    elif action == "state":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "缺少工作流ID"}))
            return

        workflow_id = sys.argv[2]
        state = executor.load_workflow_state(workflow_id)
        print(json.dumps(state, ensure_ascii=False, indent=2))

    else:
        print(json.dumps({"error": "未知操作"}))

if __name__ == "__main__":
    main()