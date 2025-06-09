#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import schedule
import time
import logging
import os
from datetime import datetime
from chatlog_bot import ChatLogBot

class ScheduledChatLogBot:
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
    def setup_logging(self):
        """设置日志配置"""
        # 创建logs目录
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # 设置日志格式
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        
        # 配置根日志器
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            datefmt=date_format,
            handlers=[
                # 文件处理器 - 按日期命名
                logging.FileHandler(
                    f'logs/chatlog_bot_{datetime.now().strftime("%Y%m%d")}.log',
                    encoding='utf-8'
                ),
                # 控制台处理器
                logging.StreamHandler()
            ]
        )
        
    def run_chatlog_bot(self):
        """运行聊天日志机器人"""
        self.logger.info("=" * 60)
        self.logger.info("开始执行定时任务 - 聊天日志机器人")
        self.logger.info(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 初始化并运行机器人
            bot = ChatLogBot()
            self.logger.info("聊天日志机器人初始化成功")
            
            # 执行任务
            bot.run()
            
            self.logger.info("聊天日志机器人执行完成")
            
        except Exception as e:
            self.logger.error(f"聊天日志机器人执行失败: {str(e)}")
            self.logger.error(f"错误详情: ", exc_info=True)
        
        self.logger.info("定时任务执行结束")
        self.logger.info("=" * 60)
    
    def test_run(self):
        """测试运行（立即执行一次）"""
        self.logger.info("执行测试运行...")
        self.run_chatlog_bot()
    
    def start_scheduler(self):
        """启动定时调度器"""
        self.logger.info("启动定时调度器")
        self.logger.info("设置每天18:00执行聊天日志机器人任务")
        
        # 设置定时任务 - 每天18点执行
        schedule.every().day.at("18:00").do(self.run_chatlog_bot)
        
        # 显示下次执行时间
        next_run = schedule.next_run()
        self.logger.info(f"下次执行时间: {next_run}")
        
        self.logger.info("定时调度器启动成功，程序将持续运行...")
        self.logger.info("按 Ctrl+C 停止程序")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
                
        except KeyboardInterrupt:
            self.logger.info("接收到停止信号，正在关闭程序...")
        except Exception as e:
            self.logger.error(f"调度器运行出错: {str(e)}", exc_info=True)
        finally:
            self.logger.info("程序已停止")

def print_menu():
    """打印菜单"""
    print("\n" + "=" * 50)
    print("聊天日志机器人 - 定时调度程序")
    print("=" * 50)
    print("1. 启动定时调度器（每天18:00执行）")
    print("2. 立即执行一次（测试运行）")
    print("3. 查看日志文件")
    print("4. 退出程序")
    print("=" * 50)

def show_logs():
    """显示最新的日志文件内容"""
    logs_dir = 'logs'
    if not os.path.exists(logs_dir):
        print("日志目录不存在")
        return
    
    log_files = [f for f in os.listdir(logs_dir) if f.endswith('.log')]
    if not log_files:
        print("没有找到日志文件")
        return
    
    # 显示最新的日志文件
    latest_log = sorted(log_files)[-1]
    log_path = os.path.join(logs_dir, latest_log)
    
    print(f"\n显示最新日志文件: {latest_log}")
    print("-" * 50)
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # 显示最后30行
            for line in lines[-30:]:
                print(line.rstrip())
    except Exception as e:
        print(f"读取日志文件失败: {e}")

def main():
    """主程序入口"""
    scheduler = ScheduledChatLogBot()
    
    while True:
        print_menu()
        choice = input("\n请选择操作 (1-4): ").strip()
        
        if choice == '1':
            print("\n启动定时调度器...")
            scheduler.start_scheduler()
            break
            
        elif choice == '2':
            print("\n执行测试运行...")
            scheduler.test_run()
            input("\n按回车键继续...")
            
        elif choice == '3':
            show_logs()
            input("\n按回车键继续...")
            
        elif choice == '4':
            print("\n退出程序")
            break
            
        else:
            print("\n无效选择，请重新输入")

if __name__ == "__main__":
    main() 