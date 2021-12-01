'''
Simulación de una avenida con paso peatonal

En esta simulación se representa una avenida con dos carriles y un paso peatonal. 
El tráfico se controla con dos semáforos que detienen a los autos en el paso peatonal.
'''

import queue
import agentpy as ap
import numpy as np
import math

# Definición del agente semaforo
class Semaphore(ap.Agent):
    """ 
        Esta clase define a un semáforo.
    """

    def setup(self):
        """ Este método se utiliza para inicializar al semáforo. """
        
        self.step_time = 0.1         # Tiempo que dura cada paso de la simulación

        self.direction = [0, 1]      # Dirección a la que apunta el semáforo

        self.state = 2               # Estado del semáforo 0 = verde, 1 = amarillo, 2 = rojo
        self.state_time = 0          # Tiempo que ha durado el semáforo en el estado actual

        self.voteType = 0            # 0: Justo, 1: Egoísta (Preferencia de 10s)
        self.carsInFront = 0

        self.num = 0
        self.green_duration = 50     # Tiempo que dura el semáforo en verde
        self.yellow_duration = 5     # Tiempo que dura el semáforo en amarillo
        self.red_duration = self.model.p['steps']        # Tiempo total en el que el semáforo ha estado en rojo        

    def update(self):
        """ Este método actualiza el estado del semáforo. """
        self.state_time += self.step_time

        if self.state == 0:
            # Caso en el que el semáforo está en verde
            if self.state_time >= self.green_duration:
                self.set_yellow()
                self.green_duration = 0
        elif self.state == 1:
            # Caso en el que el semáforo está en amarillo
            if self.state_time >= self.yellow_duration:
                self.set_red()

                # Cambiar a verde next semaphore
                next = self.model.getNextSemaphore()
                self.model.semaphores[next].set_green()
        elif self.state == 2:
            # Caso en el que el semáforo está en rojo
            self.red_duration -= 1

    def set_green(self):
        """ Este método forza el semáforo a estar en verde. """        
        self.state = 0
        self.state_time = 0
        self.carsInFront = 0

    def set_yellow(self):
        """ Este método forza el semáforo a estar en amarillo. """        
        self.state = 1
        self.state_time = 0

    def set_red(self):
        """ Este método forza el semáforo a estar en rojo. """        
        self.state = 2
        self.state_time = 0
    
    def checkCarsInFront(self):
        for car in self.model.cars:
            
            # Verifica si el carro va en la misma dirección
            dot_p1 = self.direction[0]*car.direction[0] + self.direction[1]*car.direction[1]                

            if dot_p1 < 0:                  
                self.carsInFront += 1

# Definición del agente auto
class Car(ap.Agent):
    """ 
        Esta clase define a un auto.
    """

    def setup(self):
        """ Este método se utiliza para inicializar un robot limpiador. """
        self.step_time = 0.1          # Tiempo que dura cada paso de la simulación
        self.direction = [1, 0]       # Dirección a la que viaja el auto
        self.dirAngle = 0             # Dirección en grados en que se mueve el carro
        self.speed = 0.0              # Velocidad en metros por segundo
        self.max_speed = 4            # Máxima velocidad en metros por segundo
        self.state = 1                # Car state: 1 = ok, 0 = dead

    def update_position(self):
        """ Este método se utiliza para inicializar la posición del auto. """

        # Verifica si el auto no ha chocado
        if self.state == 0:
            return
        
        self.model.avenue.move_by(self, [self.speed*self.direction[0], self.speed*self.direction[1]])

    def update_speed(self):
        
        """ Este método se utiliza para inicializar la velocidad del auto. """

        # Verifica si el auto no ha chocado
        if self.state == 0:
            return
        
        # Obten la distancia más pequeña a uno de los autos que vaya en la misma dirección        
        p = self.model.avenue.positions[self]

        min_car_distance = 1000000
        for car in self.model.cars:
            if car != self:
                # Verifica si el carro va en la misma dirección
                dot_p1 = self.direction[0]*car.direction[0] + self.direction[1]*car.direction[1]                
                
                # Verifica si el carro está atrás o adelante
                p2 = self.model.avenue.positions[car]
                dot_p2 = (p2[0]-p[0])*self.direction[0] + (p2[1]-p[1])*self.direction[1]

                if dot_p1 > 0 and dot_p2 > 0:                     
                    d = math.sqrt((p[0]-p2[0])**2 + (p[1]-p2[1])**2)                    
                    
                    if min_car_distance > d:
                        min_car_distance = d
       
        # Obten la distancia al próximo semáforo
        min_semaphore_distance = 1000000
        semaphore_state = 0
        close_semaphore = self.model.semaphores[0]
        for semaphore in self.model.semaphores:

            # Verifica si el semáforo apunta hacia el vehículo
            dot_p1 = semaphore.direction[0]*self.direction[0] + semaphore.direction[1]*self.direction[1]
            
            # Verifica si el semáforo está adelante o atrás del vehículo
            p2 = self.model.avenue.positions[semaphore]
            dot_p2 = (p2[0]-p[0])*self.direction[0] + (p2[1]-p[1])*self.direction[1]

            if dot_p1 < 0 and dot_p2 > 0:                            
                d = math.sqrt((p[0]-p2[0])**2 + (p[1]-p2[1])**2)  
                
                if min_semaphore_distance > d:
                    close_semaphore = semaphore
                    min_semaphore_distance = d
                    semaphore_state = semaphore.state
        
        # Actualiza la velocidad del auto
        if min_car_distance < 2:
            self.speed = 0
            self.state = 0

        elif min_car_distance < 10:
              self.speed = np.maximum(self.speed - 200*self.step_time, 0)

        elif min_car_distance < 15:
              self.speed = np.maximum(self.speed - 80*self.step_time, 0)
                
        elif min_semaphore_distance < 45 and semaphore_state == 1:
            self.speed = np.minimum(self.speed + 5*self.step_time, self.max_speed)

        elif min_semaphore_distance < 60 and semaphore_state == 1:
            self.speed = np.maximum(self.speed - 5*self.step_time, 0)
            
        elif min_semaphore_distance < 70 and semaphore_state == 2:
            self.speed = np.maximum(self.speed - 20*self.step_time, 0)

        else:
            self.speed = np.minimum(self.speed + 5*self.step_time, self.max_speed)

# Definicón del modelo de la avenida
class AvenueModel(ap.Model):
    """ Esta clase define un modelo para una avenida simple con semáforo peatonal. """

    def setup(self):
        """ Este método se utiliza para inicializar la avenida con varios autos y semáforos. """
        
        self.strFile = """{
                    "time": 10,
                    "fps": 20,
                    "cars": [
                        """

        self.frames = ""

        # Inicializa los agentes los autos y los semáforos        
        self.cars = ap.AgentList(self, self.p.cars, Car)
        self.cars.step_time =  self.p.step_time
        
        # Cantidad de autos por carril (proporción)
        lane = int(self.p.cars/8)

        # Cantidad de carros en cada carril
        c_north = lane - 1
        c_north2 = lane + 3
        c_south = lane - 1
        c_south2 = lane + 2
        c_east = lane - 2
        c_east2 = lane - 1
        c_west = lane
        c_west2 = self.p.cars - lane * 7

        # Inicializar las direcciones de todos los carros
        carsSum = 0
        for k in range(c_north + c_north2):
            self.cars[k+carsSum].direction = [0,1]
            self.cars[k+carsSum].dirAngle = 90

        carsSum += c_north + c_north2
        for k in range(c_south + c_south2):
            self.cars[k+carsSum].direction = [0,-1]
            self.cars[k+carsSum].dirAngle = 270
        
        carsSum += c_south + c_south2
        for k in range(c_east + c_east2):
            self.cars[k+carsSum].direction = [1, 0]
            self.cars[k+carsSum].dirAngle = 0

        carsSum += c_east + c_east2
        for k in range(c_west + c_west2):
            self.cars[k+carsSum].direction = [-1, 0]
            self.cars[k+carsSum].dirAngle = 180

        self.semaphores = ap.AgentList(self, 4, Semaphore)
        self.semaphores.step_time =  self.p.step_time
        self.semaphores.green_duration = self.p.green
        self.semaphores.yellow_duration = self.p.yellow

        # Mira hacia el norte
        self.semaphores[0].num = 0
        self.semaphores[0].direction = [0, 1]
        # Mira hacia el sur
        self.semaphores[1].num = 1
        self.semaphores[1].direction = [0, -1]
        # Mira hacia el este
        self.semaphores[2].num = 2
        self.semaphores[2].direction = [1, 0]
        # Mira hacia el oeste
        self.semaphores[3].num = 3
        self.semaphores[3].direction = [-1, 0]
        
        # Inicializa el entorno
        self.avenue = ap.Space(self, shape=[self.p.size, self.p.size], torus = True)

        semaphore_separation = 20
                
        # Agrega los semáforos al entorno
        self.avenue.add_agents(self.semaphores, random=True)
        self.avenue.move_to(self.semaphores[0], [self.p.size*0.5 - semaphore_separation, self.p.size*0.5 - semaphore_separation])
        self.avenue.move_to(self.semaphores[1], [self.p.size*0.5 + semaphore_separation, self.p.size*0.5 + semaphore_separation])
        self.avenue.move_to(self.semaphores[2], [self.p.size*0.5 - semaphore_separation, self.p.size*0.5 + semaphore_separation])
        self.avenue.move_to(self.semaphores[3], [self.p.size*0.5 + semaphore_separation, self.p.size*0.5 - semaphore_separation])

        # Inicializar el orden de los semáforos
        self.semaphoreOrder = queue.Queue(4)
        self.semaphores[self.getNextSemaphore()].state = 0

        # Inicializar un semáforo egoísta
        selfish = np.random.randint(0, 4)
        self.semaphores[selfish].voteType = 1

        # Agrega los autos al entorno
        self.avenue.add_agents(self.cars, random=True)

        laneDis = self.p['laneDis']
        crossDistance = self.p['crossDistance']

        carsSum = 0
        # Norte
        for k in range(c_north):
            car = self.cars[k]
            x = self.p.size*0.5 + laneDis
            y = (self.p.size*0.5 - crossDistance) - np.random.randint(10,12) * (k+1)
            self.avenue.move_to(car, [x,y])
            self.initializeCar(car)
            self.strFile += ","

        carsSum += c_north
        for k in range(c_north2):
            car = self.cars[k+carsSum]
            x = self.p.size*0.5 + laneDis*2
            y = (self.p.size*0.5 - crossDistance) - np.random.randint(10,12) * (k+1)
            self.avenue.move_to(car, [x,y])

            self.initializeCar(car)
            self.strFile += ","

        carsSum += c_north2
        # Sur
        for k in range(c_south):
            car = self.cars[k+carsSum]
            x = self.p.size*0.5 - laneDis
            y = (self.p.size*0.5 + crossDistance) + np.random.randint(10,12) * (k+1)
            self.avenue.move_to(car, [x,y])

            self.initializeCar(car)
            self.strFile += ","
        
        carsSum += c_south
        for k in range(c_south2):
            car = self.cars[k+carsSum]
            x = self.p.size*0.5 - laneDis*2
            y = (self.p.size*0.5 + crossDistance) + np.random.randint(10,12) * (k+1)
            self.avenue.move_to(car, [x,y])

            self.initializeCar(car)
            self.strFile += ","

        carsSum += c_south2
        # Este
        for k in range(c_east):
            car = self.cars[k+carsSum]
            x = (self.p.size*0.5 - crossDistance) - np.random.randint(10,12) * (k+1)
            y = self.p.size*0.5 - laneDis
            self.avenue.move_to(car, [x,y])

            self.initializeCar(car)
            self.strFile += ","
        
        carsSum += c_east
        for k in range(c_east2):
            car = self.cars[k+carsSum]
            x = (self.p.size*0.5 - crossDistance) - np.random.randint(10,12) * (k+1)
            y = self.p.size*0.5 - laneDis*2
            self.avenue.move_to(car, [x,y])

            self.initializeCar(car)
            self.strFile += ","
        
        carsSum += c_east2
        # Oeste
        for k in range(c_west):
            car = self.cars[k+carsSum]
            x = (self.p.size*0.5 + crossDistance) + np.random.randint(10,12) * (k+1)
            y = self.p.size*0.5 + laneDis
            self.avenue.move_to(car, [x,y])

            self.initializeCar(car)
            self.strFile += ","
          
        carsSum += c_west
        for k in range(c_west2):
            car = self.cars[k+carsSum]
            x = (self.p.size*0.5 + crossDistance) + np.random.randint(10,12) * (k+1)
            y = self.p.size*0.5 + laneDis*2
            self.avenue.move_to(car, [x,y])

            self.initializeCar(car)
            if k < c_west2-1:
              self.strFile += ","

        self.finishCars()
        self.initializeSemaphore(self.semaphores[0])
        self.strFile += ","
        self.initializeSemaphore(self.semaphores[1])
        self.strFile += ","
        self.initializeSemaphore(self.semaphores[2])
        self.strFile += ","
        self.initializeSemaphore(self.semaphores[3])
        self.finishInitialization()

    def step(self):
        """ Este método se invoca para actualizar el estado de la avenida. """        
        self.semaphores.update()

        self.cars.update_position()
        self.cars.update_speed()

        self.addFrame()
        if self.t < self.p.steps:
          self.frames += ","
    
    def update(self):
        if self.t >= self.p.steps:
            self.stop()
            
    def end(self):        
        self.closeFile()
    
    def transformDir(self, direction):
        if direction == [1, 0]:
            dir = 0
        elif direction == [0, 1]:
            dir = 90
        elif direction == [-1, 0]:
            dir = 180
        elif direction == [0, -1]:
            dir = 270
        return dir

    def smallerTime(self, e):
        return e[0]
    
    # Definir un nuevo orden para los semáforos, mediante una votación
    def generateSemaphoreOrder(self):
        times = [0]*4
        for i in range(len(self.semaphores)):
            # Si el semáforo es egoísta, restarle tiempo del rojo para que tenga más prioridad
            if self.semaphores[i].voteType == 1:
                self.semaphores[i].red_duration -= 4
            
            # Si el semáforo está en alto, se cuenta la cantidad de autos que tiene de frente
            # De tal manera que el la luz verde dure el tiempo justo para que todos los autos pasen
            if self.semaphores[i].state == 2:
                self.semaphores[i].checkCarsInFront()
                self.semaphores[i].green_duration += self.semaphores[i].carsInFront
                # A los semáforos comunes (no el egoísta), se les resta tiempo a la duración del rojo
                # De tal manera que tengan mayor prioridad
                if self.semaphores[i].voteType == 0:
                    self.semaphores[i].red_duration -= self.semaphores[i].carsInFront

            times[i] = [self.semaphores[i].red_duration, i]
            
        # Ordenar descendentemente según su tiempo en rojo
        times.sort(key = self.smallerTime)

        # Guardar el orden en la cola
        for semaphore in times:
            self.semaphoreOrder.put(semaphore[1])
    
    # Tomar el siguiente semáforo de la lista
    def getNextSemaphore(self):
        
        if self.semaphoreOrder.empty():
            self.generateSemaphoreOrder()
        return self.semaphoreOrder.get()


    # Funciones para crear el archivo JSON

    # Agregar Auto a la inicialización del archivo
    def initializeCar(self, car):
        self.strFile += """{
                  "id": """ + str(car.id) + """,
                  "type": "CAR",
                  "origin": {
                      "x": """ + str(self.avenue.positions[car][1]-self.p.size*0.5) + """,
                      "z": """ + str(self.avenue.positions[car][0]-self.p.size*0.5) + """
                  },
                  "dir": """ + str(car.dirAngle) + """
              }"""
    
    # Cerrar arreglo de autos e inicializar el de Semáforos
    def finishCars(self):
        self.strFile += """],
                "trafficLights": ["""

    # Inicializar semáforo en el archivo
    def initializeSemaphore(self, light):
        self.strFile += """{
                  "id": """ + str(light.id) + """,
                  "type": "LIGHT",
                  "origin": {
                      "x": """ + str(self.avenue.positions[light][1]-self.p.size*0.5) + """,
                      "z": """ + str(self.avenue.positions[light][0]-self.p.size*0.5) + """
                  },
                  "state": """ + str(light.state) + """,
                  "dir": """ + str(self.transformDir(light.direction)) + """
              }"""

    # Cerrar arreglo de semáforos   
    def finishInitialization(self):
        self.strFile += """],
              """
        self.frames = """"frames": [
            """
    # Agregar frame nuevo
    def addFrame(self):
        
        self.frames += """{
                            "frame": """ + str(self.t) + """,
                            "trafficLights": ["""
        carSize = len(self.cars)
        trafficSize = len(self.semaphores)

        for i in range(trafficSize): 
            self.frames += """{
                                  "id": """ + str(self.semaphores[i].id) + """,
                                  "state": """ + str(self.semaphores[i].state) + """
                              }"""
            if i < trafficSize-1:
              self.frames += ","
        

        self.frames += """],
                          "cars": ["""
        for i in range(carSize):
            self.frames += """{
                                  "id": """ + str(self.cars[i].id) + """,
                                  "x": """ + str(self.avenue.positions[self.cars[i]][1]-self.p.size*0.5) + """,
                                  "z": """ + str(self.avenue.positions[self.cars[i]][0]-self.p.size*0.5) + """,
                                  "dir": """ + str(self.cars[i].dirAngle) + """
                              }"""
            if i < carSize-1:
              self.frames += ","
        
        self.frames += """]
            }"""

    # Cerrar el archivo y agregar el string de los objetos JSON
    def closeFile(self):
        with open("testData.json", "w") as file:
          self.strFile += self.frames + "]}"
          # Parse
          file.write(self.strFile)

# Parametros
parameters = {
    'step_time': 0.1,       # Procentaje de área cubierta por árboles
    'size': 1000,           # Tamaño en metros de la avenida
    'green': 0,             # Duración de la luz verde
    'yellow': 5,            # Duración de la luz amarilla
    'cars': 32,             # Número de autos en la simulación
    'steps': 1000,           # Número de pasos de la simulación
    'laneDis': 5,           # Distancia entre carriles
    'semaphores': 4,        # Cantidad de Semáforos en la simulación
    'crossDistance': 30     # Distancia del origen al inicio de cada carril
}

# Simulación
model = AvenueModel(parameters)
results = model.run()