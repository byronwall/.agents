import appDataJson from "../../data/app-data.json";
import type { AppData } from "../../types/app-data";

const appData = appDataJson satisfies AppData;

export function GET() {
  return Response.json(appData, {
    headers: {
      "Cache-Control": "no-store",
    },
  });
}
