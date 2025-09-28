"use client";

import { useState, useEffect } from "react";

export function useEventSource(url: string | null) {
  const [messages, setMessages] = useState<string[]>([]);

  useEffect(() => {
    // If the URL is not ready, do nothing.
    if (!url) {
      return;
    }

    // Create a new EventSource instance. The browser handles the connection.
    const eventSource = new EventSource(url);

    // Clear any previous logs when a new connection is established.
    setMessages([]);

    // Handler for when the connection is successfully opened.
    eventSource.onopen = () => {
      console.log("SSE connection established");
      // The backend sends a "connected" event, but we can also add a client-side message.
      setMessages((prev) => [...prev, "[INFO] Live log stream connected."]);
    };

    // Handler for receiving a message from the server.
    eventSource.onmessage = (event) => {
      // The `event.data` contains the string sent from the backend.
      setMessages((prev) => [...prev, event.data]);
    };

    // Handler for any errors. The browser will automatically attempt to reconnect.
    eventSource.onerror = (error) => {
      console.error("EventSource failed:", error);
      setMessages((prev) => [
        ...prev,
        "[ERROR] Log stream connection lost. Attempting to reconnect...",
      ]);
      // No need to manually close or reconnect; the browser's EventSource API handles this.
    };

    // The cleanup function is critical. It's called when the component unmounts.
    // This closes the connection to prevent memory leaks.
    return () => {
      eventSource.close();
      console.log("SSE connection closed.");
    };
  }, [url]); // This effect re-runs if the URL changes.

  return messages;
}
