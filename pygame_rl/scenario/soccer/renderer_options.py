class RendererOptions(object):
    """Renderer options.
    """
    show_display = False
    max_fps = 0
    enable_key_events = False

    def __init__(self, show_display=False, max_fps=0, enable_key_events=False):
        self.show_display = show_display
        self.max_fps = max_fps
        self.enable_key_events = enable_key_events
