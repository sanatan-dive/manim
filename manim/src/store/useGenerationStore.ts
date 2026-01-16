import { create } from "zustand";
import { toast } from "sonner";

export type JobStatus =
  | "pending"
  | "generating_code"
  | "rendering"
  | "completed"
  | "failed";

export interface Message {
  role: "user" | "assistant";
  content: string;
  videoUrl?: string;
}

interface GenerationState {
  messages: Message[];
  isLoading: boolean;
  status: JobStatus | "idle";
  currentJobId: string | null;
  error: string | null;

  // Actions
  addMessage: (message: Message) => void;
  setLoading: (isLoading: boolean) => void;
  setStatus: (status: JobStatus | "idle") => void;
  setError: (error: string | null) => void;
  generateAnimation: (prompt: string) => Promise<void>;
  reset: () => void;
}

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const useGenerationStore = create<GenerationState>((set, get) => ({
  messages: [],
  isLoading: false,
  status: "idle",
  currentJobId: null,
  error: null,

  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),
  setLoading: (isLoading) => set({ isLoading }),
  setStatus: (status) => set({ status }),
  setError: (error) => set({ error }),

  reset: () =>
    set({
      messages: [],
      isLoading: false,
      status: "idle",
      currentJobId: null,
      error: null,
    }),

  generateAnimation: async (prompt: string) => {
    const { addMessage, setLoading, setStatus, setError } = get();

    // Reset error on new attempt
    setError(null);
    setLoading(true);
    // Add user message immediately
    addMessage({ role: "user", content: prompt });

    try {
      // 1. Submit Job
      let response;
      let retries = 3;
      while (retries > 0) {
        try {
          response = await fetch(`${API_URL}/generate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt }),
          });
          if (response.ok) break;
          // If 500 error, maybe retry? If 400, don't.
          if (response.status >= 500) {
            throw new Error(`Server error: ${response.status}`);
          } else {
            // Client error, don't retry
            break;
          }
        } catch (e) {
          console.warn(`Attempt failed, retries left: ${retries - 1}`, e);
          if (retries === 1) throw e;
        }
        retries--;
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }

      if (!response || !response.ok) {
        throw new Error("Failed to start generation");
      }

      const data = await response.json();
      const jobId = data.job_id;

      set({ currentJobId: jobId });

      // Add initial assistant response
      addMessage({
        role: "assistant",
        content: "I'm on it! Generating your animation code...",
      });

      // 2. Poll Status
      const maxAttempts = 120; // 10 minutes (5s interval)
      let attempts = 0;

      const pollInterval = setInterval(async () => {
        try {
          attempts++;
          const statusRes = await fetch(
            `${API_URL}/status/${jobId}`
          );

          if (!statusRes.ok) {
            // Transient error in polling, ignore or count?
            // We'll just continue polling unless it happens too often.
            console.warn("Poll request failed");
            return;
          }

          const jobData = await statusRes.json();
          // Map backend status to frontend status if needed
          // Backend may return: "pending", "generating_code", "rendering", "completed", "failed"
          const currentStatus = jobData.status;
          setStatus(currentStatus);

          if (currentStatus === "completed") {
            clearInterval(pollInterval);
            setLoading(false);
            
            // Use the proxy endpoint to avoid S3 presigned URL issues
            const videoUrl = `${API_URL}/video/stream/${jobId}`;

            // Add completion message
            addMessage({
              role: "assistant",
              content: "Here represents your animation!",
              videoUrl,
            });
            toast.success("Animation generated successfully!");
          } else if (currentStatus === "failed") {
            clearInterval(pollInterval);
            setLoading(false);
            const errorMsg = jobData.error_message || "Unknown error occurred";
            setError(errorMsg);
            addMessage({
              role: "assistant",
              content: `I encountered an error: ${errorMsg}`,
            });
            toast.error(`Generation failed: ${errorMsg}`);
          } else {
            // Still running.
            // Maybe update last message content based on status?
            // "Generating code..." -> "Rendering video..."
            if (attempts >= maxAttempts) {
              clearInterval(pollInterval);
              setLoading(false);
              setError("Timeout waiting for generation");
              toast.error("Generation timed out");
              addMessage({
                role: "assistant",
                content: "The generation took too long and timed out.",
              });
            }
          }
        } catch (err) {
          console.error("Polling error", err);
        }
      }, 5000);
    } catch (err: any) {
      console.error("Generation error", err);
      setLoading(false);
      setStatus("failed");
      setError(err.message || "Failed to connect to server");
      toast.error("Failed to start generation");
      addMessage({
        role: "assistant",
        content:
          "Sorry, I could not start the generation process. Please try again.",
      });
    }
  },
}));
