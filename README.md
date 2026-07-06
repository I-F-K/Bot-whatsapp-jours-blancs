# Bot Rappel Jours Blancs (Ayyam al-Bid) — WhatsApp

Petit script Python qui envoie automatiquement un message de rappel sur un groupe WhatsApp avant chaque période des **jours blancs** (Ayyam al-Bid : les 13, 14 et 15 de chaque mois du calendrier hijri), pour ne plus les oublier entre amis.

## Fonctionnement

1. **Calcul des dates** : le script interroge l'API [Aladhan](https://aladhan.com/islamic-calendar-api) pour convertir le calendrier grégorien en hijri sur les prochains mois, et repère les groupes de 3 jours consécutifs correspondant aux jours 13-14-15 du mois hijri.
2. **Déclenchement** : lancé une fois par jour (via une tâche planifiée, cf. plus bas), il vérifie si la date du jour correspond exactement à *N jours avant* le début de la prochaine période (`jours_avant_rappel`, 2 par défaut).
3. **Envoi** : si c'est le bon jour, un message est envoyé sur le groupe WhatsApp via [`pywhatkit`](https://github.com/Ankit404butfound/PyWhatKit), qui pilote WhatsApp Web depuis le navigateur.
4. **Anti-doublon** : chaque envoi est enregistré dans `historique_envois.json` (créé automatiquement) pour ne jamais envoyer deux fois le rappel de la même période.
5. **Cas particulier Ramadan** : pendant le mois de Ramadan, le jeûne quotidien rend le rappel inutile — le script détecte ce mois et n'envoie rien.

## Prérequis

- Python 3.8+
- Un navigateur avec **WhatsApp Web déjà connecté** (pywhatkit ouvre un onglet et s'appuie sur la session active)
- L'identifiant du groupe WhatsApp cible (`id_groupe`) — récupérable depuis le lien d'invitation du groupe

## Installation

```bash
pip install requests pywhatkit
```

## Configuration

Dans le bloc `if __name__ == "__main__":` en bas du script, renseigner :

```python
mon_bot = BotJoursBlancs(id_groupe="ENTRER_ID_GROUPE", jours_avant_rappel=2)
```

- `id_groupe` : identifiant du groupe WhatsApp (obligatoire)
- `jours_avant_rappel` : nombre de jours avant le début de la période pour envoyer le rappel (2 par défaut)

## Utilisation

Lancement manuel :
```bash
python bot_jours_blancs.py
```

Pour un envoi vraiment automatique, il faut planifier l'exécution **une fois par jour** (le script lui-même ne boucle pas en continu) :

- **Linux/Mac** : une tâche cron (`crontab -e`)
  ```
  0 9 * * * /usr/bin/python3 /chemin/vers/bot_jours_blancs.py
  ```
- **Windows** : le Planificateur de tâches (Task Scheduler), une tâche quotidienne pointant vers le script

## Limites connues

- `pywhatkit` pilote un vrai onglet de navigateur (WhatsApp Web) : la machine doit être allumée, connectée à internet, avec une session WhatsApp Web active au moment de l'exécution planifiée — ça ne fonctionne pas en pur arrière-plan headless sans session ouverte.
- L'API Aladhan peut occasionnellement être indisponible ou renvoyer un code d'erreur ; le script ignore silencieusement le mois concerné dans ce cas (pas de retry).
- Le fichier `historique_envois.json` est local : si le script tourne sur plusieurs machines ou est réinitialisé, l'historique des envois est perdu et un doublon est possible.
