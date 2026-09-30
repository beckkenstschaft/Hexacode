/** Sessions list page */

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { formatDistanceToNow } from "date-fns";
import { LANGUAGES } from "../utils/constants";
import { useSessions, useDeleteSession } from "../hooks/useApi";
import {
  Button,
  Card,
  CardContent,
  Badge,
  Select,
  EmptyState,
  Loading,
  ErrorState,
  PageHeader,
} from "../components";
import type { Session } from "../types/api";

export function SessionsPage() {
  const navigate = useNavigate();
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [page, setPage] = useState(0);
  const limit = 20;

  const { data: sessions, isLoading, error, refetch } = useSessions({
    limit,
    offset: page * limit,
    status: statusFilter !== "all" ? statusFilter : undefined,
  });

  const deleteSession = useDeleteSession();

  const handleDelete = async (id: string) => {
    if (window.confirm("Are you sure you want to delete this session?")) {
      await deleteSession.mutateAsync(id);
      refetch();
    }
  };

  const handleView = (id: string) => {
    navigate(`/sessions/${id}`);
  };

  const statusOptions = [
    { value: "all", label: "All" },
    { value: "active", label: "Active" },
    { value: "completed", label: "Completed" },
    { value: "archived", label: "Archived" },
  ];

  if (isLoading && !sessions) {
    return (
      <div>
        <PageHeader title="Sessions" subtitle="All your recorded sessions" />
        <Loading text="Loading sessions..." />
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <PageHeader title="Sessions" subtitle="All your recorded sessions" />
        <ErrorState
          title="Failed to load sessions"
          message={error.message}
          onRetry={() => refetch()}
        />
      </div>
    );
  }

  const languageMap = new Map(LANGUAGES.map((l) => [l.code, l.name]));

  return (
    <div>
      <PageHeader
        title="Sessions"
        subtitle="All your recorded sessions"
        action={
          <Select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(0);
            }}
            options={statusOptions}
            className="w-40"
          />
        }
      />

      <Card>
        <CardContent className="p-0">
          {sessions && sessions.length > 0 ? (
            <div className="divide-y divide-gray-200">
              {sessions.map((session) => (
                <div
                  key={session.id}
                  className="p-4 hover:bg-gray-50 transition-colors cursor-pointer"
                  onClick={() => handleView(session.id)}
                >
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 flex-wrap">
                        <h3 className="font-medium text-snapdragon-navy truncate">{session.title}</h3>
                        <Badge variant={session.status === "active" ? "success" : "default"} size="sm">
                          {session.status}
                        </Badge>
                        <Badge variant="info" size="sm">
                          {languageMap.get(session.language) || session.language}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-500 mt-1">
                        Started {formatDistanceToNow(new Date(session.started_at), { addSuffix: true })}
                        {session.ended_at && (
                          <>
                            {" • "}
                            Ended {formatDistanceToNow(new Date(session.ended_at), { addSuffix: true })}
                          </>
                        )}
                      </p>
                    </div>
                    <div className="flex items-center gap-2 sm:ml-4">
                      <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); handleView(session.id); }}>
                        View
                      </Button>
                      <Button variant="ghost" size="sm" variant="danger" onClick={(e) => { e.stopPropagation(); handleDelete(session.id); }}>
                        Delete
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              title="No sessions yet"
              description="Start a live caption session to create your first recording"
              action={
                <Button onClick={() => navigate("/")}>Start Live Session</Button>
              }
            />
          )}

          {/* Pagination */}
          {sessions && sessions.length === limit && (
            <div className="px-4 py-4 border-t border-gray-200 flex items-center justify-between">
              <Button variant="outline" onClick={() => setPage((p) => Math.max(0, p - 1))} disabled={page === 0}>
                Previous
              </Button>
              <span className="text-sm text-gray-500">Page {page + 1}</span>
              <Button variant="outline" onClick={() => setPage((p) => p + 1)}>
                Next
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}