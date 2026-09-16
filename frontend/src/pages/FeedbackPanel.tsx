import React, { useEffect, useState } from 'react';
import { submitFeedback } from '../api/feedback';
import { ScoreSlider } from '../components/ScoreSlider';
import { FeedbackResponse } from '../types';

interface FeedbackPanelProps {
  initialUserId?: string;
  initialActivityId?: number;
  initialScore?: number;
  onFeedbackSubmitted?: (result: FeedbackResponse) => void;
  isEmbedded?: boolean;
}

export const FeedbackPanel: React.FC<FeedbackPanelProps> = ({
  initialUserId = 'ACM2278',
  initialActivityId = 1,
  initialScore = 0.50,
  onFeedbackSubmitted,
  isEmbedded = false,
}) => {
  const [userId, setUserId] = useState<string>(initialUserId);
  const [activityId, setActivityId] = useState<number>(initialActivityId);
  const [adjustedScore, setAdjustedScore] = useState<number>(initialScore);
  const [notes, setNotes] = useState<string>('Analyst calibrated score based on investigation context.');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [feedbackResult, setFeedbackResult] = useState<FeedbackResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Sync props when initial selection changes
  useEffect(() => {
    setUserId(initialUserId);
    setActivityId(initialActivityId);
    setAdjustedScore(initialScore);
    setFeedbackResult(null);
    setErrorMessage(null);
  }, [initialUserId, initialActivityId, initialScore]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      const res = await submitFeedback({
        activity_id: activityId,
        user_id: userId,
        adjusted_score: adjustedScore,
        notes: notes.trim() || null,
      });

      setFeedbackResult(res);
      onFeedbackSubmitted?.(res);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to submit analyst feedback.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const formContent = (
    <form onSubmit={handleSubmit} className="space-y-4">
      {!isEmbedded && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
              Target Employee ID
            </label>
            <input
              type="text"
              required
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
              Activity Record ID
            </label>
            <input
              type="number"
              required
              min={1}
              value={activityId}
              onChange={(e) => setActivityId(parseInt(e.target.value, 10))}
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 focus:border-blue-500 focus:outline-none"
            />
          </div>
        </div>
      )}

      {/* Interactive Score Slider */}
      <ScoreSlider
        value={adjustedScore}
        onChange={setAdjustedScore}
        disabled={isSubmitting}
        label="Analyst Calibrated Risk Score"
      />

      {/* Investigation Notes */}
      <div>
        <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
          Analyst Investigation Rationale
        </label>
        <textarea
          rows={2}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Document authorized exceptions, pen-test activity, or escalated suspicion..."
          className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:border-blue-500 focus:outline-none"
        />
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full rounded-lg bg-blue-600 py-2.5 text-xs font-semibold uppercase tracking-wider text-white shadow-lg transition hover:bg-blue-500 active:scale-95 disabled:opacity-50"
      >
        {isSubmitting ? 'Recording Human Calibration...' : 'Commit Risk Score Adjustment'}
      </button>

      {/* Error state */}
      {errorMessage && (
        <div className="rounded-lg border border-rose-800 bg-rose-950/60 p-3 text-xs text-rose-300">
          <span className="font-semibold">Submission Error: </span>
          {errorMessage}
        </div>
      )}

      {/* Mathematical Score Blending Success State */}
      {feedbackResult && (
        <div className="rounded-lg border border-emerald-800/80 bg-emerald-950/50 p-4 text-xs space-y-2 shadow-lg">
          <div className="flex items-center gap-2 text-emerald-300 font-semibold">
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <span>Feedback Successfully Blended & Persisted</span>
          </div>

          <div className="grid grid-cols-3 gap-2 pt-1 font-mono text-center">
            <div className="rounded bg-slate-900/80 p-2 border border-slate-800">
              <div className="text-[10px] text-slate-400">Original AI</div>
              <div className="text-sm font-bold text-slate-200">{feedbackResult.original_score.toFixed(3)}</div>
            </div>
            <div className="rounded bg-slate-900/80 p-2 border border-slate-800">
              <div className="text-[10px] text-slate-400">Analyst Adj.</div>
              <div className="text-sm font-bold text-amber-300">{feedbackResult.adjusted_score.toFixed(3)}</div>
            </div>
            <div className="rounded bg-slate-900/80 p-2 border border-emerald-800/60 bg-emerald-950/40">
              <div className="text-[10px] text-emerald-400">Blended (α=0.7)</div>
              <div className="text-sm font-bold text-emerald-300">{feedbackResult.blended_score.toFixed(3)}</div>
            </div>
          </div>

          <p className="text-[11px] text-slate-400 pt-1">
            Mathematical formula: S_final = (1 - α)·S_AI + α·S_user (α = 0.70). Record ID #{feedbackResult.feedback_id}.
          </p>

          {feedbackResult.retrain_threshold_reached && (
            <div className="mt-2 rounded bg-amber-950/80 p-2 text-[11px] text-amber-300 border border-amber-800 flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-amber-400 animate-ping" />
              <span>Feedback buffer capacity reached (N=50). Background online fine-tuning queued.</span>
            </div>
          )}
        </div>
      )}
    </form>
  );

  if (isEmbedded) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl backdrop-blur">
        <div className="border-b border-slate-800/80 pb-3 mb-4">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">
              Analyst Feedback Calibration
            </h3>
            <span className="rounded bg-amber-950/80 px-2 py-0.5 text-[10px] font-semibold text-amber-300 border border-amber-800/60 uppercase">
              Human-in-the-Loop
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Calibrate risk score for Activity #{activityId}. Changes update training buffers.
          </p>
        </div>
        {formContent}
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="border-b border-slate-800 pb-5">
        <h1 className="text-2xl font-bold tracking-tight text-slate-100 sm:text-3xl">
          Analyst Calibration Feedback
        </h1>
        <p className="mt-1 text-sm text-slate-400">
          Incorporate human-in-the-loop expert corrections. Scores are blended via mathematical weighting and stored for online model fine-tuning.
        </p>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl backdrop-blur">
        {formContent}
      </div>
    </div>
  );
};

export default FeedbackPanel;
