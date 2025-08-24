export const metadata = {
  title: 'ArchiVision',
  description: 'AI renders & 3D from architecture sketches',
};

import '../styles/globals.css';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
