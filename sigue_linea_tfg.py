#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 16:55:19 2017

@author: samuel
"""

#importamos las librerias con las que vayamos a trabajar
import numpy as np
import cv2
import time

def region_of_interest(img,vertices):
    mask = np.zeros_like(img)
    if len(img.shape) > 2:
        channel_count = img.shape[2]
        ignore_mask_color = (255,) * channel_count
    else:
        ignore_mask_color = 255
    
    cv2.fillPoly(mask, vertices, ignore_mask_color)
    masked_image = cv2.bitwise_and(img,mask)
    return masked_image

def draw_lines(img_without,img):
    linesP = cv2.HoughLines(img_without,1,np.pi/180,120)
    try:
        for rho,theta in linesP[0]:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*(rho)
            y0 = b*(rho)
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))
            if rho>0:
                if rho<900:
                    if theta<0.8 and theta>0.3:
                        if x1<150 and x2<1100:
                            cv2.line(img,(x1,y1),(x2,y2),(0,255,0),1)            
            else:
                if theta>0:
                    if rho<(-150):
                        if x1<200 and x2>600:
                            cv2.line(img,(x1,y1),(x2,y2),(0,255,0),1)            
    except TypeError:
        print 'Error, no se econtraron lineas'

    return img

def filters(img):
    img = cv2.erode (img,cv2.getStructuringElement(cv2.MORPH_RECT,(3,3)),iterations = 1)
    img = cv2.dilate (img,cv2.getStructuringElement(cv2.MORPH_RECT,(5,5)),iterations = 1)
    return img

cv2.namedWindow('webcam')
vc = cv2.VideoCapture('/Users/samuel/Documents/tfg/videos/carril_bici_8.MOV')

#Define la region de interest que deseamos en este caso un trapecio
bot_left = [80,700]
bot_right = [980,700]
appex_left = [360,60]
appex_right = [560,60]
v = [np.array([bot_left,bot_right,appex_right,appex_left], dtype=np.int32)]

# Define el rango de blanco en HSV
lower_blanco = np.array([0,0,230])
upper_blanco = np.array([179,85,255])

while (True):
    # Leemos de lo que estamos capturando
    ret, frame = vc.read()

    #donde mezclo las dos imagenes que quiero para poner mi region de interes
    img_trapecio = region_of_interest(frame,v)

    # Convierte BGR a HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Limpa la imagen de imperfecciones con los filtros erode y dilate
    hsv = filters (hsv)

    #Difumina la mascara para suavizar los contornos y aplicamos filtro canny
    hsv = cv2.GaussianBlur(hsv, (5, 5), 0)

    # Threshold de la imagen para obtener solo los colores blancos
    hsv = cv2.inRange(hsv, lower_blanco, upper_blanco)

    # Bitwise-AND mask y la imagen original
    res = cv2.bitwise_and(frame,frame, mask= hsv)

    #Saca el contorno con la funcion Canny
    prueba = cv2.Canny(res,50,150,apertureSize = 3)
    
    #Funcion para dibujar las lineas rectas en nuestra imagen 'frame'
    res = draw_lines(prueba,res)

    #Creamos una nueva imagen a partir de res para poder filtrar el color verde de los contornos    
    #---------------------------------------------------------
    hsv_2 = cv2.cvtColor(res,cv2.COLOR_BGR2HSV)

    verde_bajo = np.array([49,50,50], dtype=np.uint8)
    verde_alto = np.array([80,255,255], dtype=np.uint8)

    mask = cv2.inRange(hsv_2, verde_bajo, verde_alto)
    #---------------------------------------------------------

    #Recorremos el area de la imagen para ver donde estan las lineas verdes del contrno
    #y colocar una circulo verde para seguirlo
    #---------------------------------------------------------
    moments = cv2.moments(mask)
    area = moments['m00']
    if (area > 200000): #2000000
        x = int(moments['m10']/moments['m00'])
        y = int(moments['m01']/moments['m00'])
        cv2.rectangle(frame,(x,y),(x+2,y+2),(0,255,0),2)
        # Mostramos un circulo verde en la posicion en la que se encuentra el objeto
        cv2.circle (frame,(x,y),20,(0,255,0), 2)
    #---------------------------------------------------------

    #hacer mas pequeno el cuadrado de mostrar la webcam
    res = cv2.resize(res,(400, 400), interpolation = cv2.INTER_CUBIC)
    frame = cv2.resize(frame,(400, 400), interpolation = cv2.INTER_CUBIC)
    img_trapecio = cv2.resize(img_trapecio,(400, 400), interpolation = cv2.INTER_CUBIC)

    cv2.imshow('frame',frame)
    cv2.imshow('res',res)
    cv2.imshow('img_trapecio',img_trapecio)

    tecla = cv2.waitKey(33) & 0xFF
    if tecla!=255:
        if tecla==27:    # Esc key to stop
            cv2.DestroyAllWindows()
            break
        elif tecla==13:  # normally -1 returned,so don't print it
            time.sleep(10)
            print 'pausado'
        elif tecla==-1:  # normally -1 returned,so don't print it
            continue
        else:
            print ('Debe pulsar ESC para salir no: ',tecla) # else print its value

cv2.DestroyAllWindows()