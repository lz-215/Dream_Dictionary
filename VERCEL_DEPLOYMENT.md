# 使用Vercel部署梦境解析器

本指南将引导您如何使用Vercel部署梦境解析器应用程序的前端和后端。

## 前提条件

1. Vercel账户（如果没有，请在[vercel.com](https://vercel.com)注册）
2. 已将代码推送到GitHub仓库（您已经完成了这一步）

## 部署步骤

### 1. 登录Vercel

访问[vercel.com/dashboard](https://vercel.com/dashboard)并登录您的账户。

### 2. 导入项目

1. 点击"Add New..."按钮，然后选择"Project"
2. 选择"Import Git Repository"
3. 选择您的GitHub仓库：`lz-215/Dream_Dictionary`
4. 如果您的GitHub账户尚未连接到Vercel，请按照提示进行连接

### 3. 配置项目

在配置页面上：

- **Project Name**：保持默认或输入您喜欢的名称
- **Framework Preset**：选择"Other"
- **Root Directory**：保持默认（`./`）
- **Build and Output Settings**：保持默认，我们已经在`vercel.json`中配置了这些设置
- **Environment Variables**：暂时不需要添加任何环境变量

### 4. 部署

点击"Deploy"按钮开始部署过程。

### 5. 等待部署完成

Vercel将开始构建和部署您的应用程序。这通常需要几分钟时间。

### 6. 访问您的应用

部署完成后，Vercel将提供一个URL（例如`https://dream-dictionary.vercel.app`）。点击这个URL访问您的应用程序。

## 自定义域名（可选）

如果您想使用自己的域名：

1. 在项目仪表板中，点击"Settings"
2. 点击"Domains"
3. 输入您的域名并点击"Add"
4. 按照Vercel提供的说明配置您的DNS设置

## 持续部署

Vercel会自动监控您的GitHub仓库。每当您推送更改到主分支时，Vercel都会自动重新部署您的应用程序。

## 监控和分析

Vercel提供了内置的监控和分析工具：

1. 在项目仪表板中，点击"Analytics"查看性能和使用情况数据
2. 点击"Logs"查看部署和运行时日志

## 故障排除

如果您遇到部署问题：

1. 检查Vercel的部署日志，了解错误详情
2. 确保您的`vercel.json`文件配置正确
3. 验证API处理程序是否正确实现

## 高级功能

Vercel提供了许多高级功能，您可以根据需要使用：

- **Serverless Functions**：扩展后端功能
- **Edge Functions**：在全球边缘网络上运行代码
- **Image Optimization**：自动优化图像
- **Web Analytics**：跟踪网站性能和用户行为

## 资源

- [Vercel文档](https://vercel.com/docs)
- [Vercel Python Serverless Functions](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Vercel CLI](https://vercel.com/docs/cli)
