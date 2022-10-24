""" Mòdul que conté l'agent per jugar al joc de les monedes.

Percepcions:
    ClauPercepcio.MONEDES
Solució:
    " XXXC"
"""
import queue

from ia_2022 import agent, entorn
from monedes.entorn import AccionsMoneda

# CONSTANTS
COST_DESPLAÇAMENT = 1
COST_BOTAR = 2
COST_GIRAR = 2
SOLUCIO = " XXXC"


class AgentMoneda(agent.Agent):
    def __init__(self):
        super().__init__(long_memoria=0)
        self.__oberts = None
        self.__tancats = None
        self.__accions = None

    def pinta(self, display):
        print(self._posicio_pintar)

    def _cerca(self, estat):
        self.__oberts = queue.PriorityQueue()
        self.__tancats = set()

        self.__oberts.queue.append(estat)

        actual = None
        while len(self.__oberts.queue) > 0:
            actual = self.__oberts.queue.pop()
            if actual in self.__tancats:
                continue

            self.__tancats.add(actual)

            estats_fills = actual.generaFill()

            if actual.es_meta():
                break

            for estat_f in estats_fills:
                self.__oberts.queue.append(estat_f)

            self.__tancats.add(actual)
        if actual is None:
            raise ValueError("Error impossible")

        if actual.es_meta():
            accions = []
            iterador = actual

            while iterador.pare is not None:
                pare, accio = iterador.pare

                accions.append(accio)
                iterador = pare
            self.__accions = accions
            return True
        else:
            return False

    def actua(self, percep: entorn.Percepcio) -> entorn.Accio | tuple[entorn.Accio, object]:
        estat = Estat(percep.to_dict())

        if self.__accions is None:
            self._cerca(estat=estat)

        if len(self.__accions) > 0:
            return self.__accions.pop()
        else:
            return AccionsMoneda.RES


class Estat:
    def __init__(self, info, pes=0, pare=None):
        if info is None:
            self.info = "C CCX"
        else:
            self.__info = info

        self.__pare = pare
        self.__pes = pes

    def getHeuristica(self):
        i = 0
        heuristica = 0

        for i in range(self.__info):
            if self.__info[i] == ' ':
                heuristica += i
            else:
                if self.__info[i] != SOLUCIO[i]:
                    heuristica += 1
        # Heuristica de A*
        return heuristica + self.__pes

    def generaFill(self) -> list:
        """ Mètode per generar els estats fills.

            Genera tots els estats fill a partir de l'estat actual.

                Returns:
                    Llista d'estats fills generats.
        """
        estats_generats = []
        # cercam l'index del caracter en blanc
        a = ""
        index_blanc = 0
        while self.__info[index_blanc] != ' ':
            index_blanc += 1
        #index_blanc = self.__info.find(' ')
        # indexos
        posEsq = index_blanc
        posDreta = len(self.__info - index_blanc)

        # desplaçaments cap al blanc

        # Cas 1: Desplaçar monedes
        if posEsq > 0:
            llista = [*self.getEstat()]  # string to list
            # swap
            llista[index_blanc] = self.getEstat()[index_blanc - 1]
            llista[index_blanc - 1] = ' '
            # final swap
            llista = ''.join(map(str, llista))  # llista to str
            estats_generats.append(Estat(str, self.getHeuristica() + COST_DESPLAÇAMENT, self))

        if posDreta > 0:
            llista = [*self.getEstat()]  # string to list
            # swap
            llista[index_blanc] = self.getEstat()[index_blanc - 1]
            llista[index_blanc + 1] = ' '
            # final swap
            llista = ''.join(map(str, llista))  # llista to str

            estats_generats.append(Estat(llista, self.__pes + COST_DESPLAÇAMENT, self))

        # Cas 2: Girar monedes
        for i in range(len(self.__info)):
            if self.__info[i] == 'X':
                llista = [*self.getEstat()]  # string to list
                # llista[i]='C'
                # llista = ''.join(map(str, str))  # llista to str
                llista = self.setChar(llista, i, 'C')
            elif self.__info[i] == 'C':
                llista = [*self.getEstat()]  # string to list
                # llista= self.setChar(str, i, 'X')
                # llista[i] = 'X'
                # llista = ''.join(map(str, llista))  # llista to str
                llista = self.setChar(llista, i, 'X')
            estats_generats.append(Estat(llista, self.__pes + COST_GIRAR, self))

        # Cas 3 botar monedes

        if (posEsq > 1):
            llista = [*self.getEstat()]
            llista = self.swap(llista, index_blanc, index_blanc - 2)
            if (llista[index_blanc] == 'X'):
                llista = self.setChar(llista, index_blanc, 'C')
            else:
                llista = self.setChar(llista, index_blanc, 'X')
            estats_generats.append(Estat(llista, self.__pes + COST_BOTAR, self))
        if (posDreta > 1):
            llista = [*self.getEstat()]
            llista = self.swap(llista, index_blanc, index_blanc + 2)
            if (llista[index_blanc] == 'X'):
                llista = self.setChar(llista, index_blanc, 'C')
            else:
                llista = self.setChar(llista, index_blanc, 'X')
            estats_generats.append(Estat(llista, self.__pes + COST_BOTAR, self))

        return estats_generats

    def getEstat(self):
        return self.__info

    def getChar(self, index):
        return self.__info[index]

    def es_meta(self):
        return self.__info == " XXXC"

    def setChar(self, llista, pos, value):
        llista[pos] = value
        return ''.join(map(str, llista))

    def swap(self, llista, index1, index2):
        aux = llista[index1]
        llista[index1] = llista[index2]
        llista[index2] = aux

        return llista

    def __hash__(self):
        return hash(tuple(self.__info.items()))
