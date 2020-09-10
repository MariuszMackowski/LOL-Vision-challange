import cv2
import numpy as np
import sys
import os

def clean_hud(img):
    """
    Function dims non-transparent elements of the screenshot like minimap, replay control bar and champion pictures on both sides of pictures. 

    Parameters
    ----------
    img : numpy.ndarray
        Loaded image.

    Returns
    -------
    img : TYPE
        Image with black boxes on non-transparent elements.

    """
    cv2.rectangle(img,(1650,810),(1920,1080),(0,0,0),-1)  # minimap
    cv2.rectangle(img,(608,1007),(1320,1072),(0,0,0),-1)  # replay control bar
    
    for i in range(5):  # Champions pictures on both size
        
        cv2.rectangle(img,(2,152+i*103),(75,225+i*103),(0,0,0),-1)  # Left side champion picture
        cv2.circle(img,(72,163+i*103),10,(0,0,0),-1)  # Left side champion ultimate
        
        cv2.rectangle(img,(1842,152+i*103),(1915,225+i*103),(0,0,0),-1)  # Right side champion picture
        cv2.circle(img,(1845,163+i*103),10,(0,0,0),-1)  # Right side champion ultimate
        
    return img


def find_blue(img):
    """
    Function filters given image. Only pixels with values in ranges of either mask remain.
    There are four masks with values ranges that are in blue healts bars of champions.
    Using basic morphological operations, black spaces in health bars are filled and noise is cleared.
    After preprocesing image is given to function thats finds and count visable blue health bars.

    Parameters
    ----------
    img : numpy.ndarray
        Image after loading and clearing hud.

    Returns
    -------
    found_bars : int
        Number of found bars.

    """
    
    ## Four masks of blue health bar
    lower_bound = np.array([216,154,40])
    upper_bound = np.array([230,162,80])
    mask1 = cv2.inRange(img, lower_bound, upper_bound)
     
    lower_bound = np.array([216,182,85])
    upper_bound = np.array([230,200,100])
    mask2 = cv2.inRange(img, lower_bound, upper_bound)
    
    lower_bound = np.array([183,132,42])
    upper_bound = np.array([186,135,46])
    mask3 = cv2.inRange(img, lower_bound, upper_bound)
    
    lower_bound = np.array([124,110,75])
    upper_bound = np.array([133,116,88])
    mask4 = cv2.inRange(img, lower_bound, upper_bound)
    
    ## Filters image with bitwiseAND and sums outputs
    image = cv2.bitwise_and(img, img, mask = mask1) + cv2.bitwise_and(img, img, mask = mask2)+ cv2.bitwise_and(img, img, mask = mask3)+ cv2.bitwise_and(img, img, mask = mask4) 
    

    ## Morphological operations
    kernel = np.array(1,np.uint8)
    image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations = 3)  # Clearning noise with OPEN.
    
    kernel = np.array(([0,0,0],
                       [1,1,1],
                       [0,0,0]),np.uint8)
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations = 10)  # Closing gaps in healthbars with CLOSE and horizontal kernel. 
    
    kernel = np.array(1,np.uint8)
    image = cv2.morphologyEx(image, cv2.MORPH_DILATE, kernel, iterations = 2)  # Thickens healtbars to make them more visable.
    
    kernel = np.array(1,np.uint8)
    image = cv2.morphologyEx(image, cv2.MORPH_ERODE, kernel, iterations = 1)  # Erode all noise that remained.
    
    
    kernel = np.array(([0,0,0],
                       [1,1,1],
                       [0,0,0]),np.uint8)
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations = 10)  # Again close gaps if any left.
    
    return find_bars(image,True)
    
  
def find_red(img):
    """
    Function filters given image. Only pixels with values in ranges of either mask remain.
    There are two masks with values ranges that are in red healts bars of champions.
    Using basic morphological operations, black spaces in health bars are filled and noise is cleared.
    After preprocesing image is given to function thats finds and count visable red health bars.

    Parameters
    ----------
    img : numpy.ndarray
        Image after loading and clearing hud.

    Returns
    -------
    found_bars : int
        Number of found bars.

    """
    
    ## Two masks of red health bar
    lower_bound = np.array([95,100,180])
    upper_bound = np.array([115,120,200])
    mask1 = cv2.inRange(img, lower_bound, upper_bound)    
    lower_bound= np.array([38,49,149])
    upper_bound = np.array([60,67,167])
    mask2 = cv2.inRange(img, lower_bound, upper_bound)      
    
    ## Filters image with bitwiseAND and sums outputs
    image = cv2.bitwise_and(img, img, mask = mask1) + cv2.bitwise_and(img, img, mask = mask2)


    kernel = np.array(1,np.uint8)
    image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations = 3)  # Clearning noise with OPEN.  
    
    kernel = np.array(([0,0,0],
                       [1,1,1],
                       [0,0,0]),np.uint8)    
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations = 15)  # Closing gaps in healthbars with CLOSE and horizontal kernel.  
    
    kernel = np.array(1,np.uint8)
    image = cv2.morphologyEx(image, cv2.MORPH_DILATE, kernel, iterations = 3)  # Thickens healtbars to make them more visable.
    
    kernel = np.array(([0,1,0],
                       [0,1,0],
                       [0,1,0]),np.uint8)
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations = 1)  # Connects top and bottom of bar vertically.
    
    kernel = np.array(1,np.uint8)
    image = cv2.morphologyEx(image, cv2 .MORPH_ERODE, kernel, iterations = 2)  # Erode all noise that remained.
    
    kernel = np.array(([0,0,0],
                       [1,1,1],
                       [0,0,0]),np.uint8)
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations = 20)  # Again close gaps if any left.

    return find_bars(image,False)
    
  
def find_bars(img,not_check_rect):    
    """  
    Function gets image with done preprocessing,
    makes image gray and finds contours using cv2 built-in function,
    search in contours for ones with healthbar size (40 - 2000 px) and if not_check_rect = True - rectangualirty    value (>0.4). (Blue bars seems to work better without this condition)
    If bar is wider than 120 px, it is probably two bars conntected - counter + 2.
    
    Parameters
    ----------
    img : numpy.ndarray
        Image with done preprocessing.
    not_check_rect: Boolean
        If True, function will ignore rectangualirty condition.

    Returns
    -------
    found_bars : int
        Number of found bars
        
   """  
    
    gray_image = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    image, contours, hierarchy = cv2.findContours(gray_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cv2.imwrite('red2.jpg',gray_image)
    found_bars = 0
    for cont in contours:        
        x,y,w,h = cv2.boundingRect(cont)
        area = w*h
        rectangualirty = cv2.contourArea(cont)/(w*h) 
        
        if ((area > 40) and (area < 2000)) and (not_check_rect or rectangualirty>0.4):            
            found_bars = found_bars +1 + int(w>120)              
              
    return found_bars
    

if __name__ == '__main__':    
    """        
    Read image from given path if path is valid,
    clears hud if image is in full resolution (1920x1080),
    starts finding functions,
    prints acquired output
    """
    
    file = sys.argv[1]
    if os.path.isfile(file) and '.jpg' in file:        
        img=cv2.imread(file)            
        if np.size(img,0) == 1080 and np.size(img,1) == 1920:
            img = clean_hud(img)  
     
        print(find_red(img)+ find_blue(img))
    else:
        print('File does not exist or is not .jpg')
        
