import { create } from "zustand";
import { toast } from "sonner";

export type JobStatus =
  | "pending"
  | "generating_code"
  | "fixing_code"
  | "rendering"
  | "completed"
  | "failed"
  | string; // Allow dynamic status strings like "rendering (retry 2/3)"

export interface Message {
  role: "user" | "assistant";
  content: string;
  videoUrl?: string;
  code?: string;
}

export interface Job {
  id: string;
  title?: string;
  prompt: string;
  status: JobStatus;
  videoUrl?: string;
  createdAt: string;
  conversationId?: string;
}

export interface Conversation {
  id: string;
  title: string;
  updatedAt: string;
  jobs?: Job[];
}

interface GenerationState {
  messages: Message[];
  isLoading: boolean;
  status: JobStatus | "idle";
  currentJobId: string | null;
  error: string | null;

  // API Key State
  apiKey: string | null;
  showApiKeyDialog: boolean;
  setApiKey: (key: string) => void;
  setShowApiKeyDialog: (show: boolean) => void;

  // Conversation State
  conversations: Conversation[];
  currentConversationId: string | null;
  isConversationsLoading: boolean;

  // Actions
  addMessage: (message: Message) => void;
  setLoading: (isLoading: boolean) => void;
  setStatus: (status: JobStatus | "idle") => void;
  setError: (error: string | null) => void;
  generateAnimation: (prompt: string, token?: string | null) => Promise<void>;

  // New Conversation Actions
  fetchConversations: (token: string) => Promise<void>;
  createConversation: (token: string, title?: string) => Promise<string>;
  loadConversation: (
    conversation: Conversation,
    token: string,
  ) => Promise<void>;
  deleteConversation: (id: string, token: string) => Promise<void>;
  startNewChat: () => void;
  reset: () => void;
}

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const API_KEY_STORAGE_KEY = "manim_genai_api_key";

export const useGenerationStore = create<GenerationState>((set, get) => ({
  messages: [],
  isLoading: false,
  status: "idle",
  currentJobId: null,
  error: null,
  conversations: [],
  currentConversationId: null,
  isConversationsLoading: false,

  // Initialize from local storage
  apiKey: localStorage.getItem(API_KEY_STORAGE_KEY),
  showApiKeyDialog: false,

  setApiKey: (key: string) => {
    localStorage.setItem(API_KEY_STORAGE_KEY, key);
    set({ apiKey: key });
  },

  setShowApiKeyDialog: (show: boolean) => set({ showApiKeyDialog: show }),

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
      currentConversationId: null,
    }),

  startNewChat: () => {
    set({
      messages: [],
      isLoading: false,
      status: "idle",
      currentJobId: null,
      error: null,
      currentConversationId: null,
    });
  },

  fetchConversations: async (token: string) => {
    set({ isConversationsLoading: true });
    try {
      const response = await fetch(`${API_URL}/conversations/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        set({ conversations: data });
      }
    } catch (e) {
      console.error("Failed to fetch conversations", e);
    } finally {
      set({ isConversationsLoading: false });
    }
  },

  createConversation: async (token: string, title: string = "New Chat") => {
    try {
      const response = await fetch(`${API_URL}/conversations/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ title }),
      });
      if (!response.ok) throw new Error("Failed to create conversation");
      const data = await response.json();
      set((state) => ({
        conversations: [data, ...state.conversations],
        currentConversationId: data.id,
      }));
      return data.id;
    } catch (e) {
      console.error(e);
      throw e;
    }
  },

  deleteConversation: async (id: string, token: string) => {
    try {
      const response = await fetch(`${API_URL}/conversations/${id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error("Failed to delete conversation");

      // Update local state
      set((state) => {
        const newConversations = state.conversations.filter((c) => c.id !== id);
        // If we deleted the current conversation, reset state or switch to another?
        // Let's just reset if current is deleted.
        if (state.currentConversationId === id) {
          return {
            conversations: newConversations,
            currentConversationId: null,
            messages: [],
            status: "idle",
            error: null,
          };
        }
        return { conversations: newConversations };
      });
      toast.success("Conversation deleted");
    } catch (e) {
      console.error(e);
      toast.error("Failed to delete conversation");
    }
  },

  loadConversation: async (conversation: Conversation, token: string) => {
    // Set basic info first
    set({
      currentConversationId: conversation.id,
      isLoading: true,
      messages: [], // Clear previous messages while loading
    });

    try {
      // Fetch full conversation details to get jobs
      const response = await fetch(
        `${API_URL}/conversations/${conversation.id}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        },
      );

      if (!response.ok) throw new Error("Failed to load conversation details");

      const fullConv = await response.json();

      // Convert jobs to messages
      const messages: Message[] = [];
      if (fullConv.jobs && fullConv.jobs.length > 0) {
        fullConv.jobs.forEach((job: any) => {
          messages.push({ role: "user", content: job.prompt });
          if (job.status === "completed" && job.videoUrl) {
            messages.push({
              role: "assistant",
              content: "Here is the animation:",
              videoUrl: `${API_URL}/video/stream/${job.id}`,
              // Provide both fields to handle different aliases depending on API version
              code: job.code || job.generatedCode,
            });
          } else if (job.status === "failed") {
            messages.push({
              role: "assistant",
              content: `Generation failed: ${job.errorMessage || "Unknown error"}`,
            });
          } else if (
            job.status === "pending" ||
            job.status === "generating_code" ||
            job.status === "rendering"
          ) {
            // Pending job logic can be tricky if we want to resume polling.
            // For now, just show status. Ideally we resume polling.
            messages.push({
              role: "assistant",
              content: "Generation in progress...",
            });
          }
        });
      }

      set({
        messages,
        isLoading: false,
        // If last job is pending, we might want to set status/currentJobId to resume polling?
        // Skipping that complexity for now unless requested.
      });
    } catch (e) {
      console.error(e);
      set({ isLoading: false, error: "Failed to load conversation" });
    }
  },

  generateAnimation: async (prompt: string, token?: string | null) => {
    const {
      addMessage,
      setLoading,
      setStatus,
      setError,
      currentConversationId,
      apiKey,
    } = get();

    // Reset error on new attempt
    setError(null);
    setLoading(true);
    // Add user message immediately
    addMessage({ role: "user", content: prompt });

    try {
      let conversationId = currentConversationId;

      // Create conversation if none exists
      if (!conversationId && token) {
        // Use first few words of prompt as title
        const title = prompt.split(" ").slice(0, 5).join(" ") + "...";
        try {
          // Create it
          const newConvResponse = await fetch(`${API_URL}/conversations/`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({ title }),
          });
          if (newConvResponse.ok) {
            const newConv = await newConvResponse.json();
            conversationId = newConv.id;
            set((state) => ({
              conversations: [newConv, ...state.conversations],
              currentConversationId: newConv.id,
            }));
          }
        } catch (e) {
          console.warn(
            "Failed to create conversation, proceeding without it",
            e,
          );
        }
      }

      // 1. Submit Job
      let response;
      let retries = 3;
      while (retries > 0) {
        try {
          const headers: HeadersInit = { "Content-Type": "application/json" };
          if (token) {
            headers["Authorization"] = `Bearer ${token}`;
          }
          if (apiKey) {
            headers["x-gemini-api-key"] = apiKey;
          }

          response = await fetch(`${API_URL}/generate`, {
            method: "POST",
            headers,
            body: JSON.stringify({
              prompt,
              conversation_id: conversationId,
            }),
          });

          if (response.status === 402) {
            set({ showApiKeyDialog: true, isLoading: false });
            throw new Error(
              "Free credits exhausted. Please provide an API key.",
            );
          }

          if (response.ok) break;
          // If 500 error, maybe retry? If 400, don't.
          if (response.status >= 500) {
            throw new Error(`Server error: ${response.status}`);
          } else {
            // Client error, don't retry
            break;
          }
        } catch (e: any) {
          if (e.message.includes("Free credits")) throw e;
          console.warn(`Attempt failed, retries left: ${retries - 1}`, e);
          if (retries === 1) throw e;
        }
        retries--;
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }

      if (!response || !response.ok) {
        if (response?.status !== 402) {
          throw new Error("Failed to start generation");
        }
        return;
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
          const statusRes = await fetch(`${API_URL}/status/${jobId}`);

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
              code: jobData.code,
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
      if (err.message.includes("Free credits")) {
        setLoading(false);
        return;
      }
      console.error("Generation error", err);
      setLoading(false);
      setStatus("failed");
      setError(err.message || "Failed to connect to server");
      toast.error(err.message || "Failed to start generation");
      addMessage({
        role: "assistant",
        content:
          "Sorry, I could not start the generation process. Please try again.",
      });
    }
  },
}));
