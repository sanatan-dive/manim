import { useAuth, useUser } from "@clerk/clerk-react";
import { useEffect, useState } from "react";
import { Activity, Trash2, Download } from "lucide-react";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import { VideoCardSkeleton } from "../components/VideoCardSkeleton";
import { ProfileSkeleton } from "../components/ProfileSkeleton";

interface Job {
  id: string;
  prompt: string;
  title?: string;
  status: string;
  created_at: string;
  duration?: number;
  output_url?: string;
}

interface JobsResponse {
  jobs: Job[];
  total: number;
  limit: number;
  offset: number;
}

interface UserData {
  id: string; // This is actually uuid in DB, but clerkId is separate
  clerkId: string;
  email: string;
  name: string;
  credits: number;
  generationCount: number;
  plan: string;
}

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function Profile() {
  const { getToken, isLoaded: authLoaded } = useAuth();
  const { user, isLoaded: userLoaded } = useUser();
  const [userData, setUserData] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(true);

  // Gallery State
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loadingJobs, setLoadingJobs] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const limit = 8; // Smaller limit for dashboard

  const fetchUserData = async () => {
    try {
      setLoading(true);
      const token = await getToken();
      const response = await fetch(`${API_URL}/users/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch user data");
      }

      const data = await response.json();
      setUserData(data);
    } catch (error) {
      console.error(error);
      toast.error("Failed to load profile data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (authLoaded && userLoaded && user) {
      // Sync first just in case
      const syncAndFetch = async () => {
        const token = await getToken();
        await fetch(`${API_URL}/users/sync`, {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
        });
        fetchUserData();
        fetchUserJobs();
      };
      syncAndFetch();
    }
  }, [authLoaded, userLoaded, user, page]); // Re-fetch jobs on page change

  const fetchUserJobs = async () => {
    try {
      setLoadingJobs(true);
      const token = await getToken();
      const offset = (page - 1) * limit;

      const response = await fetch(
        `${API_URL}/jobs/?limit=${limit}&offset=${offset}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        },
      );

      if (!response.ok) throw new Error("Failed to fetch jobs");

      const data: JobsResponse = await response.json();
      setJobs(data.jobs);
      setTotalPages(Math.ceil(data.total / limit));
    } catch (error) {
      console.error(error);
      // toast.error('Failed to load your history');
    } finally {
      setLoadingJobs(false);
    }
  };

  const handleDeleteVideo = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    if (!confirm("Are you sure you want to delete this animation?")) return;

    try {
      const token = await getToken();
      const response = await fetch(`${API_URL}/jobs/${id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error("Failed to delete");

      toast.success("Animation deleted");
      setJobs(jobs.filter((job) => job.id !== id));
      // Optionally refetch user stats
      fetchUserData();
    } catch (error) {
      console.error(error);
      toast.error("Could not delete animation");
    }
  };

  const handleDownload = async (
    id: string,
    prompt: string,
    e: React.MouseEvent,
  ) => {
    e.preventDefault();
    e.stopPropagation();
    try {
      const token = await getToken();
      const response = await fetch(`${API_URL}/video/stream/${id}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error("Download failed");

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `manim-${prompt.slice(0, 20).replace(/\s+/g, "-")}.mp4`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error(error);
      toast.error("Failed to download video");
    }
  };

  if (!authLoaded || !userLoaded || loading) {
    return <ProfileSkeleton />;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8 pt-24 transition-colors duration-300">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center gap-4">
          <img
            src={user?.imageUrl}
            alt={user?.fullName || "User"}
            className="w-20 h-20 rounded-full border-2 border-white shadow-md"
          />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {user?.fullName}
            </h1>
            <p className="text-gray-500">
              {user?.primaryEmailAddress?.emailAddress}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-1 gap-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col items-center justify-center space-y-2">
            <div className="p-3 bg-purple-50 rounded-full">
              <Activity className="w-6 h-6 text-purple-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {userData?.generationCount}
            </div>
            <div className="text-sm text-gray-500">Animations Generated</div>
          </div>
        </div>

        {/* My Animations Section */}
        <div>
          <h2 className="text-2xl font-bold text-stone-900 mb-6 font-funnel">
            My Animations
          </h2>
          {loadingJobs && jobs.length === 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {[...Array(4)].map((_, i) => (
                <VideoCardSkeleton key={i} />
              ))}
            </div>
          ) : jobs.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-xl border border-stone-100">
              <p className="text-stone-500">
                You haven't generated any animations yet.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <AnimatePresence>
                {jobs.map((job) => (
                  <motion.div
                    key={job.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="group bg-white rounded-lg overflow-hidden border border-stone-100 shadow-sm hover:shadow-md transition-all"
                  >
                    <div className="relative aspect-video bg-stone-900">
                      {job.status === "completed" ? (
                        <video
                          src={`${API_URL}/video/stream/${job.id}`}
                          className="w-full h-full object-cover"
                          controls
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-stone-500 text-xs">
                          {job.status}
                        </div>
                      )}

                      {/* Actions Overlay */}
                      <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2 pointer-events-none">
                        <button
                          onClick={(e) => handleDownload(job.id, job.prompt, e)}
                          className="p-2 bg-white/90 text-black rounded-full hover:bg-white pointer-events-auto"
                          title="Download"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                        <button
                          onClick={(e) => handleDeleteVideo(job.id, e)}
                          className="p-2 bg-red-500/90 text-white rounded-full hover:bg-red-600 pointer-events-auto"
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    <div className="p-3">
                      <p
                        className="text-sm font-medium truncate"
                        title={job.prompt}
                      >
                        {job.prompt}
                      </p>
                      <p className="text-xs text-stone-400 mt-1">
                        {new Date(job.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          )}

          {totalPages > 1 && (
            <div className="flex justify-center gap-2 mt-8">
              <button
                disabled={page === 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="px-3 py-1 rounded border disabled:opacity-50 text-sm"
              >
                Prev
              </button>
              <span className="text-sm py-1">
                Page {page} of {totalPages}
              </span>
              <button
                disabled={page === totalPages}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                className="px-3 py-1 rounded border disabled:opacity-50 text-sm"
              >
                Next
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
