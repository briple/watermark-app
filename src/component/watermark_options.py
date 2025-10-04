import os
import platform
import json
from tkinter import Frame, Label, Entry, Button, Scale, StringVar, OptionMenu, Radiobutton, filedialog, END, IntVar, Toplevel, Listbox, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk
import tkinter as tk

class TextWatermarkOptions(Frame):
    def __init__(self, master, update_callback=None):
        super().__init__(master)
        self.update_callback = update_callback
        
        # 水印文本 - 单独一行
        Label(self, text="水印文本:").grid(row=0, column=0, sticky='e', padx=5, pady=2)
        self.text_entry = Entry(self, width=18)
        self.text_entry.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        self.text_entry.insert(0, "Watermark")
        
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
        self.font_family = StringVar(value="Times New Roman")
        
        font_menu = OptionMenu(font_frame, self.font_family, *self.available_fonts)
        font_menu.config(width=12)
        font_menu.pack(side='left', padx=(0, 10))
        if update_callback:
            self.font_family.trace('w', lambda *args: update_callback())
        
        Label(font_frame, text="字号:").pack(side='left', padx=(0, 5))
        self.font_size = IntVar(value=36)
        font_size_entry = Entry(font_frame, textvariable=self.font_size, width=4)
        font_size_entry.pack(side='left', padx=(0, 5))
        
        # 字号确认按钮
        self.size_confirm_btn = Button(font_frame, text="确认", command=self.confirm_size, width=6)
        self.size_confirm_btn.pack(side='left', padx=(0, 10))
        
        self.bold = IntVar(value=0)
        bold_cb = tk.Checkbutton(font_frame, text="粗体", variable=self.bold)
        bold_cb.pack(side='left', padx=(0, 5))
        if update_callback:
            bold_cb.config(command=update_callback)
        
        self.italic = IntVar(value=0)
        italic_cb = tk.Checkbutton(font_frame, text="斜体", variable=self.italic)
        italic_cb.pack(side='left')
        if update_callback:
            italic_cb.config(command=update_callback)
        
        # 颜色和透明度 - 放在一行
        color_frame = Frame(self)
        color_frame.grid(row=2, column=0, columnspan=5, sticky='ew', padx=5, pady=2)
        
        Label(color_frame, text="颜色:").pack(side='left', padx=(0, 5))
        self.color = StringVar(value="#FF0000")
        self.color_preview = Label(color_frame, text="    ", bg=self.color.get(), relief="solid", bd=1, width=4)
        self.color_preview.pack(side='left', padx=(0, 10))
        Button(color_frame, text="选择颜色", command=self.choose_color, width=8).pack(side='left', padx=(0, 15))
        
        Label(color_frame, text="透明度:").pack(side='left', padx=(0, 5))
        self.opacity = Scale(color_frame, from_=0, to=100, orient='horizontal', length=100)
        self.opacity.set(50)
        self.opacity.pack(side='left', padx=(0, 5), fill='x', expand=True)
        
        # 透明度确认按钮
        self.opacity_confirm_btn = Button(color_frame, text="确认", command=self.confirm_opacity, width=6)
        self.opacity_confirm_btn.pack(side='left', padx=(5, 0))
        
        # 样式效果和描边宽度 - 放在一行
        style_frame = Frame(self)
        style_frame.grid(row=3, column=0, columnspan=5, sticky='ew', padx=5, pady=2)
        
        Label(style_frame, text="样式效果:").pack(side='left', padx=(0, 5))
        self.shadow = IntVar(value=0)
        shadow_cb = tk.Checkbutton(style_frame, text="阴影", variable=self.shadow)
        shadow_cb.pack(side='left', padx=(0, 10))
        if update_callback:
            shadow_cb.config(command=update_callback)
        
        self.stroke = IntVar(value=0)
        stroke_cb = tk.Checkbutton(style_frame, text="描边", variable=self.stroke)
        stroke_cb.pack(side='left', padx=(0, 10))
        if update_callback:
            stroke_cb.config(command=update_callback)
        
        Label(style_frame, text="描边宽度:").pack(side='left', padx=(0, 5))
        self.stroke_width = IntVar(value=2)
        stroke_entry = Entry(style_frame, textvariable=self.stroke_width, width=3)
        stroke_entry.pack(side='left', padx=(0, 5))
        
        # 描边宽度确认按钮
        self.stroke_confirm_btn = Button(style_frame, text="确认", command=self.confirm_stroke, width=6)
        self.stroke_confirm_btn.pack(side='left')
        
        # 位置选择 - 单独一行
        position_frame = Frame(self)
        position_frame.grid(row=4, column=0, columnspan=5, sticky='ew', padx=5, pady=2)
        
        Label(position_frame, text="位置:").pack(side='left', padx=(0, 10))
        # 更新位置选项以匹配九宫格
        self.position = StringVar(value="center")
        positions = ["top-left", "top", "top-right", 
                    "left", "center", "right", 
                    "bottom-left", "bottom", "bottom-right"]
        position_menu = OptionMenu(position_frame, self.position, *positions)
        position_menu.pack(side='left')
        if update_callback:
            self.position.trace('w', lambda *args: update_callback())

    def confirm_text(self):
        """确认文本更改"""
        if self.update_callback:
            self.update_callback()

    def confirm_size(self):
        """确认字号更改"""
        if self.update_callback:
            self.update_callback()

    def confirm_opacity(self):
        """确认透明度更改"""
        if self.update_callback:
            self.update_callback()

    def confirm_stroke(self):
        """确认描边宽度更改"""
        if self.update_callback:
            self.update_callback()

    def choose_color(self):
        """打开颜色选择器"""
        from tkinter import colorchooser
        color_code = colorchooser.askcolor(title="选择字体颜色", initialcolor=self.color.get())
        if color_code and color_code[1]:
            self.color.set(color_code[1])
            self.color_preview.config(bg=color_code[1])
            if self.update_callback:
                self.update_callback()
    
    def get_font(self):
        """获取字体对象 - 简化版本"""
        try:
            font_size = self.font_size.get()
            font_family = self.font_family.get()
            is_bold = self.bold.get() == 1
            is_italic = self.italic.get() == 1
            
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
        """应用文本水印到图片 - 修复版本"""
        # 检查图片是否有效
        if image is None:
            print("错误: 图片对象为None")
            return None
            
        if not self.text_entry.get().strip():
            return image
            
        try:
            # 创建水印层
            watermark = Image.new("RGBA", image.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(watermark)
            
            # 获取字体 - 使用基于图片尺寸的固定比例
            base_size = min(image.width, image.height)
            font_scale = 0.04  # 4% 的图片高度
            font_size = max(12, int(base_size * font_scale))
            
            # 重新创建字体对象
            font_family = self.font_family.get()
            is_bold = self.bold.get() == 1
            is_italic = self.italic.get() == 1
            
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
            text = self.text_entry.get()
            
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
            opacity = int(255 * self.opacity.get() / 100)
            color = self.color.get()
            fill_color = self.hex_to_rgba(color, opacity)
            
            # 应用样式效果
            if self.stroke.get():
                self.add_stroke(draw, text, position, font, fill_color)
            elif self.shadow.get():
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
        
        position = self.position.get()
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
        stroke_width = self.stroke_width.get()
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
        return {
            'text': self.text_entry.get(),
            'font_family': self.font_family.get(),
            'font_size': self.font_size.get(),
            'bold': self.bold.get(),
            'italic': self.italic.get(),
            'color': self.color.get(),
            'opacity': self.opacity.get(),
            'shadow': self.shadow.get(),
            'stroke': self.stroke.get(),
            'stroke_width': self.stroke_width.get(),
            'position': self.position.get()
        }
    
    def set_settings(self, settings):
        """应用文本水印设置"""
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

class ImageWatermarkOptions(Frame):
    def __init__(self, master, update_callback=None):
        super().__init__(master)
        self.update_callback = update_callback
        
        # 水印图片选择 - 单独一行
        Label(self, text="水印图片:").grid(row=0, column=0, sticky='e', padx=5, pady=2)
        self.image_path = StringVar()
        Button(self, text="选择PNG图片", command=self.select_image, width=12).grid(row=0, column=1, sticky='w', padx=5, pady=2)
        self.path_label = Label(self, text="未选择", fg="gray", width=15, anchor='w')
        self.path_label.grid(row=0, column=2, columnspan=2, sticky='w', padx=5, pady=2)
        
        # 缩放比例和透明度 - 放在一行
        scale_opacity_frame = Frame(self)
        scale_opacity_frame.grid(row=1, column=0, columnspan=4, sticky='ew', padx=5, pady=2)
        
        Label(scale_opacity_frame, text="缩放比例(%):").pack(side='left', padx=(0, 5))
        self.scale_percent = Scale(scale_opacity_frame, from_=10, to=200, orient='horizontal', length=100)
        self.scale_percent.set(30)
        self.scale_percent.pack(side='left', padx=(0, 10), fill='x', expand=True)
        
        # 缩放比例确认按钮
        self.scale_confirm_btn = Button(scale_opacity_frame, text="确认", command=self.confirm_scale, width=6)
        self.scale_confirm_btn.pack(side='left', padx=(0, 20))
        
        Label(scale_opacity_frame, text="透明度:").pack(side='left', padx=(0, 5))
        self.opacity = Scale(scale_opacity_frame, from_=0, to=100, orient='horizontal', length=100)
        self.opacity.set(50)
        self.opacity.pack(side='left', padx=(0, 10), fill='x', expand=True)
        
        # 透明度确认按钮
        self.opacity_confirm_btn = Button(scale_opacity_frame, text="确认", command=self.confirm_opacity, width=6)
        self.opacity_confirm_btn.pack(side='left')
        
        # 位置选择 - 单独一行
        position_frame = Frame(self)
        position_frame.grid(row=2, column=0, columnspan=4, sticky='ew', padx=5, pady=2)
        
        Label(position_frame, text="位置:").pack(side='left', padx=(0, 10))
        # 更新位置选项以匹配九宫格
        self.position = StringVar(value="center")
        positions = ["top-left", "top", "top-right", 
                    "left", "center", "right", 
                    "bottom-left", "bottom", "bottom-right"]
        position_menu = OptionMenu(position_frame, self.position, *positions)
        position_menu.pack(side='left')
        if update_callback:
            self.position.trace('w', lambda *args: update_callback())

    def confirm_scale(self):
        """确认缩放比例更改"""
        if self.update_callback:
            self.update_callback()

    def confirm_opacity(self):
        """确认透明度更改"""
        if self.update_callback:
            self.update_callback()

    def select_image(self):
        """选择水印图片"""
        path = filedialog.askopenfilename(
            title="选择水印图片",
            filetypes=[("PNG Images", "*.png"), ("All files", "*.*")]
        )
        if path:
            self.image_path.set(path)
            self.path_label.config(text=os.path.basename(path))
            if self.update_callback:
                self.update_callback()
    
    def apply_watermark(self, base_image):
        """应用图片水印到基础图片 - 修复版本"""
        # 检查图片是否有效
        if base_image is None:
            print("错误: 基础图片对象为None")
            return None
            
        if not self.image_path.get():
            return base_image
            
        try:
            # 检查水印图片文件是否存在
            if not os.path.exists(self.image_path.get()):
                print(f"错误: 水印图片文件不存在: {self.image_path.get()}")
                return base_image
                
            # 打开水印图片
            watermark = Image.open(self.image_path.get()).convert("RGBA")
            
            # 缩放水印 - 基于图片尺寸的百分比
            scale_factor = self.scale_percent.get() / 100.0
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
            opacity = self.opacity.get() / 100.0
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
        
        position = self.position.get()
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
        return {
            'image_path': self.image_path.get(),
            'scale_percent': self.scale_percent.get(),
            'opacity': self.opacity.get(),
            'position': self.position.get()
        }
    
    def set_settings(self, settings):
        """应用图片水印设置"""
        self.image_path.set(settings.get('image_path', ''))
        if self.image_path.get():
            self.path_label.config(text=os.path.basename(self.image_path.get()))
        else:
            self.path_label.config(text="未选择")
        
        self.scale_percent.set(settings.get('scale_percent', 30))
        self.opacity.set(settings.get('opacity', 50))
        self.position.set(settings.get('position', 'center'))

class TemplateManager:
    def __init__(self, template_file="watermark_templates.json"):
        self.template_file = template_file
        self.templates = self.load_templates()
    
    def load_templates(self):
        """加载模板文件"""
        if os.path.exists(self.template_file):
            try:
                with open(self.template_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载模板文件失败: {e}")
                return {}
        return {}
    
    def save_templates(self):
        """保存模板到文件"""
        try:
            with open(self.template_file, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存模板文件失败: {e}")
            return False
    
    def save_template(self, name, watermark_type, text_settings, image_settings):
        """保存模板"""
        self.templates[name] = {
            'watermark_type': watermark_type,
            'text_settings': text_settings,
            'image_settings': image_settings,
            'timestamp': os.path.getmtime(self.template_file) if os.path.exists(self.template_file) else 0
        }
        return self.save_templates()
    
    def load_template(self, name):
        """加载模板"""
        return self.templates.get(name)
    
    def delete_template(self, name):
        """删除模板"""
        if name in self.templates:
            del self.templates[name]
            return self.save_templates()
        return False
    
    def get_template_names(self):
        """获取所有模板名称"""
        return list(self.templates.keys())

class WatermarkOptions(Frame):
    def __init__(self, master, images_ref, output_format_ref, update_callback=None):
        super().__init__(master)
        self.images_ref = images_ref
        self.output_format_ref = output_format_ref
        self.update_callback = update_callback
        self.master_ref = master
        
        # 初始化模板管理器
        self.template_manager = TemplateManager()
        
        # 水印类型选择 - 紧凑布局
        type_frame = Frame(self)
        type_frame.grid(row=0, column=0, columnspan=3, sticky='w', padx=5, pady=5)
        
        Label(type_frame, text="水印类型:").pack(side='left', padx=(0, 10))
        self.watermark_type = StringVar(value="text")
        
        Radiobutton(type_frame, text="文本水印", variable=self.watermark_type, 
                   value="text", command=self.switch_watermark_type).pack(side='left', padx=(0, 15))
        Radiobutton(type_frame, text="图片水印", variable=self.watermark_type, 
                   value="image", command=self.switch_watermark_type).pack(side='left')

        # 创建两种水印选项
        self.text_options = TextWatermarkOptions(self, self.update_preview_callback)
        self.image_options = ImageWatermarkOptions(self, self.update_preview_callback)
        
        self.text_options.grid(row=1, column=0, columnspan=3, sticky='ew', padx=5, pady=5)
        self.image_options.grid(row=1, column=0, columnspan=3, sticky='ew', padx=5, pady=5)
        
        # 默认显示文本水印
        self.image_options.grid_remove()

        # 导出设置 - 扩展布局
        export_frame = Frame(self)
        export_frame.grid(row=2, column=0, columnspan=3, sticky='ew', padx=5, pady=5)
        
        # 第一行：导出文件夹和命名规则
        export_row1 = Frame(export_frame)
        export_row1.pack(fill='x', pady=(0, 5))
        
        Label(export_row1, text="导出文件夹:").pack(side='left', padx=(0, 5))
        self.export_folder = Entry(export_row1, width=20)
        self.export_folder.pack(side='left', padx=(0, 5))
        Button(export_row1, text="选择", command=self.select_export_folder, width=6).pack(side='left', padx=(0, 15))
        
        Label(export_row1, text="命名规则:").pack(side='left', padx=(0, 5))
        self.naming_rule = StringVar(value="添加后缀")
        naming_menu = OptionMenu(export_row1, self.naming_rule, "原文件名", "添加前缀", "添加后缀")
        naming_menu.config(width=10)
        naming_menu.pack(side='left', padx=(0, 5))
        
        self.custom_text = Entry(export_row1, width=12)
        self.custom_text.pack(side='left', padx=(0, 5))
        self.custom_text.insert(0, "_watermarked")
        
        # 第二行：图片质量和缩放设置
        export_row2 = Frame(export_frame)
        export_row2.pack(fill='x', pady=(0, 5))
        
        # 图片质量设置（仅对JPEG有效）
        Label(export_row2, text="JPEG质量:").pack(side='left', padx=(0, 5))
        self.quality = Scale(export_row2, from_=1, to=100, orient='horizontal', length=120)
        self.quality.set(95)
        self.quality.pack(side='left', padx=(0, 15))
        
        # 图片缩放设置
        Label(export_row2, text="缩放比例(%):").pack(side='left', padx=(0, 5))
        self.scale_percent = Scale(export_row2, from_=10, to=200, orient='horizontal', length=120)
        self.scale_percent.set(100)
        self.scale_percent.pack(side='left', padx=(0, 5))
        
        # 第三行：导出按钮和模板管理
        export_row3 = Frame(export_frame)
        export_row3.pack(fill='x', pady=(5, 0))
        
        # 导出按钮
        self.export_btn = Button(export_row3, text="批量导出", command=self.add_watermark_and_export,
                                bg="#4CAF50", fg="black", font=("Arial", 10, "bold"), width=10, padx=10)
        self.export_btn.pack(side='left', padx=(0, 10))
        
        # 模板管理按钮
        self.template_btn = Button(export_row3, text="模板管理", command=self.manage_templates,
                                  bg="#2196F3", fg="black", font=("Arial", 10), width=8)
        self.template_btn.pack(side='left', padx=(0, 5))
        
        # 保存模板按钮
        self.save_template_btn = Button(export_row3, text="保存模板", command=self.save_current_template,
                                       bg="#FF9800", fg="black", font=("Arial", 10), width=8)
        self.save_template_btn.pack(side='left', padx=(0, 5))
        
        # 加载默认模板
        self.load_default_template()

    def update_preview_callback(self):
        """包装更新回调，确保不会丢失图片选择状态"""
        if self.update_callback:
            self.update_callback()

    def switch_watermark_type(self):
        """切换水印类型显示"""
        if self.watermark_type.get() == "text":
            self.text_options.grid()
            self.image_options.grid_remove()
        else:
            self.text_options.grid_remove()
            self.image_options.grid()
        
        if self.update_callback:
            self.update_callback()

    def select_export_folder(self):
        """选择导出文件夹"""
        folder = filedialog.askdirectory(title="选择导出文件夹")
        if folder:
            # 检查是否选择了原文件夹
            original_folders = set()
            for image_data in self.images_ref:
                if image_data and len(image_data) > 0:
                    original_folder = os.path.dirname(image_data[0])
                    original_folders.add(original_folder)
            
            if folder in original_folders:
                self.show_message("警告", "为了安全起见，请不要导出到原文件夹！\n请选择其他文件夹。")
                return
            
            self.export_folder.delete(0, END)
            self.export_folder.insert(0, folder)

    def apply_watermark_preview(self, image):
        """应用水印用于预览 - 修复版本"""
        # 检查图片是否有效
        if image is None:
            print("错误: 预览图片对象为None")
            return None
            
        try:
            if self.watermark_type.get() == "text":
                result = self.text_options.apply_watermark(image)
            else:
                result = self.image_options.apply_watermark(image)
            
            # 检查结果是否有效
            if result is None:
                print("警告: 水印应用返回了None，返回原图")
                return image
            return result
            
        except Exception as e:
            print(f"应用水印预览时出错: {e}")
            import traceback
            traceback.print_exc()
            return image

    def add_watermark_and_export(self):
        """批量添加水印并导出 - 修复版本"""
        images = self.images_ref
        if not images:
            self.show_message("错误", "请先上传图片")
            return
            
        export_dir = self.export_folder.get()
        if not export_dir or not os.path.exists(export_dir):
            self.show_message("错误", "请选择有效的导出文件夹")
            return

        output_format = self.output_format_ref.get()
        
        # 检查是否导出到原文件夹
        original_folders = set()
        for image_data in images:
            if image_data and len(image_data) > 0:
                original_folder = os.path.dirname(image_data[0])
                original_folders.add(original_folder)
        
        if export_dir in original_folders:
            self.show_message("错误", "为了安全起见，禁止导出到原文件夹！\n请选择其他文件夹。")
            return

        success_count = 0
        total_count = len(images)
        
        for i, image_data in enumerate(images):
            try:
                # 正确获取文件路径（第一个元素）
                img_path = image_data[0]
                
                print(f"正在处理第 {i+1}/{total_count} 张图片: {os.path.basename(img_path)}")
                
                # 检查文件是否存在
                if not os.path.exists(img_path):
                    print(f"错误: 图片文件不存在: {img_path}")
                    continue
                
                # 每次都重新从文件加载原图
                with Image.open(img_path) as original_img:
                    # 转换为RGBA模式
                    if original_img.mode != 'RGBA':
                        original_img = original_img.convert("RGBA")
                    
                    # 应用水印
                    watermarked_img = self.apply_watermark_preview(original_img)
                    
                    if watermarked_img is None:
                        print(f"警告: 图片 {img_path} 水印应用失败，跳过")
                        continue
                    
                    # 应用图片缩放
                    scale_factor = self.scale_percent.get() / 100.0
                    if scale_factor != 1.0:
                        new_width = int(watermarked_img.width * scale_factor)
                        new_height = int(watermarked_img.height * scale_factor)
                        watermarked_img = watermarked_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # 生成输出文件名
                    basename = os.path.splitext(os.path.basename(img_path))[0]
                    ext = ".png" if output_format == "PNG" else ".jpg"
                    
                    # 根据命名规则生成文件名
                    naming_rule = self.naming_rule.get()
                    custom_text = self.custom_text.get().strip()
                    
                    if naming_rule == "原文件名":
                        outname = f"{basename}{ext}"
                    elif naming_rule == "添加前缀" and custom_text:
                        outname = f"{custom_text}{basename}{ext}"
                    elif naming_rule == "添加后缀" and custom_text:
                        outname = f"{basename}{custom_text}{ext}"
                    else:
                        outname = f"{basename}_watermarked{ext}"
                    
                    outpath = os.path.join(export_dir, outname)
                    
                    # 如果文件已存在，添加数字后缀
                    counter = 1
                    while os.path.exists(outpath):
                        if naming_rule == "原文件名":
                            outname = f"{basename}_{counter}{ext}"
                        elif naming_rule == "添加前缀" and custom_text:
                            outname = f"{custom_text}{basename}_{counter}{ext}"
                        elif naming_rule == "添加后缀" and custom_text:
                            outname = f"{basename}{custom_text}_{counter}{ext}"
                        else:
                            outname = f"{basename}_watermarked_{counter}{ext}"
                        outpath = os.path.join(export_dir, outname)
                        counter += 1
                    
                    # 保存图片
                    save_kwargs = {}
                    if output_format == "JPEG":
                        watermarked_img = watermarked_img.convert("RGB")
                        save_kwargs['quality'] = self.quality.get()
                        save_kwargs['optimize'] = True
                    
                    watermarked_img.save(outpath, output_format, **save_kwargs)
                    print(f"成功导出: {outname}")
                    success_count += 1
                    
            except Exception as e:
                print(f"处理图片 {image_data[0]} 时出错: {e}")
                import traceback
                traceback.print_exc()
        
        # 显示结果
        if success_count == total_count:
            self.show_message("完成", f"成功导出所有 {success_count} 张图片到:\n{export_dir}")
        elif success_count > 0:
            self.show_message("部分完成", 
                            f"成功导出 {success_count}/{total_count} 张图片\n"
                            f"失败: {total_count - success_count} 张\n"
                            f"导出到: {export_dir}")
        else:
            self.show_message("失败", "所有图片导出失败，请查看控制台错误信息")

    def show_message(self, title, message):
        """显示消息对话框"""
        dialog = Toplevel(self)
        dialog.title(title)
        dialog.geometry("400x150")
        dialog.transient(self)
        dialog.grab_set()
        
        Label(dialog, text=message, pady=20, justify='left').pack()
        Button(dialog, text="确定", command=dialog.destroy).pack()

    # 模板管理相关方法
    def save_current_template(self):
        """保存当前设置为模板"""
        template_name = tk.simpledialog.askstring("保存模板", "请输入模板名称:")
        if not template_name:
            return
        
        if template_name in self.template_manager.get_template_names():
            if not messagebox.askyesno("确认", f"模板 '{template_name}' 已存在，是否覆盖？"):
                return
        
        # 获取当前设置
        watermark_type = self.watermark_type.get()
        text_settings = self.text_options.get_settings()
        image_settings = self.image_options.get_settings()
        
        # 保存模板
        if self.template_manager.save_template(template_name, watermark_type, text_settings, image_settings):
            messagebox.showinfo("成功", f"模板 '{template_name}' 保存成功！")
        else:
            messagebox.showerror("错误", "保存模板失败！")

    def manage_templates(self):
        """管理模板对话框"""
        dialog = Toplevel(self)
        dialog.title("水印模板管理")
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()
        
        # 模板列表
        list_frame = Frame(dialog)
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        Label(list_frame, text="已保存的模板:", font=("Arial", 10, "bold")).pack(anchor='w')
        
        template_list = Listbox(list_frame, height=10)
        template_list.pack(fill='both', expand=True, pady=5)
        
        # 刷新模板列表
        def refresh_list():
            template_list.delete(0, END)
            for name in self.template_manager.get_template_names():
                template_list.insert(END, name)
        
        refresh_list()
        
        # 按钮框架
        btn_frame = Frame(dialog)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        # 加载模板按钮
        def load_selected_template():
            selection = template_list.curselection()
            if not selection:
                messagebox.showwarning("警告", "请先选择一个模板！")
                return
            
            template_name = template_list.get(selection[0])
            template = self.template_manager.load_template(template_name)
            if template:
                self.apply_template(template)
                dialog.destroy()
                messagebox.showinfo("成功", f"模板 '{template_name}' 加载成功！")
            else:
                messagebox.showerror("错误", "加载模板失败！")
        
        Button(btn_frame, text="加载模板", command=load_selected_template, width=10).pack(side='left', padx=5)
        
        # 删除模板按钮
        def delete_selected_template():
            selection = template_list.curselection()
            if not selection:
                messagebox.showwarning("警告", "请先选择一个模板！")
                return
            
            template_name = template_list.get(selection[0])
            if messagebox.askyesno("确认", f"确定要删除模板 '{template_name}' 吗？"):
                if self.template_manager.delete_template(template_name):
                    refresh_list()
                    messagebox.showinfo("成功", f"模板 '{template_name}' 删除成功！")
                else:
                    messagebox.showerror("错误", "删除模板失败！")
        
        Button(btn_frame, text="删除模板", command=delete_selected_template, width=10).pack(side='left', padx=5)
        
        # 关闭按钮
        Button(btn_frame, text="关闭", command=dialog.destroy, width=10).pack(side='right', padx=5)
        
        refresh_list()

    def apply_template(self, template):
        """应用模板设置"""
        # 设置水印类型
        self.watermark_type.set(template.get('watermark_type', 'text'))
        self.switch_watermark_type()
        
        # 应用文本水印设置
        self.text_options.set_settings(template.get('text_settings', {}))
        
        # 应用图片水印设置
        self.image_options.set_settings(template.get('image_settings', {}))
        
        # 更新预览
        if self.update_callback:
            self.update_callback()

    def load_default_template(self):
        """加载默认模板"""
        template_names = self.template_manager.get_template_names()
        if template_names:
            # 尝试加载名为"默认"的模板，否则加载第一个模板
            default_template = self.template_manager.load_template("默认")
            if not default_template and template_names:
                default_template = self.template_manager.load_template(template_names[0])
            
            if default_template:
                self.apply_template(default_template)
                print("默认模板加载成功")