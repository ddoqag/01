# Commit Message 技能

## 概述

智能Git提交信息生成技能，基于代码变更自动生成符合Conventional Commits规范的提交信息。

## 功能特性

- 🤖 **智能分析**：自动分析代码变更内容
- 📝 **规范格式**：严格遵循Conventional Commits规范
- 🎯 **精准分类**：自动识别变更类型（feat、fix、refactor等）
- 📊 **详细说明**：生成包含body的完整提交信息
- 🔧 **灵活配置**：支持自定义提交类型和格式要求

## 安装方法

1. 将技能复制到mcp-tools的skills目录：
```bash
cp -r commit-message ~/.claude/skills/
```

2. 或直接克隆到技能目录：
```bash
cd ~/.claude/skills/
git clone <repository-url> commit-message
```

## 使用方法

### 方法1：集成到Claude Code

技能会自动识别以下触发条件：
- `git diff` 输出
- `git status` 结果
- 文件变更列表
- 变更描述文本

### 方法2：手动调用

```bash
# 使用git diff作为输入
git diff | skill commit-message

# 或使用变更描述
skill commit-message "修复登录页面在移动端显示错乱"
```

## 支持的提交类型

| 类型 | 描述 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(auth): add OAuth2 integration` |
| `fix` | Bug修复 | `fix(api): handle null response` |
| `docs` | 文档更新 | `docs(readme): update installation guide` |
| `style` | 代码格式 | `style(ui): fix button alignment` |
| `refactor` | 代码重构 | `refactor(utils): extract date functions` |
| `perf` | 性能优化 | `perf(db): optimize query performance` |
| `test` | 测试相关 | `test(user): add unit tests for auth` |
| `build` | 构建变更 | `build: update webpack configuration` |
| `ci` | CI/CD变更 | `ci(github): add automated tests` |
| `chore` | 其他杂项 | `chore(deps): update dependencies` |

## 输出格式

### 基本格式
```
<type>[optional scope]: <description>
```

### 完整格式
```
<type>[optional scope]: <description>

[optional body explaining the what and why]

[optional footer for breaking changes or issue references]
```

## 使用示例

### 示例1：新功能
**输入**：`添加用户头像上传功能`
**输出**：
```
feat(user): add avatar upload functionality

Implement avatar upload with image cropping and compression.
Supports JPG/PNG formats up to 5MB with automatic resizing.
```

### 示例2：Bug修复
**输入**：`修复登录页面移动端显示问题`
**输出**：
```
fix(auth): correct mobile layout for login page

Fix responsive design issues on mobile devices.
Adjust button sizes and spacing for better touch targets.
```

## 配置选项

在`skill.json`中可以配置：

- `supported_commit_types`: 支持的提交类型
- `max_subject_length`: 标题最大长度（默认50）
- `max_body_line_length`: 正文每行最大长度（默认72）
- `require_scope`: 是否强制要求scope
- `require_body`: 是否强制要求body
- `require_footer`: 是否强制要求footer

## 测试

运行测试用例：
```bash
cd ~/.claude/skills/commit-message/tests/
cat test-examples.md
```

## 贡献

欢迎提交Issue和Pull Request来改进这个技能！

## 许可证

MIT License