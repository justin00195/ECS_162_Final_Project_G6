import { writable } from 'svelte/store';

export const isLoggedIn = writable(false);
export const userInfo = writable({});
export const loading = writable(true);

export async function checkAuth() {
  loading.set(true);
  try {
    const res = await fetch('http://localhost:8000/auth/user', {
      credentials: 'include'
    });
    const data = await res.json();

    if (res.status === 200) {
      isLoggedIn.set(true);
      userInfo.set(data);
    } else {
      isLoggedIn.set(false);
    }
  } catch (err) {
    console.error('Auth check failed:', err);
    isLoggedIn.set(false);
  } finally {
    loading.set(false);
  }
}