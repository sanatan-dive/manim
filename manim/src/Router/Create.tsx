import { PlaceholdersAndVanishInput } from "../components/ui/placeholders-and-vanish-input";
import { useState, useRef, useEffect } from "react";
import {
  X,
  ChevronRight,
  SidebarClose,
  SidebarIcon,
  CheckCircle2,
  Circle,
  Loader2,
} from "lucide-react";
import { useGenerationStore } from "../store/useGenerationStore";

function Create() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  const { messages, isLoading, status, generateAnimation } =
    useGenerationStore();

  const bottomRef = useRef<HTMLDivElement>(null);

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

  const handleChange = (_: React.ChangeEvent<HTMLInputElement>) => {
    // console.log(e.target.value);
  };

  const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const prompt = (e.target as any).querySelector("input").value;
    if (!prompt) return;

    await generateAnimation(prompt);
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

  const getStatusDisplay = () => {
    if (status === "idle" || status === "completed" || status === "failed")
      return null;

    const steps = [
      { id: "generating_code", label: "Generating Code" },
      { id: "rendering", label: "Rendering Animation" },
    ];

    // Map status to active step index
    let activeIndex = -1;
    if (status === "generating_code") activeIndex = 0;
    if (status === "rendering") activeIndex = 1;
    if (status === "pending") activeIndex = 0; // Show first step as loading

    return (
      <div className="flex items-center justify-center space-x-4 py-2 bg-gray-50 rounded-lg max-w-sm mx-auto mt-2">
        {steps.map((step, idx) => (
          <div key={step.id} className="flex items-center space-x-2">
            {idx < activeIndex ? (
              <CheckCircle2 className="w-5 h-5 text-green-500" />
            ) : idx === activeIndex ? (
              <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
            ) : (
              <Circle className="w-5 h-5 text-gray-300" />
            )}
            <span
              className={`text-sm ${
                idx === activeIndex
                  ? "font-bold text-blue-600"
                  : "text-gray-500"
              }`}
            >
              {step.label}
            </span>
            {idx < steps.length - 1 && (
              <div className="w-8 h-px bg-gray-300 mx-2" />
            )}
          </div>
        ))}
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
              <div className="flex-1 overflow-y-auto p-6 space-y-4 pb-32 scroll-smooth">
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
                          {idx === messages.length - 1 &&
                            isLoading &&
                            getStatusDisplay()}
                        </div>
                      ) : (
                        msg.content
                      )}
                    </div>
                  </div>
                ))}
                <div ref={bottomRef} />
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
