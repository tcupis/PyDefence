"""
Project: PyDefence
Author: Tom Cupis
Date started: 5/9/2018

"""

#* Imports/dependencies
#Standard libraries
import time
import random
import os
import math
import json

#Required libraries
try:
    import tkinter as tk
    import data.rpc as rpc
    import _thread as thr
    import base64 as b64

    from tkinter import messagebox
    from datetime import datetime
    from PIL import Image, ImageTk
except:
    #Quit if failed
    raise


class PyDefence():
    #PyDefence class will act as a helper file with common methods/variables
    
    #* Helper config methods
    def __init__(self):
        #Screen constants
        self.WINDOW_RESOLUTIONS = [
            [800,450],
            [960,540],
            [1024,576],
            [1280,720],
            [1366,768],
            [1440,810],
            [1600,900],
            [1920,1080],
            [2048,1152],
            [2304,1296],
            [2560,1440],
            [3200,1800],
            [3840,2160],
            [4096,2304],
            [5120,2880]
        ]
        self.MAIN_FRAME_WIDTH_RATIO = 16
        self.MAIN_FRAME_HEIGHT_RATIO = 9

        #Game constants
        self.TEXTURE_PACKS = list(filter(lambda d:os.path.isdir("textures/"+d), os.listdir("textures/")))
        self.UNIQUE_KEY = "PYDEFENCE"
        self.SETTINGS_PATH  = "data/settings.json"

        #Read and apply settings from file
        try:
            settings = json.loads(open(self.SETTINGS_PATH, 'r').read())
            
            self.RESOLUTION = settings["resolution"] 
            self.FULLSCREEN = settings["fullscreen"] 
            self.CLIENT_NAME = settings["client_name"] 
            self.ACTIVE_TEXTURE = settings["texture_pack"] 
            self.DRP_ENABLED = settings["rich_presence"] 
            self.DEBUG = settings["debug"] 
            self.DS_ADDRESS = settings["server_address"] 
            self.defaults_loaded = False
        except:
            self.setDefaults()
            self.defaults_loaded = True
            self.alert("Invalid/No 'settings.json' file\nDefaults loaded", "Warning")


        #Developer/debug constants
        if self.DEBUG:
            print("Debug Mode: ENABLED")
            open("data/debug.data", 'a').write("\n\n<<< NEW SESSION AT {} >>>\n".format(datetime.now().strftime("%H:%M:%S.%f")))
        
        #Rich presence
        self.drp()


        #Get game save data (badges)
        self.GAME_DATA_PATH = "data/save.data"
        
        #Try to open file, create default if unsuccessful
        try: 
            self.GAME_DATA = json.loads(self.decode_85(open(self.GAME_DATA_PATH, 'r').read()))
        except:
            open(self.GAME_DATA_PATH, 'w').write(self.encode_85('{"badges_unlocked": [], "highscore": 0}'))

        self.GAME_DATA = json.loads(self.decode_85(open(self.GAME_DATA_PATH, 'r').read()))
        self.log("badges unlocked {}".format(self.GAME_DATA["badges_unlocked"]))

        #Help text
        self.HELP_TEXT = {
            "0": "ABILITIES\nThere are 6 abilities all with varying costs. Purchase once and use for the entire game. Must be purchased in order of cost",
            "1": "PAUSE BUTTON\nPause a game for as long as you want with the pause button. Unlimited uses! You may exit the game from this screen",
            "2": "UNITS\nPlay with the default units or edit the config files and even add your own. Don't let them reach your base!",
            "3": "GAME MODES\n Feeling nervous? Pick from 4 unique game modes for players of all abilities. Beat your highscores and earn all the badges!",
            "4": "TOWERS\nPlay with 9 default and balanced towers. Place them around the path to protect your base! Click on a tower to sell it",
            "5": "SETTINGS\nChange PyDefence to suit your requirements. Only available from the title screen. *A game restart maybe required*"
        }

        #Gameplay constants
        self.FPS = 60
        self.TILE_VARIANCE = 0.08

        self.DEFAULT_PRE_ROUND_TIME = 30
        self.max_pre_round_time = 30

        self.EASY_NO_ROUNDS = 20
        self.NORMAL_NO_ROUNDS = 30
        self.HARD_NO_ROUNDS = 40
        self.CRAZY_NO_ROUNDS = 50

        self.EASY_START_MONEY = 8000
        self.NORMAL_START_MONEY = 5000
        self.HARD_START_MONEY = 3000
        self.CRAZY_START_MONEY = 2000

        self.EASY_BASE_HEALTH = 4000
        self.NORMAL_BASE_HEALTH = 2500
        self.HARD_BASE_HEALTH = 1000
        self.CRAZY_BASE_HEALTH = 100

        self.DEFAULT_GAME_DETAIL_DESCRIPTION = "Hover over an item to see details"

        self.ABILITY_INFO = {
                            "1": {
                                "name": "Ice sheet",
                                "description": "A blizzard of ice to stop oncoming enemies",
                                "cost": 1000,
                                "once_per_round": False,
                                "cooldown_step" : 3.5
                            },
                            "2": {
                                "name": "Weakness potion",
                                "description": "Reduce enemies strength by 1/2 for 20 seconds",
                                "cost": 3000,
                                "once_per_round": False,
                                "cooldown_step" : 10
                            },
                            "3": {
                                "name": "Death wave",
                                "description": "Reduce the enemies current health by a third",
                                "cost": 5000,
                                "once_per_round": False,
                                "cooldown_step" : 15
                            },
                            "4": {
                                "name": "x3 Troop value",
                                "description": "x3 the value of the troops in the wave for 3 seconds",
                                "cost": 8000,
                                "once_per_round": True,
                                "cooldown_step" : 0
                            },
                            "5": {
                                "name": "Heal base",
                                "description": "Heal your base 1/4 it's original health",
                                "cost": 10000,
                                "once_per_round": True,
                                "cooldown_step" : 0
                            },
                            "6": {
                                "name": "Tower potion",
                                "description": "2x tower projectile damage for 10 seconds",
                                "cost": 15000,
                                "once_per_round": False,
                                "cooldown_step" : 15
                            }
            }

        self.base_attributes = {
            "rate_of_fire": 1.0,
            "cost": 0,
            "range": 1,
            "min_range": 0,
            "projectile": {
                "texture_name": "base-projectile.png",
                "damage": 30.0,
                "speed": 1.0,
                "splash_area": 1.0,
                "lifetime": 20.0, 
                "mod_time": 3.0,
                "speed_mod": 1.0,
                "damage_mod": 1.0,
                "value_mod": 1.0
                }
            }

        #Gameplay variables
        self.game_images_scaled = False
        self.crazy_toggle_state = False
        self.pause_toggle_state = False
        self.multiplayer_toggle_state = "JOIN"
        self.last_unlocked_ability = 0
        self.money = 0
        self.current_base_health = 0
        self.max_base_health = 1
        self.current_round = 0
        self.max_rounds = 0
        self.units_killed = 0
        self.time_left = 0
        self.difficulty_value = 0
        self.game_over = False
        self.wave = []
        self.game_speed_mod = 1
        self.projectiles_active = 0
        self.MAX_PROJECTILES = 30

        #Fonts
        self.default_font = "Verdana"


    def setDefaults(self):
        self.RESOLUTION = self.WINDOW_RESOLUTIONS[0]
        self.FULLSCREEN = False
        self.CLIENT_NAME = "Player{}".format(random.randint(1,2**16))
        self.ACTIVE_TEXTURE = "default_texture"
        self.DRP_ENABLED = False
        self.DEBUG = True
        self.DS_ADDRESS = "pydefence.tk"


    #* Encryption methods
    def encode_85(self, data):
        #Encode data in base 85 format
        encode_key = b64.b85encode(self.UNIQUE_KEY.encode())
        encoded_data = b64.b85encode(str(data).encode())

        encoded_final = b64.b85encode(encode_key+encoded_data).decode()

        return encoded_final

    def decode_85(self, data):
        #Decode data in base 85 format
        decoded_data = b64.b85decode(str(data).encode())
        encode_key = b64.b85encode(self.UNIQUE_KEY.encode()).decode()

        decoded_final = b64.b85decode(decoded_data[len(encode_key):]).decode()

        return decoded_final

    #* Scaling methods
    def calcFrameSize(self, frame_w, frame_h, screen_w, screen_h):
        #Find the max widths/heights using a specified aspect ratio

        #Calculate frame and screen ratios
        frame_ratio = frame_w / frame_h
        screen_ratio = screen_w / screen_h

        #Compare ideal frame ratio to screen ratio
        if screen_ratio > frame_ratio:
            self.calc_width = (screen_h / frame_h) * frame_w #scale width
            self.calc_height = screen_h
        else:
            self.calc_height = (screen_w / frame_w) * frame_h #scale height
            self.calc_width = screen_w

        #Return scaled width/height
        return int(self.calc_width), int(self.calc_height)

    def fontScale(self, native_size):
        #Scale font to screen size
        scaled_font = int((((self.calc_height/1080)+(self.calc_width/1920))/2)*native_size)
        return scaled_font

    #* Load all images 
    def loadInitialImages(self, res_w=1920, res_h=1080):
        #Load all images needed for the title screen, expected wait <1 sec

        #Calculate scale factors for 1080p textures
        self.x_scalefactor = res_w/1920
        self.y_scalefactor = res_h/1080
        self.tile_scalefactor = 1 #init this var for later

        self.log("scaling initial images by factors ({}, {})".format(self.x_scalefactor, self.y_scalefactor))

        #Cursor
        self.CURSOR = "@textures/"+self.ACTIVE_TEXTURE+"/ui/cursor.ico"

        # Title screen
        self.BG_IMG = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/bg.png")
        self.BUTTON_POLE = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/button-pole.png")

        #Main panel
        self.TITLE_PANEL = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/title-panel.png")
        self.PLAY_BUTTON = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/play-button.png")
        self.SETTINGS_BUTTON = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/settings-button.png")
        self.HELP_BUTTON = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/help-button.png")
        self.QUIT_BUTTON = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/quit-button.png")

        #Gamemode panel
        self.EASY_BUTTON = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/easy-button.png")
        self.NORMAL_BUTTON = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/normal-button.png")
        self.HARD_BUTTON = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/hard-button.png")
        self.MULTIPLAYER_BUTTON = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/multiplayer-button.png")

        #GM details panel
        self.EASY_PANEL = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/easy-panel.png")
        self.NORMAL_PANEL = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/normal-panel.png")
        self.HARD_PANEL = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/hard-panel.png")
        self.MULTIPLAYER_PANEL = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/multiplayer-panel.png")

        self.EASY_BADGE = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/easy-badge.png")
        self.NORMAL_BADGE = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/normal-badge.png")
        self.HARD_BADGE = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/hard-badge.png")
        self.CRAZY_BADGE = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/special-badge.png")
        self.BLANK_BADGE = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/blank-badge.png")

        self.thumbnail_image = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/map-placeholder.png")
        self.MAP_OVERLAY = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/map-overlay.png")
        self.LAUNCH_BUTTON = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/launch-button.png")
        self.OPEN_BUTTON = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/open-button.png")
        self.MULTIPLAYER_JOIN = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/multiplayer-join.png")
        self.MULTIPLAYER_CREATE = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/multiplayer-create.png")
        self.LOBBY_PLAQUE = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/lobby-plaque.png")

        self.MONEY_ICON = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/money-icon.png")
        self.CRAZY_ON = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/crazy-on.png")

        #Content panel
        self.CHECKBOX_BLANK = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/checkbox-blank.png")
        self.SETTINGS_PANEL = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/settings-panel.png")
        self.FULLSCREEN_ON = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/fullscreen-on.png")
        self.DRP_ON = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/drp-on.png")
        self.DEBUG_ON = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/debug-on.png")
        self.RESET_BUTTON = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/reset-button.png")
        self.NEXT_BUTTON = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/next-button.png")
        self.PREV_BUTTON = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/prev-button.png")
        self.HELP_PANEL = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/help-panel.png")
        self.SAVE_BUTTON = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/save-button.png")
        self.CLOSE_BUTTON = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/close-button.png")

        self.HELP_IMAGE_0 = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/help-image-0.png")
        self.HELP_IMAGE_1 = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/help-image-1.png")
        self.HELP_IMAGE_2 = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/help-image-2.png")
        self.HELP_IMAGE_3 = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/help-image-3.png")
        self.HELP_IMAGE_4 = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/help-image-4.png")
        self.HELP_IMAGE_5 = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/title/help-image-5.png")

        #Loading screen
        self.LOADING_OVERLAY = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/loading/main-cover.png")
        self.LOADING_BAR = self.image("textures/"+self.ACTIVE_TEXTURE+"/ui/loading/main-bar.png")

        self.log("title image scaling finished")

        #Store image paths for gameplay
        self.game_images = [
            ["MAP_START_PTR", "textures/"+self.ACTIVE_TEXTURE+"/map/misc/start-ptr.png"],
            ["MAP_END_PTR", "textures/"+self.ACTIVE_TEXTURE+"/map/misc/end-ptr.png"],
            
            ["MAP_PATH_BL", "textures/"+self.ACTIVE_TEXTURE+"/map/paths/path-bl.png"],
            ["MAP_PATH_BR", "textures/"+self.ACTIVE_TEXTURE+"/map/paths/path-br.png"],
            ["MAP_PATH_TL", "textures/"+self.ACTIVE_TEXTURE+"/map/paths/path-tl.png"],
            ["MAP_PATH_TR", "textures/"+self.ACTIVE_TEXTURE+"/map/paths/path-tr.png"],
            ["MAP_PATH_X", "textures/"+self.ACTIVE_TEXTURE+"/map/paths/path-x.png"],
            ["MAP_PATH_Y", "textures/"+self.ACTIVE_TEXTURE+"/map/paths/path-y.png"],

            ["MAP_DECO_FARM_1", "textures/"+self.ACTIVE_TEXTURE+"/map/decorations/farm-1.png"],
            ["MAP_DECO_FARM_2", "textures/"+self.ACTIVE_TEXTURE+"/map/decorations/farm-2.png"],
            ["MAP_DECO_FARM_3", "textures/"+self.ACTIVE_TEXTURE+"/map/decorations/farm-3.png"],
            ["MAP_DECO_GRASS", "textures/"+self.ACTIVE_TEXTURE+"/map/decorations/grass.png"],
            ["MAP_DECO_HUT", "textures/"+self.ACTIVE_TEXTURE+"/map/decorations/hut.png"],
            ["MAP_DECO_POND", "textures/"+self.ACTIVE_TEXTURE+"/map/decorations/pond.png"],
            ["MAP_DECO_ROCK_1", "textures/"+self.ACTIVE_TEXTURE+"/map/decorations/rock-1.png"],
            ["MAP_DECO_ROCK_2", "textures/"+self.ACTIVE_TEXTURE+"/map/decorations/rock-2.png"],
            ["MAP_DECO_WELL", "textures/"+self.ACTIVE_TEXTURE+"/map/decorations/well.png"],

            ["BASE_1", "textures/"+self.ACTIVE_TEXTURE+"/towers/base/castle-1.png"],
            ["BASE_2", "textures/"+self.ACTIVE_TEXTURE+"/towers/base/castle-2.png"],
            ["BASE_3", "textures/"+self.ACTIVE_TEXTURE+"/towers/base/castle-3.png"],
            ["BASE_UPGRADE", "textures/"+self.ACTIVE_TEXTURE+"/towers/base/upgrade-base.png"],

            ["BASE_START", "textures/"+self.ACTIVE_TEXTURE+"/map/paths/start-overlay.png"],

            ["TOWER_SELL_ICON", "textures/"+self.ACTIVE_TEXTURE+"/towers/tower-sell-icon.png"],

            ["CONTROL_BG", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/control-bg.png"],
            ["TITLE_IMAGE", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/title-bar.png"],
            ["SELECTION_AREA", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/selection-area.png"],
            ["SPECIAL_BAR", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/special-bar.png"],
            ["CHAT_AREA", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/chat-area.png"],
            ["SEND_MSG_BUTTON", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/send-msg-button.png"],

            ["PLAY_BUTTON_ON", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/play-button-on.png"],
            ["PLAY_BUTTON_OFF", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/play-button-off.png"],
            ["HELP_BUTTON", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/help-button.png"],
            ["HELP_BUTTON_ACTIVE", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/help-button-active.png"],
            ["HELP_OVERLAY", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/help-overlay.png"],
            ["CHAT_BUTTON", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/chat-button.png"],
            ["CHAT_BUTTON_DISABLED", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/chat-button-disabled.png"],
            ["CHAT_BUTTON_ACTIVE", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/chat-button-active.png"],
            ["PAUSE_BUTTON", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/pause-button.png"],
            ["PAUSE_BUTTON_ACTIVE", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/pause-button-active.png"],

            ["PAUSE_MAP_OVERLAY", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/pause-map-overlay.png"],

            ["GAMEOVER_OVERLAY", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/gameover-overlay.png"],
            ["GAMEOVER_LOGO", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/gameover-logo.png"],
            ["GAMEOVER_LOST", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/gameover-lost.png"],
            ["GAMEOVER_WON", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/gameover-won.png"],
            ["BACK_TITLE_BUTTON", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/back-title-button.png"],
            ["CONTINUE_GAME_BUTTON", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/continue-game-button.png"],


            ["ABILITY_1", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/abilities/ability-1.png"],
            ["ABILITY_2", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/abilities/ability-2.png"],
            ["ABILITY_3", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/abilities/ability-3.png"],
            ["ABILITY_4", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/abilities/ability-4.png"],
            ["ABILITY_5", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/abilities/ability-5.png"],
            ["ABILITY_6", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/abilities/ability-6.png"],

            ["FREEZE_OVERLAY", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/abilities/freeze-overlay.png"],
            ["DEATHWAVE_OVERLAY", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/abilities/deathwave-overlay.png"],

            ["ABILITY_LOCK_OVERLAY", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/abilities/ability-locked-overlay.png"],
            ["ABILITY_COOLDOWN_4", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/abilities/ability-cooldown-4.png"],
            ["ABILITY_COOLDOWN_3", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/abilities/ability-cooldown-3.png"],
            ["ABILITY_COOLDOWN_2", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/abilities/ability-cooldown-2.png"],
            ["ABILITY_COOLDOWN_1", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/abilities/ability-cooldown-1.png"],
            ["ABILITY_COOLDOWN_ROUND", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/abilities/ability-cooldown-round.png"],

            ["PANEL_TOWER_PLAQUE", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/tower-plaque.png"],
            ["PANEL_TOWER_PLAQUE_INFO", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/tower-plaque-info.png"],
            ["PANEL_BUY_BUTTON", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/buy-tower-button.png"],
            ["PANEL_CANCEL_BUTTON", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/cancel-purchase-button.png"],
            ["PANEL_INFO_BUTTON", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/tower-info-button.png"],
            ["PANEL_INFO_CLOSE_BUTTON", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/tower-info-close-button.png"],
            ["HORIZONTAL_SLIDER", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/horizontal-slider.png"],

            ["AUTO_RUN_OFF", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/auto-run-off.png"],
            ["AUTO_RUN_ON", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/auto-run-on.png"],
            ["TIME_1", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/time-1.png"],
            ["TIME_2", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/time-2.png"],
            ["TIME_4", "textures/"+self.ACTIVE_TEXTURE+"/ui/gameplay/time-4.png"],

            ["UNIT_DEATH_FRAME", "textures/"+self.ACTIVE_TEXTURE+"/units/death-frame.png"],
            ["PROJ_DEATH_FRAME", "textures/"+self.ACTIVE_TEXTURE+"/towers/projectiles/projectile-death-frame.png"],

        ]

        #Check for any custom decorations
        try:
            custom_deco = 0
            for img in os.listdir("textures/"+self.ACTIVE_TEXTURE+"/map/decorations/"):
                if img.split(".")[-1] in ["png", "jpg"] and img not in ['farm-1.png', 'farm-2.png', 'farm-3.png', 'grass.png', 'hut.png', 'pond.png', 'rock-1.png', 'rock-2.png', 'well.png']:
                    self.game_images.append(["MAP_"+str(img).upper(), "textures/"+self.ACTIVE_TEXTURE+"/map/decorations/"+img])
                    custom_deco += 1
            if custom_deco > 0:
                self.alert("Found {} textures!\nHopefully you know what you're doing!".format(custom_deco))
        except FileNotFoundError:
            self.alert("No texture pack with name '{}' found!\n\nPlease relocate the texture pack to the /textures/ folder \nor change the texture name in the 'settings.json' file".format(self.ACTIVE_TEXTURE), "Warning")

    def loadGameImages(self, map_size):
        #Load all images used for gameplay, time >2 secs
        self.log("scaling gameplay images by factors ({}, {})".format(self.x_scalefactor, self.y_scalefactor))

        #Summary texts
        self.summary_texts = ["Collecting helmets",
                              "Sharpening swords",
                              "Constructing towers",
                              "Laying pavestones",
                              "Transforming landscape",
                              "Scattering pebbles",
                              "Polishing boots",
                              "Lighting fires",
                              "Positioning troops"]

        #Initial variables
        self.game_image_progress = 0
        game_image_objects = {}

        #Loading status
        self.current_summary_text = "Gathering equipment..."

        #Create scaled image objects
        for i in range(len(self.game_images)):
            self.current_image_path = self.game_images[i][1]

            #Scale map textures depending map size
            if "MAP" in self.game_images[i][0][:3] or self.game_images[i][0][:5].replace("_", "") in ["UNIT", "BASE", "PROJ", "TOWER"]:
                self.tile_scalefactor = 6/map_size
            elif "PREV_TOWER_" in self.game_images[i][0]:
                self.tile_scalefactor = 0.75
            else:
                self.tile_scalefactor = 1

            #Put the image in the dictionary
            game_image_objects[self.game_images[i][0]] = self.image(self.current_image_path)
            self.game_image_progress = (i) / (len(self.game_images)) #loading percentage

            #Random text display
            if i % (len(self.game_images)//2) == 0:
                self.current_summary_text = random.choice(self.summary_texts)
                del self.summary_texts[self.summary_texts.index(self.current_summary_text)]

        
        #Log image completion
        self.log("image dictionary created")

        #Make the completed dictionary accessible
        self.GAME_IMAGE_DICT = game_image_objects

        #Process complete
        time.sleep(0.3)
        self.game_images_scaled = True


    #* Image manipulation methods
    def image(self, path, resetTileSF=False, theta=0):
        #Takes a path and returns an image object

        #! Validation
        #Tries to open the image if fails replaces with missing texture
        try:
            open(path)
        except (FileNotFoundError, PermissionError):
            self.log("missing texture {}".format(path))
            path = "textures/missing.png"
            try:
                open(path)
            except (FileNotFoundError, PermissionError):
                self.alert("No missing texture found!", "FATAL")
                quit()

        #If sf needs to be reset
        if resetTileSF:
            self.tile_scalefactor = 1

        #Create image object
        img = Image.open(path).rotate(theta)
        if self.x_scalefactor != 1 or self.y_scalefactor != 1 or self.tile_scalefactor != 1: #don't resize if not needed

            #Get current and new size
            width, height = img.size
            new_size = (int(width*self.x_scalefactor*self.tile_scalefactor)+1, int(height*self.y_scalefactor*self.tile_scalefactor)+1)

            #Resize with antialiasing
            img = img.resize(new_size, Image.ANTIALIAS)

            #Log image change
            self.log("{} from ({},{}) to ({},{}) with rotation ({} deg)".format(path, width, height, new_size[0], new_size[1], theta))

        #Return object
        return ImageTk.PhotoImage(img)
    

    #* General program function
    def loadJSON(self, JSON_string):
        #Return a dictionary from json string
        return json.loads(JSON_string)

    def log(self, data):
        #Takes data and prints if debugging is enabled
        if self.DEBUG:
            print(datetime.now().strftime("%H:%M:%S.%f"),">>>", data)
            open("data/debug.data", 'a').write("{} >>> {}\n".format(datetime.now().strftime("%H:%M:%S.%f"), data))

    def alert(self, msg, title="Alert!", event=""):
        #Prompt an OS alert
        tk.Tk().withdraw()
        messagebox.showinfo(title, msg)

    #* Math methods
    def linearInterpolation2D(self, p0, p1, t):
        #Interpolate between p0,p1 by percentage t
	    return ((1 - t) * p0[0] + t * p1[0], (1 - t) * p0[1] + t * p1[1])

    def euclidDistance2D(self, p0, p1):
        #Calculate euclidean distance between p0, p1
        return ((p1[0]-p0[0])**2 + (p1[1]-p0[1])**2)**0.5

    def gauss2D(self, mu, sigma):
        #Generate 2d normal distribution
        x = random.gauss(mu, sigma)
        y = random.gauss(mu, sigma)

        #Min max output to prevent units over spilling
        return (min(0.25, max(-0.25, x)), min(0.25, max(-0.25, y)))

    def calcAngle2D(self, x1, y1, x2, y2):
        #Calculate angle between two points in 2d space
        theta = (x2-x1)/max(1, abs(x2-x1)) * (180/math.pi) * math.acos((y1-y2)/((x1-x2)**2+(y1-y2)**2)**0.5)
        if y2 > y1 and int(theta) == 0: theta = 180
        if theta <= 0: theta = abs(360+theta)
        return int(360.5-theta)

    #* Animation methods
    def glide(self, canvas, tag, start, end, duration):
        start_time = time.time()
        #Animate tag on a canvas between start and end points
        while time.time()-start_time <= duration: #force sync - will take exact duration to complete, no way to slow it
            self.deathwave_coords = self.linearInterpolation2D(start, end, (time.time()-start_time)/duration)
            canvas.coords(tag, self.deathwave_coords)
            time.sleep(1/(duration*self.FPS)) #frame limiter
        
        canvas.coords(tag, end)
        self.deathwave_coords = end


    #* Discord rich presence
    def updateDRP(self, state="", detail="", sm_txt="", lg_txt="", sm_img="", lg_img=""):
        #Update DRP status
        if state != "": self.rp_state = state
        if detail != "": self.rp_details = detail
        if sm_txt != "": self.rp_sm_txt = sm_txt
        if lg_txt != "": self.rp_lg_txt = lg_txt
        if sm_img != "": self.rp_sm_img = sm_img
        if lg_img != "": self.rp_lg_img = lg_img

    def drp(self):
        #Discord rich presence thread
        def drp_thread(self, refresh_time=15):
            while self.DRP_ENABLED:
                activity = {
                        "state": str(self.rp_state),
                        "details": str(self.rp_details),
                        "assets": {
                            "small_text": str(self.rp_sm_txt),
                            "small_image": self.rp_sm_img,
                            "large_text": str(self.rp_lg_txt),
                            "large_image": self.rp_lg_img
                        }
                    }
                try: rpc_obj.set_activity(activity)
                except OSError: pass
                time.sleep(refresh_time) #15 sec API limiter 
            
            try: rpc_obj.close()
            except: pass

        #Pydefence client id
        client_id = '522197869311164436'

        #Attempt to enable
        try:
            rpc_obj = rpc.DiscordIpcClient.for_platform(client_id)
        except:
            self.DRP_ENABLED = False

        #Default states
        self.rp_state = "Launching..."
        self.rp_details = "Playing PyDefence"
        self.rp_sm_txt = "null"
        self.rp_lg_txt = "PyDefence"
        self.rp_sm_img = "null"
        self.rp_lg_img = "logo"

        #DRP thread launch
        thr.start_new_thread(drp_thread, (self, ))


#* Game objects
class Tile():
    #Data object for storing tile data

    def __init__(self, x_pos, y_pos, tag, texture=None):
        self.x = x_pos
        self.y = y_pos
        self.tag = tag

        self.texture = texture

class Unit():
    #Object for storing and executing unit gameplay

    #* Unit setup
    def __init__(self, _canvas, _name, _image, _attributes, pyd, tag=None):
        #Helper
        self.pyd = pyd

        #Preset information from JSON/main app
        self.name = _name
        self.image = _image
        self.speed = _attributes["speed"]
        self.strength = _attributes["strength"]
        self.health_max = _attributes["health"]
        self.value = _attributes["value"]
        self.specials = _attributes["specials"]

        #Canvas/gameplay information
        self.DEATH_FRAME = self.pyd.GAME_IMAGE_DICT["UNIT_DEATH_FRAME"]

        self.canvas = _canvas
        self.tag = tag
        self.active_image_object = None
        self.pos = (0,0)
        self.active = False
        self.fps = self.pyd.FPS
        self.health = self.health_max
        self.stopped = False
        self.force_colour = False
        self.r, self.g, self.b = 0, 0, 0
        
        #Imported methods
        self.euclidDistance2D = self.pyd.euclidDistance2D
        self.linearInterpolation2D = self.pyd.linearInterpolation2D

    def setupUnit(self, _images, _path, _sf):
        #All information required to animate a unit object
        self.image = _images
        self.path = _path
        self.sf = _sf

    def toggleStop(self):
        #Toggle if the unit needs to stop e.g. a pause
        if self.stopped:
            self.stopped = False
        else:
            self.stopped = True


    #* Unit gameplay methods
    def die(self):
        #Kills the unit object and updates variables 
        self.active = False
        self.pyd.units_killed += 1
        self.pyd.money += self.value
        self.health = -1
        self.canvas.delete("HEALTH"+str(self.tag))
        self.canvas.itemconfigure(self.tag, image=self.DEATH_FRAME)
        time.sleep(3)
        self.canvas.delete(str(self.tag))

    def damageBase(self, amount=0):
        #Damages the players base
        if amount == 0:
            amount = self.strength

        self.pyd.current_base_health -= amount/128 #balanced dps

    def reduceHealth(self, amount):
        #Reduces the health of the unit
        self.health -= amount
        self.health = max(0, self.health)

        #Calculate healthbar colour
        health_percentage = self.health/self.health_max
        try:
            if not self.force_colour:
                n=10
                t = 1/(1 + math.e**((n/2)-n*health_percentage)) #sigmoid modifier
                self.r, self.g = self.linearInterpolation2D((255,0), (0,255), t)
                self.canvas.itemconfigure("HEALTH_BAR_CURRENT"+self.tag, fill='#%02X%02X%02X' % (int(self.r), int(self.g), self.b))
            else:
                self.canvas.itemconfigure("HEALTH_BAR_CURRENT"+self.tag, fill='#%02X%02X%02X' % self.force_colour)
        
            self.current_health_x = ((self.health/self.health_max) * 2*self.healthbar_x) - self.healthbar_x
        except (AttributeError, TypeError):
            pass
        
    def go(self):
        #Creates and places image
        self.canvas.create_image(self.path[0][0], self.path[0][1], image=None, tag=("UNIT", self.tag), state="disabled")
        self.canvas.coords(self.tag, self.path[0])

        #Create and places health bar
        self.healthbar_x, self.healthbar_y= 0.15*self.sf, 0.025*self.sf
        self.current_health_x = self.healthbar_x
        self.canvas.create_rectangle(self.path[0][0]-self.healthbar_x, self.path[0][1]-self.healthbar_y-(0.25*self.sf), self.path[0][0]+self.healthbar_x, self.path[0][1]+self.healthbar_y-(0.25*self.sf), fill='#%02X%02X%02X' % (0,255,0), state="disabled", tag=("HEALTH_BAR_CURRENT"+self.tag, "HEALTH"+self.tag))
        
        self.active = True
        self.reduceHealth(0)

        #Iterates through path and animates image
        for i in range(1, len(self.path)):
            #Calculate distance to travel
            d = self.euclidDistance2D(self.path[i-1], self.path[i])/self.sf
            
            #If at base stop just before (1/3 away)
            if i == len(self.path)-1:
                d /= 3
                self.path[-1] = self.pyd.linearInterpolation2D(self.path[i-1], self.path[i], 1/3)

            #Update image to rotated image
            self.canvas.itemconfigure(self.tag, image=self.image[i-1])

            #Animation per frame
            for frame in range(self.fps):
                #Halt if unit needs to stop
                while self.stopped:
                    try:
                        self.canvas.coords("HEALTH_BAR_CURRENT"+self.tag, (x-self.healthbar_x, y-self.healthbar_y-(0.25*self.sf), x+self.current_health_x, y+self.healthbar_y-(0.25*self.sf)))
                    
                        #Check if unit dead
                        if self.health <= 0:
                            self.die()
                            return
                    except:
                        pass

                    time.sleep(d/(self.pyd.game_speed_mod*self.speed*self.fps))


                #Check if unit dead
                if self.health <= 0:
                    self.die()
                    return

                #Linearly interpolate new coords for frame
                x, y = self.linearInterpolation2D(self.path[i-1], self.path[i], (frame)/(self.fps))
                self.pos = (x,y)

                #Move health bar and image
                self.canvas.coords(self.tag, (x,y))
                self.canvas.coords("HEALTH_BAR_CURRENT"+self.tag, (x-self.healthbar_x, y-self.healthbar_y-(0.25*self.sf), x+self.current_health_x, y+self.healthbar_y-(0.25*self.sf)))

                #Sync movement with units speed and fps
                time.sleep(2*d/(self.pyd.game_speed_mod*self.speed*self.fps))

        #Base sequence
        while True:
            #Stop if halted
            while self.stopped:
                try:
                    self.canvas.coords("HEALTH_BAR_CURRENT"+self.tag, (x-self.healthbar_x, y-self.healthbar_y-(0.25*self.sf), x+self.current_health_x, y+self.healthbar_y-(0.25*self.sf)))
                except:
                    pass
                time.sleep(1/(self.pyd.game_speed_mod*self.fps))
                

            #Damage the base with unit strength
            self.damageBase((self.strength*self.pyd.game_speed_mod)/(self.fps))

            #Update healthbar
            self.canvas.coords("HEALTH_BAR_CURRENT"+self.tag, (x-self.healthbar_x, y-self.healthbar_y-(0.25*self.sf), x+self.current_health_x, y+self.healthbar_y-(0.25*self.sf)))

            #Break if unit dies
            if self.health <= 0:
                break

            #Damage per second limiter
            time.sleep(1/(self.pyd.game_speed_mod*self.fps))
        
        #Kill the unit
        self.die()

class Projectile():
    #Object for storing and executing projectile behaviour

    def __init__(self, _canvas, _image, _attributes, _tower, pyd, tag=None):
        #Helper
        self.pyd = pyd

        #Preset information from JSON/main app
        self.image = "textures/"+str(self.pyd.ACTIVE_TEXTURE)+"/towers/projectiles/"+_image

        self.damage = _attributes["damage"]
        self.speed = _attributes["speed"]
        self.splash_area = _attributes["splash_area"]
        self.lifetime = _attributes["lifetime"]
        self.mod_time = _attributes["mod_time"]
        self.speed_mod = _attributes["speed_mod"]
        self.damage_mod = _attributes["damage_mod"]
        self.value_mod = _attributes["value_mod"]

        self.tower = _tower
        self.target = None

        #Canvas/gameplay information
        self.DEATH_FRAME = self.pyd.GAME_IMAGE_DICT["PROJ_DEATH_FRAME"]

        self.canvas = _canvas
        self.tag = tag
        self.active_image_object = None
        self.fps = self.pyd.FPS
        self.sf = self.tower.sf
        self.projectile_limiter_max = 2
        self.pos = self.tower.pos

        #Imported methods
        self.euclidDistance2D = self.pyd.euclidDistance2D
        self.linearInterpolation2D = self.pyd.linearInterpolation2D
        self.calcAngle2D = self.pyd.calcAngle2D

    def setTarget(self, target):
        #Set target to unit object
        self.target = target

    #* Projectile gameplay methods
    def die(self, explosion_time=0):
        #Kills the projectile object and updates variables
        self.canvas.itemconfigure(self.tag, image=self.DEATH_FRAME)
        time.sleep(explosion_time)
        self.canvas.itemconfigure(self.tag, state="hidden")
        self.pos = self.tower.pos
        self.canvas.delete(str(self.tag))
        self.pyd.projectiles_active -= 1

    def go(self):
        #Checks number of projectiles saving/limiting canvas objects to a set max
        if self.pyd.projectiles_active >= self.pyd.MAX_PROJECTILES:
            self.target.reduceHealth(self.damage)
        else:
            self.pyd.projectiles_active += 1

            #Creates and places image
            self.canvas.create_image(self.pos[0], self.pos[1], image=None, tag=(self.tag), state="disabled")
            
            #Initialise animation variables
            start_time = time.time()
            current_lifetime = 0
            explosion_time = 0
            image_update_limiter_count = self.projectile_limiter_max

            while current_lifetime <= self.lifetime:
                #Halt projectile if paused
                while self.pyd.pause_toggle_state:
                    time.sleep(1/(self.pyd.game_speed_mod*self.fps*self.speed))

                current_lifetime = time.time() - start_time
                image_update_limiter_count += 1

                #Calculate distance to target
                distance_to_target = self.euclidDistance2D(self.pos, self.target.pos)

                #Collision detection
                if distance_to_target/self.sf <= self.splash_area/8:
                    self.target.reduceHealth(self.damage)
                    explosion_time = 0.25
                    break

                if self.target.active:
                    #Linearly interpolate new coords for frame
                    self.pos = self.linearInterpolation2D(self.pos, self.target.pos, 1/(max(1, distance_to_target)**0.5))

                    #Update limiter - prevents slowdowns on low-power PC's
                    if image_update_limiter_count >= self.projectile_limiter_max:
                        image_update_limiter_count = 0
                        self.active_image_object = self.pyd.image(self.image, theta=self.calcAngle2D(self.pos[0], self.pos[1], self.target.pos[0], self.target.pos[1]))
                        self.canvas.itemconfigure(self.tag, image=self.active_image_object)
                    
                    self.canvas.coords(self.tag, self.pos[0], self.pos[1])

                    #Sync movement with projectiles speed and fps
                    time.sleep(1/(self.pyd.game_speed_mod*self.fps*self.speed))
                else:
                    explosion_time = 0
                    break
        
            #Kill the projectile
            self.die(explosion_time)

class Tower():
    #Object that stores tower details

    def __init__(self, _canvas, _pos, _image, _attributes, sf, pyd, tag=None):
        #Helper
        self.pyd = pyd
        
        #Tower variable initialisation
        self.canvas = _canvas
        self.pos = _pos
        self.tag = tag
        self.sf = sf
        self.active = True

        self.rate_of_fire = _attributes["rate_of_fire"]
        self.cost = _attributes["cost"]
        self.range = _attributes["range"]
        self.min_range = _attributes["min_range"]
        self.projectile = _attributes["projectile"]
        self.image = _image

        #Special case for upgradable towers e.g. base tower
        try:
            self.current_image = self.image[0]#select first image
        except:
            self.current_image = self.image
            self.canvas.tag_bind(self.tag, "<Button-1>", self.sell)

        
        #Imported methods
        self.euclidDistance2D = self.pyd.euclidDistance2D
        self.linearInterpolation2D = self.pyd.linearInterpolation2D

        #Draw range preview
        if self.min_range > 0:
            self.canvas.create_oval(self.pos[0]-(self.min_range*self.sf), self.pos[1]-(self.min_range*self.sf), self.pos[0]+(self.min_range*self.sf), self.pos[1]+(self.min_range*self.sf), state="hidden", outline="#992020", width=3, tags="RANGE"+self.tag)
        
        self.canvas.create_oval(self.pos[0]-(self.range*self.sf), self.pos[1]-(self.range*self.sf), self.pos[0]+(self.range*self.sf), self.pos[1]+(self.range*self.sf), state="hidden", width=3, tags="RANGE"+self.tag)
        self.canvas.tag_bind(self.tag, "<Enter>", self.showDetails)
        self.canvas.tag_bind(self.tag, "<Leave>", self.hideDetails)

        #Draw tower image onto canvas
        self.canvas.create_image(self.pos, image=self.current_image, tags=self.tag)
        self.canvas.create_image(self.pos, image=self.pyd.GAME_IMAGE_DICT["TOWER_SELL_ICON"], state="hidden", tags=("SELL_ICON_"+self.tag, self.tag))

    #* Tower gameplay methods
    def hideDetails(self, event=""):
        #Hide all hover details
        self.canvas.itemconfigure("TOWER_RANGE_PREVIEW", state="hidden")
        self.canvas.itemconfigure("RANGE"+self.tag, state="hidden")
        self.canvas.itemconfigure("SELL_ICON_"+self.tag, state="hidden")

    def showDetails(self, event=""):
        #Show all hover details
        self.canvas.itemconfigure("TOWER_RANGE_PREVIEW", state="hidden")
        self.canvas.itemconfigure("RANGE"+self.tag, state="disabled")
        self.canvas.itemconfigure("SELL_ICON_"+self.tag, state="disabled")

    def sell(self, event=""):
        #Sell the tower, removing the object and restoring money to the user's balance
        self.canvas.delete(self.tag)
        self.active = False
        self.canvas.delete("RANGE"+self.tag)
        self.pyd.money += self.cost*0.9

    def go(self):
        #Activate the tower
        projectile_count = 0

        while not self.pyd.game_over and self.active:
            #Stop firing if game paused
            while self.pyd.pause_toggle_state:
                time.sleep(1/(self.pyd.game_speed_mod*self.rate_of_fire))
            
            #Find the nearest unit to target
            unit_distances = []
            for unit in self.pyd.wave:
                unit_dist = self.euclidDistance2D(unit.pos, self.pos)/self.sf
                if unit.active and unit_dist >= self.min_range and unit_dist <= self.range:
                    unit_distances.append([unit, unit_dist])
            sorted_units = sorted(unit_distances, key=lambda x: x[1])
            
            #Find shortest unit and check if the unit is active i.e not dead
            for unit_dist in unit_distances:
                if unit_dist[0].active:
                    if unit_dist == sorted_units[0]: #Closest unit

                        #Fire a projectile at the closest unit
                        projectile = Projectile(self.canvas, self.projectile["texture_name"], self.projectile, self, self.pyd, "PROJECTILE_"+self.tag+"_"+str(projectile_count))
                        projectile.setTarget(unit_dist[0])
                        thr.start_new_thread(projectile.go, ())

                        projectile_count += 1

            #Rate of fire limiter
            time.sleep(1/(self.pyd.game_speed_mod*self.rate_of_fire))
        
class BaseTower(Tower):
    #Object to store the base, inherits the Tower class

    def __init__(self, _canvas, _pos, _image, _attributes, sf, pyd, tag=None):
        #Inherit tower class
        super(BaseTower, self).__init__(_canvas, _pos, _image, _attributes, sf, pyd, tag)
        
        #Initialise additional variables
        self.level = 0
        self.money_level_requirements = [10000, 25000]

        #Create upgrade text and image
        self.canvas.create_image(self.pos, image=self.pyd.GAME_IMAGE_DICT["BASE_UPGRADE"], state="hidden", tags=("UPGRADE_BASE", "UPGRADE_BASE_ICON"))
        self.canvas.create_text(self.pos, text="", state="hidden", font=(self.pyd.default_font, self.pyd.fontScale(12)), fill="white", tags=("UPGRADE_BASE", "UPGRADE_BASE_TEXT"))
        self.updateImage()
        self.canvas.tag_bind(self.tag, "<Button-1>", self.levelUp)

    #* Base tower gameplay methods
    def updateImage(self):
        #Update base image if base upgraded
        self.current_image = self.image[self.level]
        self.canvas.itemconfigure(self.tag, image=self.current_image)
        self.canvas.coords("RANGE"+self.tag, self.pos[0]-(self.range*self.sf), self.pos[1]-(self.range*self.sf), self.pos[0]+(self.range*self.sf), self.pos[1]+(self.range*self.sf))

    def levelUp(self, event=""):
        #Level up the base and update tower variables
        if len(self.image)-1 >= self.level+1: #Check that level isn't greater than the number of images
            if self.pyd.money >= self.money_level_requirements[self.level]: #Check user has enough money

                #Reduce money and update level
                self.pyd.money -= self.money_level_requirements[self.level]
                self.level += 1
                self.level = min(len(self.image)-1, self.level)

                #Update base statistics
                self.range *= 1.25
                self.projectile["damage"] *= 1.5
                self.rate_of_fire *= 1.5
                self.pyd.current_base_health += self.pyd.max_base_health
                self.pyd.max_base_health *= 2

                #Update base image
                self.updateImage()
