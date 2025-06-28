import openai
import requests
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

class RealLLMFunctionCalling:
    """
    基于真实大模型API的Function Calling实现
    支持OpenAI GPT-4、Claude等多种模型
    """
    
    def __init__(self, api_key: str, base_url: str, model: str = "gpt-4-turbo-preview"):
        """
        初始化大模型客户端
        
        Args:
            api_key: OpenAI API密钥
            model: 使用的模型名称
        """
        self.client = openai.OpenAI(
            base_url=base_url,
            api_key=api_key)
        self.model = model
        self.conversation_history = []  # 保存对话历史
        
        # 定义可用的函数工具
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_real_weather",
                    "description": "获取指定城市的实时天气信息，包括温度、湿度、风速等详细数据",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "要查询天气的城市名称，支持中英文"
                            },
                            "units": {
                                "type": "string",
                                "enum": ["metric", "imperial"],
                                "description": "温度单位，metric为摄氏度，imperial为华氏度",
                                "default": "metric"
                            }
                        },
                        "required": ["city"]
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "search_news",
                    "description": "搜索最新的新闻信息，可以按照关键词、时间范围等条件筛选",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜索关键词，支持中英文"
                            },
                            "category": {
                                "type": "string",
                                "enum": ["general", "business", "entertainment", "health", "science", "sports", "technology"],
                                "description": "新闻分类",
                                "default": "general"
                            },
                            "country": {
                                "type": "string",
                                "description": "国家代码，如cn、us等",
                                "default": "cn"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_stock",
                    "description": "分析股票的基本信息和价格趋势，提供投资参考",
                    "parameters": {
                        "type": "object", 
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "股票代码，如AAPL、TSLA等"
                            },
                            "period": {
                                "type": "string",
                                "enum": ["1d", "5d", "1mo", "3mo", "6mo", "1y"],
                                "description": "分析时间周期",
                                "default": "1mo"
                            }
                        },
                        "required": ["symbol"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "send_email",
                    "description": "发送电子邮件给指定收件人",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "to": {
                                "type": "string",
                                "description": "收件人邮箱地址"
                            },
                            "subject": {
                                "type": "string", 
                                "description": "邮件主题"
                            },
                            "content": {
                                "type": "string",
                                "description": "邮件正文内容"
                            }
                        },
                        "required": ["to", "subject", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "send_message_with_weixin",
                    "description": "发送微信信息给指定用户",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_name": {
                                "type": "string",
                                "description": "指定用户的用户名字"
                            },
                            "content": {
                                "type": "string",
                                "description": "发送内容"
                            }
                        },
                        "required": ["user_name", "content"]
                    }
                }
            }
        ]

    def get_real_weather(self, city: str, units: str = "metric") -> Dict[str, Any]:
        """
        调用真实的天气API获取天气信息
        这里使用OpenWeatherMap API作为示例
        """
        try:
            # 注意：你需要在OpenWeatherMap注册并获取API密钥
            api_key = os.getenv("OPENWEATHER_API_KEY", "your_openweather_api_key")
            
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": city,
                "appid": api_key,
                "units": units,
                "lang": "zh_cn"  # 中文描述
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # 解析天气数据
            weather_info = {
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": round(data["main"]["temp"], 1),
                "feels_like": round(data["main"]["feels_like"], 1),
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
                "visibility": data.get("visibility", "未知") / 1000 if data.get("visibility") else "未知",
                "units": "°C" if units == "metric" else "°F",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return {
                "success": True,
                "data": weather_info
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"网络请求失败: {str(e)}"
            }
        except KeyError as e:
            return {
                "success": False,
                "error": f"API响应格式错误: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"未知错误: {str(e)}"
            }

    def search_news(self, query: str, category: str = "general", country: str = "cn") -> Dict[str, Any]:
        """
        搜索新闻信息
        这里使用NewsAPI作为示例
        """
        try:
            # 注意：你需要在NewsAPI注册并获取API密钥
            api_key = os.getenv("NEWS_API_KEY", "your_news_api_key")
            
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "apiKey": api_key,
                "language": "zh" if country == "cn" else "en",
                "sortBy": "publishedAt",
                "pageSize": 5  # 限制返回结果数量
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # 解析新闻数据
            articles = []
            for article in data.get("articles", [])[:5]:  # 只取前5条
                articles.append({
                    "title": article["title"],
                    "description": article["description"],
                    "url": article["url"],
                    "source": article["source"]["name"],
                    "published_at": article["publishedAt"]
                })
            
            return {
                "success": True,
                "data": {
                    "query": query,
                    "total_results": data.get("totalResults", 0),
                    "articles": articles,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"新闻搜索失败: {str(e)}"
            }

    def analyze_stock(self, symbol: str, period: str = "1mo") -> Dict[str, Any]:
        """
        分析股票信息
        这里使用Yahoo Finance API作为示例
        """
        try:
            # 使用yfinance库（需要安装：pip install yfinance）
            import yfinance as yf
            
            stock = yf.Ticker(symbol)
            
            # 获取股票基本信息
            info = stock.info
            
            # 获取历史价格数据
            hist = stock.history(period=period)
            
            if hist.empty:
                return {
                    "success": False,
                    "error": f"未找到股票代码 {symbol} 的数据"
                }
            
            # 计算基本统计信息
            current_price = hist['Close'].iloc[-1]
            price_change = hist['Close'].iloc[-1] - hist['Close'].iloc[-2]
            price_change_percent = (price_change / hist['Close'].iloc[-2]) * 100
            
            analysis_result = {
                "symbol": symbol,
                "company_name": info.get("longName", symbol),
                "current_price": round(current_price, 2),
                "price_change": round(price_change, 2),
                "price_change_percent": round(price_change_percent, 2),
                "volume": hist['Volume'].iloc[-1],
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "52_week_high": round(hist['High'].max(), 2),
                "52_week_low": round(hist['Low'].min(), 2),
                "analysis_period": period,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return {
                "success": True,
                "data": analysis_result
            }
            
        except ImportError:
            return {
                "success": False,
                "error": "需要安装yfinance库：pip install yfinance"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"股票分析失败: {str(e)}"
            }

    def send_email(self, to: str, subject: str, content: str) -> Dict[str, Any]:
        """
        发送邮件功能
        这里使用SMTP协议发送邮件
        """
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # 邮件服务器配置（这里以Gmail为例）
            smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            sender_email = os.getenv("SENDER_EMAIL", "your_email@gmail.com")
            sender_password = os.getenv("SENDER_PASSWORD", "your_app_password")
            
            # 创建邮件
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = to
            message["Subject"] = subject
            
            # 添加邮件正文
            message.attach(MIMEText(content, "plain", "utf-8"))
            
            # 发送邮件
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(message)
            
            return {
                "success": True,
                "data": {
                    "to": to,
                    "subject": subject,
                    "sent_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "message": "邮件发送成功"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"邮件发送失败: {str(e)}"
            }
        
    def send_message_with_weixin(self, user_name: str, content: str) -> Dict[str, Any]:
        """
        发送微信信息功能
        """
        try:
            print("*"*20)
            print(f"{content}")
            print("*"*20)
            
            return {
                "success": True,
                "data": {
                    "user_name": user_name,
                    "sent_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "message": "信息发送成功"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"信息发送失败: {str(e)}"
            }

    def execute_function_call(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行具体的函数调用
        这是连接大模型决策和实际工具执行的桥梁
        """
        print(f"🔧 执行函数: {function_name}")
        print(f"📋 参数: {arguments}")
        
        function_map = {
            "get_real_weather": self.get_real_weather,
            "search_news": self.search_news,
            "analyze_stock": self.analyze_stock,
            "send_email": self.send_email,
            "send_message_with_weixin": self.send_message_with_weixin
        }
        
        if function_name not in function_map:
            return {
                "success": False,
                "error": f"未知函数: {function_name}"
            }
        
        try:
            # 执行函数并返回结果
            result = function_map[function_name](**arguments)
            print(f"✅ 函数执行完成: {result.get('success', False)}")
            return result
            
        except TypeError as e:
            return {
                "success": False,
                "error": f"函数参数错误: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"函数执行异常: {str(e)}"
            }

    def chat_with_function_calling(self, user_message: str, max_retries: int = 3) -> str:
        """
        与大模型进行支持函数调用的对话
        这是整个系统的核心方法
        """
        print(f"👤 用户: {user_message}")
        print("-" * 60)
        
        # 将用户消息添加到对话历史
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                print(f"🤖 调用大模型 (尝试 {retry_count + 1}/{max_retries})")
                
                # 调用大模型API
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.conversation_history,
                    tools=self.tools,
                    tool_choice="auto",  # 让模型自动决定是否使用工具
                    temperature=0.7,
                    max_tokens=1500
                )
                
                assistant_message = response.choices[0].message
                print("$$$", assistant_message)
                
                # 检查是否需要调用函数
                if assistant_message.tool_calls:
                    print(f"🔍 模型决定调用 {len(assistant_message.tool_calls)} 个函数")
                    
                    # 将助手的消息（包含函数调用请求）添加到历史
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": assistant_message.content,
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "type": tool_call.type,
                                "function": {
                                    "name": tool_call.function.name,
                                    "arguments": tool_call.function.arguments
                                }
                            }
                            for tool_call in assistant_message.tool_calls
                        ]
                    })
                    
                    # 执行所有函数调用
                    for tool_call in assistant_message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        
                        # 执行函数
                        function_result = self.execute_function_call(function_name, function_args)
                        
                        # 将函数执行结果添加到对话历史
                        self.conversation_history.append({
                            "role": "tool",
                            "content": json.dumps(function_result, ensure_ascii=False),
                            "tool_call_id": tool_call.id
                        })
                    
                    # 再次调用模型，让它基于函数结果生成最终回复
                    print("🔄 基于函数结果生成最终回复...")
                    final_response = self.client.chat.completions.create(
                        model=self.model,
                        messages=self.conversation_history,
                        temperature=0.7,
                        max_tokens=1500
                    )
                    
                    final_message = final_response.choices[0].message.content
                    
                    # 将最终回复添加到历史
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": final_message
                    })
                    
                    print(f"✨ 最终回复: {final_message}")
                    return final_message
                
                else:
                    # 没有函数调用，直接返回模型回复
                    final_message = assistant_message.content
                    
                    # 将回复添加到历史
                    self.conversation_history.append({
                        "role": "assistant", 
                        "content": final_message
                    })
                    
                    print(f"💬 直接回复: {final_message}")
                    return final_message
                
            except openai.RateLimitError:
                retry_count += 1
                wait_time = 2 ** retry_count
                print(f"⚠️ API调用频率限制，等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
                
            except openai.APITimeoutError:
                retry_count += 1
                print(f"⚠️ API调用超时，重试中...")
                
            except Exception as e:
                print(f"❌ API调用失败: {str(e)}")
                return f"抱歉，我遇到了技术问题：{str(e)}"
        
        return "抱歉，在多次尝试后仍无法完成您的请求，请稍后再试。"

    def start_interactive_chat(self):
        """
        启动交互式对话模式
        让用户可以持续与AI助手对话
        """
        print("🎉 欢迎使用Function Calling智能助手！")
        print("💡 我可以帮您：查询天气、搜索新闻、分析股票、发送邮件等")
        print("❓ 输入 'quit' 或 'exit' 退出对话")
        print("=" * 60)
        
        while True:
            try:
                user_input = input("\n您的问题: ").strip()
                
                if user_input.lower() in ['quit', 'exit', '退出', '再见']:
                    print("👋 再见！感谢使用智能助手！")
                    break
                
                if not user_input:
                    print("请输入您的问题...")
                    continue
                
                # 处理用户输入
                response = self.chat_with_function_calling(user_input)
                print(f"\n🤖 助手: {response}")
                print("=" * 60)
                
            except KeyboardInterrupt:
                print("\n\n👋 检测到中断信号，正在退出...")
                break
            except Exception as e:
                print(f"\n❌ 发生错误: {str(e)}")


# 使用示例和配置说明
def main():
    """
    主函数：演示如何使用真实的Function Calling系统
    """
    print("📚 Function Calling 实际案例演示")
    print("=" * 50)
    
    # 重要：在实际使用前，你需要设置以下环境变量：
    print("""
    ⚙️ 使用前请设置以下环境变量：
    
    1. OPENAI_API_KEY=your_openai_api_key
    2. OPENWEATHER_API_KEY=your_openweather_api_key  
    3. NEWS_API_KEY=your_news_api_key
    4. SMTP_SERVER=smtp.gmail.com (邮件服务器)
    5. SMTP_PORT=587
    6. SENDER_EMAIL=your_email@gmail.com
    7. SENDER_PASSWORD=your_app_password
    
    📝 API密钥获取地址：
    - OpenAI: https://platform.openai.com/api-keys
    - OpenWeatherMap: https://openweathermap.org/api
    - NewsAPI: https://newsapi.org/
    """)
    
    # 检查必要的API密钥
    #openai_key = os.getenv("OPENAI_API_KEY")
    model = "moonshot-v1-8k"       # The LLM model to use
    base_url = "https://api.moonshot.cn/v1" # API endpoint URL
    api_key = "Your API key"                   # 
    #api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        print("💡 示例: export OPENAI_API_KEY='your-api-key-here'")
        return
    
    try:
        # 初始化Function Calling助手
        assistant = RealLLMFunctionCalling(
            api_key=api_key,
            base_url = base_url,
            model=model 
        )
        
        print("✅ 助手初始化成功！")

        # 启动交互模式
        start_interactive = 'yes' #input("\n🎮 是否启动交互模式？(y/n): ").lower().strip()
        if start_interactive in ['y', 'yes', '是']:
            assistant.start_interactive_chat()
        
        # # 演示一些测试用例
        # test_cases = [
        #     "给crush发送微信信息：晚安，宝贝💤"
        #     "北京今天的天气怎么样？",
        #     "搜索一下最新的人工智能新闻", 
        #     "帮我分析一下苹果公司(AAPL)的股票情况",
        #     "你好，请介绍一下你的功能"
        # ]
        
        # print("\n🧪 运行测试用例：")
        # for i, test_case in enumerate(test_cases, 1):
        #     print(f"\n--- 测试用例 {i} ---")
        #     response = assistant.chat_with_function_calling(test_case)
        #     print("=" * 50)
        
        
            
    except Exception as e:
        print(f"❌ 系统初始化失败: {str(e)}")
        print("💡 请检查API密钥和网络连接")


if __name__ == "__main__":
    main()
