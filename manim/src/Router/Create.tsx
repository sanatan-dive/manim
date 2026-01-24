import { PlaceholdersAndVanishInput } from "../components/ui/placeholders-and-vanish-input";
import { useState, useRef, useEffect } from "react";
import {
  X,
  Trash2,
  SidebarClose,
  SidebarIcon,
  CheckCircle2,
  Circle,
  Loader2,
  Plus,
  MessageSquare,
} from "lucide-react";
import { useGenerationStore } from "../store/useGenerationStore";
import type { Conversation } from "../store/useGenerationStore";
import { useAuth, useUser } from "@clerk/clerk-react"; // Import Clerk hook
import { useNavigate, useSearchParams } from "react-router-dom";
import { ChatMessage } from "../components/ChatMessage";
import { toast } from "sonner";
import { ApiKeyDialog } from "../components/ApiKeyDialog";

function Create() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const { getToken } = useAuth(); // Get auth token
  const { user } = useUser(); // Get user details
  const [inputValue, setInputValue] = useState("");

  const {
    messages,
    isLoading,
    status,
    generateAnimation,
    conversations,
    currentConversationId,
    fetchConversations,
    loadConversation,
    deleteConversation,
    startNewChat,
    isConversationsLoading,
    showApiKeyDialog,
    setShowApiKeyDialog,
    setApiKey,
  } = useGenerationStore();

  const bottomRef = useRef<HTMLDivElement>(null);

  // Keyboard shortcut for focus
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd/Ctrl + K to focus
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        const input = document.querySelector(
          'input[type="text"]',
        ) as HTMLInputElement;
        if (input) input.focus();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  // Load conversations on mount
  useEffect(() => {
    const initData = async () => {
      try {
        const token = await getToken();
        if (token) {
          await fetchConversations(token);
        }
      } catch (error) {
        console.error("Failed to fetch conversations", error);
      }
    };
    initData();
  }, [getToken, fetchConversations]);

  // Handle URL params for Chat ID
  useEffect(() => {
    const chatId = searchParams.get("chatId");
    if (
      chatId &&
      chatId !== currentConversationId &&
      conversations.length > 0
    ) {
      const conv = conversations.find((c) => c.id === chatId);
      if (conv) {
        const load = async () => {
          const token = await getToken();
          if (token) await loadConversation(conv, token);
        };
        load();
      }
    } else if (!chatId && currentConversationId) {
      // If URL has no chatId but store has one (e.g. from new chat creation), maintain sync?
      // Or if user navigated to /create without params, maybe reset?
      // For now, let's just create a new chat if user clears URL? No, that's annoying.
    }
  }, [searchParams, conversations, currentConversationId, getToken]);

  // Sync URL with current conversation
  useEffect(() => {
    if (currentConversationId) {
      setSearchParams({ chatId: currentConversationId });
    } else {
      setSearchParams({});
    }
  }, [currentConversationId, setSearchParams]);

  const handleNewChat = () => {
    startNewChat();
    setSearchParams({}); // Clear URL param
    // Close sidebar on mobile
    if (window.innerWidth < 1024) {
      setIsSidebarOpen(false);
    }
  };

  const handleLoadConversation = async (conv: Conversation) => {
    try {
      const token = await getToken();
      if (token) {
        await loadConversation(conv, token);
        // Close sidebar on mobile
        if (window.innerWidth < 1024) {
          setIsSidebarOpen(false);
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleDeleteConversation = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation(); // Prevent loading the conversation when clicking delete
    if (!confirm("Delete this chat?")) return;

    try {
      const token = await getToken();
      if (token) {
        await deleteConversation(id, token);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handlePromptClick = (text: string) => {
    setInputValue(text);
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading, status]);

  const placeholders = [
    "Create a circle that transforms into a square",
    "Animate a bouncing ball with physics",
    "Show a sine wave animation",
    "Create a rotating cube in 3D",
    "Animate text that fades in and moves",
  ];

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (isLoading) return; // Prevent multiple submissions
    if (!inputValue) return;

    // Input Validation
    if (inputValue.length < 10) {
      toast.warning("Prompt must be at least 10 characters long.");
      return;
    }
    if (inputValue.length > 1000) {
      toast.warning("Prompt must be less than 1000 characters.");
      return;
    }

    try {
      const token = await getToken();
      await generateAnimation(inputValue, token);
    } catch (error) {
      console.error("Auth error or generation failed", error);
      toast.error("Failed to generate animation. Please try again.");
    }
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const toggleSidebarCollapse = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
  };

  const getStatusDisplay = () => {
    if (status === "idle" || status === "completed" || status === "failed")
      return null;

    const steps = [
      { id: "generating_code", label: "Generating Code" },
      { id: "fixing_code", label: "Fixing Code" },
      { id: "rendering", label: "Rendering Animation" },
    ];

    // Map status to active step index (handle string matching for dynamic statuses)
    let activeIndex = -1;
    const statusStr = String(status);
    if (statusStr === "generating_code") activeIndex = 0;
    if (statusStr.includes("fixing_code")) activeIndex = 1;
    if (statusStr.includes("rendering")) activeIndex = 2;
    if (statusStr === "pending") activeIndex = 0; // Show first step as loading

    // Filter out fixing_code step if we haven't reached it
    const visibleSteps =
      activeIndex >= 1 ? steps : steps.filter((s) => s.id !== "fixing_code");

    return (
      <div className="flex items-center justify-center space-x-3 py-2 bg-gray-50/80 backdrop-blur-sm rounded-xl max-w-md mx-auto mt-2">
        {visibleSteps.map((step, idx) => {
          const originalIndex = steps.findIndex((s) => s.id === step.id);
          return (
            <div key={step.id} className="flex items-center space-x-2">
              {originalIndex < activeIndex ? (
                <CheckCircle2 className="w-4 h-4 text-green-500" />
              ) : originalIndex === activeIndex ? (
                <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
              ) : (
                <Circle className="w-4 h-4 text-gray-300" />
              )}
              <span
                className={`text-xs ${
                  originalIndex === activeIndex
                    ? "font-semibold text-blue-600"
                    : originalIndex < activeIndex
                      ? "text-green-600"
                      : "text-gray-400"
                }`}
              >
                {step.label}
              </span>
              {idx < visibleSteps.length - 1 && (
                <div className="w-6 h-px bg-gray-300 mx-1" />
              )}
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div>
      <div className="bg-gray-50 min-h-screen flex font-funnel">
        {/* Sidebar */}
        <div
          className={`fixed inset-y-0 left-0 z-50 ${
            isSidebarCollapsed ? "w-16" : "w-64"
          } bg-gray-200 m-3 shadow-lg transform transition-all duration-300 ease-in-out rounded-r-2xl -ml-2 ${
            isSidebarOpen ? "translate-x-0" : "-translate-x-full"
          } lg:translate-x-0 lg:static lg:inset-0`}
        >
          <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
            {!isSidebarCollapsed && (
              <div
                className="font-funnel flex items-center gap-2 m-4 cursor-pointer"
                onClick={() => navigate("/")}
              >
                <div className="w-3 h-3 bg-black border rounded-full translate-y-0.5 "></div>
                <h1 className="text-xl font-medium">Madio</h1>
              </div>
            )}
            <div className="flex items-center space-x-2">
              <button
                onClick={toggleSidebarCollapse}
                className="hidden lg:flex p-2 rounded-lg hover:bg-gray-100 transition-colors"
              >
                {isSidebarCollapsed ? (
                  <SidebarIcon className="w-5 h-5 text-gray-600" />
                ) : (
                  <SidebarClose className="w-5 h-5 text-gray-600" />
                )}
              </button>
              <button
                onClick={toggleSidebar}
                className="lg:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <X className="w-5 h-5 text-gray-600" />
              </button>
            </div>
          </div>

          <nav className="mt-6 px-4 flex flex-col h-[calc(100vh-140px)]">
            {/* New Chat Button */}
            <button
              onClick={handleNewChat}
              className={`flex items-center w-full px-4 py-3 mb-4 bg-white border border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50 hover:border-gray-300 transition-all duration-200 ${
                isSidebarCollapsed ? "justify-center" : ""
              }`}
              title="New Chat"
            >
              <Plus className="w-5 h-5 flex-shrink-0" />
              {!isSidebarCollapsed && (
                <span className="font-medium ml-3">New Chat</span>
              )}
            </button>

            {/* Conversations List */}
            <div className="flex-1 overflow-y-auto space-y-2 pr-1 custom-scrollbar">
              {isConversationsLoading ? (
                <div className="space-y-2 px-1">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <div
                      key={i}
                      className="flex items-center px-4 py-3 bg-white/50 rounded-xl"
                    >
                      <div className="w-5 h-5 bg-gray-200 rounded animate-pulse flex-shrink-0" />
                      {!isSidebarCollapsed && (
                        <div className="ml-3 h-4 bg-gray-200 rounded animate-pulse w-3/4" />
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <>
                  {conversations.length > 0 && !isSidebarCollapsed && (
                    <div className="px-4 py-2 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                      Recent
                    </div>
                  )}

                  {conversations.map((conv) => (
                    <div
                      key={conv.id}
                      className={`flex items-center w-full px-4 py-3 rounded-xl transition-colors duration-200 group relative ${
                        currentConversationId === conv.id
                          ? "bg-white shadow-sm ring-1 ring-gray-200"
                          : "hover:bg-white hover:shadow-sm"
                      }`}
                    >
                      <button
                        onClick={() => handleLoadConversation(conv)}
                        className="flex-1 flex items-center text-left min-w-0"
                        title={isSidebarCollapsed ? conv.title : ""}
                      >
                        <MessageSquare
                          className={`w-5 h-5 flex-shrink-0 ${
                            currentConversationId === conv.id
                              ? "text-gray-700 "
                              : "text-gray-400 group-hover:text-gray-600"
                          }`}
                        />
                        {!isSidebarCollapsed && (
                          <span
                            className={`font-medium ml-3 truncate text-sm ${
                              currentConversationId === conv.id
                                ? "text-gray-800"
                                : "text-gray-600"
                            }`}
                          >
                            {conv.title}
                          </span>
                        )}
                      </button>

                      {!isSidebarCollapsed && (
                        <button
                          onClick={(e) => handleDeleteConversation(e, conv.id)}
                          className={`m-1 p-1 relative rounded-md hover:bg-red-100 hover:text-red-600 text-gray-400 opacity-0 group-hover:opacity-100 transition-all duration-200 ${
                            currentConversationId === conv.id
                              ? "opacity-0 hover:opacity-100"
                              : ""
                          }`}
                          title="Delete chat"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  ))}

                  {conversations.length === 0 && !isSidebarCollapsed && (
                    <div className="px-4 py-4 text-sm text-gray-400 text-center italic">
                      No history yet
                    </div>
                  )}
                </>
              )}
            </div>
          </nav>

          <div className="absolute bottom-4 left-4 right-4">
            {!isSidebarCollapsed && (
              <div className="flex items-center space-x-3 mb-2">
                {user?.imageUrl && (
                  <img
                    src={user.imageUrl}
                    alt="Profile"
                    className="w-8 h-8 rounded-full border border-gray-200"
                  />
                )}
                <div className="flex flex-col overflow-hidden">
                  <p className="text-sm font-medium text-gray-700 truncate">
                    {user?.fullName || user?.firstName || "User"}
                  </p>
                  <p className="text-xs text-gray-500 truncate">
                    {user?.primaryEmailAddress?.emailAddress}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Overlay for mobile */}
        {isSidebarOpen && (
          <div
            className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
            onClick={toggleSidebar}
          ></div>
        )}

        {/* Main Content */}
        <div className="flex-1 flex flex-col h-screen overflow-hidden">
          <main className="flex-1 flex flex-col bg-white rounded-3xl m-3 shadow-lg relative overflow-y-auto no-scrollbar">
            <div className="absolute shadow-xl rounded-b-xl left-1/2 -translate-x-1/2 z-10">
              <div className="h-8 w-32 bg-gray-200 rounded-b-xl" />
            </div>

            {/* Chat Interface */}
            <div className="flex-1 flex flex-col relative bg-white">
              {/* Chat History */}
              {/* Added overflow-y-auto and styled scrollbar to ensure scrollability */}
              <div className="flex-1 overflow-y-auto overflow-x-hidden p-6 space-y-4 pb-48 scroll-smooth custom-scrollbar">
                {messages.length === 0 && !isLoading && (
                  <div className="text-center  mt-20">
                    <h1 className="text-4xl font-semibold font-funnel text-gray-800 mb-4">
                      Create With Madio
                    </h1>
                    <p className="text-gray-600 font-funnel">
                      Enter your prompt below to generate a Manim animation.
                    </p>
                  </div>
                )}

                {/* Loading Skeleton for Conversation History */}
                {isLoading && messages.length === 0 && (
                  <div className="space-y-6 pt-10">
                    {[1, 2].map((i) => (
                      <div key={i} className="space-y-6">
                        <div className="flex justify-end">
                          <div className="max-w-[80%] bg-blue-50/50 w-64 h-16 rounded-2xl rounded-br-none p-4 animate-pulse" />
                        </div>
                        <div className="flex justify-start">
                          <div className="max-w-[90%] w-full space-y-3">
                            <div className="bg-gray-50 w-full h-32 rounded-2xl rounded-bl-none animate-pulse" />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {messages.map((msg, idx) => (
                  <ChatMessage
                    key={idx}
                    msg={msg}
                    isLast={idx === messages.length - 1}
                    isLoading={isLoading}
                    statusDisplay={getStatusDisplay()}
                  />
                ))}
                <div ref={bottomRef} />
              </div>

              {/* Input Area */}
              <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-white via-white to-transparent">
                <PlaceholdersAndVanishInput
                  placeholders={placeholders}
                  onChange={handleChange}
                  onSubmit={onSubmit}
                  value={inputValue}
                  setValue={setInputValue}
                />

                {/* Example Prompts (Static for now, could be dynamic) */}
                <div className="mt-4 flex gap-4 max-w-4xl mx-auto overflow-x-auto pb-2 scrollbar-none">
                  <div className="flex gap-2 shrink-0">
                    <span className="text-xs text-gray-500 py-1.5 self-center">
                      Try:
                    </span>
                    {placeholders.slice(0, 3).map((p, i) => (
                      <button
                        key={i}
                        onClick={() => handlePromptClick(p)}
                        className="text-xs border border-gray-200 hover:border-gray-300 text-gray-600 px-3 py-1.5 rounded-full transition-colors whitespace-nowrap"
                      >
                        {p}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </main>
        </div>
      </div>

      <ApiKeyDialog
        isOpen={showApiKeyDialog}
        onClose={() => setShowApiKeyDialog(false)}
        onSubmit={(key) => {
          setApiKey(key);
          toast.success("API Key saved! Please retry generation.");
        }}
      />
    </div>
  );
}

export default Create;
