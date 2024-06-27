import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
from itertools import combinations
from IPython.display import display, HTML

class TBTFEuro:
    def __init__(self):
        self.Grupper = {
            'Gruppe A': ['Tyskland', 'Skotland', 'Ungarn', 'Schweiz'],
            'Gruppe B': ['Spanien', 'Kroatien', 'Italien', 'Albanien'],
            'Gruppe C': ['Slovenien', 'Danmark', 'Serbien', 'England'],
            'Gruppe D': ['Polen', 'Holland', 'Østrig', 'Frankrig'],
            'Gruppe E': ['Belgien', 'Slovakiet', 'Rumænien', 'Ukraine'],
            'Gruppe F': ['Tyrkiet', 'Georgien', 'Portugal', 'Tjekkiet']
        }

        self.GrupperKort = {
            'Skotland': {'Gule kort': 5, 'Røde kort': 1},
            'Belgien': {'Gule kort': 5, 'Røde kort': 0},
            'England': {'Gule kort': 4, 'Røde kort': 0},
            'Frankrig': {'Gule kort': 3, 'Røde kort': 0},
            'Ukraine': {'Gule kort': 3, 'Røde kort': 0},
            'Holland': {'Gule kort': 2, 'Røde kort': 0},
            'Slovakiet': {'Gule kort': 2, 'Røde kort': 0},
            'Rumænien': {'Gule kort': 7, 'Røde kort': 0},
            'Italien': {'Gule kort': 7, 'Røde kort': 0},
            'Portugal': {'Gule kort': 7, 'Røde kort': 0},
            'Albanien': {'Gule kort': 7, 'Røde kort': 0},
            'Slovenien': {'Gule kort': 7, 'Røde kort': 0},
            'Danmark': {'Gule kort': 6, 'Røde kort': 0},
            'Georgien': {'Gule kort': 6, 'Røde kort': 0},
            'Spanien': {'Gule kort': 5, 'Røde kort': 0},
            'Tyskland': {'Gule kort': 5, 'Røde kort': 0},
            'Tyrkiet': {'Gule kort': 16, 'Røde kort': 0},
            'Tjekkiet': {'Gule kort': 13, 'Røde kort': 2},
            'Østrig': {'Gule kort': 10, 'Røde kort': 0},
            'Ungarn': {'Gule kort': 10, 'Røde kort': 0},
            'Serbien': {'Gule kort': 9, 'Røde kort': 0},
            'Polen': {'Gule kort': 8, 'Røde kort': 0},
            'Schweiz': {'Gule kort': 8, 'Røde kort': 0},
            'Kroatien': {'Gule kort': 7, 'Røde kort': 0}
        }

        self._ImporterGrupperResultater()
        self._BeregnGrupperStilling()
        self._ImporterBud()
        self._BeregnGrupperBois()

    def _ImporterGrupperResultater(self):
        # Importerer resultater fra gruppespillet
        ResultatFil = 'Resultater.xlsx' # Definerer resultatfil

        self.GrupperResultater = pd.read_excel( # Indlæser resultatfil
            ResultatFil,
            header=None,
            names=['Hold 1', 'Hold 2', 'Mål 1', 'Mål 2']
        ).dropna()
        self.GrupperResultater[['Mål 1', 'Mål 2']] = self.GrupperResultater[['Mål 1', 'Mål 2']].astype(int) # Konverterer 'Mål' til int

        self.GrupperResultater = self.GrupperResultater.to_dict(orient='records') # Konverterer til dict

    def _BeregnGrupperStilling(self):
        # Beregner faktisk stilling i gruppespillet
        self.StillingSamlet = {} # Definerer tom dict til samlet stilling
        self.StillingGrupper = {} # Definerer tom dict til gruppestillinger
        self.StillingTredjepladser = {} # Definerer tom dict til tredjepladser

        for gruppe, lande in self.Grupper.items(): # Fylder dict med variable for hvert land
            for land in lande:
                self.StillingSamlet[land] = {
                    'Point': 0, 
                    'Mål for': 0, 
                    'Mål imod': 0, 
                    'Målforskel': 0,
                    'Kort': 0
                }
        
        for resultat in self.GrupperResultater: # Beregner point fra faktiske resultater
            if resultat['Mål 1'] > resultat['Mål 2']: # Hold 1 vinder
                self.StillingSamlet[resultat['Hold 1']]['Point'] += 3
            if resultat['Mål 1'] < resultat['Mål 2']: # Hold 2 vinder
                self.StillingSamlet[resultat['Hold 2']]['Point'] += 3
            if resultat['Mål 1'] == resultat['Mål 2']: # Uafgjort
                self.StillingSamlet[resultat['Hold 1']]['Point'] += 1
                self.StillingSamlet[resultat['Hold 2']]['Point'] += 1
            
            self.StillingSamlet[resultat['Hold 1']]['Mål for'] += resultat['Mål 1'] # Beregner mål for og imod
            self.StillingSamlet[resultat['Hold 1']]['Mål imod'] += resultat['Mål 2']
            self.StillingSamlet[resultat['Hold 2']]['Mål for'] += resultat['Mål 2']
            self.StillingSamlet[resultat['Hold 2']]['Mål imod'] += resultat['Mål 1']

        for land, værdier in self.StillingSamlet.items(): # Beregner målforskel og disciplin
            værdier['Målforskel'] = værdier['Mål for'] - værdier['Mål imod']
            værdier['Kort'] = self.GrupperKort[land]['Gule kort'] + self.GrupperKort[land]['Røde kort']
            
        for gruppe, lande in self.Grupper.items():
            dict = {land: self.StillingSamlet[land] for land in lande}
            df = pd.DataFrame.from_dict(dict, orient='index')

            self.StillingGrupper[gruppe] = df.sort_values(
                by=['Point', 'Målforskel', 'Mål for', 'Kort'], 
                ascending=[False, False, False, True]
            )

            TredjeRække = self.StillingGrupper[gruppe].iloc[[2]]
            TredjeLand = TredjeRække.index[0]
            self.StillingTredjepladser[TredjeLand] = TredjeRække.to_dict(orient='index')[TredjeLand]

            self.StillingGrupper[gruppe] = self.StillingGrupper[gruppe].drop('Kort', axis='columns')
        
        self.StillingTredjepladser = pd.DataFrame.from_dict(self.StillingTredjepladser, orient='index').sort_values(
            by=['Point', 'Målforskel', 'Mål for', 'Kort'], ascending=[False, False, False, True]).drop('Kort', axis='columns')
            
    def _VisGrupperStilling(self):
        # Viser gruppestillinger
        def formattering(s, tredjepladser):
            formattering = []
            for idx in range(len(s)):
                if s.index[idx] in tredjepladser:
                    formattering.append('background-color: rgba(0, 209, 0, 0.12)') 
                elif idx < 1:
                    formattering.append('background-color: rgba(0, 209, 0, 0.5)') 
                elif 0 < idx < 2:
                    formattering.append('background-color: rgba(0, 209, 0, 0.25)') 
                else:
                    formattering.append('')
            return formattering

        tredjepladser = self.StillingTredjepladser.index[:4].tolist()

        html = "<div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px;'>"
        for gruppe, df in self.StillingGrupper.items():
            styled_df = df.style.apply(formattering, axis=0, tredjepladser=tredjepladser).set_table_attributes('style="display:inline;margin:5px;"').set_caption(gruppe)
            html += styled_df._repr_html_()
        html += "</div>"

        html += "<div style='text-align:center; margin-top: 20px;'>"
        styled_third_place_df = self.StillingTredjepladser.style.apply(formattering, axis=0, tredjepladser=tredjepladser).set_table_attributes('style="display:inline;margin:5px;"').set_caption('Bedste 3\'ere')
        html += styled_third_place_df._repr_html_()
        html += "</div>"

        display(HTML(html))

    def _ImporterBud(self):
        # Importer bois bud på gruppespillet
        BudFil = 'Bud.xlsx'

        self.GrupperBud = pd.read_excel(
            BudFil,
            sheet_name=None,
            header=None,
            names=['Hold 1', 'Hold 2', 'Mål 1', 'Mål 2']
        )
    
        for boi, ark in self.GrupperBud.items():
            ark = ark.dropna()
            ark[['Mål 1', 'Mål 2']] = ark[['Mål 1', 'Mål 2']].astype(int)
            ark = ark.to_dict(orient='records')
            self.GrupperBud[boi] = ark

    def _BeregnGrupperBois(self):
        # Beregner point i gruppespillet for bois' bud
        self.GrupperBoisPoint = {boi: [] for boi in self.GrupperBud.keys()}

        for boi in self.GrupperBud.keys():
            for kamp, værdi in enumerate(self.GrupperBud[boi]):
                if kamp < len(self.GrupperResultater): # Tjekker kun bud så længe der er resultater
                    bHold1 = værdi['Hold 1'] # Definerer hold i bud
                    bHold2 = værdi['Hold 2']

                    Hold1 = self.GrupperResultater[kamp]['Hold 1'] # Definerer hold i kamp
                    Hold2 = self.GrupperResultater[kamp]['Hold 2']

                    bMål1 = værdi['Mål 1'] # Definerer mål i bud
                    bMål2 = værdi['Mål 2']

                    Mål1 = self.GrupperResultater[kamp]['Mål 1'] # Definerer mål i kamp
                    Mål2 = self.GrupperResultater[kamp]['Mål 2']

                    if bMål1 > bMål2: # Definerer vinder i bud
                        bVinder = bHold1
                    elif bMål1 < bMål2:
                        bVinder = bHold2
                    else:
                        bVinder = 'Uafgjort'

                    if Mål1 > Mål2: # Definerer vinder i kamp
                        Vinder = Hold1
                    elif Mål1 < Mål2:
                        Vinder = Hold2
                    else:
                        Vinder = 'Uafgjort'

                    if [bHold1, bHold2] == [Hold1, Hold2]: # Tjekker at kamp og bud er på samme hold
                        if [bMål1, bMål2] == [Mål1, Mål2]: # Regel 1: Resultat og begge målscorer
                            bPoint = 7
                        elif (bMål1 == Mål1 or bMål2 == Mål2) and bVinder == Vinder: # Regel 2: Resultat og én målscore
                            bPoint = 4
                        elif bVinder == Vinder: # Regel 3: Resultat
                            bPoint = 3
                        elif bMål1 == Mål1 or bMål2 == Mål2: # Regel 4: Én målscore
                            bPoint = 1
                        else:
                            bPoint = 0
                    else:
                        bPoint = np.nan
                    
                    self.GrupperBoisPoint[boi].append(bPoint)

        # Beregner samlet stilling for bois
        PointSum = {boi: sum(filter(lambda x: x == x, bPoint)) for boi, bPoint in self.GrupperBoisPoint.items()}

        self.BoisStilling = pd.DataFrame(list(PointSum.items()), columns=['Boi', 'Point'])
        self.BoisStilling = self.BoisStilling.sort_values(by='Point', ascending=False).reset_index(drop=True)

    def _VisBoisStilling(self):
        # Viser bois stilling
        html = f"""
        <div style="display: flex; justify-content: center;">
            {self.BoisStilling.to_html(index=False)}
        </div>
        """
        display(HTML(html))