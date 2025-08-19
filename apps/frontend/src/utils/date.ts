// Date utility functions for TaskWarrior frontend
import { format, formatDistanceToNow, parseISO, isValid } from 'date-fns';

export function formatTaskDate(dateString?: string): string {
  if (!dateString) return '';
  
  const date = parseISO(dateString);
  if (!isValid(date)) return dateString;
  
  return format(date, 'MMM dd, yyyy HH:mm');
}

export function formatRelativeDate(dateString?: string): string {
  if (!dateString) return '';
  
  const date = parseISO(dateString);
  if (!isValid(date)) return dateString;
  
  return formatDistanceToNow(date, { addSuffix: true });
}

export function formatDueDate(dateString?: string): {
  formatted: string;
  relative: string;
  isOverdue: boolean;
} {
  if (!dateString) {
    return { formatted: '', relative: '', isOverdue: false };
  }
  
  const date = parseISO(dateString);
  if (!isValid(date)) {
    return { formatted: dateString, relative: '', isOverdue: false };
  }
  
  const now = new Date();
  const isOverdue = date < now;
  
  return {
    formatted: format(date, 'MMM dd, yyyy HH:mm'),
    relative: formatDistanceToNow(date, { addSuffix: true }),
    isOverdue,
  };
}

export function formatDateForInput(dateString?: string): string {
  if (!dateString) return '';
  
  const date = parseISO(dateString);
  if (!isValid(date)) return '';
  
  return format(date, "yyyy-MM-dd'T'HH:mm");
}

export function formatDateForAPI(dateString: string): string {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  if (!isValid(date)) return dateString;
  
  return date.toISOString();
}

export function isDateOverdue(dateString?: string): boolean {
  if (!dateString) return false;
  
  const date = parseISO(dateString);
  if (!isValid(date)) return false;
  
  return date < new Date();
}

export function getDaysUntilDue(dateString?: string): number {
  if (!dateString) return 0;
  
  const date = parseISO(dateString);
  if (!isValid(date)) return 0;
  
  const now = new Date();
  const diffTime = date.getTime() - now.getTime();
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}