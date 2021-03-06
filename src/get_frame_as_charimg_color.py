#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :rich1.py
# @Time      :2021/01/28 11:17:54
# @Author    :Raink

import os
import cv2
import time
from threading import Thread
from queue import Queue
from rich.console import Console
from rich.text import Text


pix_map = ["一", "二", "十", "了", "工", "口", 
           "仁", "日", "只", "长", "王", "甘", 
           "舟", "目", "自", "革", "固", "国", 
           "制", "冒", "筋", "最", "酶", "藏", "霾", "龘"]


class Camera:
    def __init__(self, device_id, frame_queue):
        self.device_id = device_id  # 摄像头id
        self.cam = cv2.VideoCapture(self.device_id)  # 获取摄像头
        self.frame_queue = frame_queue  # 帧队列
        self.is_running = False  # 状态标签
        self.fps = 0.0  # 实时帧率
        self._t_last = time.time() * 1000
        self._data = {} 
 
    def capture_queue(self):
        # 捕获图像
        self._t_last = time.time() * 1000
        while self.is_running and self.cam.isOpened():
            ret, frame = self.cam.read()
            if not ret:
                break
            if self.frame_queue.qsize() < 1: 
                # 当队列中的图像都被消耗完后，再压如新的图像              
                t  = time.time() * 1000 
                t_span = t - self._t_last                
                self.fps = int(1000.0 / t_span)
                self._data["image"] = frame.copy()
                self._data["fps"] = self.fps
                self.frame_queue.put(self._data)
                self._t_last = t
 
    def run(self):
        self.is_running = True
        self.thread_capture = Thread(target=self.capture_queue)
        self.thread_capture.start()
 
    def stop(self):
        self.is_running = False
        self.cam.release()

def detec_show(frame): 
    console = Console()    
    while flag_cam_run:
        if frame.qsize() > 0:
            data = frame.get()        
            image = cv2.resize(data["image"], (64, 48))
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            text = Text("")
            for i in range(image.shape[0]):
                for j in range(image.shape[1]):
                    gray = 0.3*image[i][j][0] + 0.59*image[i][j][1] + 0.11*image[i][j][2]
                    index = int(gray /10.0 + 0.5)
                    if index < 0: index = 0
                    if index > 25: index = 25
                    style_ij="rgb({},{},{})".format(image[i][j][0], image[i][j][1], image[i][j][2])
                    text.append(pix_map[index], style=style_ij)
                text.append("\n")
            print("------------------------------------")
            console.print(text)     
            print("------------------------------------")
            frame_queue.task_done()
            time.sleep(0.5)  
            console.clear()
        if not flag_cam_run: 
            break

if __name__ == "__main__":
    # 启动 获取摄像头画面的 线程
    frame_queue = Queue()
    cam = Camera(0, frame_queue)
    cam.run()
    flag_cam_run = True
    # 启动处理（显示）摄像头画面的线程
    thread_show = Thread(target=detec_show, args=(frame_queue,))
    thread_show.start()
    time.sleep(60)
    cam.stop()
    flag_cam_run = False