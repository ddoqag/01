# Commit Message 技能测试用例

## 测试用例1：新功能开发

**测试输入**:
```
新增用户头像上传功能，支持裁剪和压缩
```

**预期输出**:
```
feat(user): add avatar upload functionality

Implement avatar upload with image cropping and compression.
Supports JPG/PNG formats up to 5MB with automatic resizing.
```

## 测试用例2：Bug修复

**测试输入**:
```
修复登录页面在移动端显示错乱的问题
```

**预期输出**:
```
fix(auth): correct mobile layout for login page

Fix responsive design issues on mobile devices.
Adjust button sizes and spacing for better touch targets.
```

## 测试用例3：重构

**测试输入**:
```
将HTTP请求从fetch改为axios，统一错误处理
```

**预期输出**:
```
refactor(api): replace fetch with axios for HTTP requests

Migrate from native fetch to axios for better error handling
and request/response interceptors. Improves debugging and
error reporting consistency.
```

## 测试用例4：文档更新

**测试输入**:
```
更新README.md，添加安装和使用说明
```

**预期输出**:
```
docs(readme): update installation and usage instructions

Add comprehensive setup guide and usage examples.
Include troubleshooting section and API reference links.
```

## 测试用例5：性能优化

**测试输入**:
```
优化图片懒加载，减少首屏加载时间
```

**预期输出**:
```
perf(ui): optimize image lazy loading for better performance

Implement intersection observer for image lazy loading.
Reduce initial page load time by 30% and improve LCP score.
```

## 测试用例6：测试添加

**测试输入**:
```
为用户服务添加单元测试，覆盖主要功能
```

**预期输出**:
```
test(user): add unit tests for user service

Add comprehensive unit tests covering user CRUD operations,
authentication methods and error handling scenarios.
Achieve 90% code coverage for user service module.
```

## 测试用例7：破坏性变更

**测试输入**:
```
更改API响应格式，移除废弃字段
```

**预期输出**:
```
BREAKING CHANGE: api: update user response format

Remove deprecated fields from user API response.
Add new preferred_name field and update validation.

BREAKING CHANGE: user.name is replaced by user.preferred_name
```

## 测试用例8：杂项变更

**测试输入**:
```
更新依赖包版本，修复安全漏洞
```

**预期输出**:
```
chore(deps): update dependencies to fix security vulnerabilities

Update lodash to 4.17.21 and express to 4.18.2.
Fixes CVE-2021-23337 and CVE-2022-24999.
```

## 验证标准

每个输出应该满足：
- ✅ 符合Conventional Commits规范
- ✅ type选择准确
- ✅ description简洁清晰（≤50字符）
- ✅ 使用祈使句式
- ✅ 包含必要的body说明
- ✅ 格式正确且一致

## 边界测试

### 最小变更
**输入**: "修复拼写错误"
**输出**: `fix: correct spelling error in README`

### 复杂变更
**输入**: "重构整个认证系统，支持多因素认证，添加OAuth2集成，修复所有已知安全问题"
**输出**: 应该包含详细的body说明所有变更

### 模糊描述
**输入**: "更新代码"
**预期**: 技能应该要求更具体的变更信息