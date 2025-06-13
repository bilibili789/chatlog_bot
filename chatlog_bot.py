import requests
import json
from datetime import datetime
import urllib.parse
import os
import logging
from dotenv import load_dotenv

class ChatLogBot:
    def __init__(self):
        # 设置日志器
        self.logger = logging.getLogger(__name__)
        
        # 加载环境变量
        load_dotenv()
        
        # 加载配置文件
        self.load_config()
        
        # 从环境变量获取敏感数据
        self.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
        self.feishu_webhook = os.getenv('FEISHU_WEBHOOK')
        
        # 验证必要的环境变量
        if not self.deepseek_api_key:
            raise ValueError("DEEPSEEK_API_KEY 环境变量未设置")
        if not self.feishu_webhook:
            raise ValueError("FEISHU_WEBHOOK 环境变量未设置")
        
        # 获取今天的日期
        self.today = datetime.now().strftime("%Y-%m-%d")
    
    def load_config(self):
        """加载配置文件"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.chatlog_api_base = config['chatlog_api_base']
            self.deepseek_base_url = config['deepseek_base_url']
            self.deepseek_model = config['deepseek_model']
            self.talkers = config['talkers']
            self.deepseek_config = config['deepseek_config']
            
            self.logger.info("配置文件加载成功")
        except FileNotFoundError:
            raise FileNotFoundError("config.json 配置文件未找到")
        except json.JSONDecodeError:
            raise ValueError("config.json 配置文件格式错误")
        except KeyError as e:
            raise KeyError(f"配置文件缺少必要的配置项: {e}")
    
    def truncate_text(self, text, max_length=200, prefix=""):
        """缩略显示长文本"""
        if not text:
            return text
        
        text_str = str(text)
        if len(text_str) <= max_length:
            return f"{prefix}{text_str}" if prefix else text_str
        
        truncated = text_str[:max_length]
        return f"{prefix}{truncated}... (共{len(text_str)}字符)" if prefix else f"{truncated}... (共{len(text_str)}字符)"
    
    def get_chatlog(self, talker):
        """获取指定群组的聊天日志"""
        try:
            # URL编码talker参数
            encoded_talker = urllib.parse.quote(talker)
            url = f"{self.chatlog_api_base}?time={self.today}&talker={encoded_talker}"
            
            self.logger.info(f"请求URL: {url}")
            self.logger.debug(f"原始talker: {talker}")
            self.logger.debug(f"编码后talker: {encoded_talker}")
            
            response = requests.get(url)
            self.logger.info(f"响应状态码: {response.status_code}")
            self.logger.debug(f"响应头: {response.headers}")
            self.logger.info(f"响应内容长度: {len(response.text)}")
            self.logger.debug(f"响应内容预览: {self.truncate_text(response.text, 150)}")
            
            if response.status_code == 200:
                if response.text.strip():
                    self.logger.info(f"chatlog默认返回格式为文本类型，作为纯文本处理")
                    self.logger.debug(f"文本内容预览: {self.truncate_text(response.text, 200)}")
                    return response.text.strip()
                else:
                    self.logger.warning("响应内容为空")
                    return None
            else:
                self.logger.error(f"获取 {talker} 聊天日志失败：{response.status_code}")
                self.logger.error(f"错误响应内容: {self.truncate_text(response.text, 300)}")
                return None
        except Exception as e:
            self.logger.error(f"获取 {talker} 聊天日志异常：{str(e)}")
            import traceback
            self.logger.error(f"详细错误信息: {traceback.format_exc()}")
            return None
    
    def create_summary_prompt(self, talker, chatlog_data):
        """构造总结提示词"""
        prompt = f"""talker：{talker}
Time：{self.today}

请帮我将 "{talker}" 在"{self.today}" 的群聊内容总结成一个群聊报告，包含不多于5个的话题的总结（如果还有更多话题，可以在后面简单补充）。每个话题包含以下内容：  
- 话题名（50字以内，带序号1️⃣2️⃣3️⃣，同时附带热度，以🔥数量表示）  
- 参与者（不超过5个人，将重复的人名去重）  
- 时间段（从几点到几点）  
- 过程（50到200字左右）  
- 评价（50字以下）  
- 分割线： ------------  

另外有以下要求：  
1. 每个话题结束使用 ------------ 分割  
2. 使用中文冒号  
3. 无需大标题  
4. 开始给出本群讨论风格的整体评价，例如活跃、太水、太黄、太暴力、话题不集中、无聊诸如此类

群聊内容：
{chatlog_data if isinstance(chatlog_data, str) else json.dumps(chatlog_data, ensure_ascii=False, indent=2)}"""
        
        return prompt
    
    def call_deepseek(self, prompt):
        """调用DeepSeek API进行总结"""
        try:
            url = f"{self.deepseek_base_url}/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.deepseek_model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": self.deepseek_config["temperature"],
                "max_tokens": self.deepseek_config["max_tokens"]
            }
            
            self.logger.info(f"调用DeepSeek API: {url}")
            self.logger.debug(f"请求数据大小: {len(json.dumps(data))} 字符")
            self.logger.debug(f"提示词长度: {len(prompt)} 字符")
            
            response = requests.post(url, headers=headers, json=data)
            self.logger.info(f"DeepSeek响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                self.logger.info(f"DeepSeek返回内容长度: {len(content)} 字符")
                self.logger.debug(f"DeepSeek返回内容预览: {self.truncate_text(content, 100)}")
                
                # 清理markdown格式，移除**
                cleaned_content = content.replace("**", "").replace("###", "")
                self.logger.info(f"清理后内容长度: {len(cleaned_content)} 字符")
                self.logger.debug(f"清理后内容预览: {self.truncate_text(cleaned_content, 100)}")
                
                return cleaned_content
            else:
                self.logger.error(f"调用DeepSeek API失败：{response.status_code}")
                self.logger.error(f"错误响应: {self.truncate_text(response.text, 300)}")
                return None
        except Exception as e:
            self.logger.error(f"调用DeepSeek API异常：{str(e)}")
            import traceback
            self.logger.error(f"详细错误信息: {traceback.format_exc()}")
            return None
    
    def send_to_feishu(self, message):
        """发送消息到飞书群"""
        try:
            payload = {
                "msg_type": "text",
                "content": {
                    "text": message
                }
            }
            
            self.logger.info(f"发送飞书消息，内容长度: {len(message)} 字符")
            self.logger.debug(f"飞书Webhook: {self.feishu_webhook}")
            self.logger.debug(f"消息内容预览: {self.truncate_text(message, 100)}")
            
            response = requests.post(
                self.feishu_webhook,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload)
            )
            
            self.logger.info(f"飞书响应状态码: {response.status_code}")
            self.logger.debug(f"飞书响应内容: {self.truncate_text(response.text, 200)}")
            
            if response.status_code == 200:
                self.logger.info("消息发送到飞书成功！")
                return True
            else:
                self.logger.error(f"发送到飞书失败：{response.status_code}, {response.text}")
                return False
        except Exception as e:
            self.logger.error(f"发送到飞书异常：{str(e)}")
            import traceback
            self.logger.error(f"详细错误信息: {traceback.format_exc()}")
            return False
    
    def test_api_connection(self):
        """测试API连接"""
        self.logger.info("=== 测试API连接 ===")
        
        # 测试聊天日志API
        test_url = f"{self.chatlog_api_base}?time={self.today}&talker=test"
        try:
            response = requests.get(test_url, timeout=10)
            self.logger.info(f"聊天日志API连接测试: {response.status_code}")
        except Exception as e:
            self.logger.warning(f"聊天日志API连接失败: {str(e)}")
        
        # 测试DeepSeek API
        try:
            test_data = {
                "model": self.deepseek_model,
                "messages": [{"role": "user", "content": "测试"}],
                "max_tokens": 10
            }
            response = requests.post(
                f"{self.deepseek_base_url}/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.deepseek_api_key}", "Content-Type": "application/json"},
                json=test_data,
                timeout=10
            )
            self.logger.info(f"DeepSeek API连接测试: {response.status_code}")
        except Exception as e:
            self.logger.warning(f"DeepSeek API连接失败: {str(e)}")
        
        self.logger.info("===================")

    def process_single_talker(self, talker):
        """处理单个群组的聊天日志"""
        self.logger.info(f"开始处理群组：{talker}")
        
        # 1. 获取聊天日志
        chatlog_data = self.get_chatlog(talker)
        if not chatlog_data:
            self.logger.warning(f"跳过群组 {talker}：无法获取聊天日志")
            return False
        
        # 检查数据是否为空或无效
        if isinstance(chatlog_data, str):
            if len(chatlog_data.strip()) == 0:
                self.logger.warning(f"跳过群组 {talker}：聊天日志文本为空")
                return False
            self.logger.info(f"成功获取聊天日志，文本长度: {len(chatlog_data)} 字符")
            self.logger.debug(f"聊天日志预览: {self.truncate_text(chatlog_data, 200)}")
        elif isinstance(chatlog_data, dict) and not chatlog_data:
            self.logger.warning(f"跳过群组 {talker}：聊天日志为空")
            return False
        elif isinstance(chatlog_data, list) and len(chatlog_data) == 0:
            self.logger.warning(f"跳过群组 {talker}：聊天日志列表为空")
            return False
        else:
            self.logger.info(f"成功获取聊天日志，数据类型: {type(chatlog_data)}")
            if isinstance(chatlog_data, list):
                self.logger.info(f"聊天记录数量: {len(chatlog_data)}")
            elif isinstance(chatlog_data, dict):
                self.logger.info(f"聊天日志字典键: {list(chatlog_data.keys())}")
        
        # 2. 构造提示词
        prompt = self.create_summary_prompt(talker, chatlog_data)
        
        # 3. 调用大模型总结
        summary = self.call_deepseek(prompt)
        if not summary:
            self.logger.warning(f"跳过群组 {talker}：无法获取总结")
            return False
        
        # 4. 发送到飞书
        full_message = f"📊 群聊日报 - {talker} ({self.today})\n\n{summary}"
        success = self.send_to_feishu(full_message)
        
        if success:
            self.logger.info(f"群组 {talker} 处理完成")
        
        return success
    
    def run(self):
        """运行主程序"""
        self.logger.info(f"开始处理 {self.today} 的群聊日志")
        self.logger.info(f"需要处理的群组数量：{len(self.talkers)}")
        self.logger.info(f"群组列表：{self.talkers}")
        
        # 先测试API连接
        self.test_api_connection()
        
        success_count = 0
        
        for talker in self.talkers:
            if self.process_single_talker(talker):
                success_count += 1
            self.logger.info("-" * 50)
        
        self.logger.info(f"处理完成！成功处理 {success_count}/{len(self.talkers)} 个群组")

if __name__ == "__main__":
    bot = ChatLogBot()
    bot.run() 