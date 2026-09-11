import type { AppData } from "../types/app-data";

interface AppShellProps {
  data: AppData;
}

export function AppShell(props: AppShellProps) {
  return (
    <main class="app-shell">
      <p class="label">SolidStart SPA</p>
      <h1>{props.data.title}</h1>
      <p>{props.data.description}</p>
      <code>GET /api/app-data</code>
    </main>
  );
}
