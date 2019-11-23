import cv2
import numpy as np
import sys
import matplotlib.pyplot as plt
import math
import operator
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

def PolyArea(x,y):
    return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))

def PolyInPoly(fst, snd):
    # xs in [0], ys in [1] 
    polygon = Polygon(fst)
    count_ = 0
    for i in range(0, len(snd)):
        point = Point(snd[i][0], snd[i][1])
        # TODO: overlapping?
        if polygon.contains(point) == False:
            count_ += 1
    # Are there more than 2 points outside from the polygon -> then is the entire polygon inside
    if count_ > 2:
        return False
    return True

def myCrop(photo):
    path = photo
    src = cv2.imread(path, 1)
    
    avg = np.mean(np.array(src)) / 255.0
    print(avg)
   
    if True:
        ret, src = cv2.threshold(src,127,255,cv2.THRESH_BINARY)
    else:
        a = np.double(src)
        b = a
        # when it's already too white -> make it black
        if avg > 0.75:
            b = b * (1 - avg)
        src = np.uint8(b)
    
    height = src.shape[0]
    width = src.shape[1]
    
    newH = int(height * 0.92)
    new_img = src[0:newH, 0:width]
    return new_img

def extract(photo, storeHerePath):
    # path = 'data/' + photo + '.jpg'
    # src = cv2.imread(path, 1)
    
    src = myCrop(photo)
    height = src.shape[0]
    width = src.shape[1]

    # img_reverted = cv2.bitwise_not(img)
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY) # convert to grayscale
    blur = cv2.blur(gray, (3, 3)) # blur the image
    ret, thresh = cv2.threshold(blur, 50, 255, cv2.THRESH_BINARY)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # create hull array for convex hull points
    hull = []
    
    # calculate points for each contour
    print(len(contours))
    areas = {}
    polys = {}
    HULLS = {}
    for i in range(len(contours)):
        xs = []
        ys = []
        zipped = []
        for j in range(0, len(contours[i])):
            x = contours[i][j][0][0]
            y = contours[i][j][0][1]
            xs.append(x)
            ys.append(y)
            zipped.append((x, y))
        polys[i] = zipped
        area = PolyArea(xs, ys)
        areas[i] = area
        
        # creating convex hull object for each contour
        currHull = cv2.convexHull(contours[i], False)
        hull.append(currHull)
        
        # Create hull in normal form
        tmp = []
        for j in range(0, len(currHull)):
            x = currHull[j][0][0]
            y = currHull[j][0][1]
            tmp.append((x, y))
        HULLS[i] = tmp
    
    sorted_areas = sorted(areas.items(), key=operator.itemgetter(1), reverse=True)
    
    # Too many cracks?
    if len(sorted_areas) > 100:
        # Sum up all cracks areas
        total_ = 0
        for elem in sorted_areas:
            total_ += elem[1]
        
        print("before = " + " " + str(len(sorted_areas)))
        
        # Filter tiny cracks
        keptAreas = []
        sum_ = 0
        threshHold = total_ * 0.95
        print(total_)
        for elem in sorted_areas:
            print(str(elem) + " " + str(sum_))
            if sum_ <= threshHold:
                keptAreas.append(elem)
            sum_ += elem[1]
        sorted_areas = keptAreas
        print("at the end " + str(len(sorted_areas)))
    
    # Take the biggest one and take into consideration the cracks which are inside it
    isCrack = {}
    isBroken = {}
    if len(sorted_areas) != 0:
        # in [0] is the index of the corpus
        best = sorted_areas[0]
        isCrack[best[0]] = False
        for curr in sorted_areas:
            if curr[0] != best[0]:
                flag = PolyInPoly(HULLS[best[0]], polys[curr[0]])
                if flag:
                    isCrack[curr[0]] = True
                else:
                    # TODO: fix with convex hull - see weiss
                    isBroken[curr[0]] = True
                    print(str(curr[0]) + "is broken")
                    # isBroken[curr[0]] = True
                    # print("Is already broken!")
    else:
        print("Error - area is empty")
        
    # create an empty black image
    drawing = np.zeros((thresh.shape[0], thresh.shape[1], 3), np.uint8)
    
    # Erased hierarchy!!!
    # draw contours and hull points
    for elem in sorted_areas:
        i = elem[0]
        color_contours = (0, 255, 0) # green - color for contours
        color = (255, 0, 0) # blue - color for convex hull
        # draw ith contour
        if i in isCrack:
            if isCrack[i] == True:
                cv2.drawContours(drawing, contours, i, color_contours, 1, 8)
            else:
                cv2.drawContours(drawing, hull, i, color, 1, 8)
                # print in red
                cv2.drawContours(drawing, contours, i, (0, 0, 255), 1, 8)
        if i in isBroken:
            if isBroken[i] == True:
                cv2.drawContours(drawing, contours, i, (255, 255, 255), 1, 8)
        # draw ith convex hull object
        # cv2.drawContours(drawing, hull, i, color, 1, 8)
    cv2.imwrite(storeHerePath, drawing)

def main(photo):
    return
  
if __name__ == '__main__':
    # cv2.imwrite('cropped.png', myCrop(sys.argv[1]))
    extract(sys.argv[1], sys.argv[2])

