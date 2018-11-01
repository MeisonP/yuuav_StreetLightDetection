#coding:utf-8
import cv2 as cv
import numpy as np
import matplotlib as plt
import exifread as ef
import time
import timeit
import logging

def clock(func):  
    def clocked(*args):  
        t0 = timeit.default_timer()  
        result = func(*args)  
        elapsed = timeit.default_timer() - t0  
        name = func.__name__ 
        #arg_str = ', '.join(repr(arg) for arg in args) 
        #logging.info('%s....'%name)
        logging.info('%s(): [%0.8fs]' %(name, elapsed))  
        return result  
    return clocked 

 #https://gist.github.com/snakeye/fdc372dbf11370fe29eb 
def _convert_to_degress(value):
    """
    Helper function to convert the GPS coordinates stored in the EXIF to degress in float format
    :param value:
    :type value: exifread.utils.Ratio
    :rtype: float
    """
    d = float(value.values[0].num) / float(value.values[0].den)
    m = float(value.values[1].num) / float(value.values[1].den)
    s = float(value.values[2].num) / float(value.values[2].den)

    return d + (m / 60.0) + (s / 3600.0)
@clock
def get_GPS(filepath):
    '''
    returns gps data if present other wise returns empty dictionary
    '''
    with open(filepath, 'r') as f:
        tags = ef.process_file(f)
        latitude = tags.get('GPS GPSLatitude')
        latitude_ref = tags.get('GPS GPSLatitudeRef')
        longitude = tags.get('GPS GPSLongitude')
        longitude_ref = tags.get('GPS GPSLongitudeRef')
        if latitude:
            lat_value = _convert_to_degress(latitude)
            if latitude_ref.values != 'N':
                lat_value = -lat_value
        else:
            return {}
        if longitude:
            lon_value = _convert_to_degress(longitude)
            if longitude_ref.values != 'E':
                lon_value = -lon_value
        else:
            return {}
        return {'latitude': round(lat_value,6), 'longitude': round(lon_value,6)}
    return {}

 
def show_image(image,name):
    cv.imshow('%s'%name,image)
    cv.waitKey(0)

#高斯滤波
def gauss_filter(image,kernel_size,sigma):
    image_Guass=cv.GaussianBlur(image,(kernel_size, kernel_size), sigma)# (7, 7), 1)
    return image_Guass

#中值滤波
def median_filter(image,kernel_size):
    imaeg_Median = cv.medianBlur(image, kernel_size)
    return imaeg_Median


#图像灰度化, 三种方式：最大，平均，加权平均
def gray_op(image):
    image_gray=cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    return image_gray

def binary_op(image,threshold):
    return_value,image_Binary=cv.threshold(image,threshold,255,cv.THRESH_BINARY)
    return image_Binary

#腐蚀
def erosion_op(image,kernel_size):
    kernel = np.ones((kernel_size,kernel_size),np.uint8)
    erosion = cv.erode(image,kernel,1)
    return erosion


#膨胀
def dilation_op(image,kernel_size):
    #logging.info('dilation...')
    #kernel = np.ones((40,40),np.uint8)
    kernel=cv.getStructuringElement(cv.MORPH_RECT,(kernel_size,kernel_size))
    dilation= cv.dilate(image,kernel,1)
    return dilation

#开操作，去除外噪声
def open_op(image,kernel_size):
    #kernel = np.ones((5,5),np.uint8)
    kernel=cv.getStructuringElement(cv.MORPH_RECT,(kernel_size,kernel_size))  #must be int 方阵
    image_Open=cv.morphologyEx(image,cv.MORPH_OPEN,kernel)
    return image_Open

#闭操作，区域连接，去除空洞
def close_op(image,kernel_size):# should input binary image
    kernel=cv.getStructuringElement(cv.MORPH_RECT,(kernel_size,kernel_size))  #must be int 方阵
    #func explaination   https://blog.csdn.net/qq_31186123/article/details/78770141
    image_Close=cv.morphologyEx(image,cv.MORPH_CLOSE,kernel)
    return image_Close

#轮廓，边界
def edges_cal(image):#should input binary image
    #calculation
    #image=cv.imread(path,cv.CV_8UC1) 
    binary,contours, hierarchy = cv.findContours(image,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_NONE) 
    #in open CV3， findContours return 3 value; so my version is openCV3
    #draw boundary on the image
    #image=cv.drawContours(image,contours,-1,(0,0,255),3)#-1:draw all edge;  3:line width；（0，0，255):RGB color scaler
    #image_Edge=image
    return contours #outpur contours is a array, 

#center of contours
def contours_centers(contours):
    N= np.array(contours).shape[0]
    centers=[]
    for i in range (0,N):
        min_rect=cv.minAreaRect(contours[i]) #box  center is （min_[0][0],min_[0][1]）
        centers.append(min_rect[0])
    return centers



#不相连的轮廓求最小外界矩形,并添加到原图中
def draw_Min_Rects(image,contours):
    N= np.array(contours).shape[0]
    for i in range (0,N):
        min_=cv.minAreaRect(contours[i]) #box  center is （min_[0][0],min_[0][1]）
        box = cv.boxPoints(min_) 
        box = np.int0(box)
        cv.drawContours(image, [box], 0, (0,0,255), 5)
    image_with_MinRect=image
    Box_update=box
    return image_with_MinRect



#颜色分割
def color_segment(image_orig,image_HSV,H_Min,H_Max,S_Min,S_Max,V_Min,V_Max,return_type):#must be HSV 
    Lower = np.array([H_Min, S_Min,V_Min])
    Upper = np.array([H_Max, S_Max,V_Max])
    gray_= cv.inRange(image_HSV, Lower, Upper)#in range then set to 1, 白色； 0=背景黑色
    color_= cv.bitwise_and(image_orig,image_orig,mask=gray_)#图像与运算，类似于显示原图中的区域
    if return_type=='gray_':
        image_Segment=gray_
    else:
        image_Segment=color_

    return image_Segment


def Rect_filter(contours,down):
    N= np.array(contours).shape[0]
    contours_update=[]
    Box_update=[]
    for i in range (0,N):
        Rect=cv.minAreaRect(contours[i])
        Area_=Rect[1][0]*Rect[1][1]
        if Area_ >=down:# and (Rect[1][1]<300):
            #logging.info('W:%s ,L:%s'%(Rect[1][0],Rect[1][1]))
            contours_update.append(contours[i])
            Box_update.append(Rect)
    return contours_update,Box_update


