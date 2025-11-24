# 提交信息模板

## 基本模板
```
<type>[optional scope]: <description>
```

## 完整模板
```
<type>[optional scope]: <description>

[optional body explaining the what and why]

[optional footer for breaking changes or issue references]
```

## 常用模板示例

### 新功能
```
feat(<scope>): add <feature name>

Implement <detailed description of the feature>.
Includes <key components or changes>.

Closes #<issue-number>
```

### Bug修复
```
fix(<scope>): resolve <issue description>

Fix <description of the problem> by <solution approach>.
Prevent <negative consequences> and improve <positive outcome>.
```

### 重构
```
refactor(<scope>): extract/improve/optimize <what>

<Rename/move/optimize> <component> to <reason>.
Improves <benefits like readability, performance, maintainability>.
```

### 文档更新
```
docs(<scope>): update <documentation section>

Add/update <type of documentation> for <feature/component>.
Includes <what was added or changed>.
```

### 性能优化
```
perf(<scope>): optimize <what>

Improve <metric> by <optimization technique>.
Reduces <resource usage> and increases <performance gain>.
```

### 测试
```
test(<scope>): add/update tests for <what>

Add <unit/integration/e2e> tests for <feature/component>.
Covers <test cases> and ensures <guarantees>.
```