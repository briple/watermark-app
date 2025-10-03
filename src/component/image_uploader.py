import os
from tkinter import Frame, Button, Listbox, filedialog, Label, Scrollbar, Canvas, NW, StringVar, OptionMenu, RIGHT, Y, BOTH, END
from PIL import Image, ImageTk
from component.watermark_options import WatermarkOptions
from tkinterdnd2 import TkinterDnD, DND_FILES

SUPPORTED_FORMATS = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif')

class ImageUploader(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.images = []  # [(filepath, thumbnail)]
        self.selected_index = None
        self.watermark_options = None  # 将在后面初始化

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

        # 拖拽上传区域 - 放在右上方
        self.drag_label = Label(right_frame, text="拖拽图片或文件到此处上传", 
                               relief="groove", width=60, height=3,
                               font=("Arial", 10), bg="#f0f0f0")
        self.drag_label.pack(fill='x', pady=(0, 10))
        self.drag_label.drop_target_register(DND_FILES)
        self.drag_label.dnd_bind('<<Drop>>', self.drop_files)

        # 缩略图展示 - 放在拖拽区域正下方，尽可能大
        preview_frame = Frame(right_frame)
        preview_frame.pack(fill='both', expand=True)
        
        Label(preview_frame, text="图片预览", font=("Arial", 10, "bold")).pack(pady=(0, 5))
         # 创建Canvas和滚动条容器
        canvas_container = Frame(preview_frame)
        canvas_container.pack(fill='both', expand=True)
        
        # 创建Canvas和垂直滚动条
        self.canvas = Canvas(canvas_container, bg="white", relief="solid", bd=1, 
                           scrollregion=(0, 0, 600, 800))  # 设置较大的滚动区域
        self.canvas_vscroll = Scrollbar(canvas_container, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.canvas_vscroll.set)
        
        # 布局Canvas和滚动条
        self.canvas.pack(side='left', fill='both', expand=True)
        self.canvas_vscroll.pack(side='right', fill='y')
        
        # 绑定鼠标滚轮事件
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)

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
        self.watermark_options = WatermarkOptions(self, self.images, self.output_format)
        self.watermark_options.grid(row=3, column=0, columnspan=2, sticky='ew', padx=10, pady=10)

        # 配置网格权重
        self.grid_rowconfigure(0, weight=1)  # 第一行可扩展
        self.grid_rowconfigure(1, weight=0)  # 第二行固定高度
        self.grid_rowconfigure(2, weight=0)  # 按钮行固定高度
        self.grid_rowconfigure(3, weight=0)  # 水印选项行固定高度
        
        self.grid_columnconfigure(0, weight=0)  # 左侧固定宽度
        self.grid_columnconfigure(1, weight=1)  # 右侧可扩展

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
                thumb = self.make_thumbnail(f)
                self.images.append((f, thumb))
                self.file_list.insert(END, os.path.basename(f))

    def make_thumbnail(self, filepath):
        try:
            img = Image.open(filepath)
            # 创建适合大canvas的缩略图，但不再限制高度，保持原始比例
            img.thumbnail((1000, 320))  # 增加最大高度限制
            return ImageTk.PhotoImage(img)
        except Exception:
            return None

    def show_thumbnail(self, event):
        selection = self.file_list.curselection()
        if selection:
            idx = selection[0]
            self.selected_index = idx
            thumb = self.images[idx][1]
            self.canvas.delete("all")
            if thumb:
                # 获取canvas实际尺寸
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                
                # 如果canvas还没有实际尺寸，使用默认尺寸
                if canvas_width <= 1:
                    canvas_width = 600
                    canvas_height = 450
                
                # 计算居中位置
                x = (canvas_width - thumb.width()) // 2
                y = (canvas_height - thumb.height()) // 2
                
                self.canvas.create_image(x, y, anchor=NW, image=thumb)
                self.canvas.image = thumb

                # 更新滚动区域以适应图片高度
                total_height = thumb.height() + 20  # 图片高度 + 边距
                self.canvas.configure(scrollregion=(0, 0, canvas_width, total_height))
                
                # 重置滚动位置到顶部
                self.canvas.yview_moveto(0.0)


    def delete_selected(self):
        selection = self.file_list.curselection()
        if selection:
            idx = selection[0]
            self.file_list.delete(idx)
            del self.images[idx]
            self.canvas.delete("all")
            self.selected_index = None

             # 重置滚动区域
            self.canvas.configure(scrollregion=(0, 0, 600, 800))

    def drop_files(self, event):
        files = self.master.tk.splitlist(event.data)
        all_files = []
        for f in files:
            if os.path.isdir(f):
                # 遍历文件夹，添加所有支持格式的图片
                for root, _, filenames in os.walk(f):
                    for fname in filenames:
                        if fname.lower().endswith(SUPPORTED_FORMATS):
                            all_files.append(os.path.join(root, fname))
            else:
                all_files.append(f)
        self.add_files(all_files)