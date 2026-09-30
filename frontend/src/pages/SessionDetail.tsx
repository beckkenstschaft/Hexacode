/** Session detail page */

import { useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { formatDistanceToNow } from "date-fns";
import { LANGUAGES, PROVIDER_LABELS } from "../utils/constants";
import { useSession, useGenerateSummary } from "../hooks/useApi";
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Badge,
  EmptyState,
  Loading,
  ErrorState,
  PageHeader,
} from "../components";
import type { SessionDetail, TranscriptSegment, Summary } from "../types/api";

export function SessionDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const generateSummary = useGenerateSummary();

  const { data: session, isLoading, error, refetch } = useSession(id!);

  const languageMap = new Map(LANGUAGES.map((l) => [l.code, l.name]));

  const handleGenerateSummary = async () => {
    await generateSummary.mutateAsync(id!);
    refetch();
  };

  const handleBack = () => {
    navigate("/sessions");
  };

  if (isLoading && !session) {
    return (
      <div>
        <PageHeader title="Loading..." action={<Button variant="ghost" onClick={handleBack}>Back</Button>} />
        <Loading text="Loading session details..." />
      </div>
    );
  }

  if (error || !session) {
    return (
      <div>
        <PageHeader title="Session Not Found" action={<Button variant="ghost" onClick={handleBack}>Back to Sessions</Button>} />
        <ErrorState
          title="Session not found"
          message={error?.message || "This session may have been deleted"}
          onRetry={handleBack}
          retryLabel="Back to Sessions"
        />
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title={session.title}
        subtitle={
          <>
            <Badge variant={session.status === "active" ? "success" : "default"} className="mr-2">
              {session.status}
            </Badge>
            <Badge variant="info">
              {languageMap.get(session.language) || session.language}
            </Badge>
            <span className="text-gray-500 ml-2">
              Started {formatDistanceToNow(new Date(session.started_at), { addSuffix: true })}
              {session.ended_at && (
                <>
                  {" • "}
                  Ended {formatDistanceToNow(new Date(session.ended_at), { addSuffix: true })}
                </>
              )}
            </span>
          </>
        }
        action={
          <div className="flex items-center gap-2">
            <Button variant="ghost" onClick={handleBack}>
              Back
            </Button>
            <Button
              onClick={handleGenerateSummary}
              disabled={generateSummary.isPending || session.status !== "completed"}
            >
              {generateSummary.isPending ? "Generating..." : "Generate Summary"}
            </Button>
          </div>
        }
      />

      {/* Transcript */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Transcript</CardTitle>
        </CardHeader>
        <CardContent>
          {session.transcript_segments && session.transcript_segments.length > 0 ? (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {session.transcript_segments.map((segment: TranscriptSegment) => (
                <div
                  key={segment.id}
                  className="p-3 rounded-lg bg-gray-50 border-l-4 border-snapdragon-blue-light"
                >
                  <p className="whitespace-pre-wrap text-snapdragon-navy">{segment.text}</p>
                  <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
                    <Badge variant={segment.simulated ? "simulated" : "default"} size="sm">
                      {PROVIDER_LABELS[segment.provider] || segment.provider}
                    </Badge>
                    <span>{new Date(segment.start_ms).toLocaleTimeString()} - {new Date(segment.end_ms).toLocaleTimeString()}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              title="No transcript available"
              description="This session doesn't have any transcript segments yet"
            />
          )}
        </CardContent>
      </Card>

      {/* Summaries */}
      <Card>
        <CardHeader>
          <CardTitle>Summaries</CardTitle>
        </CardHeader>
        <CardContent>
          {session.summaries && session.summaries.length > 0 ? (
            session.summaries.map((summary: Summary) => (
              <div key={summary.id} className="mb-6 last:mb-0">
                <div className="flex items-center gap-2 mb-3">
                  <Badge variant={summary.simulated ? "simulated" : "default"} size="sm">
                    {PROVIDER_LABELS[summary.provider] || summary.provider}
                  </Badge>
                  <span className="text-sm text-gray-500">
                    Generated {formatDistanceToNow(new Date(summary.created_at), { addSuffix: true })}
                  </span>
                </div>

                {summary.key_points && summary.key_points.length > 0 && (
                  <div className="mb-4">
                    <h4 className="font-medium text-snapdragon-navy mb-2">Key Points</h4>
                    <ul className="space-y-1 list-disc list-inside text-gray-700">
                      {summary.key_points.map((point, i) => (
                        <li key={i}>{point}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {summary.action_items && summary.action_items.length > 0 && (
                  <div>
                    <h4 className="font-medium text-snapdragon-navy mb-2">Action Items</h4>
                    <ul className="space-y-1 list-disc list-inside text-gray-700">
                      {summary.action_items.map((item, i) => (
                        <li key={i}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))
          ) : (
            <EmptyState
              title="No summaries yet"
              description="Click 'Generate Summary' to create a summary from the transcript"
            />
          )}
        </CardContent>
      </Card>
    </div>
  );
}