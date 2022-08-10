# !/usr/bin/python3
# _*_ coding: utf-8 _*_


# abf文件读取，提取其中trace信息，并plot为png格式图片
# 可保存.csv数据信息
import multiprocessing
import os
import psutil
from pyabf import ABF
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def get_data(file, sub):
    abf = ABF(file)
    data = pd.DataFrame(index=abf.sweepX, dtype='float32')
    for i in range(abf.sweepCount):
        if abf.channelCount == 1:
            abf.setSweep(i)
        else:
            abf.setSweep(i, sub)
        data.insert(0, "{} trace{}".format(file.strip(".abf"), (i + 1)), abf.sweepY)
    data = data.iloc[:, ::-1]
    return data


def concatenate(file, sub):
    data = get_data(file, sub)
    data_array = data.values
    sample_rate = int(1 / (data.index[1] - data.index[0]))
    concatenate_time_point = data.values.shape[0] * data.values.shape[1]
    new_time_x = np.linspace(0, concatenate_time_point / sample_rate, concatenate_time_point)
    data_series = data_array.T.reshape(concatenate_time_point, ).T
    concatenate_data = pd.Series(data=data_series, index=new_time_x, dtype='float32',
                                 name="concat trace {}".format(file.strip(".abf")))
    # print(concatenate_data)
    return concatenate_data


def plot_abf(file, sub, merge=False, export=False):
    abf = ABF(file)
    if merge is False:
        data = get_data(file, sub)
    else:
        data = concatenate(file, sub)
    plt.figure(figsize=(9, 6), dpi=300)
    plt.title(file.strip(".abf"))
    plt.xlabel('{}'.format(abf.sweepLabelX))
    plt.ylabel('{}'.format(abf.sweepLabelY))
    plt.plot(data, 'k', lw=0.5, label='{}'.format(file.strip('.abf')))
    plt.savefig("预览图{}.png".format(file.strip('.abf')), dpi=300)
    plt.close()
    # print('data is: ', data)
    if export is True:
        data.to_csv("{}.csv".format(file.strip(".abf")))


if __name__ == "__main__":

    now = time.strftime('\n%Y-%m-%d \n%H:%M:%S')

    print("*"*10 + "abf文件预览程序" + "*"*10 + "\n\n")
    print("当前时间：", now)
    print("\n请按提示输入")

    def main():
        cpu_core = psutil.cpu_count(logical=False)
        file_dir = ""
        sub = ""
        export = ""
        merge = ""
        
        while file_dir == "":
            file_dir = input('input dir (请输入数据所在目录）: ')
            if os.path.exists(file_dir) == False:
                print("Path is not exist, please retry!")
                main()
            else:
                os.chdir(file_dir)
        files = os.listdir()
        abf_file = []
        for file in files:
             if file.endswith(".abf"):
                abf_file.append(file)
        file_str = " ".join(abf_file)
        if abf_file == []:
            print("Sorry, no '.abf' file found, please check the directory!")
            main()
        else:
            print("\n目录包含{}个abf文件：".format(len(abf_file)), file_str)
        
        while sub == "":
            sub = input('\nsub or not(Y/N) (是否进行漏检）: ')
        while merge == "":
            merge = input('\nconcatenate or not(Y/N) (是否进行拼接）: ')
        while export == "":
            export = input('\nexport data or not(Y/N) (是否导出csv格式数据)：')
        sub = 1 if sub[0] in ['y', 'Y'] else 0
        export = True if export[0] in ['y', 'Y'] else False
        merge = True if merge[0] in ['y', 'Y'] else False

        begin_time = time.time()
        
        print("please waite for seconds...")
        # 仅支持物理核心并行，不支持逻辑核心。例如R7-3700X支持core=8
        pool = multiprocessing.Pool(cpu_core)
        for i in range(len(abf_file)):
            pool.apply_async(plot_abf, (abf_file[i], sub, merge, export))
        pool.close()
        pool.join()
        end_time = time.time()
        Dur = end_time - begin_time
        print("数据导出成功！") if export is True else print("已生成预览图")
        print("\n共耗时：{:.2f}秒\n\n".format(Dur))
        print("*" * 10 + "END" + "*" * 10)

        go_on = input('\ncontinue or not? (Y/N): ')
        if go_on[0] in ['Y', 'y']:
            main()
        else:
            exit()


    main()
