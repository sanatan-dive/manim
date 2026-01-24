import { Skeleton } from "./ui/skeleton";
import { VideoCardSkeleton } from "./VideoCardSkeleton";


export function ProfileSkeleton() {
  return (
    <div className="min-h-screen bg-gray-50 p-8 pt-24 transition-colors duration-300">
  
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Profile Info Skeleton */}
        <div className="flex items-center gap-4">
          <Skeleton className="w-20 h-20 rounded-full" />
          <div className="space-y-2">
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-4 w-64" />
          </div>
        </div>

        {/* Stats Skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-1 gap-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col items-center justify-center space-y-2 h-[140px]">
            <Skeleton className="h-6 w-6 rounded-full" />
            <Skeleton className="h-8 w-16" />
            <Skeleton className="h-4 w-32" />
          </div>
        </div>

        {/* Animations Skeleton */}
        <div>
          <Skeleton className="h-8 w-48 mb-6" />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[...Array(4)].map((_, i) => (
              <VideoCardSkeleton key={i} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
