import zipfile
import tarfile
import rarfile
import os
import pathlib
import shutil
from typing import Union
import pydicom as pdc
import gc
import nibabel as nib

def data_execute(path: str, return_files: bool = False) -> list | str:
    TMP_PATH = r"C:\Users\user\Desktop\MIREA\Хак\scripts\tmp"
    
    def file_runner(folder: str) -> list:
        files = []
        extensions = []
        
        for file in folder.rglob('*'):
            if file.is_file():
                extension = file.suffix
                filename = file.name
                
                files.append(file)
                extensions.append(extension)
        
        return files, set(extensions)
    
    def format_explore(files: list, extentions: set) -> list | str:
        processed_formats = []
        output_type = "slices"
        
        if len(extentions) == 1 or len(extentions) == 0:
            extention = list(extentions)[0]
            
            match extention:
                case '.dcm' | '':
                    for file in files:
                        dc_file = pdc.dcmread(file)
                        processed_formats.append(dc_file.pixel_array)
                    
                case '.nii' | '.gz':
                    for file in files:
                            nii_volume = nib.load(file)
                            nii_volume = nii_volume.get_fdata()
                            
                            processed_formats.append(nii_volume)
                            
                    output_type = "volumes"
                case _:
                    return "Некорректный формат"
                
            return processed_formats, output_type
        else:
            return None, None

    def main(path: str) -> None:
        nonlocal TMP_PATH
        nonlocal file_runner
        nonlocal format_explore
        
        if os.path.exists(path):
            if os.path.isfile(path)== True and zipfile.is_zipfile(path) == False and tarfile.is_tarfile(path) == False:
            # извлечение информации о файлах
                return "is a file"
            else:
            
                if os.path.isdir(path):
                    folder = pathlib.Path(path)
                    files, extentions = file_runner(folder)
                    
                elif zipfile.is_zipfile(path):
                    archive_path = pathlib.Path(path)
                    archive_name = archive_path.stem
                    
                    with zipfile.ZipFile(path, 'r') as zip:
                        zip.extractall(TMP_PATH)
                    
                    folder = pathlib.Path(os.path.join(TMP_PATH, archive_name))
                    files, extentions = file_runner(folder)
                    
                    if folder.exists() and folder.is_dir():
                        shutil.rmtree(folder)
                    
                elif tarfile.is_tarfile(path):
                    archive_path = pathlib.Path(path)
                    archive_name = archive_path.stem
                    
                    with tarfile.open(path, 'r') as tar:
                        tar.extractall(TMP_PATH)
                    
                    folder = pathlib.Path(os.path.join(TMP_PATH, archive_name))
                    files, extentions = file_runner(folder)
                    
                    if folder.exists() and folder.is_dir():
                        shutil.rmtree(folder)
                    
                elif rarfile.is_rarfile(path):
                    archive_path = pathlib.Path(path)
                    archive_name = archive_path.stem
                    
                    with rarfile.RarFile(path) as rar:
                        rar.extractall(TMP_PATH)
                    
                    folder = pathlib.Path(os.path.join(TMP_PATH, archive_name))
                    files, extentions = file_runner(folder)
                    
                    if folder.exists() and folder.is_dir():
                        shutil.rmtree(folder)
                else:
                    return os.listdir(path)
                
                if return_files:
                    data, output_type = format_explore(files, extentions)
                    return data, files, output_type 
                else:
                    data, output_type = format_explore(files, extentions)
                    return data, files, output_type 
        else:
            return "Указанного пути не существует"

    return main(path)