import 'package:flutter_tts/flutter_tts.dart';

class TtsService {
  final FlutterTts _tts = FlutterTts();
  bool _isInitialized = false;

  Future<void> init() async {
    if (_isInitialized) return;

    await _tts.setLanguage('fr-FR');
    await _tts.setSpeechRate(0.5);
    await _tts.setVolume(1.0);
    await _tts.setPitch(1.0);

    _isInitialized = true;
  }

  Future<void> speak(String text) async {
    if (!_isInitialized) {
      await init();
    }
    await _tts.speak(text);
  }

  Future<void> speakPlayingMusic(String titre, String artiste) async {
    await speak('Lecture de $titre par $artiste');
  }

  Future<void> speakError(String message) async {
    await speak(message);
  }

  Future<void> speakNoMusicFound(String query) async {
    await speak("Je n'ai pas trouvé de musique correspondant à $query");
  }

  Future<void> speakCommandUnderstood(String intent) async {
    switch (intent) {
      case 'PLAY':
        // Will be followed by speakPlayingMusic
        break;
      case 'STOP':
        await speak('Arrêt de la musique');
        break;
      case 'PAUSE':
        await speak('Pause');
        break;
      case 'RESUME':
        await speak('Reprise');
        break;
      case 'NEXT':
        await speak('Piste suivante');
        break;
      case 'PREVIOUS':
        await speak('Piste précédente');
        break;
      default:
        await speak("Je n'ai pas compris");
    }
  }

  Future<void> stop() async {
    await _tts.stop();
  }

  Future<void> dispose() async {
    await _tts.stop();
  }
}
