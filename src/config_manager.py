#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
按键精灵 - 配置管理器
负责管理应用程序配置，包括自定义快捷键
"""

import os
import json

# 默认配置
DEFAULT_CONFIG = {
    "hotkeys": {
        "record_toggle": "F9",
        "play_toggle": "F10",
        "new_script": "Control-n",
        "open_script": "Control-o",
        "save_script": "Control-s",
        "save_as_script": "Control-Shift-s",
        "stop_all": "Escape"
    },
    "global_hotkeys": True  # 是否启用全局热键
}

class ConfigManager:
    """配置管理类"""
    
    def __init__(self, config_file="config.json"):
        """初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self):
        """加载配置
        
        Returns:
            dict: 配置字典
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    
                # 确保所有默认配置项都存在
                for key, value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                    elif isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            if sub_key not in config[key]:
                                config[key][sub_key] = sub_value
                                
                return config
            except Exception as e:
                print(f"加载配置文件错误: {str(e)}")
                return DEFAULT_CONFIG.copy()
        else:
            return DEFAULT_CONFIG.copy()
            
    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置文件错误: {str(e)}")
            
    def get_hotkey(self, action):
        """获取指定操作的快捷键
        
        Args:
            action: 操作名称
            
        Returns:
            str: 快捷键
        """
        return self.config["hotkeys"].get(action, DEFAULT_CONFIG["hotkeys"].get(action, ""))
        
    def set_hotkey(self, action, hotkey):
        """设置指定操作的快捷键
        
        Args:
            action: 操作名称
            hotkey: 快捷键
        """
        if "hotkeys" not in self.config:
            self.config["hotkeys"] = {}
            
        self.config["hotkeys"][action] = hotkey
        self.save_config()
        
    def get_all_hotkeys(self):
        """获取所有快捷键
        
        Returns:
            dict: 快捷键字典
        """
        return self.config.get("hotkeys", {}).copy()
        
    def reset_hotkeys(self):
        """重置所有快捷键为默认值"""
        self.config["hotkeys"] = DEFAULT_CONFIG["hotkeys"].copy()
        self.save_config()
        
    def is_global_hotkeys_enabled(self):
        """检查是否启用全局热键
        
        Returns:
            bool: 是否启用全局热键
        """
        return self.config.get("global_hotkeys", DEFAULT_CONFIG.get("global_hotkeys", True))
        
    def set_global_hotkeys_enabled(self, enabled):
        """设置是否启用全局热键
        
        Args:
            enabled: 是否启用全局热键
        """
        self.config["global_hotkeys"] = bool(enabled)
        self.save_config()
