import { useEffect, useState } from "react";
import axios from "axios";
import { API_URL } from "./api";

export interface QualityOption {
  value: string;
  label: string;
}

// Used until /api/formats responds, and as a fallback if it can't be reached.
const FALLBACK_OPTIONS: QualityOption[] = [
  { value: "128", label: "128 kbps (4-5 MB/min)" },
  { value: "192", label: "192 kbps (6-7 MB/min)" },
  { value: "256", label: "256 kbps (8-9 MB/min)" },
  { value: "320", label: "320 kbps (10-12 MB/min) - Best" },
];

/** Audio quality options, sourced from the backend with a local fallback. */
export function useQualityOptions(): QualityOption[] {
  const [options, setOptions] = useState<QualityOption[]>(FALLBACK_OPTIONS);

  useEffect(() => {
    let cancelled = false;
    axios
      .get(`${API_URL}/api/formats`)
      .then((res) => {
        const fetched = res.data?.formats;
        if (!cancelled && Array.isArray(fetched) && fetched.length > 0) {
          setOptions(fetched);
        }
      })
      .catch(() => {
        /* keep the fallback options */
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return options;
}
