from json import JSONEncoder

class Transaction():

    def __init__(
        self,
        id,
        rekeningnummer, 
        muntsoort, 
        transactiedatum,
        rentedatum,
        beginsaldo,
        eindsaldo,
        transactiebedrag,
        omschrijving 
    ):
        self.id = id,
        self.rekeningnummer = rekeningnummer
        self.muntsoort = muntsoort
        self.transactiedatum = transactiedatum
        self.rentedatum = rentedatum
        self.beginsaldo = beginsaldo
        self.eindsaldo = eindsaldo
        self.transactiebedrag = transactiebedrag
        self.total_omschrijving = omschrijving
    
    def serialize(self):
        return {
            'id': self.id[0],
            'rekeningnummer': self.rekeningnummer,
            'muntsoort': self.muntsoort,
            'transactiedatum': self.transactiedatum,
            'rentedatum': self.rentedatum,
            'beginsaldo': self.beginsaldo,
            'eindsaldo': self.eindsaldo,
            'transactiebedrag': self.transactiebedrag,
            # 'receiver_rekeningnummer': self.receiver_rekeningnummer,
            # 'receiver_bic': self.receiver_bic,
            # 'receiver_naam': self.receiver_naam,
            'afschrijving': self.afschrijving,
            # 'kenmerk': self.kenmerk,
            # 'omschrijving': self.omschrijving,
        }
    
    @property
    def afschrijving(self):
        return float(self.beginsaldo) - float(self.eindsaldo) > 0
    
    @property
    def receiver_rekeningnummer(self):
        try:
            return self.total_omschrijving.split("IBAN: ")[1].split(" BIC")[0]
        except IndexError:
            return None 

    @property
    def receiver_bic(self):
        try:
            return self.total_omschrijving.split("BIC: ")[1].split(" Naam")[0]
        except IndexError:
            return None 
    
    @property
    def receiver_naam(self):
        try:
            return self.total_omschrijving.split("Naam: ")[1].split(" Omschrijving")[0]
        except IndexError:
            return None 

    @property
    def omschrijving(self):
        return self.total_omschrijving.split("Omschrijving:")[1].split(" Kenmerk")[0]

    @property
    def kenmerk(self):
        return self.total_omschrijving.split("Kenmerk:")[1]

    def __str__(self):
        return str(self.transactiebedrag)