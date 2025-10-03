from tkinterdnd2 import TkinterDnD
from tkinter import Label
from component.image_uploader import ImageUploader

def main():
    root = TkinterDnD.Tk()
    root.title("Watermark App")
    # root.attributes('-fullscreen', True)
    root.geometry("1200x800")

    uploader = ImageUploader(root)
    uploader.pack(fill='both', expand=True)
    root.mainloop()

if __name__ == "__main__":
    main()