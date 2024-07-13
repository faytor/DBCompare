import tkinter as tk
from tkinter import filedialog, ttk
from db_handler import compare_databases

# ==============================
# Mouse Wheel Handling Function
# ==============================
def on_mouse_wheel(event, text1, text2):
    """
    Handle mouse wheel events for synchronized scrolling of two text widgets.

    This function is designed to work with both Windows and Linux systems,
    accounting for different event structures.

    Args:
        event (tk.Event): The mouse wheel event.
        text1 (tk.Text): The first text widget to scroll.
        text2 (tk.Text): The second text widget to scroll.

    Returns:
        str: "break" to prevent the event from being handled further.
    """
    # Determine the scroll direction
    if event.delta:
        # Windows-style mouse wheel event
        delta = event.delta
    elif event.num == 4 or event.num == 5:
        # Linux-style mouse wheel event
        delta = 1 if event.num == 4 else -1
    else:
        # Unknown event type
        return "break"

    # Calculate the number of units to scroll
    # 120 is a common "step" value for mouse wheels
    scroll_units = -1 * (delta // 120)

    # Scroll both text widgets
    text1.yview_scroll(scroll_units, "units")
    text2.yview_scroll(scroll_units, "units")

    # Prevent further handling of the event
    return "break"



# ==============================
# Display Differences Function
# ==============================
def display_differences(notebook, title, data1, data2, db1_path, db2_path):
    """
    Display the differences between two datasets in a notebook tab.

    Args:
        notebook (ttk.Notebook): The notebook widget to add the tab to.
        title (str): The title of the tab.
        data1 (list): Data from the first database.
        data2 (list): Data from the second database.
        db1_path (str): Path to the first database file.
        db2_path (str): Path to the second database file.
    """
    # ==============================
    # Frame and Label Setup
    # ==============================
    frame = ttk.Frame(notebook)
    notebook.add(frame, text=title)
    
    label1 = ttk.Label(frame, text=f"Database 1: {db1_path}")
    label2 = ttk.Label(frame, text=f"Database 2: {db2_path}")
    
    label1.grid(row=0, column=0, sticky='ew')
    label2.grid(row=0, column=1, sticky='ew')

    # ==============================
    # Text Widgets Setup
    # ==============================
    text1 = tk.Text(frame, wrap=tk.NONE, width=50)
    text2 = tk.Text(frame, wrap=tk.NONE, width=50)
    
    text1.grid(row=1, column=0, sticky='nsew')
    text2.grid(row=1, column=1, sticky='nsew')

    # ==============================
    # Scrollbar Setup
    # ==============================
    vsb = ttk.Scrollbar(frame, orient="vertical")
    hsb = ttk.Scrollbar(frame, orient="horizontal")
    
    vsb.grid(row=1, column=2, sticky='ns')
    hsb.grid(row=2, column=0, columnspan=2, sticky='ew')

    # ==============================
    # Vertical Scrolling Functions
    # ==============================
    def yscroll(*args):
        if args:
            text1.yview(*args)
            text2.yview(*args)

    def on_text_scroll(*args):
        yscroll('moveto', args[0])
        vsb.set(*args)

    vsb.config(command=yscroll)
    text1.config(yscrollcommand=on_text_scroll)
    text2.config(yscrollcommand=on_text_scroll)

    # ==============================
    # Horizontal Scrolling Functions
    # ==============================
    def xscroll(*args):
        if args:
            text1.xview(*args)
            text2.xview(*args)

    def on_text_xscroll(*args):
        xscroll('moveto', args[0])
        hsb.set(*args)

    hsb.config(command=xscroll)
    text1.config(xscrollcommand=on_text_xscroll)
    text2.config(xscrollcommand=on_text_xscroll)

    # ==============================
    # Frame Configuration
    # ==============================
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=1)
    frame.grid_rowconfigure(1, weight=1)

    # ==============================
    # Data Processing and Display
    # ==============================
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

    # ==============================
    # Text Widget Configuration
    # ==============================
    text1.tag_configure('diff_line', background='mistyrose')
    text2.tag_configure('diff_line', background='honeydew')
    text1.tag_configure('diff_field', background='lightcoral')
    text2.tag_configure('diff_field', background='lightgreen')
    
    text1.configure(state='disabled')
    text2.configure(state='disabled')

    # ==============================
    # Mouse Wheel Bindings
    # ==============================
    text1.bind("<MouseWheel>", lambda e: on_mouse_wheel(e, text1, text2))
    text2.bind("<MouseWheel>", lambda e: on_mouse_wheel(e, text2, text1))
    text1.bind("<Shift-MouseWheel>", lambda e: hsb.delta(-1*(e.delta//120), 0))
    text2.bind("<Shift-MouseWheel>", lambda e: hsb.delta(-1*(e.delta//120), 0))


    # Linux compatibility
    text1.bind("<Button-4>", lambda e: on_mouse_wheel(e, text1, text2))
    text1.bind("<Button-5>", lambda e: on_mouse_wheel(e, text1, text2))
    text2.bind("<Button-4>", lambda e: on_mouse_wheel(e, text2, text1))
    text2.bind("<Button-5>", lambda e: on_mouse_wheel(e, text2, text1))


# ==============================
# UI Cleanup Function
# ==============================
def clear_diff_tabs():
    """
    Clear all difference tabs by destroying Toplevel widgets.

    This function removes any existing comparison results
    displayed in separate windows.
    """
    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel):
            widget.destroy()


# ==============================
# Database File Selection Function
# ==============================
def browse_database(entry_widget):
    """
    Open a file dialog to select a database file and update the given entry widget.

    Args:
        entry_widget (tk.Entry): The entry widget to update with the selected file path.

    This function opens a file dialog for selecting SQLite database files
    and updates the provided entry widget with the selected file path.
    """
    filename = filedialog.askopenfilename(
        filetypes=[("SQLite Database", "*.db *.sqlite *.sqlite3")]
    )
    entry_widget.delete(0, tk.END)
    entry_widget.insert(0, filename)



# ==============================
# Database Comparison GUI Function
# ==============================
def compare_databases_gui():
    """
    Perform a GUI-based comparison of two databases and display the results.

    This function retrieves the paths of two databases from entry widgets,
    compares them, and displays the results in a text widget and, if differences
    are found, in a new window with detailed comparisons.

    Global variables used:
        db1_entry (ttk.Entry): Entry widget for the first database path.
        db2_entry (ttk.Entry): Entry widget for the second database path.
        result_text (tk.Text): Text widget to display summary results.
        root (tk.Tk): The main application window.

    Functions called:
        clear_diff_tabs(): Clears any existing difference tabs.
        compare_databases(db1_path, db2_path): Compares two databases.
        display_differences(notebook, title, data1, data2, db1_path, db2_path):
            Displays detailed differences in a notebook tab.
    """

    # Retrieve database paths
    db1_path = db1_entry.get()
    db2_path = db2_entry.get()
    
    # Validate input
    if not db1_path or not db2_path:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "Please select both databases.")
        return
    
    # Clear previous results
    result_text.delete(1.0, tk.END)
    clear_diff_tabs()
    
    # Perform database comparison
    comparison_result = compare_databases(db1_path, db2_path)
    
    # Handle comparison errors
    if 'error' in comparison_result:
        result_text.insert(tk.END, f"An error occurred: {comparison_result['error']}")
        return
    
    # Check for identical databases
    if not comparison_result['differences'] and not comparison_result['only_in_db1'] and not comparison_result['only_in_db2']:
        result_text.insert(tk.END, "No differences found. The databases are identical.")
        return
    
    # Display tables unique to each database
    if comparison_result['only_in_db1']:
        result_text.insert(tk.END, "Tables only in DB1: " + str(comparison_result['only_in_db1']) + "\n")
    if comparison_result['only_in_db2']:
        result_text.insert(tk.END, "Tables only in DB2: " + str(comparison_result['only_in_db2']) + "\n")
    
    # Display and visualize differences
    if comparison_result['differences']:
        result_text.insert(tk.END, "\nDifferences found in the following tables:\n")
        for diff in comparison_result['differences']:
            result_text.insert(tk.END, f"- {diff['table']}\n")
        
        # Create new window for detailed differences
        diff_window = tk.Toplevel(root)
        diff_window.title("Database Differences")
        diff_window.geometry("1000x600")
        
        # Configure style for difference tabs
        style = ttk.Style()
        style.configure("TNotebook.Tab", padding=[10, 5], font=('TkDefaultFont', 10, 'bold'))
        style.map("TNotebook.Tab",
                  background=[("selected", "#ffffff"), ("!selected", "#ffffff")],
                  foreground=[("selected", "#000000"), ("!selected", "#707570")])
        
        # Create notebook for difference tabs
        notebook = ttk.Notebook(diff_window)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Display differences for each table
        for diff in comparison_result['differences']:
            display_differences(notebook, f"Table: {diff['table']}", diff['data1'], diff['data2'], db1_path, db2_path)
    else:
        result_text.insert(tk.END, "\nNo differences found in common tables.")




# ==============================
# Main GUI Setup Function
# ==============================
def setup_main_gui():
    """
    Set up the main GUI window for the SQLite Database Comparison Tool.

    This function creates the main window, sets up all widgets including
    entry fields for database paths, browse buttons, compare button,
    and a text area for displaying results.

    Global variables created:
        root (tk.Tk): The main application window.
        db1_entry (ttk.Entry): Entry widget for the first database path.
        db2_entry (ttk.Entry): Entry widget for the second database path.
        result_text (tk.Text): Text widget to display comparison results.

    Functions used:
        browse_database(entry): Opens a file dialog to select a database file.
        compare_databases_gui(): Performs the database comparison and displays results.
    """
    global root, db1_entry, db2_entry, result_text

    # Create main window
    root = tk.Tk()
    root.title("DB Compare")
    root.geometry("600x400")
    
    # Set window icon
    try:
        icon = tk.PhotoImage(file='img/ico.png')
        root.iconphoto(True, icon)

    except tk.TclError as e:
        print(f"Error setting icon: {e}")
        # Fallback to a built-in icon if there's an error
        root.iconbitmap('warning')



    # Create main frame
    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Database 1 selection
    ttk.Label(frame, text="Database 1:").grid(column=0, row=0, sticky=tk.W)
    db1_entry = ttk.Entry(frame, width=50)
    db1_entry.grid(column=1, row=0, sticky=(tk.W, tk.E))
    ttk.Button(frame, text="Browse", command=lambda: browse_database(db1_entry)).grid(column=2, row=0)

    # Database 2 selection
    ttk.Label(frame, text="Database 2:").grid(column=0, row=1, sticky=tk.W)
    db2_entry = ttk.Entry(frame, width=50)
    db2_entry.grid(column=1, row=1, sticky=(tk.W, tk.E))
    ttk.Button(frame, text="Browse", command=lambda: browse_database(db2_entry)).grid(column=2, row=1)

    # Compare button
    ttk.Button(frame, text="Compare Databases", command=compare_databases_gui).grid(column=1, row=2)

    # Result display area
    result_text = tk.Text(frame, wrap=tk.WORD, width=70, height=20)
    result_text.grid(column=0, row=3, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Configure grid
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(3, weight=1)

    # Start the main event loop
    root.mainloop()







# ==============================
# Main Execution
# ==============================

if __name__ == "__main__":
    setup_main_gui()

