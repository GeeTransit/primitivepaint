##########################################################################
##Program Author: George Zhang                                          ##
##Revision Date: Nov 12, 2018                                           ##
##Program Name: Graphical Canvas                                        ##
##Description: This program draws on the canvas of a tkinter window.    ##
##########################################################################

#importation of tkinter, its colour and file chooser, and its alerts
import tkinter as tk
import tkinter.colorchooser as tkcolour
import tkinter.filedialog as tkfile
import tkinter.messagebox as tkmessage

#importation of maths
import math as m

#importation of system
import sys

#current version
VERSION = 1.2

#declaration of variables
actions = list()    #used for undo
adjustX = int()
adjustY = int()
canvasHeight = int()
canvasWidth = int()
current = str()     #colour
debug = bool()      #enable debug
file = str()        #file object
fileName = str()    #file path
firstX = int()      #click and drag drawing
firstY = int()
mouse = bool()
outlinePen = list() #pen outline id
pastPoints = list() #polygon drawing
previousX = int()   #pen drawing
previousY = int()
redo = list()       #used for redo
saved = bool()      #used for saving
stroke = int()      #amount of strokes
strokeType = str()  #stroke type
window = str()      #main window identifier

#default values
actions = [[]]
canvasHeight = 300
canvasWidth = 100
current = '#000000'
fileName = 'untitled.txt'
redo = [[]]
saved = True
strokeType = 'pen'

#instantiate the main window
window = tk.Tk()
window.title('Primitive Paint - untitled.txt')

#declaration of window variables
sizePen = tk.IntVar()

#default window values
sizePen.set(1.0)

#makes a shape at specified location and returns the value
def canvasShape(*args, **kwargs):
    #declaration of internal variables
    x1 = int()
    y1 = int()
    x2 = int()
    y2 = int()
    kargs = dict()

    #plot arguments to internal variables
    if (len(args) < 2):
        raise TypeError('canvasShape expected at least 2 arguments')
    elif (len(args)%2 != 0):
        raise TypeError('canvasShape expected pairs of arguments')
    else:
        try:
            x1 = args[0]
            y1 = args[1]
            x2 = args[2]
            y2 = args[3]
        except:
            pass
    kargs = dict(kwargs)

    #check for unfilled keyworded arguments
    if 'shape' not in kargs:
        raise TypeError('canvasShape expected a keyword shape')
    if 'fill' not in kargs and 'outline' not in kargs:
        raise TypeError('canvasShape expected a keyword fill or outline')
    if 'size' not in kargs:
        kargs['size'] = 1
    if (('outline' in kargs) and ('fill' not in kargs)):
        kargs['fill'] = ''
    if 'outline' not in kargs:
        kargs['outline'] = kargs['fill']

    #create and return item id
    if (kargs['shape'] == 'dot'):
        return canvas.create_line(
            x1, y1, x1 - 1, y1 - 1,
            fill = kargs['fill']
        )
    if (kargs['shape'] == 'line'):
        return canvas.create_line(
            x1, y1, x2, y2,
            fill = kargs['fill'],
            width = kargs['size']
        )
    elif (kargs['shape'] in ('circle', 'square')):
        #get corners for specified size
        top = m.floor(kargs['size']/2)
        bottom = m.ceil(kargs['size']/2) - 1
        if ((kargs['shape'] == 'circle') and (kargs['size'] > 2)):
            return canvas.create_oval(
                x1 - top, y1 - top, x1 + bottom, y1 + bottom,
                fill = kargs['fill'],
                outline = kargs['outline']
            )
        elif ((kargs['shape'] == 'square') and (kargs['size'] > 2)):
            return canvas.create_rectangle(
                x1 - top, y1 - top, x1 + bottom, y1 + bottom,
                fill = kargs['fill'],
                outline = kargs['outline']
            )
        elif (kargs['size'] == 2):
            return canvas.create_rectangle(
                x1, y1, x1 - 1, y1 - 1,
                outline = kargs['outline']
            )
        else:
            return canvas.create_line(
                x1, y1, x1 - 1, y1 - 1,
                fill = kargs['outline']
            )
    elif (kargs['shape'] == 'oval'):
        return canvas.create_oval(
            x1, y1, x2, y2,
            fill = kargs['fill'],
            outline = kargs['outline'],
            width = kargs['size']
        )
    elif (kargs['shape'] == 'rectangle'):
        if ((x1 != x2) and (y1 != y2)):
            return canvas.create_rectangle(
                x1, y1, x2, y2,
                fill = kargs['fill'],
                outline = kargs['outline'],
                width = kargs['size']
            )
        elif (kargs['size'] == 1):
            return canvas.create_line(
                x1, y1, x2, y2,
                fill = kargs['outline']
            )
        else:
            #get corners for specified size
            top = m.floor(kargs['size']/2)
            bottom = m.ceil(kargs['size']/2) - 1
            #swap ends if needed
            if ((x1 - x2 > 0) or (y1 - y2 > 0)):
                x1, y1, x2, y2 = x2, y2, x1, y1
            return canvas.create_rectangle(
                x1 - top, y1 - top, x2 + bottom, y2 + bottom,
                fill = kargs['outline'],
                outline = kargs['outline'],
                width = 1
            )
    elif (kargs['shape'] == 'polygon'):
        if ((args[0::2].count(args[0]) < len(args[0::2]))
            and (args[0::2].count(args[0]) < len(args[0::2])
        )):
            return canvas.create_polygon(
                *args,
                fill = kargs['fill'],
                outline = kargs['outline'],
                width = kargs['size']
            )
        else:
            #get corners for specified size
            top = m.floor(kargs['size']/2)
            bottom = m.ceil(kargs['size']/2) - 1
            return canvas.create_oval(
                x1 - top, y1 - top, x1 + bottom, y1 + bottom,
                fill = kargs['outline'],
                outline = kargs['outline']
            )
    else:
        pass
#end canvasShape(*args, **kwargs)

#creates a line at the mouse move event
def paint(event=None):
    #reference variables outside function
    global actions
    global current
    global previousX
    global previousY
    global sizePen
    global stroke
    global strokeType

    #declaration of internal variables
    currentX = int()
    currentY = int()

    #if event isnt there, use previous x and y positions
    if event is None:
        currentX = previousX
        currentY = previousY
    else:
        currentX = event.x
        currentY = event.y

    #draws line from previous event location if strokeType is pen
    if (strokeType == 'pen'):
        actions[stroke].append(canvasShape(
            previousX, previousY,
            currentX, currentY,
            shape = 'line',
            fill = current,
            size = sizePen.get()
        ))

        #finish end dot if larger than one
        if (sizePen.get() > 1.0):
            actions[stroke].append(canvasShape(
                currentX, currentY,
                shape = 'circle',
                fill = current,
                size = sizePen.get()
            ))
            #size five fixes
            if (sizePen.get() == 5):
                actions[stroke].append(canvasShape(
                    currentX + 1, currentY,
                    shape = 'circle',
                    fill = current,
                    size = 4
                ))

    #call the outline function
    outline(event)

    #update line start for next line
    previousX = currentX
    previousY = currentY
#end paint(event)

#resets the line start
def reset(event):
    #reference variables outside function
    global actions
    global current
    global fileName
    global firstX
    global firstY
    global mouse
    global pastPoints
    global previousX
    global previousY
    global redo
    global saved
    global sizePen
    global stroke
    global strokeType

    #set the mouse down detector
    mouse = True

    #set the mouse down location
    firstX = event.x
    firstY = event.y
    
    #adds a point to the polygon
    if (strokeType in ('polygon', 'filled polygon')):
        pastPoints.extend((event.x, event.y))

    #update saved
    saved = False

    #update title
    window.title(('*Primitive Paint - ' + fileName))

    #update current stroke if not polygon
    if (strokeType not in ('polygon', 'filled polygon')):
        stroke += 1; actions.append([])

    #empty redo list
    if (len(redo) > 1):
        redo = [[]]

    #draws starting dot of selected size
    if (strokeType in ('pen')):
        #circle shape
        actions[stroke].append(canvasShape(
            event.x, event.y,
            shape = ('circle'
            if (sizePen.get() != 2)
            else 'square'),
            fill = current,
            size = sizePen.get()
        ))
        #size five fixes
        if (sizePen.get() == 5):
            actions[stroke].append(canvasShape(
                event.x + 1, event.y,
                shape = 'circle',
                fill = current,
                size = 4
            ))

    #call the outline function
    outline(event)

    #update line start for next line
    previousX = event.x
    previousY = event.y
#end reset(event)

#button release detector
def end(event):
    #reference variables outside function
    global actions
    global current
    global mouse
    global previousX
    global previousY
    global sizePen
    global stroke
    global strokeType

    #declaration of internal variables
    currentX = int()
    currentY = int()

    #reset the mouse down detector
    mouse = False

    #finish stroke
    if (strokeType == 'line'):
        actions[stroke].append(canvasShape(
            firstX, firstY,
            shape = 'circle'
            if (sizePen.get() != 2)
            else 'square',
            fill = current,
            size = sizePen.get()
        ))
        #finish line
        actions[stroke].append(canvasShape(
            firstX, firstY,
            event.x, event.y,
            shape = 'line',
            fill = current,
            size = sizePen.get()
        ))
        #finish end dot
        actions[stroke].append(canvasShape(
            event.x, event.y,
            shape = 'circle'
            if (sizePen.get() != 2)
            else 'square',
            fill = current,
            size = sizePen.get()
        ))
        #size five fixes
        if (sizePen.get() == 5):
            actions[stroke].append(canvasShape(
                event.x + 1, event.y,
                shape = 'circle',
                fill = current,
                size = 4
            ))
    elif (strokeType in ('oval', 'filled oval')):
        actions[stroke].append(canvasShape(
            firstX, firstY,
            event.x, event.y,
            shape = 'oval',
            fill = current
            if (strokeType == 'filled oval')
            else '',
            outline = current,
            size = sizePen.get()
        ))
    elif (strokeType in ('rectangle', 'filled rectangle')):
        actions[stroke].append(canvasShape(
            firstX, firstY,
            event.x, event.y,
            shape = 'rectangle'
            if ((event.x - firstX != 0)
                and (event.y - firstY != 0))
            else 'square',
            fill = current
            if ((strokeType == 'filled rectangle')
                or ((firstX == event.x)
                and (firstY == event.y)))
            else '',
            outline = current,
            size = sizePen.get()
        ))

    #call the outline function
    outline(event)

    #update line start for next line
    previousX = event.x
    previousY = event.y
#end end(event)

#right click detector function
def finish(event):
    #reference variables outside function
    global actions
    global current
    global pastPoints
    global sizePen
    global stroke
    global strokeType

    #increase stroke amount
    stroke += 1; actions.append([])

    #check if stroke type is polygon or filled polygon
    if (strokeType not in ('polygon', 'filled polygon')): return

    #check if there's actually points in the polygon
    if ((len(pastPoints) > 1) and (len(pastPoints)%2 == 0)):
        if (len(pastPoints) == 2):
            #make a point
            actions[stroke].append(canvasShape(
                *pastPoints,
                shape = 'circle',
                fill = current,
                size = sizePen.get()
            ))
        elif (len(pastPoints) == 4):
            #make a line
            actions[stroke].append(canvasShape(
                *pastPoints,
                shape = 'line',
                fill = current,
                size = sizePen.get()
            ))
        else:
            #make a polygon
            actions[stroke].append(canvasShape(
                *pastPoints,
                shape = 'polygon',
                fill = current
                if (strokeType == 'filled polygon')
                else '',
                outline = current,
                size = sizePen.get()
            ))
        #empty the points
        del pastPoints[:]

    #call the outline function
    outline(event)
#end finish(event)

#mouse motion detector function
def outline(event=None):
    #reference variables outside function
    global current
    global firstX
    global firstY
    global mouse
    global outlinePen
    global pastPoints
    global previousX
    global previousY

    #declaration of internal variables
    currentX = int()
    currentY = int()
    colourRed = int()
    colourGreen = int()
    colourBlue = int()
    colour = str()

    #check if mouse isnt down
    if not mouse:
        #set the colour to be used to the current colour
        colour = current
    else:
        #convert colour to integer
        colourRed = int(current[1:3], 16)
        colourGreen = int(current[3:5], 16)
        colourBlue = int(current[5:7], 16)

        #get opposite
        colourRed = hex(abs(255 - colourRed))[2:].rjust(2, '0')
        colourGreen = hex(abs(255 - colourGreen))[2:].rjust(2, '0')
        colourBlue = hex(abs(255 - colourBlue))[2:].rjust(2, '0')

        #convert back to normal format
        colour = (f'#{colourRed}{colourGreen}{colourBlue}')

    #if event isnt there, use previous x and y positions
    if event is None:
        currentX = previousX
        currentY = previousY
    else:
        currentX = event.x
        currentY = event.y

    #delete all items in outline
    if outlinePen:
        #delete the outline
        for item in outlinePen: canvas.delete(item)

        #reset outline ids
        del outlinePen[:]

    #draw result
    if ((strokeType == 'line') and mouse):
        #if type is line
        outlinePen.append(canvasShape(
            firstX, firstY,
            shape = 'circle',
            fill = current,
            size = sizePen.get()
        ))
        outlinePen.append(canvasShape(
            firstX, firstY,
            currentX, currentY,
            shape = 'line',
            fill = current,
            size = sizePen.get()
        ))
        outlinePen.append(canvasShape(
            currentX, currentY,
            shape = 'circle',
            fill = current,
            size = sizePen.get()
        ))
    elif ((strokeType in ('oval', 'filled oval')) and mouse):
        #if type is oval or filled oval
        outlinePen.append(canvasShape(
            firstX, firstY,
            currentX, currentY,
            shape = 'oval',
            fill = current
            if (strokeType == 'filled oval')
            else '',
            outline = current,
            size = sizePen.get()
        ))
    elif ((strokeType in ('rectangle', 'filled rectangle')) and mouse):
        #if type is rectangle or filled rectangle
        outlinePen.append(canvasShape(
            firstX, firstY,
            currentX, currentY,
            shape = 'rectangle',
            fill = current
            if (strokeType == 'filled rectangle')
            else '',
            outline = current,
            size = sizePen.get()
        ))
    elif ((strokeType in ('polygon', 'filled polygon')) and pastPoints):
        #if type is polygon or filled polygon
        outlinePen.append(canvasShape(
            *pastPoints,
            currentX, currentY,
            shape = 'polygon',
            fill = current
            if (strokeType == 'filled polygon')
            else '',
            outline = current,
            size = sizePen.get()
        ))

    #draws outline of selected size
    if (strokeType in ('rectangle', 'filled rectangle')):
        outlinePen.append(canvasShape(
            currentX, currentY,
            shape = 'square',
            outline = colour,
            size = sizePen.get()
        ))
    elif (sizePen.get() == 5):
        def lineMake(x1, y1, x2, y2):
            nonlocal currentX
            nonlocal currentY
            outlinePen.append(canvasShape(
                currentX + x1, currentY + y1,
                currentX + x2, currentY + y2,
                shape = 'line', fill = colour
            ))
        lineMake(-2, 1, -2, -2)
        lineMake(-1, 2, 2, 2)
        lineMake(2, 1, 2, -2)
        lineMake(1, -2, -2, -2)
    else:
        outlinePen.append(canvasShape(
            currentX, currentY,
            shape = 'circle',
            outline = colour,
            size = sizePen.get()
        ))

    #update line start for next line
    previousX = currentX
    previousY = currentY
    
    #update screen
    canvas.update()
#end outline(event)

#changes colour with a popup
def colourChange(*args):
    #reference variables outside function
    global current

    #declaration of internal variables
    colourAsk = tuple()

    #ask user for new colour and replace previous colour
    colourAsk = tkcolour.askcolor(initialcolor = current)
    if (colourAsk[1] is not None): current = colourAsk[1]

    #update display
    display.config(bg = current)
#end change()

#resize with the scrollwheel
def resize(event):
    #reference variables outside function
    global mouse
    global sizePen

    #scroll up to increase, down to decrease
    if ((event.delta == -120) and (sizeChoose.get() < 100)):
        sizeChoose.set(sizePen.get() + 1)
        if mouse: paint()
    elif ((event.delta == 120) and (sizeChoose.get() > 1)):
        sizeChoose.set(sizePen.get() - 1)

    #call the outline function
    outline()

    #set size to the scale's setting just in case
    sizePen.set(sizeChoose.get())
#end resize(event)

#change drawing type
def strokeChange(position):
    #reference variables outside function
    global pastPoints
    global strokeType
    
    #declaration of internal variables
    lastTypePolygon = bool()

    #check if stroke type is a polygon
    if (lastTypePolygon in ('polygon', 'filled polygon')):
        lastTypePolygon = True

    #function to reset background
    def bgReset():
        #declaration of internal variables
        bgOff = 'SystemButtonFace'
        bgOn = '#CCCCCC'
        shapeCounter = int()

        #calculate result
        def valueMake():
            #reference non-global variables outside function
            nonlocal shapeCounter

            #increase counter
            shapeCounter += 1

            #return if it matches the counter's previous value
            if (position == shapeCounter - 1): return bgOn
            else: return bgOff
        #end valueMake()

        #reset backgrounds except for the selected one
        shapePencil.config(bg = valueMake())
        shapeLine.config(bg = valueMake())
        shapeOval.config(bg = valueMake())
        shapeFilledOval.config(bg = valueMake())
        shapeRectangle.config(bg = valueMake())
        shapeFilledRectangle.config(bg = valueMake())
        shapePolygon.config(bg = valueMake())
        shapeFilledPolygon.config(bg = valueMake())

    #specific type for each button
    for positionCheck, strokeCheck in enumerate((
        'pen', 'line',
        'oval', 'filled oval',
        'rectangle', 'filled rectangle',
        'polygon', 'filled polygon'
    )):
        #check if a button was pressed and is different than the current
        if (position == positionCheck) and (strokeType != strokeCheck):
            strokeType = strokeCheck; bgReset()
    #end for

    #delete the last points if the last type was a polygon and now it isnt
    if (lastTypePolygon and strokeType not in ('polygon', 'filled polygon')):
        del pastPoints[:]

    #call outline
    outline()
#end strokeChange(event)

def undoLast(event):
    #reference variables outside function
    global actions
    global fileName
    global redo
    global saved
    global stroke

    #save and delete last stroke one by one for updating
    if (len(actions) > 1):
        #update saved
        saved = False

        #update title
        window.title(('*Primitive Paint - ' + fileName))

        #indicate start of stroke
        redo.append([True])

        #loop through all items
        for item in actions[-1]:
            #add last substroke
            redo[-1].append(canvas.type(item))
            redo[-1].append(canvas.coords(item))
            redo[-1].append(
                canvas.itemcget(item, 'outline') + '#'
                if ((canvas.type(item)
                    in ('oval', 'rectangle', 'polygon'))
                    and ((canvas.itemcget(item, 'fill')
                    != canvas.itemcget(item, 'outline'))))
                else (canvas.itemcget(item, 'fill'))
            )
            redo[-1].append(canvas.itemcget(item, 'width'))
            canvas.delete(item)
        #end for

        #canvas.update()
        del actions[-1]
        stroke -= 1
#end undoLast(event)

def undoSingle(*args):
    #reference variables outside function
    global actions
    global fileName
    global redo
    global saved
    global stroke

    #save and delete last substroke, deleting last stroke if needed
    if (len(actions) > 1):
        #update saved
        saved = False

        #update title
        window.title(('*Primitive Paint - ' + fileName))

        #add indicator for new stroke
        if (len(actions[-1]) == 1):
            redo.append([True])
        else:
            redo.append([False])

        #add last substroke
        redo[-1].append(canvas.type(actions[-1][-1]))
        redo[-1].append(canvas.coords(actions[-1][-1]))
        redo[-1].append(
            canvas.itemcget(actions[-1][-1], 'outline') + '#'
            if ((canvas.type(actions[-1][-1])
                in ('oval', 'rectangle', 'polygon'))
                and ((canvas.itemcget(actions[-1][-1], 'fill')
                != canvas.itemcget(actions[-1][-1], 'outline'))))
            else (canvas.itemcget(actions[-1][-1], 'fill'))
        )
        redo[-1].append(canvas.itemcget(actions[-1][-1], 'width'))
        canvas.delete(actions[-1][-1])

        #delete last substroke, deleting full stroke if needed
        if (len(actions[-1]) == 1): del actions[-1]; stroke -= 1
        else: del actions[-1][-1]
#end undosingle(event)

def redoLast(*args):
    #reference variables outside function
    global actions
    global fileName
    global redo
    global saved
    global stroke

    #check first item for new stroke
    if (len(redo) > 1):
        #update saved
        saved = False

        #update title
        window.title(('*Primitive Paint - ' + fileName))

        if redo[-1][0]:
            #update stroke
            stroke += 1
            actions.append([])

            #reverse last redo list for easier removing
            list(redo[-1]).reverse()

            #loop through every item, adding from second, every fourth
            for item, option in enumerate(redo[-1]):
                if (item % 4 == 1):
                    actions[stroke].append(canvasShape(
                        *redo[-1][item + 1],
                        shape = option,
                        fill = redo[-1][item + 2]
                        if ((option == 'line')
                            or (redo[-1][item + 2][-1] != '#'))
                        else '',
                        outline = redo[-1][item + 2][:7],
                        size = int(float(redo[-1][item + 3]))
                        if redo[-1][item + 3] else 1
                    ))
            #end for

            #delete last redo list
            del redo[-1]

        #if first item wasn't a new stroke
        else:
            actions[stroke].append(canvasShape(
                *redo[-1][2],
                shape = redo[-1][1],
                fill = redo[-1][3]
                if ((redo[-1][1] == 'line')
                    or (redo[-1][3][-1] != '#'))
                else '',
                outline = redo[-1][3][:7],
                size = int(float(redo[-1][4]))
                if redo[-1][4] else 1
            ))
            #delete last redo list
            del redo[-1]
#end redo(event)

def redoAll(*args):
    #call redoLast() until there's no more left to redo
    for i in redo[1:]: redoLast()
    #end for
#end redoAll(event)

def saveAny(saveAs, *args):
    #reference variables outside function
    global actions
    global current
    global file
    global fileName
    global redo
    global saved
    global sizePen
    global stroke

    #declaration of internal variables
    filePre = str()

    #checks if no save is needed
    if (saved and not saveAs): return

    #checks for set file
    if ((fileName != 'untitled.txt') and (saveAs == False)):
        #make sure file is open
        try:
            file.close()
            file = open(fileName, mode = 'w')
        except:
            #make sure file name isnt empty
            if (fileName == ''):
                saveAny(True)
                return
            #open file if it isnt empty
            file = open(fileName, mode = 'w')

        #initiate file
        file.write('\n')
    else:
        #if file doesnt exist, ask for file name
        filePre = fileName
        fileName = tkfile.asksaveasfilename(
            defaultextension = '.txt',
            filetypes = [('*.txt', 'TXT')],
            title = 'Primitive Paint - Save As'
        )

        #make sure file name isnt empty
        if (fileName == ''):
            if (filePre == ''):
                window.title(('*Primitive Paint - untitled.txt'))
                fileName = 'untitled.txt'
            else:
                if saved:
                    window.title(('Primitive Paint - ' + filePre))
                else:
                    window.title(('*Primitive Paint - ' + filePre))
                fileName = filePre
            return

        #open and initiate
        file = open(fileName, mode = 'w')
        file.write('\n')

    #write stroke value, size value, and colour value
    file.write(str(stroke) + '\n')
    file.write(str(sizePen.get()) + '\n')
    file.write(current + '\n\n')

    #write actions a line per element
    for action in actions[1:]:
        #indicator that there's more
        file.write('True\n')

        #loop through each item in stroke
        for item in action:
            file.write(canvas.type(item) + '\n')
            file.write(str(canvas.coords(item)) + '\n')
            file.write(
                canvas.itemcget(item, 'outline') + '#\n'
                if ((canvas.type(item)
                    in ('oval', 'rectangle', 'polygon'))
                    and ((canvas.itemcget(item, 'fill')
                    != canvas.itemcget(item, 'outline'))))
                else canvas.itemcget(item, 'fill') + '\n'
            )
            file.write(
                canvas.itemcget(item, 'width') + '\n'
                if (canvas.type(item)
                    in ('line', 'oval', 'rectangle', 'polygon'))
                else '\n'
            )
        #end for
    #end for

    #indicator of the end of actions
    file.write('False')

    #close file after usage
    file.close()

    #update saved
    saved = True

    #update title
    window.title(('Primitive Paint - ' + fileName))
#end saveAny(*args)

def openAny(*args):
    #reference variables outside function
    global actions
    global current
    global file
    global fileName
    global redo
    global saved
    global sizePen
    global stroke

    #declaration of internal variables
    fileRead = list()
    line = int()

    #notify user if unsaved
    if ((not saved) and (not tkmessage.askyesno(
        'Verify', 'Are you sure you want to leave this file unsaved?'
    ))): return

    #open file chooser
    fileName = tkfile.askopenfilename(
        defaultextension = '.txt',
        filetypes = [('*.txt', 'TXT')],
        title = 'Primitive Paint - Open'
    )

    #make sure file name isnt empty
    if (fileName == ''): return

    #open and initiate
    file = open(fileName, mode = 'r')

    #check for starting empty line
    if not file.readline(): return

    #set stroke value, size value, and colour value
    stroke = int(file.readline().rstrip())
    sizePen.set(float(file.readline().rstrip()))
    current = file.readline().rstrip()
    file.readline() #ending empty line

    #loop and copy to list
    for line in file.readlines():
        fileRead.append(line.rstrip())
    #end for

    #close file after usage
    file.close()

    #reset all variables
    actions = [[]]
    line = int()
    redo = [[]]

    #reset canvas
    canvas.delete('all')

    #check if there's at least one stroke
    if (fileRead[line] == 'True'):
        #initiate first item
        actions.append([])

        while (fileRead[line + 1] != 'False'):
            #add canvas item
            actions[-1].append(canvasShape(
                *eval(fileRead[line + 2]),
                shape = fileRead[line + 1],
                fill = fileRead[line + 3]
                if ((fileRead[line + 1] == 'line')
                    or (fileRead[line + 3][-1] != '#'))
                else '',
                outline = fileRead[line + 3][:7],
                size = int(float(fileRead[line + 4]))
                if fileRead[line + 4] else 1
            ))

            #advance counter
            line += 4

            #add new stroke if 'True' found
            if (fileRead[line + 1] == 'True'):
                actions.append([])
                line += 1
        #end while
    #update display
    display.config(bg = current)

    #update saved
    saved = True

    #update title
    window.title(('Primitive Paint - ' + fileName))
#end openAny(*args)

def clearAll(*args):
    #reference variables outside function
    global actions
    global fileName
    global redo
    global saved
    global stroke

    #notify user of leaving of file
    if not saved:
        if not tkmessage.askyesno(
            'Verify', 'Are you sure you want to leave this file unsaved?'
        ): return
    elif not tkmessage.askyesno(
        'Verify', 'Are you sure you want to leave this file?'
    ): return

    #reset actions and stroke
    canvas.delete('all')
    del actions[1:]
    del redo[1:]
    stroke = 0

    #update file name
    fileName = 'untitled.txt'

    #update saved
    saved = True

    #update title
    window.title(('Primitive Paint - untitled.txt'))
#end clearAll(*args)

#create the canvas
canvas = tk.Canvas(
    window,
    width = canvasWidth, 
    height = canvasHeight,
    bg = '#FFFFFF',
    borderwidth = 2,
    relief = 'groove'
)

#put canvas on window, expanding when resized and keeps contents
canvas.grid(
    column = 0,
    row = 1,
    columnspan = 6,
    sticky = 'nsew'
)

#create the menu bar
topMenu = tk.Menu(window)
window.config(menu = topMenu)
fileMenu = tk.Menu(topMenu)
editMenu = tk.Menu(topMenu)
topMenu.add_cascade(label = 'File', menu = fileMenu)
topMenu.add_cascade(label = 'Edit', menu = editMenu)

#create the file menu dropdown
fileMenu.add_command(label = 'New', command = clearAll)
fileMenu.add_command(label = 'Open...', command = openAny)
fileMenu.add_command(
    label = 'Save',
    command = lambda x: saveAny(False)
)
fileMenu.add_command(
    label = 'Save As...',
    command = lambda x: saveAny(True)
)

#create the edit menu dropdown
editMenu.add_command(label = 'Undo', command = undoLast)
editMenu.add_command(label = 'Redo', command = redoLast)
editMenu.add_command(label = 'Redo All', command = redoAll)

#paint when clicked, resize when scrolled, end polygon when right clicked
canvas.bind('<Button-1>', reset)
canvas.bind('<Button-3>', finish)
canvas.bind('<B1-Motion>', paint)
canvas.bind('<ButtonRelease-1>', end)
canvas.bind('<MouseWheel>', resize)
canvas.bind('<Motion>', outline)

#undo stroke with Ctrl + Z and undo single with Ctrl + Shift + Z
window.bind('<Control-z>', undoLast)
window.bind('<Control-Z>', undoSingle)

#redo last with Ctrl + Y and redo all with Ctrl + Shift + Y
window.bind('<Control-y>', redoLast)
window.bind('<Control-Y>', redoAll)

#save with Ctrl + S, save as with Ctrl + A and open with Ctrl + O
window.bind('<Control-s>', lambda x: saveAny(False))
window.bind('<Control-a>', lambda x: saveAny(True))
window.bind('<Control-o>', openAny)

#debug with Ctrl + Alt + Q
window.bind('<Control-Alt-q>', lambda x: sys.exit())

#remind file is unsaved when window x is pressed
window.bind('WM_DELETE_WINDOW', (
    lambda x: window.destroy() if ((not saved) and (not tkmessage.askyesno(
        'Verify', 'Are you sure you want to leave this file unsaved?'
    ))) else None
))

#create the logo and put on top left
logo = tk.Canvas(
    window,
    width = 47 ,
    height = 36,
    borderwidth = 1,
    relief = 'flat'
)
logo.grid(
    column = 0,
    row = 0,
    padx = 2,
    pady = 2,
    sticky = 'nsew'
)

#add logo features
logo.create_text(
    29,
    21,
    text = 'PP',
    font = ('Helvetica', '-30', 'bold'),
    fill = '#68A4F3'
)

#create the label and put left of logo
label = tk.Label(
    window,
    text = 'Drag to draw. Scroll for size.\nClick colour to change',
    padx = 5,
    borderwidth = 2,
    relief = 'flat'
)
label.grid(
    column = 2,
    row = 0,
    sticky = 'nsew'
)

#create the shape selection and put left of label
shapeSelection = tk.Frame(
    window,
    width = 71,
    height = 25,
    borderwidth = 0,
    relief = 'solid'
)
shapeSelection.grid(
    column = 3,
    row = 0
)

#simplify canvas making
def selectionCanvas(column, row):
    #declaration of internal variables
    canvasHolder = str()

    #make the canvas
    canvasHolder = tk.Canvas(
        shapeSelection,
        width = 18,
        height = 13,
        borderwidth = 1,
        relief = 'solid'
    )

    #put canvas at specified column and row
    canvasHolder.grid(column = column, row = row, sticky = 'nsew')

    #simplified position check
    def position(check):
        return True if (column*2 + row == check) else False
    #end position(check)

    #add canvas icon and its function
    if position(0):
        canvasHolder.create_oval(5, 7, 11, 13, fill = '#000000')
        canvasHolder.create_oval(14, 5, 17, 8, fill = '#000000')
        canvasHolder.bind('<Button-1>', lambda x: strokeChange(0))
        canvasHolder.config(bg = '#CCCCCC')
    elif position(1):
        canvasHolder.create_line(7, 13, 16, 5, fill = '#000000')
        canvasHolder.bind('<Button-1>', lambda x: strokeChange(1))
    elif position(2):
        canvasHolder.create_oval(5, 5, 18, 13)
        canvasHolder.create_line(17, 8, 18, 9, fill = '#FFFFFF')
        canvasHolder.create_line(18, 8, 19, 9, fill = '#000000')
        canvasHolder.bind('<Button-1>', lambda x: strokeChange(2))
    elif position(3):
        canvasHolder.create_oval(5, 5, 18, 13, fill = '#000000')
        canvasHolder.create_line(18, 8, 19, 9, fill = '#000000')
        canvasHolder.bind('<Button-1>', lambda x: strokeChange(3))
    elif position(4):
        canvasHolder.create_rectangle(5, 5, 18, 13)
        canvasHolder.bind('<Button-1>', lambda x: strokeChange(4))
    elif position(5):
        canvasHolder.create_rectangle(5, 5, 18, 13, fill = '#000000')
        canvasHolder.bind('<Button-1>', lambda x: strokeChange(5))
    elif position(6):
        canvasHolder.create_polygon(
            5, 5, 5, 13, 10, 13, 18, 5, 18, 13,
            outline = '#000000', fill = ''
        )
        canvasHolder.bind('<Button-1>', lambda x: strokeChange(6))
    elif position(7):
        canvasHolder.create_polygon(
            5, 5, 5, 13, 10, 13, 18, 5, 18, 13, outline = '#000000'
        )
        canvasHolder.bind('<Button-1>', lambda x: strokeChange(7))

    #return the temporary variable holding the canvas
    return canvasHolder
#end selectionCanvas(column, row)

#add canvases in selection frame
shapePencil = selectionCanvas(0, 0)
shapeLine = selectionCanvas(0, 1)
shapeOval = selectionCanvas(1, 0)
shapeFilledOval = selectionCanvas(1, 1)
shapeRectangle = selectionCanvas(2, 0)
shapeFilledRectangle = selectionCanvas(2, 1)
shapePolygon = selectionCanvas(3, 0)
shapeFilledPolygon = selectionCanvas(3, 1)

#create the scale and put on top centre
sizeChoose = tk.Scale(
    window,
    orient = 'horizontal',
    length = 133,
    from_ = 1,
    to = 100,
    borderwidth = 2,
    relief = 'flat',
    variable = sizePen
)
sizeChoose.grid(
    column = 4,
    row = 0,
    sticky = 'nsew'
)

#create the current colour display and put right of button
display = tk.Canvas(
    window,
    width = 50,
    height = 36,
    bg = current,
    borderwidth = 1,
    relief = 'raised'
)
display.grid(
    column = 5,
    row = 0,
    padx = 2,
    pady = 2,
    sticky = 'nsew'
)

#change colour when clicked
display.bind('<Button-1>', colourChange)

#let window resize once possible
window.columnconfigure(1, weight = 1)
window.rowconfigure(1, weight = 1)
canvas.columnconfigure(1, weight = 1)
canvas.rowconfigure(1, weight = 1)

#loop until the end of the window's life
tk.mainloop()

#exit program
sys.exit()
