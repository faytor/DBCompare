import os
import sys
import tkinter as tk
from tkinter import filedialog, ttk
from db_handler import compare_databases
from scroll_functions import yscroll, on_text_scroll, xscroll, on_text_xscroll, on_mouse_wheel

def display_differences(notebook, title, data1, data2, db1_path, db2_path):
    frame = ttk.Frame(notebook)
    notebook.add(frame, text=title)
    
    label1 = ttk.Label(frame, text=f"Database 1: {db1_path}")
    label2 = ttk.Label(frame, text=f"Database 2: {db2_path}")
    
    label1.grid(row=0, column=0, sticky='ew')
    label2.grid(row=0, column=1, sticky='ew')

    text1 = tk.Text(frame, wrap=tk.NONE, width=50)
    text2 = tk.Text(frame, wrap=tk.NONE, width=50)
    
    text1.grid(row=1, column=0, sticky='nsew')
    text2.grid(row=1, column=1, sticky='nsew')

    vsb = ttk.Scrollbar(frame, orient="vertical")
    hsb = ttk.Scrollbar(frame, orient="horizontal")
    
    vsb.grid(row=1, column=2, sticky='ns')
    hsb.grid(row=2, column=0, columnspan=2, sticky='ew')

    vsb.config(command=lambda *args: yscroll(text1, text2, *args))
    text1.config(yscrollcommand=lambda *args: on_text_scroll(text1, text2, vsb, *args))
    text2.config(yscrollcommand=lambda *args: on_text_scroll(text1, text2, vsb, *args))

    hsb.config(command=lambda *args: xscroll(text1, text2, *args))
    text1.config(xscrollcommand=lambda *args: on_text_xscroll(text1, text2, hsb, *args))
    text2.config(xscrollcommand=lambda *args: on_text_xscroll(text1, text2, hsb, *args))

    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=1)
    frame.grid_rowconfigure(1, weight=1)

    data1_dict = {row[0]: row for row in data1}
    data2_dict = {row[0]: row for row in data2}
    
    all_ids = sorted(set(data1_dict.keys()) | set(data2_dict.keys()))
    
    for id in all_ids:
        row1 = data1_dict.get(id, ())
        row2 = data2_dict.get(id, ())
        
        if row1 == row2:
            text1.insert(tk.END, str(row1) + "\n")
            text2.insert(tk.END, str(row2) + "\n")
        else:
            if row1 and row2:
                text1.insert(tk.END, str(row1), 'diff_line')
                text2.insert(tk.END, str(row2), 'diff_line')
                
                for i, (val1, val2) in enumerate(zip(row1, row2)):
                    if val1 != val2:
                        start = text1.index(f"end-1c linestart+{len(str(row1[:i]))}c")
                        end = text1.index(f"end-1c linestart+{len(str(row1[:i+1]))}c")
                        text1.tag_add('diff_field', start, end)
                        
                        start = text2.index(f"end-1c linestart+{len(str(row2[:i]))}c")
                        end = text2.index(f"end-1c linestart+{len(str(row2[:i+1]))}c")
                        text2.tag_add('diff_field', start, end)
                
                text1.insert(tk.END, "\n")
                text2.insert(tk.END, "\n")
            elif row1:
                text1.insert(tk.END, str(row1) + "\n", 'diff_line')
                text2.insert(tk.END, "\n")
            else:
                text1.insert(tk.END, "\n")
                text2.insert(tk.END, str(row2) + "\n", 'diff_line')

    text1.tag_configure('diff_line', background='mistyrose')
    text2.tag_configure('diff_line', background='honeydew')
    text1.tag_configure('diff_field', background='lightcoral')
    text2.tag_configure('diff_field', background='lightgreen')
    
    text1.configure(state='disabled')
    text2.configure(state='disabled')

    text1.bind("<MouseWheel>", lambda e: on_mouse_wheel(e, text1, text2))
    text2.bind("<MouseWheel>", lambda e: on_mouse_wheel(e, text2, text1))
    text1.bind("<Shift-MouseWheel>", lambda e: hsb.delta(-1*(e.delta//120), 0))
    text2.bind("<Shift-MouseWheel>", lambda e: hsb.delta(-1*(e.delta//120), 0))

    text1.bind("<Button-4>", lambda e: on_mouse_wheel(e, text1, text2))
    text1.bind("<Button-5>", lambda e: on_mouse_wheel(e, text1, text2))
    text2.bind("<Button-4>", lambda e: on_mouse_wheel(e, text2, text1))
    text2.bind("<Button-5>", lambda e: on_mouse_wheel(e, text2, text1))

def clear_diff_tabs():
    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel):
            widget.destroy()

def browse_database(entry_widget):
    filename = filedialog.askopenfilename(
        filetypes=[("SQLite Database", "*.db *.sqlite *.sqlite3")]
    )
    entry_widget.delete(0, tk.END)
    entry_widget.insert(0, filename)

def compare_databases_gui():
    db1_path = db1_entry.get()
    db2_path = db2_entry.get()
    
    if not db1_path or not db2_path:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "Please select both databases.")
        return
    
    result_text.delete(1.0, tk.END)
    clear_diff_tabs()
    
    comparison_result = compare_databases(db1_path, db2_path)
    
    if 'error' in comparison_result:
        result_text.insert(tk.END, f"An error occurred: {comparison_result['error']}")
        return
    
    if not comparison_result['differences'] and not comparison_result['only_in_db1'] and not comparison_result['only_in_db2']:
        result_text.insert(tk.END, "No differences found. The databases are identical.")
        return
    
    if comparison_result['only_in_db1']:
        result_text.insert(tk.END, "Tables only in DB1: " + str(comparison_result['only_in_db1']) + "\n")
    if comparison_result['only_in_db2']:
        result_text.insert(tk.END, "Tables only in DB2: " + str(comparison_result['only_in_db2']) + "\n")
    
    if comparison_result['differences']:
        result_text.insert(tk.END, "\nDifferences found in the following tables:\n")
        for diff in comparison_result['differences']:
            result_text.insert(tk.END, f"- {diff['table']}\n")
        
        diff_window = tk.Toplevel(root)
        diff_window.title("Database Differences")
        diff_window.geometry("1000x600")
        
        style = ttk.Style()
        style.configure("TNotebook.Tab", padding=[10, 5], font=('TkDefaultFont', 10, 'bold'))
        style.map("TNotebook.Tab",
                  background=[("selected", "#ffffff"), ("!selected", "#ffffff")],
                  foreground=[("selected", "#000000"), ("!selected", "#707570")])
        
        notebook = ttk.Notebook(diff_window)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        for diff in comparison_result['differences']:
            display_differences(notebook, f"Table: {diff['table']}", diff['data1'], diff['data2'], db1_path, db2_path)
    else:
        result_text.insert(tk.END, "\nNo differences found in common tables.")


def setup_icon(root):
    # Path to the icon
    script_dir_path = os.path.dirname(os.path.realpath(__file__))
    icon_path = os.sep.join([script_dir_path, "img", "icon.png"])

    try:
        icon = tk.PhotoImage(file=icon_path)
        root.iconphoto(True, icon)

    except Exception as e:
        print(f"Error setting icon: {e}")


def setup_main_gui():
    global root, db1_entry, db2_entry, result_text

    root = tk.Tk()
    root.title("DB Compare")
    root.geometry("600x400")
    
    setup_icon(root)

    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    ttk.Label(frame, text="Database 1:").grid(column=0, row=0, sticky=tk.W)
    db1_entry = ttk.Entry(frame, width=50)
    db1_entry.grid(column=1, row=0, sticky=(tk.W, tk.E))
    ttk.Button(frame, text="Browse", command=lambda: browse_database(db1_entry)).grid(column=2, row=0)

    ttk.Label(frame, text="Database 2:").grid(column=0, row=1, sticky=tk.W)
    db2_entry = ttk.Entry(frame, width=50)
    db2_entry.grid(column=1, row=1, sticky=(tk.W, tk.E))
    ttk.Button(frame, text="Browse", command=lambda: browse_database(db2_entry)).grid(column=2, row=1)

    ttk.Button(frame, text="Compare Databases", command=compare_databases_gui).grid(column=1, row=2)

    result_text = tk.Text(frame, wrap=tk.WORD, width=70, height=20)
    result_text.grid(column=0, row=3, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(3, weight=1)

    root.mainloop()
