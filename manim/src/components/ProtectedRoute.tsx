import { useUser } from '@clerk/clerk-react';
import { Navigate } from 'react-router-dom';
import React from 'react';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isSignedIn, isLoaded } = useUser();

  if (!isLoaded) return null; // or a loading spinner

  // If not signed in, redirect to home
  if (!isSignedIn) {
    return <Navigate to="/" replace />;
  }

  // If signed in, render children (e.g., dashboard)
  return <>{children}</>;
};

export default ProtectedRoute;
