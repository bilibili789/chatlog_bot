# 聊天日志机器人

这个Python脚本可以自动获取群聊日志，通过大模型总结内容，并发送到飞书群。

## 功能特性

- 自动获取指定群组的当日聊天日志
- 使用DeepSeek V3模型进行智能总结
- 自动发送总结报告到飞书群
- 支持多个群组批量处理
- 配置文件和环境变量分离，安全性更高

## 安装依赖
提示：为里面其他的包的影响，建议先在项目下建立一下虚拟环境在安装python包。
以 MacOS 系统为例子：
然后在虚拟环境中安装依赖
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 配置设置

### 1. 环境变量配置

复制环境变量模板并修改：
```bash
cp env_template.txt .env
```

然后编辑 `.env` 文件，设置你的API密钥和Webhook地址：


```env
# DeepSeek API配置，先到https://siliconflow.cn申请一个 API密钥
DEEPSEEK_API_KEY=你的DeepSeek API密钥

# 飞书Webhook配置，找到对应的飞书群，在设置里面的群机器人添加一个。
FEISHU_WEBHOOK=你的飞书机器人Webhook地址
```



### 2. 应用配置

复制配置模板并修改：
```bash
cp config.template.json config.json
```

然后编辑 `config.json` 文件，主要配置：
- `chatlog_api_base`: 聊天日志API地址
- `deepseek_base_url`: DeepSeek API基础URL  
- `deepseek_model`: 使用的DeepSeek模型
- `talkers`: **需要处理的群组列表（替换为你的实际群组名称）**
- `deepseek_config`: DeepSeek API参数配置

提示：群组的名称可以通过http://127.0.0.1:5030/api/v1/chatroom接口查询。

## 使用方法

### 方式一：定时调度运行（推荐）

1. 确保聊天日志API服务运行在 `http://127.0.0.1:5030`
2. 配置环境变量和配置文件
3. 运行定时调度程序：

```bash
python main.py
```

然后选择操作：
- `1` - 启动定时调度器（每天18:00自动执行）
- `2` - 立即执行一次（测试运行）
- `3` - 查看日志文件
- `4` - 退出程序

测试选择 2，定时运行选择1，定时调度时间暂时没有放到配置文件，可以在main.py中自行修改，第 76 行。

## 输出格式

每个群组的总结报告包含：
- 整体讨论风格评价
- 最多5个热门话题
- 每个话题包含：话题名、参与者、时间段、过程、评价

## 文件结构

```
├── main.py                 # 定时调度主程序
├── chatlog_bot.py          # 聊天日志机器人核心模块
├── config.json             # 配置文件 (需要自行创建)
├── config.template.json    # 配置文件模板
├── .env                    # 环境变量文件 (需要自行创建)
├── env_template.txt        # 环境变量模板
├── requirements.txt        # Python依赖包
├── logs/                   # 日志文件目录 (自动创建)
│   └── chatlog_bot_YYYYMMDD.log
└── README.md              # 使用说明
```

## 注意事项

- 确保API服务正常运行
- 检查网络连接和API密钥有效性
- 飞书机器人需要有群组发送权限
- **不要将 `.env` 和 `config.json` 文件提交到版本控制系统**
- **`config.json` 包含群组名称等隐私信息，请妥善保管**
- 定时调度程序需要保持运行状态才能在18:00自动执行
- 日志文件按日期自动创建，存储在 `logs/` 目录中
- 可以通过日志文件监控程序运行状态和排查问题