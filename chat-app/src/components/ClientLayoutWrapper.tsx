"use client";

import { useLayoutEffect } from "react";

interface ClientLayoutWrapperProps {
  children: React.ReactNode;
  geistSansVariable: string;
  geistMonoVariable: string;
}

export default function ClientLayoutWrapper({
  children,
  geistSansVariable,
  geistMonoVariable,
}: ClientLayoutWrapperProps) {
  useLayoutEffect(() => {
    document.body.className = `${geistSansVariable} ${geistMonoVariable} antialiased`;
  }, [geistSansVariable, geistMonoVariable]);

  return <body>{children}</body>;
}
