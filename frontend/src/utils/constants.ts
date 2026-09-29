/** Product constants - single source of truth for product name */

export const PRODUCT_NAME = "Sahayak";
export const PRODUCT_TAGLINE = "Offline NPU-first meeting & classroom copilot";

export const THEME_COLORS = {
  primary: "#3253DC",
  primaryHover: "#2843B8",
  primaryLight: "#E8ECFA",
  navy: "#0B1A4F",
  navyLight: "#152A6B",
} as const;

export const LANGUAGES = [
  { code: "en", name: "English", nativeName: "English" },
  { code: "hi", name: "Hindi", nativeName: "हिन्दी" },
  { code: "hi-Latn", name: "Hinglish", nativeName: "Hinglish" },
] as const;

export const PROVIDER_LABELS: Record<string, string> = {
  QNNExecutionProvider: "NPU (QNN)",
  CUDAExecutionProvider: "GPU (CUDA)",
  DmlExecutionProvider: "GPU (DirectML)",
  CPUExecutionProvider: "CPU",
  Mock: "Simulated",
} as const;

export const STAGE_LABELS: Record<string, string> = {
  vad: "Voice Activity Detection",
  asr: "Speech Recognition",
  summarization: "Summarization",
} as const;