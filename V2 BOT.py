import requests 
import os 
import json 
import datetime as dt 
import pywhatkit as kit 

class BotJoursBlancs:
    def __init__(self, id_groupe, jours_avant_rappel=2):
        self.id_groupe = id_groupe
        self.jours_avant = jours_avant_rappel
        self.fichier_sauvegarde = 'historique_envois.json'
        self.historique = self._charger_historique()

    def _charger_historique(self):
        if os.path.exists(self.fichier_sauvegarde) and os.path.getsize(self.fichier_sauvegarde) > 0:
            with open(self.fichier_sauvegarde, 'r') as f:
                return json.load(f)
        return []

    def _sauvegarder_historique(self):
        with open(self.fichier_sauvegarde, 'w') as f:
            json.dump(self.historique, f)

    def generer_matrice(self, mois_limite=3):
        matrice = []
        ajd = dt.datetime.now()
        mois, annee = ajd.month, ajd.year
        
        for i in range(mois_limite):
            url = f"https://api.aladhan.com/v1/gToHCalendar/{mois}/{annee}"
            reponse = requests.get(url)
            
            if reponse.status_code == 200:
                calendrier = reponse.json()
                jblancs = []
                for item in calendrier['data']:
                    if item['hijri']['day'] in ['13', '14', '15']:
                        jblancs.append(item['gregorian']['date'])
                        mois_hijri = item['hijri']['month']['en']
                        if len(jblancs) == 3:
                            matrice.append({"mois_hijri": mois_hijri, "dates": jblancs})
                            jblancs = []
            mois += 1
            if mois > 12:
                mois = 1
                annee += 1
        return matrice

    def envoyer_message(self, message):
        print("Préparation de l'envoi...")
        try:
            kit.sendwhatmsg_to_group_instantly(
                group_id=self.id_groupe,
                message=message, 
                wait_time=15, tab_close=True, close_time=3
            )
            print("Message envoyé !")
        except Exception as e:
            print(f"Erreur : {e}")

    def verifier_et_lancer(self):
        matrice = self.generer_matrice()
        ajd = dt.datetime.now()

        for periode in matrice:
            premier_jour_obj = dt.datetime.strptime(periode["dates"][0], "%d-%m-%Y")
            date_envoi = premier_jour_obj - dt.timedelta(days=self.jours_avant)
            
            if premier_jour_obj < ajd:
                continue
                
            if ajd.date() == date_envoi.date():
                identifiant = f"{periode['mois_hijri']}-{periode['dates'][0]}"
                
                if identifiant in self.historique:
                    print("Déjà envoyé pour ce mois.")
                    return
                
                if periode['mois_hijri'] == "Ramadan":
                    print("C'est Ramadan: pas de message.")
                else:
                    message = f"Assalamu alaykum, rappel des jours blancs : {periode['dates']}"
                    self.envoyer_message(message)
                
                self.historique.append(identifiant)
                self._sauvegarder_historique()
                return

if __name__ == "__main__":
    mon_bot = BotJoursBlancs(id_groupe="ENTRER_ID_GROUPE", jours_avant_rappel=2)
    mon_bot.verifier_et_lancer()