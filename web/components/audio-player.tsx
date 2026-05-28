"use client";

import { useRef, useEffect, useState } from "react";

interface Segment {
  start: number;
  end: number;
  text: string;
}

interface AudioPlayerProps {
  audioSrc: string;
  segments: Segment[];
}

export default function AudioPlayer({ audioSrc, segments }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [activeIndex, setActiveIndex] = useState<number>(-1);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleTimeUpdate = () => {
      const time = audio.currentTime;
      for (let i = segments.length - 1; i >= 0; i--) {
        if (time >= segments[i].start) {
          setActiveIndex(i);
          break;
        }
      }
    };

    audio.addEventListener("timeupdate", handleTimeUpdate);
    return () => audio.removeEventListener("timeupdate", handleTimeUpdate);
  }, [segments]);

  const seekTo = (time: number, index: number) => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.currentTime = time;
    audio.play();
    setActiveIndex(index);
  };

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  return (
    <div>
      <audio ref={audioRef} controls className="w-full mb-3">
        <source src={audioSrc} type="audio/mpeg" />
      </audio>

      <div className="max-h-80 overflow-y-auto border rounded-md">
        {segments.map((seg, i) => (
          <div
            key={i}
            onClick={() => seekTo(seg.start, i)}
            className={`flex items-start gap-2 px-3 py-2 cursor-pointer text-sm border-b last:border-b-0 transition-colors ${
              activeIndex === i
                ? "bg-primary/10 font-medium"
                : "hover:bg-muted"
            }`}
          >
            <span className="text-primary font-mono whitespace-nowrap">
              [{formatTime(seg.start)}]
            </span>
            <span className="text-foreground/80">{seg.text.slice(0, 100)}{seg.text.length > 100 ? "..." : ""}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
