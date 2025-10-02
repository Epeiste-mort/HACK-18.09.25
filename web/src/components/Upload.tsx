import React, { useCallback, useRef, useState } from 'react'

export function Upload({ onUpload, loading }: { onUpload: (f: File) => void; loading: boolean }) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragOver, setDragOver] = useState(false)

  const pick = useCallback(() => inputRef.current?.click(), [])
  const onChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return
    onUpload(e.target.files[0])
  }, [onUpload])

  const onDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setDragOver(false)
    const f = e.dataTransfer.files?.[0]
    if (f) onUpload(f)
  }, [onUpload])

  return (
    <div>
      <input ref={inputRef} type="file" className="hidden" onChange={onChange} />
      <div
        onClick={pick}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        className={`rounded-xl border-2 border-dashed p-10 text-center cursor-pointer transition ${dragOver ? 'border-blue-400 bg-blue-950/30' : 'border-gray-700 bg-gray-900'}`}
      >
        <div className="text-gray-300">Перетащите файл сюда или нажмите для выбора</div>
        <div className="text-xs text-gray-500 mt-2">Поддержка: .zip, .tar(.gz), .rar, .nii(.gz), .dcm</div>
        {loading && <div className="mt-4 text-blue-300">Загрузка...</div>}
      </div>
    </div>
  )
}


