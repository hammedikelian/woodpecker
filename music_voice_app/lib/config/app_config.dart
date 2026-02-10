import 'dart:io' show Platform;

class AppConfig {
  // For physical devices, use your Mac's local IP address
  // Change this to your Mac's IP (found via: ipconfig getifaddr en0)
  static const String localNetworkIp = '192.168.1.91';

  // Set to true when testing on physical device, false for simulators/emulators
  static const bool usePhysicalDevice = true;

  static String get baseUrl {
    if (usePhysicalDevice) {
      // Physical device on same WiFi network
      return 'http://$localNetworkIp';
    } else if (Platform.isAndroid) {
      // Android emulator uses 10.0.2.2 to access host machine
      return 'http://10.0.2.2';
    } else {
      // iOS simulator uses localhost
      return 'http://localhost';
    }
  }

  // Service URLs
  static String get vocalServiceUrl => '$baseUrl:5001';
  static String get bddServiceUrl => '$baseUrl:5002';

  // API Endpoints
  static String get recognizeEndpoint => '$vocalServiceUrl/recognize';
  static String get transcribeEndpoint => '$vocalServiceUrl/transcribe';
  static String get musiquesEndpoint => '$bddServiceUrl/musiques';
  static String get healthEndpoint => '$vocalServiceUrl/health';

  // Audio settings
  static const int sampleRate = 16000;
  static const int numChannels = 1;
  static const int bitDepth = 16;

  // Timeouts
  static const Duration apiTimeout = Duration(seconds: 30);
  static const Duration recordingMaxDuration = Duration(seconds: 10);
}
