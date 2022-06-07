import traceback
import winreg
import pathlib
from zipfile import ZipFile

#gets the folder of the current driver in the driver store.
try:
    key = winreg.OpenKeyEx(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\\AMD\\EEU')
    value = winreg.QueryValueEx(key, 'LastKmdInstallPath')
    print(f'Found driver folder: {value[0]}')
except Exception:
    print(traceback.format_exc())


#starts to make the zip file.
with ZipFile('drivers.zip', mode='w') as zipobj:
    #this lists will be used to get the files in both System32 and SysWOW64.
    fileliste32 = []
    #i am not quite sure if the files in WOW64 are needed but since there are listed in the driver manager a decided to copy them too.
    fileliste64 = []
    #use pathlib to open the directory we got from the registry key.
    DSEFpath = pathlib.Path(value[0])
    #the folder that is inside of the registry key is a subfolder of the folder we want to copy so we need to acess its parent folder.
    DSFpathparent = pathlib.Path(value[0]).parent
    try:
        #copys any file inside of the System32 that has those prefix, this is not as efficient as i wanted but i could not find where device manager store its drivers info. 
        for files in ('amd*.*','ati*.*','amf*.*','kapp*.*','mantle*.*','Rapidfire*.*','samu*.*','vulkan*.*'):
            fileliste32.extend(pathlib.Path('C:\\Windows\\System32\\').glob(files))
        #some files whe need are not in that list so i added them manually to the list.
        fileliste32.extend(["C:/Windows/System32/clinfo.exe","C:/Windows/System32/detoured.dll","C:/Windows/System32/dgtrayicon.exe","C:/Windows/System32/EEURestart.exe","C:/Windows/System32/GameManager64.dll","C:/Windows/System32/OpenCL.dll","C:/Windows/System32/opengl32.dll"])
        #same as the System32 but for SysWOW64.
        for files in ('amd*.*','ati*.*','amf*.*','mantle*.*','Rapidfire*.*','vulkan*.*'):
            fileliste64.extend(pathlib.Path('C:\\Windows\\SysWOW64\\').glob(files))
        fileliste64.extend(["C:/Windows/SysWOW64/detoured.dll","C:/Windows/SysWOW64/GameManager32.dll","C:/Windows/SysWOW64/OpenCL.dll","C:/Windows/SysWOW64/opengl32.dll"])
        #Writes the files from system32.
        print("Writing zip file...")
        for file in fileliste32:
            zipobj.write(file)
        #Writes the files from sysWOW64.
        for file in fileliste64:
            zipobj.write(file)
        #Writes the files from the AMD folder inside of the System32 folder.
        for file_path in pathlib.Path("C:\\Windows\\System32\\AMD").rglob("*"):
            zipobj.write(file_path)
        #Writes the driver folder inside of the DriverStore as HostDriverStore so we dont need to rename-it when copying to the Virtual machine.
        for file in DSFpathparent.iterdir():
            zipobj.write(file, arcname="C:\\Windows\\System32\\HostDriverStore\\FileRepository\\"+ pathlib.Path(value[0]).parts[5] +"\\" + file.name)
        #Write the subfolder of the driver.
        for file in DSEFpath.iterdir():
            zipobj.write(file, arcname="C:\\Windows\\System32\\HostDriverStore\\FileRepository\\"+  pathlib.Path(value[0]).parts[5] +"\\"+  pathlib.Path(value[0]).parts[6] +"\\" + file.name)

    
    #close the zip.
        zipobj.close()
    except Exception:
        print(traceback.format_exc())

