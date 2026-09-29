/** Settings page */

import { PRODUCT_NAME, THEME_COLORS } from "../utils/constants";
import { useSettings } from "../hooks/useSettings";
import { clsx } from "clsx";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Toggle,
  Input,
  Select,
  Button,
  PageHeader,
} from "../components";

export function SettingsPage() {
  const { settings, updateSetting, resetSettings } = useSettings();

  return (
    <div>
      <PageHeader title="Settings" subtitle="Customize your experience" />

      {/* Appearance */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Appearance</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-snapdragon-navy mb-3">Theme</label>
            <div className="flex gap-4">
              {["light", "dark"].map((theme) => (
                <label
                  key={theme}
                  className={clsx(
                    "flex-1 p-4 rounded-lg border-2 cursor-pointer transition-colors text-center",
                    settings.theme === theme
                      ? "border-snapdragon-blue bg-snapdragon-blue-light"
                      : "border-gray-200 hover:border-gray-300"
                  )}
                >
                  <input
                    type="radio"
                    name="theme"
                    value={theme}
                    checked={settings.theme === theme}
                    onChange={(e) => updateSetting("theme", e.target.value as "light" | "dark")}
                    className="sr-only"
                  />
                  <span className="capitalize font-medium text-snapdragon-navy">{theme}</span>
                </label>
              ))}
            </div>
          </div>

          <div>
            <Toggle
              checked={settings.highContrast}
              onChange={(e) => updateSetting("highContrast", e.target.checked)}
              label="High Contrast Mode"
              description="Increase contrast for better readability (WCAG AAA)"
            />
          </div>

          <Input
            label="Caption Font Size"
            type="number"
            min={12}
            max={48}
            value={settings.captionSize}
            onChange={(e) => updateSetting("captionSize", parseInt(e.target.value) || 18)}
            className="max-w-xs"
          />
        </CardContent>
      </Card>

      {/* Language */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Language</CardTitle>
        </CardHeader>
        <CardContent>
          <Select
            label="Default Language"
            value={settings.defaultLanguage}
            onChange={(e) => updateSetting("defaultLanguage", e.target.value)}
            options={[
              { value: "en", label: "English" },
              { value: "hi", label: "Hindi (हिन्दी)" },
              { value: "hi-Latn", label: "Hinglish" },
            ]}
            className="max-w-md"
          />
        </CardContent>
      </Card>

      {/* Data & Privacy */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Data & Privacy</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-gray-600">
            All data is stored locally on your device. No audio or transcripts are sent to external servers.
          </p>
          <div className="flex items-center gap-4">
            <Button variant="outline" onClick={resetSettings}>
              Reset to Defaults
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* About */}
      <Card>
        <CardHeader>
          <CardTitle>About</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${THEME_COLORS.primary}, ${THEME_COLORS.navy})` }}>
              <svg className="w-7 h-7 text-white" viewBox="0 0 100 100" aria-hidden="true">
                <defs>
                  <linearGradient id="aboutGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor={THEME_COLORS.primary} />
                    <stop offset="100%" stopColor={THEME_COLORS.navy} />
                  </linearGradient>
                </defs>
                <rect width="100" height="100" rx="20" fill="url(#aboutGrad)" />
                <path d="M30 50 L45 65 L70 35" stroke="white" strokeWidth="8" fill="none" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <div>
              <h3 className="font-semibold text-snapdragon-navy">{PRODUCT_NAME}</h3>
              <p className="text-sm text-gray-500">Version 0.1.0</p>
            </div>
          </div>
          <p className="text-sm text-gray-600">
            Offline, NPU-first meeting and classroom copilot for Snapdragon-powered HP PCs.
            Built with FastAPI, React, ONNX Runtime, and ❤️
          </p>
          <div className="pt-4 border-t border-gray-200">
            <p className="text-xs text-gray-400">
              This is a baseline demo. Translation, Meeting Q&A, and Read-aloud are stretch goals.
              NPU benchmarks require Snapdragon X Windows ARM64 device (to verify on device).
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}