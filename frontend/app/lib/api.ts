// Central place for the backend API base URL.
//
// In Docker (dev and prod compose), NEXT_PUBLIC_API_URL is set to the
// backend service's address on the compose network (e.g. http://backend:8000).
// Outside Docker (running `next dev` directly against a locally-running
// backend), it falls back to localhost on the backend's default port.
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
