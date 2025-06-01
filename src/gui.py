#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
按键精灵 - GUI界面
提供用户界面，包括记录、播放、编辑和管理脚本的功能
"""

import os
import time
import threading
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
import keyboard  # 导入keyboard库用于全局热键
from recorder import Recorder
from player import Player
from script_manager import ScriptManager
from config_manager import ConfigManager, DEFAULT_CONFIG

class AnJianApp(ctk.CTk):
    """按键精灵主应用程序类"""
    
    def __init__(self, config_manager=None):
        super().__init__()
        
        # 初始化应用程序
        self.title("按键精灵 - Windows 11自动化工具")
        self.geometry("900x600")
        self.minsize(800, 500)
        
        # 创建组件
        self.recorder = Recorder(config_manager)
        self.player = Player(config_manager)
        self.script_manager = ScriptManager()
        self.config_manager = config_manager or ConfigManager()
        
        # 状态变量
        self.is_recording = False
        self.is_playing = False
        self.current_script = []
        self.current_file = None
        self.play_thread = None
        
        # 创建界面
        self.create_ui()
        
        # 绑定热键
        self.bind_hotkeys()
        
        # 当前正在录制的热键
        self.current_hotkey_action = None
        
    def create_ui(self):
        """创建用户界面"""
        # 创建主框架
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        main_frame.grid_columnconfigure(1, weight=1)  # 改为第二列自动扩展
        main_frame.grid_rowconfigure(0, weight=1)
        
        # 左侧按钮区域
        left_panel = ctk.CTkFrame(main_frame, width=200)
        left_panel.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        left_panel.grid_propagate(False)  # 防止框架缩小
        
        # 按钮标题
        title_label = ctk.CTkLabel(left_panel, text="按键精灵", font=("Arial", 16, "bold"))
        title_label.pack(pady=(15, 20))
        
        # 记录和播放按钮
        record_hotkey = self.config_manager.get_hotkey("record_toggle")
        btn_record = ctk.CTkButton(
            left_panel, 
            text=f"开始记录 [{record_hotkey}]", 
            command=self.toggle_recording,
            fg_color="#E74C3C",
            hover_color="#C0392B",
            width=180
        )
        btn_record.pack(padx=10, pady=5)
        self.btn_record = btn_record
        
        play_hotkey = self.config_manager.get_hotkey("play_toggle")
        btn_play = ctk.CTkButton(
            left_panel, 
            text=f"开始播放 [{play_hotkey}]", 
            command=self.toggle_playing,
            fg_color="#2ECC71",
            hover_color="#27AE60",
            width=180
        )
        btn_play.pack(padx=10, pady=5)
        self.btn_play = btn_play
        
        # 分隔线
        separator1 = ctk.CTkFrame(left_panel, height=1, fg_color="gray70")
        separator1.pack(fill="x", padx=15, pady=10)
        
        # 文件操作按钮
        new_hotkey = self.config_manager.get_hotkey("new_script")
        btn_new = ctk.CTkButton(
            left_panel, 
            text=f"新建 [{new_hotkey}]", 
            command=self.new_script,
            width=180
        )
        btn_new.pack(padx=10, pady=5)
        
        open_hotkey = self.config_manager.get_hotkey("open_script")
        btn_open = ctk.CTkButton(
            left_panel, 
            text=f"打开 [{open_hotkey}]", 
            command=self.open_script,
            width=180
        )
        btn_open.pack(padx=10, pady=5)
        
        save_hotkey = self.config_manager.get_hotkey("save_script")
        btn_save = ctk.CTkButton(
            left_panel, 
            text=f"保存 [{save_hotkey}]", 
            command=self.save_script,
            width=180
        )
        btn_save.pack(padx=10, pady=5)
        
        save_as_hotkey = self.config_manager.get_hotkey("save_as_script")
        btn_save_as = ctk.CTkButton(
            left_panel, 
            text=f"另存为 [{save_as_hotkey}]", 
            command=self.save_script_as,
            width=180
        )
        btn_save_as.pack(padx=10, pady=5)
        
        # 分隔线
        separator2 = ctk.CTkFrame(left_panel, height=1, fg_color="gray70")
        separator2.pack(fill="x", padx=15, pady=10)
        
        # 设置区域
        settings_frame = ctk.CTkFrame(left_panel)
        settings_frame.pack(padx=10, pady=5, fill="x")
        
        # 执行次数设置
        repeat_label = ctk.CTkLabel(settings_frame, text="执行次数:")
        repeat_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        
        self.repeat_var = tk.StringVar(value="1")
        repeat_entry = ctk.CTkEntry(settings_frame, width=50, textvariable=self.repeat_var)
        repeat_entry.grid(row=0, column=1, padx=5, pady=2)
        
        # 间隔设置
        interval_label = ctk.CTkLabel(settings_frame, text="间隔(秒):")
        interval_label.grid(row=1, column=0, padx=5, pady=2, sticky="w")
        
        self.interval_var = tk.StringVar(value="0.1")
        interval_entry = ctk.CTkEntry(settings_frame, width=50, textvariable=self.interval_var)
        interval_entry.grid(row=1, column=1, padx=5, pady=2)
        
        # 分隔线
        separator3 = ctk.CTkFrame(left_panel, height=1, fg_color="gray70")
        separator3.pack(fill="x", padx=15, pady=10)
        
        # 设置按钮
        btn_settings = ctk.CTkButton(
            left_panel, 
            text="快捷键设置", 
            command=self.open_hotkey_settings,
            width=180
        )
        btn_settings.pack(padx=10, pady=5)
        
        # 右侧脚本编辑区域
        right_panel = ctk.CTkFrame(main_frame)
        right_panel.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(0, weight=1)
        
        # 脚本编辑区标题
        script_title = ctk.CTkLabel(right_panel, text="脚本编辑区", font=("Arial", 14))
        script_title.pack(pady=(10, 5), anchor="w")
        
        # 脚本编辑框
        script_frame = ctk.CTkFrame(right_panel)
        script_frame.pack(fill="both", expand=True, padx=10, pady=10)
        script_frame.grid_columnconfigure(0, weight=1)
        script_frame.grid_rowconfigure(0, weight=1)
        
        self.script_text = ctk.CTkTextbox(script_frame, wrap="none", font=("Consolas", 12))
        self.script_text.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ctk.CTkLabel(self, textvariable=self.status_var, anchor="w")
        status_bar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 5))
        
    def bind_hotkeys(self):
        """绑定热键"""
        # 解绑所有现有热键（应用内热键）
        self.unbind_all("<F9>")
        self.unbind_all("<F10>")
        self.unbind_all("<Control-n>")
        self.unbind_all("<Control-o>")
        self.unbind_all("<Control-s>")
        self.unbind_all("<Control-Shift-s>")
        self.unbind_all("<Escape>")
        
        # 获取配置的热键
        hotkeys = self.config_manager.get_all_hotkeys()
        
        # 检查是否启用全局热键
        use_global_hotkeys = self.config_manager.is_global_hotkeys_enabled()
        
        # 解除所有已注册的全局热键
        try:
            keyboard.unhook_all()
        except:
            pass
        
        if use_global_hotkeys:
            # 注册全局热键
            try:
                # 将Tkinter热键格式转换为keyboard库格式
                def convert_hotkey(tk_hotkey):
                    # 替换常见的修饰键名称
                    hotkey = tk_hotkey.replace("Control", "ctrl").replace("Shift", "shift").replace("Alt", "alt")
                    # 将连字符替换为加号
                    hotkey = hotkey.replace("-", "+")
                    return hotkey
                
                # 注册全局热键
                keyboard.add_hotkey(convert_hotkey(hotkeys.get('record_toggle', 'F9')), self.toggle_recording)
                keyboard.add_hotkey(convert_hotkey(hotkeys.get('play_toggle', 'F10')), self.toggle_playing)
                keyboard.add_hotkey(convert_hotkey(hotkeys.get('new_script', 'ctrl+n')), self.new_script)
                keyboard.add_hotkey(convert_hotkey(hotkeys.get('open_script', 'ctrl+o')), self.open_script)
                keyboard.add_hotkey(convert_hotkey(hotkeys.get('save_script', 'ctrl+s')), self.save_script)
                keyboard.add_hotkey(convert_hotkey(hotkeys.get('save_as_script', 'ctrl+shift+s')), self.save_script_as)
                keyboard.add_hotkey(convert_hotkey(hotkeys.get('stop_all', 'Escape')), self.stop_all)
                
                self.status_var.set("全局热键已启用")
            except Exception as e:
                messagebox.showerror("错误", f"注册全局热键失败: {str(e)}")
                # 如果全局热键注册失败，回退到应用内热键
                use_global_hotkeys = False
        
        # 如果不使用全局热键或全局热键注册失败，使用应用内热键
        if not use_global_hotkeys:
            # 绑定应用内热键
            self.bind(f"<{hotkeys.get('record_toggle', 'F9')}>", lambda e: self.toggle_recording())
            self.bind(f"<{hotkeys.get('play_toggle', 'F10')}>", lambda e: self.toggle_playing())
            self.bind(f"<{hotkeys.get('new_script', 'Control-n')}>", lambda e: self.new_script())
            self.bind(f"<{hotkeys.get('open_script', 'Control-o')}>", lambda e: self.open_script())
            self.bind(f"<{hotkeys.get('save_script', 'Control-s')}>", lambda e: self.save_script())
            self.bind(f"<{hotkeys.get('save_as_script', 'Control-Shift-s')}>", lambda e: self.save_script_as())
            self.bind(f"<{hotkeys.get('stop_all', 'Escape')}>", lambda e: self.stop_all())
        
    def stop_all(self):
        """停止所有操作"""
        if self.is_recording:
            self.toggle_recording()
        if self.is_playing:
            self.toggle_playing()
            
    def toggle_recording(self):
        """切换记录状态"""
        if self.is_playing:
            messagebox.showwarning("警告", "请先停止播放")
            return
            
        if not self.is_recording:
            # 开始记录
            self.is_recording = True
            record_hotkey = self.config_manager.get_hotkey("record_toggle")
            self.btn_record.configure(text=f"停止记录 [{record_hotkey}]")
            self.status_var.set("正在记录...")
            
            # 清空当前脚本
            self.current_script = []
            self.script_text.delete("1.0", "end")
            
            # 启动记录器
            self.recorder.start_recording(callback=self.on_action_recorded)
        else:
            # 停止记录
            self.is_recording = False
            self.btn_record.configure(text="开始记录")
            self.status_var.set("记录已停止")
            
            # 停止记录器
            self.recorder.stop_recording()
            
    def toggle_playing(self):
        """切换播放状态"""
        if self.is_recording:
            messagebox.showwarning("警告", "请先停止记录")
            return
            
        if not self.is_playing:
            # 获取脚本内容
            script_text = self.script_text.get("1.0", "end").strip()
            if not script_text:
                messagebox.showwarning("警告", "没有可播放的脚本")
                return
                
            # 解析脚本
            try:
                script = self.script_manager.parse_script(script_text)
                if not script:
                    raise ValueError("脚本解析失败")
            except Exception as e:
                messagebox.showerror("错误", f"脚本格式错误: {str(e)}")
                return
                
            # 获取重复次数和间隔
            try:
                repeat = int(self.repeat_var.get())
                interval = float(self.interval_var.get())
                if repeat < 1:
                    repeat = 1
                if interval < 0:
                    interval = 0
            except ValueError:
                messagebox.showerror("错误", "请输入有效的执行次数和间隔")
                return
                
            # 开始播放
            self.is_playing = True
            play_hotkey = self.config_manager.get_hotkey("play_toggle")
            self.btn_play.configure(text=f"停止播放 [{play_hotkey}]")
            self.status_var.set(f"正在播放... (重复: {repeat}, 间隔: {interval}秒)")
            
            # 在新线程中播放，避免阻塞UI
            self.play_thread = threading.Thread(
                target=self.play_script,
                args=(script, repeat, interval),
                daemon=True
            )
            self.play_thread.start()
        else:
            # 停止播放
            self.is_playing = False
            play_hotkey = self.config_manager.get_hotkey("play_toggle")
            self.btn_play.configure(text=f"开始播放 [{play_hotkey}]")
            self.status_var.set("播放已停止")
            
            # 停止播放器
            self.player.stop_playing()
            
    def play_script(self, script, repeat, interval):
        """播放脚本"""
        try:
            # 传递配置管理器给播放器，并启用录制停止快捷键
            if not hasattr(self.player, "config_manager") or self.player.config_manager is None:
                self.player.config_manager = self.config_manager
            
            # 播放脚本，并在最后录制停止快捷键
            self.player.play(script, repeat, interval, record_stop_key=True)
        except Exception as e:
            # 在UI线程中显示错误
            self.after(0, lambda: messagebox.showerror("播放错误", str(e)))
        finally:
            # 在UI线程中更新状态
            self.after(0, self.on_play_finished)
            
    def on_play_finished(self):
        """播放完成后的回调"""
        self.is_playing = False
        play_hotkey = self.config_manager.get_hotkey("play_toggle")
        self.btn_play.configure(text=f"开始播放 [{play_hotkey}]")
        self.status_var.set("播放完成")
        
        # 播放结束后重新绑定热键，确保全局热键在游戏中仍然有效
        self.after(500, self.bind_hotkeys)  # 延迟500毫秒后重新绑定
            
    def on_action_recorded(self, action):
        """记录动作的回调"""
        # 添加到当前脚本
        self.current_script.append(action)
        
        # 更新文本显示
        action_str = self.script_manager.format_action(action)
        self.script_text.insert("end", action_str + "\n")
        self.script_text.see("end")
            
    def new_script(self):
        """新建脚本"""
        if self.is_recording or self.is_playing:
            messagebox.showwarning("警告", "请先停止当前操作")
            return
            
        # 检查是否需要保存当前脚本
        if self.script_text.get("1.0", "end").strip():
            if messagebox.askyesno("确认", "当前脚本未保存，是否保存?"):
                self.save_script()
                
        # 清空当前脚本
        self.script_text.delete("1.0", "end")
        self.current_script = []
        self.current_file = None
        self.status_var.set("新建脚本")
            
    def open_script(self):
        """打开脚本"""
        if self.is_recording or self.is_playing:
            messagebox.showwarning("警告", "请先停止当前操作")
            return
            
        # 打开文件对话框
        file_path = filedialog.askopenfilename(
            title="打开脚本",
            filetypes=[("按键精灵脚本", "*.ajs"), ("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                # 加载脚本
                script_text = self.script_manager.load_script(file_path)
                
                # 更新UI
                self.script_text.delete("1.0", "end")
                self.script_text.insert("1.0", script_text)
                self.current_file = file_path
                self.status_var.set(f"已加载: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("错误", f"无法打开文件: {str(e)}")
            
    def save_script(self):
        """保存脚本"""
        if not self.current_file:
            self.save_script_as()
        else:
            try:
                # 获取脚本内容
                script_text = self.script_text.get("1.0", "end")
                
                # 保存脚本
                self.script_manager.save_script(self.current_file, script_text)
                self.status_var.set(f"已保存: {os.path.basename(self.current_file)}")
            except Exception as e:
                messagebox.showerror("错误", f"无法保存文件: {str(e)}")
            
    def save_script_as(self):
        """另存为脚本"""
        # 打开保存文件对话框
        file_path = filedialog.asksaveasfilename(
            title="保存脚本",
            defaultextension=".ajs",
            filetypes=[("按键精灵脚本", "*.ajs"), ("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            self.current_file = file_path
            self.save_script()
            
    def open_hotkey_settings(self):
        """打开快捷键设置对话框"""
        if self.is_recording or self.is_playing:
            messagebox.showwarning("警告", "请先停止当前操作")
            return
            
        # 创建设置对话框
        settings_dialog = ctk.CTkToplevel(self)
        settings_dialog.title("快捷键设置")
        settings_dialog.geometry("500x400")
        settings_dialog.resizable(False, False)
        settings_dialog.transient(self)  # 设置为模态
        settings_dialog.grab_set()  # 模态对话框
        
        # 创建设置界面
        settings_frame = ctk.CTkFrame(settings_dialog)
        settings_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 标题
        title_label = ctk.CTkLabel(settings_frame, text="自定义快捷键", font=("Arial", 16, "bold"))
        title_label.pack(pady=(10, 10))
        
        # 全局热键开关
        global_hotkey_frame = ctk.CTkFrame(settings_frame)
        global_hotkey_frame.pack(fill="x", padx=10, pady=5)
        
        global_hotkey_var = tk.BooleanVar(value=self.config_manager.is_global_hotkeys_enabled())
        global_hotkey_switch = ctk.CTkSwitch(
            global_hotkey_frame, 
            text="启用全局热键（在游戏中可用）", 
            variable=global_hotkey_var,
            command=lambda: self.toggle_global_hotkeys(global_hotkey_var.get())
        )
        global_hotkey_switch.pack(pady=5, padx=10, anchor="w")
        
        # 快捷键列表
        hotkeys_frame = ctk.CTkFrame(settings_frame)
        hotkeys_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 显示所有快捷键
        hotkeys = self.config_manager.get_all_hotkeys()
        hotkey_buttons = {}
        
        # 快捷键名称映射
        hotkey_names = {
            "record_toggle": "开始/停止记录",
            "play_toggle": "开始/停止播放",
            "new_script": "新建脚本",
            "open_script": "打开脚本",
            "save_script": "保存脚本",
            "save_as_script": "另存为脚本",
            "stop_all": "停止所有操作"
        }
        
        # 创建每个快捷键的设置行
        for i, (action, hotkey) in enumerate(hotkeys.items()):
            frame = ctk.CTkFrame(hotkeys_frame)
            frame.pack(fill="x", padx=5, pady=5)
            
            # 操作名称
            action_name = hotkey_names.get(action, action)
            label = ctk.CTkLabel(frame, text=f"{action_name}:", width=120, anchor="e")
            label.pack(side="left", padx=(10, 5))
            
            # 当前快捷键
            button = ctk.CTkButton(
                frame, 
                text=hotkey,
                width=150,
                command=lambda a=action, b=None: self.record_hotkey(a, b)
            )
            button.pack(side="left", padx=5)
            hotkey_buttons[action] = button
            
            # 重置按钮
            reset_button = ctk.CTkButton(
                frame, 
                text="重置",
                width=80,
                command=lambda a=action, b=button: self.reset_hotkey(a, b)
            )
            reset_button.pack(side="left", padx=5)
        
        # 保存所有按钮引用
        self.hotkey_buttons = hotkey_buttons
        
        # 底部按钮
        button_frame = ctk.CTkFrame(settings_frame)
        button_frame.pack(fill="x", padx=10, pady=(20, 10))
        
        # 重置所有按钮
        reset_all_button = ctk.CTkButton(
            button_frame, 
            text="重置所有",
            command=self.reset_all_hotkeys
        )
        reset_all_button.pack(side="left", padx=5)
        
        # 关闭按钮
        close_button = ctk.CTkButton(
            button_frame, 
            text="关闭",
            command=settings_dialog.destroy
        )
        close_button.pack(side="right", padx=5)
        
        # 保存对话框引用
        self.settings_dialog = settings_dialog
        
    def record_hotkey(self, action, button=None):
        """记录新的快捷键
        
        Args:
            action: 操作名称
            button: 按钮对象
        """
        if button is None:
            button = self.hotkey_buttons.get(action)
            
        if button:
            # 更新按钮文本
            button.configure(text="按下新快捷键...")
            
            # 设置当前正在录制的热键
            self.current_hotkey_action = action
            
            # 绑定键盘事件
            self.settings_dialog.bind("<Key>", self.on_hotkey_press)
            
    def on_hotkey_press(self, event):
        """处理热键按下事件
        
        Args:
            event: 键盘事件
        """
        if self.current_hotkey_action is None:
            return
            
        # 获取按键名称
        key_name = event.keysym
        
        # 检查修饰键
        modifiers = []
        if event.state & 0x4:  # Control
            modifiers.append("Control")
        if event.state & 0x1:  # Shift
            modifiers.append("Shift")
        if event.state & 0x8:  # Alt
            modifiers.append("Alt")
            
        # 组合修饰键和按键
        if modifiers:
            hotkey = "-".join(modifiers + [key_name])
        else:
            hotkey = key_name
            
        # 更新配置
        self.config_manager.set_hotkey(self.current_hotkey_action, hotkey)
        
        # 更新按钮文本
        button = self.hotkey_buttons.get(self.current_hotkey_action)
        if button:
            button.configure(text=hotkey)
            
        # 重置当前录制的热键
        self.current_hotkey_action = None
        
        # 解绑键盘事件
        self.settings_dialog.unbind("<Key>")
        
        # 更新主界面按钮文本
        self.update_button_texts()
        
        # 重新绑定热键
        self.bind_hotkeys()
        
    def reset_hotkey(self, action, button):
        """重置单个快捷键为默认值
        
        Args:
            action: 操作名称
            button: 按钮对象
        """
        # 获取默认值
        # 使用ConfigManager中的默认值，而不是直接使用DEFAULT_CONFIG
        from config_manager import DEFAULT_CONFIG
        default_hotkey = DEFAULT_CONFIG["hotkeys"].get(action, "")
        
        # 更新配置
        self.config_manager.set_hotkey(action, default_hotkey)
        
        # 更新按钮文本
        if button:
            button.configure(text=default_hotkey)
            
        # 更新主界面按钮文本
        self.update_button_texts()
        
        # 重新绑定热键
        self.bind_hotkeys()
        
    def reset_all_hotkeys(self):
        """重置所有快捷键为默认值"""
        # 重置配置
        self.config_manager.reset_hotkeys()
        
        # 更新所有按钮文本
        hotkeys = self.config_manager.get_all_hotkeys()
        for action, hotkey in hotkeys.items():
            button = self.hotkey_buttons.get(action)
            if button:
                button.configure(text=hotkey)
                
        # 更新主界面按钮文本
        self.update_button_texts()
        
        # 重新绑定热键
        self.bind_hotkeys()
        
    def toggle_global_hotkeys(self, enabled):
        """启用或禁用全局热键
        
        Args:
            enabled: 是否启用全局热键
        """
        # 更新配置
        self.config_manager.set_global_hotkeys_enabled(enabled)
        
        # 重新绑定热键
        self.bind_hotkeys()
        
        # 更新状态栏
        if enabled:
            self.status_var.set("全局热键已启用")
        else:
            self.status_var.set("全局热键已禁用")
            
    def update_button_texts(self):
        """更新主界面按钮文本，显示当前快捷键"""
        # 获取当前快捷键
        record_hotkey = self.config_manager.get_hotkey("record_toggle")
        play_hotkey = self.config_manager.get_hotkey("play_toggle")
        new_hotkey = self.config_manager.get_hotkey("new_script")
        open_hotkey = self.config_manager.get_hotkey("open_script")
        save_hotkey = self.config_manager.get_hotkey("save_script")
        save_as_hotkey = self.config_manager.get_hotkey("save_as_script")
        
        # 更新按钮文本
        if hasattr(self, "btn_record"):
            text = "停止记录" if self.is_recording else "开始记录"
            self.btn_record.configure(text=f"{text} [{record_hotkey}]")
            
        if hasattr(self, "btn_play"):
            text = "停止播放" if self.is_playing else "开始播放"
            self.btn_play.configure(text=f"{text} [{play_hotkey}]")
