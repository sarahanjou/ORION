/// Configuration de l'application Orion
class AppConfig {
  // Configuration Backend
  // En démo, on peut utiliser un token LiveKit statique pour éviter de passer par le serveur.
  // Mettre useStaticToken à false pour revenir au comportement normal (appel HTTP au serveur).
  static const bool useStaticToken = true;

  // Token statique pour la démo (généré par le serveur Render)
  // TODO: Retirer ce token hardcodé et utiliser uniquement l'appel serveur
  static const String staticToken =
      "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoibW9iaWxlLWFwcCIsInZpZGVvIjp7InJvb21Kb2luIjp0cnVlLCJyb29tIjoibXktcm9vbSIsImNhblB1Ymxpc2giOnRydWUsImNhblN1YnNjcmliZSI6dHJ1ZSwiY2FuUHVibGlzaERhdGEiOnRydWV9LCJzdWIiOiJpZGVudGl0eSIsImlzcyI6IkFQSTU0M0ROOGtURjV3bSIsIm5iZiI6MTc2ODU5MDM4OSwiZXhwIjoxNzY4NjExOTg5fQ.tBK9RypF4b_407XFEs_xrFYIViUwQUe-eJrSyobe0mE";

  // URL du serveur distant (utilisé uniquement si useStaticToken == false)
  static const String serverUrl = "https://server-render-0rab.onrender.com/getToken";
  static const String livekitUrl = "wss://orion-aqpqwzx7.livekit.cloud";
  
  // Nom de la room par défaut
  static const String defaultRoomName = "my-room";
}
