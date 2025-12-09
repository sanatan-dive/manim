import { PlaceholdersAndVanishInput } from "../components/ui/placeholders-and-vanish-input";
import { useState } from "react";
import { X, ChevronRight, SidebarClose, SidebarIcon } from "lucide-react";

function Create() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<
    { role: "user" | "assistant"; content: string; videoUrl?: string }[]
  >([]);

  const placeholders = [
    "Create a circle that transforms into a square",
    "Animate a bouncing ball with physics",
    "Show a sine wave animation",
    "Create a rotating cube in 3D",
    "Animate text that fades in and moves",
  ];

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log(e.target.value);
  };

  const pollJobStatus = async (jobId: string): Promise<void> => {
    const maxAttempts = 60; // Poll for up to 5 minutes (60 * 5 seconds)
    let attempts = 0;

    const poll = async () => {
      try {
        const response = await fetch(`http://localhost:8000/status/${jobId}`);
        const job = await response.json();

        console.log(`[Poll] Job ${jobId} status: ${job.status}`);

        if (job.status === "completed") {
          // Success!
          const videoUrl = `http://localhost:8000${job.video_url}`;
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: "Here is your animation!",
              videoUrl,
            },
          ]);
          setIsLoading(false);
          return;
        } else if (job.status === "failed") {
          // Failed
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: `Generation failed: ${
                job.error_message || "Unknown error"
              }`,
            },
          ]);
          setIsLoading(false);
          return;
        } else {
          // Still processing (pending, generating_code, rendering)
          attempts++;
          if (attempts >= maxAttempts) {
            setMessages((prev) => [
              ...prev,
              {
                role: "assistant",
                content: "Generation timed out. Please try again.",
              },
            ]);
            setIsLoading(false);
            return;
          }

          // Poll again after 5 seconds
          setTimeout(poll, 5000);
        }
      } catch (error) {
        console.error("Error polling job status:", error);
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "Error checking job status. Please try again.",
          },
        ]);
        setIsLoading(false);
      }
    };

    // Start polling
    poll();
  };

  const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const prompt = (e.target as any).querySelector("input").value;
    if (!prompt) return;

    setMessages((prev) => [...prev, { role: "user", content: prompt }]);
    setIsLoading(true);

    try {
      // Submit the job
      const response = await fetch("http://localhost:8000/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: prompt,
        }),
      });

      const data = await response.json();

      if (response.ok && data.job_id) {
        // Job created successfully, show status message
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "Generating your animation... This may take a minute.",
          },
        ]);

        // Start polling for status
        pollJobStatus(data.job_id);
      } else {
        console.error("Failed to create job:", data);
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: `Failed to start generation: ${
              data.detail || data.message || "Unknown error"
            }`,
          },
        ]);
        setIsLoading(false);
      }
    } catch (error: any) {
      console.error("Error calling backend:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Error connecting to server. Please try again.",
        },
      ]);
      setIsLoading(false);
    }
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const toggleSidebarCollapse = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
  };

  const sidebarItems = [
    {
      label: "Chat 1: Bouncing Ball",
      href: "#chat1",
    },
    {
      label: "Chat 2: Sine Wave",
      href: "#chat2",
    },
    {
      label: "Chat 3: Animated Flag",
      href: "#chat3",
    },
    {
      label: "Chat 4: Math Equation",
      href: "#chat4",
    },
  ];

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
              <div className="font-funnel flex items-center gap-2 m-4 cursor-pointer ">
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

          <nav className="mt-6 px-4">
            <ul className="space-y-2">
              {sidebarItems.map((item, index) => (
                <li key={index}>
                  <a
                    href={item.href}
                    className="flex items-center px-4 py-3 text-gray-700 rounded-xl hover:bg-gray-100 transition-colors duration-200 group"
                    title={isSidebarCollapsed ? item.label : ""}
                  >
                    <ChevronRight className="w-5 h-5 text-gray-500 group-hover:text-gray-700 flex-shrink-0" />
                    {!isSidebarCollapsed && (
                      <span className="font-medium ml-3">{item.label}</span>
                    )}
                  </a>
                </li>
              ))}
            </ul>
          </nav>

          <div className="absolute bottom-3 left-4">
            <p>Welcome, Guest</p>
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
          <main className="flex-1 flex flex-col bg-white rounded-3xl m-3 shadow-lg relative overflow-hidden">
            <div className="absolute shadow-xl rounded-b-xl left-1/2 -translate-x-1/2 z-10">
              <div className="h-8 w-32 bg-gray-200 rounded-b-xl" />
            </div>

            {/* Chat Interface */}
            <div className="flex-1 flex flex-col relative bg-white">
              {/* Chat History */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4 pb-32">
                {messages.length === 0 && (
                  <div className="text-center  mt-20">
                    <h1 className="text-4xl font-semibold font-funnel text-gray-800 mb-4">
                      Create With Madio
                    </h1>
                    <p className="text-gray-600 font-funnel">
                      Enter your prompt below to generate a Manim animation.
                    </p>
                  </div>
                )}

                {messages.map((msg, idx) => (
                  <div
                    key={idx}
                    className={`flex ${
                      msg.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-[80%] ${
                        msg.role === "user"
                          ? "bg-blue-600 text-white rounded-2xl rounded-br-none p-4"
                          : ""
                      }`}
                    >
                      {msg.role === "assistant" && msg.videoUrl ? (
                        <div className="space-y-3">
                          <div className="bg-gray-100 text-gray-800 rounded-2xl rounded-bl-none p-3">
                            {msg.content}
                          </div>
                          <div className="w-full bg-black rounded-xl overflow-hidden shadow-2xl">
                            <video
                              src={msg.videoUrl}
                              controls
                              autoPlay
                              className="w-full h-full object-contain"
                            />
                          </div>
                        </div>
                      ) : msg.role === "assistant" ? (
                        <div className="bg-gray-100 text-gray-800 rounded-2xl rounded-bl-none p-4">
                          {msg.content}
                        </div>
                      ) : (
                        msg.content
                      )}
                    </div>
                  </div>
                ))}

                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 p-4 rounded-2xl rounded-bl-none flex items-center space-x-2">
                      <div
                        className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                        style={{ animationDelay: "0ms" }}
                      />
                      <div
                        className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                        style={{ animationDelay: "150ms" }}
                      />
                      <div
                        className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                        style={{ animationDelay: "300ms" }}
                      />
                    </div>
                  </div>
                )}
              </div>

              {/* Input Area */}
              <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-white via-white to-transparent">
                <PlaceholdersAndVanishInput
                  placeholders={placeholders}
                  onChange={handleChange}
                  onSubmit={onSubmit}
                />
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}

export default Create;
