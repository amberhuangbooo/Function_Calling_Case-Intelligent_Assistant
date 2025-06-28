# Function Calling 案例：智能助手

这是一个展示如何实现基于大模型的 Function Calling 功能的简单案例。Function Calling 允许大模型自动调用预定义的工具函数，以完成特定任务并增强模型能力。本项目通过集成多种实用工具（如查询天气、搜索新闻、股票分析和发送消息等），演示了如何构建一个功能强大的智能助手。

## 功能概述

  * **天气查询** ：获取全球任意城市的实时天气信息，包括温度、湿度、风速等详细数据。
  * **新闻搜索** ：根据关键词搜索最新的新闻资讯，按类别（如科技、体育等）筛选，并返回新闻标题、简介和链接。
  * **股票分析** ：分析股票的基本信息和价格趋势，提供投资参考数据，如市值、市盈率和近期价格波动。
  * **消息发送** ：通过微信或其他渠道向指定用户发送个性化消息。

## 代码结构

  * `RealLLMFunctionCalling.py` ：主程序文件，定义了核心类和函数，包括大模型初始化、对话管理、函数调用逻辑等。
  * `函数定义部分` ：预定义了多种工具函数，每个函数都有明确的参数要求和返回格式，确保大模型能正确调用并处理结果。
  * `交互模式` ：支持用户与智能助手进行持续对话，输入问题后，助手会自动判断是否需要调用函数来完成任务。

## 环境配置

在运行本项目前，请确保已设置以下环境变量：

```env
OPENAI_API_KEY=your_openai_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
NEWS_API_KEY=your_news_api_key
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
```

**API 密钥获取地址：**

  * OpenAI：[https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
  * OpenWeatherMap：[https://openweathermap.org/api](https://openweathermap.org/api)
  * NewsAPI：[https://newsapi.org/](https://newsapi.org/)

## 使用示例

### 示例 1：发送微信消息

  * **用户问题** ：给 crush 发送微信信息：“晚安，宝贝💤”。
  * **助手处理流程** ：调用`send_message_with_weixin`函数，传入用户名和消息内容，执行发送操作后，向用户反馈发送成功的信息。

### 示例 2：查询北京天气

  * **用户问题** ：北京今天的天气怎么样？
  * **助手处理流程** ：调用`get_real_weather`函数，传入城市名称“北京”，获取实时天气数据后，以清晰的格式返回给用户。

### 示例 3：搜索人工智能新闻

  * **用户问题** ：搜索一下最新的人工智能新闻。
  * **助手处理流程** ：调用`search_news`函数，以“人工智能”为关键词搜索新闻，返回相关新闻的标题、简介和链接。

### 示例 4：分析苹果公司股票

  * **用户问题** ：帮我分析一下苹果公司（AAPL）的股票情况。
  * **助手处理流程** ：调用`analyze_stock`函数，传入股票代码“AAPL”，分析其基本信息和价格趋势，为用户提供高质量的股票分析结果。

## 项目扩展

本项目提供了基础的 Function Calling 框架和示例，你可以根据实际需求进行扩展：

  * **添加新工具** ：定义更多符合 Moonshot JSON Schema 的工具函数，如支付接口、数据可视化工具等，以满足不同业务场景。
  * **优化对话逻辑** ：调整大模型的参数（如温度值、token 限制等），改进对话的流畅性和准确性。
  * **增强错误处理** ：完善函数调用失败时的重试机制和用户反馈，提高系统的健壮性。

通过这个案例，你可以快速掌握 Function Calling 的实现原理和应用场景，为开发更智能、实用的 AI 应用奠定基础。
