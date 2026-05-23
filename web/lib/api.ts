// Base URL of the Flask backend. Direct process.env reference so Next.js
// can inline it at build time; falls back to localhost for local dev.
export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
