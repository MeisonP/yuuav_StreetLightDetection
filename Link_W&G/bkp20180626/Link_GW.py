# coding: utf-8

#20180604, cut from 20180531_try_other_algorithm
# Better then threshold filter


import cv2 as cv
import numpy as np
import units
import time 


import cv2 as cv
import numpy as np
import logging
import time, timeit  
import exifread as ef
import os
import units


def ini():      
    TM=time.strftime("%Y-%m-%d %H-%M-%S",time.localtime())
    LOG_FORMAT = "%(asctime)s - %(levelname)s - [:%(lineno)d]- %(message)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    logging.info('**************************Mason(%s):model*******************'%(TM))
    return TM


#Link  func
def centers_filter(image_,image_orig,contours,centers,delta_d,delta_val,delta_area):
    N=np.array(contours).shape[0]
    for i in range (0,N-1):#update all centers 0-34:total 35， N=35
        for j in range(i+1,N):
            Rect_i=cv.minAreaRect(contours[i])
            Area_i=Rect_i[1][0]*Rect_i[1][1]
            
            Rect_j=cv.minAreaRect(contours[j])
            Area_j=Rect_j[1][0]*Rect_j[1][1]
            
            dx=abs(np.array(centers)[i][0]-np.array(centers)[j][0])
            dy=abs(np.array(centers)[i][1]-np.array(centers)[j][1])
            distance=np.sqrt(pow(dx,2)+pow(dy,2))
            #print distance
            if distance<=delta_d:
                if (Area_i<1000 and Area_j<1000) or abs(Area_i-Area_j)>=delta_area:
                    stpoint=(int(centers[i][0]),int(centers[i][1]))
                    endpoint=(int(centers[j][0]),int(centers[j][1]))
                    cv.arrowedLine(image_,stpoint,endpoint,(255,255,255),6)

    ret,image_binary=cv.threshold(image_,50,255,cv.THRESH_BINARY)
    #cv.imwrite('./test/'+'image_arrowed.jpg',image_)
    
    binary,contours_update, hierarchy = cv.findContours(image_binary,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_NONE)
    contours_update,Box_update=units.Rect_filter(contours_update,3000)
    centers_update=units.contours_centers(contours_update)
    
    return centers_update,contours_update
    

#Text
def put_text(image,contours,latitude,longitude):
    N= np.array(contours).shape[0]
    for i in range (0,N):
        min_=cv.minAreaRect(contours[i]) #box  center is （min_[0][0],min_[0][1]）
        box = cv.boxPoints(min_) 
        box = np.int0(box)
        G_latitude=latitude+(min_[0][0]-center[0])*(-ratio)
        G_longitude=longitude+(min_[0][1]-center[1])*(-ratio)

        cv.putText(image,'%d(La:%0.6f, Lo:%0.6f)'%(i,G_latitude,G_longitude),
                   (box[0][0],box[0][1]+60),cv.FONT_HERSHEY_PLAIN,4,(0,0,255),5)
    return image  
    

    

'''#process 
def process(image_orig,filepath):
    return image_with_text'''

#record
#write box info into txt file
def gps_record(filename,contours,latitude,longitude):#latitude,longitude is the image's gps info
    N= np.array(contours).shape[0]
    for i in range (0,N):
        min_=cv.minAreaRect(contours[i]) #box  center is （min_[0][0],min_[0][1]）
        G_latitude=latitude+(min_[0][0]-center[0])*(-ratio) #center  is a global parameter
        G_longitude=longitude+(min_[0][1]-center[1])*(-ratio)
        try:
            with open (box_gps,'a') as f:
                f.write('Filename:%s'%filename+'\t'+'Boxs:%s'%N+'\t'+'No.%d'%i+'\t'+'GPS:(%0.6f,%0.6f)\n'%(G_latitude,G_longitude))
        except IOError:
            logging.info('IO Error when write gps info into txt file!')
            pass
            

    
##################################  
       
    
#if __name__ == '__main__':
def main(arg):
    try:
        TM=ini()
        logging.info('arg value=%s'%arg)
        if arg=='1':
            TM0 = timeit.default_timer()
            global center,ratio,path_image,path_result,box_gps
            center=(1500,2000)
            ratio=0.36e-6 #pixel to GPS
            
            path_image='./image/'
            path_result='./results/'
            gps_record_path='./GPS_record/'
            box_gps=gps_record_path+TM+'box_gps.txt'
            
            
            filelist=os.listdir(path_image)#全部文件, name+jpg
            num=1
            for files in filelist:#files=name+jpg
                filename=os.path.splitext(files)[0];#文件名
                filepath=path_image+files#单个文件路径
                #box_gps=gps_record_path+TM+filename+'box_gps.txt'
                
                logging.info('%%%%%%%%%%%%%%%%%%%%%%%%processing image No.%s:%s'%(num,filename))

                try:
                    image_orig=cv.imread(filepath)
                    mage_gray=units.gray_op(image_orig)
                except Exception: 
                    logging.info('The filepath (image) is not found!')
                    raise
                #image_with_text=process(image_orig,filepath)
                
                
                ##################################
                ##################################

                
                #GPS
                gps=units.get_GPS(filepath) 
                latitude=gps['latitude']
                longitude=gps['longitude']
                logging.info('GPS info of image:%s'%gps)


                #HSV
                logging.info('HSV process...')
                image_orig=cv.imread(filepath)
                image_HSV=cv.cvtColor(image_orig, cv.COLOR_BGR2HSV)
                H, S, V = cv.split(image_HSV)

                #Segment by HSV
                logging.info('Segment...')
                image_seg_g=units.color_segment(image_orig,image_HSV,30,80,80,255,80,255,"color_")
                image_seg_w=units.color_segment(image_orig,image_HSV,0,180,0,30,200,255,"color_")
                #cv.imwrite('./test/results_seg_g.jpg',image_seg_g)
                #cv.imwrite('./test/results_seg_w.jpg',image_seg_w)


                #process after segment
                logging.info('Segment process...')
                image_dilation_g=units.dilation_op(image_seg_g,90)
                image_erosion_w=units.erosion_op(image_seg_w,7)
                image_dilation_w=units.dilation_op(image_erosion_w,90)        

                image_gray_w=cv.cvtColor(image_dilation_w, cv.COLOR_BGR2GRAY)
                image_gray_g=cv.cvtColor(image_dilation_g, cv.COLOR_BGR2GRAY)

                ret,image_binary_w=cv.threshold(image_gray_w,130,255,cv.THRESH_BINARY)
                ret,image_binary_g=cv.threshold(image_gray_g,130,255,cv.THRESH_BINARY)
                image_w=units.open_op(image_binary_w,9)
                image_g=units.open_op(image_binary_g,9)
                #combine white and green
                image_binary=image_w+image_g


                #Contours
                logging.info('Contours...')
                binary,contours, hierarchy=cv.findContours(image_binary,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_NONE) 
                centers=units.contours_centers(contours)
                center_update,contours_update=centers_filter(image_binary,image_orig,contours,centers,300,30,3000)
                
                #Output result
                logging.info('Draw minRect and put Text...')
                image_with_MinRect=units.draw_Min_Rects(image_orig,contours_update)
                image_with_text=put_text(image_with_MinRect,contours_update,latitude,longitude)
                
                
                #Write gps&box info into txt
                gps_record(filename,contours_update,latitude,longitude)
                ##################################
                ##################################
                
                try:
                    cv.imwrite(path_result+'%s'%TM+files,image_with_text)
                except Exception :
                    logging.info('output path is not found; mkdir...!')
                    os.mkdir(path)
                    cv.imwrite(path_result+'%s'%TM+files,image_with_text)
                
                num=num+1               
            #Time record  
            TM_end = timeit.default_timer()   
            logging.info('Total time consuption (60 pisce):%0.4f second'%(TM_end-TM0))

            logging.info('process completed...back to Flask App')
            global test
            test=1

            return test
            
        else:
            logging.info('arg value from Flask error, please try again!')
    except:
        logging.info('model process error...Back to Flask',exc_info=True)


