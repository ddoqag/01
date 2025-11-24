# Commit Message 技能使用示例

## 示例1：基于Git Diff生成

**输入** (git diff输出):
```
diff --git a/src/components/Button.js b/src/components/Button.js
index 1234567..abcdefg 100644
--- a/src/components/Button.js
+++ b/src/components/Button.js
@@ -10,7 +10,7 @@ function Button({
     className={`btn btn-${variant} ${size ? `btn-${size}` : ''} ${className}`}
     onClick={onClick}
     disabled={disabled}
-    style={{ backgroundColor: color }}
+    style={{ backgroundColor: color, borderRadius: '8px' }}
   >
     {children}
   </button>
```

**输出**:
```
fix(ui): add border radius to button component

Apply consistent 8px border radius to all button variants
to match design system specifications.
```

## 示例2：基于文件变更列表生成

**输入**:
```
Modified files:
- src/api/user.js (added authentication logic)
- src/middleware/auth.js (new file)
- package.json (added jsonwebtoken, bcrypt)
```

**输出**:
```
feat(auth): implement JWT-based user authentication

Add complete authentication system with user login, JWT token
generation and validation. Includes secure password hashing
and middleware for protected routes.
```

## 示例3：基于变更描述生成

**输入**:
```
修复了用户注册时邮箱验证的正则表达式错误，现在可以正确验证包含特殊字符的邮箱地址
```

**输出**:
```
fix(auth): correct email validation regex for special characters

Update email validation pattern to properly handle special
characters like plus signs, dots, and hyphens in email
addresses before the @ symbol.
```

## 示例4：重构变更

**输入**:
```
将日期处理工具函数从utils.js移动到独立的date-utils.js文件中
```

**输出**:
```
refactor(utils): extract date utilities to separate module

Move date formatting and parsing functions from main utils
module to dedicated date-utils module for better code
organization and maintainability.
```

## 示例5：性能优化

**输入**:
```
优化了数据库查询，添加了索引，将用户列表查询时间从2秒减少到100ms
```

**输出**:
```
perf(db): optimize user list query with proper indexing

Add database indexes on frequently queried fields and optimize
SELECT statements. Reduces query time from 2s to 100ms.
```

## 使用场景

1. **开发团队协作**：保持提交信息的一致性和可读性
2. **自动化工具**：集成到CI/CD流程中
3. **代码审查**：快速了解代码变更的意图
4. **变更日志生成**：自动生成release notes
5. **版本管理**：语义化版本控制的基础

## 最佳实践

- ✅ 使用祈使句式（"add"而不是"added"）
- ✅ 首字母小写
- ✅ 标题不超过50个字符
- ✅ 正文每行不超过72个字符
- ✅ 解释变更的原因，而不是变更的内容
- ✅ 使用一致的scope命名