import 'dart:async';
import 'package:just_audio/just_audio.dart';
import '../models/musique.dart';

enum PlayerState { idle, loading, playing, paused, stopped, error }

class AudioPlayerService {
  final AudioPlayer _player = AudioPlayer();
  Musique? _currentMusique;
  List<Musique> _playlist = [];
  int _currentIndex = -1;

  // Stream controllers
  final _stateController = StreamController<PlayerState>.broadcast();
  final _positionController = StreamController<Duration>.broadcast();
  final _durationController = StreamController<Duration?>.broadcast();
  final _currentMusiqueController = StreamController<Musique?>.broadcast();

  // Getters
  Stream<PlayerState> get stateStream => _stateController.stream;
  Stream<Duration> get positionStream => _positionController.stream;
  Stream<Duration?> get durationStream => _durationController.stream;
  Stream<Musique?> get currentMusiqueStream => _currentMusiqueController.stream;

  Musique? get currentMusique => _currentMusique;
  List<Musique> get playlist => _playlist;
  int get currentIndex => _currentIndex;
  bool get hasNext => _currentIndex < _playlist.length - 1;
  bool get hasPrevious => _currentIndex > 0;

  AudioPlayerService() {
    _initStreams();
  }

  void _initStreams() {
    // Listen to player state changes
    _player.playerStateStream.listen((state) {
      if (state.processingState == ProcessingState.loading) {
        _stateController.add(PlayerState.loading);
      } else if (state.processingState == ProcessingState.ready) {
        if (state.playing) {
          _stateController.add(PlayerState.playing);
        } else {
          _stateController.add(PlayerState.paused);
        }
      } else if (state.processingState == ProcessingState.completed) {
        _stateController.add(PlayerState.stopped);
        // Auto-play next if available
        if (hasNext) {
          playNext();
        }
      } else if (state.processingState == ProcessingState.idle) {
        _stateController.add(PlayerState.idle);
      }
    });

    // Listen to position changes
    _player.positionStream.listen((position) {
      _positionController.add(position);
    });

    // Listen to duration changes
    _player.durationStream.listen((duration) {
      _durationController.add(duration);
    });
  }

  Future<void> play(Musique musique, {String? audioUrl}) async {
    try {
      _currentMusique = musique;
      _currentMusiqueController.add(musique);
      _stateController.add(PlayerState.loading);

      // For now, we'll use a placeholder audio URL
      // In production, this would come from the server or local assets
      final url = audioUrl ?? 'asset:///assets/musiques/${musique.fichierAudio}';

      await _player.setUrl(url);
      await _player.play();
    } catch (e) {
      _stateController.add(PlayerState.error);
      rethrow;
    }
  }

  Future<void> playFromPlaylist(int index) async {
    if (index >= 0 && index < _playlist.length) {
      _currentIndex = index;
      await play(_playlist[index]);
    }
  }

  void setPlaylist(List<Musique> musiques, {int startIndex = 0}) {
    _playlist = musiques;
    _currentIndex = startIndex;
    if (_playlist.isNotEmpty && startIndex < _playlist.length) {
      play(_playlist[startIndex]);
    }
  }

  Future<void> pause() async {
    await _player.pause();
  }

  Future<void> resume() async {
    await _player.play();
  }

  Future<void> stop() async {
    await _player.stop();
    _currentMusique = null;
    _currentMusiqueController.add(null);
    _stateController.add(PlayerState.stopped);
  }

  Future<void> playNext() async {
    if (hasNext) {
      _currentIndex++;
      await play(_playlist[_currentIndex]);
    }
  }

  Future<void> playPrevious() async {
    // If more than 3 seconds in, restart current track
    if (_player.position.inSeconds > 3) {
      await seek(Duration.zero);
      return;
    }

    if (hasPrevious) {
      _currentIndex--;
      await play(_playlist[_currentIndex]);
    }
  }

  Future<void> seek(Duration position) async {
    await _player.seek(position);
  }

  Future<void> setVolume(double volume) async {
    await _player.setVolume(volume.clamp(0.0, 1.0));
  }

  Future<void> dispose() async {
    await _player.dispose();
    await _stateController.close();
    await _positionController.close();
    await _durationController.close();
    await _currentMusiqueController.close();
  }
}
