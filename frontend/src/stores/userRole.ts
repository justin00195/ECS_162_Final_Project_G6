import { writable } from 'svelte/store';

export const userRole = writable<string | null>(null);
export const userRoleLoading = writable(false);
export const userRoleError = writable<string | null>(null);

export async function fetchUserRole() {
  userRoleLoading.set(true);
  userRoleError.set(null);
  try {
    const res = await fetch('http://localhost:8000/auth/user', {
      credentials: 'include',
    });
    const data = await res.json();
    if (res.ok && data && (data.role || (data.user && data.user.role))) {
      userRole.set(data.role || (data.user && data.user.role));
    } else {
      userRole.set(null);
    }
  } catch (err: any) {
    userRoleError.set(err.message || 'Error fetching user role');
    userRole.set(null);
  } finally {
    userRoleLoading.set(false);
  }
} 