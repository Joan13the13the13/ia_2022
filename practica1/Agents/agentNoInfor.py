from ia_2022 import entorn
from practica1 import joc
from practica1.entorn import ClauPercepcio, AccionsRana, Direccio

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
CLASSE Estat:
ATRIBUTS:
    ·Classe:   No hi ha atributs de classe

    ·Objecte:  1. self.__posicioAgs: array per anar emmagatzemant les accions a realitzar
                                    obtingudes en el mètode cerca.
               2. self.__posPizza:  enter que pot agafar els valors dins el rang [0,2]. 
                                    Indica els torns d'espera al botar.
               3. self.__nom:       Indica el nom de l'agent
               4. self.__parets:    Indica les parets del taulell
               5. self.__pes:       Indica el acumulat fins arribar a aquest node
               6. self.__pare:      Indica l'estat pare de l'estat
MÈTODES:
    ·Classe: no hi ha mètode de classe.

    ·Objecte:  1. __init__:         constructor que s'hereda de joc.Rana.
               2. __eq__:           mètode que s'hereda.
               3. __lt__:           algoritme genètic per a trobar una solució.
               4. __hash__:         mètode per anar retornant les diferents accions que ha de fer l'agent.
               5. pare:             mètode amb el qual podem saber l'estat pare d'un estat determinat
               6. es_valid:         comprova si un estat és vàlid o no.
               7. es_meta:          mètode que ens diu si un estat és final o no
               8. generaFills:      mètode per a generar els fills corresponents.
               9. getPosAg:         mètode per a obtenir la posició d'un agent.
"""

class Estat:
    """
    Constructor que rep per paràmetres la posició de la pizza,agent, parets i opcionalment pes,pare.
    """
    def __init__(self, posPizza, posAgent, parets,nom, pes=0, pare=None):
        self.__posicioAg = posAgent
        self.__posPizza = posPizza
        self.__nom = nom
        self.__parets = parets
        self.__pes = pes
        self.__pare = pare

    def __eq__(self, other):
        return self.__posicioAg == other.getPosAg()

    def __lt__(self, other):
        return False

    def __hash__(self):
        return hash(tuple(self.__posicioAg))

    @property
    def pare(self):
        return self.__pare

    @pare.setter
    def pare(self, value):
        self.__pare = value

    """
    Mètode que té la funció de mirar si un estat és vàlid.
    És a dir, que l'agent no està fora del mapa ni en una paret.
    """
    def es_valid(self):
        # mirar si hi ha parets
        for p in self.__parets:
            if((self.__posicioAg[self.__nom][0]==p[0])and(self.__posicioAg[self.__nom][1]==p[1])):
                return False
        # mirar si està dins el mapa
        return (self.__posicioAg[self.__nom][0] <= 7) and (self.__posicioAg[self.__nom][0] >= 0) \
               and (self.__posicioAg[self.__nom][1] <= 7) and (self.__posicioAg[self.__nom][1] >= 0)

    """
    Mètode per evaluar si l'agent ha arribat a la meta.
    """
    def es_meta(self):
        return (self.__posicioAg[self.__nom][0] == self.__posPizza[0]) and (
                    self.__posicioAg[self.__nom][1] == self.__posPizza[1])
    """
    Mètode per a obtenir la posició d'un agent.
    Es retorna en format de diccionari.
    """
    def getPosAg(self):
        return self.__posicioAg

    """
    Mètode que s'encarrega de generar els fills iterant amb els valors d'un diccionari, on els quals coincideixen amb els
    strings dels possibles valors de la Direcció. D'aquesta manera, podem reutilitzar l'índex per passar-lo per paràmetre
    i obtenir la direcció corresponent a la iteració actual.
    """
    def generaFills(self):
        movs = {"ESQUERRE": (-1, 0), "DRETA": (+1, 0), "DALT": (0, -1), "BAIX": (0, +1)}
        claus = list(movs.keys())
        fills = []

        """
        Cas 1: Moviments de desplaçament a caselles adjacents.
        """
        for i, m in enumerate(movs.values()):
            coords = [sum(tup) for tup in zip(self.__posicioAg[self.__nom], m)]
            coord = {self.__nom: coords}
            cost = self.__pes + COST_DESPL
            actual = Estat(self.__posPizza, coord, self.__parets,self.__nom, cost,
                           (self, (AccionsRana.MOURE, Direccio.__getitem__(claus[i]))))
            if (actual.es_valid()):
                fills.append(actual)

        """
        Cas 2: Moviments de desplaçament de 2 caselles en 2 caselles.
        """
        movs = {"ESQUERRE": (-2, 0), "DRETA": (+2, 0), "DALT": (0, -2), "BAIX": (0, +2)}
        for i, m in enumerate(movs.values()):
            coords = [sum(tup) for tup in zip(self.__posicioAg[self.__nom], m)]
            coord = {self.__nom: coords}
            cost = self.__pes + COST_BOTAR
            actual = Estat(self.__posPizza, coord, self.__parets,self.__nom, cost,
                           (self, (AccionsRana.BOTAR, Direccio.__getitem__(claus[i]))))
            if (actual.es_valid()):
                fills.append(actual)
        return fills

"""
CLASSE RANA:
ATRIBUTS:
    ·Classe:   1. P:       nombre invidividus població inicial
               2. solucio: boolean que determina si s'ha trobat la solució

    ·Objecte:  1. self.__accions: array per anar emmagatzemant les accions a realitzar
                                  obtingudes en el mètode cerca.
               2. self.__jumping: enter que pot agafar els valors dins el rang [0,2]. 
                                  Indica els torns d'espera al botar.
               3. self.__oberts:  array per emmagatzemar els estats encara oberts a explorar.
               4. self.__closed:  array per emmagatzemar els estats ja vists per no tornar a explorar-los.
MÈTODES:
    ·Classe: no hi ha mètode de classe.

    ·Objecte:  1. __init__:  constructor que s'hereda de joc.Rana.
               2. __pinta__: mètode que s'hereda.
               3. _cerca:    algoritme de cerca en amplada per a trobar la solució.
               4.  actua:    mètode per anar retornant les diferents accions que ha de fer l'agent.

"""
class Rana(joc.Rana):

    def __init__(self, *args, **kwargs):
        super(Rana, self).__init__(*args, **kwargs)
        self.__closed = None
        self.__oberts = None
        self.__accions = None
        self.__jumping = 0

    def pinta(self, display):
        pass
    """
    Mètode de cerca en amplada que que s'encarrega d'anar iterant i extreure l'element primer introduït.
    Es van generant fills de manera vàlida fins que es trobi una solucio.
    """
    def _cerca(self, estat: Estat):
        self.__oberts = []    #array per guardar estats
        self.__closed = set() #conjunt no ordenat d'elements que guarda els estats ja explorats

        self.__oberts.append(estat) #afegim estat inicial a oberts
        actual = None

        """
        Mentre quedin elements per recórrer o no es trobi solució.
        """
        while len(self.__oberts)>0:
            # si un retorn no t'interessa li posam _
            actual = self.__oberts[0]
            self.__oberts=self.__oberts[1:]

            if actual in self.__closed:#si estat ja explorat continua
                continue

            if not actual.es_valid():
                self.__closed.append(actual)
                continue

            estats_fills = actual.generaFills()

            if actual.es_meta():
                break

            for estat_f in estats_fills:
                self.__oberts.append(estat_f)

            self.__closed.add(actual)

        if actual is None:#gestió d'errors
            raise ValueError("Error impossible")

        if actual.es_meta():
            accions = []
            iterador = actual

            #iteram des de l'estat solució fins l'arrel de l'arbre per trobar el cami d'accions a realitzar
            while iterador.pare is not None:
                pare, accio = iterador.pare
                accions.append(accio)
                iterador = pare
            self.__accions = accions

    """
    Mètode actua que primerament crida a cerca si no té les accions definides en l'atribut self.__accions.
    Després va extreguent les operacions a realitzar una per una. Si es tracta d'un bot, assigna dos torns d'espera.
    """
    def actua(
            self, percep: entorn.Percepcio
    ) -> entorn.Accio | tuple[entorn.Accio, object]:
        estat = Estat(percep[ClauPercepcio.OLOR],percep[ClauPercepcio.POSICIO],percep[ClauPercepcio.PARETS],self.nom)

        if self.__accions is None:
            self._cerca(estat=estat)

        if self.__accions:
            if(self.__jumping>0): #esta botant
                self.__jumping-=1
                return AccionsRana.ESPERAR
            else:
                acc = self.__accions.pop()
                if(acc[0]==AccionsRana.BOTAR):
                    self.__jumping=2
                return acc[0],acc[1]
        else:
            return AccionsRana.ESPERAR