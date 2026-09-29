/** Settings persistence hook */

import { useCallback, useEffect, useState } from "react";

interface Settings {
  captionSize: number;
  highContrast: boolean;
  theme: "light" | "dark";
  defaultLanguage: string;
}

const DEFAULT_SETTINGS: Settings = {
  captionSize: 18,
  highContrast: false,
  theme: "light",
  defaultLanguage: "en",
};

const STORAGE_KEY = "sahayak-settings";

export function useSettings() {
  const [settings, setSettings] = useState<Settings>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        return { ...DEFAULT_SETTINGS, ...JSON.parse(stored) };
      }
    } catch {
      // Ignore parse errors
    }
    return DEFAULT_SETTINGS;
  });

  // Persist settings
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
    } catch {
      // Ignore write errors
    }
  }, [settings]);

  // Apply theme to document
  useEffect(() => {
    document.documentElement.classList.toggle("dark", settings.theme === "dark");
    document.documentElement.classList.toggle("high-contrast", settings.highContrast);
  }, [settings.theme, settings.highContrast]);

  const updateSetting = useCallback(<K extends keyof Settings>(key: K, value: Settings[K]) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
  }, []);

  const resetSettings = useCallback(() => {
    setSettings(DEFAULT_SETTINGS);
  }, []);

  return {
    settings,
    updateSetting,
    resetSettings,
  };
}