# Code Reviewer 技能

## 概述

智能代码审查技能，自动检测代码质量问题、安全漏洞、性能问题和最佳实践违规。支持多种编程语言，提供详细的审查报告和修复建议。

## 功能特性

- 🔒 **安全检测**：SQL注入、XSS、硬编码凭证等安全漏洞
- ⚡ **性能分析**：算法复杂度、内存泄漏、数据库优化
- 🛠️ **质量评估**：代码可读性、可维护性、最佳实践
- 📊 **结构化报告**：分级问题分类、具体修复建议
- 🌐 **多语言支持**：JavaScript、Python、Java、Go等

## 支持的审查类型

### 安全性审查
- SQL注入、XSS、命令注入
- 硬编码敏感信息
- 弱加密算法
- 权限控制问题

### 性能分析
- 算法复杂度分析
- 内存管理问题
- 数据库查询优化
- 异步处理模式

### 代码质量
- 命名规范检查
- 错误处理评估
- 代码结构分析
- 可维护性评估

### 最佳实践
- 语言特性使用
- 框架规范检查
- 设计原则验证
- 测试覆盖建议

## 支持的语言

| 语言 | 支持程度 | 检查规则 |
|------|----------|----------|
| JavaScript/TypeScript | ✅ 完整 | 安全、性能、ES6特性 |
| Python | ✅ 完整 | PEP8、安全、性能 |
| Java | 🚧 基础 | 安全、性能、最佳实践 |
| Go | 🚧 基础 | 并发安全、性能 |
| C++ | 🚧 基础 | 内存安全、性能 |
| PHP | 🚧 基础 | 安全、最佳实践 |

## 使用方法

### 方法1：集成到Claude Code

```bash
# 审查单个文件
skill code-reviewer "审查这个文件的安全性：$(cat app.js)"

# 审查代码变更
git diff | skill code-reviewer

# 审查特定问题
skill code-reviewer "检查这段代码的性能问题：[代码片段]"
```

### 方法2：在开发流程中使用

```bash
# 作为Git钩子
git pre-commit hook: "skill code-reviewer --pre-commit"

# CI/CD集成
github actions: "uses: code-reviewer-action@v1"

# IDE插件
vscode extension: "Code Reviewer AI"
```

## 审查报告示例

### 总体评估
```
📊 代码审查报告
总体评分：B
代码质量：良好，存在一些改进空间
```

### 问题分类
```
🚨 严重问题 (Critical) - 2个
⚠️ 高优先级 (High) - 3个
💡 中优先级 (Medium) - 5个
ℹ️ 低优先级 (Low) - 2个
```

### 具体建议
```
#### 问题1：SQL注入漏洞
- 位置：app.js:45
- 严重性：Critical
- 修复方案：使用参数化查询
```

## 配置选项

### 基础配置
```json
{
  "review_categories": [
    "security", "performance", "maintainability"
  ],
  "severity_levels": ["critical", "high", "medium", "low"],
  "max_suggestions_per_category": 5
}
```

### 语言特定配置
```json
{
  "javascript": {
    "check_es6_features": true,
    "require_strict_mode": true,
    "security_checks": true
  },
  "python": {
    "pep8_compliance": true,
    "type_hints": true,
    "docstring_checks": true
  }
}
```

## 集成示例

### Git Hook集成
```bash
#!/bin/sh
# .git/hooks/pre-commit

echo "运行代码审查..."
skill code-reviewer --files=$(git diff --cached --name-only)
if [ $? -ne 0 ]; then
  echo "代码审查发现问题，请修复后提交"
  exit 1
fi
```

### GitHub Actions集成
```yaml
name: Code Review
on: [pull_request]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Code Reviewer
        run: skill code-reviewer --diff=${{ github.event.pull_request.diff_url }}
```

## 最佳实践

### 开发团队使用
1. **统一标准**：团队统一使用相同的审查规则
2. **渐进改进**：优先修复严重和高优先级问题
3. **学习导向**：将审查结果作为学习机会
4. **定期复盘**：定期分析代码质量趋势

### 个人开发者
1. **提交前检查**：每次提交前运行代码审查
2. **持续学习**：理解发现的问题和修复方案
3. **工具辅助**：结合IDE插件实时反馈
4. **质量提升**：逐步提高代码质量标准

## 扩展和定制

### 添加自定义规则
```json
{
  "custom_rules": {
    "company_naming": {
      "pattern": "[A-Z][a-zA-Z]*Controller",
      "message": "控制器类名必须以Controller结尾"
    }
  }
}
```

### 自定义审查模板
```markdown
### {{company_name}}代码审查标准
- 安全检查：强制要求
- 性能检查：生产代码必须
- 文档要求：公共API需要文档
```

## 故障排除

### 常见问题
1. **误报**：调整规则配置或添加白名单
2. **性能慢**：限制审查范围或使用增量审查
3. **规则不适用**：针对特定项目自定义规则

### 调试模式
```bash
skill code-reviewer --debug --verbose input.js
```

## 贡献

欢迎贡献新的审查规则、语言支持或改进建议！

## 许可证

MIT License