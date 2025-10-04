import os
from tkinter import Frame, Button, Listbox, filedialog, Label, Scrollbar, Canvas, NW, StringVar, OptionMenu, RIGHT, Y, BOTH, END
from PIL import Image, ImageTk, ImageDraw
from component.watermark_options import WatermarkOptions
from tkinterdnd2 import TkinterDnD, DND_FILES

SUPPORTED_FORMATS = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif')

class ImageUploader(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.images = []  # [(filepath, original_thumb_tk, watermarked_thumb_tk, original_image)]
        self.selected_index = None
        self.watermark_options = None
        self.current_watermark_pos = None
        self.dragging_watermark = False
        self.drag_start_pos = None
        self.custom_position = None  # 保存自定义位置 (rel_x, rel_y)
        self.saved_scroll_position = (0.0, 0.0)  # 保存滚动位置
        
        # 左侧区域：文件列表
        left_frame = Frame(self)
        left_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky='ns')
        
        # 图片列表及滚动条
        Label(left_frame, text="图片列表", font=("Arial", 10, "bold")).pack(pady=(0, 5))
        self.file_list = Listbox(left_frame, width=25, height=15)
        self.file_list.pack(side='left', fill='both', expand=True)
        self.file_list.bind('<<ListboxSelect>>', self.show_thumbnail)

        self.scrollbar = Scrollbar(left_frame)
        self.scrollbar.pack(side='right', fill='y')
        self.file_list.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.file_list.yview)

        # 右侧区域：拖拽上传和预览
        right_frame = Frame(self)
        right_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky='nsew')

        # 拖拽上传区域
        self.drag_label = Label(right_frame, text="拖拽图片或文件到此处上传", 
                               relief="groove", width=60, height=3,
                               font=("Arial", 10), bg="#f0f0f0")
        self.drag_label.pack(fill='x', pady=(0, 10))
        self.drag_label.drop_target_register(DND_FILES)
        self.drag_label.dnd_bind('<<Drop>>', self.drop_files)

        # 预览区域
        preview_frame = Frame(right_frame)
        preview_frame.pack(fill='both', expand=True)
        
        Label(preview_frame, text="图片预览 (带九宫格参考线)", font=("Arial", 10, "bold")).pack(pady=(0, 5))
        
        # 创建Canvas和滚动条容器
        canvas_container = Frame(preview_frame)
        canvas_container.pack(fill='both', expand=True)
        
        # 创建Canvas和垂直滚动条
        self.canvas = Canvas(canvas_container, bg="white", relief="solid", bd=1)
        self.canvas_vscroll = Scrollbar(canvas_container, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.canvas_vscroll.set)
        
        # 布局Canvas和滚动条
        self.canvas.pack(side='left', fill='both', expand=True)
        self.canvas_vscroll.pack(side='right', fill='y')
        
        # 绑定鼠标事件用于水印拖拽
        self.canvas.bind("<ButtonPress-1>", self.on_watermark_press)
        self.canvas.bind("<B1-Motion>", self.on_watermark_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_watermark_release)
        
        # 绑定鼠标滚轮事件
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)

        # 九宫格位置选择按钮
        self.position_frame = Frame(preview_frame)
        self.position_frame.pack(fill='x', pady=(10, 0))
        
        Label(self.position_frame, text="预设位置:").pack(side='left')
        
        # 创建九宫格位置按钮
        positions = [
            ("左上", "top-left"), ("中上", "top"), ("右上", "top-right"),
            ("左中", "left"), ("居中", "center"), ("右中", "right"),
            ("左下", "bottom-left"), ("中下", "bottom"), ("右下", "bottom-right")
        ]
        
        for text, pos in positions:
            btn = Button(self.position_frame, text=text, width=6,
                        command=lambda p=pos: self.set_watermark_position(p))
            btn.pack(side='left', padx=2)

        # 按钮容器 Frame
        self.button_frame = Frame(self)
        self.button_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky='ew')

        # 选择图片按钮
        self.upload_btn = Button(self.button_frame, text="选择图片", command=self.upload_files)
        self.upload_btn.grid(row=0, column=0, padx=10, pady=5)

        # 选择文件夹按钮
        self.folder_btn = Button(self.button_frame, text="选择文件夹", command=self.upload_folder)
        self.folder_btn.grid(row=0, column=1, padx=10, pady=5)

        # 删除按钮
        self.delete_btn = Button(self.button_frame, text="删除选中图片", command=self.delete_selected)
        self.delete_btn.grid(row=0, column=2, padx=10, pady=5)

        # 输出格式选择
        Label(self.button_frame, text="输出格式:").grid(row=0, column=3, padx=10, pady=5)
        self.output_format = StringVar(value="PNG")
        self.format_menu = OptionMenu(self.button_frame, self.output_format, "PNG", "JPEG")
        self.format_menu.grid(row=0, column=4, padx=10, pady=5)

        # 在下方调用水印和导出组件
        self.watermark_options = WatermarkOptions(self, self.images, self.output_format, self.update_preview)
        self.watermark_options.grid(row=3, column=0, columnspan=2, sticky='ew', padx=10, pady=10)

        # 配置网格权重
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

    def _on_mousewheel(self, event):
        """处理鼠标滚轮滚动事件"""
        if event.delta:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")

    def upload_files(self):
        files = filedialog.askopenfilenames(filetypes=[
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
            ("All files", "*.*")
        ])
        self.add_files(files)

    def upload_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            for fname in os.listdir(folder):
                fpath = os.path.join(folder, fname)
                if os.path.isfile(fpath) and fpath.lower().endswith(SUPPORTED_FORMATS):
                    self.add_files([fpath])

    def add_files(self, files):
        for f in files:
            if f.lower().endswith(SUPPORTED_FORMATS) and f not in [img[0] for img in self.images]:
                original_thumb_tk, watermarked_thumb_tk, original_img = self.make_thumbnails(f)
                self.images.append((f, original_thumb_tk, watermarked_thumb_tk, original_img))
                self.file_list.insert(END, os.path.basename(f))

    def make_thumbnails(self, filepath):
        """创建原始缩略图和水印缩略图 - 统一尺寸"""
        try:
            original_img = Image.open(filepath).convert("RGBA")
            
            # 统一缩略图尺寸
            thumb_size = (800, 600)
            
            # 1. 原始缩略图
            original_thumb = original_img.copy()
            original_thumb.thumbnail(thumb_size, Image.Resampling.LANCZOS)
            original_thumb_tk = ImageTk.PhotoImage(original_thumb)
            
            # 2. 水印缩略图
            watermarked_thumb = self.apply_watermark_to_thumbnail(original_img.copy())
            watermarked_thumb.thumbnail(thumb_size, Image.Resampling.LANCZOS)
            watermarked_thumb_tk = ImageTk.PhotoImage(watermarked_thumb)
            
            return original_thumb_tk, watermarked_thumb_tk, original_img
        except Exception as e:
            print(f"创建缩略图时出错: {e}")
            return None, None, None

    def apply_watermark_to_thumbnail(self, image):
        """应用水印到缩略图"""
        try:
            # 使用水印选项应用水印
            if self.watermark_options:
                watermarked = self.watermark_options.apply_watermark_preview(image)
                # 统一缩略图尺寸
                watermarked.thumbnail((800, 600), Image.Resampling.LANCZOS)
                return watermarked
            image.thumbnail((800, 600), Image.Resampling.LANCZOS)
            return image
        except Exception as e:
            print(f"应用水印时出错: {e}")
            image.thumbnail((800, 600), Image.Resampling.LANCZOS)
            return image
    
    def apply_watermark_preview(self, image):
        """应用水印用于预览 - 使用当前设置的位置"""
        if self.watermark_type.get() == "text":
            return self.text_options.apply_watermark(image)
        else:
            return self.image_options.apply_watermark(image)

    def update_preview(self):
        """更新所有图片的预览 - 使用自定义位置或预设位置"""
        print("更新预览...")  # 调试信息
        
        # 确定使用自定义位置还是预设位置
        use_custom_position = self.custom_position is not None
        
        for i, (filepath, original_thumb_tk, _, original_img) in enumerate(self.images):
            try:
                # 重新从文件加载图片，避免引用丢失
                img = Image.open(filepath).convert("RGBA")
                
                # 应用水印 - 根据是否使用自定义位置选择不同的方法
                if use_custom_position:
                    # 使用自定义位置
                    watermarked_thumb = self.apply_watermark_with_custom_position(img.copy(), self.custom_position[0], self.custom_position[1])
                else:
                    # 使用预设位置
                    watermarked_thumb = self.apply_watermark_to_thumbnail(img.copy())
                
                watermarked_thumb.thumbnail((800, 600), Image.Resampling.LANCZOS)
                watermarked_thumb_tk = ImageTk.PhotoImage(watermarked_thumb)
                
                # 更新水印缩略图，保持原始缩略图和原图引用
                self.images[i] = (filepath, original_thumb_tk, watermarked_thumb_tk, original_img)
                
            except Exception as e:
                print(f"更新预览时出错: {e}")
        
        # 刷新当前显示的预览
        if self.selected_index is not None:
            self.show_thumbnail(None)
    def show_thumbnail(self, event):
        """显示选中的图片预览（带九宫格参考线）"""
        selection = self.file_list.curselection()
        if selection:
            idx = selection[0]
            self.selected_index = idx
            
            # 保存当前滚动位置
            current_scroll = self.canvas.yview()
            
            # 获取水印缩略图
            filepath, _, watermarked_thumb_tk, _ = self.images[idx]
            
            if watermarked_thumb_tk:
                self.canvas.delete("all")
                
                # 显示完整图片
                self.create_preview_with_grid(watermarked_thumb_tk)
                
                # 恢复滚动位置
                self.canvas.yview_moveto(current_scroll[0])

    def create_preview_with_grid(self, thumb_image):
        """创建带九宫格参考线的预览 - 修改版：添加图片上边距"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1:
            canvas_width = 600
            canvas_height = 450
        
        # 计算图片在canvas中的位置 - 添加10px上边距
        img_x = (canvas_width - thumb_image.width()) // 2
        img_y = 10  # 固定上边距10px，不再居中垂直
        
        # 显示完整图片
        self.canvas.create_image(img_x, img_y, anchor=NW, image=thumb_image, tags="preview_image")
        
        # 计算九宫格线的位置（基于图片坐标，不是canvas坐标）
        img_width = thumb_image.width()
        img_height = thumb_image.height()
        
        # 水平分割线位置（图片内的相对位置）
        h_line1 = img_y + img_height // 3
        h_line2 = img_y + 2 * img_height // 3
        
        # 垂直分割线位置（图片内的相对位置）
        v_line1 = img_x + img_width // 3
        v_line2 = img_x + 2 * img_width // 3
        
        # 绘制九宫格参考线（半透明红色）
        self.canvas.create_line(img_x, h_line1, img_x + img_width, h_line1, 
                            fill="red", width=1, dash=(4, 4), tags="grid_line")
        self.canvas.create_line(img_x, h_line2, img_x + img_width, h_line2, 
                            fill="red", width=1, dash=(4, 4), tags="grid_line")
        self.canvas.create_line(v_line1, img_y, v_line1, img_y + img_height, 
                            fill="red", width=1, dash=(4, 4), tags="grid_line")
        self.canvas.create_line(v_line2, img_y, v_line2, img_y + img_height, 
                            fill="red", width=1, dash=(4, 4), tags="grid_line")
        
        # 更新滚动区域
        total_height = max(canvas_height, img_y + img_height + 20)
        self.canvas.configure(scrollregion=(0, 0, canvas_width, total_height))
        self.canvas.yview_moveto(0.0)

    def set_watermark_position(self, position):
        """设置水印位置"""
        # 重置自定义位置，使用预设位置
        self.custom_position = None
        print(f"切换到预设位置: {position}")
        
        # 更新水印选项中的位置
        if self.watermark_options:
            if self.watermark_options.watermark_type.get() == "text":
                self.watermark_options.text_options.position.set(position)
            else:
                self.watermark_options.image_options.position.set(position)
        
        # 更新预览
        self.update_preview()

    def on_watermark_press(self, event):
        """鼠标按下事件 - 开始拖拽水印"""
        # 检查是否点击在图片区域内
        items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        if items and "preview_image" in self.canvas.gettags(items[0]):
            self.dragging_watermark = True
            self.drag_start_pos = (event.x, event.y)
            
            # 保存当前的滚动位置
            self.saved_scroll_position = self.canvas.yview()
            
            # 获取图片位置和尺寸
            img_items = self.canvas.find_withtag("preview_image")
            if img_items:
                # 使用 canvasx/canvasy 获取相对于画布的真实坐标（考虑滚动）
                canvas_x = self.canvas.canvasx(event.x)
                canvas_y = self.canvas.canvasy(event.y)
                
                img_coords = self.canvas.coords(img_items[0])
                img_x, img_y = img_coords
                img_width = self.images[self.selected_index][2].width() if self.selected_index is not None else 0
                img_height = self.images[self.selected_index][2].height() if self.selected_index is not None else 0
                
                if img_width > 0 and img_height > 0:
                    # 计算点击位置在图片内的相对坐标（0-1范围）
                    rel_x = (canvas_x - img_x) / img_width
                    rel_y = (canvas_y - img_y) / img_height
                    
                    # 限制在图片范围内
                    rel_x = max(0, min(1, rel_x))
                    rel_y = max(0, min(1, rel_y))
                    
                    print(f"点击位置: 相对坐标({rel_x:.2f}, {rel_y:.2f}), 画布坐标({canvas_x}, {canvas_y})")
                    
                    # 立即更新水印位置到点击位置
                    self.set_custom_watermark_position(rel_x, rel_y)

    def on_watermark_drag(self, event):
        """鼠标拖拽事件 - 实时更新水印位置"""
        if self.dragging_watermark:
            # 检查是否在图片区域内
            items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
            if items and "preview_image" in self.canvas.gettags(items[0]):
                # 获取图片位置和尺寸
                img_items = self.canvas.find_withtag("preview_image")
                if img_items:
                    # 使用 canvasx/canvasy 获取相对于画布的真实坐标（考虑滚动）
                    canvas_x = self.canvas.canvasx(event.x)
                    canvas_y = self.canvas.canvasy(event.y)
                    
                    img_coords = self.canvas.coords(img_items[0])
                    img_x, img_y = img_coords
                    img_width = self.images[self.selected_index][2].width() if self.selected_index is not None else 0
                    img_height = self.images[self.selected_index][2].height() if self.selected_index is not None else 0
                    
                    if img_width > 0 and img_height > 0:
                        # 计算鼠标位置在图片内的相对坐标（0-1范围）
                        rel_x = (canvas_x - img_x) / img_width
                        rel_y = (canvas_y - img_y) / img_height
                        
                        # 限制在图片范围内
                        rel_x = max(0, min(1, rel_x))
                        rel_y = max(0, min(1, rel_y))
                        
                        # 实时更新水印位置
                        self.set_custom_watermark_position(rel_x, rel_y)
                        
                        # 恢复滚动位置
                        self.canvas.yview_moveto(self.saved_scroll_position[0])

    def on_watermark_release(self, event):
        """鼠标释放事件 - 结束拖拽水印"""
        if self.dragging_watermark:
            self.dragging_watermark = False
            
            # 检查是否释放在图片区域内
            items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
            if items and "preview_image" in self.canvas.gettags(items[0]):
                # 获取图片位置和尺寸
                img_items = self.canvas.find_withtag("preview_image")
                if img_items:
                    # 使用 canvasx/canvasy 获取相对于画布的真实坐标（考虑滚动）
                    canvas_x = self.canvas.canvasx(event.x)
                    canvas_y = self.canvas.canvasy(event.y)
                    
                    img_coords = self.canvas.coords(img_items[0])
                    img_x, img_y = img_coords
                    img_width = self.images[self.selected_index][2].width() if self.selected_index is not None else 0
                    img_height = self.images[self.selected_index][2].height() if self.selected_index is not None else 0
                    
                    if img_width > 0 and img_height > 0:
                        # 计算释放位置在图片内的相对坐标（0-1范围）
                        rel_x = (canvas_x - img_x) / img_width
                        rel_y = (canvas_y - img_y) / img_height
                        
                        # 限制在图片范围内
                        rel_x = max(0, min(1, rel_x))
                        rel_y = max(0, min(1, rel_y))
                        
                        print(f"释放位置: 相对坐标({rel_x:.2f}, {rel_y:.2f}), 画布坐标({canvas_x}, {canvas_y})")
                        
                        # 最终更新水印位置
                        self.set_custom_watermark_position(rel_x, rel_y)
            
            # 恢复滚动位置
            self.canvas.yview_moveto(self.saved_scroll_position[0])

    def set_custom_watermark_position(self, rel_x, rel_y):
        """设置自定义水印位置（基于相对坐标）"""
        # 保存自定义位置
        self.custom_position = (rel_x, rel_y)
        print(f"设置自定义位置: ({rel_x:.2f}, {rel_y:.2f})")
        
        # 强制更新水印位置
        self.force_update_watermark_position(rel_x, rel_y)
    
    def force_update_watermark_position(self, rel_x, rel_y):
        """强制更新水印位置到指定相对坐标"""
        if self.selected_index is not None and self.watermark_options:
            try:
                # 保存当前滚动位置
                current_scroll = self.canvas.yview()
                
                # 获取原图
                filepath, _, _, original_img = self.images[self.selected_index]
                img = Image.open(filepath).convert("RGBA")
                
                # 应用水印到原图（使用自定义位置）
                watermarked_img = self.apply_watermark_with_custom_position(img.copy(), rel_x, rel_y)
                
                # 创建缩略图
                watermarked_thumb = watermarked_img.copy()
                watermarked_thumb.thumbnail((800, 600), Image.Resampling.LANCZOS)
                watermarked_thumb_tk = ImageTk.PhotoImage(watermarked_thumb)
                
                # 更新图片数据
                original_thumb_tk = self.images[self.selected_index][1]
                self.images[self.selected_index] = (filepath, original_thumb_tk, watermarked_thumb_tk, original_img)
                
                # 刷新显示
                self.show_thumbnail(None)
                
                # 恢复滚动位置
                self.canvas.yview_moveto(current_scroll[0])
                
            except Exception as e:
                print(f"更新自定义位置水印时出错: {e}")

    def apply_watermark_with_custom_position(self, image, rel_x, rel_y):
        """使用自定义位置应用水印"""
        if not self.watermark_options:
            return image
        
        if self.watermark_options.watermark_type.get() == "text":
            return self.apply_text_watermark_custom(image, rel_x, rel_y)
        else:
            return self.apply_image_watermark_custom(image, rel_x, rel_y)

    def apply_text_watermark_custom(self, image, rel_x, rel_y):
        """应用文本水印到自定义位置"""
        if not self.watermark_options.text_options.text_entry.get().strip():
            return image
            
        # 创建水印层
        watermark = Image.new("RGBA", image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(watermark)
        
        # 获取字体
        font = self.watermark_options.text_options.get_font()
        
        # 获取文本
        text = self.watermark_options.text_options.text_entry.get()
        
        # 计算文本尺寸
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except:
            text_width = len(text) * self.watermark_options.text_options.font_size.get() // 2
            text_height = self.watermark_options.text_options.font_size.get()
        
        # 计算自定义位置（将相对坐标转换为绝对坐标）
        img_width, img_height = image.size
        position_x = int(rel_x * (img_width - text_width))
        position_y = int(rel_y * (img_height - text_height))
        
        # 设置透明度
        opacity = int(255 * self.watermark_options.text_options.opacity.get() / 100)
        color = self.watermark_options.text_options.color.get()
        fill_color = self.watermark_options.text_options.hex_to_rgba(color, opacity)
        
        # 应用样式效果
        if self.watermark_options.text_options.stroke.get():
            self.watermark_options.text_options.add_stroke(draw, text, (position_x, position_y), font, fill_color)
        elif self.watermark_options.text_options.shadow.get():
            self.watermark_options.text_options.add_shadow(draw, text, (position_x, position_y), font, fill_color)
        else:
            draw.text((position_x, position_y), text, font=font, fill=fill_color)
        
        # 合并水印和原图
        return Image.alpha_composite(image.convert("RGBA"), watermark)

    def apply_image_watermark_custom(self, image, rel_x, rel_y):
        """应用图片水印到自定义位置"""
        if not self.watermark_options.image_options.image_path.get():
            return image
            
        try:
            # 打开水印图片
            watermark = Image.open(self.watermark_options.image_options.image_path.get()).convert("RGBA")
            
            # 缩放水印
            scale_factor = self.watermark_options.image_options.scale_percent.get() / 100.0
            new_width = int(image.width * scale_factor)
            new_height = int(image.height * scale_factor)
            
            # 保持水印图片的宽高比
            wm_ratio = watermark.width / watermark.height
            if new_width / new_height > wm_ratio:
                new_width = int(new_height * wm_ratio)
            else:
                new_height = int(new_width / wm_ratio)
                
            watermark = watermark.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 设置透明度
            opacity = self.watermark_options.image_options.opacity.get() / 100.0
            watermark = self.apply_opacity_to_image(watermark, opacity)
            
            # 计算自定义位置（将相对坐标转换为绝对坐标）
            img_width, img_height = image.size
            position_x = int(rel_x * (img_width - new_width))
            position_y = int(rel_y * (img_height - new_height))
            
            # 创建结果图片
            result = image.convert("RGBA")
            result.paste(watermark, (position_x, position_y), watermark)
            
            return result
            
        except Exception as e:
            print(f"应用自定义位置图片水印时出错: {e}")
            return image

    def apply_opacity_to_image(self, image, opacity):
        """调整图片透明度"""
        if opacity >= 1.0:
            return image
            
        # 创建一个新的alpha通道
        alpha = image.split()[3]
        alpha = alpha.point(lambda p: p * opacity)
        image.putalpha(alpha)
        return image

    def delete_selected(self):
        selection = self.file_list.curselection()
        if selection:
            idx = selection[0]
            self.file_list.delete(idx)
            del self.images[idx]
            self.canvas.delete("all")
            self.selected_index = None
            self.canvas.configure(scrollregion=(0, 0, 600, 800))

    def drop_files(self, event):
        files = self.master.tk.splitlist(event.data)
        all_files = []
        for f in files:
            if os.path.isdir(f):
                for root, _, filenames in os.walk(f):
                    for fname in filenames:
                        if fname.lower().endswith(SUPPORTED_FORMATS):
                            all_files.append(os.path.join(root, fname))
            else:
                all_files.append(f)
        self.add_files(all_files)