import datetime
from datetime import timedelta
import pytz

# Timezone Paris
paris_tz = pytz.timezone("Europe/Paris")

# Dates clés calculées au chargement
now = datetime.datetime.now(paris_tz)
aujourdhui = now.date()
demain = aujourdhui + timedelta(days=1)
apres_demain = aujourdhui + timedelta(days=2)
hier = aujourdhui + timedelta(days=-1)
avanthier = aujourdhui + timedelta(days=-2)

# Heures pratiques
midi = "12:00"
minuit = "00:00"
fiftynine = "23:59"


