def yscroll(text1, text2, *args):
    if args:
        text1.yview(*args)
        text2.yview(*args)

def on_text_scroll(text1, text2, vsb, *args):
    yscroll(text1, text2, 'moveto', args[0])
    vsb.set(*args)

def xscroll(text1, text2, *args):
    if args:
        text1.xview(*args)
        text2.xview(*args)

def on_text_xscroll(text1, text2, hsb, *args):
    xscroll(text1, text2, 'moveto', args[0])
    hsb.set(*args)

def on_mouse_wheel(event, text1, text2):
    if event.delta:
        delta = event.delta
    elif event.num == 4 or event.num == 5:
        delta = 1 if event.num == 4 else -1
    else:
        return "break"

    scroll_units = -1 * (delta // 120)
    text1.yview_scroll(scroll_units, "units")
    text2.yview_scroll(scroll_units, "units")
    return "break"
