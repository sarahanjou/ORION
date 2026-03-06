import datetime
from datetime import timedelta
import pytz

# Timezone Paris
paris_tz = pytz.timezone("Europe/Paris")


def _now():
    return datetime.datetime.now(paris_tz)


def aujourdhui():
    return _now().date()


def demain():
    return aujourdhui() + timedelta(days=1)


def apres_demain():
    return aujourdhui() + timedelta(days=2)


def hier():
    return aujourdhui() + timedelta(days=-1)


def avanthier():
    return aujourdhui() + timedelta(days=-2)


# Heures pratiques
midi = "12:00"
minuit = "00:00"
fiftynine = "23:59"
