import { SignedIn, SignedOut, SignIn, UserButton, useUser } from "@clerk/clerk-react";
import { PlaceholdersAndVanishInput } from "../components/ui/placeholders-and-vanish-input";
import { useState } from "react";
import {  X,  ChevronRight, SidebarClose, SidebarIcon } from "lucide-react";

function Create() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const {user} = useUser();
  console.log(user);

  const placeholders = [
    "What's the first rule of Fight Club?",
    "Who is Tyler Durden?",
    "Where is Andrew Laeddis Hiding?",
    "Write a Javascript method to reverse a string",
    "How to assemble your own PC?",
  ];

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log(e.target.value);
  };

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    console.log("submitted");
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
      <SignedIn>
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
               <div className='font-funnel flex items-center gap-2 m-4 cursor-pointer '>
                  <div className='w-3 h-3 bg-black border rounded-full translate-y-0.5 '></div>
                  <h1 className='text-xl font-medium'>Madio</h1>
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
           
            <div className="absolute bottom-3 left-4"><UserButton/> 
            
                <p>Welcome, {user?.username}</p>
              
           
            
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
          <div className="flex-1 flex flex-col">
            {/* Header */}
           

            {/* Content Area */}
            <main className="flex-1 flex items-center justify-center bg-white rounded-3xl  m-3  p-6 shadow-lg ">
              <div className="absolute top-3 left-1/2"> 
                <div className="h-10 w-48 bg-gray-50 border-b border-1px border-gray-200 rounded-b-full -z-50 rounded-l-xl rounded-r-xl "/>
              </div>
              <div>
                <h1 className="text-6xl  font-semibold font-funnel text-gray-800 mb-4">Create With Madio</h1>
                <p className="text-gray-600 font-funnel mb-6 ml-2">
                  Enter your prompt below to generate a Manim animation.
                </p>
              </div>
               <div className="absolute bottom-24  right-1/4">
            <div className="w-full ">
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
      </SignedIn>

      <SignedOut>
        <div className="bg-gray-50 min-h-screen flex items-center justify-center">
          <div className="bg-white p-8 rounded-2xl shadow-lg">
            <SignIn />
          </div>
        </div>
      </SignedOut>
    </div>
  );
}

export default Create;