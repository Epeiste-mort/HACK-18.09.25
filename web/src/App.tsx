import React, { useState } from 'react'
import { Upload } from './components/Upload'
import { ResultCard } from './components/ResultCard'

type Result = {
  label: 'Норма' | 'Патология'
  probabilities: [number, number]
  device: 'GPU' | 'CPU'
  preview_png_b64?: string
}

export default function App() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<Result | null>(null)

  const onUpload = async (file: File) => {
    setError(null)
    setResult(null)
    setLoading(true)
    try {
      const form = new FormData()
      form.append('file', file)
      const resp = await fetch('/api/analyze', {
        method: 'POST',
        body: form
      })
      if (!resp.ok) {
        const msg = await resp.text()
        throw new Error(msg || 'Ошибка запроса')
      }
      const json: Result = await resp.json()
      setResult(json)
    } catch (e: any) {
      setError(e.message || 'Ошибка')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <div className="max-w-4xl mx-auto p-6">
        <h1 className="text-2xl font-semibold mb-4">Поиск аномалий</h1>
        <p className="text-gray-400 mb-6">Загрузите архив тома или файл снимка (.zip, .tar.gz, .nii, .dcm)</p>
        <Upload onUpload={onUpload} loading={loading} />
        {error && <div className="mt-4 text-red-400">{error}</div>}
        {result && <ResultCard className="mt-6" result={result} />}
      </div>
    </div>
  )
}


