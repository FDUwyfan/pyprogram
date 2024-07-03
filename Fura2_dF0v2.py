# !/usr/bin/python3
# _*_ coding: utf-8 _*_


"""
For Ca2+ imaging data processing
Support .xlsx data
module openpyxl is required
Written by Fan at 1st Jul 2024
"""

import os
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Pool
import psutil

def process_data(file, basetime_start, basetime_end, data_dir):
    file_path = os.path.join(data_dir, file)
    df = pd.read_excel(file_path, index_col=0, header=None)
    new_df = df.loc['Time (sec)':].iloc[1:].astype('float32')
    cell_num = len(new_df.columns) // 5 - 1
    
    wholeData = pd.DataFrame(index=new_df.index, dtype='float32')
    
    for i in range(cell_num):
        F340 = new_df.iloc[:, 5*(i+1)]
        F380 = new_df.iloc[:, 5*(i+2)-3]
        ratio = F340 / F380
        
        ratio_rotate = (ratio - np.arange(len(ratio)) * np.tan((ratio.iloc[basetime_end] - ratio.iloc[basetime_start]) / (basetime_end - basetime_start)))
        baseline = ratio_rotate.iloc[basetime_start:basetime_end].mean()
        deltaFF0 = (ratio_rotate - baseline) / baseline
        
        cell_folder = os.path.join(data_dir, file.strip('.xlsx'), 'single_cell')
        if not os.path.exists(cell_folder):
            os.makedirs(cell_folder)
        plt.plot(deltaFF0)
        plt.savefig(os.path.join(cell_folder, f'cell{i+1}.png'), dpi=300, transparent=True)
        plt.close()
        
        wholeData[f'cell{i+1}'] = deltaFF0
    
    # 保存为.xlsx格式
    output_path = os.path.join(data_dir, f'whole_{file.strip(".xlsx")}.xlsx')
    wholeData.to_excel(output_path)
    
    plt.plot(wholeData)
    plt.savefig(os.path.join(data_dir, f'{file.strip(".xlsx")}.png'), dpi=300, transparent=True)
    plt.close()

def main():
    cpu_core = psutil.cpu_count(logical=False)
    data_dir = input('Input directory (请输入文件路径): ')
    basetime_start = int(input('请输入基线时间开始（单位：frame）: '))
    basetime_end = int(input('请输入基线时间结束（单位：frame）: '))
    print("Processing, please wait for seconds... (数据处理中，请稍等...)")

    start_time = time.time()
    
    file_list = [f for f in os.listdir(data_dir) if f.endswith('.xlsx') and not f.startswith('~')]
    file_num = len(file_list)
    print(f"Processing {file_num} files...")
    
    with Pool(cpu_core) as pool:
        pool.starmap(process_data, [(file, basetime_start, basetime_end, data_dir) for file in file_list])
    
    end_time = time.time()
    print(f"Total time: {end_time - start_time:.2f} seconds")
    print("Data export successful!\n\n")
    print("*" * 20)

    go_on = input('Continue or not? (Y/N): ')
    if go_on.lower() == 'y':
        main()
    else:
        print("Exiting...")
        exit()

if __name__ == "__main__":
    main()
