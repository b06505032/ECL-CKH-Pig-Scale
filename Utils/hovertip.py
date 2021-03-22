from tkinter import *
"""
Tools for displaying tool-tips.
ref: https://github.com/python/cpython/blob/master/Lib/idlelib/tooltip.py
"""
class TooltipBase(object):
    def __init__(self, anchor_widget):
        self.anchor_widget = anchor_widget
        self.tipwindow = None

    def __del__(self):
        self.hidetip()

    def showtip(self):
        if self.tipwindow:
            return
        self.tipwindow = tw = Toplevel(self.anchor_widget)
        tw.wm_overrideredirect(1)
        try:
            # This command is only needed and available on Tk >= 8.4.0 for OSX.
            # Without it, call tips intrude on the typing process by grabbing
            # the focus.
            tw.tk.call("::tk::unsupported::MacWindowStyle", "style", tw._w,
                       "help", "noActivates")
        except TclError:
            pass

        self.position_window()
        self.showcontents()
        self.tipwindow.update_idletasks()  # Needed on MacOS -- see #34275.
        self.tipwindow.lift()  # work around bug in Tk 8.5.18+ (issue #24570)

    def position_window(self):
        x, y = self.get_position()
        root_x = self.anchor_widget.winfo_rootx() + x
        root_y = self.anchor_widget.winfo_rooty() + y
        self.tipwindow.wm_geometry("+%d+%d" % (root_x, root_y))

    def get_position(self):
        """choose a screen position for the tooltip"""
        return 20, self.anchor_widget.winfo_height() + 1

    def showcontents(self):
        raise NotImplementedError

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            try:
                tw.destroy()
            except TclError:  # pragma: no cover
                pass

class OnHoverTooltipBase(TooltipBase):
    def __init__(self, anchor_widget, hover_delay=1000):
        super(OnHoverTooltipBase, self).__init__(anchor_widget)
        self.hover_delay = hover_delay

        self._after_id = None
        self._id1 = self.anchor_widget.bind("<Enter>", self._show_event)
        self._id2 = self.anchor_widget.bind("<Leave>", self._hide_event)
        self._id3 = self.anchor_widget.bind("<Button>", self._hide_event)

    def __del__(self):
        try:
            self.anchor_widget.unbind("<Enter>", self._id1)
            self.anchor_widget.unbind("<Leave>", self._id2)  # pragma: no cover
            self.anchor_widget.unbind("<Button>", self._id3) # pragma: no cover
        except TclError:
            pass
        super(OnHoverTooltipBase, self).__del__()

    def _show_event(self, event=None):
        if self.hover_delay:
            self.schedule()
        else:
            self.showtip()

    def _hide_event(self, event=None):
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self._after_id = self.anchor_widget.after(self.hover_delay,self.showtip)

    def unschedule(self):
        after_id = self._after_id
        self._after_id = None
        if after_id:
            self.anchor_widget.after_cancel(after_id)

    def hidetip(self):
        try:
            self.unschedule()
        except TclError:  # pragma: no cover
            pass
        super(OnHoverTooltipBase, self).hidetip()

class Hovertip(OnHoverTooltipBase):
    def __init__(self, anchor_widget, text, hover_delay=1000):
        super(Hovertip, self).__init__(anchor_widget, hover_delay=hover_delay)
        self.text = text

    def showcontents(self):
        label = Label(self.tipwindow, text=self.text, justify=LEFT,
                    background="#ffffe0", relief=SOLID, borderwidth=1)
        label.pack()