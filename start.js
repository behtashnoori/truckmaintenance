import { spawn } from 'child_process';

const isWin = process.platform === 'win32';
const npmCmd = isWin ? 'npm.cmd' : 'npm';

const backend = spawn('python', ['-m', 'backend.main'], { stdio: 'inherit' });
const frontend = spawn(npmCmd, ['run', 'frontend'], { stdio: 'inherit' });

const processes = [backend, frontend];

function shutdown(code) {
  for (const proc of processes) {
    if (!proc.killed) {
      proc.kill('SIGINT');
    }
  }
  if (code !== undefined) {
    process.exit(code);
  }
}

for (const proc of processes) {
  proc.on('exit', (code) => shutdown(code ?? 0));
}

process.on('SIGINT', () => shutdown());
process.on('SIGTERM', () => shutdown());
