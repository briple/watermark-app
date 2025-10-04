
import os
from tkinter import Frame, Label, Button, Scale, StringVar, OptionMenu, END
from tkinter import filedialog
from PIL import Image, ImageTk
from .watermark_settings import global_watermark_settings

class ImageWatermarkOptions(Frame):
    def __init__(self, master, update_callback=None):
        super().__init__(master)
        self.update_callback = update_callback
        
        # 水印图片选择 - 单独一行
        Label(self, text="水印图片:").grid(row=0, column=0, sticky='e', padx=5, pady=2)
        self.image_path = StringVar(value=global_watermark_settings.image_settings['image_path'])
        Button(self, text="选择PNG图片", command=self.select_image, width=12).grid(row=0, column=1, sticky='w', padx=5, pady=2)
        self.path_label = Label(self, text="未选择", fg="gray", width=15, anchor='w')
        self.path_label.grid(row=0, column=2, columnspan=2, sticky='w', padx=5, pady=2)
        
        # 缩放比例和透明度 - 放在一行
        scale_opacity_frame = Frame(self)
        scale_opacity_frame.grid(row=1, column=0, columnspan=4, sticky='ew', padx=5, pady=2)
        
        Label(scale_opacity_frame, text="缩放比例(%):").pack(side='left', padx=(0, 5))
        self.scale_percent = Scale(scale_opacity_frame, from_=10, to=200, orient='horizontal', length=100)
        self.scale_percent.set(global_watermark_settings.image_settings['scale_percent'])
        self.scale_percent.pack(side='left', padx=(0, 10), fill='x', expand=True)
        # 添加缩放比例变化监听
        self.scale_percent.configure(command=self.on_slider_change)
        
        # 缩放比例确认按钮
        self.scale_confirm_btn = Button(scale_opacity_frame, text="确认", command=self.confirm_scale, width=6)
        self.scale_confirm_btn.pack(side='left', padx=(0, 20))
        
        Label(scale_opacity_frame, text="透明度:").pack(side='left', padx=(0, 5))
        self.opacity = Scale(scale_opacity_frame, from_=0, to=100, orient='horizontal', length=100)
        self.opacity.set(global_watermark_settings.image_settings['opacity'])
        self.opacity.pack(side='left', padx=(0, 10), fill='x', expand=True)
        # 添加透明度变化监听
        self.opacity.configure(command=self.on_slider_change)
        
        # 透明度确认按钮
        self.opacity_confirm_btn = Button(scale_opacity_frame, text="确认", command=self.confirm_opacity, width=6)
        self.opacity_confirm_btn.pack(side='left')
        
        # 位置选择 - 单独一行
        position_frame = Frame(self)
        position_frame.grid(row=2, column=0, columnspan=4, sticky='ew', padx=5, pady=2)
        
        Label(position_frame, text="位置:").pack(side='left', padx=(0, 10))
        # 更新位置选项以匹配九宫格
        self.position = StringVar(value=global_watermark_settings.image_settings['position'])
        positions = ["top-left", "top", "top-right", 
                    "left", "center", "right", 
                    "bottom-left", "bottom", "bottom-right"]
        position_menu = OptionMenu(position_frame, self.position, *positions)
        position_menu.pack(side='left')
        if update_callback:
            self.position.trace('w', self.on_setting_change)

    def on_setting_change(self, *args):
        """设置变化处理"""
        global_watermark_settings.update_image_setting('position', self.position.get())
        if self.update_callback:
            self.update_callback(immediate=True)  # 立即更新

    def on_slider_change(self, value):
        """滑块变化处理"""
        global_watermark_settings.update_image_setting('scale_percent', self.scale_percent.get())
        global_watermark_settings.update_image_setting('opacity', self.opacity.get())
        if self.update_callback:
            self.update_callback(immediate=True)  # 立即更新

    def confirm_scale(self):
        """确认缩放比例更改"""
        global_watermark_settings.update_image_setting('scale_percent', self.scale_percent.get())
        if self.update_callback:
            self.update_callback(immediate=True)

    def confirm_opacity(self):
        """确认透明度更改"""
        global_watermark_settings.update_image_setting('opacity', self.opacity.get())
        if self.update_callback:
            self.update_callback(immediate=True)

    def select_image(self):
        """选择水印图片"""
        path = filedialog.askopenfilename(
            title="选择水印图片",
            filetypes=[("PNG Images", "*.png"), ("All files", "*.*")]
        )
        if path:
            self.image_path.set(path)
            self.path_label.config(text=os.path.basename(path))
            global_watermark_settings.update_image_setting('image_path', path)
            if self.update_callback:
                self.update_callback(immediate=True)
    
    def apply_watermark(self, base_image):
        """应用图片水印到基础图片 - 修复版本"""
        # 检查图片是否有效
        if base_image is None:
            print("错误: 基础图片对象为None")
            return None
            
        if not global_watermark_settings.image_settings['image_path']:
            return base_image
            
        try:
            # 检查水印图片文件是否存在
            if not os.path.exists(global_watermark_settings.image_settings['image_path']):
                print(f"错误: 水印图片文件不存在: {global_watermark_settings.image_settings['image_path']}")
                return base_image
                
            # 打开水印图片
            watermark = Image.open(global_watermark_settings.image_settings['image_path']).convert("RGBA")
            
            # 缩放水印 - 基于图片尺寸的百分比
            scale_factor = global_watermark_settings.image_settings['scale_percent'] / 100.0
            new_width = int(base_image.width * scale_factor)
            new_height = int(base_image.height * scale_factor)
            
            # 保持水印图片的宽高比
            wm_ratio = watermark.width / watermark.height
            if new_width / new_height > wm_ratio:
                new_width = int(new_height * wm_ratio)
            else:
                new_height = int(new_width / wm_ratio)
                
            watermark = watermark.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 设置透明度
            opacity = global_watermark_settings.image_settings['opacity'] / 100.0
            watermark = self.apply_opacity(watermark, opacity)
            
            # 计算位置
            position = self.get_watermark_position(base_image.size, watermark.size)
            
            # 创建结果图片
            result = base_image.convert("RGBA")
            result.paste(watermark, position, watermark)
            
            return result
            
        except Exception as e:
            print(f"应用图片水印时出错: {e}")
            import traceback
            traceback.print_exc()
            return base_image
    
    def apply_opacity(self, image, opacity):
        """调整图片透明度"""
        if opacity >= 1.0:
            return image
            
        # 创建一个新的alpha通道
        alpha = image.split()[3]
        alpha = alpha.point(lambda p: p * opacity)
        image.putalpha(alpha)
        return image
    
    def get_watermark_position(self, base_size, watermark_size):
        """根据位置设置计算水印坐标"""
        base_width, base_height = base_size
        wm_width, wm_height = watermark_size
        
        position = global_watermark_settings.image_settings['position']
        margin = 20  # 边距
        
        if position == "center":
            return ((base_width - wm_width) // 2, (base_height - wm_height) // 2)
        elif position == "top-left":
            return (margin, margin)
        elif position == "top":
            return ((base_width - wm_width) // 2, margin)
        elif position == "top-right":
            return (base_width - wm_width - margin, margin)
        elif position == "left":
            return (margin, (base_height - wm_height) // 2)
        elif position == "right":
            return (base_width - wm_width - margin, (base_height - wm_height) // 2)
        elif position == "bottom-left":
            return (margin, base_height - wm_height - margin)
        elif position == "bottom":
            return ((base_width - wm_width) // 2, base_height - wm_height - margin)
        elif position == "bottom-right":
            return (base_width - wm_width - margin, base_height - wm_height - margin)
        else:
            return (margin, margin)  # 默认位置

    def get_settings(self):
        """获取当前图片水印设置"""
        return global_watermark_settings.image_settings.copy()
    
    def set_settings(self, settings):
        """应用图片水印设置"""
        # 暂时禁用回调
        old_callback = self.update_callback
        self.update_callback = None
        
        self.image_path.set(settings.get('image_path', ''))
        if self.image_path.get():
            self.path_label.config(text=os.path.basename(self.image_path.get()))
        else:
            self.path_label.config(text="未选择")
        
        self.scale_percent.set(settings.get('scale_percent', 30))
        self.opacity.set(settings.get('opacity', 50))
        self.position.set(settings.get('position', 'center'))
        
        # 更新全局设置
        for key, value in settings.items():
            global_watermark_settings.update_image_setting(key, value)
        
        # 恢复回调
        self.update_callback = old_callback