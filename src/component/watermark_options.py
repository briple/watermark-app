import os
from tkinter import Frame, Label, Entry, Button, Scale, StringVar, OptionMenu, Radiobutton, filedialog, END, IntVar, Toplevel
from PIL import Image, ImageDraw, ImageFont, ImageTk
import tkinter as tk

class TextWatermarkOptions(Frame):
    def __init__(self, master, update_callback=None):
        super().__init__(master)
        self.update_callback = update_callback
        
        # 水印文本 - 单独一行
        Label(self, text="水印文本:").grid(row=0, column=0, sticky='e', padx=5, pady=2)
        self.text_entry = Entry(self, width=25)
        self.text_entry.grid(row=0, column=1, columnspan=4, sticky='w', padx=5, pady=2)
        self.text_entry.insert(0, "Watermark")
        if update_callback:
            self.text_entry.bind('<KeyRelease>', lambda e: update_callback())
        
        # 字体、字号、粗斜体 - 放在一行
        font_frame = Frame(self)
        font_frame.grid(row=1, column=0, columnspan=5, sticky='ew', padx=5, pady=2)
        
        Label(font_frame, text="字体:").pack(side='left', padx=(0, 5))
        self.font_family = StringVar(value="Arial")
        available_fonts = ["Arial", "Helvetica", "Times New Roman", "Courier New", "Verdana", "Tahoma"]
        font_menu = OptionMenu(font_frame, self.font_family, *available_fonts)
        font_menu.pack(side='left', padx=(0, 10))
        if update_callback:
            self.font_family.trace('w', lambda *args: update_callback())
        
        Label(font_frame, text="字号:").pack(side='left', padx=(0, 5))
        self.font_size = IntVar(value=36)
        font_size_entry = Entry(font_frame, textvariable=self.font_size, width=4)
        font_size_entry.pack(side='left', padx=(0, 10))
        if update_callback:
            self.font_size.trace('w', lambda *args: update_callback())
        
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
        self.opacity = Scale(color_frame, from_=0, to=100, orient='horizontal', length=120)
        self.opacity.set(50)
        self.opacity.pack(side='left', fill='x', expand=True)
        if update_callback:
            self.opacity.config(command=lambda e: update_callback())
        
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
        stroke_entry.pack(side='left')
        if update_callback:
            self.stroke_width.trace('w', lambda *args: update_callback())
        
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
        """获取字体对象"""
        try:
            font_size = self.font_size.get()
            font_family = self.font_family.get()
            
            # 构建字体路径或名称，考虑粗体和斜体
            # 对于常见字体，我们可以尝试不同的字体变体名称
            font_variants = {
                (False, False): font_family,  # 常规
                (True, False): f"{font_family} Bold",  # 粗体
                (False, True): f"{font_family} Italic",  # 斜体
                (True, True): f"{font_family} Bold Italic"  # 粗斜体
            }
            
            variant_key = (self.bold.get() == 1, self.italic.get() == 1)
            font_name = font_variants[variant_key]
            
            try:
                # 首先尝试直接加载指定名称的字体
                return ImageFont.truetype(font_name, font_size)
            except:
                # 如果失败，尝试加载基础字体并使用字体变体
                try:
                    base_font = ImageFont.truetype(font_family, font_size)
                    
                    # 使用font_variant方法应用样式
                    if self.bold.get() and self.italic.get():
                        return base_font.font_variant(bold=True, italic=True)
                    elif self.bold.get():
                        return base_font.font_variant(bold=True)
                    elif self.italic.get():
                        return base_font.font_variant(italic=True)
                    else:
                        return base_font
                except:
                    # 如果都失败，使用默认字体
                    return ImageFont.load_default()
                    
        except Exception as e:
            print(f"加载字体时出错: {e}")
            return ImageFont.load_default()

    def apply_watermark(self, image):
        """应用文本水印到图片"""
        if not self.text_entry.get().strip():
            return image
            
        # 创建水印层
        watermark = Image.new("RGBA", image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(watermark)
        
        # 获取字体
        font = self.get_font()
        
        # 计算文本位置
        text = self.text_entry.get()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
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
        self.scale_percent = Scale(scale_opacity_frame, from_=10, to=200, orient='horizontal', length=120)
        self.scale_percent.set(30)
        self.scale_percent.pack(side='left', padx=(0, 20), fill='x', expand=True)
        if update_callback:
            self.scale_percent.config(command=lambda e: update_callback())
        
        Label(scale_opacity_frame, text="透明度:").pack(side='left', padx=(0, 5))
        self.opacity = Scale(scale_opacity_frame, from_=0, to=100, orient='horizontal', length=120)
        self.opacity.set(50)
        self.opacity.pack(side='left', fill='x', expand=True)
        if update_callback:
            self.opacity.config(command=lambda e: update_callback())
        
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
        """应用图片水印到基础图片"""
        if not self.image_path.get():
            return base_image
            
        try:
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


class WatermarkOptions(Frame):
    def __init__(self, master, images_ref, output_format_ref, update_callback=None):
        super().__init__(master)
        self.images_ref = images_ref
        self.output_format_ref = output_format_ref
        self.update_callback = update_callback

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
        self.text_options = TextWatermarkOptions(self, update_callback)
        self.image_options = ImageWatermarkOptions(self, update_callback)
        
        self.text_options.grid(row=1, column=0, columnspan=3, sticky='ew', padx=5, pady=5)
        self.image_options.grid(row=1, column=0, columnspan=3, sticky='ew', padx=5, pady=5)
        
        # 默认显示文本水印
        self.image_options.grid_remove()

        # 导出设置 - 紧凑布局
        export_frame = Frame(self)
        export_frame.grid(row=2, column=0, columnspan=3, sticky='ew', padx=5, pady=5)
        
        Label(export_frame, text="导出文件夹:").pack(side='left', padx=(0, 5))
        self.export_folder = Entry(export_frame, width=25)
        self.export_folder.pack(side='left', padx=(0, 5))
        Button(export_frame, text="选择", command=self.select_export_folder, width=6).pack(side='left', padx=(0, 10))
        
        # 导出按钮
        self.export_btn = Button(export_frame, text="批量导出", command=self.add_watermark_and_export,
                                bg="#4CAF50", fg="black", font=("Arial", 10, "bold"), width=10, padx=10)
        self.export_btn.pack(side='left')

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
            self.export_folder.delete(0, END)
            self.export_folder.insert(0, folder)

    def apply_watermark_preview(self, image):
        """应用水印用于预览"""
        if self.watermark_type.get() == "text":
            return self.text_options.apply_watermark(image)
        else:
            return self.image_options.apply_watermark(image)

    def add_watermark_and_export(self):
        """批量添加水印并导出"""
        images = self.images_ref
        if not images:
            self.show_message("错误", "请先上传图片")
            return
            
        export_dir = self.export_folder.get()
        if not export_dir or not os.path.exists(export_dir):
            self.show_message("错误", "请选择有效的导出文件夹")
            return

        output_format = self.output_format_ref.get()
        
        success_count = 0
        for img_path, _, _ in images:
            try:
                # 打开原图
                original_img = Image.open(img_path).convert("RGBA")
                
                # 应用水印
                watermarked_img = self.apply_watermark_preview(original_img)
                
                # 生成输出文件名
                basename = os.path.splitext(os.path.basename(img_path))[0]
                ext = ".png" if output_format == "PNG" else ".jpg"
                outname = f"{basename}_watermarked{ext}"
                outpath = os.path.join(export_dir, outname)
                
                # 保存图片
                if output_format == "JPEG":
                    watermarked_img = watermarked_img.convert("RGB")
                watermarked_img.save(outpath, output_format)
                success_count += 1
                
            except Exception as e:
                print(f"处理图片 {img_path} 时出错: {e}")
        
        self.show_message("完成", f"成功导出 {success_count}/{len(images)} 张图片")

    def show_message(self, title, message):
        """显示消息对话框"""
        dialog = Toplevel(self)
        dialog.title(title)
        dialog.geometry("300x100")
        dialog.transient(self)
        dialog.grab_set()
        
        Label(dialog, text=message, pady=20).pack()
        Button(dialog, text="确定", command=dialog.destroy).pack()