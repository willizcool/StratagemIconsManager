import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
import ImageProcess as IP
import os, sys, json, math
import MakePatch as patcher
from PIL import Image, ImageTk, ImageEnhance, ImageFilter, ImageDraw
import numpy as np
from MakePatch import Global_temp_directory

class ImageSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Helldivers 2 Stratagem Manager v3.21")
        self.root.iconbitmap(os.getcwd()+"\\resource\\deps\\Helldivers.ico")
        self.root.geometry("550x650")  # Fixed size: 900x700 pixels
        self.root.minsize(600, 200)
        self.root.maxsize(600, 9999)

        self.images = []
        self.tiles = []
        self.tile_index_list = []
        self.tile_index = [0,0,0,0]
        self.save_data = {}
        self.save_file_path = os.path.join(os.path.curdir,"resource","deps","save_data.json")
        self.load_states()
        self.create_widgets()
        
    def create_widgets(self):
        self.header_frame =tk.Frame(self.root,height=1)
        self.canvas_frame =tk.Frame(self.root)
        self.foot_Frame = tk.Frame(self.root,bg=f"lightgrey")
        self.header_frame.pack(side="top",fill="x")
        self.canvas_frame.pack(expand=True,fill="both")
        self.foot_Frame.pack(side = "bottom",fill="x")
        # Canvas and scrollable frame setup
        self.canvas = tk.Canvas(self.canvas_frame)
        self.v_scrollbar = tk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = tk.Frame(self.canvas_frame)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.group_labels = [tk.Label(self.scrollable_frame) for _ in range(4)]
        self.group_frames = [tk.Frame(self.scrollable_frame) for _ in range(4)]
        self.group_labels[IP.colorindex.index("offense")].config(text="Offense",font=("Helvetica", 10, "bold"))
        self.group_frames[IP.colorindex.index("offense")].config(bg=IP.offensecolor)
        self.group_labels[IP.colorindex.index("supply")].config(text="Supply",font=("Helvetica", 10, "bold"))
        self.group_frames[IP.colorindex.index("supply")].config(bg=IP.supplycolor)
        self.group_labels[IP.colorindex.index("defense")].config(text="Defense",font=("Helvetica", 10, "bold"))
        self.group_frames[IP.colorindex.index("defense")].config(bg=IP.defensecolor)
        self.group_labels[IP.colorindex.index("mission")].config(text="Mission",font=("Helvetica", 10, "bold"))
        self.group_frames[IP.colorindex.index("mission")].config(bg=IP.missioncolor)

        for i in range(4):
            self.group_labels[i].pack()
            self.group_frames[i].pack(fill="y")

        self.canvas.configure(yscrollcommand=self.v_scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.v_scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)  # Linux scroll up
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)  # Linux scroll down
        ##########header
        self.import_button=tk.Button(self.header_frame,bg=f"lightgrey",text="Import Pack",command=importpack)
        self.new_button=tk.Button(self.header_frame,bg=f"lightgrey",text="New Sheet",command=newsheet)
        self.drop_down= ttk.Combobox(self.header_frame, values=self.tile_index_list, state="readonly")
        self.apply_button=tk.Button(self.header_frame,bg=f"lightgrey",text="Apply To All",command=self.apply_all)
        self.remove_button=tk.Button(self.header_frame,bg=f"lightgrey",text="Remove Archive",command=self.removesheet)
        self.import_button.pack(side="left",fill="x",expand=True)
        self.new_button.pack(side="left",fill="x",expand=True)
        self.drop_down.pack(expand=True,fill="x",side="left")
        self.apply_button.pack(fill="x",expand=True,side="left")
        self.remove_button.pack(side="left",fill="x",expand=True)

        #self.import_button.bind("<Button-1>", importpack)
        #self.apply_button.bind("<Button-1>", self.apply_all)

        ##########foot
        self.leftside_Frame= tk.Frame(self.foot_Frame,bg=f"lightgrey")
        self.leftside_Frame.pack(fill="y",side="left",anchor="nw")
        self.setting_frame=tk.Frame(self.foot_Frame,bg=f"lightgrey")
        self.setting_frame.pack(fill="y",side="left")
        self.middle_frame=tk.Frame(self.foot_Frame,bg=f"lightgrey")
        self.middle_frame.pack(fill="both",expand=True)

        self.scroll_left_frame = tk.Frame(self.setting_frame,bg=f"lightgrey")
        self.scroll_right_frame = tk.Frame(self.setting_frame,bg=f"lightgrey")
        self.scroll_left_frame.pack(side="left")
        self.scroll_right_frame.pack(side="right")

        self.label_transparency = tk.Label(self.scroll_left_frame,text="Dimming amount",bg=f"lightgrey")
        self.label_transparency.pack(side="top")
        self.tranp_scroler = tk.Scale(self.scroll_left_frame, from_=0, to=100,orient="horizontal",command=self.on_dim_move,bg=f"lightgrey")
        self.tranp_scroler.set(self.load_variable("dim",50))
        self.tranp_scroler.pack(side="top",padx=5,pady=5)
        self.label_highlight = tk.Label(self.scroll_right_frame,text="Glow intensity",bg=f"lightgrey")
        self.label_highlight.pack(side="top")
        self.highlight_scroler = tk.Scale(self.scroll_right_frame, from_=0, to=100,orient="horizontal",command=self.on_high_move,bg=f"lightgrey")
        self.highlight_scroler.set(self.load_variable("glow",50))
        self.highlight_scroler.pack(padx=5,pady=5)


        self.over_button_frame = tk.Frame(self.middle_frame,bg=f"lightgrey")
        self.over_button_frame.pack(side="top",fill="x",expand=True)
        self.name_label= tk.Label(self.over_button_frame,text="Mod Name:",bg=f"lightgrey")
        self.name_label.pack(side="left")
        self.packname = self.load_variable("ModName","Custom Stratagem Mod")
        self.name_entry = tk.Entry(self.over_button_frame,textvariable=self.packname)
        self.name_entry.pack(expand=True,padx=5,fill="x")
        self.name_entry.insert(0,self.packname)
        


        self.save_button = tk.Button(self.middle_frame, text="Create Patch", command=self.save_image, bg=f"lightblue",highlightcolor=f"blue",font=("Helvetica", 12, "bold"))
        self.save_button.pack(fill="both",padx=5,pady=5,expand=True)

        #left side settings
        self.select_frame=tk.Frame(self.leftside_Frame,bg=f"lightgrey")
        self.select_frame.pack(side="top",fill="x")
        self.empty_frame=tk.Frame(self.leftside_Frame,bg=f"lightgrey")
        self.empty_frame.pack(fill="both",expand=True)

        self.help_label = tk.Label(self.empty_frame, text="Help",bg=f"lightgrey", fg="blue", cursor="hand2",font=("Helvetica", 10, "bold"))
        self.help_label.pack(side="bottom",anchor="sw")  # Position at bottom left
        self.help_label.bind("<Button-1>", self.open_help_page)
        #select all
        self.Favorites = self.load_variable("Flabel",1)
        self.toggle_filters = tk.Label(self.select_frame, text="Disable Favorites"if self.Favorites!=0 else "Enable Favorites", fg="red", cursor="hand2",bg=f"lightgrey")
        self.toggle_filters.bind("<Button-1>", self.toggle_all_filters)
        self.toggle_filters.pack(side="top",anchor="nw")

        self.select_label = tk.Label(self.select_frame, text="Favorite All", fg="red", cursor="hand2",bg=f"lightgrey")
        self.select_label.bind("<Button-1>", self.select_all)
        self.select_label.pack(anchor="nw",side="top")

        self.deselect_label = tk.Label(self.select_frame, text="UnFavorite All", fg="red", cursor="hand2",bg=f"lightgrey")
        self.deselect_label.bind("<Button-1>", self.deselect_all)
        self.deselect_label.pack(side="top",anchor="nw")
    
    def load_images(self,patchname,library_pages):
        for page in library_pages:
            image_path = page["NAME"]
            imagepath = patcher.LoadImage(patchname,os.path.splitext(image_path)[0])
            img = Image.open(imagepath)
            image = IP.Images(img,image_path,page["DETAILS"])
            self.images.append(image)
            tiles = image.split_image()
            for tile in tiles:
                self.tiles.append(tile)

    def load_moreimages(self,patchname,library_pages):
        for i,page in enumerate(library_pages):
            image_path = page["NAME"]
            imagepath = patcher.LoadImage(patchname,os.path.splitext(image_path)[0])
            self.images[i].split_existing_image(Image.open(imagepath))

    def save_image(self):
        self.packname = self.name_entry.get()
        if not self.packname:
            self.packname = "Custom Stratagem Mod"
        self.save_data["ModName"] = self.packname
        patcher.PrepPatch()
        img : IP.Images
        for img in self.images:
            # Create a copy of the original image to modify
            modified_image = img.img.copy()
            tile :IP.Tile
            for tile in img.tiles:
                box = tile.box
                if(tile.nofilter):
                    nofilter_tile = tile.tile_imgs[tile.selectedindex]
                    modified_image.paste(nofilter_tile, box)
                elif tile.selected:
                    highlighted_tile = self.highlighttile(tile.tile_imgs[tile.selectedindex],True)
                    modified_image.paste(highlighted_tile, box)
                else:
                    darkened_tile = self.darken_tile(tile.tile_imgs[tile.selectedindex])
                    modified_image.paste(darkened_tile, box)

            # Save the modified image
            save_path = os.path.join(patcher.GetImageLocation(),os.path.splitext(img.image_path)[0]+"_new.png")
            if save_path:
                modified_image.save(save_path)
            patcher.Overwriteimage(os.path.splitext(img.image_path)[0])
        patcher.CreatePatch(self.packname)
        self.save_states()

    def load_states(self):
        """Load state from a JSON file."""
        try:
            with open(self.save_file_path, 'r') as file:
                self.save_data = json.load(file)
            print(f"State successfully loaded from {self.save_file_path}")
        except FileNotFoundError:
            print("Save file not found, starting with default state.")
        except Exception as e:
            print(f"Error loading state: {e}")

    def load_variable(self,name,default):
        if name not in self.save_data:
            self.save_data[name] = default
        return self.save_data[name]

    def load_select_state(self, id):
        if "selected" not in self.save_data:
            self.save_data["selected"] = []
        return True if id in self.save_data["selected"] else False
    
    def load_filter_state(self, id):
        if "nofilter" not in self.save_data:
            self.save_data["nofilter"] = []
        return True if id in self.save_data["nofilter"] else False
    
    def load_selected_tile(self,names:list, id):
        name = ""
        index = 0
        if "tileindexes" not in self.save_data:
            self.save_data["tileindexes"] = []
        try:
            name = self.save_data["tileindexes"][id]
            index = names.index(name)
        except:
            name = names[0]
            while len(self.save_data["tileindexes"]) <= id:
                self.save_data["tileindexes"].append(name)
            index = names.index(name)
        return index
        

    def save_states(self):
        """Save state to a JSON file."""
        try:
            with open(self.save_file_path, 'w') as file:
                json.dump(self.save_data, file, indent=4)
            print(f"State successfully saved to {self.save_file_path}")
        except Exception as e:
            print(f"Error saving state: {e}")
        

    def display_tiles(self,indexnames):
        image: IP.Images
        tile: IP.Tile
        for i,tile in enumerate(self.tiles):
            # Convert tile to PhotoImage for display in tkinter
            tileindex = self.load_selected_tile(indexnames,tile.id)
            tile.selectedindex = tileindex
            tile.tkimage = ImageTk.PhotoImage(tile.displaytiles[tileindex])
            tile_frame = tk.Frame(self.group_frames[tile.group], width=tile.tkimage.width(), pady=0)
            tile_label = tk.Label(tile_frame, image=tile.tkimage, pady=0,bg=f"grey")
            rfilter_button = tk.Button(tile_frame,bg=f"lightgrey")
            rl_frame = tk.Frame(tile_frame, height=5,width=tile.tkimage.width())
            rlkey_label = tk.Label(tile_frame,text=indexnames[tileindex],width=15) 
            rkey_button = tk.Button(rl_frame,bg=f"lightgrey",text="→")
            lkey_button = tk.Button(rl_frame,bg=f"lightgrey",text="←")
            tile.tkbutton = rfilter_button
            tile.tkpack = rlkey_label
            self.set_filter_text(tile)
            description_label = tk.Label(tile_frame, text=tile.name,wraplength=tile.tkimage.width(),height=2,pady=0)

            tile_label.pack()
            description_label.pack()
            rfilter_button.pack(fill="x")
            rlkey_label.pack(side="top",anchor="center")
            rl_frame.pack(fill="both",expand=True)
            rkey_button.pack(side="right",expand=True,anchor="e")
            lkey_button.pack(side="right",expand=True,anchor="w")
            tile_group_index=self.tile_index[tile.group]
            rows = 5
            tile_frame.grid(row=math.floor(tile_group_index/rows), column=tile_group_index%rows, padx=2, pady=2)
            tile_label.bind("<Button-1>", lambda e, tile_index=i : self.select_tile(tile_index))
            rfilter_button.bind("<Button-1>", lambda e, tile_index=i : self.toggle_filter(tile_index))
            tile_label.bind("<Button-3>", lambda e, tile_index=i : self.deselect_tile(tile_index))
            rkey_button.bind("<Button-1>", lambda e, tile_index=i : self.next_image(tile_index))
            lkey_button.bind("<Button-1>", lambda e, tile_index=i : self.prior_image(tile_index))
            self.tile_index[tile.group] += 1
            tile.tktile = tile_label

            if self.load_filter_state(tile.id) and not tile.nofilter:
                self.toggle_filter(i)
            if self.load_select_state(tile.id):
                self.select_tile(i,True)
            else:
                self.deselect_tile(i,True)

    def deselect_all(self,dispose):
        for i,tile in enumerate(self.tiles):
            self.deselect_tile(i)

    def deselect_tile(self, index,firsttime =False):
        tile:IP.Tile = self.tiles[index]
        if tile.nofilter:
            return
        if tile.selected or firsttime:
            self.tkdarken_tile(tile)
            tile.selected = False
            if tile.id in self.save_data["selected"]:
                self.save_data["selected"].remove(tile.id)

    def tkdarken_tile(self,tile):
        tile_label = tile.tktile
        darkened_tile = self.darken_tile(tile.cleandisplaytiles[tile.selectedindex])
        tile.tkimage = ImageTk.PhotoImage(darkened_tile)
        tile_label.configure(image=tile.tkimage)
        tile.displaytiles[tile.selectedindex] = darkened_tile

    def darken_tile(self, tile):
        enhancer = ImageEnhance.Brightness(tile)
        darkened_tile = enhancer.enhance(1-self.tranp_scroler.get()/100)
        return darkened_tile

    def select_all(self,_):
        for i,tile in enumerate(self.tiles):
            self.select_tile(i)

    def select_tile(self, index, firstime=False):
        tile:IP.Tile = self.tiles[index]
        if tile.nofilter:
            return
        if not tile.selected or firstime:
            tile_label = tile.tktile
            # Darken the tile image by 80% while keeping the current display size
            self.tkhighlighttile(tile)
            tile.selected = True
            if tile.id not in self.save_data["selected"]:
                self.save_data["selected"].append(tile.id)
    
    def toggle_all_filters(self,_):
        tile:IP.Tile
        for i,tile in enumerate(self.tiles):
            if self.Favorites != 0 and not tile.nofilter:
                self.toggle_filter(i)
            elif not self.Favorites and tile.nofilter:
                self.toggle_filter(i)
            if self.load_select_state(tile.id):
                self.select_tile(i,True)
            else:
                self.deselect_tile(i,True)
        if self.Favorites != 0:
            self.toggle_filters.configure(text="Enable Favorites")
            self.save_data["Flabel"] = 0
            self.Favorites = 0
        else:
            self.toggle_filters.configure(text="Disable Favorites")
            self.save_data["Flabel"] = 1
            self.Favorites = 1
       
            
            

    def toggle_filter(self, index):
        tile:IP.Tile = self.tiles[index]

        tile.nofilter = not tile.nofilter

        tile_label = tile.tktile
        # Darken the tile image by 80% while keeping the current display size
        nofilter_tile = tile.cleandisplaytiles[tile.selectedindex]
        tile.tkimage = ImageTk.PhotoImage(nofilter_tile)
        tile_label.configure(image=tile.tkimage)
        tile.displaytiles[tile.selectedindex] = nofilter_tile
        if tile.nofilter and tile.id not in self.save_data["nofilter"]:
            self.save_data["nofilter"].append(tile.id)
        elif not tile.nofilter and tile.id in self.save_data["nofilter"]:
            self.save_data["nofilter"].remove(tile.id)
        self.set_filter_text(tile)
        if not tile.nofilter:
            if tile.selected:
                self.tkhighlighttile(tile)
            else:
                self.tkdarken_tile(tile)

    def next_image(self, index):
        tile:IP.Tile = self.tiles[index]
        tile.selectedindex += 1
        if tile.selectedindex >= len(tile.displaytiles):
            tile.selectedindex = 0
        self.update_selected_tile(tile)

            

    def prior_image(self, index):
        tile:IP.Tile = self.tiles[index]
        tile.selectedindex -= 1
        if tile.selectedindex < 0:
            tile.selectedindex = len(tile.displaytiles) -1
        self.update_selected_tile(tile)

    def apply_all(self,):
        tile:IP.Tile
        for i,tile in enumerate(self.tiles):
            tile.selectedindex = self.drop_down.current()
            self.update_selected_tile(tile)

    def removesheet(self,):
        if self.drop_down.current() == -1:
            return
        archivename = self.tile_index_list[self.drop_down.current()]
        if archivename == "0riginal":
            messagebox.showinfo("Info", "Please dont delete the original archive, it is needed for backups")
            return
        response = messagebox.askyesno("Confirmation", f"Are You sure you want to delete {archivename}?")
        if response:
            patcher.removeArchive(archivename)
            del self.tile_index_list[self.drop_down.current()]
            app.drop_down['values'] = app.tile_index_list
            self.drop_down.current(0)
            
    

    def update_selected_tile(self,tile):
        if not tile.nofilter:
            if tile.selected:
                self.tkhighlighttile(tile)
            else:
                self.tkdarken_tile(tile)
        else:
            nofilter_tile = tile.cleandisplaytiles[tile.selectedindex]
            tile.tkimage = ImageTk.PhotoImage(nofilter_tile)
            tile.tktile.configure(image=tile.tkimage)
        self.save_data["tileindexes"][tile.id] = self.tile_index_list[tile.selectedindex]
        tile.tkpack.configure(text=self.tile_index_list[tile.selectedindex])
        

    def set_filter_text(self, tile:IP.Tile):
        if tile.nofilter == True:
            disptext = "Favorites Filter"
        else:
            disptext = "Remove Filter"
        tile.tkbutton.config(text=disptext)

    def tkhighlighttile(self,tile):
        tile_label = tile.tktile
        highlighted_tile = self.highlighttile(tile.cleandisplaytiles[tile.selectedindex])
        tile.tkimage = ImageTk.PhotoImage(highlighted_tile)
        tile_label.configure(image=tile.tkimage)
        tile.displaytiles[tile.selectedindex] = highlighted_tile


    def highlighttile(self,tile,issave=False):
        image = tile.convert("RGBA")
        glow_size = 20
        if issave:
            glow_color = (142,255,64)
        else:
            glow_color = (255,255,255)
        intensity = self.highlight_scroler.get()/100

        # Extract RGB channels and detect non-black pixels
        np_image = np.array(image)
        non_black_mask = np.any(np_image[:, :, :3] != [0, 0, 0], axis=-1)

        # Create the mask for the sprite region
        mask = Image.fromarray((non_black_mask * 255).astype(np.uint8))
        
        # Expand mask by adding a glow effect using Gaussian blur
        glow_mask = mask.filter(ImageFilter.GaussianBlur(glow_size))

        # Convert the glow mask into a colored glow layer
        glow_layer = Image.new("RGBA", image.size, (*glow_color, 0))
        glow_data = np.array(glow_layer, dtype=np.uint8)

        # Apply glow intensity based on the glow mask values
        glow_alpha = np.array(glow_mask, dtype=np.float32) * (intensity / 255.0)
        glow_data[:, :, 3] = np.clip(glow_alpha * 255, 0, 255).astype(np.uint8)

        # Create the glow effect image
        glow_layer = Image.fromarray(glow_data, "RGBA")

        # Composite the glow layer with the original image
        result = Image.alpha_composite(image, glow_layer)

        return result

    #-----UIactions--------
    def on_dim_move(self,value):
        self.save_data["dim"] = value
        tile:IP.Tile
        for tile in self.tiles:
            if(tile.nofilter):
                continue
            if not tile.selected:
                self.tkdarken_tile(tile)

    def on_high_move(self,value):
        self.save_data["glow"] = value
        tile:IP.Tile
        for tile in self.tiles:
            if(tile.nofilter):
                continue
            if tile.selected:
                self.tkhighlighttile(tile)

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        scroll_amount = -1 if event.num == 5 or event.delta < 0 else 1
        self.canvas.yview_scroll(-1*scroll_amount, "units")
    def open_help_page(self,_):
        readme_path = os.path.join(os.getcwd(), "readme.txt")  # Change to "README.md" if it's markdown
        if os.path.exists(readme_path):
            # Open the file using the system's default text editor
            try:
                if os.name == "nt":  # Windows
                    os.startfile(readme_path)
                elif os.name == "posix":  # macOS/Linux
                    subprocess.run(["xdg-open", readme_path])
            except Exception as e:
                print(f"Error opening README: {e}")
        else:
            print("README file not found.")

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

def newsheet():
    name = simpledialog.askstring("Input", "Enter your sheet name:")
    if name:
        patcher.CopyOG(name)
        findnewarchives()
        createsheetmask(os.path.join(Global_temp_directory,name))

def createsheetmask(newdir):
    for page in allpages:
        image_size = page["SIZE"]
        image_name = f"{page['NAME']}_mask"
        newimg = Image.new('RGBA', image_size, (0, 0, 0, 0))
        for tile in page["DETAILS"]:
            realsize = 264
            dif = int((tile[0][0]-realsize)/2)
            x = tile[0][0]*(tile[1][0]) + tile[0][1]
            y = tile[0][0]*(tile[1][1]) + tile[0][2]
            draw = ImageDraw.Draw(newimg)
            draw.rectangle((x+dif,y+dif,x+tile[0][0]-dif,y+tile[0][0]-dif), fill=(255,255,255,127),outline=(0,0,0,255),width=5)
        newimg.save(os.path.join(newdir, f"{image_name}.png"), "PNG")

def importpack():
    global app
    file_path = filedialog.askopenfilename(
        title="Select a stratagem pack",
        filetypes=[("ZIP Files", "*.zip")],  # Filters to show only .zip files
    )
    if file_path == "":
        return
    Foundarchive = False
    patcher.CopyArchive(file_path)
    findnewarchives()

def findnewarchives():
    arch = patcher.FindArchives(allpages)
    for a in arch:
        patchname = patcher.LoadArchive(a)
        if patchname not in app.tile_index_list:
            Foundarchive = True
            app.tile_index_list.append(patchname)
            app.load_moreimages(patchname,allpages)
    app.drop_down['values'] = app.tile_index_list
    app.drop_down.current(0)  # Set default selection
    if not Foundarchive:
        messagebox.showinfo("Info", "No archive found")


if __name__ == "__main__":
    with HiddenPrints():
        with open(os.path.join(os.path.curdir,"IconData.json"), "r") as json_file:
            allpages = json.load(json_file)
        ogpatch = ""
        root = tk.Tk()
        app = ImageSplitterApp(root)
        patcher.register()
        arch = patcher.FindArchives(allpages)
        firstimage = True
        for a in arch:
            patchname = patcher.LoadArchive(a)
            if patchname not in app.tile_index_list:
                app.tile_index_list.append(patchname)
            if firstimage or patchname == ogpatch:
                app.load_images(patchname,allpages)
                ogpatch = patchname
                firstimage = False
            else:
                app.load_moreimages(patchname,allpages)
        app.display_tiles(app.tile_index_list)
        app.drop_down['values'] = app.tile_index_list
        app.drop_down.current(0)  # Set default selection
        root.mainloop()