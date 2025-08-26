import { spawn } from 'child_process';

const viteProcess = spawn('npx', ['vite', '--host', '--port', '3033'], {
  stdio: 'inherit',
  env: {
    ...process.env,
    VITE_API_URL: 'http://localhost:8085/api'
  }
});

viteProcess.on('error', (err) => {
  console.error('Failed to start Vite:', err);
  process.exit(1);
});
