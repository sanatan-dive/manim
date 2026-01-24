import { StrictMode, Suspense, lazy } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { ClerkProvider } from "@clerk/clerk-react";
import { Toaster } from "sonner";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./components/theme-provider";

import ProtectedRoute from "./components/ProtectedRoute";
import Header from "./components/Header";
import OfflineIndicator from "./components/OfflineIndicator";

// Lazy load components
const App = lazy(() => import("./App.tsx"));
const Create = lazy(() => import("./Router/Create.tsx"));
const Profile = lazy(() => import("./Router/Profile.tsx"));
const Gallery = lazy(() => import("./Router/Gallery.tsx"));
const Help = lazy(() => import("./Router/Help.tsx"));
const NotFound = lazy(() => import("./Router/NotFound.tsx"));

// Loading component
const PageLoader = () => (
  <div className="flex items-center justify-center min-h-screen bg-black text-white">
    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-white"></div>
  </div>
);

const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

if (!PUBLISHABLE_KEY) {
  throw new Error("Add your Clerk Publishable Key to the .env file");
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ErrorBoundary>
      <ClerkProvider publishableKey={PUBLISHABLE_KEY}>
        <ThemeProvider defaultTheme="light" storageKey="vite-ui-theme">
          <Toaster position="top-center" richColors />
          <OfflineIndicator />
          <BrowserRouter>
            <Suspense fallback={<PageLoader />}>
              <Routes>
                <Route path="/" element={<App />} />
                <Route path="/help" element={<Help />} />
                <Route
                  path="/create"
                  element={
                    <ProtectedRoute>
                      <Create />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/gallery"
                  element={
                    <ProtectedRoute>
                      <div className="relative">
                        <Header />
                        <Gallery />
                      </div>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/dashboard"
                  element={
                    <ProtectedRoute>
                      <div className="relative">
                        <Header />
                        <Profile />
                      </div>
                    </ProtectedRoute>
                  }
                />
                <Route path="*" element={<NotFound />} />
              </Routes>
            </Suspense>
          </BrowserRouter>
        </ThemeProvider>
      </ClerkProvider>
    </ErrorBoundary>
  </StrictMode>,
);
