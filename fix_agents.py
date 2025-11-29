#!/usr/bin/env python3
"""
修复Agent文件的frontmatter格式
将frontmatter移到文件开头，删除重复内容
"""

import os
import re
from pathlib import Path

# 需要修复的文件列表
files_to_fix = [
    "C:\\Users\\ddo\\.claude\\agents\\ai-engineer-v3.md",
    "C:\\Users\\ddo\\.claude\\agents\\cloud-architect-v3.md",
    "C:\\Users\\ddo\\.claude\\agents\\blockchain-developer-v3.md",
    "C:\\Users\\ddo\\.claude\\agents\\code-reviewer-v3.md",
    "C:\\Users\\ddo\\.claude\\agents\\data-scientist-v3.md",
    "C:\\Users\\ddo\\.claude\\agents\\devops-troubleshooter-v3.md",
    "C:\\Users\\ddo\\.claude\\agents\\game-developer-v3.md",
    "C:\\Users\\ddo\\.claude\\agents\\frontend-developer-v3.md",
    "C:\\Users\\ddo\\.claude\\agents\\monitoring-expert-v3.md",
    "C:\\Users\\ddo\\.claude\\agents\\mobile-developer-v3.md",
    "C:\\Users\\ddo\\.claude\\agents\\kubernetes-architect-v3.md",
    "C:\\Users\\ddo\\.claude\\agents\\performance-engineer-v3.md",
    "C:\\Users\\ddo\\.claude\\agents\\react-native-expert-v2.md",
    "C:\\Users\\ddo\\.claude\\agents\\security-expert-v3.md",
    "C:\\Users\\ddo\\.claude\\agents\\web-performance-expert-v2.md",
    "C:\\Users\\ddo\\.claude\\agents\\ui-ux-designer-v3.md",
    "C:\\Users\\ddo\\.claude\\agents\\typescript-pro-v3.md"
]

def fix_agent_file(file_path):
    """修复单个Agent文件的frontmatter格式"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 查找frontmatter块
        frontmatter_match = re.search(r'---\n(.*?name:\s*\w+.*?model:\s*\w+.*?)(?:---\n)', content, re.DOTALL)

        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)

            # 查找标题行
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else ""

            # 查找技能标签
            skills_match = re.search(r'\*\*技能标签\*\*:\s*(.+)', content)
            skills = skills_match.group(1) if skills_match else ""

            # 移除旧的frontmatter和重复的描述
            content_clean = re.sub(r'^.*?---\n.*?---\n', '', content, flags=re.DOTALL)
            content_clean = re.sub(r'\nname:.*?\n.*?model:.*?\n.*?---', '', content_clean, flags=re.DOTALL)

            # 构建新的文件内容
            new_content = f"""---
{frontmatter}---

# {title}

**技能标签**: {skills}

{content_clean.strip()}"""

            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            print(f"✅ 修复完成: {os.path.basename(file_path)}")
            return True
        else:
            print(f"❌ 未找到frontmatter: {os.path.basename(file_path)}")
            return False

    except Exception as e:
        print(f"❌ 修复失败 {os.path.basename(file_path)}: {str(e)}")
        return False

def main():
    """主函数"""
    print("Starting agent file frontmatter fix...")

    success_count = 0
    total_count = len(files_to_fix)

    for file_path in files_to_fix:
        if os.path.exists(file_path):
            if fix_agent_file(file_path):
                success_count += 1
        else:
            print(f"File not found: {file_path}")

    print(f"\nFix completed: {success_count}/{total_count} files successfully fixed")

if __name__ == "__main__":
    main()