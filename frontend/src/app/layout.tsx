import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'HabitQuest - Gamifiez vos habitudes',
  description: 'Transformez vos habitudes quotidiennes en quêtes épiques. Gagnez de l\'XP, montez de niveau et devenez la meilleure version de vous-même.',
  keywords: ['habits', 'gamification', 'productivity', 'rpg', 'self-improvement'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr" className="dark">
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
