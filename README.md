# 抖音评论生成器

一个基于文心一言API的抖音视频评论自动生成工具。

## 功能特点

- 支持抖音视频链接解析
- 自动下载视频信息
- 使用文心一言API生成智能评论
- 美观的Web界面
- 支持多种视频链接格式

## 部署步骤

1. Fork 这个仓库到你的GitHub账号

2. 在Vercel上部署:
   - 访问 [Vercel](https://vercel.com)
   - 使用GitHub账号登录
   - 点击 "Import Project"
   - 选择你fork的仓库
   - 设置环境变量:
     - `ERNIE_API_KEY`: 百度智能云API Key
     - `ERNIE_SECRET_KEY`: 百度智能云Secret Key

3. 完成部署！

## 本地开发

1. 克隆仓库:
```bash
git clone <your-repo-url>
cd douyin_comment_generator
```

2. 安装依赖:
```bash
pip install -r requirements.txt
```

3. 设置环境变量:
复制 `.env.example` 到 `.env` 并填写你的API密钥

4. 运行应用:
```bash
python app.py
```

## 注意事项

- 需要有效的百度智能云API密钥
- 请遵守API使用限制
- 建议在生产环境中使用更安全的密钥管理方式
