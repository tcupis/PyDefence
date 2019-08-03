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
    import _thread as thr

    from tkinter import filedialog, messagebox

    from data.pydefence import Unit, Tower, BaseTower, PyDefence
    import data.client as client
except:
    #Writing logs if import fails
    temp_file = open("FATAL-GAME-LAUNCH-{}.txt".format(random.randint(0,10**10)), 'w')
    temp_file.write("A fatal launch error occurred, ensure you have the required packages\n\nGet required packages:\n\t-_thread\n\t-tkinter\n\t-base64\n\t-pillow\n\t-pydefence (within /data/)")
    temp_file.close()

    quit()


class App:
    # App class will contain the application


    def __init__(self):
        #* Window config
        #Helper file
        self.pyd = PyDefence()

        #Create GUI root
        self.root = tk.Tk()

        #* Window geometry config
        #Get screen resolution
        if self.pyd.FULLSCREEN:
            self.root.attributes("-fullscreen", True)
            SCREEN_WIDTH = self.root.winfo_screenwidth()
            SCREEN_HEIGHT = self.root.winfo_screenheight()

            self.pyd.RESOLUTION = [self.root.winfo_screenwidth(), self.root.winfo_screenheight()]
            
        else:
            SCREEN_WIDTH = self.pyd.RESOLUTION[0]
            SCREEN_HEIGHT = self.pyd.RESOLUTION[1]

        self.prev_resolution = self.pyd.RESOLUTION

        self.root.geometry("{}x{}+{}+{}".format(SCREEN_WIDTH, SCREEN_HEIGHT, abs(self.root.winfo_screenwidth()-SCREEN_WIDTH)//2, abs(self.root.winfo_screenheight()-SCREEN_HEIGHT)//2))

        #Calculate the max width/height for 16:9
        self.pyd.calcFrameSize(self.pyd.MAIN_FRAME_WIDTH_RATIO, self.pyd.MAIN_FRAME_HEIGHT_RATIO, SCREEN_WIDTH, SCREEN_HEIGHT)

        self.pyd.log("screen ({},{})".format(SCREEN_WIDTH, SCREEN_HEIGHT))
        self.pyd.log("adjusted ({},{})".format(self.pyd.calc_width, self.pyd.calc_height))

        
        #Config window settings
        self.root.configure(background='black')
        self.root.title("PyDefence")

        #Try to load window icon
        try:
            self.root.iconbitmap("textures/pydefence.ico")
        except:
            self.pyd.log("Window icon failed to load")

        #Bind alt-f4 to close function
        self.root.protocol("WM_DELETE_WINDOW", self.quitProgram)
        

        #* Scale initial screen images
        #Scales images in advance
        self.pyd.loadInitialImages(self.pyd.calc_width, self.pyd.calc_height)

        #Set the cursor
        try:
            self.root.configure(cursor=self.pyd.CURSOR)
        except:
            pass

        #Create a main frame at the max size for 16:9
        self.main_area = tk.Frame(self.root, width=self.pyd.calc_width, height=self.pyd.calc_height)
        self.main_area.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.overseeing = False

        #Start client
        self.client = client.GameServerInterface((self.pyd.DS_ADDRESS, 1000))
        thr.start_new_thread(self.client.start, ())

        #* Launch title screen
        self.titleScreen()

    #* Title screen
    def titleScreen(self):
        #Update DRP status
        self.pyd.updateDRP(state="On the title screen", detail="Playing PyDefence")

        #* Title screen UI
        #Create a frame for the title screen
        self.title_area = tk.Frame(self.main_area, width=self.pyd.calc_width, height=self.pyd.calc_height)
        self.title_area.pack()

        #Create the canvas for image placement
        self.title_canvas = tk.Canvas(self.title_area, width=self.pyd.calc_width, height=self.pyd.calc_height, highlightthickness=0)
        self.title_canvas.place(relx=0, rely=0)

        #Place the background image on the canvas
        self.title_canvas.create_image(self.pyd.calc_width//2,self.pyd.calc_height//2, image=self.pyd.BG_IMG, tag="BG_IMG")

        #* Main panel
        #All initial buttons and images with bindings
        main_panel_x = self.pyd.calc_width//6

        self.title_canvas.create_image(main_panel_x, self.pyd.calc_height//2, image=self.pyd.BUTTON_POLE, tag=("MAIN_PANEL", "BUTTON_POLE"))

        self.title_canvas.create_image(main_panel_x, (1*self.pyd.calc_height)//9, image=self.pyd.TITLE_PANEL, tag=("MAIN_PANEL", "TITLE_PANEL"))
        self.title_canvas.tag_bind('TITLE_PANEL', '<ButtonPress-1>', self.displayDefault)

        self.title_canvas.create_image(main_panel_x, (3.5*self.pyd.calc_height)//9, image=self.pyd.PLAY_BUTTON, tag=("MAIN_PANEL", "PLAY_BUTTON"))
        self.title_canvas.tag_bind('PLAY_BUTTON', '<ButtonPress-1>', self.displayGamemodes)

        self.title_canvas.create_image(main_panel_x, (5.4*self.pyd.calc_height)//9, image=self.pyd.SETTINGS_BUTTON, tag=("MAIN_PANEL", "SETTINGS_BUTTON"))
        self.title_canvas.tag_bind('SETTINGS_BUTTON', '<ButtonPress-1>', lambda x: self.displayContentPanel("SETTINGS_PANEL", x))

        self.title_canvas.create_image(main_panel_x, (6.7*self.pyd.calc_height)//9, image=self.pyd.HELP_BUTTON, tag=("MAIN_PANEL", "HELP_BUTTON"))
        self.title_canvas.tag_bind('HELP_BUTTON', '<ButtonPress-1>', lambda x: self.displayContentPanel("HELP_PANEL", x))

        self.title_canvas.create_image(main_panel_x, (8*self.pyd.calc_height)//9, image=self.pyd.QUIT_BUTTON, tag=("MAIN_PANEL", "QUIT_BUTTON"))
        self.title_canvas.tag_bind('QUIT_BUTTON', '<ButtonPress-1>', self.quitProgram)


        #Gamemode panel
        gamemode_panel_x = (self.pyd.calc_width*3)//6

        self.title_canvas.create_image(gamemode_panel_x, self.pyd.calc_height//2, image=self.pyd.BUTTON_POLE, tag=("GAMEMODE_PANEL", "BUTTON_POLE"))

        self.title_canvas.create_image(gamemode_panel_x, (1.75*self.pyd.calc_height)//9, image=self.pyd.EASY_BUTTON, tag=("GAMEMODE_PANEL", "EASY_BUTTON"))
        self.title_canvas.tag_bind('EASY_BUTTON', '<ButtonPress-1>', lambda x: self.displayGMDetails("EASY_PANEL", x))

        self.title_canvas.create_image(gamemode_panel_x, (3.5*self.pyd.calc_height)//9, image=self.pyd.NORMAL_BUTTON, tag=("GAMEMODE_PANEL", "NORMAL_BUTTON"))
        self.title_canvas.tag_bind('NORMAL_BUTTON', '<ButtonPress-1>', lambda x: self.displayGMDetails("NORMAL_PANEL", x))

        self.title_canvas.create_image(gamemode_panel_x, (5.25*self.pyd.calc_height)//9, image=self.pyd.HARD_BUTTON, tag=("GAMEMODE_PANEL", "HARD_BUTTON"))
        self.title_canvas.tag_bind('HARD_BUTTON', '<ButtonPress-1>', lambda x: self.displayGMDetails("HARD_PANEL", x))

        self.title_canvas.create_image(gamemode_panel_x, (7.25*self.pyd.calc_height)//9, image=self.pyd.MULTIPLAYER_BUTTON, tag=("GAMEMODE_PANEL", "MULTIPLAYER_BUTTON"))
        self.title_canvas.tag_bind('MULTIPLAYER_BUTTON', '<ButtonPress-1>', lambda x: self.displayGMDetails("MULTIPLAYER_PANEL", x))


        #GM details panel
        gm_details_panel_x = (self.pyd.calc_width*5)//6
        gm_details_panel_centre_x = (self.pyd.calc_width*55)//64
        badge_position_x = (self.pyd.calc_width*5.6)//6
        badge_position_y = (self.pyd.calc_height)//6

        #Easy panel
        easy_text = "The easy game mode is a gentle introduction to tower defence.\nBuild your skills to take on a limited number of a waves without being too challenging!"
        self.title_canvas.create_image(gm_details_panel_x, self.pyd.calc_height//2, image=self.pyd.EASY_PANEL, tag=("GM_DETAILS_PANEL", "EASY_PANEL"))
        self.title_canvas.create_image(badge_position_x, badge_position_y, image=self.checkBadge("EASY"), tag=("GM_DETAILS_PANEL", "EASY_PANEL", "EASY_BADGE"))
        self.title_canvas.create_text(gm_details_panel_centre_x, (self.pyd.calc_height*17)//36, font=(self.pyd.default_font, self.pyd.fontScale(18)), justify="center", fill="white", text=easy_text, width=(self.pyd.calc_width*7)//32, tag=("GM_DETAILS_PANEL", "EASY_PANEL"))

        self.title_canvas.create_text(gm_details_panel_centre_x, (self.pyd.calc_height*22)//36, font=(self.pyd.default_font, self.pyd.fontScale(24)), justify="center", fill="white", text=str(self.pyd.EASY_NO_ROUNDS), tag=("GM_DETAILS_PANEL", "EASY_PANEL"))
        self.title_canvas.create_text(gm_details_panel_centre_x*0.99, (self.pyd.calc_height*24)//36, font=(self.pyd.default_font, self.pyd.fontScale(24)), justify="center", fill="white", text=str(self.pyd.EASY_START_MONEY), tag=("GM_DETAILS_PANEL", "EASY_PANEL"))
        self.title_canvas.create_text(gm_details_panel_centre_x, (self.pyd.calc_height*26)//36, font=(self.pyd.default_font, self.pyd.fontScale(24)), justify="center", fill="white", text=str(self.pyd.EASY_BASE_HEALTH), tag=("GM_DETAILS_PANEL", "EASY_PANEL"))

        #Normal panel
        normal_text = "The normal game mode is for players looking for standard play.\nRefine your skills taking on a number of a waves that are more challenging!"
        self.title_canvas.create_image(gm_details_panel_x, self.pyd.calc_height//2, image=self.pyd.NORMAL_PANEL, tag=("GM_DETAILS_PANEL", "NORMAL_PANEL"))
        self.title_canvas.create_image(badge_position_x, badge_position_y, image=self.checkBadge("NORMAL"), tag=("GM_DETAILS_PANEL", "NORMAL_PANEL", "NORMAL_BADGE"))
        self.title_canvas.create_text(gm_details_panel_centre_x, (self.pyd.calc_height*17)//36, font=(self.pyd.default_font, self.pyd.fontScale(18)), justify="center", fill="white", text=normal_text, width=(self.pyd.calc_width*7)//32, tag=("GM_DETAILS_PANEL", "NORMAL_PANEL"))

        self.title_canvas.create_text(gm_details_panel_centre_x, (self.pyd.calc_height*22)//36, font=(self.pyd.default_font, self.pyd.fontScale(24)), justify="center", fill="white", text=str(self.pyd.NORMAL_NO_ROUNDS), tag=("GM_DETAILS_PANEL", "NORMAL_PANEL"))
        self.title_canvas.create_text(gm_details_panel_centre_x*0.99, (self.pyd.calc_height*24)//36, font=(self.pyd.default_font, self.pyd.fontScale(24)), justify="center", fill="white", text=str(self.pyd.NORMAL_START_MONEY), tag=("GM_DETAILS_PANEL", "NORMAL_PANEL"))
        self.title_canvas.create_text(gm_details_panel_centre_x, (self.pyd.calc_height*26)//36, font=(self.pyd.default_font, self.pyd.fontScale(24)), justify="center", fill="white", text=str(self.pyd.NORMAL_BASE_HEALTH), tag=("GM_DETAILS_PANEL", "NORMAL_PANEL"))

        #Hard panel
        hard_text = "The hard game mode is for players looking for advanced play.\nTest your skills with very challenging waves, only the best win!"
        self.title_canvas.create_image(gm_details_panel_x, self.pyd.calc_height//2, image=self.pyd.HARD_PANEL, tag=("GM_DETAILS_PANEL", "HARD_PANEL"))
        self.title_canvas.create_image(badge_position_x, badge_position_y, image=self.checkBadge("HARD"), tag=("GM_DETAILS_PANEL", "HARD_PANEL", "HARD_BADGE"))
        self.title_canvas.create_text(gm_details_panel_centre_x, (self.pyd.calc_height*16)//36, font=(self.pyd.default_font, self.pyd.fontScale(16)), justify="center", fill="white", text=hard_text, width=(self.pyd.calc_width*7)//32, tag=("GM_DETAILS_PANEL", "HARD_PANEL"))

        #Crazy mode
        self.title_canvas.create_text(gm_details_panel_centre_x*0.975, (self.pyd.calc_height*19.5)//36, font=(self.pyd.default_font, self.pyd.fontScale(18)), justify="center", fill="white", text="Crazy hard?", tag=("GM_DETAILS_PANEL", "HARD_PANEL", "CRAZY_TEXT"))
        self.title_canvas.create_image(gm_details_panel_centre_x*1.04, (self.pyd.calc_height*19.5)//36, image=self.pyd.CHECKBOX_BLANK, tag=("GM_DETAILS_PANEL", "HARD_PANEL", "CRAZY_TOGGLE"))
        self.title_canvas.tag_bind('CRAZY_TOGGLE', '<ButtonPress-1>', self.toggleCrazy)
        self.title_canvas.tag_bind('CRAZY_TEXT', '<ButtonPress-1>', self.toggleCrazy)

        self.title_canvas.create_text(gm_details_panel_centre_x, (self.pyd.calc_height*22)//36, font=(self.pyd.default_font, self.pyd.fontScale(24)), justify="center", fill="white", text=str(self.pyd.HARD_NO_ROUNDS), tag=("GM_DETAILS_PANEL", "HARD_PANEL", "HARD_ROUNDS"))
        self.title_canvas.create_text(gm_details_panel_centre_x*0.99, (self.pyd.calc_height*24)//36, font=(self.pyd.default_font, self.pyd.fontScale(24)), justify="center", fill="white", text=str(self.pyd.HARD_START_MONEY), tag=("GM_DETAILS_PANEL", "HARD_PANEL", "HARD_MONEY"))
        self.title_canvas.create_text(gm_details_panel_centre_x, (self.pyd.calc_height*26)//36, font=(self.pyd.default_font, self.pyd.fontScale(24)), justify="center", fill="white", text=str(self.pyd.HARD_BASE_HEALTH), tag=("GM_DETAILS_PANEL", "HARD_PANEL", "HARD_HEALTH"))

        #Multiplayer panel
        self.title_canvas.create_image(gm_details_panel_x, self.pyd.calc_height//2, image=self.pyd.MULTIPLAYER_PANEL, tag=("GM_DETAILS_PANEL", "MULTIPLAYER_PANEL"))

        self.title_canvas.create_text((self.pyd.calc_width*53)//64, (self.pyd.calc_height*14.5)//36, font=(self.pyd.default_font, self.pyd.fontScale(12)), justify="center", fill="white", text="Status:",  tag=("GM_DETAILS_PANEL", "MULTIPLAYER_PANEL"))
        self.title_canvas.create_text((self.pyd.calc_width*57)//64, (self.pyd.calc_height*14.5)//36, font=(self.pyd.default_font, self.pyd.fontScale(12)), justify="center", fill="white", text="Not connected",  tag=("GM_DETAILS_PANEL", "MULTIPLAYER_PANEL", "SERVER_STATUS", "SERVER_STATUS_COL"))
        self.title_canvas.create_image(gm_details_panel_centre_x, (self.pyd.calc_height*17)//36, image=self.pyd.MULTIPLAYER_JOIN, tag=("GM_DETAILS_PANEL", "MULTIPLAYER_PANEL", "MULTIPLAYER_TOGGLE"))
        self.title_canvas.tag_bind('MULTIPLAYER_TOGGLE', '<ButtonPress-1>', self.toggleMultiplayer)

        self.title_canvas.create_text(gm_details_panel_centre_x, (self.pyd.calc_height*21)//36, font=(self.pyd.default_font, self.pyd.fontScale(18)), justify="center", fill="red", text="No lobbies online...", tag=("GM_DETAILS_PANEL", "MULTIPLAYER_PANEL", "MULTIPLAYER_JOIN"))
        
        
        #Creating a lobby
        #Lobby name
        self.lobby_name = tk.StringVar(self.root)
        self.lobby_name.set("")
        self.lobby_name_entry = tk.Entry(self.root, font=(self.pyd.default_font, self.pyd.fontScale(14)), textvariable=self.lobby_name, bg="lightgrey")
        self.lobby_name_entry.pack(expand=1, fill=tk.BOTH)

        self.title_canvas.create_text(gm_details_panel_centre_x, (self.pyd.calc_height*20)//36, text="Lobby name", fill="white", font=(self.pyd.default_font, self.pyd.fontScale(16)), tag=("GM_DETAILS_PANEL", "MULTIPLAYER_PANEL", "MULTIPLAYER_CREATE"))
        self.title_canvas.create_window(gm_details_panel_centre_x, (self.pyd.calc_height*21.5)//36, window=self.lobby_name_entry, tag=("GM_DETAILS_PANEL", "MULTIPLAYER_PANEL", "MULTIPLAYER_CREATE"))

        #Difficulty slider
        self.lobby_difficulty = tk.DoubleVar(self.root)
        self.lobby_difficulty.set(2)
        self.lobby_difficulty_entry = tk.Scale(self.root, variable=self.lobby_difficulty, from_=1, to=5, resolution=0.1, orient=tk.HORIZONTAL, showvalue=True, bg="white")
        self.lobby_difficulty_entry.pack(expand=1, fill=tk.BOTH)

        self.title_canvas.create_text(gm_details_panel_centre_x, (self.pyd.calc_height*23)//36, text="Game difficulty", fill="white", font=(self.pyd.default_font, self.pyd.fontScale(16)), tag=("GM_DETAILS_PANEL", "MULTIPLAYER_PANEL", "MULTIPLAYER_CREATE"))
        self.title_canvas.create_window(gm_details_panel_centre_x, (self.pyd.calc_height*25)//36, window=self.lobby_difficulty_entry, tag=("GM_DETAILS_PANEL", "MULTIPLAYER_PANEL", "MULTIPLAYER_CREATE"))


        #Gamemode persistant details
        self.title_canvas.create_image((self.pyd.calc_width*52)//64, (self.pyd.calc_height*10.5)//36, image=self.pyd.thumbnail_image, tag=("GM_DETAILS_PANEL", "GM_SETTINGS", "MAP_THUMBNAIL"))
        self.title_canvas.create_image((self.pyd.calc_width*52)//64, (self.pyd.calc_height*10.5)//36, image=self.pyd.MAP_OVERLAY, tag=("GM_DETAILS_PANEL", "GM_SETTINGS", "MAP_OVERLAY"))
        self.title_canvas.tag_bind('MAP_OVERLAY', '<ButtonPress-1>', self.openMap)

        self.title_canvas.create_image((self.pyd.calc_width*59)//64, (self.pyd.calc_height*12)//36, image=self.pyd.OPEN_BUTTON, tag=("GM_DETAILS_PANEL", "GM_SETTINGS", "OPEN_BUTTON"))
        self.title_canvas.tag_bind('OPEN_BUTTON', '<ButtonPress-1>', self.openMap)

        self.title_canvas.create_text((self.pyd.calc_width*57)//64, (self.pyd.calc_height*8.5)//36, text="Map:", font=(self.pyd.default_font, self.pyd.fontScale(16)), fill="white", tag=("GM_DETAILS_PANEL", "GM_SETTINGS"))
        self.title_canvas.create_text((self.pyd.calc_width*59)//64, (self.pyd.calc_height*9.5)//36, text="Select a map...", font=(self.pyd.default_font, self.pyd.fontScale(12)), fill="white", tag=("GM_DETAILS_PANEL", "GM_SETTINGS", "MAP_NAME"))

        self.title_canvas.create_text(gm_details_panel_centre_x, (self.pyd.calc_height*21)//36, font=(self.pyd.default_font, self.pyd.fontScale(14)), justify="center", fill="white", text="Number of waves:", tag=("GM_DETAILS_PANEL", "GM_INFO"))
        self.title_canvas.create_text(gm_details_panel_centre_x, (self.pyd.calc_height*23)//36, font=(self.pyd.default_font, self.pyd.fontScale(14)), justify="center", fill="white", text="Starting money:", tag=("GM_DETAILS_PANEL", "GM_INFO"))
        self.title_canvas.create_image(gm_details_panel_centre_x*1.025, (self.pyd.calc_height*24)//36, image=self.pyd.MONEY_ICON, tag=("GM_DETAILS_PANEL", "GM_INFO"))
        self.title_canvas.create_text(gm_details_panel_centre_x, (self.pyd.calc_height*25)//36, font=(self.pyd.default_font, self.pyd.fontScale(14)), justify="center", fill="white", text="Base health:", tag=("GM_DETAILS_PANEL", "GM_INFO"))

        self.title_canvas.create_image(gm_details_panel_centre_x, self.pyd.calc_height//1.2, image=self.pyd.LAUNCH_BUTTON, tag=("GM_DETAILS_PANEL", "GM_SETTINGS", "LAUNCH_BUTTON"))
        self.title_canvas.tag_bind('LAUNCH_BUTTON', '<ButtonPress-1>', self.launchGame)


        #*Content panels
        content_panel_x = (self.pyd.calc_width*2)//3

        #Settings panel
        self.title_canvas.create_image(content_panel_x, self.pyd.calc_height//2, image=self.pyd.SETTINGS_PANEL, tag=("CONTENT_PANEL", "SETTINGS_PANEL"))


        #Resolution selection
        self.title_canvas.create_text((self.pyd.calc_width*30)//64, (self.pyd.calc_height*9)//36, text="Display", fill="white", font=(self.pyd.default_font, self.pyd.fontScale(32)), tag=("CONTENT_PANEL", "SETTINGS_PANEL"))
        
        try:
            self.resolution_ptr = self.pyd.WINDOW_RESOLUTIONS.index(self.pyd.RESOLUTION)
        except ValueError:
            self.resolution_ptr = 0

        self.title_canvas.create_text((self.pyd.calc_width*34)//64, (self.pyd.calc_height*11)//36, text="Screen resolution", fill="white", font=(self.pyd.default_font, self.pyd.fontScale(24)), tag=("CONTENT_PANEL", "SETTINGS_PANEL"))
        self.title_canvas.create_text((self.pyd.calc_width*34)//64, (self.pyd.calc_height*13)//36, text="{}x{}".format(self.pyd.RESOLUTION[0], self.pyd.RESOLUTION[1]), fill="white", font=(self.pyd.default_font, self.pyd.fontScale(20)), tag=("CONTENT_PANEL", "SETTINGS_PANEL", "RESOLUTION"))
        self.title_canvas.create_image((self.pyd.calc_width*32.5)//64, (self.pyd.calc_height*15.5)//36, image=self.pyd.PREV_BUTTON, tag=("CONTENT_PANEL", "SETTINGS_PANEL", "PREV_RESOLUTION"))
        self.title_canvas.create_image((self.pyd.calc_width*35.5)//64, (self.pyd.calc_height*15.5)//36, image=self.pyd.NEXT_BUTTON, tag=("CONTENT_PANEL", "SETTINGS_PANEL", "NEXT_RESOLUTION"))
        self.title_canvas.tag_bind("PREV_RESOLUTION", "<Button-1>", self.prevResolution)
        self.title_canvas.tag_bind("NEXT_RESOLUTION", "<Button-1>", self.nextResolution)

        #Fullscreen selection
        self.fullscreen_toggle = self.pyd.FULLSCREEN
        self.title_canvas.create_text((self.pyd.calc_width*33)//64, (self.pyd.calc_height*18)//36, text="Fullscreen", fill="white", font=(self.pyd.default_font, self.pyd.fontScale(22)), tag=("CONTENT_PANEL", "SETTINGS_PANEL"))
        self.title_canvas.create_image((self.pyd.calc_width*37)//64, (self.pyd.calc_height*18)//36, image=self.pyd.CHECKBOX_BLANK, tag=("CONTENT_PANEL", "SETTINGS_PANEL", "FULLSCREEN_CHECKBOX"))
        self.title_canvas.tag_bind("FULLSCREEN_CHECKBOX", "<Button-1>", self.toggleFullscreen)

        if self.fullscreen_toggle:
            self.title_canvas.itemconfigure("FULLSCREEN_CHECKBOX", image=self.pyd.FULLSCREEN_ON)
        else:
            self.title_canvas.itemconfigure("FULLSCREEN_CHECKBOX", image=self.pyd.CHECKBOX_BLANK)


        #Multiplayer settings
        self.title_canvas.create_text((self.pyd.calc_width*31)//64, (self.pyd.calc_height*21)//36, text="Multiplayer", fill="white", font=(self.pyd.default_font, self.pyd.fontScale(32)), tag=("CONTENT_PANEL", "SETTINGS_PANEL"))
        
        #Client name
        self.client_name = tk.StringVar(self.root)
        self.client_name.set(self.pyd.CLIENT_NAME)
        self.client_name_entry = tk.Entry(self.root, font=(self.pyd.default_font, self.pyd.fontScale(20)), textvariable=self.client_name, bg="lightgrey")
        self.client_name_entry.pack(expand=1, fill=tk.BOTH)

        self.title_canvas.create_text((self.pyd.calc_width*34)//64, (self.pyd.calc_height*23)//36, text="Client name", fill="white", font=(self.pyd.default_font, self.pyd.fontScale(22)), tag=("CONTENT_PANEL", "SETTINGS_PANEL"))
        self.title_canvas.create_window((self.pyd.calc_width*34)//64, (self.pyd.calc_height*25)//36, window=self.client_name_entry, tag=("CONTENT_PANEL", "SETTINGS_PANEL"))


        #Game server address info
        self.title_canvas.create_text((self.pyd.calc_width*34)//64, (self.pyd.calc_height*27)//36, text="Server address", fill="white", font=(self.pyd.default_font, self.pyd.fontScale(22)), tag=("CONTENT_PANEL", "SETTINGS_PANEL"))
        self.title_canvas.create_text((self.pyd.calc_width*34)//64, (self.pyd.calc_height*28.5)//36, text="'{}'".format(self.pyd.DS_ADDRESS), fill="white", font=(self.pyd.default_font, self.pyd.fontScale(20)), tag=("CONTENT_PANEL", "SETTINGS_PANEL", "SERVER_STATUS_COL"))
        self.title_canvas.create_text((self.pyd.calc_width*34)//64, (self.pyd.calc_height*29.25)//36, text="", fill="white", font=(self.pyd.default_font, self.pyd.fontScale(12)), tag=("CONTENT_PANEL", "SETTINGS_PANEL", "SERVER_STATUS", "SERVER_STATUS_COL"))
        self.title_canvas.create_text((self.pyd.calc_width*34)//64, (self.pyd.calc_height*30.5)//36, text="You can change this by editing the 'settings.json' file directly", fill="white", font=(self.pyd.default_font, self.pyd.fontScale(10)), tag=("CONTENT_PANEL", "SETTINGS_PANEL"))
        

        #Texture selection
        self.title_canvas.create_text((self.pyd.calc_width*50)//64, (self.pyd.calc_height*9)//36, text="Textures", fill="white", font=(self.pyd.default_font, self.pyd.fontScale(32)), tag=("CONTENT_PANEL", "SETTINGS_PANEL"))
        
        try:
            self.texture_ptr = self.pyd.TEXTURE_PACKS.index(self.pyd.ACTIVE_TEXTURE)
        except ValueError:
            self.resetToDefaults()
            self.saveSettings()

        self.title_canvas.create_text((self.pyd.calc_width*54)//64, (self.pyd.calc_height*11)//36, text="Texture pack", fill="white", font=(self.pyd.default_font, self.pyd.fontScale(24)), tag=("CONTENT_PANEL", "SETTINGS_PANEL"))
        self.title_canvas.create_text((self.pyd.calc_width*54)//64, (self.pyd.calc_height*13)//36, text=str(self.pyd.ACTIVE_TEXTURE), fill="white", font=(self.pyd.default_font, self.pyd.fontScale(20)), tag=("CONTENT_PANEL", "SETTINGS_PANEL", "ACTIVE_TEXTURE"))
        self.title_canvas.create_image((self.pyd.calc_width*52.5)//64, (self.pyd.calc_height*15.5)//36, image=self.pyd.PREV_BUTTON, tag=("CONTENT_PANEL", "SETTINGS_PANEL", "PREV_TEXTURE"))
        self.title_canvas.create_image((self.pyd.calc_width*55.5)//64, (self.pyd.calc_height*15.5)//36, image=self.pyd.NEXT_BUTTON, tag=("CONTENT_PANEL", "SETTINGS_PANEL", "NEXT_TEXTURE"))
        self.title_canvas.tag_bind("PREV_TEXTURE", "<Button-1>", self.prevTexture)
        self.title_canvas.tag_bind("NEXT_TEXTURE", "<Button-1>", self.nextTexture)


        #Other
        self.title_canvas.create_text((self.pyd.calc_width*49)//64, (self.pyd.calc_height*19)//36, text="Other", fill="white", font=(self.pyd.default_font, self.pyd.fontScale(32)), tag=("CONTENT_PANEL", "SETTINGS_PANEL"))
        
        #DRP toggle
        self.drp_toggle = self.pyd.DRP_ENABLED
        self.title_canvas.create_text((self.pyd.calc_width*53)//64, (self.pyd.calc_height*21)//36, text="Discord Rich Presence", fill="white", font=(self.pyd.default_font, self.pyd.fontScale(20)), tag=("CONTENT_PANEL", "SETTINGS_PANEL"))
        self.title_canvas.create_image((self.pyd.calc_width*59)//64, (self.pyd.calc_height*21)//36, image=self.pyd.CHECKBOX_BLANK, tag=("CONTENT_PANEL", "SETTINGS_PANEL", "DRP_CHECKBOX"))
        self.title_canvas.tag_bind("DRP_CHECKBOX", "<Button-1>", self.toggleDRP)
        if self.drp_toggle:
            self.title_canvas.itemconfigure("DRP_CHECKBOX", image=self.pyd.DRP_ON)
        else:
            self.title_canvas.itemconfigure("DRP_CHECKBOX", image=self.pyd.CHECKBOX_BLANK)

        #Debug toggle
        self.debug_toggle = self.pyd.DEBUG
        self.title_canvas.create_text((self.pyd.calc_width*53)//64, (self.pyd.calc_height*23)//36, text="Debug mode", fill="white", font=(self.pyd.default_font, self.pyd.fontScale(20)), tag=("CONTENT_PANEL", "SETTINGS_PANEL"))
        self.title_canvas.create_image((self.pyd.calc_width*59)//64, (self.pyd.calc_height*23)//36, image=self.pyd.CHECKBOX_BLANK, tag=("CONTENT_PANEL", "SETTINGS_PANEL", "DEBUG_CHECKBOX"))
        self.title_canvas.tag_bind("DEBUG_CHECKBOX", "<Button-1>", self.toggleDebug)
        if self.debug_toggle:
            self.title_canvas.itemconfigure("DEBUG_CHECKBOX", image=self.pyd.DEBUG_ON)
        else:
            self.title_canvas.itemconfigure("DEBUG_CHECKBOX", image=self.pyd.CHECKBOX_BLANK)

        
        #Save/reset
        self.title_canvas.create_image((self.pyd.calc_width*50)//64, (self.pyd.calc_height*30)//36, image=self.pyd.RESET_BUTTON, tag=("CONTENT_PANEL", "SETTINGS_PANEL", "RESET_BUTTON"))
        self.title_canvas.tag_bind("RESET_BUTTON", "<Button-1>", self.resetToDefaults)
        
        self.title_canvas.create_image((self.pyd.calc_width*58)//64, (self.pyd.calc_height*30)//36, image=self.pyd.SAVE_BUTTON, tag=("CONTENT_PANEL", "SETTINGS_PANEL", "SAVE_BUTTON"))
        self.title_canvas.tag_bind("SAVE_BUTTON", "<Button-1>", self.saveSettings)

        
        

        #Help panel
        self.title_canvas.create_image(content_panel_x, self.pyd.calc_height//2, image=self.pyd.HELP_PANEL, tag=("CONTENT_PANEL", "HELP_PANEL"))

        #Help column 1
        help_text_0 = self.pyd.HELP_TEXT["0"]
        help_text_1 = self.pyd.HELP_TEXT["1"]
        help_text_2 = self.pyd.HELP_TEXT["2"]

        self.title_canvas.create_text(content_panel_x-(self.pyd.calc_width)//16, (self.pyd.calc_height*2.75)//9, font=(self.pyd.default_font, self.pyd.fontScale(18)), justify="center", width=(self.pyd.calc_width*5)//32, fill="white", text=help_text_0, tag=("CONTENT_PANEL", "HELP_PANEL"))
        self.title_canvas.create_image(content_panel_x-(self.pyd.calc_width*3.25)//16, (self.pyd.calc_height*2.75)//9, image=self.pyd.HELP_IMAGE_0, tag=("CONTENT_PANEL", "HELP_PANEL"))

        self.title_canvas.create_text(content_panel_x-(self.pyd.calc_width)//16, (self.pyd.calc_height*4.75)//9, font=(self.pyd.default_font, self.pyd.fontScale(18)), justify="center", width=(self.pyd.calc_width*5)//32, fill="white", text=help_text_1, tag=("CONTENT_PANEL", "HELP_PANEL"))
        self.title_canvas.create_image(content_panel_x-(self.pyd.calc_width*3.25)//16, (self.pyd.calc_height*4.75)//9, image=self.pyd.HELP_IMAGE_1, tag=("CONTENT_PANEL", "HELP_PANEL"))

        self.title_canvas.create_text(content_panel_x-(self.pyd.calc_width)//16, (self.pyd.calc_height*6.75)//9, font=(self.pyd.default_font, self.pyd.fontScale(18)), justify="center", width=(self.pyd.calc_width*5)//32, fill="white", text=help_text_2, tag=("CONTENT_PANEL", "HELP_PANEL"))
        self.title_canvas.create_image(content_panel_x-(self.pyd.calc_width*3.25)//16, (self.pyd.calc_height*6.75)//9, image=self.pyd.HELP_IMAGE_2, tag=("CONTENT_PANEL", "HELP_PANEL"))

        #Help column 2
        help_text_3 = self.pyd.HELP_TEXT["3"]
        help_text_4 = self.pyd.HELP_TEXT["4"]
        help_text_5 = self.pyd.HELP_TEXT["5"]

        self.title_canvas.create_text(content_panel_x+(self.pyd.calc_width*3.75)//16, (self.pyd.calc_height*2.75)//9, font=(self.pyd.default_font, self.pyd.fontScale(18)), justify="center", width=(self.pyd.calc_width*5)//32, fill="white", text=help_text_3, tag=("CONTENT_PANEL", "HELP_PANEL"))
        self.title_canvas.create_image(content_panel_x+(self.pyd.calc_width*1.5)//16, (self.pyd.calc_height*2.75)//9, image=self.pyd.HELP_IMAGE_3, tag=("CONTENT_PANEL", "HELP_PANEL"))

        self.title_canvas.create_text(content_panel_x+(self.pyd.calc_width*3.75)//16, (self.pyd.calc_height*4.75)//9, font=(self.pyd.default_font, self.pyd.fontScale(18)), justify="center", width=(self.pyd.calc_width*5)//32, fill="white", text=help_text_4, tag=("CONTENT_PANEL", "HELP_PANEL"))
        self.title_canvas.create_image(content_panel_x+(self.pyd.calc_width*1.5)//16, (self.pyd.calc_height*4.75)//9, image=self.pyd.HELP_IMAGE_4, tag=("CONTENT_PANEL", "HELP_PANEL"))

        self.title_canvas.create_text(content_panel_x+(self.pyd.calc_width*3.75)//16, (self.pyd.calc_height*6.75)//9, font=(self.pyd.default_font, self.pyd.fontScale(18)), justify="center", width=(self.pyd.calc_width*5)//32, fill="white", text=help_text_5, tag=("CONTENT_PANEL", "HELP_PANEL"))
        self.title_canvas.create_image(content_panel_x+(self.pyd.calc_width*1.5)//16, (self.pyd.calc_height*6.75)//9, image=self.pyd.HELP_IMAGE_5, tag=("CONTENT_PANEL", "HELP_PANEL"))


        #*Finishing methods
        self.displayDefault() #default settings
        thr.start_new_thread(self.serverStatusUpdater, ()) #online server manager


    #*Title specific methods
    def displayDefault(self, event=""):
        if event != "": # log event info
            self.pyd.log("displayDefault() from event {} at ({},{})".format(event.type,event.x,event.y))
        
        #Hide all panels bar the main panel
        self.title_canvas.itemconfigure("MAIN_PANEL", state='normal')
        self.title_canvas.itemconfigure("GAMEMODE_PANEL", state='hidden')
        self.title_canvas.itemconfigure("GM_DETAILS_PANEL", state='hidden')
        self.title_canvas.itemconfigure("CONTENT_PANEL", state='hidden')

    def displayGamemodes(self, event=""):
        if event != "": # log event info
            self.pyd.log("displayGamemodes() from event {} at ({},{})".format(event.type,event.x,event.y))

        #Hide all panels bar the main & gamemode panels
        self.displayDefault()
        self.title_canvas.itemconfigure("GAMEMODE_PANEL", state='normal')

    def displayContentPanel(self, panel, event=""):
        if event != "": # log event info
            self.pyd.log("displayContentPanel({}) from event {} at ({},{})".format(panel, event.type,event.x,event.y))

        #Hide all panels bar the main & content panels
        self.displayDefault()
        self.title_canvas.itemconfigure(panel, state="normal")
        if self.fullscreen_toggle:
            self.title_canvas.itemconfigure("PREV_RESOLUTION", state="hidden")
            self.title_canvas.itemconfigure("NEXT_RESOLUTION", state="hidden")

    def displayGMDetails(self, panel, event=""):
        if event != "": # log event info
            self.pyd.log("displayGMDetails({}) from event {} at ({},{})".format(panel, event.type,event.x,event.y))

        self.gamemode_selected = panel[:panel.find("_")] #set gamemode e.g. "HARD_PANEL" -> "HARD"

        #Hide all panels bar the main, gamemode & GM detail panels
        self.title_canvas.itemconfigure("GM_DETAILS_PANEL", state='hidden')
        self.title_canvas.itemconfigure("CONTENT_PANEL", state='hidden')
        self.title_canvas.itemconfigure(panel, state="normal")
        self.title_canvas.itemconfigure("GM_SETTINGS", state="normal")

        #Customise game details if multiplayer
        if panel == "MULTIPLAYER_PANEL":
            self.title_canvas.itemconfigure("MULTIPLAYER_CREATE", state="hidden")
            self.title_canvas.itemconfigure("MULTIPLAYER_TOGGLE", image=self.pyd.MULTIPLAYER_JOIN)
            self.pyd.multiplayer_toggle_state = "JOIN"
            self.displayLobbies = True

        else:
            self.title_canvas.itemconfigure("GM_INFO", state="normal")
            self.displayLobbies = False

    def toggleMultiplayer(self, event=""):
        if event != "": # log event info
            self.pyd.log("toggleMultiplayer() from event {} at ({},{})".format(event.type,event.x,event.y))

        #Toggle multiplayer details for either joining or creating a server
        if self.pyd.multiplayer_toggle_state == "JOIN":
            self.pyd.multiplayer_toggle_state = "CREATE"
            self.title_canvas.itemconfigure("MULTIPLAYER_TOGGLE", image=self.pyd.MULTIPLAYER_CREATE)
            self.title_canvas.itemconfigure("MULTIPLAYER_CREATE", state="normal")
            self.title_canvas.itemconfigure("MULTIPLAYER_JOIN", state="hidden")
            self.displayLobbies = False
        else:
            self.pyd.multiplayer_toggle_state = "JOIN"
            self.title_canvas.itemconfigure("MULTIPLAYER_TOGGLE", image=self.pyd.MULTIPLAYER_JOIN)
            self.title_canvas.itemconfigure("MULTIPLAYER_CREATE", state="hidden")
            self.title_canvas.itemconfigure("MULTIPLAYER_JOIN", state="normal")
            self.displayLobbies = True

    def toggleCrazy(self, event=""):
        if event != "": # log event info
            self.pyd.log("toggleCrazy() from event {} at ({},{})".format(event.type,event.x,event.y))

        #Toggle the crazy mode and update variables
        if self.pyd.crazy_toggle_state:
            self.pyd.crazy_toggle_state = False
            self.title_canvas.itemconfigure("CRAZY_TOGGLE", image=self.pyd.CHECKBOX_BLANK)
            self.title_canvas.itemconfigure("HARD_ROUNDS", text=str(self.pyd.HARD_NO_ROUNDS))
            self.title_canvas.itemconfigure("HARD_MONEY", text=str(self.pyd.HARD_START_MONEY))
            self.title_canvas.itemconfigure("HARD_HEALTH", text=str(self.pyd.HARD_BASE_HEALTH))
            self.gamemode_selected = "HARD"
        else:
            self.pyd.crazy_toggle_state = True
            self.title_canvas.itemconfigure("CRAZY_TOGGLE", image=self.pyd.CRAZY_ON)
            self.title_canvas.itemconfigure("HARD_ROUNDS", text=str(self.pyd.CRAZY_NO_ROUNDS))
            self.title_canvas.itemconfigure("HARD_MONEY", text=str(self.pyd.CRAZY_START_MONEY))
            self.title_canvas.itemconfigure("HARD_HEALTH", text=str(self.pyd.CRAZY_BASE_HEALTH))
            self.gamemode_selected = "CRAZY"

        self.title_canvas.itemconfigure("HARD_BADGE", image=self.checkBadge(self.gamemode_selected))

    def saveSettings(self, event=""):
        if event != "": # log event info
            self.pyd.log("saveSettings() from event {} at ({},{})".format(event.type,event.x,event.y))

        #Try and get client name
        try:
            self.pyd.CLIENT_NAME = self.client_name.get()
        except AttributeError:
            pass

        #Store settings in dictionary for JSON storage
        settings = {
            "resolution": self.pyd.RESOLUTION,
            "fullscreen":  self.pyd.FULLSCREEN ,
            "client_name": self.pyd.CLIENT_NAME,
            "texture_pack": self.pyd.ACTIVE_TEXTURE,
            "rich_presence": self.pyd.DRP_ENABLED,
            "debug": self.pyd.DEBUG,
            "server_address": self.pyd.DS_ADDRESS,
        }
        
        #Write JSON to file
        open(self.pyd.SETTINGS_PATH, 'w').write(json.dumps(settings, indent=4))

        #Restart the program
        os.startfile(__file__)
        quit()

    def resetToDefaults(self, event=""):
        if event != "": # log event info
            self.pyd.log("resetToDefaults() from event {} at ({},{})".format(event.type,event.x,event.y))

        #Dialogue to confirm decision
        if messagebox.askokcancel("Reset all to default", "Do you want to reset all settings to their defaults?"): #returns bool
            self.pyd.setDefaults() #reset settings to defaults
            
            #Updates title screen with new settings
            self.title_canvas.itemconfigure("RESOLUTION", text="{}x{}".format(self.pyd.RESOLUTION[0], self.pyd.RESOLUTION[1]))
            self.client_name.set(self.pyd.CLIENT_NAME)
            
            self.resolution_ptr = self.pyd.WINDOW_RESOLUTIONS.index(self.pyd.RESOLUTION)
            self.texture_ptr = self.pyd.TEXTURE_PACKS.index(self.pyd.ACTIVE_TEXTURE)

            if self.pyd.FULLSCREEN:
                self.title_canvas.itemconfigure("FULLSCREEN_CHECKBOX", image=self.pyd.FULLSCREEN_ON)
            else:
                self.title_canvas.itemconfigure("FULLSCREEN_CHECKBOX", image=self.pyd.CHECKBOX_BLANK)
            
            self.title_canvas.itemconfigure("ACTIVE_TEXTURE", text=str(self.pyd.ACTIVE_TEXTURE))

            if self.pyd.DRP_ENABLED:
                self.title_canvas.itemconfigure("DRP_CHECKBOX", image=self.pyd.DRP_ON)
            else:
                self.title_canvas.itemconfigure("DRP_CHECKBOX", image=self.pyd.CHECKBOX_BLANK)

            if self.pyd.DEBUG:
                self.title_canvas.itemconfigure("DEBUG_CHECKBOX", image=self.pyd.DEBUG_ON)
            else:
                self.title_canvas.itemconfigure("DEBUG_CHECKBOX", image=self.pyd.CHECKBOX_BLANK)

            #Save settings and reset game
            self.saveSettings()

    def prevResolution (self, event=""):
        #Find previously available texture pack
        self.resolution_ptr -= 1
        self.resolution_ptr = max(0, min(len(self.pyd.WINDOW_RESOLUTIONS)-1, self.resolution_ptr))
        try:
            self.pyd.RESOLUTION = self.pyd.WINDOW_RESOLUTIONS[self.resolution_ptr]
        except IndexError:
            pass

        #Update UI with new resolution        
        self.title_canvas.itemconfigure("RESOLUTION", text="{}x{}".format(self.pyd.RESOLUTION[0], self.pyd.RESOLUTION[1]))

    def nextResolution (self, event=""):
        #Find next available texture pack
        self.resolution_ptr += 1
        self.resolution_ptr = max(0, min(len(self.pyd.WINDOW_RESOLUTIONS)-1, self.resolution_ptr))
        try:
            self.pyd.RESOLUTION = self.pyd.WINDOW_RESOLUTIONS[self.resolution_ptr]
        except IndexError:
            pass

        #Update UI with new resolution
        self.title_canvas.itemconfigure("RESOLUTION", text="{}x{}".format(self.pyd.RESOLUTION[0], self.pyd.RESOLUTION[1]))

    def toggleFullscreen (self, event=""):
        #Toggle fullscreen setting
        if not self.fullscreen_toggle:
            self.fullscreen_toggle = True
            self.title_canvas.itemconfigure("NEXT_RESOLUTION", state="hidden")
            self.title_canvas.itemconfigure("PREV_RESOLUTION", state="hidden")
            
            self.title_canvas.itemconfigure("RESOLUTION", text="{}x{}".format(self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
            self.title_canvas.itemconfigure("FULLSCREEN_CHECKBOX", image=self.pyd.FULLSCREEN_ON)

            self.prev_resolution = self.pyd.RESOLUTION
            self.pyd.RESOLUTION = [self.root.winfo_screenwidth(), self.root.winfo_screenheight()]

        else:
            self.fullscreen_toggle = False
            self.pyd.RESOLUTION = self.prev_resolution

            self.title_canvas.itemconfigure("NEXT_RESOLUTION", state="normal")
            self.title_canvas.itemconfigure("PREV_RESOLUTION", state="normal")

            self.title_canvas.itemconfigure("RESOLUTION", text="{}x{}".format(self.pyd.RESOLUTION[0], self.pyd.RESOLUTION[1]))
            self.title_canvas.itemconfigure("FULLSCREEN_CHECKBOX", image=self.pyd.CHECKBOX_BLANK)

            

        self.pyd.FULLSCREEN = self.fullscreen_toggle

    def nextTexture(self, event=""):
        #Find next available texture pack
        self.texture_ptr += 1
        self.texture_ptr = max(0, min(len(self.pyd.TEXTURE_PACKS)-1, self.texture_ptr))
        try:
            self.pyd.ACTIVE_TEXTURE = self.pyd.TEXTURE_PACKS[self.texture_ptr]
        except IndexError:
            pass

        #Update UI with new texture
        self.title_canvas.itemconfigure("ACTIVE_TEXTURE", text="{}".format(self.pyd.ACTIVE_TEXTURE))

    def prevTexture(self, event=""):
        #Find previously available texture pack
        self.texture_ptr -= 1
        self.texture_ptr = max(0, min(len(self.pyd.TEXTURE_PACKS)-1, self.texture_ptr))
        try:
            self.pyd.ACTIVE_TEXTURE = self.pyd.TEXTURE_PACKS[self.texture_ptr]
        except IndexError:
            pass

        #Update UI with new texture
        self.title_canvas.itemconfigure("ACTIVE_TEXTURE", text="{}".format(self.pyd.ACTIVE_TEXTURE))

    def toggleDRP (self, event=""):
        #Toggle discord rich presence
        if not self.drp_toggle:
            self.drp_toggle = True
            self.title_canvas.itemconfigure("DRP_CHECKBOX", image=self.pyd.DRP_ON)#update UI
        else:
            self.drp_toggle = False
            self.title_canvas.itemconfigure("DRP_CHECKBOX", image=self.pyd.CHECKBOX_BLANK)#update UI

        self.pyd.DRP_ENABLED = self.drp_toggle

    def toggleDebug (self, event=""):
        #Toggle debug mode
        if not self.debug_toggle:
            self.debug_toggle = True
            self.title_canvas.itemconfigure("DEBUG_CHECKBOX", image=self.pyd.DEBUG_ON)#update UI
        else:
            self.debug_toggle = False
            self.title_canvas.itemconfigure("DEBUG_CHECKBOX", image=self.pyd.CHECKBOX_BLANK)#update UI

        self.pyd.DEBUG = self.debug_toggle

    def openMap(self, event="", filename=None):
        if event != "": # log event info
            self.pyd.log("openMap() from event {} at ({},{})".format(event.type, event.x, event.y))

        #Prompt user to select a file
        while True:
            if filename == None:
                filename = filedialog.askopenfilename(initialdir="/maps/", title="Select file", filetypes=(("PyDefence map file","*.json"),))
                

            #! Validation
            #Validate selected file
            if filename != "": #must not be empty string
                if filename.split(".")[-1].lower() == "json": #must have .json extension
                    try:
                        self.loaded_map = self.pyd.loadJSON(open(filename, 'r').read())

                        #Check if file contains valid keys
                        self.loaded_map["map_difficulty"]
                        self.loaded_map["name"]

                        #Check if the map was designed with another texture pack in mind
                        if self.loaded_map["texture"] != self.pyd.ACTIVE_TEXTURE:
                            self.pyd.alert("Map selected was designed with a different texture pack", "Warning")

                        #Check that the number tiles matches the stated number
                        if len(self.loaded_map["tiles"]) != self.loaded_map["map_size"]**2:
                            raise ValueError

                        #Get details from file and config UI text
                        self.map_name = self.loaded_map["name"]
                        self.title_canvas.itemconfigure("MAP_NAME", text="{}".format(self.map_name[:20]))
                        self.pyd.log("map '{}' selected".format(self.map_name))
                        self.map_size = int(self.loaded_map["map_size"])

                        break

                    except (FileNotFoundError, FileExistsError):
                        return

                    except:
                        #If map file is invalid
                        if filename != None:
                            self.pyd.log("invalid map selected")
                            self.pyd.alert("Map selected isn't in the correct format", "Warning")
                            continue
                        else:
                            return
                else:
                    continue
            else:
                return

        #Set thumbnail
        self.pyd.thumbnail_image = self.pyd.image("{}.png".format(filename[:-5]), True) #180x180 image from mapping tool
        self.title_canvas.itemconfigure("MAP_THUMBNAIL", image=self.pyd.thumbnail_image)

    def checkBadge(self, badge):
        #Check if a badge has been unlocked
        unlocked_badges = self.pyd.GAME_DATA["badges_unlocked"]
        self.pyd.log("loaded {} badges from save".format(unlocked_badges))

        #Check for easy/normal badges
        if badge in unlocked_badges:
            if badge == "EASY":
                image = self.pyd.EASY_BADGE
            elif badge == "NORMAL":
                image = self.pyd.NORMAL_BADGE
        else:
            image = self.pyd.BLANK_BADGE

        #Check for hard/crazy badges
        if badge == "HARD":
            if "HARD" in unlocked_badges:
                image = self.pyd.HARD_BADGE

            if "CRAZY" in unlocked_badges:
                image = self.pyd.CRAZY_BADGE
        
        return image

    def launchGame(self, event=""):
        if event != "": # log event info
            self.pyd.log("launchGame({}) from event {} at ({},{})".format(self.gamemode_selected, event.type, event.x, event.y))

        #Confirm a map has been selected
        try:
            self.map_size
        except AttributeError:
            #Highlight if map not selected
            self.title_canvas.itemconfigure("MAP_NAME", fill="red", font=(self.pyd.default_font, self.pyd.fontScale(16)))
            self.root.update()
            time.sleep(0.5)
            self.title_canvas.itemconfigure("MAP_NAME", fill="white", font=(self.pyd.default_font, self.pyd.fontScale(12)))
            return

        #If multiplayer check that client is connected and lobbies are available
        if self.gamemode_selected == "MULTIPLAYER":
            if self.pyd.multiplayer_toggle_state == "JOIN" and len(self.client.all_lobbies) == 0: 
                return

            if self.client.ping == "Not connected":
                return


        #Launch the game hiding the title frame
        self.title_canvas.itemconfigure("LAUNCH_BUTTON", state="disabled") 
        self.title_area.pack_forget()

        #Update gameplay variables based off difficulty
        self.pyd.last_unlocked_ability = 0
        self.pyd.current_round = 0
        self.pyd.game_over = False
        self.pyd.units_killed = 0
        self.ability1_active = False
        self.purchased_tower = None
        self.pyd.max_pre_round_time = self.pyd.DEFAULT_PRE_ROUND_TIME
        self.pyd.game_speed_mod = 1
        self.prev_msg = None

        #Setting game parameters
        if self.gamemode_selected == "EASY":
            self.pyd.money = self.pyd.EASY_START_MONEY
            self.pyd.max_base_health = self.pyd.EASY_BASE_HEALTH
            self.pyd.max_rounds = self.pyd.EASY_NO_ROUNDS
            self.pyd.difficulty_value = 2

        elif self.gamemode_selected == "NORMAL":
            self.pyd.money = self.pyd.NORMAL_START_MONEY
            self.pyd.max_base_health = self.pyd.NORMAL_BASE_HEALTH
            self.pyd.max_rounds = self.pyd.NORMAL_NO_ROUNDS
            self.pyd.difficulty_value = 2.25

        elif self.gamemode_selected == "HARD":
            self.pyd.money = self.pyd.HARD_START_MONEY
            self.pyd.max_base_health = self.pyd.HARD_BASE_HEALTH
            self.pyd.max_rounds = self.pyd.HARD_NO_ROUNDS
            self.pyd.difficulty_value = 2.4

        elif self.gamemode_selected == "CRAZY":
            self.pyd.money = self.pyd.CRAZY_START_MONEY
            self.pyd.max_base_health = self.pyd.CRAZY_BASE_HEALTH
            self.pyd.max_rounds = self.pyd.CRAZY_NO_ROUNDS
            self.pyd.difficulty_value = 2.5

        elif self.gamemode_selected == "MULTIPLAYER":
            self.pyd.money = 5000
            self.pyd.max_base_health = 2000
            self.pyd.max_rounds = "INF"


        #Update live game variables
        self.pyd.current_base_health = self.pyd.max_base_health

        #Launch loading screen to scale gameplay images
        self.loadingScreen()
        self.title_canvas.itemconfigure("LAUNCH_BUTTON", state="normal")
        self.loading_area.pack_forget() 

        #Launch gameplay screen
        self.gameplayScreen()

    def serverStatusUpdater(self):
        #Server status checker/updater

        #Initialise variables
        prev_lobbies = None
        refresh_counter = 0
        self.lobby_selected = None


        while True:
            try:
                #Check if a new message has been sent
                try:
                    if self.client.new_msg["sender"] != None:
                        self.chatLog(self.client.new_msg)
                        self.client.resetMsg()
                except:
                    pass

                #Update ping text
                if self.client.ping == "Not connected":
                    col="red"
                    status = str(self.client.ping)
                else:
                    col="lime"
                    status = "Online ({})".format(str(self.client.ping))

                self.title_canvas.itemconfigure("SERVER_STATUS", text=status)
                self.title_canvas.itemconfigure("SERVER_STATUS_COL", fill=col)

                #Get lobbies every 50 updates
                refresh_counter += 1
                if refresh_counter >= 50:
                    refresh_counter = 0
                    if self.client.ping != "Not connected":
                        self.client.getLobbies()

                #Display lobbies on the join lobby screen
                if prev_lobbies != self.client.all_lobbies:
                    y=0
                    self.title_canvas.delete("LOBBY_PREVIEWS")
                    for i in range(min(3, len(list(self.client.all_lobbies)))):
                        lobby = list(self.client.all_lobbies)[i]
                        lobby_details = self.client.all_lobbies[lobby]

                        y+=2

                        #Display lobby plaques
                        if self.displayLobbies: lobby_plaque_state = "normal"
                        else: lobby_plaque_state = "hidden"
                        
                        self.title_canvas.create_image((self.pyd.calc_width*55)//64, (self.pyd.calc_height*(19+y))//36, image=self.pyd.LOBBY_PLAQUE, state=lobby_plaque_state, tag=("GM_DETAILS_PANEL", "MULTIPLAYER_PANEL", "MULTIPLAYER_JOIN", "LOBBY_PREVIEWS", "LOBBY_PREVIEW_ID_{}".format(i)))
                        self.title_canvas.create_text((self.pyd.calc_width*55)//64, (self.pyd.calc_height*(19+y))//36, font=(self.pyd.default_font, self.pyd.fontScale(12)), justify="center", fill="white", text="{} | {} | {}".format(lobby_details["name"][:min(len(lobby_details["name"]), 16)], lobby_details["map"][:min(len(lobby_details["map"]), 8)], lobby_details["difficulty"]),  state=lobby_plaque_state, tag=("GM_DETAILS_PANEL", "MULTIPLAYER_PANEL", "MULTIPLAYER_JOIN", "LOBBY_PREVIEWS", "LOBBY_PREVIEW_ID_{}".format(i)))
                        self.title_canvas.tag_bind("LOBBY_PREVIEW_ID_{}".format(i), "<Button-1>", lambda event, idx=i: self.setLobby(idx, event))

                    prev_lobbies = self.client.all_lobbies
                    
            except:
                pass
            
            #Rate limiter
            time.sleep(0.1)

    def setLobby(self, idx, event=""):
        #Try and launch the lobby that was clicked
        self.lobby_selected = list(self.client.all_lobbies)[idx]

        #Try to open the lobby's map locally
        if self.openMap(event, "maps/"+self.client.all_lobbies[self.lobby_selected]["map"]+".json") != None:
            self.pyd.alert("You don't have that map file!")
            return

        #Set game settings
        self.pyd.difficulty_value = self.client.all_lobbies[self.lobby_selected]["difficulty"]
        
        #Launch game
        self.launchGame(event)


    #* Loading screen
    def loadingScreen(self):
        #Initial variables
        self.pyd.game_images_scaled = False

        #Create a frame for the loading screen
        self.loading_area = tk.Frame(self.main_area, width=self.pyd.calc_width, height=self.pyd.calc_height, bg="white")
        self.loading_area.pack()

        #Create the canvas for image placement
        self.loading_canvas = tk.Canvas(self.loading_area, width=self.pyd.calc_width, height=self.pyd.calc_height, highlightthickness=0, bg="white")
        self.loading_canvas.place(relx=0, rely=0)

        #Images used for loading bar
        self.loading_canvas.create_image(-self.pyd.calc_width//32, self.pyd.calc_height//2, image=self.pyd.LOADING_BAR, tag=("LOADING_OVERLAY", "LOADING_BAR"))

        self.loading_canvas.create_image(self.pyd.calc_width//2, self.pyd.calc_height//2, image=self.pyd.LOADING_OVERLAY, tag=("LOADING_OVERLAY"))

        #Status text
        self.loading_canvas.create_text(self.pyd.calc_width//2, (self.pyd.calc_height*6)//9, text="", fill="black", font=(self.pyd.default_font, self.pyd.fontScale(32)), tag=("LOADING_OVERLAY", "LOADING_SUMMARY"))


        #* Load units
        #Gather all units and sort them by strength
        self.unit_dictionary = []
        try:
            unit_file_list = os.listdir("units/")
        except:
            self.pyd.alert("No unit folder found!", "FATAL")
            quit()

        #! Validation
        #Validate units
        corrupt_units = False
        for unit_file in unit_file_list:
            if unit_file.split(".")[-1] == "json":
                try:
                    unit_json = self.pyd.loadJSON(open("units/{}".format(unit_file), 'r').read())
                    
                    #Validate contents - must contain:
                    unit_json["name"]
                    unit_json["texture_name"]
                    dict(unit_json["attributes"])

                    self.unit_dictionary.append(unit_json)
                    self.pyd.game_images.append(["UNIT_"+str(unit_json["texture_name"]), "textures/"+self.pyd.ACTIVE_TEXTURE+"/units/"+str(unit_json["texture_name"])])
                except:
                    corrupt_units = True
        
        #Alert for corrupt units
        if corrupt_units: 
            self.pyd.log("invalid units found")
            self.pyd.alert("Corrupted unit files in unit folder", "Warning")

        #Check if no valid units
        if len(self.unit_dictionary) == 0: 
            self.pyd.alert("No valid units", "FATAL")
            quit()

        #Sort unit dictionary
        self.unit_dictionary = sorted(self.unit_dictionary, key=lambda k: k["attributes"]["strength"])


        #* Load towers
        #Gather all units and sort them by strength
        self.tower_dictionary = []
        try:
            tower_file_list = os.listdir("towers/")
        except:
            self.pyd.alert("No tower folder found!", "FATAL")
            quit()

        #! Validation
        #Validate towers
        corrupt_towers = False
        for tower_file in tower_file_list:
            if tower_file.split(".")[-1] == "json":
                try:
                    tower_json = self.pyd.loadJSON(open("towers/{}".format(tower_file), 'r').read())
                    
                    #Validate contents - must contain:
                    tower_json["name"]
                    tower_json["description"]
                    tower_json["texture_name"]
                    dict(tower_json["attributes"])
                    dict(tower_json["attributes"]["projectile"])

                    self.tower_dictionary.append(tower_json)
                    self.pyd.game_images.append(["TOWER_"+str(tower_json["texture_name"]), "textures/"+self.pyd.ACTIVE_TEXTURE+"/towers/"+str(tower_json["texture_name"])])
                    self.pyd.game_images.append(["PREV_TOWER_"+str(tower_json["texture_name"]), "textures/"+self.pyd.ACTIVE_TEXTURE+"/towers/"+str(tower_json["texture_name"])])
                    self.pyd.game_images.append(["PROJ_"+str(tower_json["attributes"]["projectile"]["texture_name"]), "textures/"+self.pyd.ACTIVE_TEXTURE+"/towers/projectiles/"+str(tower_json["attributes"]["projectile"]["texture_name"])])
                except ValueError:
                    corrupt_towers = True
        
        #Alert for corrupt towers
        if corrupt_towers:
            self.pyd.log("invalid towers found")
            self.pyd.alert("Corrupted towers files in tower folder", "Warning")

        #Check if no valid towers
        if len(self.tower_dictionary) == 0: 
            self.pyd.alert("No valid towers", "FATAL")
            quit()

        #Sort tower dictionary
        self.tower_dictionary = sorted(self.tower_dictionary, key=lambda k: k["attributes"]["cost"])


        #Connect to server
        if self.gamemode_selected == "MULTIPLAYER":
            if self.pyd.multiplayer_toggle_state == "JOIN":
                if self.lobby_selected != None and self.client.ping != "Not connected":
                    self.client.joinGameLobby(self.lobby_selected)
            else:
                if self.client.ping != "Not connected":
                    self.pyd.difficulty_value = self.lobby_difficulty.get()
                    self.client.createGameLobby([self.loaded_map["name"], self.lobby_difficulty.get(), self.lobby_name.get()])


        #Syncing loading from helper and progress bar
        thr.start_new_thread(self.pyd.loadGameImages, (self.map_size, ))

        #Wait until thread started
        while True: 
            try:
                self.pyd.game_image_progress
                break
            except: pass

        #Wait until thread finished and move progressbar
        while not self.pyd.game_images_scaled:
            self.loading_canvas.coords("LOADING_BAR", ((self.pyd.calc_width//2)*self.pyd.game_image_progress), self.pyd.calc_height//2)
            self.loading_canvas.itemconfigure("LOADING_SUMMARY", text=self.pyd.current_summary_text)
            self.root.update()


        self.pyd.log("game launch success")


    #* Gameplay screen
    def gameplayScreen(self):
        #Create a frame for the gameplay screen
        self.gameplay_area = tk.Frame(self.main_area, width=self.pyd.calc_width, height=self.pyd.calc_height, bg="white")
        self.gameplay_area.pack()

        #Create the canvas for image placement
        self.map_canvas = tk.Canvas(self.gameplay_area, width=self.pyd.calc_height, height=self.pyd.calc_height, highlightthickness=0)
        self.map_canvas.place(relx=0, rely=0)

        #Place map grid
        for x in range(self.map_size):
            for y in range(self.map_size):
                _tag = "x{}y{}".format(x,y)

                #Create image on canvas
                self.map_canvas.create_image(((x/self.map_size)*self.pyd.calc_height)+(self.pyd.calc_height//2)/self.map_size, ((y/self.map_size)*self.pyd.calc_height)+(self.pyd.calc_height//2)/self.map_size, image=self.pyd.GAME_IMAGE_DICT[str(self.loaded_map["tiles"][self.map_size*x+y]["texture"])], tags=("MAP_TILE", "x{}y{}".format(x,y)))
                self.map_canvas.tag_bind(_tag, "<Button-1>", self.placeTower)

        #Place base + start
        sf = self.pyd.calc_height/self.map_size

        start_pos = self.loaded_map["valid_path"].split("/")[:-1][0].split(".")
        self.map_canvas.create_image(int(start_pos[0])*sf+sf/2, int(start_pos[1])*sf+sf/2, image=self.pyd.GAME_IMAGE_DICT["BASE_START"])

        base_pos = self.loaded_map["valid_path"].split("/")[:-1][-1].split(".")
        base_images = [self.pyd.GAME_IMAGE_DICT["BASE_1"], self.pyd.GAME_IMAGE_DICT["BASE_2"], self.pyd.GAME_IMAGE_DICT["BASE_3"]]
        self.base_object = BaseTower(self.map_canvas, (int(base_pos[0])*sf+sf/2, int(base_pos[1])*sf+sf/2), base_images, self.pyd.base_attributes, sf, self.pyd, tag="BASE")
        thr.start_new_thread(self.base_object.go, ())

        #Towers placed list
        self.towers_placed = []

        #Range preview object
        self.map_canvas.create_oval(0,0,1,1, state="hidden", width=int(2/(self.pyd.x_scalefactor*self.pyd.y_scalefactor)), outline="black", tags="TOWER_RANGE_PREVIEW")


        #Create content area canvas
        content_x = (((self.pyd.calc_width*7)//16)*3.5)//7
        self.content_canvas = tk.Canvas(self.gameplay_area, width=((self.pyd.calc_width*7)//16), height=(self.pyd.calc_height), highlightthickness=0, bg="black")
        self.content_canvas.place(relx=9/16, rely=0)

        self.content_canvas.create_image(content_x, ((self.pyd.calc_height*4.5)//9), image=self.pyd.GAME_IMAGE_DICT["CONTROL_BG"])

        #Header
        self.content_canvas.create_image(content_x, ((self.pyd.calc_height*1)//9), image=self.pyd.GAME_IMAGE_DICT["TITLE_IMAGE"])
        self.content_canvas.create_text(content_x*0.2, ((self.pyd.calc_height*1.75)//9), text="{}".format(self.pyd.money), font=(self.pyd.default_font, self.pyd.fontScale(20)), state="disabled", tag=("MONEY_STATISTIC"))
        self.content_canvas.create_text(content_x*0.625, ((self.pyd.calc_height*1.75)//9), text="{:0>2}:{:0>2}".format(self.pyd.time_left%60, self.pyd.time_left-(60*self.pyd.time_left%60)), font=(self.pyd.default_font, self.pyd.fontScale(20)), state="disabled", tag=("TIME_STATISTIC"))
        self.content_canvas.create_text(content_x*0.95, ((self.pyd.calc_height*1.75)//9), text="{}".format(self.pyd.units_killed), font=(self.pyd.default_font, self.pyd.fontScale(20)), state="disabled", tag=("UNIT_KILL_STATISTIC"))
        self.content_canvas.create_text(content_x*1.275, ((self.pyd.calc_height*1.75)//9), text="{}".format(self.pyd.current_round), font=(self.pyd.default_font, self.pyd.fontScale(20)), state="disabled", tag=("ROUND_STATISTIC"))
        
        #Health bar
        self.healthbar_coords = [content_x*1.55, (self.pyd.calc_height*1.8)//9, content_x*1.85,(self.pyd.calc_height*1.85)//9]
        self.content_canvas.create_rectangle(self.healthbar_coords, fill='grey')
        self.content_canvas.create_rectangle(self.healthbar_coords, fill='#%02X%02X%02X' % (0,255,0), tags=("BASE_HEALTH_BAR"))
        self.content_canvas.create_text(content_x*1.7, ((self.pyd.calc_height*1.7)//9), text="{}/{}".format(self.pyd.current_base_health, self.pyd.max_base_health), font=(self.pyd.default_font, self.pyd.fontScale(12)), state="disabled", tag=("HEALTH_STATISTIC"))

        #Towers selection
        self.content_canvas.create_image(content_x, ((self.pyd.calc_height*4.5)//9), image=self.pyd.GAME_IMAGE_DICT["SELECTION_AREA"])

        #Tower plaques
        self.tower_plaque_start_x = content_x*(0.265)
        for column in range(int(len(self.tower_dictionary)/2+0.5)):
            #First row 
            idx1 = (column*2)

            #Main display card
            self.content_canvas.create_image(content_x*(0.265+(column*0.488)), ((self.pyd.calc_height*3.09)//9), image=self.pyd.GAME_IMAGE_DICT["PANEL_TOWER_PLAQUE"], tags=("TOWER_SELECTION", "TOWER_PLAQUE_{}".format(idx1)))
            self.content_canvas.create_image(content_x*(0.265+(column*0.488)), ((self.pyd.calc_height*2.59)//9), image=self.pyd.GAME_IMAGE_DICT["PREV_TOWER_{}".format(self.tower_dictionary[idx1]["texture_name"])], tags=("TOWER_SELECTION", "TOWER_BUY_{}".format(idx1)))
            self.content_canvas.create_text(content_x*(0.265+(column*0.488)), ((self.pyd.calc_height*3.19)//9), text="{}".format(self.tower_dictionary[idx1]["name"]), fill="white", font=(self.pyd.default_font, self.pyd.fontScale(14)), tags=("TOWER_SELECTION"))
            self.content_canvas.create_text(content_x*(0.265+(column*0.488)), ((self.pyd.calc_height*3.4)//9), text="{}".format(self.tower_dictionary[idx1]["attributes"]["cost"]), fill="white", font=(self.pyd.default_font, self.pyd.fontScale(16)), tags=("TOWER_SELECTION", "TOWER_COST_{}".format(idx1)))
            self.content_canvas.create_image(content_x*(0.265+(column*0.488)), ((self.pyd.calc_height*3.79)//9), image=self.pyd.GAME_IMAGE_DICT["PANEL_BUY_BUTTON"], tags=("TOWER_SELECTION", "TOWER_BUY_BUTTON_{}".format(idx1), "TOWER_BUY_{}".format(idx1)))
            self.content_canvas.tag_bind("TOWER_BUY_{}".format(idx1), "<Button-1>", lambda event, x=idx1: self.purchaseTower(x))

            self.content_canvas.create_image(content_x*(0.45+(column*0.488)), ((self.pyd.calc_height*2.24)//9), image=self.pyd.GAME_IMAGE_DICT["PANEL_INFO_BUTTON"], tags=("TOWER_SELECTION", "TOWER_INFO_BUTTON_{}".format(idx1)))
            self.content_canvas.tag_bind("TOWER_INFO_BUTTON_{}".format(idx1), "<Button-1>", lambda event, x=idx1: self.infoTowerPanel(x))
            
            self.content_canvas.create_image(content_x*(0.265+(column*0.488)), ((self.pyd.calc_height*3.09)//9), image=self.pyd.GAME_IMAGE_DICT["PANEL_TOWER_PLAQUE_INFO"], state="hidden", tags=("TOWER_SELECTION", "TOWER_INFO_{}".format(idx1)))
            
            self.content_canvas.create_image(content_x*(0.45+(column*0.488)), ((self.pyd.calc_height*2.24)//9), image=self.pyd.GAME_IMAGE_DICT["PANEL_INFO_CLOSE_BUTTON"], state="hidden", tags=("TOWER_SELECTION", "TOWER_INFO_{}".format(idx1), "TOWER_INFO_CLOSE_BUTTON_{}".format(idx1)))
            self.content_canvas.tag_bind("TOWER_INFO_{}".format(idx1), "<Button-1>", lambda event, x=idx1: self.infoTowerPanel(x, True))
            
            #Info display card
            self.content_canvas.create_text(content_x*(0.265+(column*0.488)), ((self.pyd.calc_height*2.4)//9), text="{}".format(self.tower_dictionary[idx1]["name"]), fill="white", font=(self.pyd.default_font, self.pyd.fontScale(14)), state="hidden", tags=("TOWER_SELECTION", "TOWER_INFO_{}".format(idx1)))
            
            self.content_canvas.create_text(content_x*(0.265+(column*0.488)), ((self.pyd.calc_height*2.7)//9), text="Rate of fire", fill="white", font=(self.pyd.default_font, self.pyd.fontScale(11)), state="hidden", tags=("TOWER_SELECTION", "TOWER_INFO_{}".format(idx1)))
            self.content_canvas.create_text(content_x*(0.265+(column*0.488)), ((self.pyd.calc_height*2.9)//9), text="{}".format(self.tower_dictionary[idx1]["attributes"]["rate_of_fire"]), fill="white", font=(self.pyd.default_font, self.pyd.fontScale(14)), state="hidden", tags=("TOWER_SELECTION", "TOWER_INFO_{}".format(idx1)))
            
            self.content_canvas.create_text(content_x*(0.265+(column*0.488)), ((self.pyd.calc_height*3.1)//9), text="Projectile damage", fill="white", font=(self.pyd.default_font, self.pyd.fontScale(11)), state="hidden", tags=("TOWER_SELECTION", "TOWER_INFO_{}".format(idx1)))
            self.content_canvas.create_text(content_x*(0.265+(column*0.488)), ((self.pyd.calc_height*3.3)//9), text="{}".format(self.tower_dictionary[idx1]["attributes"]["projectile"]["damage"]), fill="white", font=(self.pyd.default_font, self.pyd.fontScale(14)), state="hidden", tags=("TOWER_SELECTION", "TOWER_INFO_{}".format(idx1)))
            
            self.content_canvas.create_text(content_x*(0.265+(column*0.488)), ((self.pyd.calc_height*3.5)//9), text="Projectile speed", fill="white", font=(self.pyd.default_font, self.pyd.fontScale(11)), state="hidden", tags=("TOWER_SELECTION", "TOWER_INFO_{}".format(idx1)))
            self.content_canvas.create_text(content_x*(0.265+(column*0.488)), ((self.pyd.calc_height*3.7)//9), text="{}".format(self.tower_dictionary[idx1]["attributes"]["projectile"]["speed"]), fill="white", font=(self.pyd.default_font, self.pyd.fontScale(14)), state="hidden", tags=("TOWER_SELECTION", "TOWER_INFO_{}".format(idx1)))
            


            #Check that 2nd row can be populated
            try:
                self.tower_dictionary[1+(column*2)]
            except:
                break

            #Second row
            idx2 = 1+(column*2)

            #Main display card
            self.content_canvas.create_image(content_x*(0.265+(column*0.488)), ((self.pyd.calc_height*5.21)//9), image=self.pyd.GAME_IMAGE_DICT["PANEL_TOWER_PLAQUE"], tags=("TOWER_SELECTION", "TOWER_PLAQUE_{}".format(idx2)))
            self.content_canvas.create_image(content_x*(0.265+(column*0.488)), ((self.pyd.calc_height*4.71)//9), image=self.pyd.GAME_IMAGE_DICT["PREV_TOWER_{}".format(self.tower_dictionary[idx2]["texture_name"])], tags=("TOWER_SELECTION", "TOWER_BUY_{}".format(idx2)))
            self.content_canvas.create_text(content_x*(0.265+(column*0.488)), ((self.pyd.calc_height*5.31)//9), text="{}".format(self.tower_dictionary[idx2]["name"]), fill="white", font=(self.pyd.default_font, self.pyd.fontScale(14)), tags=("TOWER_SELECTION"))
            self.content_canvas.create_text(content_x*(0.265+(column*0.488)), ((self.pyd.calc_height*5.52)//9), text="{}".format(self.tower_dictionary[idx2]["attributes"]["cost"]), fill="white", font=(self.pyd.default_font, self.pyd.fontScale(16)), tags=("TOWER_SELECTION", "TOWER_COST_{}".format(idx2)))
            self.content_canvas.create_image(content_x*(0.265+(column*0.488)), ((self.pyd.calc_height*5.91)//9), image=self.pyd.GAME_IMAGE_DICT["PANEL_BUY_BUTTON"], tags=("TOWER_SELECTION", "TOWER_BUY_BUTTON_{}".format(idx2), "TOWER_BUY_{}".format(idx2)))
            self.content_canvas.tag_bind("TOWER_BUY_{}".format(idx2), "<Button-1>", lambda event, x=idx2: self.purchaseTower(x))

            self.content_canvas.create_image(content_x*(0.45+(column*0.488)), ((self.pyd.calc_height*4.36)//9), image=self.pyd.GAME_IMAGE_DICT["PANEL_INFO_BUTTON"], tags=("TOWER_SELECTION", "TOWER_INFO_BUTTON_{}".format(idx2)))
            self.content_canvas.tag_bind("TOWER_INFO_BUTTON_{}".format(idx2), "<Button-1>", lambda event, x=idx2: self.infoTowerPanel(x))
            
            self.content_canvas.create_image(content_x*(0.265+(column*0.488)), ((self.pyd.calc_height*5.21)//9), image=self.pyd.GAME_IMAGE_DICT["PANEL_TOWER_PLAQUE_INFO"], state="hidden", tags=("TOWER_SELECTION", "TOWER_INFO_{}".format(idx2)))
            self.content_canvas.create_image(content_x*(0.45+(column*0.488)), ((self.pyd.calc_height*4.36)//9), image=self.pyd.GAME_IMAGE_DICT["PANEL_INFO_CLOSE_BUTTON"], state="hidden", tags=("TOWER_SELECTION", "TOWER_INFO_{}".format(idx2), "TOWER_INFO_CLOSE_BUTTON_{}".format(idx2)))
            self.content_canvas.tag_bind("TOWER_INFO_{}".format(idx2), "<Button-1>", lambda event, x=idx2: self.infoTowerPanel(x, True))

            #Info display card
            self.content_canvas.create_text(content_x*(0.265+(column*0.488)), ((self.pyd.calc_height*4.5)//9), text="{}".format(self.tower_dictionary[idx2]["name"]), fill="white", font=(self.pyd.default_font, self.pyd.fontScale(14)), state="hidden", tags=("TOWER_SELECTION", "TOWER_INFO_{}".format(idx2)))
            
            self.content_canvas.create_text(content_x*(0.265+(column*0.488)), ((self.pyd.calc_height*4.8)//9), text="Rate of fire", fill="white", font=(self.pyd.default_font, self.pyd.fontScale(11)), state="hidden", tags=("TOWER_SELECTION", "TOWER_INFO_{}".format(idx2)))
            self.content_canvas.create_text(content_x*(0.265+(column*0.488)), ((self.pyd.calc_height*5.0)//9), text="{}".format(self.tower_dictionary[idx2]["attributes"]["rate_of_fire"]), fill="white", font=(self.pyd.default_font, self.pyd.fontScale(14)), state="hidden", tags=("TOWER_SELECTION", "TOWER_INFO_{}".format(idx2)))
            
            self.content_canvas.create_text(content_x*(0.265+(column*0.488)), ((self.pyd.calc_height*5.2)//9), text="Projectile damage", fill="white", font=(self.pyd.default_font, self.pyd.fontScale(11)), state="hidden", tags=("TOWER_SELECTION", "TOWER_INFO_{}".format(idx2)))
            self.content_canvas.create_text(content_x*(0.265+(column*0.488)), ((self.pyd.calc_height*5.4)//9), text="{}".format(self.tower_dictionary[idx2]["attributes"]["projectile"]["damage"]), fill="white", font=(self.pyd.default_font, self.pyd.fontScale(14)), state="hidden", tags=("TOWER_SELECTION", "TOWER_INFO_{}".format(idx2)))
            
            self.content_canvas.create_text(content_x*(0.265+(column*0.488)), ((self.pyd.calc_height*5.6)//9), text="Projectile speed", fill="white", font=(self.pyd.default_font, self.pyd.fontScale(11)), state="hidden", tags=("TOWER_SELECTION", "TOWER_INFO_{}".format(idx2)))
            self.content_canvas.create_text(content_x*(0.265+(column*0.488)), ((self.pyd.calc_height*5.8)//9), text="{}".format(self.tower_dictionary[idx2]["attributes"]["projectile"]["speed"]), fill="white", font=(self.pyd.default_font, self.pyd.fontScale(14)), state="hidden", tags=("TOWER_SELECTION", "TOWER_INFO_{}".format(idx2)))
            

        #Slider creation
        self.slider_sensitivity = (len(self.tower_dictionary)/8)
        self.prev_x = 80*self.pyd.x_scalefactor
        self.content_canvas.create_image(80*self.pyd.x_scalefactor, ((self.pyd.calc_height*6.63)//9), image=self.pyd.GAME_IMAGE_DICT["HORIZONTAL_SLIDER"], tag=("HORIZONTAL_SLIDER"))
        self.content_canvas.tag_bind('HORIZONTAL_SLIDER', '<B1-Motion>', self.updateSliderPos) 
        self.content_canvas.tag_bind('HORIZONTAL_SLIDER', '<ButtonRelease-1>', self.alignPlaques)

        #Chat window
        self.content_canvas.create_image(content_x, ((self.pyd.calc_height*4.5)//9), image=self.pyd.GAME_IMAGE_DICT["CHAT_AREA"], state="hidden", tags=("CHAT_AREA", "CHAT"))
        self.content_canvas.create_image(content_x*1.8, ((self.pyd.calc_height*6.63)//9), image=self.pyd.GAME_IMAGE_DICT["SEND_MSG_BUTTON"], state="hidden", tags=("SEND_MSG", "CHAT"))
        
        self.chat_frame = tk.Frame(self.content_canvas, width=int(self.pyd.x_scalefactor*785), height=int(self.pyd.x_scalefactor*475), bg="black")
        self.chat_log = tk.Text(self.chat_frame, height=int(self.pyd.fontScale(20)), width=int(self.pyd.fontScale(65)), selectbackground="lightgrey", font=(self.pyd.default_font, 14), state="disabled")
        self.chat_log.pack(anchor=tk.NW, expand=1, fill=tk.BOTH)
        
        self.content_canvas.create_window(content_x, ((self.pyd.calc_height*4.2)//9), window=self.chat_frame, state="hidden", tags=("CHAT_LOG", "CHAT"))

        self.msg_to_send = tk.StringVar(self.root)
        self.msg_frame = tk.Frame(self.content_canvas, width=self.pyd.x_scalefactor*650, height=self.pyd.x_scalefactor*50)
        self.msg_entry = tk.Entry(self.msg_frame, width=int(self.pyd.fontScale(32)/self.pyd.x_scalefactor), font=(self.pyd.default_font, self.pyd.fontScale(24)), textvariable=self.msg_to_send, bg="lightgrey")
        self.msg_entry.pack(anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.root.bind('<Return>', lambda x, msg=self.msg_entry: self.sendMsg(msg.get()))
        self.content_canvas.create_image(content_x, ((self.pyd.calc_height*4.5)//9), image=self.pyd.GAME_IMAGE_DICT["CHAT_AREA"], state="hidden", tags=("CHAT_AREA", "CHAT"))
        self.content_canvas.create_image(content_x*1.8, ((self.pyd.calc_height*6.63)//9), image=self.pyd.GAME_IMAGE_DICT["SEND_MSG_BUTTON"], state="hidden", tags=("SEND_MSG", "CHAT"))
        self.content_canvas.tag_bind("SEND_MSG", '<Button-1>', lambda x, msg=self.msg_entry: self.sendMsg(msg.get()))

        self.content_canvas.create_window(content_x*0.825, ((self.pyd.calc_height*6.63)//9), window=self.msg_frame, state="hidden", tags=("MSG_ENTRY", "CHAT"))

        #Specials bar
        self.content_canvas.create_image(content_x, ((self.pyd.calc_height*8)//9), image=self.pyd.GAME_IMAGE_DICT["SPECIAL_BAR"])

        special_bar_x = (((self.pyd.calc_width*7)//16))//7
        self.content_canvas.create_image(special_bar_x*6, ((self.pyd.calc_height*8)//9), image=self.pyd.GAME_IMAGE_DICT["PLAY_BUTTON_OFF"], tag=("CONTROL_BUTTON", "PLAY_BUTTON"))
        self.content_canvas.tag_bind('PLAY_BUTTON', '<Enter>', lambda x: self.displayGameDetail("Plays the next round", x))
        self.content_canvas.tag_bind('PLAY_BUTTON', '<Button-1>', self.forceRoundStart)
        self.content_canvas.tag_bind('PLAY_BUTTON', '<ButtonRelease-1>', lambda x: self.content_canvas.itemconfigure("PLAY_BUTTON", image=self.pyd.GAME_IMAGE_DICT["PLAY_BUTTON_OFF"]))


        self.auto_run = False
        self.content_canvas.create_image(special_bar_x*5.6, ((self.pyd.calc_height*8.667)//9), image=self.pyd.GAME_IMAGE_DICT["AUTO_RUN_OFF"], tag=("CONTROL_BUTTON", "AUTO_RUN"))
        self.content_canvas.tag_bind('AUTO_RUN', '<Enter>', lambda x: self.displayGameDetail("Automatically skips to the next round", x))
        self.content_canvas.tag_bind('AUTO_RUN', '<Button-1>', self.toggleAutoRun)

        self.speed_mod_list = [1,2,4]
        self.speed_mod_ptr = 0
        self.content_canvas.create_image(special_bar_x*6.5, ((self.pyd.calc_height*8.667)//9), image=self.pyd.GAME_IMAGE_DICT["TIME_1"], tag=("CONTROL_BUTTON", "SPEED_MOD"))
        self.content_canvas.tag_bind('SPEED_MOD', '<Enter>', lambda x: self.displayGameDetail("Speeds up the gameplay!", x))
        self.content_canvas.tag_bind('SPEED_MOD', '<Button-1>', self.stepSpeed)


        self.help_toggled = False
        self.content_canvas.create_image(special_bar_x*4.667, ((self.pyd.calc_height*8)//9), image=self.pyd.GAME_IMAGE_DICT["HELP_BUTTON"], tag=("CONTROL_BUTTON", "HELP_BUTTON"))
        self.content_canvas.tag_bind('HELP_BUTTON', '<Button-1>', self.toggleHelp)
        self.content_canvas.tag_bind('HELP_BUTTON', '<Enter>', lambda x: self.displayGameDetail("Opens the help view", x))
        
        self.chat_toggled = False
        if self.gamemode_selected != "MULTIPLAYER":
            self.content_canvas.create_image(special_bar_x*4.667, ((self.pyd.calc_height*7.334)//9), image=self.pyd.GAME_IMAGE_DICT["CHAT_BUTTON_DISABLED"], tag=("CONTROL_BUTTON", "CHAT_BUTTON"))
            self.content_canvas.tag_bind('CHAT_BUTTON', '<Enter>', lambda x: self.displayGameDetail("Opens the chat dialogue", x))
        else:
            self.content_canvas.create_image(special_bar_x*4.667, ((self.pyd.calc_height*7.334)//9), image=self.pyd.GAME_IMAGE_DICT["CHAT_BUTTON"], tag=("CONTROL_BUTTON", "CHAT_BUTTON"))
            self.content_canvas.tag_bind('CHAT_BUTTON', '<Enter>', lambda x: self.displayGameDetail("Opens the chat dialogue", x))
            self.content_canvas.tag_bind('CHAT_BUTTON', '<Button-1>', self.toggleChat)

        self.content_canvas.create_image(special_bar_x*4.667, ((self.pyd.calc_height*8.667)//9), image=self.pyd.GAME_IMAGE_DICT["PAUSE_BUTTON"], tag=("CONTROL_BUTTON", "PAUSE_BUTTON"))
        self.content_canvas.tag_bind('PAUSE_BUTTON', '<Button-1>', self.togglePause)
        self.content_canvas.tag_bind('PAUSE_BUTTON', '<Enter>', lambda x: self.displayGameDetail("Pauses the game", x))


        #Abilities area with 6 unique mechanics
        ab1x, ab1y = special_bar_x*0.5, ((self.pyd.calc_height*7.5)//9)
        self.content_canvas.create_image(ab1x, ab1y, image=self.pyd.GAME_IMAGE_DICT["ABILITY_1"], tag=("CONTROL_BUTTON", "USE_ABILITY_1", "ABILITY_BUTTON"))
        self.content_canvas.create_image(ab1x, ab1y, image=self.pyd.GAME_IMAGE_DICT["ABILITY_COOLDOWN_4"], state="hidden", tag=("CONTROL_BUTTON", "ABILITY_COOLDOWN_1"))
        self.content_canvas.create_image(ab1x, ab1y, image=self.pyd.GAME_IMAGE_DICT["ABILITY_LOCK_OVERLAY"], tag=("CONTROL_BUTTON", "UNLOCK_ABILITY_1"))
        self.content_canvas.create_text(ab1x*0.895, ab1y*1.0375, text=self.pyd.ABILITY_INFO["1"]["cost"], font=(self.pyd.default_font, self.pyd.fontScale(14)), fill="white", tag=("CONTROL_BUTTON", "UNLOCK_ABILITY_1", "COST_TEXT_1"))
        self.content_canvas.tag_bind('UNLOCK_ABILITY_1', '<ButtonPress-1>', lambda x: self.unlockAbility(1, x))
        self.content_canvas.tag_bind('USE_ABILITY_1', '<ButtonPress-1>', lambda x: self.useAbility(1, x))
        self.content_canvas.tag_bind('UNLOCK_ABILITY_1', '<Enter>', lambda x: self.displayGameDetail("Unlock "+self.pyd.ABILITY_INFO["1"]["name"], x))
        self.content_canvas.tag_bind('USE_ABILITY_1', '<Enter>', lambda x: self.displayGameDetail(self.pyd.ABILITY_INFO["1"]["description"], x))

        ab2x, ab2y = special_bar_x*1.5, ((self.pyd.calc_height*7.5)//9)
        self.content_canvas.create_image(ab2x, ab2y, image=self.pyd.GAME_IMAGE_DICT["ABILITY_2"], tag=("CONTROL_BUTTON", "USE_ABILITY_2", "ABILITY_BUTTON"))
        self.content_canvas.create_image(ab2x, ab2y, image=self.pyd.GAME_IMAGE_DICT["ABILITY_COOLDOWN_4"], state="hidden", tag=("CONTROL_BUTTON", "ABILITY_COOLDOWN_2"))
        self.content_canvas.create_image(ab2x, ab2y, image=self.pyd.GAME_IMAGE_DICT["ABILITY_LOCK_OVERLAY"], tag=("CONTROL_BUTTON", "UNLOCK_ABILITY_2"))
        self.content_canvas.create_text(ab2x*0.945, ab2y*1.0375, text=self.pyd.ABILITY_INFO["2"]["cost"], font=(self.pyd.default_font, self.pyd.fontScale(14)), fill="white", tag=("CONTROL_BUTTON", "UNLOCK_ABILITY_2", "COST_TEXT_2"))
        self.content_canvas.tag_bind('UNLOCK_ABILITY_2', '<ButtonPress-1>', lambda x: self.unlockAbility(2, x))
        self.content_canvas.tag_bind('USE_ABILITY_2', '<ButtonPress-1>', lambda x: self.useAbility(2, x))
        self.content_canvas.tag_bind('UNLOCK_ABILITY_2', '<Enter>', lambda x: self.displayGameDetail("Unlock "+self.pyd.ABILITY_INFO["2"]["name"], x))
        self.content_canvas.tag_bind('USE_ABILITY_2', '<Enter>', lambda x: self.displayGameDetail(self.pyd.ABILITY_INFO["2"]["description"], x))

        ab3x, ab3y = special_bar_x*2.5, ((self.pyd.calc_height*7.5)//9)
        self.content_canvas.create_image(ab3x, ab3y, image=self.pyd.GAME_IMAGE_DICT["ABILITY_3"], tag=("CONTROL_BUTTON", "USE_ABILITY_3", "ABILITY_BUTTON"))
        self.content_canvas.create_image(ab3x, ab3y, image=self.pyd.GAME_IMAGE_DICT["ABILITY_COOLDOWN_4"], state="hidden", tag=("CONTROL_BUTTON", "ABILITY_COOLDOWN_3"))
        self.content_canvas.create_image(ab3x, ab3y, image=self.pyd.GAME_IMAGE_DICT["ABILITY_LOCK_OVERLAY"], tag=("CONTROL_BUTTON", "UNLOCK_ABILITY_3"))
        self.content_canvas.create_text(ab3x*0.97, ab3y*1.0375, text=self.pyd.ABILITY_INFO["3"]["cost"], font=(self.pyd.default_font, self.pyd.fontScale(14)), fill="white", tag=("CONTROL_BUTTON", "UNLOCK_ABILITY_3", "COST_TEXT_3"))
        self.content_canvas.tag_bind('UNLOCK_ABILITY_3', '<ButtonPress-1>', lambda x: self.unlockAbility(3, x))
        self.content_canvas.tag_bind('USE_ABILITY_3', '<ButtonPress-1>', lambda x: self.useAbility(3, x))
        self.content_canvas.tag_bind('UNLOCK_ABILITY_3', '<Enter>', lambda x: self.displayGameDetail("Unlock "+self.pyd.ABILITY_INFO["3"]["name"], x))
        self.content_canvas.tag_bind('USE_ABILITY_3', '<Enter>', lambda x: self.displayGameDetail(self.pyd.ABILITY_INFO["3"]["description"], x))

        ab4x, ab4y = special_bar_x*0.5, ((self.pyd.calc_height*8.5)//9)
        self.content_canvas.create_image(ab4x, ab4y, image=self.pyd.GAME_IMAGE_DICT["ABILITY_4"], tag=("CONTROL_BUTTON", "USE_ABILITY_4", "ABILITY_BUTTON"))
        self.content_canvas.create_image(ab4x, ab4y, image=self.pyd.GAME_IMAGE_DICT["ABILITY_COOLDOWN_4"], state="hidden", tag=("CONTROL_BUTTON", "ABILITY_COOLDOWN_4"))
        self.content_canvas.create_image(ab4x, ab4y, image=self.pyd.GAME_IMAGE_DICT["ABILITY_LOCK_OVERLAY"], tag=("CONTROL_BUTTON", "UNLOCK_ABILITY_4"))
        self.content_canvas.create_text(ab4x*0.9, ab4y*1.0325, text=self.pyd.ABILITY_INFO["4"]["cost"], font=(self.pyd.default_font, self.pyd.fontScale(14)), fill="white", tag=("CONTROL_BUTTON", "UNLOCK_ABILITY_4", "COST_TEXT_4"))
        self.content_canvas.tag_bind('UNLOCK_ABILITY_4', '<ButtonPress-1>', lambda x: self.unlockAbility(4, x))
        self.content_canvas.tag_bind('USE_ABILITY_4', '<ButtonPress-1>', lambda x: self.useAbility(4, x))
        self.content_canvas.tag_bind('UNLOCK_ABILITY_4', '<Enter>', lambda x: self.displayGameDetail("Unlock "+self.pyd.ABILITY_INFO["4"]["name"], x))
        self.content_canvas.tag_bind('USE_ABILITY_4', '<Enter>', lambda x: self.displayGameDetail(self.pyd.ABILITY_INFO["4"]["description"], x))

        ab5x, ab5y = special_bar_x*1.5, ((self.pyd.calc_height*8.5)//9)
        self.content_canvas.create_image(ab5x, ab5y, image=self.pyd.GAME_IMAGE_DICT["ABILITY_5"], tag=("CONTROL_BUTTON", "USE_ABILITY_5", "ABILITY_BUTTON"))
        self.content_canvas.create_image(ab5x, ab5y, image=self.pyd.GAME_IMAGE_DICT["ABILITY_COOLDOWN_4"], state="hidden", tag=("CONTROL_BUTTON", "ABILITY_COOLDOWN_5"))
        self.content_canvas.create_image(ab5x, ab5y, image=self.pyd.GAME_IMAGE_DICT["ABILITY_LOCK_OVERLAY"], tag=("CONTROL_BUTTON", "UNLOCK_ABILITY_5"))
        self.content_canvas.create_text(ab5x*0.945, ab5y*1.0325, text=self.pyd.ABILITY_INFO["5"]["cost"], font=(self.pyd.default_font, self.pyd.fontScale(14)), fill="white", tag=("CONTROL_BUTTON", "UNLOCK_ABILITY_5", "COST_TEXT_5"))
        self.content_canvas.tag_bind('UNLOCK_ABILITY_5', '<ButtonPress-1>', lambda x: self.unlockAbility(5, x))
        self.content_canvas.tag_bind('USE_ABILITY_5', '<ButtonPress-1>', lambda x: self.useAbility(5, x))
        self.content_canvas.tag_bind('UNLOCK_ABILITY_5', '<Enter>', lambda x: self.displayGameDetail("Unlock "+self.pyd.ABILITY_INFO["5"]["name"], x))
        self.content_canvas.tag_bind('USE_ABILITY_5', '<Enter>', lambda x: self.displayGameDetail(self.pyd.ABILITY_INFO["5"]["description"], x))

        ab6x, ab6y = special_bar_x*2.5, ((self.pyd.calc_height*8.5)//9)
        self.content_canvas.create_image(ab6x, ab6y, image=self.pyd.GAME_IMAGE_DICT["ABILITY_6"], tag=("CONTROL_BUTTON", "USE_ABILITY_6", "ABILITY_BUTTON"))
        self.content_canvas.create_image(ab6x, ab6y, image=self.pyd.GAME_IMAGE_DICT["ABILITY_COOLDOWN_4"], state="hidden", tag=("CONTROL_BUTTON", "ABILITY_COOLDOWN_6"))
        self.content_canvas.create_image(ab6x, ab6y, image=self.pyd.GAME_IMAGE_DICT["ABILITY_LOCK_OVERLAY"], tag=("CONTROL_BUTTON", "UNLOCK_ABILITY_6"))
        self.content_canvas.create_text(ab6x*0.97, ab6y*1.0325, text=self.pyd.ABILITY_INFO["6"]["cost"], font=(self.pyd.default_font, self.pyd.fontScale(14)), fill="white", tag=("CONTROL_BUTTON", "UNLOCK_ABILITY_6", "COST_TEXT_6"))
        self.content_canvas.tag_bind('UNLOCK_ABILITY_6', '<ButtonPress-1>', lambda x: self.unlockAbility(6, x))
        self.content_canvas.tag_bind('USE_ABILITY_6', '<ButtonPress-1>', lambda x: self.useAbility(6, x))
        self.content_canvas.tag_bind('UNLOCK_ABILITY_6', '<Enter>', lambda x: self.displayGameDetail("Unlock "+self.pyd.ABILITY_INFO["6"]["name"], x))
        self.content_canvas.tag_bind('USE_ABILITY_6', '<Enter>', lambda x: self.displayGameDetail(self.pyd.ABILITY_INFO["6"]["description"], x))

        self.content_canvas.tag_bind('CONTROL_BUTTON', '<Leave>', lambda x: self.displayGameDetail(self.pyd.DEFAULT_GAME_DETAIL_DESCRIPTION, x))

        self.content_canvas.create_text(content_x*1.05, (self.pyd.calc_height*8)//9, text=self.pyd.DEFAULT_GAME_DETAIL_DESCRIPTION, font=(self.pyd.default_font, self.pyd.fontScale(12)), width=special_bar_x*1.1, fill="white", tag=("GAME_DETAIL"), state="disabled")

        #Overseer function to manage game events
        thr.start_new_thread(self.overseer, ())


    #* Gameplay specific methods
    def overseer(self):
        #Oversee and manage events
        self.overseeing = True
        
        #Initial variables
        self.start_time = time.time()
        self.round_over = False
        self.force_round_start = False
        self.pyd.pause_toggle_state = False

        start_pause_time = 0
        resume_triggered = False
        round_triggered = False

        #Send server client join message
        if self.client.ping != "Not connected":
            self.client.sendMsg("{} joined".format(self.pyd.CLIENT_NAME), "SERVER")

        #Event handle loop
        while self.overseeing:
            self.updateAllStatistics()

            #Display base upgrade icon if money high enough
            if self.base_object.level+1 <= 2:
                if self.pyd.money >= self.base_object.money_level_requirements[self.base_object.level]:
                    self.map_canvas.itemconfigure("UPGRADE_BASE_TEXT", text="{}".format(self.base_object.money_level_requirements[self.base_object.level]))
                    self.map_canvas.itemconfigure("UPGRADE_BASE", state="disabled")
                else:
                    self.map_canvas.itemconfigure("UPGRADE_BASE", state="hidden")
            else:
                self.map_canvas.itemconfigure("UPGRADE_BASE", state="hidden")
            
            current_time = time.time()-self.start_time

            #Update DRP with pause status
            if self.pyd.pause_toggle_state:
                self.pyd.updateDRP(state="PAUSED | {}".format(self.gamemode_selected.lower().capitalize()), detail="Playing on '{}'".format(self.loaded_map["name"]))
            else:
                self.pyd.updateDRP(state="Round {} | {}".format(int(self.pyd.current_round+1), self.gamemode_selected.lower().capitalize()), detail="Playing on '{}'".format(self.loaded_map["name"]))

            #If pause triggered, modify start time
            if self.pyd.pause_toggle_state == resume_triggered: 

                #Sync remaining time to round start when paused
                resume_triggered = False
                start_pause_time = current_time

                self.time_before_round_trigger = self.pyd.max_pre_round_time-current_time
                self.time_before_round_trigger = max(0, self.time_before_round_trigger) #prevent minus time

                #If round ends trigger new start time
                if self.round_over: 
                    self.incrementRound()
                    if self.pyd.current_round == self.pyd.max_rounds:
                        self.gameOver(True)

                    self.round_over = False

                    round_triggered = False
                    self.start_time = time.time()
                    self.time_before_round_trigger = self.pyd.max_pre_round_time #prevents small blip of previous time
                    self.force_round_start = False

                #Force round to start by setting time remaining to 0
                if self.force_round_start: 
                    self.round_over = False
                    self.time_before_round_trigger = 0

                #Trigger round to start
                if self.time_before_round_trigger  == 0 and not round_triggered: 
                    thr.start_new_thread(self.startRound, ())
                    round_triggered = True

                #Update time statistic
                self.setTime(self.time_before_round_trigger)

            else:
                #Sync start time with when pause was triggered
                self.start_time = time.time()-start_pause_time

            #Rate limiter
            time.sleep(1/self.pyd.FPS) 

    def updateAllStatistics(self):
        #Update statistics panel
        self.updateBaseHealth()
        self.content_canvas.itemconfigure("MONEY_STATISTIC", text=int(self.pyd.money))
        self.content_canvas.itemconfigure("UNIT_KILL_STATISTIC", text=int(self.pyd.units_killed))


    #* Round methods
    def incrementRound(self, amount=1):
        #Increment round and update statistic
        self.pyd.current_round += amount
        self.content_canvas.itemconfigure("ROUND_STATISTIC", text=int(self.pyd.current_round))

    def endRound(self, event=""):
        if event != "": # log event info
            self.pyd.log("endRound() from event {} at ({},{})".format(event.type, event.x, event.y))

        #End round (see overseer function)
        self.round_over = True


    #* Money methods
    def reduceMoney(self, amount):
        #Reduce money and update statistic
        self.pyd.money -= amount
        self.content_canvas.itemconfigure("MONEY_STATISTIC", text=int(self.pyd.money))

    def addMoney(self, amount):
        #Add money and update statistic
        self.pyd.money += amount
        self.content_canvas.itemconfigure("MONEY_STATISTIC", text=int(self.pyd.money))


    #* Time methods
    def setTime(self, amount):
        #Set time remaining and update statistic
        self.pyd.time_left = amount
        self.content_canvas.itemconfigure("TIME_STATISTIC", text="{:0>2.0f}:{:0>2.0f}".format(int(self.pyd.time_left+0.5)//60, int(self.pyd.time_left+0.5) % 60))
    

    #* Unit kill methods
    def incrementUnitKills(self, amount=1):
        #Increment unit kills and update statistic
        self.pyd.units_killed += amount
        self.content_canvas.itemconfigure("UNIT_KILL_STATISTIC", text=int(self.pyd.units_killed))

    def setUnitKills(self, amount):
        #Set unit kills and update statistic
        self.pyd.units_killed = amount
        self.content_canvas.itemconfigure("UNIT_KILL_STATISTIC", text=int(self.pyd.units_killed))


    #* Base health methods
    def updateBaseHealth(self):
        #Check if base dead
        if self.pyd.current_base_health <= 0:
            #Trigger game over
            self.pyd.game_over = True
            thr.start_new_thread(self.gameOver, (False, ))

        #Calculate and display health information
        health_percentage = max(0, self.pyd.current_base_health/self.pyd.max_base_health)
        
        #Health bar
        n=10
        t = 1/(1 + math.e**((n/2)-n*health_percentage)) #sigmoid modifier
        rg = self.pyd.linearInterpolation2D((255,0), (0,255), t)
        self.content_canvas.itemconfigure("BASE_HEALTH_BAR", fill='#%02X%02X%02X' % (int(rg[0]), int(rg[1]), 0))
        
        hb_coords = self.healthbar_coords
        healthbar_x = (1 - health_percentage) * hb_coords[0] + health_percentage * hb_coords[2]
        self.content_canvas.coords("BASE_HEALTH_BAR", hb_coords[:2]+[healthbar_x]+[hb_coords[3]])
        
        #Health text
        self.content_canvas.itemconfigure("HEALTH_STATISTIC", text="{}/{}".format(max(0, int(self.pyd.current_base_health)), self.pyd.max_base_health))


    #* Game UI methods
    def infoTowerPanel(self, panel_id, close=False):
        #Display tower info card
        if close:
            self.content_canvas.itemconfigure("TOWER_INFO_{}".format(panel_id), state="hidden")
        else:
            self.content_canvas.itemconfigure("TOWER_INFO_{}".format(panel_id), state="normal")

    def chatLog(self, msg):
        #Display message to chat log, if message has changed
        if self.prev_msg != "[{}][{}] {}\n".format(time.strftime("%H:%m:%S"), self.client.new_msg["sender"], self.client.new_msg["message"]):
            self.prev_msg = "[{}][{}] {}\n".format(time.strftime("%H:%m:%S"), self.client.new_msg["sender"], self.client.new_msg["message"])
            self.chat_log.config(state="normal")
            self.chat_log.insert(tk.END, self.prev_msg)
            self.chat_log.config(state="disabled")
            self.chat_log.see(tk.END)

    def toggleAutoRun(self, event=""):
        if event != "": # log event info
            self.pyd.log("toggleAutoRun() from event {} at ({},{})".format(event.type, event.x, event.y))

        #Toggle auto run
        if self.auto_run:
            self.auto_run = False
            self.pyd.max_pre_round_time = self.pyd.DEFAULT_PRE_ROUND_TIME
            self.content_canvas.itemconfigure('AUTO_RUN', image=self.pyd.GAME_IMAGE_DICT["AUTO_RUN_OFF"])#update UI
        else:
            self.auto_run = True
            self.pyd.max_pre_round_time = 0.1
            self.content_canvas.itemconfigure('AUTO_RUN', image=self.pyd.GAME_IMAGE_DICT["AUTO_RUN_ON"])#update UI

    def stepSpeed(self, event=""):
        if event != "": # log event info
            self.pyd.log("stepSpeed() from event {} at ({},{})".format(event.type, event.x, event.y))

        #Speed mod, cycle through 3 speeds
        if self.speed_mod_ptr >= len(self.speed_mod_list)-1:
            self.speed_mod_ptr = 0
        else:
            self.speed_mod_ptr += 1

        self.pyd.game_speed_mod = self.speed_mod_list[self.speed_mod_ptr]

        self.content_canvas.itemconfigure('SPEED_MOD', image=self.pyd.GAME_IMAGE_DICT["TIME_{}".format(self.speed_mod_list[self.speed_mod_ptr])])#update UI

    def sendMsg(self, msg):
        #Send a message and reset msg entry box
        if msg != "":
            self.msg_to_send.set("")
            if self.client.ping != "Not connected":
                self.client.sendMsg(msg, self.pyd.CLIENT_NAME)

    def toggleChat(self, event=""):
        #Toggle chat window
        if self.chat_toggled:
            self.chat_toggled = False
            self.content_canvas.itemconfigure("CHAT_BUTTON", image=self.pyd.GAME_IMAGE_DICT["CHAT_BUTTON"])#update UI
            self.content_canvas.itemconfigure("CHAT", state="hidden")

        else:
            self.chat_toggled = True
            self.content_canvas.itemconfigure("CHAT_BUTTON", image=self.pyd.GAME_IMAGE_DICT["CHAT_BUTTON_ACTIVE"])#update UI
            self.content_canvas.itemconfigure("CHAT", state="normal")

    def updateSliderPos(self, event):
        #Update slider image
        movement_x = -int(event.x-self.prev_x)*self.slider_sensitivity
        self.content_canvas.move("TOWER_SELECTION", movement_x, 0)
        self.content_canvas.coords("HORIZONTAL_SLIDER", min(760*self.pyd.x_scalefactor, max(80*self.pyd.x_scalefactor, event.x)), ((self.pyd.calc_height*6.63)//9))
        self.prev_x = event.x

    def alignPlaques(self, event=""):
        #Align plaques to original position
        current_x = self.content_canvas.coords("TOWER_SELECTION")[0]

        #If slider moves left past the original position
        if current_x > self.tower_plaque_start_x:

            #Update UI with aligned slider
            self.content_canvas.move("TOWER_SELECTION", self.tower_plaque_start_x-current_x, 0)
            self.prev_x = 80*self.pyd.x_scalefactor
            self.content_canvas.coords("HORIZONTAL_SLIDER", 80*self.pyd.x_scalefactor, ((self.pyd.calc_height*6.63)//9))

    def unlockAbility(self, ability_id, event=""):
        if event != "": # log event info
            self.pyd.log("unlockAbility({}) from event {} at ({},{})".format(ability_id, event.type, event.x, event.y))

        #! Validation
        #Validate ability unlock
        if self.pyd.last_unlocked_ability+1 == ability_id: #Bought in order
            if self.pyd.money >= self.pyd.ABILITY_INFO[str(ability_id)]["cost"]: #Enough money
                #Successful purchase of ability
                self.content_canvas.itemconfigure("UNLOCK_ABILITY_"+str(ability_id), state="hidden")
                self.reduceMoney(self.pyd.ABILITY_INFO[str(ability_id)]["cost"])
                self.pyd.last_unlocked_ability = ability_id

            else:
                #Handle not enough money
                self.pyd.log("NOT ENOUGH MONEY, BAL={} COST={}".format(self.pyd.money, self.pyd.ABILITY_INFO[str(ability_id)]["cost"]))

                thr.start_new_thread(self.highlightText, ("red", ability_id))

        else:
            #Handle not purchased in order
            self.pyd.log("NOT IN ORDER, NEXT SHOULD BE {}".format(self.pyd.last_unlocked_ability+1))

            thr.start_new_thread(self.highlightText, ("green", self.pyd.last_unlocked_ability+1))

    def highlightText(self, colour, tag, pretag="COST_TEXT_"):
        #Display red followed by default colour to alert attention
        self.content_canvas.itemconfigure(pretag+str(tag), fill=colour)
        time.sleep(0.3)
        self.content_canvas.itemconfigure(pretag+str(tag), fill="white")

    def cooldownThread(self, ability_id):
        #Get ability info from id
        ability_dict = self.pyd.ABILITY_INFO[str(ability_id)]
        prev_round = self.pyd.current_round

        #Display cooldown overlays over ability icons
        self.content_canvas.itemconfigure("ABILITY_COOLDOWN_"+str(ability_id), state="normal")
        if not ability_dict["once_per_round"]:
            #Display timer countdown and update images
            for i in range(4, 0, -1):
                self.content_canvas.itemconfigure("ABILITY_COOLDOWN_"+str(ability_id), image=self.pyd.GAME_IMAGE_DICT["ABILITY_COOLDOWN_"+str(i)])

                for i in range(self.pyd.FPS):
                    #Stop counting if game paused
                    while self.pyd.pause_toggle_state:
                        time.sleep(0.01)

                    time.sleep(ability_dict["cooldown_step"]/(self.pyd.game_speed_mod*self.pyd.FPS))

                    #Check if round over and prevent troops spawing if ability 1 active
                    if self.pyd.current_round != prev_round:
                        while self.ability1_active:
                            time.sleep(0.01)

                        self.content_canvas.itemconfigure("ABILITY_COOLDOWN_"+str(ability_id), state="hidden")
                        return
        else:
            #Display round only timer and update image
            self.content_canvas.itemconfigure("ABILITY_COOLDOWN_"+str(ability_id), image=self.pyd.GAME_IMAGE_DICT["ABILITY_COOLDOWN_ROUND"])
            
        #Wait to the end of the round
        while self.pyd.current_round == prev_round and ability_dict["once_per_round"]:
            time.sleep(0.01)

        #Remove cooldown overlay
        self.content_canvas.itemconfigure("ABILITY_COOLDOWN_"+str(ability_id), state="hidden")

    def useAbility(self, ability_id, event=""):
        if event != "": # log event info
            self.pyd.log("useAbility({}) from event {} at ({},{})".format(ability_id, event.type, event.x, event.y))

        #Ability threads
        def iceThread(self):
            #Disables the pause button
            self.content_canvas.itemconfigure("PAUSE_BUTTON", state="disabled")
            self.content_canvas.itemconfigure("HELP_BUTTON", state="disabled")

            #Create the overlay
            self.map_canvas.create_image(((self.pyd.calc_width*4.5)//16), ((self.pyd.calc_height*4.5)//9), image=self.pyd.GAME_IMAGE_DICT["FREEZE_OVERLAY"], state="disabled", tag=("FREEZE_OVERLAY"))
            
            #Stop the units
            for unit in self.pyd.wave:
                unit.stopped = True

            #Ability duration
            for i in range(self.pyd.FPS):
                time.sleep(5/(self.pyd.game_speed_mod*self.pyd.FPS))

            #Resume the units
            for unit in self.pyd.wave:
                unit.stopped = False

            #Remove the overlay and enable the pause button
            self.content_canvas.itemconfigure("PAUSE_BUTTON", state="normal")
            self.content_canvas.itemconfigure("HELP_BUTTON", state="normal")
            self.map_canvas.delete("FREEZE_OVERLAY")
            self.ability1_active = False

        def weaknessThread(self):
            #Change the units attributes
            for unit in self.pyd.wave:
                unit.strength /= 2
                unit.b = 200
                unit.reduceHealth(0)

            #Ability duration
            for i in range(self.pyd.FPS):
                time.sleep(20/(self.pyd.game_speed_mod*self.pyd.FPS))

            #Reset the units attributes
            for unit in self.pyd.wave:
                unit.strength *= 2
                unit.b = 0
                unit.reduceHealth(0)

        def deathwaveThread(self):
            #Death wave animation
            start_pos = (int(1.5*self.pyd.calc_height), self.pyd.calc_height//2)
            self.pyd.deathwave_coords = start_pos
            self.map_canvas.create_image(start_pos, image=self.pyd.GAME_IMAGE_DICT["DEATHWAVE_OVERLAY"], state="disabled", tag=("DEATHWAVE_OVERLAY"))
            thr.start_new_thread(self.pyd.glide, (self.map_canvas, "DEATHWAVE_OVERLAY", start_pos, (-self.pyd.calc_height, self.pyd.calc_height//2), 2))
            
            #Wait until wave animated
            while self.pyd.deathwave_coords != (-self.pyd.calc_height, self.pyd.calc_height//2):
                for unit in self.pyd.wave:
                    #Damage units that the wave has passed over
                    if unit.active:
                        if int(unit.pos[0]) < int(self.pyd.deathwave_coords[0])-(self.pyd.calc_height//2.2) and int(unit.pos[0]) > int(self.pyd.deathwave_coords[0])-(self.pyd.calc_height//1.5):
                            unit.reduceHealth(unit.health/16)

                time.sleep(1/self.pyd.FPS)
            
            #Delete death wave image
            self.map_canvas.delete("DEATHWAVE_OVERLAY")

        def moneyThread(self):
            #Change the units attributes
            for unit in self.pyd.wave:
                unit.value *= 3
                unit.force_colour = (225,225,0)
                unit.reduceHealth(0)

            #Ability duration
            for i in range(self.pyd.FPS):
                time.sleep(3/(self.pyd.game_speed_mod*self.pyd.FPS))

            #Reset the units attributes
            for unit in self.pyd.wave:
                unit.value /= 3
                unit.force_colour = False
                unit.reduceHealth(0)

        def towerThread(self):
            #Change the towers attributes
            projectiles_checked = []
            for tower in self.towers_placed:
                if tower.projectile not in projectiles_checked:
                    tower.projectile["damage"] *= 2
                    projectiles_checked.append(tower.projectile)

            #Ability duration
            for i in range(self.pyd.FPS):
                time.sleep(10/(self.pyd.game_speed_mod*self.pyd.FPS))

            #Reset the towers attributes
            projectiles_checked = []
            for tower in self.towers_placed:
                if tower.projectile not in projectiles_checked:
                    tower.projectile["damage"] /= 2
                    projectiles_checked.append(tower.projectile)

        #Use ability functions
        if ability_id == 1:
            #Freeze units
            self.ability1_active = True
            thr.start_new_thread(iceThread, (self, ))
            
        elif ability_id == 2:
            #Weakness potion
            thr.start_new_thread(weaknessThread, (self, ))
            
        elif ability_id == 3:
            #Death wave
            thr.start_new_thread(deathwaveThread, (self, ))
            
        elif ability_id == 4:
            #Unit value increase
            thr.start_new_thread(moneyThread, (self, ))

        elif ability_id == 5:
            #Castle health increase
            self.pyd.current_base_health += self.pyd.max_base_health//4
            self.pyd.current_base_health = min(self.pyd.max_base_health, self.pyd.current_base_health)
            self.updateBaseHealth()
            
        elif ability_id == 6:
            #Tower damage boost
            thr.start_new_thread(towerThread, (self, ))

        #Cooldown
        thr.start_new_thread(self.cooldownThread, (ability_id, ))

    def checkNoPathPresence(self, x, y):
        #For a given x,y check path presence
        sf = self.pyd.calc_height/self.map_size
        valid_path = self.loaded_map["valid_path"].split("/")[:-1]
        scaled_x, scaled_y = x/sf, y/sf
        found_path = False

        #Iterate through all path tiles, check if x,y is the same as mouse click
        for i in range(len(valid_path)):
            path_coords = valid_path[i].split(".")
            path_x, path_y = int(path_coords[0]), int(path_coords[1])
            if [path_x, path_y] == [int(scaled_x), int(scaled_y)]:
                found_path = True
                break
        
        #Add upper and lower bounds depending on tile selected
        if found_path:
            x_upper_bound = path_x+1
            x_lower_bound = path_x

            y_upper_bound = path_y+1
            y_lower_bound = path_y

            padding = 0.15
            texture_name = self.loaded_map["tiles"][self.map_size*path_x+path_y]["texture"] #get texture at x,y
            if texture_name == "MAP_PATH_X":
                y_upper_bound -= padding
                y_lower_bound += padding
            elif texture_name == "MAP_PATH_Y":
                x_upper_bound -= padding
                x_lower_bound += padding
            elif texture_name == "MAP_PATH_TR":
                y_lower_bound += padding
                x_upper_bound -= padding
            elif texture_name == "MAP_PATH_TL":
                x_lower_bound += padding
                y_lower_bound += padding
            elif texture_name == "MAP_PATH_BR":
                x_upper_bound -= padding
                y_upper_bound -= padding
            elif texture_name == "MAP_PATH_BL":
                y_upper_bound -= padding
                x_lower_bound += padding

            #Preventing placing of towers outside of padding
            if (scaled_x > x_lower_bound and scaled_x < x_upper_bound) and (scaled_y > y_lower_bound and scaled_y < y_upper_bound):
                return False

        return True

    def purchaseTower(self, tower_id):
        #Cancel all tower purchases
        for i in range(len(self.tower_dictionary)):
            self.cancelTowerPurchase(i)

        #Config UI with cancel button
        self.content_canvas.itemconfigure("TOWER_BUY_BUTTON_{}".format(tower_id), image=self.pyd.GAME_IMAGE_DICT["PANEL_CANCEL_BUTTON"])
        self.content_canvas.tag_bind("TOWER_BUY_{}".format(tower_id), "<Button-1>", lambda event, x=tower_id: self.cancelTowerPurchase(x))
        
        #Draw range preview when hovering over map
        if tower_id <= len(self.tower_dictionary):
            if self.pyd.money-self.tower_dictionary[tower_id]["attributes"]["cost"] >= 0: #check if tower can be purchased
                self.purchased_tower = self.tower_dictionary[tower_id]
                self.map_canvas.tag_bind("MAP_TILE", "<Motion>", self.updateRangePreview)
                self.map_canvas.tag_bind("MAP_TILE", "<Leave>", lambda e: self.map_canvas.itemconfigure("TOWER_RANGE_PREVIEW", state="hidden"))
            else:
                #Handle not enough money
                thr.start_new_thread(self.highlightText, ("red", tower_id, "TOWER_COST_"))
                self.cancelTowerPurchase(tower_id)

    def updateRangePreview(self, event=""):
        #Draw range of tower if purchased tower is not None
        if self.purchased_tower != None:
            #Scale range to map size
            sf = self.pyd.calc_height/self.map_size
            tower_range = self.purchased_tower["attributes"]["range"]
            self.map_canvas.coords("TOWER_RANGE_PREVIEW", event.x-(tower_range*sf), event.y-(tower_range*sf), event.x+(tower_range*sf), event.y+(tower_range*sf))
            self.map_canvas.itemconfigure("TOWER_RANGE_PREVIEW", state="disabled")

            #Check path presence and update preview colour
            if self.checkNoPathPresence(event.x, event.y):
                self.map_canvas.itemconfigure("TOWER_RANGE_PREVIEW", outline="black")
            else:
                self.map_canvas.itemconfigure("TOWER_RANGE_PREVIEW", outline="red")

    def cancelTowerPurchase(self, tower_id, event=""):
        if event != "": # log event info
            self.pyd.log("cancelTowerPurchase({}) from event {} at ({},{})".format(tower_id, event.type, event.x, event.y))
        
        #Update tower panel with initial buttons
        self.content_canvas.itemconfigure("TOWER_BUY_BUTTON_{}".format(tower_id), image=self.pyd.GAME_IMAGE_DICT["PANEL_BUY_BUTTON"])
        self.content_canvas.tag_bind("TOWER_BUY_{}".format(tower_id), "<Button-1>", lambda event, x=tower_id: self.purchaseTower(x))

        #Unbind any range previewing
        self.map_canvas.tag_unbind("MAP_TILE", "ALL")
        self.map_canvas.itemconfigure("TOWER_RANGE_PREVIEW", state="hidden")
        self.purchased_tower = None

    def placeTower(self, event):
        #Place a tower if valid

        #! Validation
        x,y = event.x, event.y
        if self.purchased_tower != None and self.checkNoPathPresence(x,y): #Check that a tower is purchased and no path is underneath the clicked area

            #Add tower object to towers_placed list which keeps track on placed towers
            self.towers_placed.append(Tower(self.map_canvas, (x,y), self.pyd.GAME_IMAGE_DICT["TOWER_"+self.purchased_tower["texture_name"]], self.purchased_tower["attributes"], self.pyd.calc_height/self.map_size, self.pyd, tag="TOWER"+str(x)+str(y)))
            thr.start_new_thread(self.towers_placed[-1].go, ()) #activate the tower
            self.reduceMoney(self.purchased_tower["attributes"]["cost"]) #reduce money

            self.pyd.log("tower placed at ({}, {})".format(x,y)) #log event

            #Check that user has money for another tower and if not cancel further tower purchases 
            if self.pyd.money-self.purchased_tower["attributes"]["cost"] < 0:
                tower_id = self.tower_dictionary.index(self.purchased_tower)
                thr.start_new_thread(self.highlightText, ("red", tower_id, "TOWER_COST_"))
                self.cancelTowerPurchase(tower_id)

    def displayGameDetail(self, description="", event=""):
        if event != "": # log event info
            self.pyd.log("displayGameDetail({}) from event {} at ({},{})".format(description, event.type, event.x, event.y))

        #Display game details
        self.content_canvas.itemconfigure("GAME_DETAIL", text=description)

    def togglePause(self, event=""):
        if event != "": # log event info
            self.pyd.log("togglePause() from event {} at ({},{})".format(event.type, event.x, event.y))

        #Stop all units
        for unit in self.pyd.wave:
            unit.toggleStop()

        #Toggle pause state
        if self.pyd.pause_toggle_state:
            self.pyd.pause_toggle_state = False

            #Update UI elements enabling disabled features
            self.map_canvas.delete("PAUSE_OVERLAY")
            self.map_canvas.delete("BACK_TITLE_BUTTON")
            self.content_canvas.itemconfigure("PAUSE_BUTTON", image=self.pyd.GAME_IMAGE_DICT["PAUSE_BUTTON"])
            self.content_canvas.itemconfigure("TIME_STATISTIC", fill="black")
            self.content_canvas.itemconfigure("ABILITY_BUTTON", state="normal")
            self.content_canvas.itemconfigure("ABILITY_BUTTON", state="normal")
            self.content_canvas.itemconfigure("HELP_BUTTON", state="normal")
        else:
            #Update UI elements disabling enabled features
            self.pyd.pause_toggle_state = True
            self.map_canvas.create_image(((self.pyd.calc_width*4.5)//16), ((self.pyd.calc_height*4.5)//9), image=self.pyd.GAME_IMAGE_DICT["PAUSE_MAP_OVERLAY"], tag=("PAUSE_OVERLAY"))
            self.content_canvas.itemconfigure("PAUSE_BUTTON", image=self.pyd.GAME_IMAGE_DICT["PAUSE_BUTTON_ACTIVE"])
            self.content_canvas.itemconfigure("TIME_STATISTIC", fill="#c10c0c")
            self.content_canvas.itemconfigure("ABILITY_BUTTON", state="disabled")
            self.content_canvas.itemconfigure("HELP_BUTTON", state="disabled")

            #Animate back to title screen
            start_pos = (self.pyd.calc_height//2, 1.2*self.pyd.calc_height)
            self.map_canvas.create_image(start_pos, image=self.pyd.GAME_IMAGE_DICT["BACK_TITLE_BUTTON"], tag=("BACK_TITLE_BUTTON"))
            self.map_canvas.tag_bind("BACK_TITLE_BUTTON", '<ButtonPress-1>',self.exitToTitleScreen)
            thr.start_new_thread(self.pyd.glide,(self.map_canvas, "BACK_TITLE_BUTTON", start_pos, (self.pyd.calc_height//2, ((self.pyd.calc_height*8)//9)), 1))

    def toggleHelp(self, event=""):
        if event != "": # log event info
            self.pyd.log("toggleHelp() from event {} at ({},{})".format(event.type, event.x, event.y))

        #Stop all units
        for unit in self.pyd.wave:
            unit.toggleStop()

        #Toggle pause state
        if self.pyd.pause_toggle_state:
            self.pyd.pause_toggle_state = False

            #Update UI elements enabling disabled features                    
            self.map_canvas.delete("HELP_OVERLAY")
            self.content_canvas.itemconfigure("HELP_BUTTON", image=self.pyd.GAME_IMAGE_DICT["HELP_BUTTON"])
            self.content_canvas.itemconfigure("TIME_STATISTIC", fill="black")
            self.content_canvas.itemconfigure("ABILITY_BUTTON", state="normal")
            self.content_canvas.itemconfigure("ABILITY_BUTTON", state="normal")
            self.content_canvas.itemconfigure("PAUSE_BUTTON", state="normal")
        else:
            #Update UI elements disabling enabled features                
            self.pyd.pause_toggle_state = True
            self.map_canvas.create_image(((self.pyd.calc_width*4.5)//16), ((self.pyd.calc_height*4.5)//9), image=self.pyd.GAME_IMAGE_DICT["HELP_OVERLAY"], tag=("HELP_OVERLAY"))
            self.content_canvas.itemconfigure("HELP_BUTTON", image=self.pyd.GAME_IMAGE_DICT["HELP_BUTTON_ACTIVE"])
            self.content_canvas.itemconfigure("TIME_STATISTIC", fill="#c10c0c")
            self.content_canvas.itemconfigure("ABILITY_BUTTON", state="disabled")
            self.content_canvas.itemconfigure("PAUSE_BUTTON", state="disabled")
            
    def forceRoundStart(self, event=""):
        if event != "": # log event info
            self.pyd.log("forceRoundStart() from event {} at ({},{})".format(event.type, event.x, event.y))

        #Force round start and resume gameplay 
        self.content_canvas.itemconfigure("PLAY_BUTTON", image=self.pyd.GAME_IMAGE_DICT["PLAY_BUTTON_ON"])
        self.force_round_start = True
        if self.pyd.pause_toggle_state:
            self.togglePause()

    def exitToTitleScreen(self, event=""):
        if event != "": # log event info
            self.pyd.log("exitToTitleScreen() from event {} at ({},{})".format(event.type, event.x, event.y))

        #Send disconnect message to lobby
        if self.client.ping != "Not connected":
            self.client.sendMsg("{} left".format(self.pyd.CLIENT_NAME), "SERVER")
            
            #Disconnect from lobby
            self.client.disconnectRequest()

        #Stop event handling
        self.lobby_selected = None
        self.overseeing = False

        #Kill all unit and tower objects
        for unit in self.pyd.wave:
            thr.start_new_thread(unit.die, ())

        for tower in self.towers_placed:
            thr.start_new_thread(tower.sell, ())

        self.base_object.sell() #destroy base

        #Update new badges if unlocked any
        self.title_canvas.itemconfigure("{}_BADGE".format(self.gamemode_selected), image=self.checkBadge(self.gamemode_selected))

        #Switch frames
        self.gameplay_area.pack_forget()
        self.title_area.pack()

        #Update DRP 
        self.pyd.updateDRP(state="On the title screen", detail="Playing PyDefence")
        

    #* Game methods
    def gameOver(self, won=True):

        self.pyd.log("gameOver(won={}".format(won))

        #Stop all units still alive
        for unit in self.pyd.wave:
            unit.toggleStop()

        #Stop event handling
        self.overseeing = False

        #Disable game UI buttons
        self.content_canvas.itemconfigure("PAUSE_BUTTON", state="disabled")
        self.content_canvas.itemconfigure("HELP_BUTTON", state="disabled")
        self.content_canvas.itemconfigure("PLAY_BUTTON", state="disabled")
        self.content_canvas.itemconfigure("ABILITY_BUTTON", state="disabled")
        
        #Animate overlay
        start_pos = (self.pyd.calc_height//2, -self.pyd.calc_height)
        self.map_canvas.create_image(start_pos, image=self.pyd.GAME_IMAGE_DICT["GAMEOVER_OVERLAY"], state="normal", tag=("GAMEOVER_OVERLAY", "GAMEOVER_FEATURES"))
        thr.start_new_thread(self.pyd.glide,(self.map_canvas, "GAMEOVER_OVERLAY", start_pos, (self.pyd.calc_height//2, self.pyd.calc_height//2), 1))

        time.sleep(0.2)

        #Animate logo
        start_pos = (self.pyd.calc_height//2, -self.pyd.calc_height)
        self.map_canvas.create_image(start_pos, image=self.pyd.GAME_IMAGE_DICT["GAMEOVER_LOGO"], state="disabled", tag=("GAMEOVER_LOGO", "GAMEOVER_FEATURES"))
        thr.start_new_thread(self.pyd.glide,(self.map_canvas, "GAMEOVER_LOGO", start_pos, (self.pyd.calc_height//2, ((self.pyd.calc_height*2)//9)), 3))


        #Score logo
        start_pos = (-self.pyd.calc_height, ((self.pyd.calc_height*6.25)//9))
        self.map_canvas.create_text(start_pos, text="Score: {:.0f}".format(self.calcScore()), font=(self.pyd.default_font, self.pyd.fontScale(48)), fill="white", state="disabled", tag=("GAME_SCORE", "GAMEOVER_FEATURES"))
        thr.start_new_thread(self.pyd.glide,(self.map_canvas, "GAME_SCORE", start_pos, (self.pyd.calc_height//2, ((self.pyd.calc_height*6.25)//9)), 4))

        #Animate content, for win or loss
        if won:
            #Update DRP to win status
            self.pyd.updateDRP(state="Won on {}".format(self.gamemode_selected.lower().capitalize()), detail="Playing on '{}'".format(self.loaded_map["name"]))
            
            #Store badge unlocked in file
            self.pyd.GAME_DATA["badges_unlocked"].append(self.gamemode_selected)
            open(self.pyd.GAME_DATA_PATH, 'w').write(self.pyd.encode_85(json.dumps(self.pyd.GAME_DATA)))


            #Animate logo
            start_pos = (self.pyd.calc_height//2, -self.pyd.calc_height)
            self.map_canvas.create_image(start_pos, image=self.pyd.GAME_IMAGE_DICT["GAMEOVER_LOGO"], state="disabled", tag=("GAMEOVER_LOGO", "GAMEOVER_FEATURES"))
            thr.start_new_thread(self.pyd.glide,(self.map_canvas, "GAMEOVER_LOGO", start_pos, (self.pyd.calc_height//2, ((self.pyd.calc_height*2)//9)), 3))

            time.sleep(0.5)

            start_pos = (self.pyd.calc_height*2, ((self.pyd.calc_height*2.75)//9))
            self.map_canvas.create_image(start_pos, image=eval("self.pyd.{}_BADGE".format(self.gamemode_selected)), state="disabled", tag=("BADGE_WON", "GAMEOVER_FEATURES"))
            thr.start_new_thread(self.pyd.glide,(self.map_canvas, "BADGE_WON", start_pos, ((self.pyd.calc_height*5)//8, ((self.pyd.calc_height*2.75)//9)), 3))

            time.sleep(0.5)

            #Animate game won image
            start_pos = (-self.pyd.calc_height, self.pyd.calc_height//2)
            self.map_canvas.create_image(start_pos, image=self.pyd.GAME_IMAGE_DICT["GAMEOVER_WON"], state="disabled", tag=("GAMEOVER_WON", "GAMEOVER_FEATURES"))
            thr.start_new_thread(self.pyd.glide,(self.map_canvas, "GAMEOVER_WON", start_pos, (self.pyd.calc_height//2, self.pyd.calc_height//2), 3))

            time.sleep(3)

            #Animate back to title screen and continue game
            start_pos = (self.pyd.calc_height//4, 2*self.pyd.calc_height)
            self.map_canvas.create_image(start_pos, image=self.pyd.GAME_IMAGE_DICT["BACK_TITLE_BUTTON"], tag=("BACK_TITLE_BUTTON", "GAMEOVER_FEATURES"))
            self.map_canvas.tag_bind("BACK_TITLE_BUTTON", '<ButtonPress-1>',self.exitToTitleScreen)
            thr.start_new_thread(self.pyd.glide,(self.map_canvas, "BACK_TITLE_BUTTON", start_pos, (self.pyd.calc_height//4, ((self.pyd.calc_height*8)//9)), 1))

            start_pos = ((self.pyd.calc_height*3)//4, 2*self.pyd.calc_height)
            self.map_canvas.create_image(start_pos, image=self.pyd.GAME_IMAGE_DICT["CONTINUE_GAME_BUTTON"], tag=("CONTINUE_GAME_BUTTON", "GAMEOVER_FEATURES"))
            self.map_canvas.tag_bind("CONTINUE_GAME_BUTTON", '<ButtonPress-1>', self.continueGame)
            thr.start_new_thread(self.pyd.glide,(self.map_canvas, "CONTINUE_GAME_BUTTON", start_pos, ((self.pyd.calc_height*3)//4, ((self.pyd.calc_height*8)//9)), 1))
        else:
            #Update DRP to loss status
            self.pyd.updateDRP(state="Lost on {}".format(self.gamemode_selected.lower().capitalize()), detail="Playing on '{}'".format(self.loaded_map["name"]))
            
            #Animate game lost image
            start_pos = (-self.pyd.calc_height, self.pyd.calc_height//2)
            self.map_canvas.create_image(start_pos, image=self.pyd.GAME_IMAGE_DICT["GAMEOVER_LOST"], state="disabled", tag=("GAMEOVER_LOST", "GAMEOVER_FEATURES"))
            thr.start_new_thread(self.pyd.glide,(self.map_canvas, "GAMEOVER_LOST", start_pos, (self.pyd.calc_height//2, self.pyd.calc_height//2), 4))

            time.sleep(2.5)

            #Animate back to title screen
            start_pos = (self.pyd.calc_height//2, 2*self.pyd.calc_height)
            self.map_canvas.create_image(start_pos, image=self.pyd.GAME_IMAGE_DICT["BACK_TITLE_BUTTON"], tag=("BACK_TITLE_BUTTON", "GAMEOVER_FEATURES"))
            self.map_canvas.tag_bind("BACK_TITLE_BUTTON", '<ButtonPress-1>',self.exitToTitleScreen)
            thr.start_new_thread(self.pyd.glide,(self.map_canvas, "BACK_TITLE_BUTTON", start_pos, (self.pyd.calc_height//2, ((self.pyd.calc_height*8)//9)), 1))

    def calcScore(self):
        #Calculate score based on game statistics
        r = self.pyd.current_round
        m = self.pyd.difficulty_value
        d = self.loaded_map["map_difficulty"]
        c = self.pyd.current_base_health / self.pyd.max_base_health

        final_score = ((10*m*d*r)/(2-c))**1.5
        return final_score

    def continueGame(self, event=""):
        #Resume event handling
        self.overseeing = True
        thr.start_new_thread(self.overseer, ())

        #Disable game UI buttons
        self.content_canvas.itemconfigure("PAUSE_BUTTON", state="normal")
        self.content_canvas.itemconfigure("HELP_BUTTON", state="normal")
        self.content_canvas.itemconfigure("PLAY_BUTTON", state="normal")
        self.content_canvas.itemconfigure("ABILITY_BUTTON", state="normal")

        self.map_canvas.delete("GAMEOVER_FEATURES")

    def startRound(self):
        #Update time remaining display
        self.content_canvas.itemconfigure("TIME_STATISTIC", text="--:--")

        #Initialise wave settings
        self.pyd.wave = []

        r = self.pyd.current_round+1
        m = self.pyd.difficulty_value
        wave_strength = int(self.unit_dictionary[0]["attributes"]["strength"]+r**m)**(2**0.5)

        temp_unit_dictionary = self.unit_dictionary
        temp_wave_strength = wave_strength

        #Fill the wave with units closest to the wave strength
        while len(temp_unit_dictionary) >= 1:

            strongest_unit = temp_unit_dictionary[-1]
            strength_delta = temp_wave_strength / strongest_unit["attributes"]["strength"]

            #If no more strongest troops can be populated or by random chance remove the strongest troop
            if strength_delta < 1 or random.randint(1,25) == 1 and len(self.pyd.wave) >= 1:
                temp_unit_dictionary = temp_unit_dictionary[:-1]
            else:
                #Add the troop to the wave
                temp_wave_strength -= int(strength_delta)*strongest_unit["attributes"]["strength"]
                for i in range(int(strength_delta)):
                    self.pyd.wave.append(Unit(self.map_canvas, strongest_unit["name"], strongest_unit["texture_name"], strongest_unit["attributes"], self.pyd))

        #Weakest troop spawns first
        self.pyd.wave = self.pyd.wave[::-1]

        #Store the map's path
        valid_path = self.loaded_map["valid_path"].split("/")[:-1]
        
        #Delete debug lines
        self.map_canvas.delete("PATH")

        #Calculate scale factor for the map
        sf = self.pyd.calc_height/self.map_size

        #Spawn every troop with the correct rotated images
        for i in range(len(self.pyd.wave)):
            unit = self.pyd.wave[i]
            unit.tag = "UNIT"+str(i)+str(self.pyd.current_round)

            #Initialise unit path variables
            unit_path = []
            unit_angles = []
            unit_images = []

            for i in range(len(valid_path)):
                #Calculate unique paths
                tile_path = valid_path[i].split(".")
                randomness = self.pyd.gauss2D(0, self.pyd.TILE_VARIANCE)
                x,y = (int((int(tile_path[0])+randomness[0])*sf+(sf/2)), int((int(tile_path[1])+randomness[1])*sf+(sf/2)))

                #Calculate angles
                if i > 0:
                    theta = self.pyd.calcAngle2D(unit_path[-1][0], unit_path[-1][1], x, y)
                    unit_angles.append(theta)
                    unit_images.append(self.pyd.image("textures/"+self.pyd.ACTIVE_TEXTURE+"/units/{}".format(unit.image), theta=theta))

                unit_path.append((x,y))

            #Send calculated data to the unit object
            unit.setupUnit(unit_images, unit_path, sf)

            #Stop spawning troops if paused
            deploy_delay = ((1/len(self.pyd.wave)) + (1/m))/self.pyd.game_speed_mod

            while self.pyd.pause_toggle_state or self.ability1_active:
                time.sleep(deploy_delay)
            
            #Start unit in a thread
            thr.start_new_thread(unit.go,())

            #Delay between troops
            time.sleep(deploy_delay)

        wave_dead = False

        #Round game loop
        while not wave_dead and not self.pyd.game_over:
            #Game loop tick initial variables
            units_dead = 0

            #Check if every units health
            for unit in self.pyd.wave:
                if not unit.active:
                    units_dead += 1

            #Check if wave is completely killed
            if len(self.pyd.wave) <= units_dead:
                wave_dead = True

            time.sleep(1/self.pyd.FPS)

        #End the round if the game isn't over
        if not self.pyd.game_over:
            self.endRound()


    #*General methods
    def quitProgram(self, event=""):
        #Quit the program
        self.title_canvas.itemconfigure("QUIT_BUTTON", state="disabled")  # prevents further clicking

        if event != "": # log event info
            self.pyd.log("quitProgram() from event {} at ({},{})".format(event.type, event.x, event.y))

        self.pyd.DRP_ENABLED = False

        #Fade out animation
        for alpha in range(100, 0, -10):
            try:
                self.root.attributes('-alpha', alpha/100)
                self.root.update()
            except:
                pass

            time.sleep(1/(500*alpha+1))

        self.pyd.log("fade out complete, quitting...")

        self.root.destroy()
        quit()


# Main program
app = App()
app.root.mainloop()
