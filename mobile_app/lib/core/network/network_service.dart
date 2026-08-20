import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';

enum NetworkState { online, offline, syncing }

class NetworkService {
  static final NetworkService _instance = NetworkService._internal();
  factory NetworkService() => _instance;
  NetworkService._internal() {
    _initConnectivity();
  }

  final Connectivity _connectivity = Connectivity();
  final StreamController<NetworkState> _stateController = StreamController<NetworkState>.broadcast();

  NetworkState _currentState = NetworkState.online;
  NetworkState get currentState => _currentState;
  Stream<NetworkState> get onStateChanged => _stateController.stream;

  void _initConnectivity() {
    _connectivity.onConnectivityChanged.listen((result) {
      final isOffline = result == ConnectivityResult.none;
      _currentState = isOffline ? NetworkState.offline : NetworkState.online;
      _stateController.add(_currentState);
    });
  }

  Future<bool> checkConnection() async {
    final result = await _connectivity.checkConnectivity();
    final isOffline = result == ConnectivityResult.none;
    _currentState = isOffline ? NetworkState.offline : NetworkState.online;
    return !_currentState.name.contains('offline');
  }

  void setSyncing(bool syncing) {
    if (syncing) {
      _currentState = NetworkState.syncing;
    } else {
      _currentState = NetworkState.online;
    }
    _stateController.add(_currentState);
  }
}
