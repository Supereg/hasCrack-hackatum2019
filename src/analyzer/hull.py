import cv2
import numpy as np
import sys
import math
import operator
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

def compute_dist(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[0])**2)

def computeDepth(p1, p2, ourPoint):
    # print(p1)
    # d = np.linalg.norm(np.cross(p2-p1, p1-ourPoint))/np.linalg.norm(p2-p1)
    
    x1=p1[0]
    y1=p1[1]
    x2=p2[0]
    y2=p2[1]
    x3=ourPoint[0]
    y3=ourPoint[1]
    
    a = y2 - y1
    b = x1 - x2
    c = a * x1 + b * y1
    
    # print(str(a * x2 + b * y2 - c))
    
    d = abs(a * x3 + b * y3 - c) / math.sqrt(a**2 + b**2)
    
    # d = abs((x2-x1)*(y1-y0) - (x1-x0)*(y2-y1)) / np.sqrt(np.square(x2-x1) + np.square(y2-y1))
    return d

def next_(currPos, len_):
    if currPos == (len_ - 1):
        return 0
    else:
        return currPos + 1
    
def prev_(currPos, len_):
    if currPos == 0:
        return len_ - 1
    else:
        return currPos - 1

def isOn(fst, snd, p):
    # blue = (x, y)
    fstDist = math.sqrt((p[0] - fst[0])**2 + (p[1] - fst[1])**2)
    sndDist = math.sqrt((p[0] - snd[0])**2 + (p[1] - snd[1])**2)
    totalDist = math.sqrt((fst[0] - snd[0])**2 + (fst[1] - snd[1])**2)
    return (fstDist + sndDist) == totalDist

def PolyArea(x,y):
    return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))

def PolyAreaZipped(poly):
    x, y = [list(t) for t in zip(*poly)]
    return PolyArea(x, y)

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
    
    # Is it too gray?
    if avg <= 0.52:
        if True:   
            ret, src = cv2.threshold(src,127,255,cv2.THRESH_BINARY)
        else:
            a = np.double(src)
            b = a
            # when it's already too white -> make it black
            if avg > 0.75:
                b = b * (1 - avg)
            src = np.uint8(b)
    elif avg >= 0.62:
        ret, src = cv2.threshold(src,127,255,cv2.THRESH_BINARY)
        
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
    if len(sorted_areas) > 500:
        # Sum up all cracks areas
        total_ = 0
        for elem in sorted_areas:
            total_ += elem[1]
        
        # Filter tiny cracks
        keptAreas = []
        reduceBy = 0.95
        if False:
            sum_ = 0
            threshHold = total_ * reduceBy
            for elem in sorted_areas:
                if sum_ <= threshHold:
                    keptAreas.append(elem)
                sum_ += elem[1]
        else:
            # Begin from the end of the list, with the smallest ones
            away = {}
            partialSum = total_ * (1 - reduceBy)
            sum_ = 0
            copy = sorted_areas.copy()
            copy.reverse()
            for elem in copy:
                sum_ += elem[1]
                if sum_ <= partialSum:
                    away[elem[0]] = True
                else:
                    away[elem[0]] = False
                
            for elem in sorted_areas:
                if away[elem[0]] == False:
                    keptAreas.append(elem)
        sorted_areas = keptAreas
    
    # Take the biggest one and take into consideration the cracks which are inside it
    # TODO: white block entfernen
    isCrack = {}
    isBroken = {}
    totalyBroken = False
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
                    if curr[1] >= 0.8 * best[1]:
                        isBroken[curr[0]] = True
                        totalyBroken = True
                        # print(curr)
                    # TODO: insert wieder
                    # print(str(curr[0]) + "is broken")
                    # isBroken[curr[0]] = True
                    # print("Is already broken!")
    else:
        print("Error - area is empty")
        exit(0)
       
    # Find the lowest positioned point in HULL
    myHull_ = HULLS[best[0]]
    currMin = 1000000
    bestIndex = -1
    for i in range(0, len(myHull_)):
        if myHull_[i][1] < currMin:
            currMin = myHull_[i][1]
            bestIndex = i
        elif bestIndex == -1:
            currMin = myHull_[i][1]
            bestIndex = i
        elif myHull_[i][0] < myHull_[bestIndex][0]:
            currMin = myHull_[i][1]
            bestIndex = i
            
    # Find the point bestIndex in polys
    myRedPoly = polys[best[0]]
    startIndex = -1
    for i in range(0, len(myRedPoly)):
        if myRedPoly[i] == myHull_[bestIndex]:
            startIndex = i
            
    cracks = []
    if startIndex == -1:
        print("The start point is not in red poly")
        exit(0)
    else:
        # Through red polygon
        lastRedOnBlueLine = startIndex
        lastRedOnBluePoint = startIndex
        lastBlue = bestIndex
        
        currIndex = next_(startIndex, len(myRedPoly))
        while currIndex != startIndex:
            if myRedPoly[currIndex] in myHull_:
                if lastRedOnBlueLine != prev_(currIndex, len(myRedPoly)):
                    cracks.append((lastRedOnBlueLine, currIndex))
                    
                lastBlue = prev_(lastBlue, len(myHull_))
                lastRedOnBlueLine = currIndex
                lastRedOnBluePoint = currIndex
                
            elif isOn(myHull_[lastBlue], myHull_[prev_(lastBlue, len(myHull_))], myRedPoly[currIndex]):
                if lastRedOnBlueLine != prev_(currIndex, len(myRedPoly)):
                    # Crack is detected
                    cracks.append((lastRedOnBlueLine, currIndex))
                lastRedOnBlueLine = currIndex
            currIndex = next_(currIndex, len(myRedPoly))
        
    # Build the cracks
    # We've just intenfied the cracks
    cracksContours = []
    edgeCracksProps = []
    for crack in cracks:
        # crack is a tuple (fstIndex, lastIndex)
        fstIndex = crack[0]
        lastIndex = crack[1]
        
        # Formula for depth - max(dist(lastRedOnBlueLine, point in this polygon))
        fstPoint = myRedPoly[fstIndex]
        lastPoint = myRedPoly[lastIndex]
        width_ = math.sqrt((myRedPoly[fstIndex][0] - myRedPoly[lastIndex][0])**2 + (myRedPoly[fstIndex][1] - myRedPoly[lastIndex][1])**2)
        depth_ = 0
        
        # Normal order
        tmp = []
        if fstIndex < lastIndex:
            # The order is [i][j][0][0] bzw [i][j][0][1]
            for i in range(fstIndex, lastIndex + 1):
                point = myRedPoly[i]
                tmp.append(np.array([np.array([point[0], point[1]])]))
                currDist = computeDepth(fstPoint, lastPoint, point)
                if currDist > depth_:
                    depth_ = currDist
        else:
            for i in range(fstIndex, len(myRedPoly)):
                point = myRedPoly[i]
                tmp.append(np.array([np.array([point[0], point[1]])]))
                currDist = computeDepth(fstPoint, lastPoint, point)
                if currDist > depth_:
                    depth_ = currDist
            for i in range(0, lastIndex + 1):
                point = myRedPoly[i]
                tmp.append(np.array([np.array([point[0], point[1]])]))
                currDist = computeDepth(fstPoint, lastPoint, point)
                if currDist > depth_:
                    depth_ = currDist
        edgeCracksProps.append((width_, depth_))
        
        cracksContours.append(np.array(tmp))    
    cracksContours = np.array(cracksContours)

    # create an empty black image
    drawing = np.zeros((thresh.shape[0], thresh.shape[1], 3), np.uint8)
    drawing.fill(0)
    
    # Draw the image
    
    # RGB is reversed!!!
    
    # !!! Erased hierarchy!!!
    # draw contours and hull points
    for elem in sorted_areas:
        i = elem[0]
        color_contours = (0, 255, 0) # green - color for contours
        color = (255, 0, 0) # blue - color for convex hull
        # draw ith contour
        if i in isCrack:
            if isCrack[i] == True:
                cv2.drawContours(drawing, contours, i, color_contours, 3, 8)
            else:
                cv2.drawContours(drawing, hull, i, color, 1, 8)
                # print in white
                cv2.drawContours(drawing, contours, i, (255, 255, 255), 3, 8)
        if i in isBroken:
            if isBroken[i] == True:
                # white
                cv2.drawContours(drawing, contours, i, (255, 255, 255), 3, 8)
        # draw ith convex hull object
        # cv2.drawContours(drawing, hull, i, color, 1, 8)
    
    for i in range(0, len(cracks)):
        # orange
        color_crack = (0, 255, 255)
        cv2.drawContours(drawing, cracksContours, i, color_crack, 3, 8)
    cv2.imwrite(storeHerePath, drawing)

    # Apply the formulas
    
    if totalyBroken:
        print("rating: 100.0")
        print("loss-area: 0")
    else:
        # Edge cracks
        edgeScore = 0
        for i in range(0, len(edgeCracksProps)):
            # width = [0], depth = [1]
            width_ = edgeCracksProps[i][0]
            depth_ = edgeCracksProps[i][1]
            
            val = (depth_ / height) * 1 # -math.log2(width_ / width)
            edgeScore = max(val, edgeScore)
        # edgeScore /= len(edgeCracksProps)
        # TODO: check the values from threshold of white-black images
        
        hull_area = PolyAreaZipped(myHull_)
        redPoly_area = PolyAreaZipped(myRedPoly)
        
        divideBy = 0.25
        diff = (hull_area - redPoly_area) / hull_area
        areaScore = diff
        
        for elem in sorted_areas:
            i = elem[0]
            if i in isCrack:
                if isCrack[i] == True:
                    areaScore += elem[1] / hull_area
        totalScore = 100 * ((1.0 / divideBy) * areaScore + 2.5 * edgeScore) / 3.5
        
        # TODO: scale
        print("rating: " + str(totalScore))
        print("loss-area: " + str(100 * areaScore))
        
def main(photo):
    return
  
if __name__ == '__main__':
    # cv2.imwrite('cropped.png', myCrop(sys.argv[1]))
    extract(sys.argv[1], sys.argv[2])

