'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { PlayCircle, Loader2, AlertCircle, Volume2 } from 'lucide-react';

const languageOptions = [
  { code: 'en-US', name: 'English' },
  { code: 'hi-IN', name: 'Hindi' },
  { code: 'ta-IN', name: 'Tamil' },
  { code: 'ml-IN', name: 'Malayalam' },
  { code: 'te-IN', name: 'Telugu' },
  { code: 'kn-IN', name: 'Kannada' },
];

// Define gender options
const genderOptions = [
    { value: 'FEMALE', label: 'Female' },
    { value: 'MALE', label: 'Male' },
];

export default function Translator() {
  const [inputText, setInputText] = useState<string>('');
  const [translatedText, setTranslatedText] = useState<string>('');
  const [targetLanguage, setTargetLanguage] = useState<string>('hi-IN');
  // Add new state for selected voice gender
  const [voiceGender, setVoiceGender] = useState<string>('FEMALE');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [pendingAudio, setPendingAudio] = useState<string | null>(null);
  const [userInteracted, setUserInteracted] = useState<boolean>(false);
  const autoTranslateRef = useRef<boolean>(true);
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Connect to Server-Sent Events to receive model output
  useEffect(() => {
    const eventSource = new EventSource('/api/model-output');

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.text) {
          // Update input text with model output
          setInputText(data.text);
          autoTranslateRef.current = true; // Enable auto-translate for this update
        }
      } catch (error) {
        console.error('Error parsing SSE message:', error);
      }
    };

    eventSource.onerror = (error) => {
      console.error('SSE connection error:', error);
      // Optionally reconnect after a delay
      setTimeout(() => {
        if (eventSource.readyState === EventSource.CLOSED) {
          // Reconnect logic could go here if needed
        }
      }, 3000);
    };

    return () => {
      eventSource.close();
    };
  }, []);

  const handleTranslateAndSpeak = useCallback(async () => {
    if (!inputText.trim()) return;
    setError('');
    setIsProcessing(true);
    setTranslatedText('');

    try {
      let textToSpeak = inputText;
      if (targetLanguage !== 'en-US') {
        const translateResponse = await fetch('/api/translate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: inputText, targetLanguage: targetLanguage.split('-')[0] }),
        });
        if (!translateResponse.ok) {
            const errData = await translateResponse.json();
            throw new Error(errData.error || 'Translation failed.');
        }
        const { translatedText: newTranslatedText } = await translateResponse.json();
        textToSpeak = newTranslatedText;
        setTranslatedText(newTranslatedText);
      } else {
        setTranslatedText(inputText);
      }

      const speechResponse = await fetch('/api/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        // Pass the selected gender to the backend
        body: JSON.stringify({ text: textToSpeak, languageCode: targetLanguage, gender: voiceGender }),
      });
      if (!speechResponse.ok) {
        const errData = await speechResponse.json();
        throw new Error(errData.error || 'Speech generation failed.');
      }
      const { audioContent } = await speechResponse.json();
      
      // Create audio element
      const audio = new Audio(`data:audio/mp3;base64,${audioContent}`);
      audioRef.current = audio;
      
      // Try to play audio, handle autoplay restrictions
      try {
        const playPromise = audio.play();
        if (playPromise !== undefined) {
          await playPromise;
          // Successfully playing
          setPendingAudio(null);
          setUserInteracted(true); // Mark that we can now autoplay
        }
      } catch (playError: any) {
        // Autoplay was prevented - store audio for manual play
        console.log('Autoplay prevented, storing audio for manual play');
        setPendingAudio(`data:audio/mp3;base64,${audioContent}`);
        // Don't show this as an error to the user, just store it
      }

    } catch (err: any) {
      setError(`An error occurred: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  }, [inputText, targetLanguage, voiceGender]);

  // Function to play pending audio (called when user clicks play button)
  const playPendingAudio = useCallback(() => {
    if (pendingAudio) {
      const audio = new Audio(pendingAudio);
      audio.play().then(() => {
        setPendingAudio(null);
        setUserInteracted(true);
      }).catch((err) => {
        console.error('Error playing audio:', err);
        setError('Failed to play audio. Please try again.');
      });
    }
  }, [pendingAudio]);

  // Auto-trigger translation when input changes (with debounce)
  useEffect(() => {
    // Clear existing timer
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    // Only auto-translate if flag is set and input is not empty
    if (autoTranslateRef.current && inputText.trim()) {
      // Debounce: wait 500ms after last input change
      debounceTimerRef.current = setTimeout(() => {
        handleTranslateAndSpeak();
        autoTranslateRef.current = false; // Reset flag after auto-translation
      }, 500);
    } else {
      // If user manually types, don't auto-translate
      autoTranslateRef.current = false;
    }

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [inputText, targetLanguage, voiceGender, handleTranslateAndSpeak]);

  return (
    <div className="w-full">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 text-left">
        <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200 flex flex-col">
          <label htmlFor="input-text" className="block text-base font-semibold text-gray-700 mb-2">
            Step 1: Gesture Input
          </label>
          <textarea
            id="input-text"
            value={inputText}
            onChange={(e) => {
              setInputText(e.target.value);
              autoTranslateRef.current = false; // Disable auto-translate on manual input
            }}
            placeholder="This is a test sentence. In real use case data will be received from the smart glove."
            className="w-full flex-grow p-4 bg-gray-100 text-gray-800 rounded-md border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:outline-none transition resize-none"
          />
        </div>
        <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200 flex flex-col">
          <label htmlFor="language-select" className="block text-base font-semibold text-gray-700 mb-2">
            Step 2: Select Language & Process
          </label>
          <select
            id="language-select"
            value={targetLanguage}
            onChange={(e) => setTargetLanguage(e.target.value)}
            className="w-full p-3 bg-gray-100 text-gray-800 rounded-md border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:outline-none mb-4"
          >
            {languageOptions.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.name}
              </option>
            ))}
          </select>
          
          {/* New UI for Gender Selection */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-600 mb-2">Voice Gender</label>
            <div className="flex items-center space-x-4">
              {genderOptions.map((option) => (
                <label key={option.value} className="flex items-center space-x-2 text-sm text-gray-700 cursor-pointer">
                  <input
                    type="radio"
                    name="gender"
                    value={option.value}
                    checked={voiceGender === option.value}
                    onChange={(e) => setVoiceGender(e.target.value)}
                    className="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                  />
                  <span>{option.label}</span>
                </label>
              ))}
            </div>
          </div>
          
          <div className="w-full flex-grow p-4 bg-gray-100 rounded-md border border-gray-300 overflow-y-auto mb-4">
            <p className="text-gray-800">{translatedText || "Translated text will appear here."}</p>
          </div>
          
          {/* Show play button if audio is pending (autoplay was blocked) */}
          {pendingAudio && (
            <button
              onClick={playPendingAudio}
              className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-green-600 text-white rounded-md font-semibold hover:bg-green-700 transition-all mb-2"
            >
              <Volume2 className="h-5 w-5" /> Play Audio
            </button>
          )}
          
          <button
            onClick={() => {
              setUserInteracted(true); // Mark user interaction
              handleTranslateAndSpeak();
            }}
            disabled={isProcessing || !inputText.trim()}
            className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-md font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all"
          >
            {isProcessing ? (
              <><Loader2 className="animate-spin h-5 w-5 mr-2" /> Processing...</>
            ) : (
              <><PlayCircle /> Translate & Speak</>
            )}
          </button>
        </div>
      </div>
      {error && (
        <div className="mt-6 w-full p-4 bg-red-100 border border-red-300 text-red-800 rounded-md text-sm text-left flex items-center gap-3">
            <AlertCircle className="h-5 w-5 flex-shrink-0" />
            <span>{error}</span>
        </div>
      )}
    </div>
  );
}