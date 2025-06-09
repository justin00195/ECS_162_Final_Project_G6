import { writable } from 'svelte/store';

export interface GoalComment {
  id: number;
  user_email: string;
  content: string;
  created_by: string;
  created_at: string;
  type: string;
  milestone: string | null;
}

export const goalComments = writable<GoalComment[]>([]);
export const goalCommentsLoading = writable(false);
export const goalCommentsError = writable<string | null>(null);

export async function fetchGoalComments(user_email: string) {
  goalCommentsLoading.set(true);
  goalCommentsError.set(null);
  try {
    const res = await fetch(`http://localhost:8000/goal-comments?user_email=${encodeURIComponent(user_email)}`, {
      credentials: 'include',
    });
    if (!res.ok) throw new Error('Failed to fetch comments');
    const data: GoalComment[] = await res.json();
    goalComments.set(data);
  } catch (err: any) {
    goalCommentsError.set(err.message || 'Error fetching comments');
    goalComments.set([]);
  } finally {
    goalCommentsLoading.set(false);
  }
}

export async function postGoalComment({ user_email, content, type = 'manual', milestone = null }: { user_email: string; content: string; type?: string; milestone?: string | null; }) {
  goalCommentsLoading.set(true);
  goalCommentsError.set(null);
  try {
    const res = await fetch('http://localhost:8000/goal-comments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ user_email, content, type, milestone }),
    });
    if (!res.ok) throw new Error('Failed to post comment');
    const data: GoalComment = await res.json();
    goalComments.update((comments) => [data, ...comments]);
  } catch (err: any) {
    goalCommentsError.set(err.message || 'Error posting comment');
  } finally {
    goalCommentsLoading.set(false);
  }
}

export async function deleteGoalComment(comment_id: number) {
  goalCommentsLoading.set(true);
  goalCommentsError.set(null);
  try {
    const res = await fetch(`http://localhost:8000/goal-comments/${comment_id}`, {
      method: 'DELETE',
      credentials: 'include',
    });
    if (!res.ok) throw new Error('Failed to delete comment');
    goalComments.update((comments) => comments.filter((c) => c.id !== comment_id));
  } catch (err: any) {
    goalCommentsError.set(err.message || 'Error deleting comment');
  } finally {
    goalCommentsLoading.set(false);
  }
} 