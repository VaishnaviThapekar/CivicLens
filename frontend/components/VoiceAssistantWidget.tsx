"use client";

import { useState } from "react";
import { Mic, MicOff, Volume2, Sparkles, X, CheckCircle2 } from "lucide-react";

export default function VoiceAssistantWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [listening, setListening] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [response, setResponse] = useState<string | null>(null);
  const [language, setLanguage] = useState<"English" | "Marathi" | "Hindi">("English");

  const speakAudioReply = (textToSpeak: string) => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(textToSpeak);
      if (language === "Marathi") utterance.lang = "mr-IN";
      else if (language === "Hindi") utterance.lang = "hi-IN";
      else utterance.lang = "en-IN";

      utterance.onstart = () => setSpeaking(true);
      utterance.onend = () => setSpeaking(false);
      utterance.onerror = () => setSpeaking(false);

      window.speechSynthesis.speak(utterance);
    }
  };

  const handleStartListening = () => {
    setListening(true);
    setTranscript("");
    setResponse(null);

    // Simulate voice speech-to-text recognition
    setTimeout(() => {
      let respText = "";
      if (language === "Marathi") {
        setTranscript("कॉलेज रोडवर मोठा खड्डा पडला आहे, अपघात होण्याची शक्यता आहे.");
        respText = "मराठी संदेश मिळाला! प्रकरणाचे वर्गीकरण: रस्ता पायाभूत सुविधा (PWD). तक्रार नोंदवली गेली आहे.";
      } else if (language === "Hindi") {
        setTranscript("यहाँ कॉलेज रोड के पास सड़क पर बड़ा गड्ढा है।");
        respText = "हिंदी संदेश प्राप्त हुआ! AI श्रेणी: सड़क मरम्मत cell. प्राथमिकता: P1 Critical.";
      } else {
        setTranscript("Large crater pothole hazard near college gate corridor.");
        respText = "Voice report transcribed! AI Vision confidence: 94%. Department dispatched: PWD Division.";
      }
      setResponse(respText);
      setListening(false);
      speakAudioReply(respText);
    }, 1800);
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 animate-fade-in">
      {!isOpen ? (
        <button
          onClick={() => setIsOpen(true)}
          className="px-4 py-3 rounded-full bg-[#287C73] hover:bg-[#1F645D] text-white font-extrabold text-xs shadow-2xl flex items-center gap-2 transition-all hover:scale-105 teal-glow border-2 border-white"
        >
          <Mic className="w-4 h-4 text-white animate-pulse" />
          <span>🎙️ Multilingual AI Voice</span>
        </button>
      ) : (
        <div className="w-80 bg-white border border-[#E7E9E4] rounded-3xl p-5 shadow-2xl space-y-4 text-[#102C2B]">
          <div className="flex items-center justify-between border-b border-[#E7E9E4] pb-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-xl bg-[#287C73]/10 text-[#287C73] flex items-center justify-center font-bold">
                🎙️
              </div>
              <div>
                <h4 className="text-xs font-black">AI Multilingual Voice</h4>
                <span className="text-[10px] text-[#4B6363]">Marathi • Hindi • English</span>
              </div>
            </div>

            <button onClick={() => setIsOpen(false)} className="text-[#4B6363] hover:text-[#102C2B]">
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Language Selector */}
          <div className="flex bg-[#F7F6F2] p-1 rounded-xl border border-[#E7E9E4] text-[11px] font-bold">
            <button
              onClick={() => setLanguage("English")}
              className={`flex-1 py-1 rounded-lg ${language === "English" ? "bg-[#287C73] text-white" : "text-[#4B6363]"}`}
            >
              English
            </button>
            <button
              onClick={() => setLanguage("Marathi")}
              className={`flex-1 py-1 rounded-lg ${language === "Marathi" ? "bg-[#287C73] text-white" : "text-[#4B6363]"}`}
            >
              मराठी
            </button>
            <button
              onClick={() => setLanguage("Hindi")}
              className={`flex-1 py-1 rounded-lg ${language === "Hindi" ? "bg-[#287C73] text-white" : "text-[#4B6363]"}`}
            >
              हिंदी
            </button>
          </div>

          {/* Voice Input Button */}
          <div className="text-center py-2 space-y-2">
            <button
              onClick={handleStartListening}
              disabled={listening}
              className={`w-16 h-16 rounded-full mx-auto flex items-center justify-center shadow-lg transition-all ${
                listening ? "bg-red-500 text-white animate-ping" : "bg-[#287C73] hover:bg-[#1F645D] text-white teal-glow"
              }`}
            >
              <Mic className="w-6 h-6" />
            </button>
            <p className="text-[11px] text-[#4B6363] font-semibold">
              {listening ? "Listening... Speak in " + language : "Tap microphone to speak"}
            </p>
          </div>

          {/* Transcript Display */}
          {transcript && (
            <div className="p-3 rounded-2xl bg-[#F7F6F2] border border-[#E7E9E4] text-xs font-semibold text-[#102C2B]">
              <span className="text-[10px] text-[#287C73] font-black block uppercase">Transcribed Speech:</span>
              "{transcript}"
            </div>
          )}

          {/* Response Output & Spoken Audio Indicator */}
          {response && (
            <div className="p-3 rounded-2xl bg-emerald-50 border border-emerald-200 text-xs font-bold text-emerald-800 space-y-1">
              <div className="flex items-center justify-between text-[#10B981]">
                <div className="flex items-center gap-1.5">
                  <Volume2 className={`w-4 h-4 ${speaking ? "animate-bounce text-emerald-600" : ""}`} />
                  <span>AI Voice Reply:</span>
                </div>
                <button
                  type="button"
                  onClick={() => speakAudioReply(response)}
                  className="text-[10px] bg-emerald-600 text-white px-2 py-0.5 rounded-full hover:bg-emerald-700"
                >
                  🔊 Replay Audio
                </button>
              </div>
              <p className="text-[11px]">{response}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
