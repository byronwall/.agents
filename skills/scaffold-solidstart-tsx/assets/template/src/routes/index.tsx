import { createResource, Show } from "solid-js";
import { AppShell } from "../components/AppShell";
import type { AppData } from "../types/app-data";

async function loadAppData(): Promise<AppData> {
  const response = await fetch("/api/app-data");
  if (!response.ok) throw new Error(`The app data request returned ${response.status}.`);
  return response.json() as Promise<AppData>;
}

export default function Home() {
  const [appData] = createResource(loadAppData);

  return (
    <Show
      when={appData()}
      fallback={
        <main class="status-page">
          <p>{appData.error?.message || "Loading…"}</p>
        </main>
      }
    >
      {(data) => <AppShell data={data()} />}
    </Show>
  );
}
