# Gets the default resoltions of the system

# Since it requires pygame initialized for detection it can only be loaded afterwards

import pygame

#initial screen size. Can be set via command-line option or preferences file
screen_info = pygame.display.Info()
default_screen_size = (screen_info.current_w, screen_info.current_h)

#current screen sizes
screen_size = default_screen_size

# Available resolutions
resolutions = [
    ( 800, 600),
    (1024, 600),
    (1024, 768),
    (1280,1024),

    (1280, 800),
    (1366, 768),
    (1440, 900),
    (1920,1080),
]

