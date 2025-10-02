import React from 'react'

export function ResultCard({ result, className }: { result: { label: 'Норма' | 'Патология'; probabilities: [number, number]; device: 'GPU' | 'CPU'; preview_png_b64?: string }, className?: string }) {
  const [normal, pathology] = result.probabilities
  return (
    <div className={`rounded-xl border border-gray-800 bg-gray-900 p-6 ${className || ''}`}>
      <div className="flex items-start gap-6">
        {result.preview_png_b64 && (
          <img src={`data:image/png;base64,${result.preview_png_b64}`} alt="preview" className="w-48 h-48 object-contain rounded" />
        )}
        <div className="flex-1">
          <div className="text-lg font-semibold mb-2">Результат: {result.label}</div>
          <div className="text-sm text-gray-300">Normal: {(normal * 100).toFixed(2)}% | Pathology: {(pathology * 100).toFixed(2)}%</div>
          <div className="text-xs text-gray-500 mt-2">Device: {result.device}</div>
        </div>
      </div>
    </div>
  )}


