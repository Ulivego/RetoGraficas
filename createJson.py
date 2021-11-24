#Programa que escribe el archivo json con los datos para la simulación
import random

file = open("dataSimul.json", "w")
strFile = """{
    "time": 10,
    "fps": 20,
    "cars": [
        """

frames = """"frames": [
    """

posX = [12.5, -12.5, -225, 225]
posY = [225, -225, 12.5, -12.5]

cant = 10
dataCarsLeft = []
dataCarsRight = []
dataCarsUp = []
dataCarsDown = []
carsLeft = 0
carsRight = 0
carsUp = 0
carsDown = 0
for i in range(cant):
    posInicial = random.randint(0, 3)

    if posX[posInicial] == -12.5:
        direction = 0
        dataCarsLeft.append([i, posX[posInicial], posY[posInicial] + 20*carsLeft, posY[posInicial]*-1, direction, posY[posInicial] + 20*carsLeft])
        carsLeft += 1
    elif posX[posInicial] == 12.5:
        direction = 180
        dataCarsRight.append([i, posX[posInicial], posY[posInicial] + 20*carsRight, posY[posInicial]*-1, direction, posY[posInicial] + 20*carsRight])
        carsRight += 1
    elif posX[posInicial] == 225:
        direction = 270
        dataCarsUp.append([i, posX[posInicial] - 20*carsUp, posY[posInicial], posY[posInicial]*-1, direction, posX[posInicial] - 20*carsUp])
        carsUp += 1
    else:
        direction = 90
        dataCarsDown.append([i, posX[posInicial] + 20*carsDown, posY[posInicial], posY[posInicial]*-1, direction, posX[posInicial] + 20*carsDown])
        carsDown += 1
    
    strFile += """{
        "id": """ + str(i) + """,
        "type": "CAR",
        "origin": {
            "x": """ + str(posX[posInicial]) + """,
            "z": """ + str(posY[posInicial]) + """
        },
        "target": {
            "x": """ + str(posX[posInicial]) + """,
            "z": """ + str(posY[posInicial] * -1) + """
        },
        "dir": """ + str(direction)
    if i < cant-1:
        strFile += """
        },
        """
    else:
        strFile += """
        }],
        """

strFile += """
    "trafficLights": [
        {
        "id": 0,
        "type": "LIGHT",
        "origin": {
            "x": 0,
            "z": -30
        },
        "state": 1   
        },
        {
        "id": 1,
        "type": "LIGHT",
        "origin": {
            "x": 0,
            "z": 30
        },
        "state": 0   
        },
        {
        "id": 2,
        "type": "LIGHT",
        "origin": {
            "x": 30,
            "z": 0
        },
        "state": 0   
        },
        {
        "id": 3,
        "type": "LIGHT",
        "origin": {
            "x": -30,
            "z": 0
        },
        "state": 0   
        }],
    """

seg = 0
tLights = [1, 0, 0, 0]
lightGreen = 0

for i in range(401):
    frames += """{
            "frame": """ + str(i) + """,
            "trafficLights": ["""
    
    #Tiempos en los que se cambia el semáforo
    if (seg < 200):
        tLights[lightGreen] = 1
    elif (seg < 300):
        tLights[lightGreen] = 0
        # if seg < 299:
        #     tLights[lightGreen] = 1
        if lightGreen < 3:
            lightGreen = 0
        else:
            lightGreen += 1
    if (seg == 400):
        seg = -1
        
    # elif (seg == 400):
    #     tLights[lightGreen][0] = 0
    #     tLights[lightGreen][1] = 0
    #     if lightGreen < 3:
    #         lightGreen = 0
    #     else:
    #         lightGreen += 1
    #     seg = 0

    #Texto para el json de los semáforos
    for m in range(4):
        frames += """{
                     "id": """ + str(m) + """,
                     "state": """ + str(tLights[m]) + """
                     }"""
        if m < 3:
            frames += ","
        

    index = 0

    frames += """],
    "cars": ["""
    for j in dataCarsLeft:
        frames += """{
                    "id": """ + str(j[0]) + """,
                    "x": """ + str(j[1]) + """,
                    "z": """ + str(j[2] + i) + """,
                    "dir": """ + str(j[4]) + """
                }"""
        if index < cant-1:
            frames += ","
        index += 1
    for m in dataCarsRight:
        if m[5] <= m[2] - 195 and tLights[0] == 0:
            stop = 0
        else:
            stop = 1
        frames += """{
                    "id": """ + str(m[0]) + """,
                    "x": """ + str(m[1]) + """,
                    "z": """ + str(m[5] - stop) + """,
                    "dir": """ + str(m[4]) + """
                    }"""
        m[5] = m[5] - stop
        if index < cant-1:
            frames += ","
        index += 1
    for n in dataCarsUp:
        frames += """{
                "id": """ + str(n[0]) + """,
                "x": """ + str(n[1] - i) + """,
                "z": """ + str(n[2]) + """,
                "dir": """ + str(n[4]) + """
            }"""
        if index < cant-1:
            frames += ","
        index += 1
    for o in dataCarsDown:
        frames += """{
                "id": """ + str(o[0]) + """,
                "x": """ + str(o[1]  + i) + """,
                "z": """ + str(o[2]) + """,
                "dir": """ + str(o[4]) + """
            }"""
        if index < cant-1:
            frames += ","
        index += 1

    frames += """]
    }"""
    if i < 400:
        frames += ","

    seg += 1

strFile += frames + "]}"
file.write(strFile)
    
