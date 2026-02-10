class Musique {
  final int id;
  final String titre;
  final String artiste;
  final String? album;
  final int dureeSecondes;
  final String fichierAudio;
  final String? fichierCover;

  Musique({
    required this.id,
    required this.titre,
    required this.artiste,
    this.album,
    required this.dureeSecondes,
    required this.fichierAudio,
    this.fichierCover,
  });

  factory Musique.fromJson(Map<String, dynamic> json) {
    return Musique(
      id: json['id'] as int,
      titre: json['titre'] as String,
      artiste: json['artiste'] as String,
      album: json['album'] as String?,
      dureeSecondes: json['duree_secondes'] as int,
      fichierAudio: json['fichier_audio'] as String,
      fichierCover: json['fichier_cover'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'titre': titre,
      'artiste': artiste,
      'album': album,
      'duree_secondes': dureeSecondes,
      'fichier_audio': fichierAudio,
      'fichier_cover': fichierCover,
    };
  }

  String get formattedDuration {
    final minutes = dureeSecondes ~/ 60;
    final seconds = dureeSecondes % 60;
    return '$minutes:${seconds.toString().padLeft(2, '0')}';
  }

  @override
  String toString() {
    return 'Musique{id: $id, titre: $titre, artiste: $artiste}';
  }
}
