#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
按键精灵 - 脚本管理器
负责脚本的保存、加载和解析
"""

import os
import json
import time

class ScriptManager:
    """脚本管理类"""
    
    def __init__(self):
        """初始化脚本管理器"""
        pass
        
    def format_action(self, action):
        """将操作格式化为可读的文本
        
        Args:
            action: 要格式化的操作
            
        Returns:
            str: 格式化后的文本
        """
        action_type = action.get("type", "")
        time_str = f"{action.get('time', 0):.3f}"
        
        if action_type == "key_press":
            key = action.get("key", "")
            return f"[{time_str}] KEY_PRESS: {key}"
            
        elif action_type == "key_release":
            key = action.get("key", "")
            return f"[{time_str}] KEY_RELEASE: {key}"
            
        elif action_type == "mouse_move":
            x = action.get("x", 0)
            y = action.get("y", 0)
            return f"[{time_str}] MOUSE_MOVE: {x}, {y}"
            
        elif action_type == "mouse_click":
            x = action.get("x", 0)
            y = action.get("y", 0)
            button = action.get("button", "left")
            pressed = "DOWN" if action.get("pressed", False) else "UP"
            return f"[{time_str}] MOUSE_{pressed}: {button} at {x}, {y}"
            
        elif action_type == "mouse_scroll":
            x = action.get("x", 0)
            y = action.get("y", 0)
            dx = action.get("dx", 0)
            dy = action.get("dy", 0)
            direction = "UP" if dy > 0 else "DOWN"
            return f"[{time_str}] MOUSE_SCROLL_{direction}: at {x}, {y}"
            
        return f"[{time_str}] UNKNOWN: {action}"
        
    def parse_script(self, script_text):
        """解析脚本文本为操作序列
        
        Args:
            script_text: 要解析的脚本文本
            
        Returns:
            list: 操作序列
        """
        if not script_text:
            return []
            
        actions = []
        lines = script_text.strip().split("\n")
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
                
            try:
                # 解析时间戳
                time_start = line.find("[") + 1
                time_end = line.find("]")
                if time_start <= 0 or time_end <= 0:
                    continue
                    
                time_str = line[time_start:time_end].strip()
                action_time = float(time_str)
                
                # 解析操作类型和参数
                action_part = line[time_end + 1:].strip()
                if not action_part:
                    continue
                    
                # 分割操作类型和参数
                parts = action_part.split(":", 1)
                if len(parts) != 2:
                    continue
                    
                action_type = parts[0].strip()
                params_str = parts[1].strip()
                
                # 根据操作类型解析参数
                if action_type == "KEY_PRESS":
                    key = params_str
                    actions.append({
                        "type": "key_press",
                        "key": key,
                        "time": action_time
                    })
                    
                elif action_type == "KEY_RELEASE":
                    key = params_str
                    actions.append({
                        "type": "key_release",
                        "key": key,
                        "time": action_time
                    })
                    
                elif action_type == "MOUSE_MOVE":
                    coords = params_str.split(",")
                    if len(coords) == 2:
                        x = int(float(coords[0].strip()))
                        y = int(float(coords[1].strip()))
                        actions.append({
                            "type": "mouse_move",
                            "x": x,
                            "y": y,
                            "time": action_time
                        })
                        
                elif action_type in ["MOUSE_DOWN", "MOUSE_UP"]:
                    # 格式: MOUSE_DOWN: left at 100, 200
                    parts = params_str.split(" at ")
                    if len(parts) == 2:
                        button = parts[0].strip()
                        coords = parts[1].split(",")
                        if len(coords) == 2:
                            x = int(float(coords[0].strip()))
                            y = int(float(coords[1].strip()))
                            actions.append({
                                "type": "mouse_click",
                                "button": button,
                                "pressed": action_type == "MOUSE_DOWN",
                                "x": x,
                                "y": y,
                                "time": action_time
                            })
                            
                elif action_type in ["MOUSE_SCROLL_UP", "MOUSE_SCROLL_DOWN"]:
                    # 格式: MOUSE_SCROLL_UP: at 100, 200
                    parts = params_str.split(" at ")
                    if len(parts) == 2:
                        coords = parts[1].split(",")
                        if len(coords) == 2:
                            x = int(float(coords[0].strip()))
                            y = int(float(coords[1].strip()))
                            dy = 1 if action_type == "MOUSE_SCROLL_UP" else -1
                            actions.append({
                                "type": "mouse_scroll",
                                "x": x,
                                "y": y,
                                "dx": 0,
                                "dy": dy,
                                "time": action_time
                            })
            except Exception as e:
                print(f"解析行错误: {line} - {str(e)}")
                
        # 按时间排序
        actions.sort(key=lambda x: x.get("time", 0))
        
        return actions
        
    def save_script(self, file_path, script_text):
        """保存脚本到文件
        
        Args:
            file_path: 文件路径
            script_text: 脚本文本
        """
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(script_text)
            
    def load_script(self, file_path):
        """从文件加载脚本
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: 脚本文本
        """
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
            
    def export_to_json(self, actions, file_path):
        """将操作序列导出为JSON格式
        
        Args:
            actions: 操作序列
            file_path: 文件路径
        """
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(actions, f, indent=2)
            
    def import_from_json(self, file_path):
        """从JSON文件导入操作序列
        
        Args:
            file_path: 文件路径
            
        Returns:
            list: 操作序列
        """
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
