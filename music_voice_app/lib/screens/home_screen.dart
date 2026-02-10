import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/music_provider.dart';
import '../widgets/voice_button.dart';
import '../widgets/mini_player.dart';
import '../widgets/audio_visualizer.dart';
import '../widgets/loading_overlay.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Music Voice',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              context.read<MusicProvider>().loadMusiques();
            },
          ),
        ],
      ),
      body: Consumer<MusicProvider>(
        builder: (context, provider, child) {
          return Stack(
            children: [
              Column(
                children: [
                  // Music list
                  Expanded(
                    child: _buildMusicList(context, provider),
                  ),

                  // Status area
                  if (provider.lastTranscript != null ||
                      provider.errorMessage != null)
                    _buildStatusArea(context, provider),

                  // Voice control area
                  _buildVoiceControlArea(context, provider),

                  // Mini player
                  if (provider.currentMusique != null)
                    const MiniPlayer(),
                ],
              ),

              // Loading overlay
              if (provider.isProcessing)
                const LoadingOverlay(message: 'Traitement en cours...'),
            ],
          );
        },
      ),
    );
  }

  Widget _buildMusicList(BuildContext context, MusicProvider provider) {
    if (provider.musiques.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.music_off,
              size: 64,
              color: Colors.grey,
            ),
            SizedBox(height: 16),
            Text(
              'Aucune musique disponible',
              style: TextStyle(color: Colors.grey),
            ),
            SizedBox(height: 8),
            Text(
              'Vérifiez la connexion au serveur',
              style: TextStyle(color: Colors.grey, fontSize: 12),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.symmetric(vertical: 8),
      itemCount: provider.musiques.length,
      itemBuilder: (context, index) {
        final musique = provider.musiques[index];
        final isCurrentlyPlaying =
            provider.currentMusique?.id == musique.id && provider.isPlaying;

        return ListTile(
          leading: Container(
            width: 50,
            height: 50,
            decoration: BoxDecoration(
              color: Colors.deepPurple.withOpacity(0.3),
              borderRadius: BorderRadius.circular(8),
            ),
            child: isCurrentlyPlaying
                ? const AudioVisualizer(isPlaying: true)
                : const Icon(Icons.music_note, color: Colors.deepPurple),
          ),
          title: Text(
            musique.titre,
            style: TextStyle(
              fontWeight:
                  isCurrentlyPlaying ? FontWeight.bold : FontWeight.normal,
              color: isCurrentlyPlaying ? Colors.deepPurple : Colors.white,
            ),
          ),
          subtitle: Text(
            '${musique.artiste} • ${musique.formattedDuration}',
            style: TextStyle(
              color: isCurrentlyPlaying
                  ? Colors.deepPurple.withOpacity(0.7)
                  : Colors.grey,
            ),
          ),
          trailing: isCurrentlyPlaying
              ? IconButton(
                  icon: const Icon(Icons.pause_circle_filled),
                  color: Colors.deepPurple,
                  iconSize: 36,
                  onPressed: () => provider.pause(),
                )
              : IconButton(
                  icon: const Icon(Icons.play_circle_outline),
                  color: Colors.grey,
                  iconSize: 36,
                  onPressed: () => provider.playMusique(musique),
                ),
          onTap: () {
            if (isCurrentlyPlaying) {
              provider.pause();
            } else {
              provider.playMusique(musique);
            }
          },
        );
      },
    );
  }

  Widget _buildStatusArea(BuildContext context, MusicProvider provider) {
    return Container(
      padding: const EdgeInsets.all(16),
      color: provider.errorMessage != null
          ? Colors.red.withOpacity(0.1)
          : Colors.deepPurple.withOpacity(0.1),
      child: Row(
        children: [
          Icon(
            provider.errorMessage != null ? Icons.error_outline : Icons.mic,
            color: provider.errorMessage != null ? Colors.red : Colors.deepPurple,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (provider.lastTranscript != null)
                  Text(
                    '"${provider.lastTranscript}"',
                    style: const TextStyle(fontStyle: FontStyle.italic),
                  ),
                if (provider.lastIntent != null && provider.errorMessage == null)
                  Text(
                    'Action: ${provider.lastIntent}',
                    style: TextStyle(
                      color: Colors.grey[400],
                      fontSize: 12,
                    ),
                  ),
                if (provider.errorMessage != null)
                  Text(
                    provider.errorMessage!,
                    style: const TextStyle(color: Colors.red),
                  ),
              ],
            ),
          ),
          if (provider.errorMessage != null)
            IconButton(
              icon: const Icon(Icons.close),
              onPressed: () => provider.clearError(),
            ),
        ],
      ),
    );
  }

  Widget _buildVoiceControlArea(BuildContext context, MusicProvider provider) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            Colors.transparent,
            Colors.deepPurple.withOpacity(0.1),
          ],
        ),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          VoiceButton(
            isListening: provider.isListening,
            onPressed: () {
              if (provider.isListening) {
                provider.stopListeningAndProcess();
              } else {
                provider.startListening();
              }
            },
            onLongPressStart: () => provider.startListening(),
            onLongPressEnd: () => provider.stopListeningAndProcess(),
          ),
          const SizedBox(height: 12),
          Text(
            provider.isListening
                ? 'Je vous écoute...'
                : 'Appuyez pour parler',
            style: TextStyle(
              color: provider.isListening ? Colors.deepPurple : Colors.grey,
              fontWeight:
                  provider.isListening ? FontWeight.bold : FontWeight.normal,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Ex: "Joue Bohemian Rhapsody"',
            style: TextStyle(
              color: Colors.grey[600],
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }
}
