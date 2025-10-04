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
        """创建原始缩略图和水印缩略图"""
        try:
            original_img = Image.open(filepath).convert("RGBA")
            
            # 创建原始缩略图
            original_thumb = original_img.copy()
            original_thumb.thumbnail((400, 400))
            original_thumb_tk = ImageTk.PhotoImage(original_thumb)
            
            # 创建水印缩略图（初始状态）
            watermarked_thumb = self.apply_watermark_to_thumbnail(original_img.copy())
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
                watermarked.thumbnail((400, 400))
                return watermarked
            image.thumbnail((400, 400))
            return image
        except Exception as e:
            print(f"应用水印时出错: {e}")
            image.thumbnail((400, 400))
            return image

    def update_preview(self):
        """更新所有图片的预览 - 修复版本"""
        print("更新预览...")  # 调试信息
        for i, (filepath, original_thumb_tk, _, original_img) in enumerate(self.images):
            try:
                # 重新从文件加载图片，避免引用丢失
                img = Image.open(filepath).convert("RGBA")
                watermarked_thumb = self.apply_watermark_to_thumbnail(img.copy())
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
            
            # 获取水印缩略图
            filepath, _, watermarked_thumb_tk, _ = self.images[idx]
            
            if watermarked_thumb_tk:
                self.canvas.delete("all")
                
                # 显示完整图片
                self.create_preview_with_grid(watermarked_thumb_tk)

    # 其余方法保持不变...

    def create_preview_with_grid(self, thumb_image):
        """创建带九宫格参考线的预览"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1:
            canvas_width = 600
            canvas_height = 450
        
        # 计算图片在canvas中的居中位置
        img_x = (canvas_width - thumb_image.width()) // 2
        img_y = (canvas_height - thumb_image.height()) // 2
        
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
            
            # 计算点击位置对应的九宫格区域
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # 获取图片位置和尺寸
            img_items = self.canvas.find_withtag("preview_image")
            if img_items:
                img_coords = self.canvas.coords(img_items[0])
                img_x, img_y = img_coords
                img_width = self.images[self.selected_index][2].width() if self.selected_index is not None else 0
                img_height = self.images[self.selected_index][2].height() if self.selected_index is not None else 0
                
                if img_width > 0 and img_height > 0:
                    # 计算点击位置在图片内的相对坐标
                    rel_x = event.x - img_x
                    rel_y = event.y - img_y
                    
                    # 计算对应的九宫格区域
                    col = int(rel_x / (img_width / 3))
                    row = int(rel_y / (img_height / 3))
                    
                    if 0 <= row < 3 and 0 <= col < 3:
                        # 将点击的格子位置转换为对应的预设位置
                        position_map = {
                            (0, 0): "top-left", (0, 1): "top", (0, 2): "top-right",
                            (1, 0): "left", (1, 1): "center", (1, 2): "right",
                            (2, 0): "bottom-left", (2, 1): "bottom", (2, 2): "bottom-right"
                        }
                        
                        new_position = position_map.get((row, col))
                        if new_position:
                            self.set_watermark_position(new_position)

    def on_watermark_drag(self, event):
        """鼠标拖拽事件 - 拖拽水印"""
        if self.dragging_watermark:
            # 可以添加拖拽时的视觉反馈，比如显示当前位置
            pass

    def on_watermark_release(self, event):
        """鼠标释放事件 - 结束拖拽水印"""
        if self.dragging_watermark:
            self.dragging_watermark = False
            
            # 检查是否释放在图片区域内
            items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
            if items and "preview_image" in self.canvas.gettags(items[0]):
                # 计算释放位置对应的九宫格区域
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                
                # 获取图片位置和尺寸
                img_items = self.canvas.find_withtag("preview_image")
                if img_items:
                    img_coords = self.canvas.coords(img_items[0])
                    img_x, img_y = img_coords
                    img_width = self.images[self.selected_index][2].width() if self.selected_index is not None else 0
                    img_height = self.images[self.selected_index][2].height() if self.selected_index is not None else 0
                    
                    if img_width > 0 and img_height > 0:
                        # 计算释放位置在图片内的相对坐标
                        rel_x = event.x - img_x
                        rel_y = event.y - img_y
                        
                        # 计算对应的九宫格区域
                        col = int(rel_x / (img_width / 3))
                        row = int(rel_y / (img_height / 3))
                        
                        if 0 <= row < 3 and 0 <= col < 3:
                            # 将释放的格子位置转换为对应的预设位置
                            position_map = {
                                (0, 0): "top-left", (0, 1): "top", (0, 2): "top-right",
                                (1, 0): "left", (1, 1): "center", (1, 2): "right",
                                (2, 0): "bottom-left", (2, 1): "bottom", (2, 2): "bottom-right"
                            }
                            
                            new_position = position_map.get((row, col))
                            if new_position:
                                self.set_watermark_position(new_position)

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