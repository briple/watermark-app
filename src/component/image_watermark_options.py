import os
from tkinter import Frame, Label, Button, Entry, Scale, StringVar, OptionMenu, END
from tkinter import filedialog, colorchooser
from PIL import Image, ImageTk
from .watermark_settings import global_watermark_settings

class ImageWatermarkOptions(Frame):
    def __init__(self, master, update_callback=None):
        super().__init__(master)
        self.update_callback = update_callback
        
        # 水印图片选择 - 单独一行
        Label(self, text="水印图片:").grid(row=0, column=0, sticky='e', padx=5, pady=2)
        self.image_path = StringVar(value=global_watermark_settings.image_settings['image_path'])
        self.path_entry = Entry(self, textvariable=self.image_path, width=25, state='readonly')
        self.path_entry.grid(row=0, column=1, columnspan=2, sticky='ew', padx=5, pady=2)
        Button(self, text="选择图片", command=self.select_image, width=8).grid(row=0, column=3, padx=5, pady=2)
        
        # 缩放和透明度 - 放在一行
        scale_frame = Frame(self)
        scale_frame.grid(row=1, column=0, columnspan=5, sticky='ew', padx=5, pady=2)
        
        Label(scale_frame, text="缩放比例(%):").pack(side='left', padx=(0, 5))
        self.scale_percent = Scale(scale_frame, from_=10, to=200, orient='horizontal', length=120)
        self.scale_percent.set(global_watermark_settings.image_settings['scale_percent'])
        self.scale_percent.pack(side='left', padx=(0, 5), fill='x', expand=True)
        
        # 缩放比例确认按钮
        self.scale_confirm_btn = Button(scale_frame, text="确认", command=self.confirm_scale, width=6)
        self.scale_confirm_btn.pack(side='left', padx=(5, 10))
        
        Label(scale_frame, text="透明度:").pack(side='left', padx=(0, 5))
        self.opacity = Scale(scale_frame, from_=0, to=100, orient='horizontal', length=100)
        self.opacity.set(global_watermark_settings.image_settings['opacity'])
        self.opacity.pack(side='left', padx=(0, 5), fill='x', expand=True)
        
        # 透明度确认按钮
        self.opacity_confirm_btn = Button(scale_frame, text="确认", command=self.confirm_opacity, width=6)
        self.opacity_confirm_btn.pack(side='left', padx=(5, 0))
        
        # 位置选择 - 单独一行
        position_frame = Frame(self)
        position_frame.grid(row=2, column=0, columnspan=5, sticky='ew', padx=5, pady=2)
        
        Label(position_frame, text="位置:").pack(side='left', padx=(0, 10))
        # 更新位置选项以匹配九宫格
        self.position = StringVar(value=global_watermark_settings.image_settings['position'])
        positions = ["top-left", "top", "top-right", 
                    "left", "center", "right", 
                    "bottom-left", "bottom", "bottom-right"]
        position_menu = OptionMenu(position_frame, self.position, *positions)
        position_menu.pack(side='left')
        if update_callback:
            self.position.trace('w', self.on_position_change)

    def select_image(self):
        """选择水印图片"""
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff *.tif"),
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="选择水印图片",
            filetypes=filetypes
        )
        
        if filename:
            self.image_path.set(filename)
            global_watermark_settings.update_image_setting('image_path', filename)
            if self.update_callback:
                self.update_callback(immediate=True)

    def confirm_scale(self):
        """确认缩放比例更改"""
        scale_value = self.scale_percent.get()
        global_watermark_settings.update_image_setting('scale_percent', scale_value)
        print(f"确认缩放比例: {scale_value}%")  # 调试信息
        if self.update_callback:
            self.update_callback(immediate=True)

    def confirm_opacity(self):
        """确认透明度更改"""
        opacity_value = self.opacity.get()
        global_watermark_settings.update_image_setting('opacity', opacity_value)
        if self.update_callback:
            self.update_callback(immediate=True)

    def on_position_change(self, *args):
        """位置变化处理 - 使用预设位置并禁用自定义位置模式"""
        try:
            position = self.position.get()
            # 使用预设位置并禁用自定义位置模式
            global_watermark_settings.set_preset_position(position)
            
            if self.update_callback:
                self.update_callback(immediate=True)
                
        except Exception as e:
            print(f"位置变化处理出错: {e}")

    def apply_watermark(self, image):
        """应用图片水印到图片"""
        if image is None:
            print("错误: 图片对象为None")
            return None
            
        if not global_watermark_settings.image_settings['image_path']:
            return image
            
        try:
            # 打开水印图片
            watermark = Image.open(global_watermark_settings.image_settings['image_path']).convert("RGBA")
            
            # 使用全局设置中的缩放比例
            base_size = min(image.width, image.height)
            scale_factor = global_watermark_settings.image_settings['scale_percent'] / 100.0
            
            # 使用固定比例而不是绝对值
            target_size = int(base_size * scale_factor * 0.15)  # 15% 的图片高度
            
            # 保持水印图片的宽高比
            wm_ratio = watermark.width / watermark.height
            if wm_ratio > 1:
                new_width = target_size
                new_height = int(target_size / wm_ratio)
            else:
                new_height = target_size
                new_width = int(target_size * wm_ratio)
            
            # 确保水印不会太小或太大
            min_size = base_size * 0.05  # 最小5%
            max_size = base_size * 0.3   # 最大30%
            
            if new_width < min_size or new_height < min_size:
                if new_width < new_height:
                    new_width = int(min_size)
                    new_height = int(min_size / wm_ratio)
                else:
                    new_height = int(min_size)
                    new_width = int(min_size * wm_ratio)
            elif new_width > max_size or new_height > max_size:
                if new_width > new_height:
                    new_width = int(max_size)
                    new_height = int(max_size / wm_ratio)
                else:
                    new_height = int(max_size)
                    new_width = int(max_size * wm_ratio)
            
            watermark = watermark.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 使用全局设置中的透明度
            opacity = global_watermark_settings.image_settings['opacity'] / 100.0
            watermark = self.apply_opacity_to_image(watermark, opacity)
            
            # 计算位置
            position = self.get_watermark_position(image.size, (new_width, new_height))
            
            # 创建结果图片
            result = image.convert("RGBA")
            result.paste(watermark, position, watermark)
            
            return result
            
        except Exception as e:
            print(f"应用图片水印时出错: {e}")
            import traceback
            traceback.print_exc()
            return image
    
    def get_watermark_position(self, image_size, watermark_size):
        """根据位置设置计算水印坐标"""
        img_width, img_height = image_size
        wm_width, wm_height = watermark_size
        
        position = global_watermark_settings.image_settings['position']
        margin = 20  # 边距
        
        if position == "center":
            return ((img_width - wm_width) // 2, (img_height - wm_height) // 2)
        elif position == "top-left":
            return (margin, margin)
        elif position == "top":
            return ((img_width - wm_width) // 2, margin)
        elif position == "top-right":
            return (img_width - wm_width - margin, margin)
        elif position == "left":
            return (margin, (img_height - wm_height) // 2)
        elif position == "right":
            return (img_width - wm_width - margin, (img_height - wm_height) // 2)
        elif position == "bottom-left":
            return (margin, img_height - wm_height - margin)
        elif position == "bottom":
            return ((img_width - wm_width) // 2, img_height - wm_height - margin)
        elif position == "bottom-right":
            return (img_width - wm_width - margin, img_height - wm_height - margin)
        else:
            return (margin, margin)  # 默认位置

    def apply_opacity_to_image(self, image, opacity):
        """调整图片透明度"""
        if opacity >= 1.0:
            return image
            
        # 创建一个新的alpha通道
        alpha = image.split()[3]
        alpha = alpha.point(lambda p: p * opacity)
        image.putalpha(alpha)
        return image

    def get_settings(self):
        """获取当前图片水印设置"""
        return global_watermark_settings.image_settings.copy()
    
    def set_settings(self, settings):
        """应用图片水印设置"""
        # 暂时禁用回调
        old_callback = self.update_callback
        self.update_callback = None
        
        self.image_path.set(settings.get('image_path', ''))
        self.scale_percent.set(settings.get('scale_percent', 30))
        self.opacity.set(settings.get('opacity', 50))
        self.position.set(settings.get('position', 'center'))
        
        # 更新全局设置
        for key, value in settings.items():
            global_watermark_settings.update_image_setting(key, value)
        
        # 恢复回调
        self.update_callback = old_callback