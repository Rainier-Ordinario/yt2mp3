"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import axios from "axios";

const QUALITY_OPTIONS = [
  { value: "128", label: "128 kbps (4-5 MB/min)" },
  { value: "192", label: "192 kbps (6-7 MB/min)" },
  { value: "256", label: "256 kbps (8-9 MB/min)" },
  { value: "320", label: "320 kbps (10-12 MB/min) - Best" },
];

// Direct process.env reference so Next.js can inline it at build time.
// Falls back to localhost so local dev works with no configuration.
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function YouTubeConverter() {
  const [url, setUrl] = useState("");
  const [quality, setQuality] = useState("320");
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState<string[]>([]);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const addStatus = (message: string) => {
    setStatus((prev) => [...prev, message]);
  };

  const clearStatus = () => {
    setStatus([]);
    setError("");
    setSuccess("");
  };

  const handleDownload = async () => {
    if (!url.trim()) {
      setError("Please enter a YouTube URL");
      return;
    }

    clearStatus();
    setIsLoading(true);

    try {
      addStatus("Validating URL...");
      addStatus("Fetching video information...");

      const response = await axios.post(`${API_URL}/api/download`, {
        url: url.trim(),
        bitrate: quality,
      });

      if (response.status === 200) {
        addStatus(`Successfully downloaded: ${response.data.title}`);
        addStatus(`Quality: ${quality} kbps`);
        addStatus("Converting to MP3...");
        setSuccess(`Downloaded: ${response.data.title}`);
        setUrl("");
        setStatus([]);
      }
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.error || err.message || "Download failed";
      setError(errorMessage);
      addStatus(`Error: ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  };

  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.6, staggerChildren: 0.1 },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 10 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.4 } },
  };

  return (
    <motion.div
      className="flex flex-col items-center text-center px-4 max-w-2xl mx-auto space-y-8"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Header */}
      <motion.div className="space-y-4" variants={itemVariants}>
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-foreground">
          YouTube to MP3
        </h1>
        <p className="text-lg md:text-xl text-muted-foreground max-w-2xl font-light leading-relaxed">
          Download and convert your favorite YouTube videos to high-quality MP3
          audio
        </p>
      </motion.div>

      {/* URL Input */}
      <motion.div className="w-full max-w-xl space-y-3" variants={itemVariants}>
        <label className="block text-sm font-semibold text-foreground text-left">
          YouTube URL
        </label>
        <Input
          type="text"
          placeholder="https://www.youtube.com/watch?v=..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleDownload()}
          disabled={isLoading}
          className="text-base h-11"
        />
      </motion.div>

      {/* Quality Selector */}
      <motion.div className="w-full max-w-xl space-y-3" variants={itemVariants}>
        <label className="block text-sm font-semibold text-foreground text-left">
          Audio Quality
        </label>
        <Select value={quality} onValueChange={setQuality} disabled={isLoading}>
          <SelectTrigger className="h-11 text-base">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {QUALITY_OPTIONS.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </motion.div>

      {/* Download Button */}
      <motion.div className="w-full max-w-xl" variants={itemVariants}>
        <Button
          onClick={handleDownload}
          disabled={isLoading}
          size="lg"
          className="w-full h-12 text-base font-semibold"
        >
          {isLoading ? "Downloading..." : "Download as MP3"}
        </Button>
      </motion.div>

      {/* Status Messages */}
      {status.length > 0 && (
        <motion.div
          className="w-full max-w-xl p-4 rounded-lg bg-secondary/50 border border-border space-y-2"
          variants={itemVariants}
        >
          <p className="text-sm font-semibold text-foreground text-left">
            Status
          </p>
          <div className="space-y-1 text-sm text-muted-foreground text-left font-mono">
            {status.map((msg, idx) => (
              <div key={idx}>→ {msg}</div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Error Message */}
      {error && (
        <motion.div
          className="w-full max-w-xl p-4 rounded-lg bg-destructive/10 border border-destructive/30"
          variants={itemVariants}
        >
          <p className="text-sm text-destructive font-medium">{error}</p>
        </motion.div>
      )}

      {/* Success Message */}
      {success && (
        <motion.div
          className="w-full max-w-xl p-4 rounded-lg bg-green-500/10 border border-green-500/30"
          variants={itemVariants}
        >
          <p className="text-sm text-green-600 font-medium">{success}</p>
        </motion.div>
      )}

      {/* Info */}
      <motion.div
        className="w-full max-w-xl pt-6 border-t border-border text-xs text-muted-foreground space-y-2 font-light"
        variants={itemVariants}
      >
        <p className="opacity-75">Saves to: ~/Downloads/YouTube MP3s</p>
        <p className="opacity-75">For personal use only. Respect content creators' rights.</p>
      </motion.div>
    </motion.div>
  );
}
