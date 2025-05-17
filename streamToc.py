import os
from memoryStream import MemoryStream
from pathlib import Path

import math, subprocess

import bpy, bmesh, mathutils
import imageio.v2 as imageio
from PIL import Image
#from bpy_extras.io_utils import ImportHelper, ExportHelper
#from bpy.props import StringProperty, BoolProperty, IntProperty, EnumProperty, PointerProperty, CollectionProperty
#from bpy.types import Panel, Operator, PropertyGroup, Scene, Menu

#import bpy.types as bpy_types

CompositeMeshID = 14191111524867688662
MeshID = 16187218042980615487
TexID  = 14790446551990181426
MaterialID  = 16915718763308572383
BoneID  = 1792059921637536489
WwiseBankID = 6006249203084351385
WwiseDepID  = 12624162998411505776
WwiseStreamID  = 5785811756662211598
WwiseMetaDataID  = 15351235653606224144

AddonPath = os.path.join(os.path.abspath(os.path.curdir),"resource")
Global_temp_directory    = os.path.join(AddonPath,"temp")

def DXGI_FORMAT(format):
    Dict = {0: "UNKNOWN", 1: "R32G32B32A32_TYPELESS", 2: "R32G32B32A32_FLOAT", 3: "R32G32B32A32_UINT", 4: "R32G32B32A32_SINT", 5: "R32G32B32_TYPELESS", 6: "R32G32B32_FLOAT", 7: "R32G32B32_UINT", 8: "R32G32B32_SINT", 9: "R16G16B16A16_TYPELESS", 10: "R16G16B16A16_FLOAT", 11: "R16G16B16A16_UNORM", 12: "R16G16B16A16_UINT", 13: "R16G16B16A16_SNORM", 14: "R16G16B16A16_SINT", 15: "R32G32_TYPELESS", 16: "R32G32_FLOAT", 17: "R32G32_UINT", 18: "R32G32_SINT", 19: "R32G8X24_TYPELESS", 20: "D32_FLOAT_S8X24_UINT", 21: "R32_FLOAT_X8X24_TYPELESS", 22: "X32_TYPELESS_G8X24_UINT", 23: "R10G10B10A2_TYPELESS", 24: "R10G10B10A2_UNORM", 25: "R10G10B10A2_UINT", 26: "R11G11B10_FLOAT", 27: "R8G8B8A8_TYPELESS", 28: "R8G8B8A8_UNORM", 29: "R8G8B8A8_UNORM_SRGB", 30: "R8G8B8A8_UINT", 31: "R8G8B8A8_SNORM", 32: "R8G8B8A8_SINT", 33: "R16G16_TYPELESS", 34: "R16G16_FLOAT", 35: "R16G16_UNORM", 36: "R16G16_UINT", 37: "R16G16_SNORM", 38: "R16G16_SINT", 39: "R32_TYPELESS", 40: "D32_FLOAT", 41: "R32_FLOAT", 42: "R32_UINT", 43: "R32_SINT", 44: "R24G8_TYPELESS", 45: "D24_UNORM_S8_UINT", 46: "R24_UNORM_X8_TYPELESS", 47: "X24_TYPELESS_G8_UINT", 48: "R8G8_TYPELESS", 49: "R8G8_UNORM", 50: "R8G8_UINT", 51: "R8G8_SNORM", 52: "R8G8_SINT", 53: "R16_TYPELESS", 54: "R16_FLOAT", 55: "D16_UNORM", 56: "R16_UNORM", 57: "R16_UINT", 58: "R16_SNORM", 59: "R16_SINT", 60: "R8_TYPELESS", 61: "R8_UNORM", 62: "R8_UINT", 63: "R8_SNORM", 64: "R8_SINT", 65: "A8_UNORM", 66: "R1_UNORM", 67: "R9G9B9E5_SHAREDEXP", 68: "R8G8_B8G8_UNORM", 69: "G8R8_G8B8_UNORM", 70: "BC1_TYPELESS", 71: "BC1_UNORM", 72: "BC1_UNORM_SRGB", 73: "BC2_TYPELESS", 74: "BC2_UNORM", 75: "BC2_UNORM_SRGB", 76: "BC3_TYPELESS", 77: "BC3_UNORM", 78: "BC3_UNORM_SRGB", 79: "BC4_TYPELESS", 80: "BC4_UNORM", 81: "BC4_SNORM", 82: "BC5_TYPELESS", 83: "BC5_UNORM", 84: "BC5_SNORM", 85: "B5G6R5_UNORM", 86: "B5G5R5A1_UNORM", 87: "B8G8R8A8_UNORM", 88: "B8G8R8X8_UNORM", 89: "R10G10B10_XR_BIAS_A2_UNORM", 90: "B8G8R8A8_TYPELESS", 91: "B8G8R8A8_UNORM_SRGB", 92: "B8G8R8X8_TYPELESS", 93: "B8G8R8X8_UNORM_SRGB", 94: "BC6H_TYPELESS", 95: "BC6H_UF16", 96: "BC6H_SF16", 97: "BC7_TYPELESS", 98: "BC7_UNORM", 99: "BC7_UNORM_SRGB", 100: "AYUV", 101: "Y410", 102: "Y416", 103: "NV12", 104: "P010", 105: "P016", 106: "420_OPAQUE", 107: "YUY2", 108: "Y210", 109: "Y216", 110: "NV11", 111: "AI44", 112: "IA44", 113: "P8", 114: "A8P8", 115: "B4G4R4A4_UNORM", 130: "P208", 131: "V208", 132: "V408"}
    return Dict[format]

class StingrayMipmapInfo:
    def __init__(self):
        self.Start     = self.BytesLeft = self.Height = self.Width  = 0
    def Serialize(self, Toc):
        self.Start      = Toc.uint32(self.Start)
        self.BytesLeft  = Toc.uint32(self.BytesLeft)
        self.Height     = Toc.uint16(self.Height)
        self.Width      = Toc.uint16(self.Width)
        return self

def SaveStingrayTexture(self, ID, TocData, GpuData, StreamData, LoadedData):
    exists = True
    try: bpy.data.images[str(ID)]
    except: exists = False

    Toc = MemoryStream(IOMode="write")
    Gpu = MemoryStream(IOMode="write")
    Stream = MemoryStream(IOMode="write")

    LoadedData.Serialize(Toc, Gpu, Stream)

    return [Toc.Data, Gpu.Data, Stream.Data]

class StingrayTexture:
    def __init__(self):
        self.UnkID = self.Unk1  = self.Unk2  = 0
        self.MipMapInfo = []

        self.ddsHeader = bytearray(148)
        self.rawTex    = b""

        self.Format     = ""
        self.Width      = 0
        self.Height     = 0
        self.NumMipMaps = 0
    def Serialize(self, Toc, Gpu, Stream):
        # clear header, so we dont have to deal with the .stream file
        if Toc.IsWriting():
            self.Unk1 = 0; self.Unk2  = 0xFFFFFFFF
            self.MipMapInfo = [StingrayMipmapInfo() for n in range(15)]

        self.UnkID = Toc.uint32(self.UnkID)
        self.Unk1  = Toc.uint32(self.Unk1)
        self.Unk2  = Toc.uint32(self.Unk2)
        if Toc.IsReading(): self.MipMapInfo = [StingrayMipmapInfo() for n in range(15)]
        self.MipMapInfo = [mipmapInfo.Serialize(Toc) for mipmapInfo in self.MipMapInfo]
        self.ddsHeader  = Toc.bytes(self.ddsHeader, 148)
        self.ParseDDSHeader()

        if Toc.IsWriting():
            Gpu.bytes(self.rawTex)
        else:# IsReading
            if len(Stream.Data) > 0:
                self.rawTex = Stream.Data
            else:
                self.rawTex = Gpu.Data

    def ToDDS(self):
        return self.ddsHeader + self.rawTex
    
    def FromDDS(self, dds):
        self.ddsHeader = dds[:148]
        self.rawTex    = dds[148::]
    
    def ParseDDSHeader(self):
        dds = MemoryStream(self.ddsHeader, IOMode="read")
        dds.seek(84)
        Header = dds.read(4)
        DX10Header = b"DX10"
        if Header != DX10Header:
            raise Exception(f"DDS must use dx10 extended header. Got: {Header}")
        dds.seek(12)
        self.Height = dds.uint32(0)
        self.Width  = dds.uint32(0)
        dds.seek(28)
        self.NumMipMaps = dds.uint32(0)
        dds.seek(128)
        self.Format = DXGI_FORMAT(dds.uint32(0))

def LoadStingrayTexture(ID, TocData, GpuData, StreamData, Reload, MakeBlendObject):
    exists = True
    try: bpy.data.images[str(ID)]
    except: exists = False

    StingrayTex = StingrayTexture()
    StingrayTex.Serialize(MemoryStream(TocData), MemoryStream(GpuData), MemoryStream(StreamData))
    dds = StingrayTex.ToDDS()

    if MakeBlendObject and not (exists and not Reload):
        tempdir = os.path.join(os.path.curdir,"images")
        dds_path = os.path.join(Global_temp_directory,"{ID}.dds")
        png_path = os.path.join(Global_temp_directory,"{ID}.png")

        with open(dds_path, 'w+b') as f:
            f.write(dds)
        image = imageio.imread(dds_path)
        Image.fromarray(image).save(png_path)
    return StingrayTex

class TocEntry:
    def __init__(self):
        self.FileID = self.TypeID = self.TocDataOffset = self.Unknown1 = self.GpuResourceOffset = self.Unknown2 = self.TocDataSize = self.GpuResourceSize = self.EntryIndex = self.StreaMemoryStreamize = self.StreamOffset = 0
        self.Unknown3 = 16
        self.Unknown4 = 64

        self.TocData =  self.TocData_OLD = b""
        self.GpuData =  self.GpuData_OLD = b""
        self.StreamData =  self.StreamData_OLD = b""

        # Custom Dev stuff
        self.LoadedData = None
        self.IsLoaded   = False
        self.IsModified = False
        self.IsCreated  = False # custom created, can be removed from archive
        self.IsSelected = False
        self.MaterialTemplate = None # for determining tuple to use for labeling textures in the material editor
        self.DEV_DrawIndex = -1
        self.VertexGroups = []
        self.TransforMemoryStream = []

    def Serialize(self, TocFile, Index=0):
        self.FileID             = TocFile.uint64(self.FileID)
        self.TypeID             = TocFile.uint64(self.TypeID)
        self.TocDataOffset      = TocFile.uint64(self.TocDataOffset)
        self.StreamOffset       = TocFile.uint64(self.StreamOffset)
        self.GpuResourceOffset  = TocFile.uint64(self.GpuResourceOffset)
        self.Unknown1           = TocFile.uint64(self.Unknown1)
        self.Unknown2           = TocFile.uint64(self.Unknown2)
        self.TocDataSize        = TocFile.uint32(len(self.TocData))
        self.StreaMemoryStreamize         = TocFile.uint32(len(self.StreamData))
        self.GpuResourceSize    = TocFile.uint32(len(self.GpuData))
        self.Unknown3           = TocFile.uint32(self.Unknown3)
        self.Unknown4           = TocFile.uint32(self.Unknown4)
        self.EntryIndex         = TocFile.uint32(Index)
        return self
    
    def Load(self, Reload=False, MakeBlendObject=True):
        callback = None
        if self.TypeID == TexID: callback = LoadStingrayTexture
        if callback != None:
            self.LoadedData = callback(self.FileID, self.TocData, self.GpuData, self.StreamData, Reload, False)
            if self.LoadedData == None: raise Exception("Archive Entry Load Failed")
            self.IsLoaded   = True
            if self.TypeID == MeshID and not self.IsModified:
                for object in bpy.data.objects:
                    try:
                        objectID = object["Z_ObjectID"]
                        infoIndex = object["MeshInfoIndex"]
                        if objectID == str(self.FileID):
                            print(f"Writing Vertex Groups for {object.name}")
                            vertexNames = []
                            for group in object.vertex_groups:
                                vertexNames.append(group.name)
                            newGroups = [objectID, infoIndex, vertexNames]
                            if newGroups not in self.VertexGroups:
                                self.VertexGroups.append(newGroups)
                            print(self.VertexGroups)
                            print(f"Writing TransforMemoryStream for {object.name}")
                            transforMemoryStream = []
                            transforMemoryStream.append(object.location)
                            transforMemoryStream.append(object.rotation_euler)
                            transforMemoryStream.append(object.scale)
                            objectTransforMemoryStream = [objectID, infoIndex, transforMemoryStream]
                            if objectTransforMemoryStream not in self.TransforMemoryStream:
                                self.TransforMemoryStream.append(objectTransforMemoryStream)
                            print(self.TransforMemoryStream)
                    except:
                        print(f"Object: {object.name} has No HD2 Properties")
        else: raise Exception("Load Callback could not be found")
    def Save(self):
        if not self.IsLoaded: self.Load(True, False)
        if self.TypeID == TexID: callback = SaveStingrayTexture
        if callback == None: raise Exception("Save Callback could not be found")

        if self.IsLoaded:
            data = callback(self, self.FileID, self.TocData, self.GpuData, self.StreamData, self.LoadedData)
            self.SetData(data[0], data[1], data[2])
    def SetData(self, TocData, GpuData, StreamData, IsModified=True):
        self.TocData = TocData
        self.GpuData = GpuData
        self.StreamData = StreamData
        self.TocDataSize     = len(self.TocData)
        self.GpuResourceSize = len(self.GpuData)
        self.StreaMemoryStreamize      = len(self.StreamData)
        self.IsModified = IsModified
    
    def SerializeData(self, TocFile, GpuFile, StreamFile):
        if TocFile.IsReading():
            TocFile.seek(self.TocDataOffset)
            self.TocData = bytearray(self.TocDataSize)
        elif TocFile.IsWriting():
            self.TocDataOffset = TocFile.tell()
        self.TocData = TocFile.bytes(self.TocData)

        if GpuFile.IsWriting(): self.GpuResourceOffset = math.ceil(float(GpuFile.tell())/64)*64
        if self.GpuResourceSize > 0:
            GpuFile.seek(self.GpuResourceOffset)
            if GpuFile.IsReading(): self.GpuData = bytearray(self.GpuResourceSize)
            self.GpuData = GpuFile.bytes(self.GpuData)

        if StreamFile.IsWriting(): self.StreamOffset = math.ceil(float(StreamFile.tell())/64)*64
        if self.StreaMemoryStreamize > 0:
            StreamFile.seek(self.StreamOffset)
            if StreamFile.IsReading(): self.StreamData = bytearray(self.StreaMemoryStreamize)
            self.StreamData = StreamFile.bytes(self.StreamData)
        if GpuFile.IsReading():
            self.TocData_OLD    = bytearray(self.TocData)
            self.GpuData_OLD    = bytearray(self.GpuData)
            self.StreamData_OLD = bytearray(self.StreamData)

class TocFileType:
    def __init__(self, ID=0, NumFiles=0):
        self.unk1     = 0
        self.TypeID   = ID
        self.NumFiles = NumFiles
        self.unk2     = 16
        self.unk3     = 64
    def Serialize(self, TocFile):
        self.unk1     = TocFile.uint64(self.unk1)
        self.TypeID   = TocFile.uint64(self.TypeID)
        self.NumFiles = TocFile.uint64(self.NumFiles)
        self.unk2     = TocFile.uint32(self.unk2)
        self.unk3     = TocFile.uint32(self.unk3)
        return self

class StreamToc:
    def __init__(self):
        self.magic      = self.numTypes = self.numFiles = self.unknown = 0
        self.unk4Data   = bytearray(56)
        self.TocTypes   = []
        self.TocEntries = []
        self.Path = ""
        self.Name = ""
        self.LocalName = ""
    def FromFile(self, path, SerializeData=True):
        self.UpdatePath(path)
        with open(path, 'r+b') as f:
            self.TocFile = MemoryStream(f.read())

        self.GpuFile    = MemoryStream()
        self.StreamFile = MemoryStream()
        if SerializeData:
            if os.path.isfile(path+".gpu_resources"):
                with open(path+".gpu_resources", 'r+b') as f:
                    self.GpuFile = MemoryStream(f.read())
            if os.path.isfile(path+".stream"):
                with open(path+".stream", 'r+b') as f:
                    self.StreamFile = MemoryStream(f.read())
        return self.Serialize(SerializeData)
    def ToFile(self, path=None):
        self.TocFile = MemoryStream(IOMode = "write")
        self.GpuFile = MemoryStream(IOMode = "write")
        self.StreamFile = MemoryStream(IOMode = "write")
        self.Serialize()
        if path == None: path = self.Path

        with open(path, 'w+b') as f:
            f.write(bytes(self.TocFile.Data))
        with open(path+".gpu_resources", 'w+b') as f:
            f.write(bytes(self.GpuFile.Data))
        with open(path+".stream", 'w+b') as f:
            f.write(bytes(self.StreamFile.Data))
    def UpdatePath(self, path):
        self.Path = path
        self.Name = Path(path).name
    def Serialize(self, SerializeData=True):
        # Create Toc Types Structs
        if self.TocFile.IsWriting():
            self.UpdateTypes()
        # Begin Serializing file
        self.magic      = self.TocFile.uint32(self.magic)
        if self.magic != 4026531857: return False

        self.numTypes   = self.TocFile.uint32(len(self.TocTypes))
        self.numFiles   = self.TocFile.uint32(len(self.TocEntries))
        self.unknown    = self.TocFile.uint32(self.unknown)
        self.unk4Data   = self.TocFile.bytes(self.unk4Data, 56)

        if self.TocFile.IsReading():
            self.TocTypes   = [TocFileType() for n in range(self.numTypes)]
            self.TocEntries = [TocEntry() for n in range(self.numFiles)]
        # serialize Entries in correct order
        self.TocTypes   = [Entry.Serialize(self.TocFile) for Entry in self.TocTypes]
        TocEntryStart   = self.TocFile.tell()
        if self.TocFile.IsReading(): self.TocEntries = [Entry.Serialize(self.TocFile) for Entry in self.TocEntries]
        else:
            Index = 1
            for Type in self.TocTypes:
                for Entry in self.TocEntries:
                    if Entry.TypeID == Type.TypeID:
                        Entry.Serialize(self.TocFile, Index)
                        Index += 1

        # Serialize Data
        if SerializeData:
            for FileEntry in self.TocEntries:
                FileEntry.SerializeData(self.TocFile, self.GpuFile, self.StreamFile)

        # re-write toc entry info with updated offsets
        if self.TocFile.IsWriting():
            self.TocFile.seek(TocEntryStart)
            Index = 1
            for Type in self.TocTypes:
                for Entry in self.TocEntries:
                    if Entry.TypeID == Type.TypeID:
                        Entry.Serialize(self.TocFile, Index)
                        Index += 1
        return True
    
    def GetEntry(self, FileID, TypeID):
        for Entry in self.TocEntries:
            if Entry.FileID == int(FileID) and Entry.TypeID == TypeID:
                return Entry
        return None
    
    def UpdateTypes(self):
        self.TocTypes = []
        for Entry in self.TocEntries:
            exists = False
            for Type in self.TocTypes:
                if Type.TypeID == Entry.TypeID:
                    Type.NumFiles += 1; exists = True
                    break
            if not exists:
                self.TocTypes.append(TocFileType(Entry.TypeID, 1))
    
    def AddEntry(self, NewEntry):
        if self.GetEntry(NewEntry.FileID, NewEntry.TypeID) != None:
            raise Exception("Entry with same ID already exists")
        self.TocEntries.append(NewEntry)
        self.UpdateTypes()