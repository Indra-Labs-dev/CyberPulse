/// Central runtime configuration for CyberPulse.
///
/// Values can be overridden at build/run time with `--dart-define`, e.g.:
/// flutter run -d windows --dart-define=API_BASE_URL=http://192.168.1.10:8000
class AppConfig {
  AppConfig._();

  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://127.0.0.1:8000',
  );

  static const String apiPrefix = '/api/v1';

  static const String socketUrl = String.fromEnvironment(
    'SOCKET_URL',
    defaultValue: 'http://127.0.0.1:8000',
  );

  static String get apiBaseUrlWithPrefix => '$apiBaseUrl$apiPrefix';

  static const Duration connectTimeout = Duration(seconds: 10);
  static const Duration receiveTimeout = Duration(seconds: 15);
}
