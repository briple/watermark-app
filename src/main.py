from tkinter import Tk, Label
from hello import display_hello

def main():
    root = Tk()
    root.title("Watermark App")
    root.geometry("600x400")

    hello_label = Label(root, text=display_hello())
    hello_label.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()