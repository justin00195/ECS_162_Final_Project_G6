import { writable } from 'svelte/store';

export type Announcement = {
  id: number;
  content: string;
  created_by: string;
  created_at: string;
};

export const announcements = writable<Announcement[]>([]);
export const announcementsLoading = writable(false);
export const announcementsError = writable<string | null>(null);

export async function fetchAnnouncements() {
  announcementsLoading.set(true);
  announcementsError.set(null);
  try {
    const res = await fetch('http://localhost:8000/announcements', {
      credentials: 'include',
    });
    if (!res.ok) throw new Error('Failed to fetch announcements');
    const data = await res.json();
    announcements.set(data);
  } catch (err: any) {
    announcementsError.set(err.message || 'Error fetching announcements');
  } finally {
    announcementsLoading.set(false);
  }
}

export async function postAnnouncement(content: string) {
  announcementsLoading.set(true);
  announcementsError.set(null);
  try {
    const res = await fetch('http://localhost:8000/announcements', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ content })
    });
    if (!res.ok) throw new Error('Failed to post announcement');
    const newAnnouncement = await res.json();
    announcements.update(list => [newAnnouncement, ...list]);
  } catch (err: any) {
    announcementsError.set(err.message || 'Error posting announcement');
  } finally {
    announcementsLoading.set(false);
  }
}

export async function deleteAnnouncement(id: number) {
  announcementsLoading.set(true);
  announcementsError.set(null);
  try {
    const res = await fetch(`http://localhost:8000/announcements/${id}`, {
      method: 'DELETE',
      credentials: 'include',
    });
    if (!res.ok) throw new Error('Failed to delete announcement');
    announcements.update(list => list.filter(a => a.id !== id));
  } catch (err: any) {
    announcementsError.set(err.message || 'Error deleting announcement');
  } finally {
    announcementsLoading.set(false);
  }
} 