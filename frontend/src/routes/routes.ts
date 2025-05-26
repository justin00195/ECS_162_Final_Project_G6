import Homepage from './Homepage.svelte';
import UserPortal from './UserPortal.svelte';
import GoalPage from './GoalPage.svelte';
import PlannerPage from './PlannerPage.svelte';
import ReportPage from './ReportPage.svelte';
import CalculatorPage from './CalculatorPage.svelte';
import RecipePage from './RecipePage.svelte';

const routes = {
    '/': Homepage,
    '/calculator': CalculatorPage,
    '/goal': GoalPage,
    '/planner': PlannerPage,
    '/report': ReportPage,
    '/recipe': RecipePage,
    '/user-portal': UserPortal
};

export default routes;
