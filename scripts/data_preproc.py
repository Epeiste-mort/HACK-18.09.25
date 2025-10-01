import numpy as np

def data_preproc(data, storing_type: str, get_slice_num: bool = False) -> list:
    """Обработка данных в зависимости от типа хранения (срезы/томограммы), а так же выделение среднего среза для поступления в модель."""
    
    if storing_type == "slices": # обработка срезов одного пациента (для папок, где одна папка со срезами = один пациент), для того чтобы выстроить пайплайн
        # требуется итеративно применять данную функцию к каждой папке
        mean_slice = None
        slice_num = None
        mid_index = len(data) // 2
        
        imgs_np = np.array(data) 
        imgs_np = imgs_np.astype(np.float32)
        imgs_np /= np.max(np.abs(imgs_np))
        
        mean_slice = imgs_np[mid_index, :, :][..., np.newaxis] 
        mean_slice = mean_slice.squeeze()
        slice_num = mid_index
    elif storing_type == "volumes": # обработка томограмм (для файлов, где один файл = один пациент)
        # самый популярный способ обработки КТ - не требует итеративности
        mean_slice = []
        slice_num = []

        for volume in data:
            for z in range(0, volume.shape[2], volume.shape[2] // 2): 
                if z != volume.shape[2] and z != 0:
                    slice_2d = volume[:, :, z]
                    nii_data = np.array(slice_2d).astype(np.float32)
                    nii_data /= np.max(np.abs(nii_data))
                    
                    mean_slice.append(nii_data)
                    slice_num.append(z)
    else:
        mean_slice = None
    
    if get_slice_num:
        return mean_slice, slice_num
    else:
        return mean_slice