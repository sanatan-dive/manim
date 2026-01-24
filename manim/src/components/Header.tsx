import {
  SignedIn,
  SignedOut,
  SignInButton,
  UserButton,
} from "@clerk/clerk-react";
import { Link } from "react-router-dom";

function Header() {
  return (
    <div className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl border-b border-stone-100">
      <div className="flex justify-between items-center px-6 py-3 max-w-7xl mx-auto">
        <Link
          to="/"
          className="font-funnel flex items-center gap-2 cursor-pointer group"
        >
          <div className="w-5 h-5 bg-black border rounded-full group-hover:scale-110 transition-transform"></div>
          <h1 className="text-xl font-medium">Madio</h1>
        </Link>
        <div className="font-funnel flex items-center gap-6 hidden md:flex">
          <Link
            to="/create"
            className="text-sm font-medium hover:text-stone-500 duration-200"
          >
            Create
          </Link>
          <Link
            to="/gallery"
            className="text-sm font-medium hover:text-stone-500 duration-200"
          >
            Gallery
          </Link>
          <Link
            to="/dashboard"
            className="text-sm font-medium hover:text-stone-500 duration-200"
          >
            Dashboard
          </Link>
          <Link
            to="/help"
            className="text-sm font-medium hover:text-stone-500 duration-200"
          >
            Help
          </Link>
        </div>

        <div className="flex items-center gap-4">
          <SignedIn>
            <UserButton />
          </SignedIn>
          <SignedOut>
            <SignInButton mode="modal">
              <button className="bg-black text-white px-4 py-1.5 rounded-full text-sm font-medium hover:bg-stone-800 duration-200 shadow-sm hover:shadow">
                Get Started
              </button>
            </SignInButton>
          </SignedOut>
        </div>
      </div>
    </div>
  );
}

export default Header;
