import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/musique.dart';
import '../services/audio_recorder_service.dart';
import '../services/audio_player_service.dart';
import '../services/vocal_api_service.dart';
import '../services/tts_service.dart';

enum AppState { idle, listening, processing, playing, error }

class MusicProvider extends ChangeNotifier {
  // Services
  final AudioRecorderService _recorderService = AudioRecorderService();
  final AudioPlayerService _playerService = AudioPlayerService();
  final VocalApiService _vocalApiService = VocalApiService();
  final TtsService _ttsService = TtsService();

  // State
  AppState _state = AppState.idle;
  String? _errorMessage;
  String? _lastTranscript;
  String? _lastIntent;
  List<Musique> _musiques = [];
  Duration _position = Duration.zero;
  Duration _duration = Duration.zero;

  // Getters
  AppState get state => _state;
  String? get errorMessage => _errorMessage;
  String? get lastTranscript => _lastTranscript;
  String? get lastIntent => _lastIntent;
  List<Musique> get musiques => _musiques;
  Musique? get currentMusique => _playerService.currentMusique;
  bool get isPlaying => _state == AppState.playing;
  bool get isListening => _state == AppState.listening;
  bool get isProcessing => _state == AppState.processing;
  Duration get position => _position;
  Duration get duration => _duration;
  bool get hasNext => _playerService.hasNext;
  bool get hasPrevious => _playerService.hasPrevious;

  // Stream subscriptions
  StreamSubscription? _playerStateSubscription;
  StreamSubscription? _positionSubscription;
  StreamSubscription? _durationSubscription;

  MusicProvider() {
    _init();
  }

  Future<void> _init() async {
    await _ttsService.init();
    _setupPlayerListeners();
    await loadMusiques();
  }

  void _setupPlayerListeners() {
    _playerStateSubscription = _playerService.stateStream.listen((playerState) {
      if (playerState == PlayerState.playing) {
        _state = AppState.playing;
      } else if (playerState == PlayerState.paused ||
          playerState == PlayerState.stopped ||
          playerState == PlayerState.idle) {
        if (_state == AppState.playing) {
          _state = AppState.idle;
        }
      } else if (playerState == PlayerState.error) {
        _state = AppState.error;
        _errorMessage = 'Erreur de lecture';
      }
      notifyListeners();
    });

    _positionSubscription = _playerService.positionStream.listen((pos) {
      _position = pos;
      notifyListeners();
    });

    _durationSubscription = _playerService.durationStream.listen((dur) {
      _duration = dur ?? Duration.zero;
      notifyListeners();
    });
  }

  Future<void> loadMusiques() async {
    try {
      _musiques = await _vocalApiService.getAllMusiques();
      _playerService.setPlaylist(_musiques, startIndex: -1);
      notifyListeners();
    } catch (e) {
      debugPrint('Failed to load musiques: $e');
    }
  }

  Future<void> startListening() async {
    if (_state == AppState.listening) return;

    try {
      _errorMessage = null;
      _state = AppState.listening;
      notifyListeners();

      await _recorderService.startRecording();
    } catch (e) {
      _state = AppState.error;
      _errorMessage = e.toString();
      notifyListeners();
    }
  }

  Future<void> stopListeningAndProcess() async {
    if (_state != AppState.listening) return;

    try {
      _state = AppState.processing;
      notifyListeners();

      final audioPath = await _recorderService.stopRecording();
      if (audioPath == null) {
        throw Exception('No recording available');
      }

      final response = await _vocalApiService.recognizeAudio(audioPath);
      _lastTranscript = response.transcript;
      _lastIntent = response.intent;

      await _handleVocalResponse(response);
    } catch (e) {
      _state = AppState.error;
      _errorMessage = e.toString();
      await _ttsService.speakError("Une erreur s'est produite");
      notifyListeners();
    }
  }

  Future<void> cancelListening() async {
    await _recorderService.cancelRecording();
    _state = AppState.idle;
    notifyListeners();
  }

  Future<void> _handleVocalResponse(VocalApiResponse response) async {
    if (!response.success) {
      _state = AppState.error;
      _errorMessage = response.error ?? 'Unknown error';
      await _ttsService.speakError(_errorMessage!);
      notifyListeners();
      return;
    }

    switch (response.intent) {
      case 'PLAY':
        if (response.musique != null) {
          await _playMusique(response.musique!);
        } else {
          _state = AppState.error;
          _errorMessage = response.error ?? 'Musique non trouvée';
          await _ttsService.speakNoMusicFound(_lastTranscript ?? '');
        }
        break;

      case 'STOP':
        await stop();
        await _ttsService.speakCommandUnderstood('STOP');
        break;

      case 'PAUSE':
        await pause();
        await _ttsService.speakCommandUnderstood('PAUSE');
        break;

      case 'RESUME':
        await resume();
        await _ttsService.speakCommandUnderstood('RESUME');
        break;

      case 'NEXT':
        await next();
        await _ttsService.speakCommandUnderstood('NEXT');
        break;

      case 'PREVIOUS':
        await previous();
        await _ttsService.speakCommandUnderstood('PREVIOUS');
        break;

      default:
        _state = AppState.error;
        _errorMessage = "Commande non reconnue";
        await _ttsService.speakCommandUnderstood('UNKNOWN');
    }

    notifyListeners();
  }

  Future<void> _playMusique(Musique musique) async {
    try {
      // Find index in playlist
      final index = _musiques.indexWhere((m) => m.id == musique.id);
      if (index >= 0) {
        _playerService.setPlaylist(_musiques, startIndex: index);
      } else {
        await _playerService.play(musique);
      }

      await _ttsService.speakPlayingMusic(musique.titre, musique.artiste);
      _state = AppState.playing;
    } catch (e) {
      _state = AppState.error;
      _errorMessage = 'Erreur de lecture: ${e.toString()}';
      await _ttsService.speakError("Impossible de lire cette musique");
    }
    notifyListeners();
  }

  Future<void> playMusique(Musique musique) async {
    await _playMusique(musique);
  }

  Future<void> pause() async {
    await _playerService.pause();
    _state = AppState.idle;
    notifyListeners();
  }

  Future<void> resume() async {
    await _playerService.resume();
    _state = AppState.playing;
    notifyListeners();
  }

  Future<void> stop() async {
    await _playerService.stop();
    _state = AppState.idle;
    notifyListeners();
  }

  Future<void> next() async {
    if (_playerService.hasNext) {
      await _playerService.playNext();
      _state = AppState.playing;
      notifyListeners();
    }
  }

  Future<void> previous() async {
    await _playerService.playPrevious();
    _state = AppState.playing;
    notifyListeners();
  }

  Future<void> seek(Duration position) async {
    await _playerService.seek(position);
  }

  void clearError() {
    _errorMessage = null;
    _state = AppState.idle;
    notifyListeners();
  }

  @override
  void dispose() {
    _playerStateSubscription?.cancel();
    _positionSubscription?.cancel();
    _durationSubscription?.cancel();
    _recorderService.dispose();
    _playerService.dispose();
    _vocalApiService.dispose();
    _ttsService.dispose();
    super.dispose();
  }
}
