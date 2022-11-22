from ia_2022 import entorn
from practica1 import joc
from practica1.entorn import ClauPercepcio, AccionsRana, Direccio
"""
ClauPercepcio:
    POSICIO = 0
    OLOR = 1
    PARETS = 2

CONSTANTS PER MOURE I ELS SEUS COSTOS
    COST_DESPL=1
    COST_ESPERAR=0.5
    COST_BOTAR=6
"""

COST_ESPERAR = 0.5
COST_BOTAR = 6
COST_DESPL = 1

"""
CLASSE Estat:
ATRIBUTS:
    ·Classe:   No hi ha atributs de classe

    ·Objecte:  1. self.__posicioAgs: array per anar emmagatzemant les accions a realitzar
                                obtingudes en el mètode cerca.
               2. self.__posPizza:   enter que pot agafar els valors dins el rang [0,2]. 
                                Indica els torns d'espera al botar.
               3. self.__nomMax: Indica el nom de l'agen que actualment està exercint de MAX
               4. self.__parets: Indica les parets del taulell
               5. self.__pes: cost d'arribar a un estat en concret
               6. self.__pare: Indica l'estat pare de l'estat
MÈTODES:
    ·Classe: no hi ha mètode de classe.

    ·Objecte:  1. __init__:         constructor que s'hereda de joc.Rana.
               2. __eq__:           mètode que s'hereda.
               3. __lt__:           algoritme genètic per a trobar una solució.
               4. __hash__:         mètode per anar retornant les diferents accions que ha de fer l'agent.
               5. pare:             mètode amb el qual podem saber l'estat pare d'un estat determinat
               6. getPosAg:         mètode amb el qual podem obtenir el valor actual de l'atribut posicioAgs
               7. calculaDistPizza: calcular la distància de l'agent a la pizza.
               8. calculaPuntuació: calcula la puntuació de l'estat que crida a aquest mètode
               9. evaluar:          mètode per evaluar un estat en funció de la perspectiva d'un agent.
               10.es_valid:         mètode per evaluar si un estat és vàlid o no.
               11.es_meta:          mètode que ens diu si un estat és final o no
               12.getAltreAgent:    mètode per a retornar l'agent que no s'ha de moure actualment
               13.generaFills:      mètode per a generar els fills corresponents.
"""
class Estat:
    def __init__(self, posPizza, posAgents, parets, nomMax, pes=0, pare=None):
        self.__posicioAgs = posAgents
        self.__posPizza = posPizza
        self.__nomMax=nomMax
        self.__parets = parets
        self.__pes = pes
        self.__pare = pare

    def __eq__(self, other):
        return self.__posicioAgs == other.getPosAg()

    def __lt__(self, other):
        return False
    def __hash__(self):
        return hash(tuple(self.__posicioAgs))

    @property
    def pare(self):
        return self.__pare

    @pare.setter
    def pare(self, value):
        self.__pare = value

    def getPosAg(self):
        return self.__posicioAgs

    """
    Mètode per a calcular la distància a la pizza
    """
    def calculaDistPizza(self, clau):
        sum = 0
        for i in range(2):
            sum += abs(self.__posPizza[i] - self.__posicioAgs[clau][i])
        return sum

    """
    Mètode per a calcular la puntuació, restant les distàncies.
    """
    def calculaPuntuacio(self,clau):
        claus = list(self.__posicioAgs.keys())

        if (clau == claus[0]):
            puntuacio = self.calculaDistPizza(claus[1]) - self.calculaDistPizza(claus[0]) #>0
        else:
            puntuacio = self.calculaDistPizza(claus[0]) - self.calculaDistPizza(claus[1])

        return puntuacio

    def evaluar(self,clau):
        return self.es_meta(clau),self.calculaPuntuacio(clau)

    """
    Mètode per a veure si un estat és vàlid o no. 
    És mira si l'agent que s'ha mogut està a una posició vàlida.
    Per això obtenim la seva clau amb el mètode getAltreAgent().
    """
    def es_valid(self):
        # canviar índex self.nomMax--->get AltreAgent
        clau = self.getAltreAgent()

        # mirar cas parets
        for p in self.__parets:
            if ((self.__posicioAgs[clau][0] == p[0]) and (self.__posicioAgs[clau][1] == p[1])):
                return False

        # mirar si hi ha agent
        if (self.__posicioAgs[clau][0] == self.__posicioAgs[self.__nomMax][0]):  # mateixa fila??
            if (self.__posicioAgs[clau][1] == self.__posicioAgs[self.__nomMax][1]):  # mateixa columna??
                return False

        # esta dins la matriu?
        return (self.__posicioAgs[clau][0] <= 7) and (self.__posicioAgs[clau][0] >= 0) \
               and (self.__posicioAgs[clau][1] <= 7) and (self.__posicioAgs[clau][1] >= 0)
    """
    Mètode per avaluar si un estat es meta, és a dir, que l'agent ha arribat a la pizza.
    """
    def es_meta(self,clau):
        return ((self.__posicioAgs[clau][0] == self.__posPizza[0]) and (
                    self.__posicioAgs[clau][1] == self.__posPizza[1]))

    """
    Mètode per obtenir l'agent contrari que s'ha mogut. 
    L'atribut self.nomMax representa l'agent que s'ha de moure.
    """
    def getAltreAgent(self):
        claus = list(self.__posicioAgs.keys())

        for i in range(2):
            if (self.__nomMax != claus[i]):
                return claus[i]

        return None

    """
    Mètode per a generar fills iterant sobre un diccionari.
    Es creen fills canviant l'atribut nom que es passa per paràmetre, ja que l'agent que s'ha mogut
    no es moura en el següent estat.
    """
    def generaFills(self):
        movs = {"ESQUERRE": (-1, 0), "DRETA": (+1, 0), "DALT": (0, -1), "BAIX": (0, +1)}
        claus = list(movs.keys())
        fills = []
        otherNom = self.getAltreAgent()

        """
        Cas 1: Moviments de desplaçament a caselles adjacents.
        """
        for i, m in enumerate(movs.values()):
            coords = [sum(tup) for tup in zip(self.__posicioAgs[self.__nomMax], m)] #suma de les coords
            t = self.__posicioAgs.copy() #feim una copia de les coordenades actuals
            t[self.__nomMax] = coords #actualitza les coords de l'agent que s'ha mogut
            actual = Estat(self.__posPizza, t, self.__parets, otherNom, 0,
                           (self, (AccionsRana.MOURE, Direccio.__getitem__(claus[i]))))
            if (actual.es_valid()):
                fills.append(actual) #si és vàlid afegim fill

        """
        Cas 2: Moviments de desplaçament de 2 caselles en caselles
        """
        movs = {"ESQUERRE": (-2, 0), "DRETA": (+2, 0), "DALT": (0, -2), "BAIX": (0, +2)}
        for i, m in enumerate(movs.values()):
            coords = [sum(tup) for tup in zip(self.__posicioAgs[self.__nomMax], m)] #suma de les coords
            t=self.__posicioAgs.copy() #feim una copia de les coordenades actuals
            t[self.__nomMax]=coords #actualitzam coords
            #self.__posicioAgs[self.__nomMax] = coords
            actual = Estat(self.__posPizza, t, self.__parets, otherNom, 0,
                           (self, (AccionsRana.BOTAR, Direccio.__getitem__(claus[i]))))
            if (actual.es_valid()):
                fills.append(actual) #si és vàlid afegim fill

        return fills



"""
CLASSE RANA:
ATRIBUTS:
    ·Classe:   1. SOLUCIO: enter que pot esser 0,1 segons si ha acabat el joc o no

    ·Objecte:  1. self.__jumping: enter que pot agafar els valors dins el rang [0,2]. 
                                  Indica els torns d'espera al botar.
MÈTODES:
    ·Classe: no hi ha mètode de classe.

    ·Objecte:  1. __init__:  constructor que s'hereda de joc.Rana.
               2. __pinta__: mètode que s'hereda.
               3. miniMax:   algoritme de cerca per a trobar la millor jugada actual
               4. max:       mètode per retornar el fill amb major puntuació.
               5. min:       mètode per retornar el fill amb menor puntuació.
               6. actua:     es retorna la acció obtinguda del mètode miniMax.

"""
class Rana(joc.Rana):
        SOLUCIO=0
        def __init__(self, *args, **kwargs):
            super(Rana, self).__init__(*args, **kwargs)
            self.__jumping = 0

        def pinta(self, display):
            pass

        """
        Mètode de cerca MiniMax.
        Funcionalitat: rep com a paràmetres l'estat actual, el torn
        i un enter que representa la profunditat. 

        Acaba si es troba la solució o si i==2(profunditat max).
        """
        def miniMax(self, estat, i, torn_de_max=True):
            meta,score = estat.evaluar(self.nom) #evaluam estat segons perspectiva nom
            if (meta) or (i == 2):
                return score, estat
            #array amb la estructura [(puntuacio,estat)...]
            puntuacio_fills = [self.miniMax(estat_fill, i + 1, not torn_de_max) for estat_fill in estat.generaFills()]


            if (torn_de_max):
                return max(puntuacio_fills)
            else:
                return min(puntuacio_fills)
        """
        Mètode que retorna element màxim(amb la seva puntuació) en una llista segons la puntuació establerta.
        Útil per a elegir el millor fill en cas de MAX.
        """
        def max(self, llista):
            max = 0
            element = None
            for e in llista:
                if (e[1] > max):
                    max = e[1]
                    element = e

            return max,element

        """
        Mètode que retorna element mínim(amb la seva puntuació) en una llista segons la puntuació establerta.
        Útil per a elegir el millor fill en cas de MIN.
        """
        def min(self, llista):
            min = 9999
            element = None
            for e in llista:
                if (e[1] < min):
                    min = e[1]
                    element = e

            return min,element
        """
        Mètode actua que abans de continuar mira si s'ha acabat el joc. Si s'ha acabat, ambdos agents només esperen.
        Cada torn es crida a miniMax, que retornarà un estat el qual anam iterant fins a trobar l'acció a realitzar.
        Cada estat té un atribut pare que es representa per tenir aquesta estructura: (pare,(Accio,Direccio)).
        D'aquesta manera, podem obtenir l'acció a realitzar
        """
        def actua(
                self, percep: entorn.Percepcio
        ) -> entorn.Accio | tuple[entorn.Accio, object]:
            estat = Estat(percep[ClauPercepcio.OLOR], percep[ClauPercepcio.POSICIO], percep[ClauPercepcio.PARETS], self.nom)

            actual=self.miniMax(estat,0)[1]#retorna l'estat més avantatjós per l'agent

            agents=percep[ClauPercepcio.POSICIO].keys()

            #miram si s'ha acabat el joc
            for a in agents:
                if(percep[ClauPercepcio.POSICIO][a]==percep[ClauPercepcio.OLOR]):
                    self.SOLUCIO=1

            #si s'ha acabat el joc els agents no es mouen
            if (self.SOLUCIO == 1):
                return AccionsRana.ESPERAR

            #bucle per anar iterant fins a trobar l'acció corresponent
            while actual.pare is not None:
                pare, accio = actual.pare
                actual = pare


            if(self.__jumping>0):#esta botant??
                self.__jumping-=1
                return AccionsRana.ESPERAR
            else:
                if(accio[0]==AccionsRana.BOTAR):
                    self.__jumping=2
                return accio[0],accio[1] #retornam acció a realitzar