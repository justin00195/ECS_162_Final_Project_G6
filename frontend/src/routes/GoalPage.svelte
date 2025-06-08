<script lang="ts">
  import { onMount } from 'svelte';
  import { calAdjust } from '../stores/calAdjust';
  import '../assets/goal.scss';
  import { userRole, fetchUserRole } from '../stores/userRole';
  import {
    goalComments,
    goalCommentsLoading,
    goalCommentsError,
    fetchGoalComments,
    postGoalComment,
    deleteGoalComment,
    type GoalComment
  } from '../stores/goalComments';
  import { get } from 'svelte/store';

  let currentWeight = 0;
  let startingWeight = 0;
  let latestWeight = 0;
  let targetWeight = 0;
  let duration = 0;
  let goalStartDate = new Date().toISOString().slice(0, 10);
  let calorieAdjust = 0;
  let message = '';
  let error = '';
  let hasExistingGoal = false;
  let showDeleteConfirmation = false;
  let showDurationTooltip = false;
  let showCalorieTooltip = false;

  let savedStartingWeight = 0;
  let savedLatestWeight = 0;
  let savedTargetWeight = 0;
  let savedDuration = 0;
  let savedStartDate = '';

  let goalType: 'lose' | 'maintain' | 'gain' = 'maintain';
  $: goalLabel =
    goalType === 'lose'
      ? 'Lose Weight'
      : goalType === 'gain'
      ? 'Gain Weight'
      : 'Maintain Weight';

  const clamp = (v: number) => Math.min(Math.max(v, 0), 1);

  let userEmail = '';
  let newComment = '';
  let selectedTemplate = '';
  let milestoneCommented: Record<string, boolean> = {
    '25': false,
    '50': false,
    '75': false,
    '100': false
  };

  const templates = [
    'Great job reaching your goal milestone!',
    'Keep up the good work!',
    'Remember to stay consistent!',
    'If you need help, reach out to the community or a moderator.'
  ];

  let userList: { email: string; name: string }[] = [];
  let selectedUserEmail = '';

  onMount(async () => {
    try {
      const savedMessage = localStorage.getItem('goalMessage');
      const savedCalorieAdjust = localStorage.getItem('calorieAdjust');
      if (savedMessage) message = savedMessage;
      if (savedCalorieAdjust) calorieAdjust = parseInt(savedCalorieAdjust);

      const profileRes = await fetch('http://localhost:8000/user/profile', {
        method: 'GET',
        credentials: 'include'
      });
      const profileData = await profileRes.json();
      if (!profileRes.ok) throw new Error(profileData.error || 'error fetching profile');

      currentWeight = profileData.weight;
      startingWeight = currentWeight;
      latestWeight = startingWeight;
      userEmail = profileData.email;

      await fetchUserRole();

      if (get(userRole) === 'admin') {
        const usersRes = await fetch('http://localhost:8000/users/list', { credentials: 'include' });
        userList = await usersRes.json();
        if (userList.length > 0) {
          selectedUserEmail = userList[0].email;
        }
        await fetchGoalAndComments(selectedUserEmail);
      } else {
        selectedUserEmail = userEmail;
        await fetchGoalAndComments(userEmail);
      }
    } catch (err: any) {
      error = err.message || 'error loading goal';
    }
  });

  async function fetchGoalAndComments(email: string) {
    // Fetch goal
    const goalRes = await fetch(`http://localhost:8000/goal`, {
      method: 'GET',
      credentials: 'include'
    });
    const goalData = await goalRes.json();
    hasExistingGoal = goalRes.ok;
    if (hasExistingGoal) {
      goalType = goalData.goal_type;
      targetWeight = goalData.target_weight;
      duration = goalData.duration_days;
      goalStartDate = goalData.start_date;
      startingWeight = goalData.starting_weight;
      latestWeight = goalData.latest_weight;
      savedStartingWeight = startingWeight;
      savedLatestWeight = latestWeight;
      savedTargetWeight = targetWeight;
      savedDuration = duration;
      savedStartDate = goalStartDate;
    }
    // Fetch comments regardless of goal
    await fetchGoalComments(email);
  }

  const setGoal = async () => {
    if (!startingWeight || !targetWeight || !duration) {
      error = 'Please fill in all fields before submitting.';
      return;
    }
    error = '';
    try {
      const res = await fetch('http://localhost:8000/goal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          goal_type: goalType,
          target_weight: targetWeight,
          duration_days: duration,
          start_date: goalStartDate,
          starting_weight: startingWeight,
          latest_weight: latestWeight
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'error setting goal');

      const wasFirstGoal = !hasExistingGoal;
      hasExistingGoal = true;
      calorieAdjust = data.calories_sug;
      calAdjust.set(data.calories_sug);
      message = data.message;

      localStorage.setItem('goalMessage', message);
      localStorage.setItem('calorieAdjust', calorieAdjust.toString());

      savedStartingWeight = startingWeight;
      savedLatestWeight = latestWeight;
      savedTargetWeight = targetWeight;
      savedDuration = duration;
      savedStartDate = goalStartDate;

      const userProfileRes = await fetch('http://localhost:8000/user/profile', {
        method: 'GET',
        credentials: 'include'
      });
      const userProfile = await userProfileRes.json();
      userProfile.weight = wasFirstGoal ? startingWeight : latestWeight;

      await fetch('http://localhost:8000/user/profile', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userProfile)
      });
    } catch (err: any) {
      error = err.message || 'network error';
    }
  };

  const confirmDelete = () => (showDeleteConfirmation = true);
  const cancelDelete = () => (showDeleteConfirmation = false);

  const deleteGoal = async () => {
    try {
      const res = await fetch('http://localhost:8000/goal', {
        method: 'DELETE',
        credentials: 'include'
      });
      if (!res.ok) throw new Error('Failed to delete goal');

      hasExistingGoal = false;
      goalType = 'maintain';
      targetWeight = 0;
      duration = 0;
      goalStartDate = new Date().toISOString().slice(0, 10);
      startingWeight = currentWeight;
      latestWeight = currentWeight;
      calorieAdjust = 0;
      calAdjust.set(0);
      message = '';

      localStorage.removeItem('goalMessage');
      localStorage.removeItem('calorieAdjust');

      savedStartingWeight = 0;
      savedLatestWeight = 0;
      savedTargetWeight = 0;
      savedDuration = 0;
      savedStartDate = '';
      showDeleteConfirmation = false;
    } catch (err: any) {
      error = err.message || 'Failed to delete goal';
    }
  };

  $: goalType =
    targetWeight < startingWeight
      ? 'lose'
      : targetWeight > startingWeight
      ? 'gain'
      : 'maintain';

  $: weightProgress = hasExistingGoal
    ? clamp(
        (savedStartingWeight - savedLatestWeight) /
          (savedStartingWeight - savedTargetWeight)
      )
    : 0;

  $: timeProgress = hasExistingGoal
    ? clamp(
        (Date.now() - new Date(savedStartDate).getTime()) /
          (savedDuration * 24 * 60 * 60 * 1000)
      )
    : 0;

  $: if (!hasExistingGoal) latestWeight = startingWeight;
  $: if (get(userRole) === 'admin' && selectedUserEmail) {
    fetchGoalAndComments(selectedUserEmail);
  }

  function handleTemplateClick(template: string) {
    selectedTemplate = template;
    newComment = template;
  }

  async function handleAddComment() {
    if (!newComment.trim()) return;
    await postGoalComment({ user_email: selectedUserEmail, content: newComment });
    newComment = '';
    selectedTemplate = '';
  }

  async function handleDeleteComment(id: number) {
    await deleteGoalComment(id);
  }

  /* Commenting out automatic milestone notifications for now
  $: if (hasExistingGoal && get(userRole) === 'admin') {
    const milestones = [25, 50, 75, 100];
    milestones.forEach(async (milestone) => {
      const progress = Math.round(weightProgress * 100);
      if (progress >= milestone && !milestoneCommented[milestone]) {
        const exists = get(goalComments).some(
          (c: GoalComment) => c.milestone == milestone
        );
        if (!exists) {
          await postGoalComment({
            user_email: selectedUserEmail,
            content: `🎉 User reached ${milestone}% of their weight goal!`,
            type: 'milestone',
            milestone
          });
          milestoneCommented[milestone] = true;
        }
      }
    });
  }
  */
</script>

{#if $userRole === 'admin'}
  <div class="card mod-notes-card">
    <h2>Admin: Leave Notes for Any User</h2>

    <div class="user-select">
      <label for="mod-user-dropdown">Select User:</label>
      <select
        id="mod-user-dropdown"
        bind:value={selectedUserEmail}
        on:change={() => fetchGoalAndComments(selectedUserEmail)}
      >
        {#each userList as user}
          <option value={user.email}>
            {user.name} ({user.email})
          </option>
        {/each}
      </select>
    </div>

    <div class="comments-section">
      <h3>Admin Notes for {selectedUserEmail}</h3>

      {#if $goalCommentsLoading}
        <p>Loading notes…</p>
      {:else if $goalCommentsError}
        <p class="error-message">{$goalCommentsError}</p>
      {:else if $goalComments.length === 0}
        <p>No notes yet.</p>
      {/if}

      <ul>
        {#each $goalComments as comment (comment.id)}
          <li>
            <div class="comment-content">{comment.content}</div>
            <div class="comment-meta">
              <span>
                {comment.created_by} |
                {new Date(comment.created_at).toLocaleString()}
              </span>
              <button
                class="delete-comment"
                on:click={() => handleDeleteComment(comment.id)}
              >
                Delete
              </button>
              {#if comment.milestone}
                <span class="milestone-badge">
                  🏅 {comment.milestone}% milestone
                </span>
              {/if}
            </div>
          </li>
        {/each}
      </ul>

      <div class="add-comment">
        <textarea
          bind:value={newComment}
          placeholder="Write a note or pick a template…"
        ></textarea>

        <div class="template-buttons">
          {#each templates as template}
            <button
              type="button"
              class:active={selectedTemplate === template}
              on:click={() => handleTemplateClick(template)}
            >
              {template}
            </button>
          {/each}
        </div>

        <button
          class="primary-button"
          on:click={handleAddComment}
          disabled={!newComment.trim()}
        >
          Add Note
        </button>
      </div>
    </div>
  </div>
{/if}

<h1>Set Your Weight Goal</h1>
{#if error}
  <p class="error-message">{error}</p>
{/if}

<div class="flex-container">
  <!-- LEFT COLUMN -->
  <div class="card left-column">
    {#if !hasExistingGoal}
<label>
  Starting Weight (kg):
  <input type="number" bind:value={startingWeight} />
</label>
    {:else}
      <div class="saved-value">
        <span class="label">Starting Weight:</span>
        <span class="value">{startingWeight} kg</span>
      </div>
    {/if}

    {#if hasExistingGoal}
<label>
  Latest Weight (kg):
  <input type="number" bind:value={latestWeight} />
</label>
    {/if}

<label>
  Target Weight (kg):
  <input type="number" bind:value={targetWeight} />
</label>

    <div class="input-with-tooltip">
<label>
  Duration (days):
  <input type="number" bind:value={duration} />
</label>
      <button
        class="info-button"
        on:click={() => (showDurationTooltip = !showDurationTooltip)}
        on:blur={() => (showDurationTooltip = false)}
      >
        ℹ️
      </button>
      {#if showDurationTooltip}
        <div class="tooltip">
          How many days until you reach your target weight?
        </div>
      {/if}
    </div>

    {#if !hasExistingGoal}
<label>
  Goal Start Date:
  <input type="date" bind:value={goalStartDate} />
</label>
    {:else}
      <div class="saved-value">
        <span class="label">Start Date:</span>
        <span class="value">📅 {goalStartDate}</span>
      </div>
    {/if}

    <div class="button-group">
      <button class="primary-button" on:click={setGoal}>
        {hasExistingGoal ? 'Update' : 'Submit'}
      </button>
      {#if hasExistingGoal}
        <button class="delete-button" on:click={confirmDelete}>
          Delete
        </button>
      {/if}
    </div>

    {#if showDeleteConfirmation}
      <div class="confirmation-popup">
        <p>Are you sure you want to delete your goal?</p>
        <div class="confirmation-buttons">
          <button class="delete-button" on:click={deleteGoal}>Yes</button>
          <button class="cancel-button" on:click={cancelDelete}>Cancel</button>
        </div>
      </div>
    {/if}
  </div>

  <!-- RIGHT COLUMN -->
  <div class="card right-column">
{#if message}
      <div class="notification">
        <span class="checkmark">✅</span>
        <span class="message">{message}</span>
        <div class="calorie-info">
          <span>
            Recommended daily calorie{' '}
            {goalType === 'lose'
              ? 'deficit'
              : goalType === 'gain'
              ? 'surplus'
              : 'adjustment'}
            :
          </span>
          <div class="input-with-tooltip">
            <strong>{calorieAdjust} kcal</strong>
            <button
              class="info-button"
              on:click={() => (showCalorieTooltip = !showCalorieTooltip)}
              on:blur={() => (showCalorieTooltip = false)}
            >
              ℹ️
            </button>
            {#if showCalorieTooltip}
              <div class="tooltip">
                This is calculated based on your weight difference and
                duration. For every 7700 calories, you gain or lose 1 kg of
                weight. Your calorie adjustment will be applied to your daily
                calorie budget.
              </div>
            {/if}
          </div>
        </div>
      </div>
{/if}

    {#if hasExistingGoal}
      <div class="goal-type">
<h3>Goal Type</h3>
<p>{goalLabel}</p>
      </div>
    {/if}

    <div class="progress-section">
<h3>Weight Progress</h3>
<progress max="1" value={weightProgress}></progress>
      <p>{Math.round(weightProgress * 100)}% toward your weight goal</p>
    </div>

    <div class="progress-section">
<h3>Time Progress</h3>
<progress max="1" value={timeProgress}></progress>
      <p>{Math.round(timeProgress * 100)}% of {savedDuration} days elapsed</p>
    </div>

    {#if hasExistingGoal && $userRole !== 'admin'}
      <div class="comments-section">
        <h3>Admin Notes</h3>

        {#if $goalCommentsLoading}
          <p>Loading comments...</p>
        {:else if $goalCommentsError}
          <p class="error-message">{$goalCommentsError}</p>
        {:else if $goalComments.length === 0}
          <p>No notes yet.</p>
        {/if}

        <ul>
          {#each $goalComments as comment (comment.id)}
            <li>
              <div class="comment-content">{comment.content}</div>
              <div class="comment-meta">
                <span>
                  {comment.created_by} |{' '}
                  {new Date(comment.created_at).toLocaleString()}
                </span>
                {#if $userRole === 'admin'}
                  <button
                    class="delete-comment"
                    on:click={() => handleDeleteComment(comment.id)}
                  >
                    Delete
                  </button>
                {/if}
                {#if comment.milestone}
                  <span class="milestone-badge">
                    🏅 {comment.milestone}% milestone
                  </span>
                {/if}
              </div>
            </li>
          {/each}
        </ul>
      </div>
    {/if}
  </div>
</div>

<style>
  .mod-notes-card {
    margin-bottom: 2rem;
    background: #fff;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  }

  .comments-section {
    margin-top: 2rem;
    background: #f8f9fa;
    border-radius: 8px;
    padding: 1rem;
  }
  .comments-section h3 {
    margin-bottom: 0.5rem;
  }
  .add-comment {
    margin-top: 1rem;
  }
  .add-comment textarea {
    width: 100%;
    min-height: 60px;
    margin-bottom: 0.5rem;
  }
  .template-buttons {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }
  .template-buttons button.active {
    background: #007bff;
    color: #fff;
  }
  .comment-content {
    font-size: 1rem;
    margin-bottom: 0.2rem;
  }
  .comment-meta {
    font-size: 0.85rem;
    color: #666;
    display: flex;
    align-items: center;
    gap: 1rem;
  }
  .delete-comment {
    background: none;
    color: #c00;
    border: none;
    cursor: pointer;
  }
  .milestone-badge {
    background: #ffe066;
    color: #856404;
    border-radius: 4px;
    padding: 0.1rem 0.5rem;
    margin-left: 0.5rem;
    font-size: 0.85rem;
  }
</style>

