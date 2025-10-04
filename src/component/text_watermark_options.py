import os
from tkinter import Frame, Label, Entry, Button, Scale, StringVar, OptionMenu, Radiobutton, END, IntVar
from tkinter import colorchooser
import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageTk
from .watermark_settings import global_watermark_settings

class TextWatermarkOptions(Frame):
    def __init__(self, master, update_callback=None):
        super().__init__(master)
        self.update_callback = update_callback
        
        # 水印文本 - 单独一行
        Label(self, text="水印文本:").grid(row=0, column=0, sticky='e', padx=5, pady=2)
        self.text_entry = Entry(self, width=18)
        self.text_entry.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        self.text_entry.insert(0, global_watermark_settings.text_settings['text'])
        # 添加文本变化监听
        self.text_entry.bind('<KeyRelease>', self.on_text_change)
        
        # 文本确认按钮
        self.text_confirm_btn = Button(self, text="确认", command=self.confirm_text, width=6)
        self.text_confirm_btn.grid(row=0, column=2, padx=5, pady=2)
        
        # 字体、字号、粗斜体 - 放在一行
        font_frame = Frame(self)
        font_frame.grid(row=1, column=0, columnspan=5, sticky='ew', padx=5, pady=2)
        
        Label(font_frame, text="字体:").pack(side='left', padx=(0, 5))
        
        # 预设常用字体映射
        self.font_mapping = {
            # 英文和通用字体
            "Arial": "Arial",
            "Helvetica": "Helvetica",
            "Helvetica Neue": "Helvetica Neue",
            "Times New Roman": "Times New Roman",
            "Courier New": "Courier New",
            "Verdana": "Verdana",
            "Tahoma": "Tahoma",
            "Georgia": "Georgia",
            "Trebuchet MS": "Trebuchet MS",
            "Comic Sans MS": "Comic Sans MS",
            "Impact": "Impact",
            "Lucida Grande": "Lucida Grande",
        }
        
        self.available_fonts = list(self.font_mapping.keys())
        self.font_family = StringVar(value=global_watermark_settings.text_settings['font_family'])
        
        font_menu = OptionMenu(font_frame, self.font_family, *self.available_fonts)
        font_menu.config(width=12)
        font_menu.pack(side='left', padx=(0, 10))
        if update_callback:
            self.font_family.trace('w', self.on_setting_change)
        
        Label(font_frame, text="字号:").pack(side='left', padx=(0, 5))
        
        # 创建验证函数
        def validate_font_size_input(P):
            """验证字号输入"""
            if P == "" or P.isdigit():
                return True
            else:
                return False
        
        vcmd = (self.register(validate_font_size_input), '%P')
        self.font_size = IntVar(value=global_watermark_settings.text_settings['font_size'])
        self.font_size_entry = Entry(font_frame, textvariable=self.font_size, width=4, validate="key", validatecommand=vcmd)
        self.font_size_entry.pack(side='left', padx=(0, 5))
        # 添加字号变化监听
        # self.font_size.trace('w', self.on_setting_change)
        
        # 字号确认按钮
        self.size_confirm_btn = Button(font_frame, text="确认", command=self.confirm_size, width=6)
        self.size_confirm_btn.pack(side='left', padx=(0, 10))
        
        self.bold = IntVar(value=global_watermark_settings.text_settings['bold'])
        bold_cb = tk.Checkbutton(font_frame, text="粗体", variable=self.bold, command=self.on_checkbutton_change)
        bold_cb.pack(side='left', padx=(0, 5))
        
        self.italic = IntVar(value=global_watermark_settings.text_settings['italic'])
        italic_cb = tk.Checkbutton(font_frame, text="斜体", variable=self.italic, command=self.on_checkbutton_change)
        italic_cb.pack(side='left')
        
        # 颜色和透明度 - 放在一行
        color_frame = Frame(self)
        color_frame.grid(row=2, column=0, columnspan=5, sticky='ew', padx=5, pady=2)
        
        Label(color_frame, text="颜色:").pack(side='left', padx=(0, 5))
        self.color = StringVar(value=global_watermark_settings.text_settings['color'])
        self.color_preview = Label(color_frame, text="    ", bg=self.color.get(), relief="solid", bd=1, width=4)
        self.color_preview.pack(side='left', padx=(0, 10))
        Button(color_frame, text="选择颜色", command=self.choose_color, width=8).pack(side='left', padx=(0, 15))
        
        Label(color_frame, text="透明度:").pack(side='left', padx=(0, 5))
        self.opacity = Scale(color_frame, from_=0, to=100, orient='horizontal', length=100)
        self.opacity.set(global_watermark_settings.text_settings['opacity'])
        self.opacity.pack(side='left', padx=(0, 5), fill='x', expand=True)
        # 添加透明度变化监听
        # self.opacity.configure(command=self.on_slider_change)
        
        # 透明度确认按钮
        self.opacity_confirm_btn = Button(color_frame, text="确认", command=self.confirm_opacity, width=6)
        self.opacity_confirm_btn.pack(side='left', padx=(5, 0))
        
        # 样式效果和描边宽度 - 放在一行
        style_frame = Frame(self)
        style_frame.grid(row=3, column=0, columnspan=5, sticky='ew', padx=5, pady=2)
        
        Label(style_frame, text="样式效果:").pack(side='left', padx=(0, 5))
        self.shadow = IntVar(value=global_watermark_settings.text_settings['shadow'])
        shadow_cb = tk.Checkbutton(style_frame, text="阴影", variable=self.shadow, command=self.on_checkbutton_change)
        shadow_cb.pack(side='left', padx=(0, 10))
        
        self.stroke = IntVar(value=global_watermark_settings.text_settings['stroke'])
        stroke_cb = tk.Checkbutton(style_frame, text="描边", variable=self.stroke, command=self.on_checkbutton_change)
        stroke_cb.pack(side='left', padx=(0, 10))
        
        Label(style_frame, text="描边宽度:").pack(side='left', padx=(0, 5))
        
        # 描边宽度验证
        def validate_stroke_width_input(P):
            """验证描边宽度输入"""
            if P == "" or P.isdigit():
                return True
            else:
                return False
        
        stroke_vcmd = (self.register(validate_stroke_width_input), '%P')
        self.stroke_width = IntVar(value=global_watermark_settings.text_settings['stroke_width'])
        self.stroke_entry = Entry(style_frame, textvariable=self.stroke_width, width=3, validate="key", validatecommand=stroke_vcmd)
        self.stroke_entry.pack(side='left', padx=(0, 5))
        # 添加描边宽度变化监听
        self.stroke_width.trace('w', self.on_setting_change)
        
        # 描边宽度确认按钮
        self.stroke_confirm_btn = Button(style_frame, text="确认", command=self.confirm_stroke, width=6)
        self.stroke_confirm_btn.pack(side='left')
        
        # 位置选择 - 单独一行
        position_frame = Frame(self)
        position_frame.grid(row=4, column=0, columnspan=5, sticky='ew', padx=5, pady=2)
        
        Label(position_frame, text="位置:").pack(side='left', padx=(0, 10))
        # 更新位置选项以匹配九宫格
        self.position = StringVar(value=global_watermark_settings.text_settings['position'])
        positions = ["top-left", "top", "top-right", 
                    "left", "center", "right", 
                    "bottom-left", "bottom", "bottom-right"]
        position_menu = OptionMenu(position_frame, self.position, *positions)
        position_menu.pack(side='left')
        if update_callback:
            self.position.trace('w', self.on_position_change)  # 修改为专门的位置变化处理

    def on_text_change(self, event=None):
        """文本变化处理"""
        global_watermark_settings.update_text_setting('text', self.text_entry.get())
        if self.update_callback:
            self.update_callback(immediate=True)  # 文本变化立即更新

    def on_setting_change(self, *args):
        """设置变化处理（除了位置）"""
        try:
            # 安全地获取字号值
            font_size_value = self.get_safe_int_value(self.font_size)
            stroke_width_value = self.get_safe_int_value(self.stroke_width)
            
            # 更新全局设置
            global_watermark_settings.update_text_setting('font_family', self.font_family.get())
            if font_size_value is not None:
                global_watermark_settings.update_text_setting('font_size', font_size_value)
            global_watermark_settings.update_text_setting('color', self.color.get())
            global_watermark_settings.update_text_setting('opacity', self.opacity.get())
            if stroke_width_value is not None:
                global_watermark_settings.update_text_setting('stroke_width', stroke_width_value)
            
            if self.update_callback:
                self.update_callback(immediate=True)  # 设置变化立即更新
                
        except Exception as e:
            print(f"设置变化处理出错: {e}")

    def on_position_change(self, *args):
        """位置变化处理 - 使用预设位置并禁用自定义位置模式"""
        try:
            position = self.position.get()
            # 使用预设位置并禁用自定义位置模式
            global_watermark_settings.set_preset_position(position)
            
            if self.update_callback:
                self.update_callback(immediate=True)  # 位置变化立即更新
                
        except Exception as e:
            print(f"位置变化处理出错: {e}")

    def on_checkbutton_change(self):
        """复选框变化处理"""
        global_watermark_settings.update_text_setting('bold', self.bold.get())
        global_watermark_settings.update_text_setting('italic', self.italic.get())
        global_watermark_settings.update_text_setting('shadow', self.shadow.get())
        global_watermark_settings.update_text_setting('stroke', self.stroke.get())
        
        if self.update_callback:
            self.update_callback(immediate=True)  # 复选框变化立即更新

    def get_safe_int_value(self, var):
        """安全地获取整数值"""
        try:
            value = var.get()
            if value == "":
                return None
            return int(value)
        except:
            return None

    def on_slider_change(self, value):
        """滑块变化处理"""
        global_watermark_settings.update_text_setting('opacity', self.opacity.get())
        if self.update_callback:
            self.update_callback(immediate=True)  # 滑块变化立即更新

    def confirm_text(self):
        """确认文本更改"""
        global_watermark_settings.update_text_setting('text', self.text_entry.get())
        if self.update_callback:
            self.update_callback(immediate=True)

    def confirm_size(self):
        """确认字号更改 - 修复：确保字号有效"""
        print("确认字号更改")  # 调试信息
        
        font_size_value = self.get_safe_int_value(self.font_size)
        if font_size_value is not None:
            print(f"确认字号: {font_size_value}")  # 调试信息
            global_watermark_settings.update_text_setting('font_size', font_size_value)
            if self.update_callback:
                self.update_callback(immediate=True)
        else:
            # 如果字号无效，恢复默认值
            print("字号无效，恢复默认值")  # 调试信息
            default_size = global_watermark_settings.text_settings.get('font_size', 36)
            self.font_size.set(default_size)
            global_watermark_settings.update_text_setting('font_size', default_size)
            if self.update_callback:
                self.update_callback(immediate=True)

    def confirm_opacity(self):
        """确认透明度更改"""
        global_watermark_settings.update_text_setting('opacity', self.opacity.get())
        if self.update_callback:
            self.update_callback(immediate=True)

    def confirm_stroke(self):
        """确认描边宽度更改"""
        stroke_width_value = self.get_safe_int_value(self.stroke_width)
        if stroke_width_value is not None:
            global_watermark_settings.update_text_setting('stroke_width', stroke_width_value)
            if self.update_callback:
                self.update_callback(immediate=True)

    def choose_color(self):
        """打开颜色选择器"""
        color_code = colorchooser.askcolor(title="选择字体颜色", initialcolor=self.color.get())
        if color_code and color_code[1]:
            self.color.set(color_code[1])
            self.color_preview.config(bg=color_code[1])
            global_watermark_settings.update_text_setting('color', color_code[1])
            if self.update_callback:
                self.update_callback(immediate=True)

    def get_font(self):
        """获取字体对象 - 简化版本"""
        try:
            font_size = global_watermark_settings.text_settings['font_size']
            font_family = global_watermark_settings.text_settings['font_family']
            is_bold = global_watermark_settings.text_settings['bold'] == 1
            is_italic = global_watermark_settings.text_settings['italic'] == 1
            
            # 构建字体名称
            if is_bold and is_italic:
                font_name = f"{font_family} Bold Italic"
            elif is_bold:
                font_name = f"{font_family} Bold"
            elif is_italic:
                font_name = f"{font_family} Italic"
            else:
                font_name = font_family
            
            try:
                # 尝试加载字体
                return ImageFont.truetype(font_name, font_size)
            except:
                # 如果失败，尝试基础字体
                try:
                    base_font = ImageFont.truetype(font_family, font_size)
                    # 使用font_variant应用样式
                    if is_bold and is_italic:
                        return base_font.font_variant(bold=True, italic=True)
                    elif is_bold:
                        return base_font.font_variant(bold=True)
                    elif is_italic:
                        return base_font.font_variant(italic=True)
                    else:
                        return base_font
                except:
                    return ImageFont.load_default()
                    
        except Exception as e:
            print(f"加载字体时出错: {e}")
            return ImageFont.load_default()

    def apply_watermark(self, image):
        """应用文本水印到图片 - 修复：确保使用正确的字号"""
        # 检查图片是否有效
        if image is None:
            print("错误: 图片对象为None")
            return None
            
        if not global_watermark_settings.text_settings['text'].strip():
            return image
            
        try:
            # 创建水印层
            watermark = Image.new("RGBA", image.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(watermark)
            
            # 修复3: 直接使用全局设置中的字号，不进行额外缩放
            font_size = global_watermark_settings.text_settings['font_size']
            print(f"应用水印使用字号: {font_size}")  # 调试信息
            
            # 确保字号不会太小
            if font_size < 12:
                font_size = 12
                
            # 重新创建字体对象
            font_family = global_watermark_settings.text_settings['font_family']
            is_bold = global_watermark_settings.text_settings['bold'] == 1
            is_italic = global_watermark_settings.text_settings['italic'] == 1
            
            if is_bold and is_italic:
                font_name = f"{font_family} Bold Italic"
            elif is_bold:
                font_name = f"{font_family} Bold"
            elif is_italic:
                font_name = f"{font_family} Italic"
            else:
                font_name = font_family
            
            try:
                font = ImageFont.truetype(font_name, font_size)
            except:
                try:
                    base_font = ImageFont.truetype(font_family, font_size)
                    if is_bold and is_italic:
                        font = base_font.font_variant(bold=True, italic=True)
                    elif is_bold:
                        font = base_font.font_variant(bold=True)
                    elif is_italic:
                        font = base_font.font_variant(italic=True)
                    else:
                        font = base_font
                except:
                    font = ImageFont.load_default()
            
            # 获取文本
            text = global_watermark_settings.text_settings['text']
            
            # 计算文本尺寸
            try:
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            except:
                # 如果计算失败，使用估计值
                text_width = len(text) * font_size // 2
                text_height = font_size
            
            # 计算位置
            position = self.get_text_position(image.size, (text_width, text_height))
            
            # 设置透明度
            opacity = int(255 * global_watermark_settings.text_settings['opacity'] / 100)
            color = global_watermark_settings.text_settings['color']
            fill_color = self.hex_to_rgba(color, opacity)
            
            # 应用样式效果
            if global_watermark_settings.text_settings['stroke']:
                self.add_stroke(draw, text, position, font, fill_color)
            elif global_watermark_settings.text_settings['shadow']:
                self.add_shadow(draw, text, position, font, fill_color)
            else:
                draw.text(position, text, font=font, fill=fill_color)
            
            # 合并水印和原图
            return Image.alpha_composite(image.convert("RGBA"), watermark)
            
        except Exception as e:
            print(f"应用文本水印时出错: {e}")
            import traceback
            traceback.print_exc()
            return image
    
    def get_text_position(self, image_size, text_size):
        """根据位置设置计算文本坐标"""
        img_width, img_height = image_size
        text_width, text_height = text_size
        
        position = global_watermark_settings.text_settings['position']
        margin = 20  # 边距
        
        if position == "center":
            return ((img_width - text_width) // 2, (img_height - text_height) // 2)
        elif position == "top-left":
            return (margin, margin)
        elif position == "top":
            return ((img_width - text_width) // 2, margin)
        elif position == "top-right":
            return (img_width - text_width - margin, margin)
        elif position == "left":
            return (margin, (img_height - text_height) // 2)
        elif position == "right":
            return (img_width - text_width - margin, (img_height - text_height) // 2)
        elif position == "bottom-left":
            return (margin, img_height - text_height - margin)
        elif position == "bottom":
            return ((img_width - text_width) // 2, img_height - text_height - margin)
        elif position == "bottom-right":
            return (img_width - text_width - margin, img_height - text_height - margin)
        else:
            return (margin, margin)  # 默认位置
    
    def add_stroke(self, draw, text, position, font, fill_color):
        """添加描边效果"""
        stroke_width = global_watermark_settings.text_settings['stroke_width']
        x, y = position
        
        # 在多个方向绘制文本来创建描边效果
        for dx in [-stroke_width, 0, stroke_width]:
            for dy in [-stroke_width, 0, stroke_width]:
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0, fill_color[3]))
        
        # 绘制主文本
        draw.text(position, text, font=font, fill=fill_color)
    
    def add_shadow(self, draw, text, position, font, fill_color):
        """添加阴影效果"""
        x, y = position
        shadow_color = (0, 0, 0, fill_color[3] // 2)  # 半透明黑色阴影
        draw.text((x + 2, y + 2), text, font=font, fill=shadow_color)
        draw.text(position, text, font=font, fill=fill_color)
    
    def hex_to_rgba(self, hex_color, alpha):
        """将十六进制颜色转换为RGBA"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b, alpha)

    def get_settings(self):
        """获取当前文本水印设置"""
        return global_watermark_settings.text_settings.copy()
    
    def set_settings(self, settings):
        """应用文本水印设置"""
        # 暂时禁用回调
        old_callback = self.update_callback
        self.update_callback = None
        
        self.text_entry.delete(0, END)
        self.text_entry.insert(0, settings.get('text', 'Watermark'))
        
        self.font_family.set(settings.get('font_family', 'Times New Roman'))
        self.font_size.set(settings.get('font_size', 36))
        self.bold.set(settings.get('bold', 0))
        self.italic.set(settings.get('italic', 0))
        self.color.set(settings.get('color', '#FF0000'))
        self.color_preview.config(bg=self.color.get())
        self.opacity.set(settings.get('opacity', 50))
        self.shadow.set(settings.get('shadow', 0))
        self.stroke.set(settings.get('stroke', 0))
        self.stroke_width.set(settings.get('stroke_width', 2))
        self.position.set(settings.get('position', 'center'))
        
        # 更新全局设置
        for key, value in settings.items():
            global_watermark_settings.update_text_setting(key, value)
        
        # 恢复回调
        self.update_callback = old_callback