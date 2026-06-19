import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';

enum PomodoroPhase { work, shortBreak }

class PomodoroState {
  const PomodoroState({
    required this.remaining,
    required this.phase,
    required this.isRunning,
    required this.completedSessions,
  });

  final Duration remaining;
  final PomodoroPhase phase;
  final bool isRunning;
  final int completedSessions;

  static const workDuration = Duration(minutes: 25);
  static const breakDuration = Duration(minutes: 5);

  factory PomodoroState.initial() => const PomodoroState(
        remaining: workDuration,
        phase: PomodoroPhase.work,
        isRunning: false,
        completedSessions: 0,
      );

  PomodoroState copyWith({Duration? remaining, PomodoroPhase? phase, bool? isRunning, int? completedSessions}) {
    return PomodoroState(
      remaining: remaining ?? this.remaining,
      phase: phase ?? this.phase,
      isRunning: isRunning ?? this.isRunning,
      completedSessions: completedSessions ?? this.completedSessions,
    );
  }
}

final pomodoroControllerProvider = StateNotifierProvider<PomodoroController, PomodoroState>((ref) {
  return PomodoroController();
});

/// Simple Pomodoro session timer (25 min focus / 5 min break) to structure
/// analyst work sessions. Purely client-side — no backend persistence needed.
class PomodoroController extends StateNotifier<PomodoroState> {
  PomodoroController() : super(PomodoroState.initial());

  Timer? _timer;

  void start() {
    if (state.isRunning) return;
    state = state.copyWith(isRunning: true);
    _timer = Timer.periodic(const Duration(seconds: 1), (_) => _tick());
  }

  void pause() {
    _timer?.cancel();
    state = state.copyWith(isRunning: false);
  }

  void reset() {
    _timer?.cancel();
    state = PomodoroState.initial();
  }

  void _tick() {
    if (state.remaining.inSeconds <= 1) {
      _switchPhase();
      return;
    }
    state = state.copyWith(remaining: state.remaining - const Duration(seconds: 1));
  }

  void _switchPhase() {
    if (state.phase == PomodoroPhase.work) {
      state = state.copyWith(
        phase: PomodoroPhase.shortBreak,
        remaining: PomodoroState.breakDuration,
        completedSessions: state.completedSessions + 1,
      );
    } else {
      state = state.copyWith(phase: PomodoroPhase.work, remaining: PomodoroState.workDuration);
    }
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }
}
