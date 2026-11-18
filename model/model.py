from database.distributore_DAO import DistributoreDAO

'''
    MODELLO:
- Rappresenta la struttura dati
- Si occupa di gestire lo stato dell'applicazione
- Interagisce con il database
'''


class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese: int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        risultato = []
        for distributore in self._distributori:
            prezzi = distributore.get_prezzi()

            # Filtro i prezzi per il mese richiesto usando le proprietà date di python
            prezzi_mese = [p.prezzo_litro for p in prezzi if p.data.month == mese]

            if len(prezzi_mese) > 0:
                media = sum(prezzi_mese) / len(prezzi_mese)
                risultato.append((distributore.nome, media))

        return risultato

    def get_sequenza_ottima(self, mese: int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in
                         enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione seguendo lo schema delle slide """

        # 🟢 A - Terminal Condition: abbiamo pianificato tutti e 7 i giorni
        if giorno > 7:
            # Se è la prima soluzione valida, o se ho trovato un costo inferiore a quello ottimo salvato
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                # FONDAMENTALE: creare una copia della lista per evitare problemi coi reference in Python
                self.__sequenza_ottima = list(sequenza_parziale)
            return

        # Ciclo tra le opzioni disponibili (Distributore A o B)
        for distributore in self._distributori:
            id_dist = distributore.id

            # 🔵 B - Compute Partial: calcolo quanto mi costa questa specifica tappa
            prezzo_al_litro = prezzi_settimana[id_dist][giorno - 1]
            costo_carburante = prezzo_al_litro * 100

            # Se è il primo giorno (ultimo_dist = None) o non cambio distributore, il costo spostamento è 0
            costo_spostamento = 0
            if ultimo_distributore is not None and ultimo_distributore != id_dist:
                costo_spostamento = 5

            nuovo_costo_parziale = costo_corrente + costo_carburante + costo_spostamento

            # 🟡 C - Filter: Taglio l'albero di ricorsione se sto già spendendo di più del costo ottimo trovato
            if self.__costo_ottimo == -1 or nuovo_costo_parziale < self.__costo_ottimo:
                # Aggiungo alla sequenza
                sequenza_parziale.append(id_dist)

                # Passo al giorno successivo
                self.__ricorsione(sequenza_parziale, giorno + 1, id_dist, nuovo_costo_parziale, prezzi_settimana)

                # 🟣 D - Back-tracking: rimuovo l'ultima scelta per valutare le altre
                sequenza_parziale.pop()

    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        prezzi_settimana = {}
        for distributore in self._distributori:
            prezzi = distributore.get_prezzi()

            # Filtro per mese e per i giorni che vanno da 1 a 7
            prezzi_filtrati = [p for p in prezzi if p.data.month == mese and 1 <= p.data.day <= 7]

            # Li ordino per giorno in modo da essere sicuro che l'indice della lista corrisponda ai giorni consecutivi
            prezzi_filtrati.sort(key=lambda p: p.data.day)

            # Estraggo solo il valore float del prezzo
            prezzi_settimana[distributore.id] = [p.prezzo_litro for p in prezzi_filtrati]

        return prezzi_settimana