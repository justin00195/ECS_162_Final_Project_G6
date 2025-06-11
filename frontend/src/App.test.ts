// src/App.test.ts
import { render, fireEvent, waitFor } from '@testing-library/svelte';
import App from './App.svelte';
import { describe, it, beforeEach, afterEach, expect, vi } from 'vitest';

function mockLoggedInFetch() {
  //https://vitest.dev/api/vi.html#vi-stubglobal
  //AI help to key what is needed for mock user login + debugging
  vi.stubGlobal('fetch', (input: RequestInfo | URL) => {
    //
    if (typeof input === 'string' && input.includes('/auth/user')) {
      const body = JSON.stringify({
        email: 'testingUser@FoodTracker.com',
        username: 'user',
        userID: '1233211234567',
      });

      return Promise.resolve(
        new Response(body, {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }),
      ) as unknown as Promise<Response>;
    }
    return Promise.reject(new Error(`Unhandled fetch URL: ${input}`));
  });
}
//https://www.npmjs.com/package/vitest-fetch-mock
//debug here
beforeEach(() => {
  mockLoggedInFetch();
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('Navigation Bar button clicked', () => {
  it('goes to Calculator', async () => {
    const { findByText } = render(App);
    //user findByText not getByText because it needs to render completely first
    const calculatorLink = await findByText('Calculator');
    await fireEvent.click(calculatorLink);

    await waitFor(() => expect(window.location.hash).toBe('#/calculator'));
  });

  it('goes to Goal page', async () => {
    const { findByText } = render(App);

    const goalLink = await findByText('Goal');
    await fireEvent.click(goalLink);

    await waitFor(() => expect(window.location.hash).toBe('#/goal'));
  });

  it('goes to Meal Planner', async () => {
    const { findByText } = render(App);

    const plannerLink = await findByText('Meal Planner');
    await fireEvent.click(plannerLink);

    await waitFor(() => expect(window.location.hash).toBe('#/planner'));
  });
});
