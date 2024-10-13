import { formatDistanceToNow, subHours } from "date-fns";

export function PSTDate(ms: number): string {
  return subHours(new Date(ms), 7).toLocaleString("en-US", {
    timeZone: "America/Los_Angeles",
  });
}

export function PSTDateRelative(ms: number): string {
  return formatDistanceToNow(subHours(new Date(ms), 7), { addSuffix: true });
}

export function relativeDate(date: Date): string {
  return formatDistanceToNow(date, { addSuffix: true });
}