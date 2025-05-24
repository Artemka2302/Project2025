from tkinter import *
from tkinter.filedialog import asksaveasfile, askopenfile
from tkinter.messagebox import showerror, askokcancel
from tkinter import font
import os
from tkinter.colorchooser import askcolor


filename = None

root = Tk()
root.title("Word-like Text Editor")
root.geometry("900x600")

# ==== ФОНЫ ====
themes = {
    'light': {
        'bg': 'white',
        'fg': 'black',
        'insertbackground': 'black',
        'selectbackground': '#cceeff'
    }
}

# ==== ФУНКЦИИ ====


def toggle_theme():
    current_bg = text.cget("bg")
    if current_bg == themes['light']['bg']:
        # Пример тёмной темы
        dark_theme = {
            'bg': '#1e1e1e',
            'fg': 'white',
            'insertbackground': 'white',
            'selectbackground': '#555555'
        }
        text.config(
            bg=dark_theme['bg'],
            fg=dark_theme['fg'],
            insertbackground=dark_theme['insertbackground'],
            selectbackground=dark_theme['selectbackground']
        )
    else:
        text.config(
            bg=themes['light']['bg'],
            fg=themes['light']['fg'],
            insertbackground=themes['light']['insertbackground'],
            selectbackground=themes['light']['selectbackground']
        )


def update_status_bar(event=None):
    text_content = text.get('1.0', 'end-1c')
    words = len(text_content.split())
    chars = len(text_content)
    status_bar.config(text=f'Слов: {words} | Символов: {chars}')

def change_text_color():
    color = askcolor(title="Выбери цвет текста")[1]
    if color:
        try:
            text.tag_add("color", "sel.first", "sel.last")
            text.tag_config("color", foreground=color)
        except:
            pass

def find_text():
    find_win = Toplevel(root)
    find_win.title("Найти и заменить")
    find_win.transient(root)
    find_win.resizable(False, False)

    Label(find_win, text="Найти:").grid(row=0, column=0, sticky='e')
    search_entry = Entry(find_win, width=30)
    search_entry.grid(row=0, column=1, padx=2, pady=2)

    Label(find_win, text="Заменить на:").grid(row=1, column=0, sticky='e')
    replace_entry = Entry(find_win, width=30)
    replace_entry.grid(row=1, column=1, padx=2, pady=2)

    def do_find():
        text.tag_remove('found', '1.0', END)
        s = search_entry.get()
        if s:
            idx = '1.0'
            while True:
                idx = text.search(s, idx, nocase=1, stopindex=END)
                if not idx: break
                lastidx = f"{idx}+{len(s)}c"
                text.tag_add('found', idx, lastidx)
                idx = lastidx
            text.tag_config('found', background='yellow')

    def do_replace():
        s = search_entry.get()
        r = replace_entry.get()
        content = text.get('1.0', END)
        new_content = content.replace(s, r)
        text.delete('1.0', END)
        text.insert('1.0', new_content)

    Button(find_win, text="Найти", command=do_find).grid(row=2, column=0, sticky='ew', padx=2, pady=2)
    Button(find_win, text="Заменить", command=do_replace).grid(row=2, column=1, sticky='ew', padx=2, pady=2)

def get_current_font():
    try:
        current_tags = text.tag_names("sel.first")
        for tag in current_tags:
            font_conf = text.tag_cget(tag, "font")
            if font_conf:
                return font.nametofont(font_conf)
    except:
        pass
    return font.Font(font=text["font"])

def update_title(name=None):
    title = name if name else "Untitled"
    root.title(f"{title} - Word Editor")

def new_file():
    global filename
    filename = None
    text.delete(1.0, END)
    update_title()

def open_file():
    global filename
    f = askopenfile(mode='r', defaultextension='.txt')
    if f is not None:
        filename = f.name
        content = f.read()
        text.delete(1.0, END)
        text.insert(1.0, content)
        update_title(os.path.basename(filename))

def save_file():
    global filename
    if filename is None:
        return save_as()
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text.get(1.0, END).rstrip())
        update_title(os.path.basename(filename))
    except Exception as e:
        showerror("Save Error", str(e))

def save_as():
    global filename
    f = asksaveasfile(mode='w', defaultextension='.txt')
    if f:
        filename = f.name
        f.write(text.get(1.0, END).rstrip())
        f.close()
        update_title(os.path.basename(filename))

def exit_app():
    if askokcancel("Quit", "Are you sure you want to exit?"):
        root.destroy()


font_family_var = StringVar(value="Consolas")
font_size_var = IntVar(value=12)

# ==== СТИЛИ ТЕКСТА ====
def toggle_format(style):
    try:
        # Используем выбранные пользователем шрифт и размер
        family = font_family_var.get()
        size = font_size_var.get()

        # Проверяем текущие теги
        current_tags = text.tag_names("sel.first")
        tag = f"{style}_{family}_{size}"  # Уникальный тег на основе стиля, шрифта и размера

        # Создаём новый шрифт
        new_font = font.Font(family=family, size=size)
        if style == "bold":
            new_font.configure(weight="bold")
        elif style == "italic":
            new_font.configure(slant="italic")
        elif style == "underline":
            new_font.configure(underline=1)

        # Если уже применён — удалить
        if tag in current_tags:
            text.tag_remove(tag, "sel.first", "sel.last")
        else:
            text.tag_configure(tag, font=new_font)
            text.tag_add(tag, "sel.first", "sel.last")
    except TclError:
        pass



def apply_font_family(event=None):
    family = font_family_var.get()
    text.config(font=(family, font_size_var.get()))

def apply_font_size(event=None):
    size = font_size_var.get()
    text.config(font=(font_family_var.get(), size))

def apply_heading(style):
    try:
        base_font = get_current_font()
        heading_font = font.Font(**base_font.configure())

        if style == 'Normal':
            heading_font.configure(size=font_size_var.get(), weight='normal')
        elif style == 'Heading 1':
            heading_font.configure(size=20, weight='bold')
        elif style == 'Heading 2':
            heading_font.configure(size=16, weight='bold')

        tag = f"heading_{style.replace(' ', '_')}"
        text.tag_configure(tag, font=heading_font)
        text.tag_add(tag, 'sel.first', 'sel.last')
    except:
        pass


# ==== ВИДЖЕТЫ ====

# Toolbar
toolbar = Frame(root, bd=1, relief=RAISED)
toolbar.pack(side=TOP, fill=X)

# Font Family
font_families = list(font.families())
font_family_var = StringVar(value="Consolas")
font_family_menu = OptionMenu(toolbar, font_family_var, *sorted(font_families), command=apply_font_family)
font_family_menu.pack(side=LEFT, padx=5)

# Font Size
font_size_var = IntVar(value=12)
font_size_menu = OptionMenu(toolbar, font_size_var, *list(range(8, 41)), command=apply_font_size)
font_size_menu.pack(side=LEFT)

# Bold, Italic, Underline buttons
Button(toolbar, text="B", width=2, command=lambda: toggle_format("bold")).pack(side=LEFT, padx=2)
Button(toolbar, text="I", width=2, command=lambda: toggle_format("italic")).pack(side=LEFT, padx=2)
Button(toolbar, text="U", width=2, command=lambda: toggle_format("underline")).pack(side=LEFT, padx=2)

# Headings
heading_var = StringVar(value="Normal")
OptionMenu(toolbar, heading_var, "Normal", "Heading 1", "Heading 2", command=apply_heading).pack(side=LEFT, padx=10)

# Text widget
text = Text(root, wrap=WORD, undo=True)
text.pack(expand=1, fill=BOTH)

# Scrollbar
scrollbar = Scrollbar(text)
scrollbar.pack(side=RIGHT, fill=Y)
text.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=text.yview)

# Text Tag Styles
bold_font = font.Font(text, text.cget("font"))
bold_font.configure(weight="bold")

italic_font = font.Font(text, text.cget("font"))
italic_font.configure(slant="italic")

underline_font = font.Font(text, text.cget("font"))
underline_font.configure(underline=1)

# Menu
menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="New", command=new_file)
filemenu.add_command(label="Open", command=open_file)
filemenu.add_command(label="Save", command=save_file)
filemenu.add_command(label="Save As", command=save_as)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=exit_app)
menubar.add_cascade(label="File", menu=filemenu)
editmenu = Menu(menubar, tearoff=0)

editmenu.add_command(label="Найти и заменить", command=find_text)
editmenu.add_command(label="Цвет текста", command=change_text_color)
editmenu.add_command(label="Тема (светлая/тёмная)", command=toggle_theme)
menubar.add_cascade(label="Правка", menu=editmenu)


root.config(menu=menubar)

# Apply initial theme and font
text.config(
    bg=themes['light']['bg'],
    fg=themes['light']['fg'],
    insertbackground=themes['light']['insertbackground'],
    selectbackground=themes['light']['selectbackground'],
    font=(font_family_var.get(), font_size_var.get())
)

# symbols counting
status_bar = Label(root, text='Слов: 0 | Символов: 0', anchor='e')
status_bar.pack(fill='x', side='bottom')

# Start app
update_title()
root.mainloop()
