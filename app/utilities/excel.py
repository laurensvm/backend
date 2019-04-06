import os
import pandas as pd
import numpy as np

import uuid
import time

from app import app

from ..models import Transaction

FILE = os.path.join(os.path.dirname(app.root_path), "static/rekeningen.xls")

def extract_excel_contents():
    df = pd.read_excel(FILE)
    objects = []
    for row in df.itertuples(index=True):
        obj = Transaction(
            id=uuid.uuid1(),
            rekeningnummer=getattr(row, "Rekeningnummer"),
            muntsoort=getattr(row, "Muntsoort"),
            transactiedatum=getattr(row, "Transactiedatum"),
            rentedatum=getattr(row, "Rentedatum"),
            beginsaldo=getattr(row, "Beginsaldo"),
            eindsaldo=getattr(row, "Eindsaldo"),
            transactiebedrag=getattr(row, "Transactiebedrag"),
            omschrijving=getattr(row, "Omschrijving")
        )
        objects.append(obj)
    return objects