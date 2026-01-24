import React, { useState } from "react";
import type { Message } from "../store/useGenerationStore";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { atomDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { Code, Video, Copy, Check } from "lucide-react";
import { toast } from "sonner";

interface ChatMessageProps {
  msg: Message;
  isLast: boolean;
  isLoading?: boolean;
  statusDisplay?: React.ReactNode;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  msg,
  isLast,
  isLoading,
  statusDisplay,
}) => {
  const [showCode, setShowCode] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (msg.code) {
      navigator.clipboard.writeText(msg.code);
      setCopied(true);
      toast.success("Code copied to clipboard");
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (msg.role === "user") {
    return (
      <div className="flex justify-end animate-in fade-in slide-in-from-bottom-2 duration-300">
        <div className="max-w-[70%] bg-blue-600 text-white rounded-2xl rounded-br-sm px-4 py-3 shadow-md">
          <p className="text-[15px] leading-relaxed">{msg.content}</p>
        </div>
      </div>
    );
  }

  // Determine if this is a text-only message (no video)
  const isTextOnly = !msg.videoUrl;

  return (
    <div className="flex justify-start w-full animate-in fade-in slide-in-from-bottom-2 duration-300 relative group">
      <div className={`${isTextOnly ? "max-w-[65%]" : "max-w-[75%]"}`}>
        {/* Toggle Button - positioned relative to content */}
        {msg.code && msg.videoUrl && (
          <div className="flex justify-end mb-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <button
              onClick={() => setShowCode(!showCode)}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-600 bg-white/80 hover:bg-white rounded-lg transition-all border border-gray-200/80 shadow-sm backdrop-blur-sm"
            >
              {showCode ? (
                <>
                  <Video className="w-3.5 h-3.5" />
                  Show Animation
                </>
              ) : (
                <>
                  <Code className="w-3.5 h-3.5" />
                  Show Code
                </>
              )}
            </button>
          </div>
        )}

        {/* Message Bubble */}
        <div className="bg-gray-50 text-gray-800 rounded-2xl rounded-bl-sm overflow-hidden shadow-sm border border-gray-200/60">
          {/* Text Content */}
          {msg.content && (
            <div className="px-4 py-3">
              <p className="text-[15px] leading-relaxed text-gray-700">
                {msg.content}
              </p>
            </div>
          )}

          {/* Media Content */}
          {msg.videoUrl && (
            <div className="bg-gradient-to-b from-gray-100/50 to-gray-100 rounded-xl overflow-hidden m-2 mt-0">
              {showCode && msg.code ? (
                <div className="relative">
                  <div className="absolute top-3 right-3 z-10">
                    <button
                      onClick={handleCopy}
                      className="p-2 bg-gray-800/70 hover:bg-gray-800 text-gray-300 rounded-lg transition-colors backdrop-blur-sm"
                      title="Copy Code"
                    >
                      {copied ? (
                        <Check className="w-4 h-4 text-green-400" />
                      ) : (
                        <Copy className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                  <div className="max-h-[300px] overflow-auto rounded-xl">
                    <SyntaxHighlighter
                      language="python"
                      style={atomDark}
                      customStyle={{
                        margin: 0,
                        padding: "1.25rem",
                        fontSize: "0.8rem",
                        lineHeight: "1.6",
                        backgroundColor: "#1a1a2e",
                      }}
                      wrapLongLines={true}
                    >
                      {msg.code}
                    </SyntaxHighlighter>
                  </div>
                </div>
              ) : (
                <div className="relative aspect-video bg-gradient-to-br from-gray-900 to-black rounded-xl overflow-hidden shadow-inner">
                  {msg.videoUrl ? (
                    <video
                      src={msg.videoUrl}
                      controls
                      autoPlay
                      loop
                      muted
                      playsInline
                      className="w-full h-full object-contain"
                    />
                  ) : (
                    <div className="flex items-center justify-center w-full h-full text-gray-400">
                      Video not available
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Status Display for last message */}
          {isLast && isLoading && statusDisplay && (
            <div className="px-4 pb-3">{statusDisplay}</div>
          )}
        </div>
      </div>
    </div>
  );
};
