# encoding=utf-8
import time
from typing import ValuesView
from weakref import WeakKeyDictionary
import PySimpleGUI as sg
import traceback
from comment.utils import check_validation, get_comments
import pandas as pd
# 取消warning
import warnings
warnings.filterwarnings('ignore')

sg.theme('BluePurple')   # Add a touch of color

# All the stuff inside your window.
layout = [	
            [sg.Text('如需批量跑请上传txt文件每行一个链接即可', size=(25,1))],
            [sg.Input(key='Input'), sg.FilesBrowse()],
            [sg.OK(), sg.Cancel()],
            # [sg.OK(), sg.Cancel()],
            [sg.Text('单条链接 输入/粘贴 需要抓取评论的链接 ~',size=(25,2)), sg.InputText()],
			[sg.Button('退出程序'),sg.Button('结果导出'), sg.Button('开始运行')],
            [sg.Output(size=(80,15))],          # an output area where all print output will go
		]

# Create the Window

window = sg.Window(title='评论获取工具V0.1 QA@wyh', layout=layout, font="bold 18")

# print('###########欢迎使用本评论获取小工具#################')
# print('当前支持的平台有微博(https://weibo.com/6724189443/JqR4UuzJC)和今日头条(https://www.toutiao.com/a7029929014202630687)')

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == 'OK':
        if values.get('Input'):
            try:
                valid_list = []
                with open(values['Input'], 'r') as f:
                    for line in f.readlines():
                        line = line.strip('\n').strip()
                        info = (check_validation(line))
                        print('读取 %s %s' %(line,info['message']))
                        if info.get('post_id'):
                            valid_list.append(info)
                    print('读取结束开始抓取.....')
                    comments = []
                    for each in valid_list:
                        c = get_comments(each)
                        comments += c
                    print('本次获取评论%d条..' %len(comments))
                    print(u'.....抓取结束，点击 结果导出 导出当前抓取数据.......')
            except Exception:
                traceback.print_exc()
        else:
            print('请上传文件!')
    if event == '开始运行':
        info = (check_validation(values[0]))
        print(info['message'])
        try:
            comments = get_comments(info)
            print('本次获取评论%d条..' % len(comments))
            print(u'.....抓取结束，点击 结果导出 导出当前抓取数据.......')
        except Exception:
            traceback.print_exc()
    if event == '结果导出':
        try:
            try:
                pf = pd.DataFrame(comments)
            except:
                print('暂无评论可供导出!')
            order = ['url', 'author_name', 'post_time', 'content', 'like_num']
            columns_map = {'author_name': '作者名', 'post_time': '评论时间', 'content': '内容', 'like_num': '点赞数' }
            pf.rename(columns=columns_map, inplace=True)
            t = str(int(time.time()))
            filename = 'data' + t + '.xlsx'
            pf.to_excel(filename)
            print(u'..... 结果导出成功！......见当前文件夹下 %s' % filename)
        except Exception:
            traceback.print_exc()
    if event == sg.WIN_CLOSED or event == '退出程序': # if user closes window or clicks cancel
        break
    

    
