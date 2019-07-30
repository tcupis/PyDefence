"""
Project: PyDefence
Author: Tom Cupis
Date started: 5/9/2018

"""

#* Imports/dependencies
#Standard libraries
import random
import os
import math
import json

#Required libraries
try:
    import tkinter as tk

    from tkinter import filedialog, messagebox
    from PIL import ImageGrab, Image, ImageTk

    from data.pydefence import Tile, PyDefence
except:
    #Writing logs if import fails
    temp_file = open("FATAL-MAPPING-LAUNCH-{}.txt".format(random.randint(0,10**10)), 'w')
    temp_file.write("A fatal launch error occurred, ensure you have the required packages\n\nGet required packages:\n\t-_thread\n\t-tkinter\n\t-base64\n\t-pillow\n\t-pydefence (within /data/)")
    temp_file.close()

    quit()

class MappingTool():
    #MappingTool class will contain the MappingTool application

    #* Initial config
    def __init__(self):
        #Helper file
        self.pyd = PyDefence()

        #Config window
        self.root = tk.Tk()
        self.root.configure(background='black')
        self.root.resizable(0,0)
        self.root.geometry("800x600")
        self.root.title("PyDefence - Mapping Tool")

        #Try to load window icon
        try:
            self.root.iconbitmap("textures/pydefence.ico")
        except:
            pass
            6
        #Defaults 
        self.help_given = False
        self.loadDefaults()

        #Launch title
        self.titleScreen()

    def loadDefaults(self):
        #Loading default values
        self.map_filename = "maps/NEW_MAP.json"
        self.map_size = 9
        self.open_existing = False
        self.loaded_map = None
        self.firstGridWarning = True
        self.current_texture_idx = 0

        self.texturepack_list = self.pyd.TEXTURE_PACKS


    #* Launch screens
    def launchTitle(self, event="", isBgReload=False):
        #Launch the title screen
        if not isBgReload:
            if len(self.placed_tiles) > 0:
                #Check if progress wants to be lost
                if messagebox.askokcancel("Exit", "Do you really wish to exit?\nAll unsaved progress will be lost."):
                    self.main_frame.pack_forget()
                    self.loadDefaults()
                    self.titleScreen()
            else:
                #? Keep order
                self.titleScreen()
                self.main_frame.pack_forget()
        else:
            #? Keep order
            self.config_frame.pack_forget()
            self.titleScreen()

    def launchMain(self, event=""):
        #Launch main editor
        self.editorGUI()
        self.help_frame.pack_forget()
        
    def launchHelp(self, event=""):
        #Launch the help screen
        if not self.help_given:
            self.help_given = True
            self.helpSplashScreen()
        else:
            self.editorGUI()

        self.config_frame.pack_forget()

        
    #* Setup methods
    def incrementMapSize(self, event=""):
        #Increase grid size
        self.map_size += 1
        self.map_size = min(16, self.map_size)

        #Warn if changing size
        self.gridWarn()

        #Refresh title screen
        self.launchTitle(event, True)

    def decrementMapSize(self, event=""):
        #Decrease grid size
        self.map_size -= 1
        self.map_size = max(6, self.map_size)
        
        #Warn if changing size
        self.gridWarn()

        #Refresh title screen
        self.launchTitle(event, True)

    def setMapSize(self, value, event=""):
        #Set map size
        self.map_size = value
        self.map_size = max(6, self.map_size)
        self.launchTitle(event, True)

    def nextTexture(self, event=""):
        #Find next available texture pack
        self.current_texture_idx += 1
        self.current_texture_idx = max(0, min(len(self.texturepack_list)-1, self.current_texture_idx))
        try:
            self.pyd.ACTIVE_TEXTURE = self.texturepack_list[self.current_texture_idx]
        except IndexError:
            pass

        self.config_canvas.itemconfigure("ACTIVE_TEXTURE", text="{}".format(self.pyd.ACTIVE_TEXTURE))

    def prevTexture(self, event=""):
        #Find previously available texture pack
        self.current_texture_idx -= 1
        self.current_texture_idx = max(0, min(len(self.texturepack_list)-1, self.current_texture_idx))
        try:
            self.pyd.ACTIVE_TEXTURE = self.texturepack_list[self.current_texture_idx]
        except IndexError:
            pass

        self.config_canvas.itemconfigure("ACTIVE_TEXTURE", text="{}".format(self.pyd.ACTIVE_TEXTURE))

    def gridWarn(self):
        #Warn if a map is already pre-loaded, changing the grid size could corrupt the map
        try:
            if self.loaded_map["map_size"] != self.map_size and self.firstGridWarning:
                self.pyd.alert("Map file loaded with grid size data!\nChanging them may cause corruption")
                self.firstGridWarning = False
        except (AttributeError, TypeError):
            pass

    def openMap(self, event=""):
        #Open a valid map file
        while True:
            #Prompt file open
            filename = filedialog.askopenfilename(initialdir="/maps/", title="Select file", filetypes=(("PyDefence map file","*.json"),))

            #! Validation
            #Validate selected file
            if filename != "": #must not be empty string
                if filename.split(".")[-1].lower() == "json": #must have .json extension
                    #Load file and settings
                    try:
                        self.map_filename = filename
                        self.loaded_map = self.pyd.loadJSON(open(self.map_filename, 'r').read())

                        #Check if valid 
                        self.loaded_map["map_difficulty"]
                        self.loaded_map["texture"]
                        self.loaded_map["name"]
                        if len(self.loaded_map["tiles"]) != self.loaded_map["map_size"]**2:
                            raise ValueError

                        #Get details from file and config UI text
                        self.open_existing = True
                        self.setMapSize(self.loaded_map["map_size"])

                        self.pyd.ACTIVE_TEXTURE = (self.loaded_map["texture"])
                        self.current_texture_idx = self.texturepack_list.index(self.loaded_map["texture"])
                        self.config_canvas.itemconfigure("ACTIVE_TEXTURE", text="{}".format(self.pyd.ACTIVE_TEXTURE))
                    except:
                        self.pyd.alert("Invalid or corrupted file\nPlease select another file")
                        self.open_existing = False
                        self.loadDefaults()
                    break
                else:
                    continue
            else:
                break

    def saveMap(self, event=""):
        #Creates the new filename for a saved file
        while True:
            filename = filedialog.asksaveasfilename(initialdir="/maps/", title="Create a new file", filetypes=(("PyDefence map file","*.json"),))
            
            #! Validation
            #Validate new file
            if filename != "": #must not be empty string
                #Check if overwriting new file
                try:
                    open(filename)
                    os.remove(filename)
                    self.open_existing = False
                except:
                    pass

                #Forces .json filetype
                if filename.split(".")[-1].lower() == "json":
                    self.map_filename = filename
                else:
                    self.map_filename = filename+".json"

                #Refresh title screen
                self.launchTitle(event, True)
                break
            else:
                break


    #* Main GUI frames
    def titleScreen(self, event=""):
        #Title screen frame
        self.config_frame = tk.Frame(self.root, width=800, height=600)
        self.config_frame.pack()

        self.config_canvas = tk.Canvas(self.config_frame, width=800, height=600, highlightthickness=0)
        self.config_canvas.pack()
        
        #Calc BG variables
        sq = self.map_size/4
        self.bg_x = int(8*sq)
        self.bg_y = int(6*sq)

        #Display BG
        for x in range(0, self.bg_x):
            for y in range(0, self.bg_y):
                #Tag
                _tag = "x{}y{}".format(x,y)

                #Random colour
                l = (random.randint(10, 20))

                #Canvas object
                self.config_canvas.create_rectangle((x/self.bg_x)*800, (y/self.bg_y)*600,((x/self.bg_x)*800)+800/self.bg_x, ((y/self.bg_y)*600)+600/self.bg_y, fill='#%02X%02X%02X' % (l,l,l), width=1, outline='#%02X%02X%02X' % (l+8,l+8,l+8))

        #Update DRP
        self.pyd.updateDRP(state="Setting up a map", detail="Using the mapping tool")

        #Title
        self.config_canvas.create_text(400, 75, text="PyDefence", font=(self.pyd.default_font, 72), fill="white", state="disabled")
        self.config_canvas.create_text(400, 150, text="Mapping tool", font=(self.pyd.default_font, 24), fill="white", state="disabled")

        #Box outline
        self.config_canvas.create_rectangle(250, 200, 550, 535, width=1,  outline="white", state="disabled")

        #Open map widget
        self.config_canvas.create_text(400, 225, text="Map name", fill="white", font=(self.pyd.default_font, 12), state="disabled")
        self.config_canvas.create_text(375, 255.5, text="..{}".format(self.map_filename[-20:]), fill="white", font=(self.pyd.default_font, 11), state="normal", tag=("MAP_NAME"))
        self.config_canvas.create_rectangle(480, 245, 510, 270,  fill="grey", outline="white", tag=("OPEN_MAP"))
        self.config_canvas.create_text(495, 255.5, text="..", fill="white", font=(self.pyd.default_font, 16), state="disabled")
        self.config_canvas.tag_bind("OPEN_MAP", "<Button-1>", self.openMap)
        self.config_canvas.tag_bind("MAP_NAME", "<Button-1>", self.saveMap)

        #Grid size widget
        self.config_canvas.create_text(400, 70+225, text="Grid size", fill="white", font=(self.pyd.default_font, 12), state="disabled")
        self.config_canvas.create_text(340, 70+255.5, text="{0}x{0}".format(self.map_size), fill="white", font=(self.pyd.default_font, 20), state="disabled")
        self.config_canvas.create_rectangle(410, 70+245, 460, 70+270,  fill="grey", outline="white", tag=("-MAP_SIZE"))
        self.config_canvas.create_text(435, 70+255.5, text="-", fill="white", font=(self.pyd.default_font, 16), state="disabled")
        self.config_canvas.tag_bind("-MAP_SIZE", "<Button-1>", self.decrementMapSize)
        self.config_canvas.create_rectangle(460, 70+245, 510, 70+270, fill="grey", outline="white", tag=("+MAP_SIZE"))
        self.config_canvas.create_text(485, 70+255.5, text="+", fill="white", font=(self.pyd.default_font, 16), state="disabled")
        self.config_canvas.tag_bind("+MAP_SIZE", "<Button-1>", self.incrementMapSize)


        #Texture widget
        self.config_canvas.create_text(400, 135+225, text="Texture pack", fill="white", font=(self.pyd.default_font, 12), state="disabled")
        self.config_canvas.create_text(360, 135+255.5, text="{}".format(self.pyd.ACTIVE_TEXTURE), fill="white", font=(self.pyd.default_font, 14), state="disabled", tag="ACTIVE_TEXTURE")
        self.config_canvas.create_rectangle(460, 135+245, 485, 135+270,  fill="grey", outline="white", tag=("NEXT_TEXTURE"))
        self.config_canvas.create_text(472.5, 135+255.5, text="<", fill="white", font=(self.pyd.default_font, 16), state="disabled")
        self.config_canvas.tag_bind("NEXT_TEXTURE", "<Button-1>", self.prevTexture)
        self.config_canvas.create_rectangle(485, 135+245, 510, 135+270, fill="grey", outline="white", tag=("PREV_TEXTURE"))
        self.config_canvas.create_text(497.5, 135+255.5, text=">", fill="white", font=(self.pyd.default_font, 16), state="disabled")
        self.config_canvas.tag_bind("PREV_TEXTURE", "<Button-1>", self.nextTexture)


        #Launch button
        self.config_canvas.create_rectangle(280, 420, 520, 520, fill="white", width=5,  tag=("LAUNCH_BUTTON"))
        self.config_canvas.create_text(400, 470, text="Launch", font=(self.pyd.default_font, 24), state="disabled")
        self.config_canvas.tag_bind("LAUNCH_BUTTON", "<Button-1>", lambda event: self.config_canvas.itemconfigure("LAUNCH_BUTTON", fill="#0F0F0F"))
        self.config_canvas.tag_bind("LAUNCH_BUTTON", "<ButtonRelease-1>", self.launchHelp)

        #Version display
        self.config_canvas.create_text(740, 590, text="{}".format("Mapping Tool | v1.0"), fill="gray", font=(self.pyd.default_font, 8), state="disabled")

    def helpSplashScreen(self):
        #Help splash screen
        self.help_frame = tk.Frame(self.root, width=800, height=600)
        self.help_frame.pack()

        self.help_canvas = tk.Canvas(self.help_frame, width=800, height=600, highlightthickness=0, bg="#101010")
        self.help_canvas.pack()

        #Help text info
        self.help_canvas.create_text(400, 80, text="Quick tips:", fill="white", font=(self.pyd.default_font, 32), state="disabled")

        self.help_canvas.create_text(400, 140, text="Right click to place tiles", fill="#D0D0D0", font=(self.pyd.default_font, 16), state="disabled")
        self.help_canvas.create_text(400, 180, text="Left click to remove tiles", fill="#D0D0D0", font=(self.pyd.default_font, 16), state="disabled")
        self.help_canvas.create_text(400, 220, text="Drag an area to place/remove multiple tiles", fill="#D0D0D0", font=(self.pyd.default_font, 16), state="disabled")
        self.help_canvas.create_text(400, 260, text="Middle click on a tile to make that the active tile", fill="#D0D0D0", font=(self.pyd.default_font, 16), state="disabled")
        self.help_canvas.create_text(400, 300, text="Click on the tiles panel to select a tile to edit with", fill="#D0D0D0", font=(self.pyd.default_font, 16), state="disabled")
        self.help_canvas.create_text(400, 340, text="Scroll or use the buttons to change tile page", fill="#D0D0D0", font=(self.pyd.default_font, 16), state="disabled")
        self.help_canvas.create_text(400, 380, text="The start of the path must be in the edges of the map", fill="#D0D0D0", font=(self.pyd.default_font, 16), state="disabled")

        #Understand button
        self.help_canvas.create_rectangle(280, 420, 520, 520, fill="white", width=5,  tag=("LAUNCH_BUTTON"))
        self.help_canvas.create_text(400, 470, text="Understood", font=(self.pyd.default_font, 24), state="disabled")
        self.help_canvas.tag_bind("LAUNCH_BUTTON", "<Button-1>", lambda event: self.help_canvas.itemconfigure("LAUNCH_BUTTON", fill="#0F0F0F"))
        self.help_canvas.tag_bind("LAUNCH_BUTTON", "<ButtonRelease-1>", self.launchMain)

    def editorGUI(self):
        #Main editor screen
        self.main_frame = tk.Frame(self.root, width=800, height=600)
        self.main_frame.pack()

        #Map variables
        self.pyd.loadInitialImages(1080, 1080)

        sf = (3/(self.map_size))
        self.pyd.x_scalefactor = sf
        self.pyd.y_scalefactor = sf
        
        self.tile_panel_images = []
        self.current_scroll_percentage = 0
        self.prev_v = 0


        #Generate texture list
        self.texture_list = []
        for texture in self.pyd.game_images:
            if "MAP_" in texture[0][:4]:
                self.texture_list.append([texture[0], self.pyd.image(texture[1])])

        #Initialise editor variables
        self.active_texture = self.texture_list[0]
        self.bg_texture_col = self.hexToRGB("#9F9F9F")#(255,255,255)
        self.bg_col = '#%02X%02X%02X' % (10,10,10)
        self.bg_outline = '#%02X%02X%02X' % (74,74,74)
        self.placed_tiles = []
        self.prev_xy = (0, 0)

        #Map canvas
        self.map_canvas = tk.Canvas(self.main_frame, width=600, height=600, bg="gray", highlightthickness=0)
        self.map=[]

        #Create grid
        for x in range(0, self.map_size):
            row = []
            for y in range(0, self.map_size):
                #Tag
                _tag = "x{}y{}".format(x,y)

                tileObject = Tile(x, y, _tag, [None, None])

                #Canvas object
                self.map_canvas.create_rectangle((x/self.map_size)*600, (y/self.map_size)*600,((x/self.map_size)*600)+600/self.map_size, ((y/self.map_size)*600)+600/self.map_size, fill=self.bg_col, activefill='#%02X%02X%02X' % self.bg_texture_col, width=1, outline=self.bg_outline, tag=(_tag, "TILE"))
                self.map_canvas.create_image(((x/self.map_size)*600)+300/self.map_size, ((y/self.map_size)*600)+300/self.map_size, image=tileObject.texture[1], state="hidden", tag=_tag+"img")
                
                #Bindings
                self.map_canvas.tag_bind(_tag, "<Enter>", lambda event, tag=_tag : self.tileHover(tag))

                self.map_canvas.tag_bind(_tag, "<Button-1>", lambda event, x=x, y=y : self.setStartPos((x,y), "plus #00FF00"))
                self.map_canvas.tag_bind(_tag, "<B1-Motion>", lambda event: self.previewTile(event, 1))
                self.map_canvas.tag_bind(_tag, "<ButtonRelease-1>", self.setTiles)

                self.map_canvas.tag_bind(_tag, "<Button-2>", lambda event, tag=_tag : self.getTileAndSelect(tag))

                self.map_canvas.tag_bind(_tag, "<Button-3>", lambda event, x=x, y=y : self.setStartPos((x,y), "X_cursor #FF0000"))
                self.map_canvas.tag_bind(_tag, "<B3-Motion>", lambda event: self.previewTile(event, 0))
                self.map_canvas.tag_bind(_tag, "<ButtonRelease-3>", self.removeTiles)

                #Map file add
                row.append(tileObject)


            self.map.append(row)
        self.map_canvas.grid(row=0, column=0, rowspan=3)

        #* Try to load save file
        #! Validation
        prev_active_texture = self.active_texture
        corrupted_file = False

        if self.open_existing: #loading an existing file
            for i in range(self.map_size**2):
                    try:
                        #Try to locate the saved map texture
                        texture = self.locateImageObject(self.loaded_map["tiles"][i]["texture"])
                        
                        #If image not found
                        if texture != -1: 
                            self.active_texture = [self.loaded_map["tiles"][i]["texture"], texture]

                            #Tile object setup
                            self.map[x][y] = Tile(x,y, self.loaded_map["tiles"][i]["tag"], self.active_texture)
                            tileObject = self.map[(i//self.map_size) %self.map_size][i%self.map_size]
                            tag = tileObject.tag
                            tileObject.texture = self.active_texture

                            #Add tile images
                            self.map_canvas.itemconfigure(tag, fill='#%02X%02X%02X' % self.bg_texture_col, outline=self.calcHighlightCol(self.bg_texture_col, 32))
                            self.map_canvas.itemconfigure(tag+"img", image=tileObject.texture[1], state="disabled")
                            self.root.update()

                            self.placed_tiles.append(tag)
                        else:
                            corrupted_file = True


                    except (IndexError, KeyError):
                        corrupted_file = True

            #Check that title screen size = loaded map size
            if self.loaded_map["map_size"] != self.map_size:
                corrupted_file = True

        self.active_texture = prev_active_texture

        #Warning if validation failed
        if corrupted_file:
            self.pyd.alert("Corrupted file!\nThis could be missing/invalid textures or invalid map sizes", "WARNING")

        #Update DRP
        if self.open_existing: 
            self.pyd.updateDRP(state="Editing '{}' a {}x{} map".format(self.loaded_map["name"], self.map_size, self.map_size), detail="Using the mapping tool")
        else: 
            self.pyd.updateDRP(state="Creating a {}x{} map".format(self.map_size, self.map_size), detail="Using the mapping tool")

        #* UI setup
        #Get panel images
        for img in self.texture_list:
            self.tile_panel_images.append([ImageTk.PhotoImage(Image.open(self.getImagePath(img[0])).resize((50,50), Image.ANTIALIAS)), img[0]])

        self.scrollbar_max = len(self.tile_panel_images)//18

        #Title panel
        self.title_canvas = tk.Canvas(self.main_frame, width=200, height=110, bg="#c10c0c", highlightthickness=0)

        self.title_canvas.create_rectangle(0,0,200,30, fill="#830000", width=0, tag=("BACK"))
        self.title_canvas.create_text(100, 15, text="< Back to setup", fill="white", font=(self.pyd.default_font, 10), tag=("BACK"))
        self.title_canvas.tag_bind("BACK", "<ButtonRelease-1>", self.launchTitle)

        self.title_canvas.create_image(40, 70, image=self.tile_panel_images[0][0], tag=("ACTIVE_TILE"))
        self.title_canvas.create_text(130, 55, text="Active tile:", fill="white", font=(self.pyd.default_font,12))
        self.title_canvas.create_text(130, 80, text="{}".format(self.tile_panel_images[0][1].replace("MAP_", "")), fill="white", font=(self.pyd.default_font, 8), tag=("ACTIVE_TILE_INFO"))

        self.title_canvas.grid(row=0, column=1)


        #Tile panel
        self.tile_canvas = tk.Canvas(self.main_frame, width=200, height=400, bg="#4A4A4A", highlightthickness=0)

        for i in range(0, len(self.tile_panel_images)-(len(self.tile_panel_images)%3), 3):
            self.tile_canvas.create_image(40, (i+1)*20+15, image=self.tile_panel_images[i][0], tag=("PANEL_TILE", "IMG"+str(i)))
            self.tile_canvas.create_image(100, (i+1)*20+15, image=self.tile_panel_images[i+1][0], tag=("PANEL_TILE", "IMG"+str(i+1)))
            self.tile_canvas.create_image(160, (i+1)*20+15, image=self.tile_panel_images[i+2][0], tag=("PANEL_TILE", "IMG"+str(i+2)))

            self.tile_canvas.tag_bind("IMG"+str(i), "<Button-1>", lambda e, i=i: self.setActive(self.tile_panel_images[int(i)][1], i))
            self.tile_canvas.tag_bind("IMG"+str(i+1), "<Button-1>", lambda e, i=i: self.setActive(self.tile_panel_images[int(i+1)][1], i+1))
            self.tile_canvas.tag_bind("IMG"+str(i+2), "<Button-1>", lambda e, i=i: self.setActive(self.tile_panel_images[int(i+2)][1], i+2))

        if len(self.tile_panel_images)%3 == 2:
            self.tile_canvas.create_image(40, (i+4)*20+15, image=self.tile_panel_images[-2:-1][0][0], tag=("PANEL_TILE", "IMG"+str(i+3)))
            self.tile_canvas.create_image(100, (i+4)*20+15, image=self.tile_panel_images[-1:][0][0], tag=("PANEL_TILE", "IMG"+str(i+4)))
            self.tile_canvas.tag_bind("IMG"+str(i+3), "<Button-1>", lambda e, i=i: self.setActive(self.tile_panel_images[int(i+3)][1], i+3))
            self.tile_canvas.tag_bind("IMG"+str(i+4), "<Button-1>", lambda e, i=i: self.setActive(self.tile_panel_images[int(i+4)][1], i+4))
        elif len(self.tile_panel_images)%3 == 1:
            self.tile_canvas.create_image(40, (i+4)*20+15, image=self.tile_panel_images[-1:][0][0], tag=("PANEL_TILE", "IMG"+str(i+3)))
            self.tile_canvas.tag_bind("IMG"+str(i+3), "<Button-1>", lambda e, i=i: self.setActive(self.tile_panel_images[int(i+3)][1], i+3))

        self.tile_canvas.bind("<Enter>", self.bindMouseWheel)
        self.tile_canvas.bind("<Leave>", self.unbindMouseWheel)

        self.tile_canvas.create_rectangle(0, 370, 120, 400, fill="#101010", width=0, tag=("STATIC", "BUTTON"))
        self.tile_canvas.create_text(60, 385, text="Page {}/{}".format(1, self.scrollbar_max+1), fill="white", font=(self.pyd.default_font, 10), tag=("PAGE_DISPLAY", "STATIC"))

        self.tile_canvas.create_rectangle(120, 370, 160, 400, fill="#202020", width=0, tag=("STATIC", "SCROLLDOWN"))
        self.tile_canvas.create_text(140, 385, text="▼", fill="white", font=(self.pyd.default_font, 10), tag=("STATIC", "SCROLLDOWN"))
        self.tile_canvas.tag_bind("SCROLLDOWN", "<Button-1>", lambda e: self.onMouseWheel(e, 1))


        self.tile_canvas.create_rectangle(160, 370, 200, 400, fill="#303030", width=0, tag=("STATIC", "SCROLLUP"))
        self.tile_canvas.create_text(180, 385, text="▲", fill="white", font=(self.pyd.default_font, 10), tag=("STATIC", "SCROLLUP"))
        self.tile_canvas.tag_bind("SCROLLUP", "<Button-1>", lambda e: self.onMouseWheel(e, -1))

        self.tile_canvas.grid(row=1, column=1)

        #Save button
        self.save_frame = tk.Canvas(self.main_frame, width=200, height=90, bg="yellow", highlightthickness=0)

        self.save_frame.create_rectangle(0, 0, 200, 90, fill="limegreen", width=0, tag=("BUTTON", "DISPLAY"))
        self.save_frame.create_text(100, 45, text="Generate", fill="white", font=(self.pyd.default_font, 24), tag=("BUTTON", "TEXT"))
        self.save_frame.tag_bind("BUTTON", "<Button-1>", self.disableSave)
        self.save_frame.tag_bind("BUTTON", "<ButtonRelease-1>", self.checkGenerate)

        self.save_frame.grid(row=2, column=1)


    #* Scrollwheel binds
    def bindMouseWheel(self, event):
        self.tile_canvas.bind_all("<MouseWheel>", self.onMouseWheel)   

    def unbindMouseWheel(self, event):
        self.tile_canvas.unbind_all("<MouseWheel>") 

    def onMouseWheel(self, event, vel=0):
        velocity = -event.delta//120
        velocity += vel

        if velocity > 0 and self.current_scroll_percentage != self.scrollbar_max:
            self.current_scroll_percentage += 1
            self.tile_canvas.yview_scroll(1, "pages")
            self.tile_canvas.itemconfigure("PAGE_DISPLAY", text="Page {}/{}".format(self.current_scroll_percentage+1, self.scrollbar_max+1))
            self.tile_canvas.move("STATIC", 0, 360)

        elif velocity < 0 and self.current_scroll_percentage != 0:
            self.current_scroll_percentage -= 1
            self.tile_canvas.yview_scroll(-1, "pages")
            self.tile_canvas.itemconfigure("PAGE_DISPLAY", text="Page {}/{}".format(self.current_scroll_percentage+1, self.scrollbar_max+1))
            self.tile_canvas.move("STATIC", 0, -360)


    #* Image search methods
    def locateImageObject(self, search, idx=1):
        #Locate an image object from string
        for i, e in enumerate(self.texture_list):
            try:
                e.index(search)
                return self.texture_list[i][idx]
            except ValueError:
                pass
        return -1

    def getImagePath(self, search):
        #Returns the path of a searched image
        for i, e in enumerate(self.pyd.game_images):
            try:
                e.index(search)
                return self.pyd.game_images[i][1]
            except ValueError:
                pass
        return "textures/missing.png"


    #* Binding methods
    def calcHighlightCol(self, tile_rgb, z, forceType=None):
        #Calculate highlights/shadows
        r,g,b = tile_rgb

        if r+g+b >= 127*3 or forceType == "shadow":
            _r,_g,_b = max(0, min(255, r-z)), max(0, min(255, g-z)), max(0, min(255, b-z))

        if r+g+b <= 127*3 or forceType == "highlight":
            _r,_g,_b = max(0, min(255, r+z)), max(0, min(255, g+z)), max(0, min(255, b+z))

        return '#%02X%02X%02X' % (_r, _g, _b)

    def hexToRGB(self, hex_):
        #hex to (r,g,b) values
        return tuple(int(hex_.replace('#', '')[i:i+2], 16) for i in (0, 2 ,4))

    def mapCoordFilter(self, x,y):
        #Filters x,y to x,y for grid, filters large x,y values
        return (min(self.map_size, max(0, int((x/600)*self.map_size))),min(self.map_size, max(0, int((y/600)*self.map_size))))

    def getStep(self, pos1, pos2):
        #Function to calculate stepping required for a given range
        if pos2[0]-pos1[0] < 0:
            step_x = -1
        else:
            step_x = 1

        if pos2[1]-pos1[1] < 0:
            step_y = -1
        else:
            step_y = 1

        return step_x, step_y

    def getRange(self, event):
        #Generate a range given start/end points
        self.end_pos = self.mapCoordFilter(event.x, event.y)

        step_x, step_y = self.getStep(self.start_pos, self.end_pos)


        x_range = range(self.start_pos[0], min(self.map_size, self.end_pos[0]+step_x), step_x)
        y_range = range(self.start_pos[1], min(self.map_size, self.end_pos[1]+step_y), step_y)

        return x_range, y_range


    #* Grid manipulation
    def setStartPos(self, pos, cursor_):
        #Set an action start point (for area creation)
        self.map_canvas.configure(cursor=cursor_)
        self.start_pos = pos
        
    def resetOutlines(self):
        #Reset grid outlines/highlights
        for x in range(self.map_size):
            for y in range(self.map_size):
                tag = self.map[x][y].tag
                if tag not in self.placed_tiles:
                    self.map_canvas.itemconfigure(tag, outline=self.bg_outline)
                else:
                    self.map_canvas.itemconfigure(tag, outline=self.calcHighlightCol(self.hexToRGB(self.map_canvas.itemcget(tag, "fill")), 32))

    def tileHover(self, tag):
        #On hover event highlight the tile
        if self.map_canvas.itemcget(tag, "fill") != self.bg_col:
            tile_rgb = self.hexToRGB(self.map_canvas.itemcget(tag, "fill"))

            #Calculate the highlighted colour
            selected_col = self.calcHighlightCol(tile_rgb, 64)

            self.map_canvas.itemconfigure(tag, activefill=selected_col)
        else:
            self.map_canvas.itemconfigure(tag, activefill='#%02X%02X%02X' % self.bg_texture_col)

    def previewTile(self, event, isAdd):
        #Preview action area of effect
        if self.mapCoordFilter(event.x, event.y) != self.prev_xy:
            self.resetOutlines()

            x_range, y_range = self.getRange(event)
            for x in x_range:
                for y in y_range:
                    tag = self.map[x][y].tag

                    #3 possible mouse events 1-delete, 2-create, 3-fill empty only
                    if isAdd == 0:
                        self.map_canvas.itemconfigure(tag, outline="red")
                    elif isAdd == 1:
                        self.map_canvas.itemconfigure(tag, outline="limegreen")
                    elif tag not in self.placed_tiles and isAdd == 2:
                        self.map_canvas.itemconfigure(tag, outline="black")

        self.prev_xy = self.mapCoordFilter(event.x, event.y)

    def setTiles(self, event):
        #Add new tiles action on event
        self.map_canvas.configure(cursor="arrow")
        x_range, y_range = self.getRange(event)
        for x in x_range:
            for y in y_range:
                tileObject = self.map[x][y]
                tag = tileObject.tag
                tileObject.texture = self.active_texture

                #Replace texture on map
                self.map_canvas.itemconfigure(tag, fill='#%02X%02X%02X' % self.bg_texture_col, outline=self.calcHighlightCol(self.bg_texture_col, 32))
                self.map_canvas.itemconfigure(tag+"img", image=tileObject.texture[1], state="disabled")

                #Move tag to end of placed tiles list
                if tag in self.placed_tiles:
                    self.placed_tiles.remove(tag)
                self.placed_tiles.append(tag)

    def getTileAndSelect(self, tag):
        #Get and select the tile with a specified tag
        if tag in self.placed_tiles:
            for i, e in enumerate(self.texture_list):
                if str(e[1]) == self.map_canvas.itemcget(tag+"img", "image"):
                    break

            self.setActive(self.texture_list[i][0], i)
        
    def removeTiles(self, event):
        #Remove tiles action on event
        self.resetOutlines()
        self.map_canvas.configure(cursor="arrow")
        x_range, y_range = self.getRange(event)
        for x in x_range:
            for y in y_range:
                tileObject = self.map[x][y]
                tag = tileObject.tag

                #Removed placed tiles
                if tag in self.placed_tiles:
                    tileObject.texture = [None, None]
                    self.map_canvas.itemconfigure(tag, fill=self.bg_col, outline=self.bg_outline)
                    self.map_canvas.itemconfigure(tag+"img", image=tileObject.texture[1], state="hidden")   
                    self.placed_tiles.remove(tag)


    #* Button binds
    def setActive(self, texture, i):
        #Set the active tile + texture
        self.active_texture = [self.locateImageObject(str(texture), 0), self.locateImageObject(str(texture))]
        self.title_canvas.itemconfigure("ACTIVE_TILE_INFO", text="{}".format(self.active_texture[0].replace("MAP_", "")))
        self.title_canvas.itemconfigure("ACTIVE_TILE", image=self.tile_panel_images[i][0])

    def disableSave(self, event=""): 
        #Disable the save button
        self.save_frame.itemconfigure("DISPLAY", fill="gray", state="disabled")
        self.save_frame.itemconfigure("TEXT", fill="lightgray", state="disabled")

    def enableSave(self, event=""): 
        #Enable the save button
        self.save_frame.itemconfigure("DISPLAY", fill="limegreen", state="normal")
        self.save_frame.itemconfigure("TEXT", fill="white", state="normal")

    def checkGenerate(self, event=""): 
        #Check if user wishes to save
        if not messagebox.askokcancel("Generate a map file", "Do you want to generate a map file now."):
            self.enableSave(event)
        else:
            self.generateMap(event)


    #* Pathfinding
    def getPath(self, start_pos, nodes, end_pos):
        #Verifying a valid path given a start/end pos and waypoints

        #Initialise variables
        active_node = start_pos
        path = ""
        nodes_checked = 0

        #Setup footprint/possible next path positions
        footprint_template = [[(1,0), "MAP_PATH_X"],[(-1,0), "MAP_PATH_X"],[(0,1), "MAP_PATH_Y"],[(0,-1), "MAP_PATH_Y"]]
        check_footprint = footprint_template

        path += "{}.{}/".format(start_pos[0], start_pos[1]) #add start ptr

        #Until the end is located find the path
        while active_node != end_pos:
            for footprint in check_footprint: #check the entire footprint
                nodes_checked +=1

                if nodes_checked >= self.map_size**2: #if all map tiles have been checked no path found
                    return False, active_node

                #Add the footprint to the active node
                future_node = [max(0, min(self.map_size-1,active_node[0]+footprint[0][0])), max(0, min(self.map_size-1,active_node[1]+footprint[0][1]))]

                #If the end found return the path
                if self.map[future_node[0]][future_node[1]].texture[0] == "MAP_END_PTR":
                    path += "{}.{}/".format(end_pos[0], end_pos[1])
                    return path

                #Check if the active node is valid or a turning node
                if self.map[future_node[0]][future_node[1]].texture[0] == footprint[-1] or future_node in nodes:

                    dx,dy = footprint[0][0], footprint[0][1] #get direction deltas

                    if active_node == start_pos: #check if at start
                        at_start = True
                    else:
                        at_start = False

                    #Initialise variables for texture checking
                    new_active_node = future_node
                    active_node = new_active_node
                    active_texture = self.map[active_node[0]][active_node[1]].texture[0]

                    path += "{}.{}/".format(active_node[0], active_node[1]) #Add tile to path

                    #Check if the direction delta has a valid tile for a path
                    if dx == 1:
                        if active_texture == "MAP_PATH_BR":
                            check_footprint = [[(0,-1), "MAP_PATH_Y"]]
                        elif active_texture == "MAP_PATH_TR":
                            check_footprint = [[(0,1), "MAP_PATH_Y"]]
                        elif active_texture in ["MAP_PATH_BL", "MAP_PATH_TL"]:
                            if at_start: #reset path if at start
                                active_node = [max(0, min(self.map_size-1,active_node[0]-footprint[0][0])), max(0, min(self.map_size-1,active_node[1]-footprint[0][1]))]
                                path = "{}.{}/".format(active_node[0], active_node[1])
                                continue
                            else: return False, active_node
                        else: check_footprint = [[(1,0), "MAP_PATH_X"]] #if not a turning node, continue
                    elif dx == -1:
                        if active_texture == "MAP_PATH_BL":
                            check_footprint = [[(0,-1), "MAP_PATH_Y"]]
                        elif active_texture == "MAP_PATH_TL":
                            check_footprint = [[(0,1), "MAP_PATH_Y"]]
                        elif active_texture in ["MAP_PATH_BR", "MAP_PATH_TR"]:
                            if at_start: #reset path if at start
                                active_node = [max(0, min(self.map_size-1,active_node[0]-footprint[0][0])), max(0, min(self.map_size-1,active_node[1]-footprint[0][1]))]
                                path = "{}.{}/".format(active_node[0], active_node[1])
                                continue
                            else: return False, active_node
                        else: check_footprint = [[(-1,0), "MAP_PATH_X"]] #if not a turning node, continue

                    if dy == 1:
                        if active_texture == "MAP_PATH_BL":
                            check_footprint = [[(1,0), "MAP_PATH_X"]]
                        elif active_texture == "MAP_PATH_BR":
                            check_footprint = [[(-1,0), "MAP_PATH_X"]]
                        elif active_texture in ["MAP_PATH_TL", "MAP_PATH_TR"]:
                            if at_start: #reset path if at start
                                active_node = [max(0, min(self.map_size-1,active_node[0]-footprint[0][0])), max(0, min(self.map_size-1,active_node[1]-footprint[0][1]))]
                                path = "{}.{}/".format(active_node[0], active_node[1])
                                continue
                            else: return False, active_node
                        else: check_footprint = [[(0,1), "MAP_PATH_Y"]] #if not a turning node, continue

                    elif dy == -1:
                        if active_texture == "MAP_PATH_TL":
                            check_footprint = [[(1,0), "MAP_PATH_X"]]
                        elif active_texture == "MAP_PATH_TR":
                            check_footprint = [[(-1,0), "MAP_PATH_X"]]
                        elif active_texture in ["MAP_PATH_BL", "MAP_PATH_BR"]:
                            if at_start: #reset path if at start
                                active_node = [max(0, min(self.map_size-1,active_node[0]-footprint[0][0])), max(0, min(self.map_size-1,active_node[1]-footprint[0][1]))]
                                path = "{}.{}/".format(active_node[0], active_node[1])
                                continue
                            else: return False, active_node
                        else: check_footprint = [[(0,-1), "MAP_PATH_Y"]] #if not a turning node, continue

                    break
    
    
    #* Map generation methods
    def generateDifficulty(self, path_length, t=0.3, m=2.45):
        #Calculate difficulty
        d = (m*t*(1+math.log((t**(-2**t)*2**(t**2))/((path_length+2**t)**t))))**m
        return d

    def generateMap(self, event=""):
        #Generate the map file
        if event != "":
            self.pyd.log("generateMap() from event {} at ({},{})".format(event.type, event.x, event.y))

        valid = True

        #! Validation
        #Correct number of tiles
        if len(self.placed_tiles) != self.map_size**2:
            valid = False
            self.pyd.alert("Map only contains {}/{} tiles!\nPlease fill all the blank spaces with tiles".format(len(self.placed_tiles), self.map_size**2))

        #Correct number of start/end pointers and build pivot nodes
        if valid:
            nodes = []
            start, end = 0,0
            for tag in self.placed_tiles:
                x = int(tag[tag.find("x")+1:tag.find("y")])
                y=int(tag[tag.find("y")+1:])

                #Check how many start/end tiles there are
                if self.map[x][y].texture[0] == "MAP_START_PTR":
                    start += 1
                    start_pos = (x,y)

                if self.map[x][y].texture[0] == "MAP_END_PTR":
                    end += 1
                    end_pos = (x,y)

                #Build waypoints/nodes
                if self.map[x][y].texture[0] in ['MAP_PATH_BL', 'MAP_PATH_TL', 'MAP_PATH_BR', 'MAP_PATH_TR']:
                    nodes.append([x,y])

            if not(start == 1 and end == 1):
                valid = False
                self.pyd.alert("Map doesn't contain correct number of start ({}) or end ({}) tiles\nOnly 1 start tile and 1 end tile is allowed!".format(start, end))
            else:
                #Check that start pointer is in the corners
                if (start_pos[0] != 0 and start_pos[1] != 0):
                    if (start_pos[0] != self.map_size-1 and start_pos[1] != self.map_size-1):
                        valid = False
                        self.pyd.alert("The start tile can only be at the edges of the map\nTip: You can place the base tile anywhere!")

        #Check if valid path
        if valid:
            path = self.getPath(start_pos, nodes, end_pos)

            #Reset any invalid tiles from last run
            self.map_canvas.itemconfigure("TILE", fill='#%02X%02X%02X' % self.bg_texture_col, outline=self.calcHighlightCol(self.bg_texture_col, 32)) 

            #Display the last tile the path was valid at
            if not path[0]:
                valid = False
                self.map_canvas.itemconfigure("x{}y{}".format(path[1][0],path[1][1]), fill="#FF0000", outline="#FF0000")
                self.pyd.alert("Couldn't find valid path")

        #Check for path tiles that aren't on the valid path
        if valid:
            path_list = path.split("/")[:-1]
            for i in range(len(path_list)):
                path_list[i] = [int(path_list[i].split(".")[0]),int(path_list[i].split(".")[1])]

            for x in range(self.map_size):
                for y in range(self.map_size):
                    if [x,y] not in path_list:
                        if self.map[x][y].texture[0] in ['MAP_PATH_X', 'MAP_PATH_Y', 'MAP_PATH_BL', 'MAP_PATH_TL', 'MAP_PATH_BR', 'MAP_PATH_TR']:
                            valid = False
                            self.map_canvas.itemconfigure("x{}y{}".format(x,y), fill="#FF0000", outline="#FF0000")
            if not valid:
                self.pyd.alert("Path tiles found outside path!")

        #Generate the file
        if valid:
            map_difficulty = self.generateDifficulty(len(path[:-1].split("/")))
            map_string = '{"name": "%s", "map_size": %s, "valid_path": "%s", "texture": "%s", "map_difficulty":%s, "tiles": [' % (self.map_filename[len(self.map_filename)-self.map_filename[::-1].find("/"):-5], self.map_size, path,self.pyd.ACTIVE_TEXTURE, map_difficulty)
            #Map file generation
            for x in range(self.map_size):
                for y in range(self.map_size):
                    map_string += '{"x" : %s, "y" : %s, "tag" : "%s", "texture" : "%s"},' % (self.map[x][y].x, self.map[x][y].y, self.map[x][y].tag, self.map[x][y].texture[0])

            map_string = map_string[:-1] + "]}"
            map_string = json.dumps(json.loads(map_string), indent=2, sort_keys=True)

            #Write the file
            fileObject = open(self.map_filename, 'w')
            fileObject.write(map_string)
            fileObject.close()

            #Save the preview image
            self.root.attributes("-topmost", 1)
            thumbnail_file = "{}.png".format(self.map_filename[:-5])

            x = self.root.winfo_rootx()+self.map_canvas.winfo_x()
            y = self.root.winfo_rooty()+self.map_canvas.winfo_y()
            x1 = x+self.map_canvas.winfo_width()
            y1 = y+self.map_canvas.winfo_height()
            ImageGrab.grab().crop((x, y, x1, y1)).resize((180,180), Image.ANTIALIAS).save(thumbnail_file)
            self.root.attributes("-topmost", 0)

            #Calculate and display size
            file_size = (os.path.getsize(self.map_filename)+os.path.getsize(thumbnail_file))/1024
            self.pyd.alert("Map successfully generated [{:.2f}KB]\nDifficulty multiplier calculated to be [x{:.2f}]\n\nThis value will be used to make the game score fairer, high multipliers mean harder maps!".format(file_size, map_difficulty))


        self.enableSave(event) #re-enable the save button

# Main program
app = MappingTool()
app.root.mainloop()
