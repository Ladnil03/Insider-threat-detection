import apiClient from "./client";
import type { Feedback } from "../types";

export async function submitFeedback(feedback: Feedback): Promise<void> {
  await apiClient.post("/feedback", feedback);
}
