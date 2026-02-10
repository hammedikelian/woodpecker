import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import '../config/app_config.dart';
import '../models/musique.dart';

class VocalApiResponse {
  final bool success;
  final String? transcript;
  final String intent;
  final Musique? musique;
  final String? error;

  VocalApiResponse({
    required this.success,
    this.transcript,
    required this.intent,
    this.musique,
    this.error,
  });

  factory VocalApiResponse.fromJson(Map<String, dynamic> json) {
    return VocalApiResponse(
      success: json['success'] as bool,
      transcript: json['transcript'] as String?,
      intent: json['intent'] as String,
      musique: json['musique'] != null
          ? Musique.fromJson(json['musique'] as Map<String, dynamic>)
          : null,
      error: json['error'] as String?,
    );
  }

  @override
  String toString() {
    return 'VocalApiResponse{success: $success, transcript: $transcript, intent: $intent, musique: $musique, error: $error}';
  }
}

class VocalApiService {
  final http.Client _client = http.Client();

  Future<VocalApiResponse> recognizeAudio(String audioFilePath) async {
    final file = File(audioFilePath);
    if (!await file.exists()) {
      throw Exception('Audio file not found: $audioFilePath');
    }

    final uri = Uri.parse(AppConfig.recognizeEndpoint);

    final request = http.MultipartRequest('POST', uri);
    request.files.add(
      await http.MultipartFile.fromPath(
        'audio',
        audioFilePath,
        contentType: MediaType('audio', 'wav'),
      ),
    );

    try {
      final streamedResponse = await request.send().timeout(
        AppConfig.apiTimeout,
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final jsonData = json.decode(response.body) as Map<String, dynamic>;
        return VocalApiResponse.fromJson(jsonData);
      } else {
        throw Exception('Server error: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      if (e is SocketException) {
        throw Exception('Unable to connect to server. Please check your connection.');
      }
      rethrow;
    }
  }

  Future<String?> transcribeOnly(String audioFilePath) async {
    final file = File(audioFilePath);
    if (!await file.exists()) {
      throw Exception('Audio file not found: $audioFilePath');
    }

    final uri = Uri.parse(AppConfig.transcribeEndpoint);

    final request = http.MultipartRequest('POST', uri);
    request.files.add(
      await http.MultipartFile.fromPath(
        'audio',
        audioFilePath,
        contentType: MediaType('audio', 'wav'),
      ),
    );

    try {
      final streamedResponse = await request.send().timeout(AppConfig.apiTimeout);
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final jsonData = json.decode(response.body) as Map<String, dynamic>;
        return jsonData['transcript'] as String?;
      } else {
        throw Exception('Server error: ${response.statusCode}');
      }
    } catch (e) {
      if (e is SocketException) {
        throw Exception('Unable to connect to server');
      }
      rethrow;
    }
  }

  Future<bool> checkHealth() async {
    try {
      final uri = Uri.parse(AppConfig.healthEndpoint);
      final response = await _client.get(uri).timeout(
        const Duration(seconds: 5),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body) as Map<String, dynamic>;
        return data['status'] == 'healthy';
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  Future<List<Musique>> getAllMusiques() async {
    try {
      final uri = Uri.parse(AppConfig.musiquesEndpoint);
      final response = await _client.get(uri).timeout(AppConfig.apiTimeout);

      if (response.statusCode == 200) {
        final List<dynamic> jsonList = json.decode(response.body);
        return jsonList
            .map((json) => Musique.fromJson(json as Map<String, dynamic>))
            .toList();
      } else {
        throw Exception('Failed to load musiques: ${response.statusCode}');
      }
    } catch (e) {
      if (e is SocketException) {
        throw Exception('Unable to connect to server');
      }
      rethrow;
    }
  }

  void dispose() {
    _client.close();
  }
}
