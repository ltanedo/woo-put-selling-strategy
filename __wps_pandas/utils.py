import math
import sys

reversal = 3

#function will provide box sizes according to traditional method
#to check and update box size according to current value of stock
def updateBoxSize(price):
    box_ranges = [(.25,.0625),
              (1,.125),
              (5,.25),
              (20,.5),
              (100,1),
              (200,2),
              (500,4),
              (1000,5),
              (25000,50),
              (sys.maxsize,500)]
    for i in range (len(box_ranges)):
        if price < box_ranges[i][0]: #Zhen: Does it return multiple values?
            return box_ranges[i][1]
    return None


#using alpha_vantage because quandl gives only data till March 2018
#if current trend is x update x column appropriately or move to o column if needed
def updateX(item, list1, list2, box_size, reversal, current_trend, numberofXBoxes, numberofOBoxes):
    box_size = updateBoxSize(list1[-1])
   # print(math.floor(item["High"]))
    if ( math.floor(item["High"]) >= list1[-1]+box_size ):
        list1[-1] = math.floor(item["High"])
        numberofXBoxes += 1
    elif ( math.ceil(item["Low"]) <= list1[-1]-reversal*box_size):
        list2.append(math.ceil(item["Low"]))
        current_trend = 'o'
        numberofOBoxes += 1
    return current_trend

#if current trend is o update o column appropriately or move to x column if needed
def updateO(item, list1, list2, box_size, reversal, current_trend,  numberofXBoxes, numberofOBoxes):
    box_size = updateBoxSize(list2[-1])
    if ( math.ceil(item["Low"]) <= list2[-1]-box_size ):
        list2[-1] = math.ceil(item["Low"])
        numberofOBoxes += 1
    elif ( math.floor(item["High"]) >= list2[-1]+reversal*box_size):
        list1.append(math.floor(item["High"]))
        current_trend = 'x'
        numberofXBoxes += 1
    return current_trend

#create the point and figure from scratch
def pointAndFigureCreate(box_size,current_trend, list1, list2, stockhilowdata, numberofXBoxes, numberofOBoxes):
    #iterate over each date for the stock and create x or o columns
    for index,row in stockhilowdata.iloc[0:].iterrows():
        if current_trend == 'x':
            current_trend = updateX(row, list1, list2, box_size, reversal, current_trend, numberofXBoxes, numberofOBoxes)
        elif current_trend=='o':
            current_trend = updateO(row, list1, list2, box_size, reversal, current_trend, numberofXBoxes, numberofOBoxes)
    return current_trend

#check for a continous triple top pattern
def continous_triple_top(current_trend, list1):
    if(len(list1)<3):
        return -1
    ret_val = 0
    if current_trend == 'x':
        if((list1[-1]> list1[-2]) and (list1[-2] == list1[-3])):
            ret_val = 1
        else:
            ret_val = -1
    return ret_val

#check for a continous triple bottom pattern
def continous_triple_bottom(current_trend, list2):
    if(len(list2)<3):
        return -1
    ret_val = 0
    if current_trend == 'o':
        if((list2[-1] < list2[-2]) and (list2[-2] == list2[-3])):
            ret_val = 1
        else:
            ret_val = -1
    return ret_val

#check for a continous double top pattern
def continous_double_top(current_trend, list1):
    if(len(list1)<2):
        return -1
    ret_val = 0
    if current_trend=='x':
        if(list1[-1]> list1[-2]):
            ret_val = 1
        else:
            ret_val = -1
    return ret_val

#check for a continous double bottom pattern
def continous_double_bottom(current_trend, list2):
    if(len(list2)<2):
        return -1
    ret_val = 0
    if current_trend == 'o':
        if(list2[-1]< list2[-2]):
            ret_val = 1
        else:
            ret_val = -1
    return ret_val

def continous_quadruple_top(current_trend, list1):
    if(len(list1)<4):
        return -1
    ret_val = 0
    if current_trend == 'x' and len(list1)>3:
        if((list1[-1] > list1[-2]) and (list1[-2] == list1[-3] == list1[-4])):
            ret_val = 1
        else:
            ret_val = -1
    return ret_val

def continous_quadruple_bottom(current_trend, list2):
    if(len(list2)<4):
        return -1
    ret_val = 0
    if current_trend == 'o' and len(list2)>3:
        if((list2[-1] < list2[-2]) and (list2[-2] == list2[-3] == list2[-4])):
            ret_val = 1
        else:
            ret_val = -1
    return ret_val

def spread_triple_top(current_trend, list1):
    ret_val = -1
    if current_trend == 'x' and len(list1)>7:
        iterprev = 0
        resistance = 0
        notstt = True
        for iter in list1[-2:-7:1]:
            if iterprev == iter:
                resistance = iter
                notstt = False
            if resistance!=0 and iter > resistance:
                notstt = True
                break
            iterprev = iter
        if(notstt == False):
            ret_val = 1
        else:
            ret_val = -1
    return ret_val

def spread_triple_bottom(current_trend, list2):
    ret_val = -1
    if current_trend == 'o' and len(list2)>7:
        iterprev = 0
        support = 0
        notstb = True
        for iter in list2[-2:-7:1]:
            if iterprev == iter:
                support = iter
                notstb = False
            if support!=0 and iter<resistance:
                notstb = True
                break
            iterprev = iter
        if(notstb == False):
            ret_val = 1
        else:
            ret_val = -1
    return ret_val

def get_support_levels(list2):
    if(len(list2)>=2):
        return list2[-1],list2[-2]
    elif (len(list2)==1):
        return list2[-1],0
    else:
        return 0,0

def get_resistance_levels(list1):
    if(len(list1)>=2):
        return list1[-1],list1[-2]
    elif (len(list1)==1):
        return list1[-1],0
    else:
        return 0,0
