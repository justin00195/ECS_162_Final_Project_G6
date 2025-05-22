declare module 'svelte-spa-router' {
    import { SvelteComponent } from 'svelte';
  
    export interface RouteDefinition {
      [path: string]: typeof SvelteComponent;
    }
  
    export interface RouterProps {
      routes: RouteDefinition;
    }
  
    export default class Router extends SvelteComponent {
      constructor(options: any);
    }
  
    export function link(node: HTMLElement): { destroy(): void };
  }