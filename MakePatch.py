import os, streamToc, subprocess, shutil, json, uuid
from streamToc import TexID, MaterialID, MeshID, CompositeMeshID
from memoryStream import MemoryStream
from pathlib import Path
import zipfile, re
from PIL import Image
import imageio.v2 as imageio

from copy import deepcopy

# # Blender


ExePath = os.path.abspath(os.path.curdir)
AddonPath = os.path.join(ExePath,"resource")
Global_mod_name          = "StratagemIconsManagerCustomMod"
Global_modpath           = os.path.join(ExePath)
Global_filehashpath      = f"{AddonPath}\\hashlists\\filehash.txt"
Global_typehashpath      = f"{AddonPath}\\hashlists\\typehash.txt"
Global_friendlynamespath = f"{AddonPath}\\hashlists\\friendlynames.txt"
Global_depspath          = f"{AddonPath}\\deps"
Global_archive_path      = os.path.join(AddonPath,"archives")
Global_temp_directory    = os.path.join(ExePath,"EditableSheets")

if not os.path.exists(Global_temp_directory):
    os.makedirs(Global_temp_directory)

Global_MaterialParentIDs = {
    3430705909399566334 : "basic+",
    15586118709890920288 : "alphaclip",
    6101987038150196875 : "original",
    15356477064658408677 : "basic",
    15235712479575174153 : "emissive"
}


Global_TypeHashes = []
def LoadTypeHashes():
    with open(Global_typehashpath, 'r') as f:
        for line in f.readlines():
            parts = line.split(" ")
            Global_TypeHashes.append([int(parts[0], 16), parts[1].replace("\n", "")])
Global_NameHashes = []

def LoadNameHashes():
    Loaded = []
    with open(Global_filehashpath, 'r') as f:
        for line in f.readlines():
            parts = line.split(" ")
            Global_NameHashes.append([int(parts[0]), parts[1].replace("\n", "")])
            Loaded.append(int(parts[0]))
    with open(Global_friendlynamespath, 'r') as f:
        for line in f.readlines():
            parts = line.split(" ", 1)
            if int(parts[0]) not in Loaded:
                Global_NameHashes.append([int(parts[0]), parts[1].replace("\n", "")])
                Loaded.append(int(parts[0]))

Global_ArchiveHashes = []
def LoadHash(path, title):
    with open(path, 'r') as f:
        for line in f.readlines():
            parts = line.split(" ", 1)
            Global_ArchiveHashes.append([parts[0], title + parts[1].replace("\n", "")])

def register():
    LoadTypeHashes()
    LoadNameHashes()

def texture_export_png(exportlocation,object_id,backuplocation):
        Global_TocManager.Load(int(object_id), TexID)
        Entry = Global_TocManager.GetEntry(int(object_id), TexID)
        if Entry != None:
            tempdir = Global_temp_directory
            filepath = exportlocation
            filename = filepath.split("\-".replace("-", ""))[-1]
            directory = filepath.replace(filename, "")
            filename = filename.replace(".png", "")
            dds_path = f"{tempdir}\\{filename}.dds"
            with open(dds_path, 'w+b') as f:
                f.write(Entry.LoadedData.ToDDS())
            image = imageio.imread(dds_path)
            Image.fromarray(image).save(directory + filename + ".png")
            # subprocess.run(
            #     [Global_texconvpath, "-y", "-o", directory, "-ft", "png", "-f", "R8G8B8A8_UNORM", dds_path],
            #     stdout=subprocess.DEVNULL,
            #     stderr=subprocess.DEVNULL,
            #     creationflags=subprocess.CREATE_NO_WINDOW  # Prevents terminal pop-up
            # )
            os.remove(dds_path)
        else:
            shutil.copy(backuplocation, exportlocation)#in case archive doesnt contain an image

        return{'FINISHED'}

#-----------TocManager---------

def GetArchiveNameFromID(EntryID):
    for hash in Global_ArchiveHashes:
        if hash[0] == EntryID:
            return hash[1]
    return ""

def GetEntryParentMaterialID(entry):
    if entry.TypeID == MaterialID:
        f = MemoryStream(entry.TocData)
        for i in range(6):
            f.uint32(0)
        parentID = f.uint64(0)
        return parentID
    else:
        raise Exception(f"Entry: {entry.FileID} is not a material")
    
def SaveImagePNG(filepath, object_id):
    Entry = Global_TocManager.GetEntry(int(object_id), TexID)
    if Entry != None:
        if len(filepath) > 1:
            # get texture data
            Entry.Load()
            StingrayTex = Entry.LoadedData
            tempdir = Global_temp_directory
            print(filepath)
            image = Image.open(filepath)
            image.save(tempdir + ".png")
            nameIndex = filepath.rfind("\.".strip(".")) + 1
            fileName = filepath[nameIndex:].replace(".png", ".dds")
            dds_path = f"{tempdir}\\{fileName}"
            print(dds_path)
            with open(dds_path, 'r+b') as f:
                StingrayTex.FromDDS(f.read())
            Toc = MemoryStream(IOMode="write")
            Gpu = MemoryStream(IOMode="write")
            Stream = MemoryStream(IOMode="write")
            StingrayTex.Serialize(Toc, Gpu, Stream)
            # add texture to entry
            Entry.SetData(Toc.Data, Gpu.Data, Stream.Data, False)
            Global_TocManager.Save(int(object_id), TexID)

class TocManager():
    def __init__(self):
        self.SearchArchives  = []
        self.LoadedArchives  = []
        self.ActiveArchive   = None
        self.Patches         = []
        self.ActivePatch     = None

        self.CopyBuffer      = []
        self.SelectedEntries = []
        self.DrawChain       = []
        self.LastSelected = None # Last Entry Manually Selected
        self.SavedFriendlyNames   = []
        self.SavedFriendlyNameIDs = []
    
    def Load(self, FileID, TypeID, Reload=False, SearchAll=False):
        Entry = self.GetEntry(FileID, TypeID, SearchAll)
        if Entry != None: Entry.Load(Reload)

    def Save(self, FileID, TypeID):
        #ApplyAllTransforms(self, FileID)
        Entry = self.GetEntry(FileID, TypeID)
        if Entry == None:
            print(f"Failed to save entry {FileID}")
            return False
        if not Global_TocManager.IsInPatch(Entry):
            Entry = self.AddEntryToPatch(FileID, TypeID)
        Entry.Save()
        return True
    
    def ArchiveNotEmpty(self, toc):
        hasMaterials = False
        hasTextures = False
        hasMeshes = False
        for Entry in toc.TocEntries:
            type = Entry.TypeID
            if type == MaterialID:
                hasMaterials = True
            elif type == MeshID:
                hasMeshes = True
            elif type == TexID:
                hasTextures = True
            elif type == CompositeMeshID:
                hasMeshes = True
        return hasMaterials or hasTextures or hasMeshes

    def LoadArchive(self, path, SetActive=True, IsPatch=False):
        for Archive in self.LoadedArchives:
            if Archive.Path == path:
                return Archive
        archiveID = path.replace(Global_archive_path, '')
        archiveName = GetArchiveNameFromID(archiveID)
        print(f"Loading Archive: {archiveID} {archiveName}")
        toc = streamToc.StreamToc()
        toc.FromFile(path)
        if SetActive and not IsPatch:
            if self.ArchiveNotEmpty(toc):
                self.LoadedArchives.append(toc)
                self.ActiveArchive = toc
            else:
                print(f"Unloading {archiveID} as it is Empty")
        elif SetActive and IsPatch:
            self.Patches.append(toc)
            self.ActivePatch = toc

            for entry in self.ActivePatch.TocEntries:
                if entry.TypeID == MaterialID:
                    ID = GetEntryParentMaterialID(entry)
                    if ID in Global_MaterialParentIDs:
                        entry.MaterialTemplate = Global_MaterialParentIDs[ID]
                        entry.Load()
                        print(f"Creating Material: {entry.FileID} Template: {entry.MaterialTemplate}")
                    else:
                        print(f"Material: {entry.FileID} Parent ID: {ID} is not an custom material, skipping.")

        # Get search archives
        if len(self.SearchArchives) == 0:
            for root, dirs, files in os.walk(Path(path).parent):
                for name in files:
                    if Path(name).suffix == "":
                        search_toc = streamToc.StreamToc()
                        success = search_toc.FromFile(os.path.join(root, name), False)
                        if success:
                            self.SearchArchives.append(search_toc)

        return toc
    
    def GetEntry(self, FileID, TypeID, SearchAll=False, IgnorePatch=False):
        # Check Active Patch
        if not IgnorePatch and self.ActivePatch != None:
            Entry = self.ActivePatch.GetEntry(FileID, TypeID)
            if Entry != None:
                return Entry
        # Check Active Archive
        if self.ActiveArchive != None:
            Entry = self.ActiveArchive.GetEntry(FileID, TypeID)
            if Entry != None:
                return Entry
        # Check All Loaded Archives
        for Archive in self.LoadedArchives:
            Entry = Archive.GetEntry(FileID, TypeID)
            if Entry != None:
                return Entry
        # Check All Search Archives
        if SearchAll:
            for Archive in self.SearchArchives:
                Entry = Archive.GetEntry(FileID, TypeID)
                if Entry != None:
                    return self.LoadArchive(Archive.Path, False).GetEntry(FileID, TypeID)
        return None
    
    def DeselectAll(self):
        for Entry in self.SelectedEntries:
            Entry.IsSelected = False
        self.SelectedEntries = []
        self.LastSelected = None
    
    def SelectEntries(self, Entries, Append=False):
        if not Append: self.DeselectAll()
        if len(Entries) == 1:
            Global_TocManager.LastSelected = Entries[0]

        for Entry in Entries:
            if Entry not in self.SelectedEntries:
                Entry.IsSelected = True
                self.SelectedEntries.append(Entry)
    
    def IsInPatch(self, Entry):
        if self.ActivePatch != None:
            PatchEntry = self.ActivePatch.GetEntry(Entry.FileID, Entry.TypeID)
            if PatchEntry != None: return True
            else: return False
        return False
    
    def CreatePatchFromActive(self, name="New Patch"):
        if self.ActiveArchive == None:
            raise Exception("No Archive exists to create patch from, please open one first")

        self.ActivePatch = deepcopy(self.ActiveArchive)
        self.ActivePatch.TocEntries  = []
        self.ActivePatch.TocTypes    = []
        # TODO: ask for which patch index
        splitpath = self.ActiveArchive.Path
        parts = splitpath.split(os.sep)
        archive_index = parts.index("archives")
        path = os.sep.join(parts[:archive_index + 1])
        path = os.path.join(path,parts[-1])
        path += ".patch_0"
        self.ActivePatch.UpdatePath(path)
        self.ActivePatch.LocalName = name
        print(self.ActivePatch.LocalName)
        self.Patches.append(self.ActivePatch)
    
    def AddEntryToPatch(self, FileID, TypeID):
        if self.ActivePatch == None:
            raise Exception("No patch exists, please create one first")

        Entry = self.GetEntry(FileID, TypeID)
        if Entry != None:
            PatchEntry = deepcopy(Entry)
            if PatchEntry.IsSelected:
                self.SelectEntries([PatchEntry], True)
            self.ActivePatch.AddEntry(PatchEntry)
            return PatchEntry
        return None
    
    def PatchActiveArchive(self):
        self.ActivePatch.ToFile()
    
    def SetActivePatch(self, Patch):
        self.ActivePatch = Patch

def SaveUnsavedEntries():
    for Entry in Global_TocManager.ActivePatch.TocEntries:
        if not Entry.IsModified:
            Global_TocManager.Save(int(Entry.FileID), Entry.TypeID)
            print(f"Saved {int(Entry.FileID)}")

def find_patch_files(directory,archives):
    archivenames = []
    for each in archives:
        if each["ARCHIVENAME"] not in archivenames:
            archivenames.append(each["ARCHIVENAME"])
    archives = []
    for each in archivenames:
        archives.extend(
            str(file.resolve())
            for file in Path(directory).rglob(f"*{each}*")
            if not file.name.endswith(".gpu_resources") and not file.name.endswith(".stream")
        )


    return archives
def clean_folder_name(name):
    """Removes leading numbers and symbols from a filename."""
    return re.sub(r'^[^a-zA-Z]+', '', name)  # Remove non-letter characters at the start

def unzip_and_clean(folder_path):
    # Get all .zip files in the folder
    zip_files = [f for f in os.listdir(folder_path) if f.endswith(".zip")]

    for zip_file in zip_files:
        zip_path = os.path.join(folder_path, zip_file)
        
        # Extract base name and clean it
        base_name = os.path.splitext(zip_file)[0]  # Remove .zip extension
        clean_name = clean_folder_name(base_name)  # Clean leading numbers/symbols
        
        extract_folder = os.path.join(folder_path, clean_name)

        # Create extraction folder if not exists
        os.makedirs(extract_folder, exist_ok=True)

        # Extract .zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)

        # Delete original .zip file
        os.remove(zip_path)

def rename_folders(folder_path):
    """Finds and renames all folders in the given directory."""
    for folder in os.listdir(folder_path):
        if folder == "0riginal":
            continue
        folder_full_path = os.path.join(folder_path, folder)

        if os.path.isdir(folder_full_path):  # Check if it's a folder
            clean_name = clean_folder_name(folder)

            if clean_name and clean_name != folder:  # Avoid renaming if it's the same
                new_path = os.path.join(folder_path, clean_name)
                os.rename(folder_full_path, new_path)

def CopyOG(newName):
    newdir = os.path.join(Global_archive_path,newName)
    count = 0
    while os.path.exists(newdir):
        newdir = os.path.join(Global_archive_path, f"{newName}{count}")
        count += 1
    for folder in os.listdir(Global_archive_path):
        if folder == "0riginal":
            break
    original_dir = os.path.join(Global_archive_path,folder)
    shutil.copytree(original_dir,newdir)
    return newdir

def removeArchive(archive_name):
    removedir = os.path.join(Global_archive_path,archive_name)
    shutil.rmtree(removedir)

def CopyArchive(file_path):
    shutil.copy(file_path,Global_archive_path)

def FindArchives(archivenames):
    unzip_and_clean(Global_archive_path)
    rename_folders(Global_archive_path)
    return find_patch_files(Global_archive_path,archivenames)



def LoadArchive(archivename):
    Global_TocManager.LoadArchive(os.path.join(Global_archive_path,archivename), SetActive=True, IsPatch=False)
    return Path(archivename).parts[len(Path(archivename).parts)-2]

def GetActiveArchive():
    return Global_TocManager.ActiveArchive.Name

backuppath = {}
def LoadImage(patchname,imageName):
    global backuppath
    imagepath = os.path.join(Global_temp_directory,patchname,imageName+".png")
    os.makedirs(os.path.dirname(imagepath), exist_ok=True)
    if imageName not in backuppath:
        backuppath[imageName] = [imagepath]
    if not os.path.exists(imagepath):
        texture_export_png(imagepath,imageName,backuppath[imageName])
    return imagepath

def GetImageLocation():
    return Global_temp_directory

def PrepPatch():
    Global_TocManager.SetActivePatch(Global_TocManager.LoadedArchives[0])
    Global_TocManager.CreatePatchFromActive()


def Overwriteimage(imageName):
    SaveImagePNG(os.path.join(Global_temp_directory,imageName+"_new.png"), imageName)

def generate_manifest(name):
    manifest_location = os.path.join(Global_depspath,"manifest.json")
    """Generates a manifest.json file with a random GUID and the given name."""
    manifest_data = {
        "Guid": str(uuid.uuid4()),  # Generate a random UUID (v4)
        "Name": name,
        "Description": "Custom Mod built by Stratagem Manager",
        "IconPath": "Helldivers.ico"
    }

    with open(manifest_location, "w", encoding="utf-8") as file:
        json.dump(manifest_data, file, indent=4)

def CreatePatch(name):
    SaveUnsavedEntries()
    generate_manifest(name)
    Global_TocManager.PatchActiveArchive()
    with zipfile.ZipFile(os.path.join(Global_modpath,name+".zip"), 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(os.path.join(Global_depspath,"Helldivers.ico"),"Helldivers.ico")
        zipf.write(os.path.join(Global_depspath,"manifest.json"),"manifest.json")
        for root, _, files in os.walk(Global_archive_path):
            for file in files:
                if file.endswith('.stream'):
                    continue  # Skip this file
                file_path = os.path.join(root, file)
                if Global_TocManager.ActivePatch.Path in file_path:
                    zipf.write(file_path, os.path.relpath(file_path.replace(".patch_0.patch_0", ".patch_0"), Global_archive_path))

    for root, _, files in os.walk(Global_archive_path):    
        for file in files:
            file_path = os.path.join(root, file)
            if Global_TocManager.ActivePatch.Path in file_path:
                os.remove(file_path)
Global_TocManager = TocManager()
    