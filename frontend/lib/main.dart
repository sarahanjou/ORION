import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'pages/voice_page.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  // Rend la barre de statut transparente pour l'immersion
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.light,
  ));
  
  // Gestion des erreurs Flutter
  FlutterError.onError = (FlutterErrorDetails details) {
    FlutterError.presentError(details);
    debugPrint("Erreur Flutter: ${details.exception}");
    debugPrint("Stack: ${details.stack}");
  };
  
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Orion',
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: Colors.transparent, 
      ),
      home: const VoicePage(),
      debugShowCheckedModeBanner: false,
    );
  }
}