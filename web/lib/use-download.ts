import { useState } from "react";
import { API_URL } from "./api";

export interface UseDownload {
  isLoading: boolean;
  error: string;
  success: string;
  /** Human-readable progress line (e.g. "45.3% • 2.1MiB/s • ETA 00:08"). */
  progress: string;
  /** Returns true if the download succeeded. */
  download: (url: string, quality: string) => Promise<boolean>;
  reset: () => void;
}

interface DownloadEvent {
  type: "progress" | "converting" | "done" | "error";
  percent?: string;
  speed?: string;
  eta?: string;
  title?: string;
  message?: string;
}

/**
 * Owns the state and API call for converting a YouTube URL to MP3, so the
 * component stays presentational. The backend streams NDJSON progress
 * events; each line is one event of type progress / converting / done / error.
 */
export function useDownload(): UseDownload {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [progress, setProgress] = useState("");

  const reset = () => {
    setError("");
    setSuccess("");
    setProgress("");
  };

  const download = async (url: string, quality: string): Promise<boolean> => {
    if (!url.trim()) {
      setError("Please enter a YouTube URL");
      return false;
    }

    reset();
    setIsLoading(true);
    setProgress("Starting…");

    try {
      const res = await fetch(`${API_URL}/api/download`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim(), bitrate: quality }),
      });

      // Synchronous validation / ffmpeg-missing errors come back as JSON.
      if (!res.ok) {
        const data = (await res.json().catch(() => null)) as
          | { error?: string }
          | null;
        setError(data?.error || "Download failed");
        return false;
      }
      if (!res.body) {
        setError("No response body from server");
        return false;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let succeeded = false;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        // One JSON event per line; a partial line stays in the buffer
        // until the next chunk completes it.
        let nl: number;
        while ((nl = buffer.indexOf("\n")) >= 0) {
          const line = buffer.slice(0, nl).trim();
          buffer = buffer.slice(nl + 1);
          if (!line) continue;

          let event: DownloadEvent;
          try {
            event = JSON.parse(line) as DownloadEvent;
          } catch {
            continue;
          }

          if (event.type === "progress") {
            const parts = [
              event.percent,
              event.speed,
              event.eta ? `ETA ${event.eta}` : "",
            ].filter(Boolean);
            setProgress(parts.length ? parts.join(" • ") : "Downloading…");
          } else if (event.type === "converting") {
            setProgress("Converting to MP3…");
          } else if (event.type === "done") {
            setSuccess(`Saved: ${event.title}`);
            succeeded = true;
          } else if (event.type === "error") {
            setError(event.message || "Download failed");
          }
        }
      }

      return succeeded;
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Download failed";
      setError(message);
      return false;
    } finally {
      setIsLoading(false);
      setProgress("");
    }
  };

  return { isLoading, error, success, progress, download, reset };
}
