// 示例代码：包含多种安全和性能问题的用户登录系统

const express = require('express');
const bcrypt = require('bcrypt');
const app = express();

// 硬编码的数据库连接字符串
const dbPassword = 'admin123';
const dbConnection = 'mysql://user:' + dbPassword + '@localhost/myapp';

// 用户登录接口
app.post('/login', async (req, res) => {
  const username = req.body.username;
  const password = req.body.password;

  // 安全问题：SQL注入漏洞
  const query = 'SELECT * FROM users WHERE username = \'' + username + '\' AND password = \'' + password + '\'';

  db.query(query, (err, result) => {
    if (err) throw err;

    if (result.length > 0) {
      // 记录敏感信息到日志
      console.log('用户登录成功: ' + username + ' 密码: ' + password);

      // 性能问题：在循环中创建对象
      const permissions = [];
      for (let i = 0; i < result[0].roles.length; i++) {
        const role = result[0].roles[i];
        const perm = { role: role, timestamp: new Date(), user: result[0].id };
        permissions.push(perm);
      }

      // 内存泄漏：未清理定时器
      setInterval(() => {
        console.log('用户活跃: ' + username);
      }, 60000);

      // 安全问题：直接输出用户输入到HTML
      res.send('<h1>欢迎, ' + username + '!</h1>');
    } else {
      res.status(401).send('登录失败');
    }
  });
});

// 数据处理函数
function processUserData(data) {
  // 性能问题：嵌套循环O(n²)
  const result = [];
  for (let i = 0; i < data.length; i++) {
    for (let j = 0; j < data[i].items.length; j++) {
      // 重复计算长度
      if (data[i].items.length > 0) {
        result.push(data[i].items[j]);
      }
    }
  }
  return result;
}

// 字符串拼接性能问题
function generateReport(users) {
  let report = '';
  for (let i = 0; i < users.length; i++) {
    report = report + 'User: ' + users[i].name + ', Email: ' + users[i].email + '\n';
  }
  return report;
}

// 错误处理不当
app.get('/user/:id', (req, res) => {
  const userId = req.params.id;

  // 安全问题：类型转换错误
  const query = 'SELECT * FROM users WHERE id = ' + userId;

  // 缺少错误处理
  db.query(query, (err, result) => {
    res.json(result[0]);
  });
});

// 启动服务器
app.listen(3000, () => {
  console.log('服务器运行在端口3000');
  eval('console.log("动态代码执行")'); // 安全问题：eval使用
});

module.exports = app;