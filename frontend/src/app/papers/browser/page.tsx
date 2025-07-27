'use client';

import { FileBrowser } from '@/components/papers/FileBrowser';

export default function FileBrowserPage() {
  return (
    <div className="h-screen flex flex-col">
      <div className="bg-white border-b px-6 py-4">
        <h1 className="text-2xl font-bold">Research Papers File Browser</h1>
        <p className="text-gray-600 mt-1">
          Browse, edit, and organize your research papers and documents
        </p>
      </div>
      <div className="flex-1 overflow-hidden">
        <FileBrowser />
      </div>
    </div>
  );
}