#file: code/singularity.py
#Copyright (C) 2005 Evil Mr Henry, Phil Bordelon, Brian Reid, MestreLion
#This file is part of Endgame: Singularity.

#Endgame: Singularity is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.

#Endgame: Singularity is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.
#A full copy of this license is provided in GPL.txt

#This file sets up initial values from command line and preferences file,
# initialize hardware, load data files and show main screen. Do not execute it
# directly. use ../singularity.py instead.

# Set language first, so help page and all error messages can be translated
import g
g.set_language()
g.load_messages()

# Since we require numpy anyway, we might as well ask pygame to use it.
try:
    import pygame
    pygame.surfarray.use_arraytype("numpy")
except AttributeError:
    pass # Pygame older than 1.8.
except ValueError:
    raise SystemExit("Endgame: Singularity requires NumPy.")
except ImportError:
    raise SystemExit("Endgame: Singularity requires pygame.")

import sys
import ConfigParser
import os.path
import optparse
import logging

import graphics.g

pygame.init()
pygame.font.init()
pygame.key.set_repeat(1000, 50)

# Can only be loaded after pygame init
import graphics.resolution

# Manually "pre-parse" command line arguments for -s|--singledir and --multidir,
# so g.get_save_folder reports the correct location of preferences file
for parser in sys.argv[1:]:
    if parser == "--singledir" or parser == "-s": g.force_single_dir = True
    if parser == "--multidir"                   : g.force_single_dir = False

#configure global logger
logfile = os.path.join(g.get_save_folder(True), "error.log")
if len(logging.getLogger().handlers) == 0:
    try:
        logging.getLogger().addHandler(logging.FileHandler(logfile, delay=True))
    except TypeError: # Python < 2.6, delay not supported yet.
        try:
            logging.getLogger().addHandler(logging.FileHandler(logfile))
        except IOError: # Probably access denied with --singledir. That's ok
            pass

#load prefs from file:
save_dir = g.get_save_folder(True)
save_loc = os.path.join(save_dir, "prefs.dat")
if os.path.exists(save_loc):

    prefs = ConfigParser.SafeConfigParser()
    savefile = open(save_loc, "r")
    try:
        prefs.readfp(savefile)
    except Exception, reason:
        sys.stderr.write("Cannot load preferences file %s! (%s)\n" % (save_loc, reason))
        sys.exit(1)

    if prefs.has_section("Preferences"):
        try:
            desired_language = prefs.get("Preferences", "lang")
            if desired_language in g.available_languages():
                g.set_language(desired_language)
            else:
                raise ValueError
        except:
            sys.stderr.write("Invalid or missing 'lang' in preferences.\n")

        try:
            if prefs.getboolean("Preferences", "fullscreen"):
                graphics.g.fullscreen = pygame.FULLSCREEN
        except:
            sys.stderr.write("Invalid or missing 'fullscreen' setting in preferences.\n")

        try:
            g.nosound = prefs.getboolean("Preferences", "nosound")
        except:
            sys.stderr.write("Invalid or missing 'nosound' setting in preferences.\n")

        try:
            pygame.event.set_grab(prefs.getboolean("Preferences", "grab"))
        except:
            sys.stderr.write("Invalid or missing 'grab' setting in preferences.\n")

        try:
            g.daynight = prefs.getboolean("Preferences", "daynight")
        except:
            sys.stderr.write("Invalid or missing 'daynight' setting in preferences.\n")

        try:
            g.soundbuf = prefs.getint("Preferences", "soundbuf")
        except:
            sys.stderr.write("Invalid or missing 'soundbuf' setting in preferences.\n")

        try:
            graphics.resolution.screen_size = (prefs.getint("Preferences", "xres"),
            graphics.resolution.screen_size[1])
        except:
            sys.stderr.write("Invalid or missing 'xres' resolution in preferences.\n")

        try:
            graphics.resolution.screen_size = (graphics.g.screen_size[0],
            prefs.getint("Preferences", "yres"))
        except:
            sys.stderr.write("Invalid or missing 'yres' resolution in preferences.\n")

#Handle the program arguments.
desc = """Endgame: Singularity is a simulation of a true AI. Go from computer to computer, pursued by the entire world. Keep hidden, and you might have a chance."""
parser = optparse.OptionParser(version=g.version, description=desc,
                               prog="singularity")
parser.add_option("--sound", action="store_true", dest="sound",
                  help="enable sound (default)")
parser.add_option("--nosound", action="store_false", dest="sound",
                  help="disable sound")
parser.add_option("--daynight", action="store_true", dest="daynight",
                  help="enable day/night display (default)")
parser.add_option("--nodaynight", action="store_false", dest="daynight",
                  help="disable day/night display")
langs = g.available_languages()
parser.add_option("-l", "--lang", "--language", dest="language", type="choice",
                  choices=langs, metavar="LANG",
                  help="set the language to LANG (available languages: " +
                       " ".join(langs) + ", default " + g.language +")")
parser.add_option("-g", "--grab", help="grab the mouse pointer", dest="grab",
                  action="store_true")
parser.add_option("--nograb", help="don't grab the mouse pointer (default)",
                  dest="grab", action="store_false")
parser.add_option("-s", "--singledir",  dest="singledir",
                  help="keep saved games and settings in the Singularity directory",
                  action="store_true")
parser.add_option("--multidir", dest="singledir",
                  help="keep saved games and settings in an OS-specific, per-user directory (default)",
                  action="store_false")
parser.add_option("--soundbuf", type="int",
                  help="set the size of the sound buffer (default 2048)")

display_options = optparse.OptionGroup(parser, "Display Options")
display_options.add_option("-r", "--res", "--resolution", dest="resolution",
                           help="set resolution to custom RES (default %dx%d)" %
                           graphics.resolution.default_screen_size,
                           metavar="RES")
for res in ["%dx%d" % res for res in graphics.resolution.resolutions]:
    display_options.add_option("--" + res, action="store_const",
                               dest="resolution", const=res,
                               help="set resolution to %s" % res)
display_options.add_option("--fullscreen", action="store_true",
                           help="start in fullscreen mode")
display_options.add_option("--windowed", action="store_false",
                           help="start in windowed mode (default)")
parser.add_option_group(display_options)

olpc_options = optparse.OptionGroup(parser, "OLPC-specific Options")
olpc_options.add_option("--xo1", action="store_const",
                        dest="resolution", const="1200x900",
                        help="set resolution to 1200x900 (OLPC XO-1)")
olpc_options.add_option("--ebook", help="enables gamepad buttons for use in ebook mode.  D-pad moves mouse, check is click.  O speeds up time, X slows down time, and square stops time.",
                        action="store_true", default=False)
parser.add_option_group(olpc_options)

hidden_options = optparse.OptionGroup(parser, "Hidden Options")
hidden_options.add_option("-p", help="(ignored)", metavar=" ")
hidden_options.add_option("-d", "--debug", help="for finding bugs",
                          action="store_true", default=False)
hidden_options.add_option("--cheater", help="for bad little boys and girls",
                          action="store_true", default=False)
# Uncomment to make the hidden options visible.
#parser.add_option_group(hidden_options)
(options, args) = parser.parse_args()

if options.language is not None:
    g.set_language(options.language)
if options.resolution is not None:
    try:
        xres, yres = options.resolution.split("x")
        graphics.resolution.screen_size = (int(xres), int(yres))
    except Exception:
        parser.error("Resolution must be of the form <h>x<v>, e.g. %dx%d." %
                     graphics.resolution.default_screen_size)
if options.grab is not None:
    pygame.event.set_grab(options.grab)
if options.fullscreen is not None:
    graphics.g.fullscreen = options.fullscreen
if options.sound is not None:
    g.nosound = not options.sound
if options.daynight is not None:
    g.daynight = options.daynight
if options.soundbuf is not None:
    g.soundbuf = options.soundbuf

graphics.g.ebook_mode = options.ebook

g.cheater = options.cheater
g.debug = options.debug

pygame.display.set_caption("Endgame: Singularity")

#I can't use the standard image dictionary, as that requires the screen to
#be created.
if pygame.image.get_extended() == 0:
    print "Error: SDL_image required. Exiting."
    sys.exit(1)

#init data:
g.load_strings()
g.load_events()
g.load_locations()
g.load_techs()
g.load_items()
g.load_bases()

# Initialize the screen with a dummy size.
pygame.display.set_mode(graphics.resolution.screen_size)

g.init_graphics_system()
g.reinit_mixer()
g.load_sounds()
g.load_music()

# Set the application icon.
pygame.display.set_icon(graphics.g.images["icon.png"])

#Display the main menu
#Import is delayed until now so selected language via command-line options or
# preferences file can be effective
from screens import main_menu
menu_screen = main_menu.MainMenu()
menu_screen.show()
