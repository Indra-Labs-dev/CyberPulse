import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/app_colors.dart';
import '../../settings/application/settings_controller.dart';
import '../application/pomodoro_controller.dart';
import '../application/productivity_controller.dart';

class FocusScreen extends ConsumerWidget {
  const FocusScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final focusMode = ref.watch(focusModeProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Mode Focus & Productivité'),
        actions: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: Row(
              children: [
                Text('Mode Focus', style: TextStyle(color: focusMode ? AppColors.neonBlue : AppColors.textSecondary)),
                Switch(
                  value: focusMode,
                  onChanged: (value) => ref.read(focusModeProvider.notifier).state = value,
                ),
              ],
            ),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (focusMode)
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                margin: const EdgeInsets.only(bottom: 16),
                decoration: BoxDecoration(
                  color: AppColors.neonBlue.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: AppColors.neonBlue.withValues(alpha: 0.4)),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.do_not_disturb_on_outlined, color: AppColors.neonBlue, size: 18),
                    SizedBox(width: 8),
                    Text('Notifications d\'alertes en sourdine — les alertes restent enregistrées.'),
                  ],
                ),
              ),
            const _PomodoroCard(),
            const SizedBox(height: 24),
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(child: _NotesCard()),
                const SizedBox(width: 16),
                Expanded(child: _TasksCard()),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _PomodoroCard extends ConsumerWidget {
  const _PomodoroCard();

  String _format(Duration d) {
    final minutes = d.inMinutes.remainder(60).toString().padLeft(2, '0');
    final seconds = d.inSeconds.remainder(60).toString().padLeft(2, '0');
    return '$minutes:$seconds';
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final pomodoro = ref.watch(pomodoroControllerProvider);
    final isWork = pomodoro.phase == PomodoroPhase.work;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            Text(
              isWork ? 'Session de travail' : 'Pause',
              style: TextStyle(color: isWork ? AppColors.neonBlue : AppColors.securityGreen, fontSize: 16),
            ),
            const SizedBox(height: 12),
            Text(_format(pomodoro.remaining), style: Theme.of(context).textTheme.displayMedium),
            const SizedBox(height: 12),
            Text('${pomodoro.completedSessions} session(s) complétée(s)',
                style: const TextStyle(color: AppColors.textSecondary, fontSize: 12)),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                ElevatedButton.icon(
                  onPressed: pomodoro.isRunning
                      ? () => ref.read(pomodoroControllerProvider.notifier).pause()
                      : () => ref.read(pomodoroControllerProvider.notifier).start(),
                  icon: Icon(pomodoro.isRunning ? Icons.pause : Icons.play_arrow, size: 18),
                  label: Text(pomodoro.isRunning ? 'Pause' : 'Démarrer'),
                ),
                const SizedBox(width: 12),
                OutlinedButton.icon(
                  onPressed: () => ref.read(pomodoroControllerProvider.notifier).reset(),
                  icon: const Icon(Icons.restart_alt, size: 18),
                  label: const Text('Réinitialiser'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _NotesCard extends ConsumerStatefulWidget {
  @override
  ConsumerState<_NotesCard> createState() => _NotesCardState();
}

class _NotesCardState extends ConsumerState<_NotesCard> {
  final _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final notesAsync = ref.watch(notesControllerProvider);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Notes rapides', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: const InputDecoration(hintText: 'Nouvelle note...'),
                    onSubmitted: (value) {
                      if (value.trim().isEmpty) return;
                      ref.read(notesControllerProvider.notifier).add(value.trim());
                      _controller.clear();
                    },
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.add, color: AppColors.neonBlue),
                  onPressed: () {
                    if (_controller.text.trim().isEmpty) return;
                    ref.read(notesControllerProvider.notifier).add(_controller.text.trim());
                    _controller.clear();
                  },
                ),
              ],
            ),
            const SizedBox(height: 8),
            notesAsync.when(
              data: (notes) => Column(
                children: notes.map((note) {
                  return ListTile(
                    dense: true,
                    contentPadding: EdgeInsets.zero,
                    title: Text(note.content, style: const TextStyle(fontSize: 13)),
                    trailing: IconButton(
                      icon: const Icon(Icons.close, size: 16, color: AppColors.textSecondary),
                      onPressed: () => ref.read(notesControllerProvider.notifier).delete(note.id),
                    ),
                  );
                }).toList(),
              ),
              error: (_, _) => const Text('Erreur de chargement'),
              loading: () => const Center(child: CircularProgressIndicator()),
            ),
          ],
        ),
      ),
    );
  }
}

class _TasksCard extends ConsumerStatefulWidget {
  @override
  ConsumerState<_TasksCard> createState() => _TasksCardState();
}

class _TasksCardState extends ConsumerState<_TasksCard> {
  final _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final tasksAsync = ref.watch(tasksControllerProvider);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('To-Do', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: const InputDecoration(hintText: 'Nouvelle tâche...'),
                    onSubmitted: (value) {
                      if (value.trim().isEmpty) return;
                      ref.read(tasksControllerProvider.notifier).add(value.trim());
                      _controller.clear();
                    },
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.add, color: AppColors.neonBlue),
                  onPressed: () {
                    if (_controller.text.trim().isEmpty) return;
                    ref.read(tasksControllerProvider.notifier).add(_controller.text.trim());
                    _controller.clear();
                  },
                ),
              ],
            ),
            const SizedBox(height: 8),
            tasksAsync.when(
              data: (tasks) => Column(
                children: tasks.map((task) {
                  final isDone = task.status == 'DONE';
                  return CheckboxListTile(
                    dense: true,
                    contentPadding: EdgeInsets.zero,
                    value: isDone,
                    onChanged: (value) => ref
                        .read(tasksControllerProvider.notifier)
                        .setStatus(task.id, value == true ? 'DONE' : 'TODO'),
                    title: Text(
                      task.title,
                      style: TextStyle(
                        fontSize: 13,
                        decoration: isDone ? TextDecoration.lineThrough : null,
                        color: isDone ? AppColors.textSecondary : null,
                      ),
                    ),
                  );
                }).toList(),
              ),
              error: (_, _) => const Text('Erreur de chargement'),
              loading: () => const Center(child: CircularProgressIndicator()),
            ),
          ],
        ),
      ),
    );
  }
}
