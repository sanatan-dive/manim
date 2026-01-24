import React, { useState } from "react";
import { X, Key, ExternalLink, ShieldCheck } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface ApiKeyDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (key: string) => void;
}

export function ApiKeyDialog({ isOpen, onClose, onSubmit }: ApiKeyDialogProps) {
  const [key, setKey] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (key.trim().length > 10) {
      onSubmit(key.trim());
      onClose();
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="w-full max-w-md bg-white border border-gray-200 rounded-xl shadow-2xl overflow-hidden"
          >
            {/* Header */}
            <div className="relative p-6 border-b border-gray-200 bg-gray-50/50">
              <button
                onClick={onClose}
                className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors"
                title="Close"
              >
                <X className="w-5 h-5" />
              </button>
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-blue-500/10 rounded-lg">
                  <Key className="w-6 h-6 text-blue-600" />
                </div>
                <h2 className="text-xl font-semibold text-gray-900">
                  Enter Gemini API Key
                </h2>
              </div>
              <p className="text-sm text-gray-600">
                You've used your free credits. To continue generating
                animations, please provide your own API key.
              </p>
            </div>

            {/* Content */}
            <div className="p-6 space-y-6">
              {/* Privacy Notice */}
              <div className="flex gap-3 p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
                <ShieldCheck className="w-5 h-5 text-green-600 shrink-0 mt-0.5" />
                <div className="text-xs text-green-800/80">
                  <strong className="text-green-700 block mb-1">
                    Privacy First
                  </strong>
                  Your API key is stored <strong>only in your browser</strong>.
                  It is never saved to our database.
                </div>
              </div>

              {/* Instructions */}
              <div className="space-y-3">
                <h3 className="text-sm font-medium text-gray-900">
                  How to get a key:
                </h3>
                <ol className="text-sm text-gray-600 space-y-2 list-decimal list-inside">
                  <li>
                    Go to{" "}
                    <a
                      href="https://aistudio.google.com/app/apikey"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline inline-flex items-center gap-1"
                    >
                      Google AI Studio <ExternalLink className="w-3 h-3" />
                    </a>
                  </li>
                  <li>Click "Create API key"</li>
                  <li>Copy the key and paste it below</li>
                </ol>
              </div>

              {/* Form */}
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <input
                    type="password"
                    value={key}
                    onChange={(e) => setKey(e.target.value)}
                    placeholder="Paste your API key here (AIzo...)"
                    className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-gray-900 placeholder-gray-400 transition-all font-mono text-sm"
                    autoFocus
                  />
                </div>
                <button
                  type="submit"
                  disabled={key.length < 10}
                  className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  Save Key & Continue
                </button>
              </form>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
