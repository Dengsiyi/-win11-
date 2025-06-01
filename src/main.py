#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
按键精灵 - Windows 11自动化工具
功能：记录和重放键盘鼠标操作，类似于按键精灵
"""

import os
import sys
import time
import threading
import customtkinter as ctk
from gui import AnJianApp
from config_manager import ConfigManager

def main():
    """主程序入口"""
    # 设置主题
    ctk.set_appearance_mode("System")  # 系统主题（自动适应深色/浅色模式）
    ctk.set_default_color_theme("blue")  # 默认颜色主题
    
    # 创建配置管理器
    config_manager = ConfigManager()
    
    # 创建应用程序实例
    app = AnJianApp(config_manager)
    
    # 启动应用程序
    app.mainloop()

if __name__ == "__main__":
    main()
