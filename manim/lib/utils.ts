// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
import { ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
