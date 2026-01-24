import { Link } from "react-router-dom";
import { MoveLeft } from "lucide-react";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-black text-white flex flex-col items-center justify-center p-4">
      <h1 className="text-9xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-500 to-purple-500">
        404
      </h1>
      <h2 className="text-2xl font-semibold mt-4 mb-8">Page Not Found</h2>
      <p className="text-gray-400 mb-8 text-center max-w-md">
        The page you are looking for doesn't exist or has been moved.
      </p>
      <Link
        to="/"
        className="flex items-center gap-2 px-6 py-3 bg-white text-black rounded-full font-medium hover:bg-gray-200 transition-colors"
      >
        <MoveLeft className="w-4 h-4" />
        Back to Home
      </Link>
    </div>
  );
}
