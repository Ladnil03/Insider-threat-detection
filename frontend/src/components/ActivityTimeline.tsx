import React from 'react';

interface TimelineEvent {
  id: string;
  timestamp: string;
  action: string;
}

interface ActivityTimelineProps {
  events: TimelineEvent[];
}

export const ActivityTimeline: React.FC<ActivityTimelineProps> = ({ events }) => {
  return (
    <div className="p-4 bg-slate-800 rounded border border-slate-700">
      <h3 className="text-lg font-semibold text-slate-200 mb-3">Activity Timeline</h3>
      <ul className="space-y-2">
        {events.map((event) => (
          <li key={event.id} className="text-xs text-slate-400">
            <span className="font-mono text-slate-500">{event.timestamp}</span>: {event.action}
          </li>
        ))}
      </ul>
    </div>
  );
};
