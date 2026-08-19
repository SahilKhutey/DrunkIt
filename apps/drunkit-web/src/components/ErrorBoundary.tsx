import { Component, type ErrorInfo, type ReactNode } from "react";
import { Seal } from "./Seal";
import { Button } from "./ui/Button";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

/**
 * Top-level error boundary. Catches render-time errors anywhere below
 * it in the tree and shows a stable fallback instead of a blank white
 * screen — this is a template in its own right (the "something broke"
 * page), distinct from the 404 "nothing here" page.
 */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    // In a real deployment this would report to an error-tracking
    // service (Sentry, etc.) rather than just the console.
    console.error("Unhandled error in component tree:", error, info);
  }

  handleReload = () => {
    window.location.href = "/";
  };

  render() {
    if (!this.state.hasError) return this.props.children;

    return (
      <div className="mx-auto flex min-h-screen max-w-md flex-col items-center justify-center px-4 text-center">
        <Seal label="Something went wrong" tone="rust" size="md" />
        <h1 className="mt-4 font-display text-2xl text-parchment">
          That didn't work as expected.
        </h1>
        <p className="mt-2 text-sm text-parchment/50">
          Nothing on your end broke this — please try again, and it should recover.
        </p>
        <Button onClick={this.handleReload} className="mt-6">
          Back to home
        </Button>
      </div>
    );
  }
}
