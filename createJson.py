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

posX = [15, -15, -225, 225]
posY = [225, -225, 15, -15]

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

    if posX[posInicial] == -15:
        direction = 0
        dataCarsLeft.append([i, posX[posInicial], posY[posInicial] + 20*carsLeft, posY[posInicial]*-1, direction])
        carsLeft += 1
    elif posX[posInicial] == 15:
        direction = 180
        dataCarsRight.append([i, posX[posInicial], posY[posInicial] - 20*carsRight, posY[posInicial]*-1, direction])
        carsRight += 1
    elif posX[posInicial] == 225:
        direction = 270
        dataCarsUp.append([i, posX[posInicial] - 20*carsUp, posY[posInicial], posY[posInicial]*-1, direction])
        carsUp += 1
    else:
        direction = 90
        dataCarsDown.append([i, posX[posInicial] + 20*carsDown, posY[posInicial], posY[posInicial]*-1, direction])
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
        "state": 1   
        },
        {
        "id": 2,
        "type": "LIGHT",
        "origin": {
            "x": 30,
            "z": 0
        },
        "state": 1   
        },
        {
        "id": 3,
        "type": "LIGHT",
        "origin": {
            "x": -30,
            "z": 0
        },
        "state": 1   
        }],
    """

for i in range(401):
    frames += """{
            "frame": """ + str(i) + """,
            "cars": ["""
    index = 0
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
        frames += """{
                "id": """ + str(m[0]) + """,
                "x": """ + str(m[1]) + """,
                "z": """ + str(m[2] - i) + """,
                "dir": """ + str(m[4]) + """
            }"""
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

strFile += frames + "]}"
file.write(strFile)
    
