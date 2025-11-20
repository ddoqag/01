#!/usr/bin/env python3
"""
Flow模式切换钩子处理器
负责管理三种交互模式的切换和状态显示
"""

import json
import os
import sys
from pathlib import Path

class FlowModeManager:
    def __init__(self):
        self.modes = ["flow", "agentflow", "fusion"]
        self.mode_icons = {
            "flow": "🎯",
            "agentflow": "🔗",
            "fusion": "🚀"
        }
        self.mode_names = {
            "flow": "Flow Mode",
            "agentflow": "AgentFlow Mode",
            "fusion": "Fusion Mode"
        }
        self.state_file = os.path.expanduser("~/.claude/flow_mode_state.json")

    def get_current_mode(self):
        """获取当前模式"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    return data.get('current_mode', 'flow')
            return 'flow'
        except Exception:
            return 'flow'

    def set_current_mode(self, mode):
        """设置当前模式"""
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump({'current_mode': mode}, f)
            return True
        except Exception:
            return False

    def get_next_mode(self, current_mode):
        """获取下一个模式（顺序切换）"""
        current_index = self.modes.index(current_mode) if current_mode in self.modes else 0
        next_index = (current_index + 1) % len(self.modes)
        return self.modes[next_index]

    def switch_mode(self, target_mode=None):
        """切换模式"""
        current_mode = self.get_current_mode()

        if target_mode:
            # 切换到指定模式
            if target_mode in self.modes:
                new_mode = target_mode
            else:
                return self.create_response(current_mode, "无效的模式名称")
        else:
            # 顺序切换到下一个模式
            new_mode = self.get_next_mode(current_mode)

        # 保存新模式
        if self.set_current_mode(new_mode):
            return self.create_response(new_mode, f"已切换到{self.mode_names[new_mode]}")
        else:
            return self.create_response(current_mode, "模式切换失败")

    def create_response(self, mode, message):
        """创建模式标识响应"""
        icon = self.mode_icons.get(mode, "📋")
        name = self.mode_names.get(mode, "Unknown Mode")

        return {
            "hookSpecificOutput": {
                "additionalContext": f"[{icon} {name}] {message}",
                "mode": mode,
                "icon": icon,
                "name": name
            }
        }

    def handle_alt_switch(self):
        """处理Alt键切换"""
        return self.switch_mode()

def main():
    """主处理函数"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "缺少参数"}))
        return

    action = sys.argv[1]
    manager = FlowModeManager()

    if action == "switch":
        target_mode = sys.argv[2] if len(sys.argv) > 2 else None
        result = manager.switch_mode(target_mode)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif action == "get":
        mode = manager.get_current_mode()
        icon = manager.mode_icons.get(mode, "📋")
        name = manager.mode_names.get(mode, "Unknown Mode")
        print(json.dumps({
            "mode": mode,
            "icon": icon,
            "name": name,
            "display": f"[{icon} {name}]"
        }, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"error": "未知操作"}))

if __name__ == "__main__":
    main()