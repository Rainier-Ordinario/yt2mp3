import { useState } from "react";
import axios from "axios";
import { API_URL } from "./api";

export interface UseDownload {
  isLoading: boolean;
  error: string;
  success: string;
  /** Returns true if the download succeeded. */
  download: (url: string, quality: string) => Promise<boolean>;
  reset: () => void;
}

/**
 * Owns the state and API call for converting a YouTube URL to MP3, so the
 * component stays presentational.
 */
export function useDownload(): UseDownload {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const reset = () => {
    setError("");
    setSuccess("");
  };

  const download = async (url: string, quality: string): Promise<boolean> => {
    if (!url.trim()) {
      setError("Please enter a YouTube URL");
      return false;
    }

    reset();
    setIsLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/download`, {
        url: url.trim(),
        bitrate: quality,
      });
      setSuccess(`Saved: ${response.data.title}`);
      return true;
    } catch (err: unknown) {
      const message =
        (axios.isAxiosError(err) && err.response?.data?.error) ||
        (err instanceof Error ? err.message : "") ||
        "Download failed";
      setError(message);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  return { isLoading, error, success, download, reset };
}
