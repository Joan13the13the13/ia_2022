from ia_2022 import entorn
from practica1 import joc
from practica1.entorn import ClauPercepcio, AccionsRana, Direccio
from queue import PriorityQueue
import random
import operator

"""
ClauPercepcio:
    POSICIO = 0
    OLOR = 1
    PARETS = 2


CONSTANTS PER MOURE I ELS REUS COSTOS
    COST_DESPL=1
    COST_ESPERAR=0.5
    COST_BOTAR=6


"""

COST_ESPERAR = 0.5
COST_BOTAR = 6
COST_DESPL = 1

"""
CLASSE Individu:

ATRIBUTS:
    ·Classe:   1. individu_len: longitud màxima d'un individu.
               2. moviments: dictat AccionsRana,Direccio amb les seves respectives tuples(x,y).

    ·Objecte:  1. self.__nom: string on s'emmagatzema el nom de l'agent.

               2. self.__posicioAg: dictat on s'emmagatzemen parelles clau-valor amb nomAgent:posicioAgent.
                                    És a dir, s'emmagatzemen les posicions dels agents corresponents.

               3. self.__accions:   vector de longitud 10 màxima

               4. self.__posPizza:  tupla on s'emmagatzemen les coordenades de la pizza.

               5. self.__parets:    array on es van emmagatzemant les coords de les parets.

MÈTODES:
    ·Classe:   1. createIndiv: mètode on s'itera fins a obtenir un vector d'accions aleatòries.
                               Aquest té una longitud de individu_len(10).

    ·Objecte:  1. __init__:             constructor que crea una instància de la classe individu.

               2. __eq__:               mètode que es crida per a comparar individus.

               3. __lt__:               mètode que es crida per a comparar indvividus.

               4. __hash__:             mètode per identificar els objectes amb un id únic.
                                        Es crea el hash en funció dels moviments que conté.

               5.  getAccions:          mètode per a obtenir les accions de un individu

               6.  getLenAccions:       mètode per a obtenir la longitud del vector d'accions.

               7.  get_key:             es crida per a obtenir la clau corresponent al valor passat per paràmetre.
                                        Es passa una tupla(x,y) i es retorna la acció que correspon.

               8.  getAccionsConvert:   mètode per a retornar el vector de tuples a objectes AccionsRana per a que l'agent
                                        pugui actuar.

               9.  calculaDistPizza:    s'utilitza per a calcular la dist a la pizza, per a posteriorment calcular la fitness.

               10. calFitness:          es calcula la puntuació fitness per a avaluar quins individus són millors.

               11. corregir:            s'utilitza aquest mètode per a retallar la longitud dels indvidus fins a una posició vàlida.

               12. reproduce:           s'utilitza per a reproduir dos individus i obtenir dos fills.

"""


class Individu:
    individu_len = 30
    moviments = {(AccionsRana.MOURE, Direccio.DRETA): (+1, 0), (AccionsRana.MOURE, Direccio.ESQUERRE): (-1, 0),
                 (AccionsRana.MOURE, Direccio.DALT): (0, -1), (AccionsRana.MOURE, Direccio.BAIX): (0, +1),
                 (AccionsRana.BOTAR, Direccio.DRETA): (+2, 0), (AccionsRana.BOTAR, Direccio.ESQUERRE): (-2, 0),
                 (AccionsRana.BOTAR, Direccio.DALT): (0, -2), (AccionsRana.BOTAR, Direccio.BAIX): (0, +2),
                 (AccionsRana.ESPERAR, None): (0, 0)}

    def __init__(self, nom, posPizza, posAgent, individu, parets):
        self.__nom = nom
        self.__posicioAg = posAgent  # ESTRUCTURA --> [NOM_AGENT:(x,y)]
        self.__accions = individu  # ESTRUCTURA --> [m0, m1, m2,..]
        self.__posPizza = posPizza  # ESTRUCTURA --> [(x,y)]
        self.__parets = parets  # ESTRUCTURA --> [(x_1,y_1),(x_2,y_2),(x_3,y_3)]

    def __eq__(self, other):
        return self.__accions == other.getAccions()

    def __lt__(self, other):
        return False

    def __hash__(self):
        return hash(tuple(self.__accions))

    def getAccions(self):
        return self.__accions

    def getLenAccions(self):
        return len(self.__accions)

    def get_key(self, val):
        for key, value in self.moviments.items():
            if val == value:
                return key

    """
    Mètode que tradueix la seqüencia de moviments continguda dins l'atribut "accions" 
    a una llista de ClauPercepcion.Moviment. Obtenim la clau de la coa de prioritat 
    de l'atribut (que es el moviment que s'ha de realitzar).
    Retorna la llista de moviments creada.
    """
    def getAccionsConvert(self):
        accionsConvert = []
        for a in self.__accions:
            acc = self.get_key(a)
            accionsConvert.append(acc)
        return accionsConvert

    """
    Mètode per a calcular la distància a la pizza.
    """
    def calculaDistPizza(self):
        sum = 0
        for i in range(2):
            sum += abs(self.__posPizza[i] - self.__posicioAg[self.nom][i])
        return sum

    """
    Mètode que calcula el valor de la funció de fitness de l'individu que crida a aquest mètode
    Retorna la puntuació de fitness calculada:
    1. Importància del 80% a trobar la solució
    2. Importància del 20% a trobar una solució 'curta'. 
    """
    def calFitness(self):
        pos = self.__posicioAg[self.__nom]

        for i in range(len(self.__accions)):
            pos = tuple(map(operator.add, pos, self.__accions[i]))  # actualitzada posició segons acció
        fitness = abs(self.__posPizza[0] - pos[0]) + abs(self.__posPizza[1] - pos[1]) * 0.8 + 0.2 * len(
            self.__accions)  # dist pizza

        return fitness

    """
    Mètode de classe que que crea un individu amb moviments aleatoris.
    Retorna l'individu creat.
    """
    @classmethod
    def createIndiv(cls):
        ind = []
        for i in range(cls.individu_len):
            ind.append(list(cls.moviments.values())[random.randint(0, 8)])

        return ind

    """
    Mètode per rectificar la longitud d'un individu que ha fet un moviment.
    Es retalla l'individu fins que ha arribat a una posició vàlida.
    Si no té cap moviment vàlid es torna a crear un individu aleatòriament(corregit)
    """
    def corregir(self):
        pos = self.__posicioAg[self.__nom]
        index = 0
        for i in range(len(self.__accions)):
            pos = pos = tuple(map(operator.add, pos, self.__accions[i]))  # actualitzada posició segons acció
            if (pos in self.__parets and self.moviments != (0, 0)) or (
                    pos[0] > 7 or pos[0] < 0 or pos[1] > 7 or pos[1] < 0):
                # index=i
                break
            index += 1
        if (index == 0):  # l'individu té longitud 0
            self.__accions = Individu.createIndiv()
            self.corregir()
        else:
            self.__accions = self.__accions[:index]

    """
    Mètode que reprodueix dos individus (el que crida a aquesta mètode i el que ens passen per paràmetre).
        -Es genera un nombre aleatori per al crosspoint en funció de l'individu més gran.
        -Es genera un nombre de l'1 al 10. 10% probabilitat per mutació.
        -Els fills tenen aquesta estructura:
            1.Primer fill: pare1[:CrossPoint]+pare2[CrossPoint:]
            2.Segon  fill: pare2[:CrossPoint]+pare1[CrossPoint:]
        -Si l'individu té longitud major que 0 es pot aplicar una mutació.
    Retorna els dos fills producte de la reproducció.
    """
    def reproduce(self, other):

        if (len(self.__accions) > len(other.getAccions())):
            max = len(self.__accions)
        else:
            max = other.getLenAccions()

        if (max == 1):  # si l'individu te longitud 1 crosspoint ha de ser 0
            crossPoint = 0
        else:
            crossPoint = random.randint(0, max - 1)

        mutacio1 = random.randint(1, 10)  # probabilitat mutar fill1
        mutacio2 = random.randint(1, 10)  # probabilitat mutar fill2

        # FILL 1: primer tros fins index pare1 + segon tros fins final pare2
        individu1 = self.__accions[:crossPoint] + other.getAccions()[crossPoint:]
        if (len(individu1) > 0):  # es pot aplicar mutació si l'individu té longitud>=1
            if mutacio1 == 1:
                accio1 = random.randint(0, len(Individu.moviments) - 1)  # genera acció aleatòria(index de dict)
                if (len(individu1) > 1):
                    genMutacio1 = random.randint(0, len(individu1) - 1)  # genera index gen aleatori
                else:
                    genMutacio1 = 0  # individu nomes té un gen->index=0
                individu1[genMutacio1] = list(self.moviments.values())[accio1]  # aplica la mutació

        fill1 = Individu(self.__nom, self.__posPizza, self.__posicioAg, individu1, self.__parets)  # crea l'individu

        # FILL 2: primer tros fins index pare2 + segon tros fins final pare1
        individu2 = other.getAccions()[:crossPoint] + self.__accions[crossPoint:]

        if (len(individu2) > 0):  # es pot aplicar mutació si l'individu té longitud>=1
            if mutacio2 == 1:
                accio2 = random.randint(0, len(Individu.moviments) - 1)  # genera acció aleatòria(index de dict)
                if (len(individu2) > 1):
                    genMutacio2 = random.randint(0, len(individu2) - 1)  # genera index gen aleatori
                else:
                    genMutacio2 = 0  # individu nomes té un gen->index=0
                individu2[genMutacio2] = list(self.moviments.values())[accio2]  # aplica la mutació
        fill2 = Individu(self.__nom, self.__posPizza, self.__posicioAg, individu2, self.__parets)  # crea l'individu

        return fill1, fill2


"""
CLASSE RANA:
ATRIBUTS:
    ·Classe:   1. P: nombre invidividus població inicial
               2. solucio: boolean que determina si s'ha trobat la solució

    ·Objecte:  1. self.__accio: array per anar emmagatzemant les accions a realitzar
                                obtingudes en el mètode cerca.
               2. self.__jumping: enter que pot agafar els valors dins el rang [0,2]. 
                                Indica els torns d'espera al botar.
MÈTODES:
    ·Classe: no hi ha mètode de classe.

    ·Objecte:  1. __init__:  constructor que s'hereda de joc.Rana.
               2. __pinta__: mètode que s'hereda.
               3. _cerca:    algoritme genètic per a trobar una solució.
               4.  actua:    mètode per anar retornant les diferents accions que ha de fer l'agent.

"""
class Rana(joc.Rana):
    P = 150
    solucio = False

    def __init__(self, *args, **kwargs):
        super(Rana, self).__init__(*args, **kwargs)
        self.__accions = None
        self.__jumping = 0

    def pinta(self, display):
        pass

    """
    Mètode cerca que genera una població inicial de P individus, els reprodueix i intenta cercar la solucio
    mitjançant el pas de generacions. S'ha posat un límit a 5 generacions, després s'extreu el millor individu.
    """
    def _cerca(self, posPizza, posAg, posParets):
        individus = PriorityQueue()
        fills = []
        solucio = False
        gen = 0
        # generam població inicial
        for i in range(self.P):
            # crear individu
            accions = Individu.createIndiv()
            individu = Individu(self.nom, posPizza, posAg, accions, posParets)
            individu.corregir()
            puntuacio = individu.calFitness()
            individus.put((puntuacio, individu))
        # mentres no soluciuó
        while (not Rana.solucio):
            # reproduir tots individus
            for i in range(self.P - 1):
                _, actual1 = list(individus.queue)[i]
                _, actual2 = list(individus.queue)[i + 1]
                # reproduir
                fill1, fill2 = actual1.reproduce(actual2)
                fill1.corregir()
                fill2.corregir()
                # inserim els fills a un array auxiliar
                fills.append(fill1)
                fills.append(fill2)
                # a cada iteració i augmenta +2
                i = i + 1
            # afegirr fills a priority queue
            for i in range(len(fills)):
                individus.put((fills[i].calFitness(), fills[i]))

            # seleccionam els 50 millors individus i la resta els
            # eliminam de la priority que
            aux = individus
            # buidam la coa de prioritat
            individus = PriorityQueue()
            for i in range(self.P):
                individus.put(aux.get())
            # mirar si algun individu.calFitness == 0
            if list(individus.queue)[0][0] == 0:
                Rana.solucio = True
            gen += 1
            # Cada 5 generacions retornam el millor individu
            if (gen == 5):
                break
        return list(individus.queue)[0][1]

    """
    Mètode actua per a retornar una acció previament introduida desde el mètode cerca.
    Rep una percepció per paràmetre que conté les posicions dels agents, pizza i parets.
    """
    def actua(
            self, percep: entorn.Percepcio
    ) -> entorn.Accio | tuple[entorn.Accio, object]:
        # Assignam a la llista d'accions les accions del millor individu generat pel mètode cerca.
        # Quan la llista d'accions de self.__accions torni a ser None, tornarem a entrar a aquest
        # condicional
        if (self.__accions is None):
            individu = self._cerca(percep[ClauPercepcio.OLOR], percep[ClauPercepcio.POSICIO], percep[ClauPercepcio.PARETS])
            self.__accions = individu.getAccionsConvert()

        if self.__accions:
            if (self.__jumping > 0):  # esta botant
                self.__jumping -= 1
                return AccionsRana.ESPERAR
            else:
                acc = self.__accions.pop(0)
                if (self.__accions is []):
                    self.__accions = None
                if (acc[0] == AccionsRana.BOTAR):
                    self.__jumping = 2
                return acc[0], acc[1]
        else:
            return AccionsRana.ESPERAR