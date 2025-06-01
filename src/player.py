#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
按键精灵 - 播放器
负责重放记录的键盘和鼠标操作
"""

import time
import threading
import pyautogui
import keyboard

# 设置pyautogui的安全特性
pyautogui.FAILSAFE = True  # 将鼠标移动到屏幕左上角将中断程序
pyautogui.PAUSE = 0.01  # 每次PyAutoGUI函数调用后暂停的秒数

class Player:
    """重放记录的操作的类"""
    
    def __init__(self, config_manager=None):
        """初始化播放器"""
        self.playing = False
        self.stop_event = threading.Event()
        self.config_manager = config_manager
        
    def play(self, script, repeat=1, interval=0.1, record_stop_key=False):
        """播放脚本
        
        Args:
            script: 要播放的脚本（操作列表）
            repeat: 重复次数
            interval: 每次重复之间的间隔（秒）
            record_stop_key: 是否在播放结束后录制停止快捷键
        """
        if not script:
            return
            
        self.playing = True
        self.stop_event.clear()
        
        try:
            # 等待一小段时间，让用户有机会切换到目标窗口
            time.sleep(1)
            
            # 重复执行指定次数
            for _ in range(repeat):
                if self.stop_event.is_set():
                    break
                    
                # 执行一次脚本
                self._play_once(script)
                
                # 如果不是最后一次重复，则等待指定的间隔
                if _ < repeat - 1 and not self.stop_event.is_set():
                    time.sleep(interval)
                    
            # 如果需要录制停止快捷键
            if record_stop_key and self.config_manager and not self.stop_event.is_set():
                self._simulate_stop_hotkey()
        finally:
            self.playing = False
            
    def _simulate_stop_hotkey(self):
        """模拟按下停止快捷键"""
        if not self.config_manager:
            return
            
        # 获取停止快捷键
        stop_hotkey = self.config_manager.get_hotkey("stop_all")
        if not stop_hotkey:
            return
            
        try:
            # 模拟按下停止快捷键
            # 使用keyboard库模拟按键，因为它支持组合键
            keyboard.press_and_release(stop_hotkey.replace("-", "+").lower())
            
            # 添加一个小延迟，确保快捷键被处理
            time.sleep(0.1)
        except Exception as e:
            print(f"模拟停止快捷键错误: {str(e)}")
            
    def stop_playing(self):
        """停止播放"""
        self.stop_event.set()
        
    def _play_once(self, script):
        """执行一次脚本
        
        Args:
            script: 要播放的脚本（操作列表）
        """
        if not script:
            return
            
        # 获取第一个操作的时间作为基准
        base_time = script[0].get("time", 0)
        last_time = base_time
        
        # 按时间顺序执行每个操作
        for action in script:
            if self.stop_event.is_set():
                break
                
            # 计算需要等待的时间
            current_time = action.get("time", 0)
            wait_time = current_time - last_time
            
            # 等待适当的时间
            if wait_time > 0:
                time.sleep(wait_time)
                
            # 执行操作
            self._execute_action(action)
            
            # 更新上一次操作的时间
            last_time = current_time
            
    def _execute_action(self, action):
        """执行单个操作
        
        Args:
            action: 要执行的操作
        """
        action_type = action.get("type", "")
        
        if action_type == "key_press":
            key = action.get("key", "")
            if key:
                try:
                    pyautogui.keyDown(key)
                except Exception as e:
                    print(f"按键按下错误: {key} - {str(e)}")
                    
        elif action_type == "key_release":
            key = action.get("key", "")
            if key:
                try:
                    pyautogui.keyUp(key)
                except Exception as e:
                    print(f"按键释放错误: {key} - {str(e)}")
                    
        elif action_type == "mouse_move":
            x = action.get("x", 0)
            y = action.get("y", 0)
            
            # 获取当前鼠标位置
            current_x, current_y = pyautogui.position()
            
            # 计算相对移动
            dx = x - current_x
            dy = y - current_y
            
            try:
                # 使用相对移动而不是绝对位置移动
                # 这对于游戏中的视角控制更有效
                if dx != 0 or dy != 0:
                    # 使用dragRel模拟鼠标拖拽，这在游戏中更有效
                    pyautogui.dragRel(dx, dy, duration=0.01, button='middle')
                    
                    # 备选方法：使用鼠标按下状态下的移动
                    # pyautogui.mouseDown(button='right')  # 按下右键
                    # pyautogui.moveRel(dx, dy)  # 相对移动
                    # pyautogui.mouseUp(button='right')  # 释放右键
            except Exception as e:
                print(f"鼠标移动错误: {x},{y} - {str(e)}")
                
        elif action_type == "mouse_click":
            x = action.get("x", 0)
            y = action.get("y", 0)
            button = action.get("button", "left")
            pressed = action.get("pressed", False)
            
            # 将pynput的按钮名称转换为pyautogui的按钮名称
            if button == "left":
                button_name = "left"
            elif button == "right":
                button_name = "right"
            elif button == "middle":
                button_name = "middle"
            else:
                button_name = "left"  # 默认为左键
                
            try:
                # 移动到位置
                pyautogui.moveTo(x, y)
                
                # 按下或释放
                if pressed:
                    pyautogui.mouseDown(button=button_name)
                else:
                    pyautogui.mouseUp(button=button_name)
            except Exception as e:
                print(f"鼠标点击错误: {x},{y},{button},{pressed} - {str(e)}")
                
        elif action_type == "mouse_scroll":
            x = action.get("x", 0)
            y = action.get("y", 0)
            dx = action.get("dx", 0)
            dy = action.get("dy", 0)
            
            try:
                # 移动到位置
                pyautogui.moveTo(x, y)
                
                # 滚动
                # pyautogui的scroll函数正值向上滚动，负值向下滚动
                # 而pynput的dy正值向上滚动，负值向下滚动，所以直接使用
                pyautogui.scroll(int(dy * 10))  # 乘以一个系数使滚动更明显
            except Exception as e:
                print(f"鼠标滚轮错误: {x},{y},{dx},{dy} - {str(e)}")
