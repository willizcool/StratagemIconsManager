from PIL import Image
import numpy as np

TILESIZE = 290
offensecolor = "#9f362d"
supplycolor = "#5186a7"
defensecolor = "#426227"
missioncolor = "#c1b670"
colorindex = ["offense", "supply", "defense", "mission"]
groupcolor = [offensecolor,supplycolor,defensecolor, missioncolor]

class Tile:
    def __init__(self,box,name,group,tile_imgs,displaytile,id):
        self.box = box
        self.name = name
        self.group = group
        self.tile_imgs = [tile_imgs]
        self.displaytiles = [displaytile]
        self.cleandisplaytiles = [displaytile.copy()]
        self.tktile = None
        self.tkbutton = None
        self.tkpack = None
        self.tkimage = None
        self.selected = True
        self.nofilter = False
        self.id = id    
        self.selectedindex = 0
    def addTile(self,tile_imgs,displaytile):
        self.tile_imgs.append(tile_imgs)
        self.displaytiles.append(displaytile)
        self.cleandisplaytiles.append(displaytile.copy())

class Images:
    def __init__(self,img,image_path,sindex):
        self.img = img
        self.image_path = image_path
        self.selectable_indexes = sindex
        self.tiles = []

    def setup_originaltile(self):
        width, height = self.img.size
        for iy,y in enumerate(range(0, height, TILESIZE)):
            for ix,x in enumerate(range(0, width, TILESIZE)):
                name = ""
                group = 0
                xoffset = 0
                yoffset = 0
                for items in self.selectable_indexes:
                    if items[1][0] == iy and items[1][1] == ix:
                        name = items[2][2]
                        group = items[2][1]
                        id = items[2][0]
                        xoffset = items[0][0]
                        yoffset = items[0][1]
                        break
                if name == "":
                    continue
                box = (x+xoffset, y+yoffset, x + TILESIZE + xoffset, y + TILESIZE + yoffset)
                tile_img = self.img.crop(box)

                # Resize tile to 25% of its original size for display
                displayed_tile = tile_img.resize(
                    (TILESIZE // 3, TILESIZE // 3), Image.LANCZOS
                )

                displayed_tile = self.replace_colors(displayed_tile, self.hex_to_rgb("#feffe2"),self.hex_to_rgb(groupcolor[group]))
                
                tile = Tile(box, name, group, tile_img, displayed_tile,id)
                self.tiles.append(tile)

    def split_existing_image(self,newimage):      
        tile :Tile    
        for tile in self.tiles:
            tile_img = newimage.crop(tile.box)
            displayed_tile = tile_img.resize(
                    (TILESIZE // 3, TILESIZE // 3), Image.LANCZOS
                )
            displayed_tile = self.replace_colors(displayed_tile, self.hex_to_rgb("#feffe2"),self.hex_to_rgb(groupcolor[tile.group]))
            tile.addTile(tile_img,displayed_tile)

    def split_image(self):
        for items in self.selectable_indexes:
            name = items[2][2]
            group = colorindex.index(items[2][1])
            id = items[2][0]
            xoffset = items[0][1]
            yoffset = items[0][2]
            gridsize = items[0][0]

            x = gridsize*items[1][0]
            y = gridsize*items[1][1]

            box = (x+xoffset, y+yoffset, x + gridsize + xoffset, y + gridsize + yoffset)
            tile_img = self.img.crop(box)

            # Resize tile to 25% of its original size for display
            displayed_tile = tile_img.resize(
                (TILESIZE // 3, TILESIZE // 3), Image.LANCZOS
            )
            displayed_tile = self.replace_colors(displayed_tile, self.hex_to_rgb("#feffe2"),self.hex_to_rgb(groupcolor[group]))
            
            tile = Tile(box, name, group,tile_img,displayed_tile, id)
            self.tiles.append(tile)
        return self.tiles
    
    def replace_colors(self, tile, green_replacement, red_replacement):
    # Convert the image to numpy array
        image_array = np.array(tile)

        # Create a mask for pixels within the color tolerance
        red = image_array[:, :, 0]
        green = image_array[:, :, 1]
        blue = image_array[:, :, 2]
        blue_mask = (red < 10) & (green < 10) & (blue > 15)
        green_mask = ~blue_mask & (green > 15) & (green > red + 40) & (red < 200)
        red_mask = ~green_mask
        
        

        # Apply the replacement color to the masked pixels
        # Ensure the replacement color is broadcasted correctly
        replacement_scaled = green_replacement * (image_array[:, :, 1] / 255.0)[:, :, np.newaxis]
        replacement_scaled2 = red_replacement * (image_array[:, :, 0] / 255.0)[:, :, np.newaxis]

        # Replace pixels in the image array
        image_array[green_mask] = replacement_scaled[green_mask]
        image_array[red_mask] = replacement_scaled2[red_mask]

        image_array[:,:,3] = 255 

        # Convert back to Image for further processing or display
        return Image.fromarray(image_array)
    
    def replace_color_red_group(self, tile, target_color, replacement_color):
    # Convert the image to numpy array
        image_array = np.array(tile)

        # Compute the color difference
        diff = np.abs(image_array - target_color)

        # Create a mask for pixels within the color tolerance
        mask = np.all(diff < 200, axis=-1)

        # Replace target color pixels with the replacement color
        image_array[mask] = replacement_color

        # Convert back to Image for further processing or display
        return Image.fromarray(image_array)
    
    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        rgb_values = [int(hex_color[i:i + 2], 16) for i in (0, 2, 4)] + [255]
        return np.array(rgb_values, dtype=np.uint8)