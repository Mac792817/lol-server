# 全网视频无水印下载器

支持抖音、快手、B站、小红书、皮皮虾、微博等平台的无水印视频解析与下载。

## 项目结构

```
python-pachong/
├── parsers/              # 视频解析器
│   ├── __init__.py
│   ├── base.py          # 基础解析类
│   ├── douyin.py        # 抖音解析
│   ├── kuaishou.py      # 快手解析
│   ├── bilibili.py      # B站解析
│   ├── xiaohongshu.py   # 小红书解析
│   ├── pipixia.py       # 皮皮虾解析
│   └── weibo.py         # 微博解析
├── templates/
│   └── index.html       # Web界面
├── config.py            # 配置文件
├── utils.py             # 工具函数
├── downloader.py        # 下载器
├── main.py              # 命令行工具
├── app.py               # Web服务
├── requirements.txt     # 依赖清单
├── Procfile             # Railway部署配置
├── runtime.txt          # Python版本
├── railway.json         # Railway配置
└── README.md
```

## 本地运行

### 命令行模式

```bash
# 安装依赖
pip install -r requirements.txt

# 解析视频
python main.py parse <视频链接>

# 下载视频
python main.py download <视频链接>

# 批量下载
python main.py batch urls.txt
```

### Web服务模式

```bash
# 启动服务
python app.py

# 访问 http://localhost:5000
```

## Railway部署

### 方法一：使用Railway CLI

1. 安装Railway CLI
2. 登录：`railway login`
3. 初始化项目：`railway init`
4. 部署：`railway up`

### 方法二：使用Git部署

1. 将代码推送到GitHub仓库
2. 在Railway上创建新项目
3. 选择GitHub仓库进行部署

### 部署注意事项

- 确保所有必要文件都包含在部署中
- Railway会自动检测Procfile和requirements.txt
- 端口通过环境变量`$PORT`配置

## API接口

### 解析视频

```
POST /api/parse
Content-Type: application/json

{
  "url": "视频链接"
}
```

响应：
```json
{
  "success": true,
  "data": {
    "title": "视频标题",
    "platform": "平台名称",
    "duration": 时长,
    "url": "无水印视频地址"
  }
}
```

### 下载视频

```
POST /api/download
Content-Type: application/json

{
  "url": "视频链接"
}
```

### 健康检查

```
GET /health
```

## 支持的平台

- ✅ 抖音 (douyin.com)
- ✅ 快手 (kuaishou.com)
- ✅ B站 (bilibili.com)
- ✅ 小红书 (xiaohongshu.com)
- ✅ 皮皮虾 (pipix.com)
- ✅ 微博 (weibo.com)

## 注意事项

- 视频平台API可能会更新，解析器需要相应调整
- 本项目仅供学习交流使用
- 请遵守各平台的用户协议

## 许可证

MIT License
