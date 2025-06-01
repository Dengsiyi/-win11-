#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
按键精灵 - 记录器
负责记录用户的键盘和鼠标操作
"""

import time
import threading
from pynput import keyboard, mouse

class Recorder:
    """记录用户键盘和鼠标操作的类"""
    
    def __init__(self, config_manager=None):
        """初始化记录器"""
        self.recording = False
        self.start_time = 0
        self.keyboard_listener = None
        self.mouse_listener = None
        self.callback = None
        self.config_manager = config_manager
        self.stop_key = None
        self.last_key_time = 0
        self.key_threshold = 0.05  # 50毫秒内的按键被视为同一个操作
        
    def start_recording(self, callback=None):
        """开始记录
        
        Args:
            callback: 当有新动作被记录时调用的回调函数
        """
        if self.recording:
            return
            
        self.recording = True
        self.start_time = time.time()
        self.callback = callback
        
        # 获取停止录制的快捷键
        if self.config_manager:
            self.stop_key = self.config_manager.get_hotkey("record_toggle")
        else:
            self.stop_key = "F9"  # 默认值
        
        # 启动键盘监听器
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self.keyboard_listener.start()
        
        # 启动鼠标监听器
        self.mouse_listener = mouse.Listener(
            on_move=self._on_mouse_move,
            on_click=self._on_mouse_click,
            on_scroll=self._on_mouse_scroll
        )
        self.mouse_listener.start()
        
    def stop_recording(self):
        """停止记录"""
        if not self.recording:
            return
            
        self.recording = False
        
        # 停止监听器
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
            
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
            
    def _get_current_time(self):
        """获取当前时间（相对于记录开始的时间）"""
        return time.time() - self.start_time
        
    def _on_key_press(self, key):
        """键盘按键按下事件处理
        
        Args:
            key: 按下的键
        """
        if not self.recording:
            return
            
        try:
            # 尝试获取字符
            char = key.char
            key_name = char
        except AttributeError:
            # 特殊键
            key_name = str(key).replace("Key.", "")
            
        # 检查是否是停止录制的快捷键
        if self._is_stop_key(key_name):
            # 如果是停止键，不记录这个按键
            return
            
        # 检查按键时间间隔，避免重复记录
        current_time = self._get_current_time()
        if current_time - self.last_key_time < self.key_threshold:
            return
            
        self.last_key_time = current_time
            
        action = {
            "type": "key_press",
            "key": key_name,
            "time": current_time
        }
        
        if self.callback:
            self.callback(action)
            
    def _on_key_release(self, key):
        """键盘按键释放事件处理
        
        Args:
            key: 释放的键
        """
        if not self.recording:
            return
            
        try:
            # 尝试获取字符
            char = key.char
            key_name = char
        except AttributeError:
            # 特殊键
            key_name = str(key).replace("Key.", "")
            
        # 检查是否是停止录制的快捷键
        if self._is_stop_key(key_name):
            # 如果是停止键，不记录这个按键
            return
            
        # 检查按键时间间隔，避免重复记录
        current_time = self._get_current_time()
        if current_time - self.last_key_time < self.key_threshold:
            return
            
        self.last_key_time = current_time
            
        action = {
            "type": "key_release",
            "key": key_name,
            "time": current_time
        }
        
        if self.callback:
            self.callback(action)
            
    def _is_stop_key(self, key_name):
        """检查是否是停止录制的快捷键
        
        Args:
            key_name: 按键名称
            
        Returns:
            bool: 是否是停止键
        """
        # 检查空值
        if not self.stop_key or not key_name:
            return False
            
        # 确保key_name是字符串
        if not isinstance(key_name, str):
            try:
                key_name = str(key_name)
            except:
                return False
            
        # 处理组合键的情况
        if "-" in self.stop_key:
            # 对于组合键，我们只检查最后一个键
            last_key = self.stop_key.split("-")[-1].lower()
            return key_name.lower() == last_key.lower()
        else:
            # 对于单个键，直接比较
            return key_name.lower() == self.stop_key.lower()
            
    def _on_mouse_move(self, x, y):
        """鼠标移动事件处理
        
        Args:
            x: 鼠标X坐标
            y: 鼠标Y坐标
        """
        if not self.recording:
            return
            
        # 为了避免记录过多的移动事件，可以设置一个最小间隔
        # 或者记录关键点（例如每隔一段时间或距离记录一次）
        # 这里简化处理，记录所有移动
        action = {
            "type": "mouse_move",
            "x": x,
            "y": y,
            "time": self._get_current_time()
        }
        
        if self.callback:
            self.callback(action)
            
    def _on_mouse_click(self, x, y, button, pressed):
        """鼠标点击事件处理
        
        Args:
            x: 鼠标X坐标
            y: 鼠标Y坐标
            button: 按下的按钮
            pressed: 是否按下（True为按下，False为释放）
        """
        if not self.recording:
            return
            
        button_name = str(button).replace("Button.", "")
        
        action = {
            "type": "mouse_click",
            "button": button_name,
            "pressed": pressed,
            "x": x,
            "y": y,
            "time": self._get_current_time()
        }
        
        if self.callback:
            self.callback(action)
            
    def _on_mouse_scroll(self, x, y, dx, dy):
        """鼠标滚轮事件处理
        
        Args:
            x: 鼠标X坐标
            y: 鼠标Y坐标
            dx: 水平滚动量
            dy: 垂直滚动量
        """
        if not self.recording:
            return
            
        action = {
            "type": "mouse_scroll",
            "x": x,
            "y": y,
            "dx": dx,
            "dy": dy,
            "time": self._get_current_time()
        }
        
        if self.callback:
            self.callback(action)
