# 代码审查报告模板

## 📊 代码审查报告

### 审查信息
- **审查日期**：{{date}}
- **审查人员**：Code Reviewer AI
- **代码文件**：{{files}}
- **代码行数**：{{lines}}
- **主要语言**：{{language}}

### 总体评估：{{overall_score}}

{{overall_summary}}

---

### 🚨 严重问题 (Critical) - {{critical_count}}个

{{#each critical_issues}}
#### {{@index}}. {{title}}
- **严重性**：Critical
- **位置**：`{{file}}:{{line}}`
- **问题描述**：{{description}}
- **修复方案**：{{solution}}

```diff
- {{before_code}}
+ {{after_code}}
```

{{/each}}

---

### ⚠️ 高优先级 (High) - {{high_count}}个

{{#each high_issues}}
#### {{@index}}. {{title}}
- **严重性**：High
- **位置**：`{{file}}:{{line}}`
- **问题描述**：{{description}}
- **修复方案**：{{solution}}

```diff
- {{before_code}}
+ {{after_code}}
```

{{/each}}

---

### 💡 中优先级 (Medium) - {{medium_count}}个

{{#each medium_issues}}
#### {{@index}}. {{title}}
- **严重性**：Medium
- **位置**：`{{file}}:{{line}}`
- **问题描述**：{{description}}
- **修复方案**：{{solution}}

{{/each}}

---

### ℹ️ 低优先级 (Low) - {{low_count}}个

{{#each low_issues}}
#### {{@index}}. {{title}}
- **严重性**：Low
- **位置**：`{{file}}:{{line}}`
- **问题描述**：{{description}}
- **修复方案**：{{solution}}

{{/each}}

---

### ✅ 代码亮点

{{#each positive_points}}
- **{{title}}**：{{description}}
{{/each}}

---

### 📈 改进建议

1. {{suggestion_1}}
2. {{suggestion_2}}
3. {{suggestion_3}}

---

### 🔧 快速修复清单

- [ ] 修复所有Critical级别问题
- [ ] 修复High级别安全问题
- [ ] 优化性能瓶颈
- [ ] 完善错误处理
- [ ] 添加单元测试
- [ ] 更新文档

---

### 📋 审查总结

**代码质量评分**：{{quality_score}}/10

| 维度 | 评分 | 说明 |
|------|------|------|
| 安全性 | {{security_score}}/10 | {{security_comment}} |
| 性能 | {{performance_score}}/10 | {{performance_comment}} |
| 可读性 | {{readability_score}}/10 | {{readability_comment}} |
| 可维护性 | {{maintainability_score}}/10 | {{maintainability_comment}} |
| 最佳实践 | {{best_practices_score}}/10 | {{best_practices_comment}} |

**下次提交前检查清单**：
- [ ] 运行静态代码分析工具
- [ ] 执行单元测试和集成测试
- [ ] 检查安全漏洞扫描结果
- [ ] 验证性能基准测试
- [ ] 更新相关文档

---

*本报告由AI代码审查助手自动生成，建议结合人工审查进行最终评估*