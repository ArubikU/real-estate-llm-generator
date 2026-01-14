interface TutorialStep4Props {
  onSkip: () => void
}

export default function TutorialStep4({ onSkip }: TutorialStep4Props) {
  return (
    <div 
      className="absolute pointer-events-auto bg-white rounded-lg shadow-2xl"
      style={{
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: '90%',
        maxWidth: '500px',
        zIndex: 60
      }}
    >
      <div className="bg-gradient-to-r from-purple-500 to-purple-600 text-white p-6 rounded-t-lg">
        <div className="flex items-center gap-3 mb-2">
          <div className="bg-white text-purple-600 rounded-full w-10 h-10 flex items-center justify-center font-bold text-xl">
            4
          </div>
          <h3 className="text-2xl font-bold">Revisa y guarda los datos</h3>
        </div>
        <p className="text-purple-100">Verifica que los datos extraídos sean correctos antes de guardar</p>
      </div>
      <div className="p-6">
        <div className="space-y-4 mb-6">
          <div className="flex items-start gap-3 bg-purple-50 rounded-lg p-4 border-l-4 border-purple-400">
            <svg className="w-6 h-6 text-purple-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
            </svg>
            <div>
              <p className="font-bold text-gray-800">Verifica los datos</p>
              <p className="text-sm text-gray-600">Precio, ubicación, habitaciones, baños, etc.</p>
            </div>
          </div>
          <div className="flex items-start gap-3 bg-purple-50 rounded-lg p-4 border-l-4 border-purple-400">
            <svg className="w-6 h-6 text-purple-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"/>
            </svg>
            <div>
              <p className="font-bold text-gray-800">Haz clic en "Guardar"</p>
              <p className="text-sm text-gray-600">Si todo se ve bien, guarda la propiedad en la base de datos</p>
            </div>
          </div>
          <div className="flex items-start gap-3 bg-purple-50 rounded-lg p-4 border-l-4 border-purple-400">
            <svg className="w-6 h-6 text-purple-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
            <div>
              <p className="font-bold text-gray-800">¡Listo para la siguiente!</p>
              <p className="text-sm text-gray-600">Repite el proceso con otra propiedad</p>
            </div>
          </div>
        </div>
        <button
          onClick={onSkip}
          className="w-full bg-gradient-to-r from-purple-600 to-purple-700 text-white py-4 px-6 rounded-lg font-bold hover:from-purple-700 hover:to-purple-800 transition-all flex items-center justify-center gap-2 text-lg"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          ¡Entendido! Comenzar a usar
        </button>
      </div>
    </div>
  )
}
