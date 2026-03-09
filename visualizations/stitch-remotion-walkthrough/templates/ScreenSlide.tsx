import React from 'react';
import {AbsoluteFill, Img, spring, useCurrentFrame, useVideoConfig} from 'remotion';

export interface ScreenSlideProps {
  imageSrc: string;
  title: string;
  description?: string;
}

export function ScreenSlide({
  imageSrc,
  title,
  description,
}: Readonly<ScreenSlideProps>) {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const imageScale = spring({
    frame,
    fps,
    from: 0.96,
    to: 1,
    config: {
      damping: 14,
      stiffness: 90,
    },
  });

  const imageOpacity = spring({
    frame,
    fps,
    from: 0,
    to: 1,
    config: {
      damping: 12,
      stiffness: 80,
    },
  });

  const textOpacity = spring({
    frame: frame - 10,
    fps,
    from: 0,
    to: 1,
    config: {
      damping: 12,
      stiffness: 80,
    },
  });

  return (
    <AbsoluteFill
      style={{
        background: 'linear-gradient(180deg, #0b1020 0%, #1f2937 100%)',
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <div
        style={{
          width: '88%',
          maxHeight: '78%',
          transform: `scale(${imageScale})`,
          opacity: imageOpacity,
        }}
      >
        <Img
          src={imageSrc}
          style={{
            width: '100%',
            height: 'auto',
            borderRadius: 18,
            boxShadow: '0 24px 80px rgba(0, 0, 0, 0.35)',
          }}
        />
      </div>

      <div
        style={{
          position: 'absolute',
          left: '8%',
          right: '8%',
          bottom: '7%',
          opacity: textOpacity,
          color: '#f9fafb',
          fontFamily: 'ui-sans-serif, system-ui, sans-serif',
        }}
      >
        <div
          style={{
            fontSize: 48,
            fontWeight: 700,
            lineHeight: 1.05,
            marginBottom: 10,
          }}
        >
          {title}
        </div>
        {description ? (
          <div
            style={{
              fontSize: 24,
              lineHeight: 1.35,
              color: '#d1d5db',
              maxWidth: '70%',
            }}
          >
            {description}
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
}
