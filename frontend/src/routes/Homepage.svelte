<script lang="ts">
  import '/src/assets/hp.scss'
  import { onMount } from 'svelte';
  import { announcements, fetchAnnouncements, postAnnouncement, deleteAnnouncement, announcementsLoading, announcementsError } from '../stores/announcements';
  import { userRole, fetchUserRole } from '../stores/userRole';
  import { get } from 'svelte/store';

  let newAnnouncement = '';
  let selectedTemplate = '';
  let posting = false;
  let error = '';

  // moderator announcement templates
  const templates = [
    { label: 'Scheduled Maintenance', text: 'Scheduled maintenance will occur tonight from 10pm to 12am.' },
    { label: 'New Feature Release', text: 'Check out our new meal planner feature, now live!' },
    { label: 'Bug Fixes', text: 'Recent bugs have been fixed. Please refresh your browser.' },
    { label: 'Custom', text: '' }
  ];

  onMount(() => {
    fetchAnnouncements();
    fetchUserRole();
  });

  $: isModerator = $userRole === 'admin';

  async function handlePost() {
    error = '';
    posting = true;
    const content = selectedTemplate && selectedTemplate !== 'Custom'
      ? templates.find(t => t.label === selectedTemplate)?.text || ''
      : newAnnouncement;
    if (!content.trim()) {
      error = 'Announcement cannot be empty.';
      posting = false;
      return;
    }
    try {
      await postAnnouncement(content);
      newAnnouncement = '';
      selectedTemplate = '';
    } catch (e) {
      error = 'Failed to post announcement.';
    } finally {
      posting = false;
    }
  }

  function handleTemplateChange(e: Event) {
    const target = e.target as HTMLSelectElement
    selectedTemplate = target.value;
    if (selectedTemplate && selectedTemplate !== 'Custom') {
      newAnnouncement = templates.find(t => t.label === selectedTemplate)?.text || '';
    } else {
      newAnnouncement = '';
    }
  }
</script>

<div class="container">
  <!-- Announcements Section -->
  <div class="announcements-section">
    <h2>Announcements</h2>
    {#if $announcementsLoading}
      <p>Loading announcements...</p>
    {:else if $announcementsError}
      <p class="error">{$announcementsError}</p>
    {:else if $announcements.length === 0}
      <p>No announcements yet.</p>
    {:else}
      <ul class="announcements-list">
        {#each $announcements as ann (ann.id)}
          <li class="announcement-item">
            <span class="announcement-content">{ann.content}</span>
            <span class="announcement-meta">{new Date(ann.created_at).toLocaleString()}</span>
            {#if isModerator}
              <button class="delete-btn" on:click={() => deleteAnnouncement(ann.id)} disabled={$announcementsLoading}>Delete</button>
            {/if}
          </li>
        {/each}
      </ul>
    {/if}

    {#if isModerator}
      <div class="announcement-manager">
        <h3>Post New Announcement</h3>
        <select on:change={handleTemplateChange} bind:value={selectedTemplate}>
          <option value="">Select a template...</option>
          {#each templates as t}
            <option value={t.label}>{t.label}</option>
          {/each}
        </select>
        <textarea
          placeholder="Write your announcement here..."
          bind:value={newAnnouncement}
          rows="3"
        ></textarea>
        <button class="post-btn" on:click={handlePost} disabled={posting || $announcementsLoading}>
          {posting ? 'Posting...' : 'Post'}
        </button>
        {#if error}
          <p class="error">{error}</p>
        {/if}
      </div>
    {/if}
  </div>

  <h1 class="welcome">Welcome to Food Tracker</h1>
  <div class="grid">
    <div class="card">
      <h3>About Us</h3>
      <p>College students struggle with healthy eating. We make it easier.</p>
    </div>
    <div class="card">
      <h3>What to Expect</h3>
      <p>Get daily, personalized meal plans based on your goals and preferences.</p>
    </div>
    <div class="card" style="flex-basis: 100%;">
      <h3>Track Your Progress</h3>
      <p>Stay motivated by tracking weight, goals, and progress over time.</p>
    </div>
  </div>
</div>

<style>

</style>