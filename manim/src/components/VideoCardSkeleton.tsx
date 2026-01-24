import { Skeleton } from "./ui/skeleton";

export function VideoCardSkeleton() {
  return (
    <div className="bg-white rounded-xl overflow-hidden border border-stone-100 shadow-sm">
      <div className="aspect-video w-full bg-stone-100">
        <Skeleton className="w-full h-full" />
      </div>

      <div className="p-4 space-y-3">
        {/* Title skeleton */}
        <Skeleton className="h-5 w-3/4" />
        
        <div className="flex justify-between items-end pt-2">
          {/* Date skeleton */}
          <Skeleton className="h-3 w-1/3" />
          
          {/* Status badge skeleton */}
          <Skeleton className="h-5 w-16 rounded-full" />
        </div>
      </div>
    </div>
  );
}
