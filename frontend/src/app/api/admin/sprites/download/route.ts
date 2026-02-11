import { NextRequest, NextResponse } from 'next/server';
import { writeFile, mkdir } from 'fs/promises';
import path from 'path';

export async function POST(request: NextRequest) {
  try {
    const { url, localPath } = await request.json();
    
    if (!url || !localPath) {
      return NextResponse.json({ error: 'Missing url or localPath' }, { status: 400 });
    }

    // Télécharger depuis GitHub
    const response = await fetch(url);
    if (!response.ok) {
      return NextResponse.json({ error: 'Failed to download sprite' }, { status: 500 });
    }

    const buffer = await response.arrayBuffer();
    
    // Créer le dossier si nécessaire
    const fullPath = path.join(process.cwd(), 'public', localPath);
    const dir = path.dirname(fullPath);
    await mkdir(dir, { recursive: true });
    
    // Sauvegarder le fichier
    await writeFile(fullPath, Buffer.from(buffer));
    
    return NextResponse.json({ success: true, path: localPath });
  } catch (error) {
    console.error('Download error:', error);
    return NextResponse.json({ error: 'Download failed' }, { status: 500 });
  }
}
