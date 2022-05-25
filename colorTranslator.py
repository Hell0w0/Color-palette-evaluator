from tabulate import tabulate
import copy

# Takes the input from the text file and removes unneccesary characters
def cleanUp(input):
    #Clean up string
    input = [s.replace(" ","").replace("rgba","").replace("rgb","").replace("RGB","").replace("(","").replace(","," ").replace(")","").split(" ") for s in input]
    
    #Convert to int
    for i in range(len(input)):
        for j in range(len(input[i])):
            input[i][j] = int(input[i][j])
    return input 

# Translates a palette from RGB to LMS 

def RGBtoLMS(paletteRGB):
    result = []
    LMS = [[17.8824, 43.5161, 4.11935],
    [3.45565, 27.1554, 3.86714],
    [0.0299566, 0.184309, 1.46709]]

    for color in paletteRGB:
        paletteLMS=[0,0,0]
        for i in range(len(color)):
            for j in range(len(LMS)):
                paletteLMS[i]+=LMS[i][j]*color[j]
        result.append(paletteLMS)
    return result
# Translates a palette from LMS to RGB 

def LMStoRGB(paletteLMS):
    RGBFlag = ["r","g","b"]
    result = []
    LMS = [[0.080944,-0.130504, 0.116721],
    [-0.0102485 ,0.0540194 ,-0.113615],
    [-0.000365294, -0.00412163, 0.693513 ]]
    for color in paletteLMS:
        paletteRGB={"r":0,"g":0,"b":0}
        for i in range(len(color)):
            for j in range(len(LMS)):
                paletteRGB[RGBFlag[i]]+=LMS[i][j]*color[j]
            paletteRGB[RGBFlag[i]] = round(paletteRGB[RGBFlag[i]])
        result.append(paletteRGB)
    return result
# Translates a palette from RGB to HSL 

def RGBtoHSL(paletteRGB):
    paletteHSL = []
    for color in paletteRGB:
        # 0 = R , 1 = G , 2 = B
        RGB = []
        #Divides the RGB value by 255
        for indexRGB in color:
            RGB.append(color[indexRGB]/255)
        max_value = max(RGB)
        max_index = RGB.index(max_value)
        min_value = min(RGB)
        range = max_value - min_value

        #Hue
        
        if max_index == 0:
            hue = ((RGB[1] - RGB[2])/range)%6
        elif max_index == 1:
            hue = ((RGB[2] - RGB[0])/range)+2
        else:
            hue = ((RGB[0] - RGB[1])/range)+4
        #Hue decimal translated to degrees.
        hue = hue * 60
        
        #Lightness

        lightness = (max_value + min_value)/2


        #Saturation

        saturation = range/(1-abs(2*lightness-1))
       
        paletteHSL.append({"h":round(hue),"s":round(saturation,2),"l":round(lightness,2)})
    return paletteHSL

# Translates a palette from HSL to RGB 
def HSLtoRGB(paletteHSL):
    paletteRGB=[]
    for color in paletteHSL:
        range = (1-abs(2*color["l"]-1))*color["s"]
        hue = color["h"]/60
        # X = Second largest compeneent
        x  = range * (1 - abs((hue%2) -1))

        if  0 <= hue < 1:
            R1,G1,B1 = (range,x,0)
        elif 1  <= hue < 2:
            R1,G1,B1 = (x,range,0)
        elif 2  <= hue < 3:
            R1,G1,B1 = (0,range,x)
        elif 3  <= hue < 4:
            R1,G1,B1 = (0,x,range)
        elif 4  <= hue < 5:
            R1,G1,B1 = (x,0,range)
        elif 5  <= hue < 6:
            R1,G1,B1 = (range,0,x)
        
        min_value  = color["l"] - (range/2)

        R2,G2,B2 = (R1 + min_value,G1 + min_value,B1 + min_value)
        R,G,B = round(R2*255),round(G2*255),round(B2*255)
        paletteRGB.append({"r":R,"g":G,"b":B})
    return paletteRGB

# Converts the colors to red colorblindness by matrix multiplication
def defectColor(palette):
    result = []
    M = [[0, 2.02344, -2.52581],[0,1,0],[0,0,1]]
    for color in palette:
        filter=[0,0,0]
        for i in range(len(color)):
            for j in range(len(M)):
                filter[i]+=M[i][j]*color[j]
        result.append(filter)
    return result
# Simulates red colorblindness
def simulateRed(palette):
    paletteLMS = RGBtoLMS(palette)
    result = defectColor(paletteLMS)
    return LMStoRGB(result)
# Simulates blue colorblindness
def simulateBlue(palette):
    result = []
    RGBFlag = ["r","g","b"]
    M = [[1.255528,	-0.076749,	-0.178779],[-0.078411,	0.930809,	0.147602],[0.004733,	0.691367,	0.303900]]
    for color in palette:
        paletteRGB={"r":0,"g":0,"b":0}
        for i in range(len(color)):
            for j in range(len(M)):
                paletteRGB[RGBFlag[i]]+=M[i][j]*color[j]
            paletteRGB[RGBFlag[i]] = round(paletteRGB[RGBFlag[i]])
        result.append(paletteRGB)
    return result
# Changes which hue range the colors are within until theres an equal or 1 difference of colors.
def balancePaletteRed(palette):
    while True:
        Y = []
        B = []
        for i in range(len(palette)):
            if 0 <= palette[i]["h"] <= 180 or 343 <= palette[i]["h"] <= 360:
                Y.append(i)
            elif 181 <= palette[i]["h"] <= 342:
                B.append(i)
        if len(Y) > len(B)+1:
            #Raise hue untill its complementary color
            while palette[Y[-1]]["h"] <= 180:
                palette[Y[-1]]["h"]+=50
            while 343 <= palette[Y[-1]]["h"] <= 360:
                palette[Y[-1]]["h"]-=50

        elif len(Y)+1 < len(B):
            #Raise hue untill its complementary color
            while  181 <= palette[B[-1]]["h"] <= 342:
                palette[B[-1]]["h"]-=50
        else:
            return palette
# Changes which hue range the colors are within until theres an equal or 1 difference of colors. 
def balancePaletteBlue(palette):
    while True:
        R = []
        B = []
        for i in range(len(palette)):
            if 0 <= palette[i]["h"] <= 70 or 280 <= palette[i]["h"] <= 360:
                R.append(i)
            elif 71 <= palette[i]["h"] <= 279:
                B.append(i)
        if len(R) > len(B)+1:
            #Raise hue untill its complementary color
            while palette[R[-1]]["h"] <= 70:
                palette[R[-1]]["h"]+=50
            while 280 <= palette[R[-1]]["h"] <= 360:
                palette[R[-1]]["h"]-=50
        elif len(R)+1 < len(B):
            #Raise hue untill its complementary color
            while 71 <= palette[B[-1]]["h"] <= 279:
                palette[B[-1]]["h"]+=50
        else:
            return palette
# Returns a new palette with optimised colors for red colorblindness with high contrast

def newPaletteRed(palette):
    yellow = []
    blue = []
    #Sets the hue and saturation of each color within the hue range
    for i in range(len(palette)):
        if 0 <= palette[i]["h"] <= 180 or 343 <= palette[i]["h"] <= 360:
            palette[i]["h"]=60
            palette[i]["s"]=0.6
            yellow.append(i)
        elif 181 <= palette[i]["h"] <= 342:
            palette[i]["h"]=240
            palette[i]["s"]=0.6
            blue.append(i)
    #Applies as high contrast as possible
    #Yellow range
    if len(yellow) == 1:
        palette[yellow[0]]["l"]=0.5
    elif len(yellow)  == 2:
        palette[yellow[0]]["l"]=0.65
        palette[yellow[1]]["l"]=0.2
    elif len(yellow) > 2:
        splitY  = 0.7/(len(yellow))
        for i in range(len(yellow)):
            palette[yellow[i]]["l"] = round(0.65 - (splitY * i),2)
    
    #Blue range
    if len(blue) == 1:
        palette[blue[0]]["l"]=0.6
    elif len(blue)  == 2:
        palette[blue[0]]["l"]=0.75
        palette[blue[1]]["l"]=0.4        
    elif len(blue) > 2:
        splitB  = 0.5/(len(yellow))
        for i in range(len(blue)):
            palette[blue[i]]["l"] = round(0.75 - (splitB * i),2)
    return palette
# Returns a new palette with optimised colors for blue colorblindness with high contrast
def newPaletteBlue(palette):
    red = []
    blue = []
    #Sets the hue and saturation of each color within the hue range
    for i in range(len(palette)):
        if 0 <= palette[i]["h"] <= 70 or 280 <= palette[i]["h"] <= 360:
            palette[i]["h"]=0
            palette[i]["s"]=0.6
            red.append(i)
        elif 71 <= palette[i]["h"] <= 279:
            palette[i]["h"]=175
            palette[i]["s"]=0.6
            blue.append(i)
    #Applies as high contrast as possible
    #Red range
    if len(red)  == 2:
        palette[red[0]]["l"]=0.75
        palette[red[1]]["l"]=0.25
        #Darkest shade needs more saturation to be distingushable from 
        # the darker shade in the other hue range
        palette[red[1]]["s"]=1
    elif len(red) > 2:
        splitR  = 0.75/(len(red))
        for i in range(len(red)):
            palette[red[i]]["l"] = round(0.75 - (splitR * i),2)
        #Darkest shade needs more saturation to be distingushable from 
        # the darker shade in the other hue range
        palette[red[-1]]["s"]=1
    #Blue range
    if len(blue)  == 2:
        palette[blue[0]]["l"]=0.75
        palette[blue[1]]["l"]=0.25
    elif len(blue) > 2:
        splitB  = 0.75/(len(blue))
        for i in range(len(blue)):
            palette[blue[i]]["l"] = round(0.75 - (splitB * i),2)
    return palette

# Computes the contrast ratio between two colors
def contrastRatio(pair):
    colors = copy.deepcopy(pair)
    luminance = []
    for color in colors:
        for x in ["r","g","b"]:
            color[x] = color[x]/255
            if color[x] <= 0.03928:
                color[x] = color[x]/12.92
            else:
                color[x] = pow(((color[x]+0.055)/1.055),2.4)
        luminance.append(0.2126 * color["r"] + 0.7152 * color["g"] + 0.0722 * color["b"])     
    #Find the lightest colors
    if luminance[0] > luminance[1]:
        ratio = (luminance[0]+0.05)/(luminance[1]+0.05)
    else:
        ratio = (luminance[1]+0.05)/(luminance[0]+0.05)
    return round(ratio,2)
# Prints a table with all the color combinations contrast ratio
def contrastRatioTable(palette):
    head=["Color"]
    head.extend(range(1,len(palette)+1))
    colorsRatios = []
    average=["Average"]
    for i in range(len(palette)):
        ratio = [i+1]
        sumaverage =0
        for j in range(len(palette)):
            if j == i:
                ratio.append("-")
            else:
                contrast = contrastRatio([palette[i],palette[j]])
                ratio.append(contrast)
                sumaverage+=contrast
        average.append(round(sumaverage/(len(palette)-1),2))
        colorsRatios.append(ratio)
    colorsRatios.append(average)
    total = round(sum(average[1:])/len(palette),2)
    print("\nContrast ratios for every color combination: \n")
    print(tabulate(colorsRatios,headers=head,tablefmt="fancy_grid"))
    print("\n")
    print("The total average contrast ratio is: "+str(total))

# Prints the colors in a palette
def displayRGBPalette(palette):
    for index,color in enumerate(palette):
        print(str(index+1)+": RGB("+str(color["r"])+","+str(color["g"])+","+str(color["b"])+")")
# Gets the colors from the input file
def getPalette():
    f = open("color.txt")
    colors = f.read().splitlines()
    return cleanUp(colors)

def printResult(result):
    paletteRGB = HSLtoRGB(result)
    print("New color palette \n")
    displayRGBPalette(paletteRGB)
    contrastRatioTable(paletteRGB)
    print("\n")

def main():

    palette = getPalette()
    print(" \n _______________________ \n")
    print("  Red Colorblindness")
    print(" _______________________ \n")

    #Simulates colorblindess for current palette
    paletteRed = simulateRed(palette)
    paletteBlue = simulateBlue(palette)

    print("\nPalette with red colorblind filter\n")
    #Displays the simulated colors and evaluates contast ratio
    displayRGBPalette(paletteRed)
    contrastRatioTable(paletteRed)
    print(" \n _______________________ \n")
    #Recommended color palette with high contrast
    hslRed = RGBtoHSL(paletteRed)
    balancedRed = balancePaletteRed(hslRed)
    resultRed = newPaletteRed(balancedRed)
    printResult(resultRed)


    print(" \n _______________________ \n")
    print("  Blue Colorblindness")
    print(" _______________________ \n")


    print("\nPalette with blue colorblind filter\n")
    #Displays the simulated colors and evaluates contast ratio
    displayRGBPalette(paletteBlue)
    contrastRatioTable(paletteBlue)
    print(" \n _______________________ \n")
    #Recommended color palette with high contrast
    hslBlue = RGBtoHSL(paletteBlue)
    balancedBlue = balancePaletteBlue(hslBlue)
    resultBlue = newPaletteBlue(balancedBlue)
    printResult(resultBlue)

    
main()