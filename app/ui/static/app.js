const ICONS = {
  assignments:
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M8 6h12"/><path d="M8 12h12"/><path d="M8 18h12"/><path d="M4 6h.01"/><path d="M4 12h.01"/><path d="M4 18h.01"/></svg>',
  bell:
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M15 17h5l-1.4-1.4A2 2 0 0 1 18 14.2V11a6 6 0 0 0-12 0v3.2a2 2 0 0 1-.6 1.4L4 17h5"/><path d="M10 20a2 2 0 0 0 4 0"/></svg>',
  calendar:
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/></svg>',
  collapse:
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/><path d="M19 18l-6-6 6-6"/></svg>',
  courses:
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6.5 12 3l9 3.5v11L12 21l-9-3.5z"/><path d="M12 21V9.5"/><path d="M21 6.5 12 10 3 6.5"/></svg>',
  dashboard:
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>',
  grades:
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20V10"/><path d="M10 20V4"/><path d="M16 20v-7"/><path d="M22 20V8"/></svg>',
  link:
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M7 17 17 7"/><path d="M8 7h9v9"/></svg>',
  close:
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>',
  edit:
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>',
  chevronRight:
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>',
  circleCheck:
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="m9.5 12 1.8 1.8L15 10.2"/></svg>',
  clock3:
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
  search:
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
  settings:
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v3"/><path d="M12 19v3"/><path d="m4.93 4.93 2.12 2.12"/><path d="m16.95 16.95 2.12 2.12"/><path d="M2 12h3"/><path d="M19 12h3"/><path d="m4.93 19.07 2.12-2.12"/><path d="m16.95 7.05 2.12-2.12"/><circle cx="12" cy="12" r="4"/></svg>',
  loader:
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-6.2-8.56"/></svg>',
  alertCircle:
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 8v4"/><path d="M12 16h.01"/></svg>',
  github:
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-4 1.5-4-2-6-2"/><path d="M15 22v-3.9a3.4 3.4 0 0 0-.9-2.6c3 0 6-1.8 6-8a6.2 6.2 0 0 0-1.8-4.3 5.7 5.7 0 0 0-.1-4.2s-1.1-.3-4.2 1.7a14.6 14.6 0 0 0-8 0C2.9-1.3 1.8-1 1.8-1A5.7 5.7 0 0 0 1.7 3.2 6.2 6.2 0 0 0 0 7.5c0 6.2 3 8 6 8a3.4 3.4 0 0 0-.9 2.6V22"/></svg>',
  play:
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="m10 9 5 3-5 3z"/></svg>',
  briefcase:
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M3 12h18"/></svg>',
  trash:
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/></svg>',
};

const ROUTES = {
  "/assignments": {
    label: "Assignments",
    title: "Assignments",
    subtitle: "Review session deliverables and student submissions.",
    render: renderAssignmentsPage,
  },
  "/dashboard": {
    label: "Dashboard",
    title: "Dashboard",
    subtitle: "A quiet operational view into the current review workspace.",
    render: renderDashboardPage,
  },
  "/courses": {
    label: "Courses",
    title: "Courses",
    subtitle: "Your enrolled courses",
    render: renderCoursesPage,
  },
  "/calendar": {
    label: "Calendar",
    title: "Calendar",
    subtitle: "Upcoming deadlines and events",
    render: renderCalendarPage,
  },
  "/grades": {
    label: "Grades",
    title: "Grades",
    subtitle: "Stored grading output across the current workspace",
    render: renderGradesPage,
  },
  "/settings": {
    label: "Settings",
    title: "Settings",
    subtitle: "Workspace configuration",
    render: renderSettingsPage,
  },
};

const state = {
  route: normalizeRoute(window.location.pathname),
  sessions: [],
  sessionWorkspaces: new Map(),
  sessionConceptDocuments: new Map(),
  selectedSessionId: null,
  selectedAssignmentIds: {},
  cardActionStates: {},
  submissionGradeStates: {},
  openCardModal: null,
  search: "",
  statusFilter: "all",
  submissionFilter: "all",
};

const SESSION_CARD_ACCENTS = [
  {
    accent: "#6f62ff",
    border: "rgba(53, 56, 68, 0.95)",
    shadow: "rgba(0, 0, 0, 0.14)",
    tint: "rgba(255, 255, 255, 0.01)",
  },
];

const ASSIGNMENT_STATUS_ACCENTS = {
  no_submissions: {
    accent: "#6f62ff",
    border: "rgba(47, 50, 60, 0.95)",
    shadow: "rgba(0, 0, 0, 0.12)",
    tint: "rgba(255, 255, 255, 0.01)",
  },
  needs_resubmission: {
    accent: "#fb5b6d",
    border: "rgba(47, 50, 60, 0.95)",
    shadow: "rgba(0, 0, 0, 0.12)",
    tint: "rgba(255, 255, 255, 0.01)",
  },
  reviewed: {
    accent: "#36b37e",
    border: "rgba(47, 50, 60, 0.95)",
    shadow: "rgba(0, 0, 0, 0.12)",
    tint: "rgba(255, 255, 255, 0.01)",
  },
  submitted: {
    accent: "#ff9f43",
    border: "rgba(47, 50, 60, 0.95)",
    shadow: "rgba(0, 0, 0, 0.12)",
    tint: "rgba(255, 255, 255, 0.01)",
  },
  under_review: {
    accent: "#5da2ff",
    border: "rgba(47, 50, 60, 0.95)",
    shadow: "rgba(0, 0, 0, 0.12)",
    tint: "rgba(255, 255, 255, 0.01)",
  },
};

const SESSION_RESOURCE_CARD_ACCENTS = {
  concepts: {
    accent: "#5da2ff",
    border: "rgba(47, 50, 60, 0.95)",
    shadow: "rgba(0, 0, 0, 0.12)",
    tint: "rgba(255, 255, 255, 0.01)",
  },
  requirements: {
    accent: "#ff7c6d",
    border: "rgba(47, 50, 60, 0.95)",
    shadow: "rgba(0, 0, 0, 0.12)",
    tint: "rgba(255, 255, 255, 0.01)",
  },
};

const REQUIREMENT_TYPE_OPTIONS = [
  { value: "mandatory_deliverable", label: "Deliverable" },
  { value: "forbidden_project_type", label: "Forbidden type" },
  { value: "scoring_criterion", label: "Scoring criterion" },
  { value: "evidence_expectation", label: "Evidence expectation" },
];

const SUBMISSION_FILTER_OPTIONS = [
  { value: "all", label: "All" },
  { value: "pending", label: "Pending" },
  { value: "reviewed", label: "Reviewed" },
  { value: "needs_resubmission", label: "Needs Action" },
];

const dom = {
  pageContent: document.getElementById("page-content"),
  pageHeaderActions: document.getElementById("page-header-actions"),
  pageSubtitle: document.getElementById("page-subtitle"),
  pageTitle: document.getElementById("page-title"),
  topbarPageLabel: document.getElementById("topbar-page-label"),
};

function setPageHeading(title, subtitle = "") {
  dom.pageTitle.textContent = title;
  dom.pageSubtitle.textContent = subtitle;
  dom.pageSubtitle.style.display = subtitle ? "" : "none";
}

document.addEventListener("DOMContentLoaded", () => {
  injectIcons();
  bindShellNavigation();
  document.addEventListener("keydown", handleGlobalKeydown);
  window.addEventListener("popstate", () => {
    state.route = normalizeRoute(window.location.pathname);
    void renderRoute();
  });
  void renderRoute();
});

function injectIcons() {
  document.querySelectorAll("[data-icon]").forEach((element) => {
    const iconName = element.dataset.icon;
    if (iconName && ICONS[iconName]) {
      element.innerHTML = ICONS[iconName];
    }
  });
}

function bindShellNavigation() {
  document.querySelectorAll("[data-route]").forEach((element) => {
    element.addEventListener("click", (event) => {
      const route = element.getAttribute("data-route");
      if (!route) {
        return;
      }
      event.preventDefault();
      if (normalizeRoute(route) === "/assignments") {
        resetAssignmentsView();
      }
      navigate(route);
    });
  });
}

function navigate(route) {
  const normalizedRoute = normalizeRoute(route);
  if (normalizedRoute === state.route) {
    if (normalizedRoute === "/assignments") {
      void renderRoute();
    }
    return;
  }
  window.history.pushState({}, "", normalizedRoute);
  state.route = normalizedRoute;
  void renderRoute();
}

function normalizeRoute(route) {
  const trimmedRoute = route.endsWith("/") && route !== "/" ? route.slice(0, -1) : route;
  return ROUTES[trimmedRoute] ? trimmedRoute : "/assignments";
}

async function renderRoute() {
  const routeConfig = ROUTES[state.route] ?? ROUTES["/assignments"];
  state.openCardModal = null;
  syncAssignmentModalState(false);
  dom.topbarPageLabel.textContent = routeConfig.label;
  setPageHeading(routeConfig.title, routeConfig.subtitle);
  dom.pageHeaderActions.innerHTML = "";
  setActiveNavigation();
  dom.pageContent.innerHTML = '<div class="loading-state">Loading...</div>';
  await routeConfig.render();
}

function setActiveNavigation() {
  document.querySelectorAll("[data-route]").forEach((element) => {
    const route = element.getAttribute("data-route");
    const isActive = route === state.route;
    element.classList.toggle("is-active", isActive);
  });
}

async function requestJson(url, options = {}) {
  const requestHeaders = {
    Accept: "application/json",
    ...(options.body ? { "Content-Type": "application/json" } : {}),
    ...(options.headers ?? {}),
  };
  const response = await fetch(url, {
    ...options,
    headers: requestHeaders,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const message = body?.error?.message ?? `Request failed with status ${response.status}.`;
    throw new Error(message);
  }
  return response.json();
}

async function fetchJson(url) {
  return requestJson(url);
}

async function postJson(url, payload = {}) {
  return requestJson(url, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

async function ensureSessionsLoaded() {
  if (state.sessions.length > 0) {
    return state.sessions;
  }

  state.sessions = await fetchJson("/allsessions");
  return state.sessions;
}

async function ensureSessionWorkspaceLoaded(sessionId) {
  if (state.sessionWorkspaces.has(sessionId)) {
    return state.sessionWorkspaces.get(sessionId);
  }

  const [requirementsDocument, submissions] = await Promise.all([
    fetchJson(`/sessions/${sessionId}/assignment-requirements`),
    fetchJson(`/sessions/${sessionId}/submissions`),
  ]);

  const assignmentsById = new Map();
  for (const assignment of requirementsDocument.assignment_requirements) {
    assignmentsById.set(assignment.assignment_requirement_id, {
      assignmentRequirementId: assignment.assignment_requirement_id,
      title: assignment.assignment_title,
      description: assignment.assignment_description ?? "",
      dueAt: assignment.due_at,
      requiredDeliverables: assignment.required_deliverables ?? [],
      requirements: assignment.requirements ?? [],
      submissions: [],
    });
  }

  for (const submission of submissions) {
    const normalizedSubmission = {
      ...submission,
      concept_scores: normalizeScoreItems(submission.concept_scores),
      assignment_requirement_scores: normalizeScoreItems(
        submission.assignment_requirement_scores,
      ),
      rubric_scores: normalizeScoreItems(submission.rubric_scores),
    };
    if (!assignmentsById.has(submission.assignment_requirement_id)) {
      assignmentsById.set(submission.assignment_requirement_id, {
        assignmentRequirementId: submission.assignment_requirement_id,
        title: submission.assignment_title,
        description: "",
        dueAt: submission.due_at,
        requiredDeliverables: [],
        requirements: [],
        submissions: [],
      });
    }
    const assignment = assignmentsById.get(submission.assignment_requirement_id);
    assignment.submissions.push(normalizedSubmission);
    assignment.dueAt = assignment.dueAt ?? submission.due_at;
  }

  const assignments = Array.from(assignmentsById.values())
    .map((assignment) => ({
      ...assignment,
      submissions: assignment.submissions.sort((left, right) =>
        right.submitted_at.localeCompare(left.submitted_at),
      ),
      counts: buildSubmissionCounts(assignment.submissions),
    }))
    .sort(compareAssignments);

  const workspace = {
    sessionId,
    assignments,
    assignmentLookup: new Map(assignments.map((assignment) => [assignment.assignmentRequirementId, assignment])),
    storedAssignmentRequirements: requirementsDocument.assignment_requirements,
    submissions: submissions.map((submission) => ({
      ...submission,
      concept_scores: normalizeScoreItems(submission.concept_scores),
      assignment_requirement_scores: normalizeScoreItems(
        submission.assignment_requirement_scores,
      ),
      rubric_scores: normalizeScoreItems(submission.rubric_scores),
    })),
  };
  state.sessionWorkspaces.set(sessionId, workspace);
  if (!Object.prototype.hasOwnProperty.call(state.selectedAssignmentIds, sessionId)) {
    state.selectedAssignmentIds[sessionId] = assignments[0]?.assignmentRequirementId ?? null;
  }
  return workspace;
}

async function ensureSessionConceptsLoaded(sessionId) {
  if (state.sessionConceptDocuments.has(sessionId)) {
    return state.sessionConceptDocuments.get(sessionId);
  }
  const conceptsDocument = await fetchJson(`/sessions/${sessionId}/concepts`);
  state.sessionConceptDocuments.set(sessionId, conceptsDocument);
  return conceptsDocument;
}

function invalidateSessionWorkspace(sessionId) {
  state.sessionWorkspaces.delete(sessionId);
}

function invalidateSessionConcepts(sessionId) {
  state.sessionConceptDocuments.delete(sessionId);
}

async function ensureAllAssignmentsLoaded() {
  const sessions = await ensureSessionsLoaded();
  const workspaces = await Promise.all(
    sessions.map((session) => ensureSessionWorkspaceLoaded(session.session_id)),
  );
  return workspaces.flatMap((workspace) => workspace.assignments);
}

function buildSubmissionCounts(submissions) {
  const counts = {
    total: submissions.length,
    submitted: 0,
    under_review: 0,
    reviewed: 0,
    needs_resubmission: 0,
  };
  for (const submission of submissions) {
    counts[submission.status] += 1;
  }
  return counts;
}

function compareAssignments(left, right) {
  if (left.dueAt && right.dueAt) {
    return left.dueAt.localeCompare(right.dueAt);
  }
  if (left.dueAt) {
    return -1;
  }
  if (right.dueAt) {
    return 1;
  }
  return left.title.localeCompare(right.title);
}

function formatDate(dateString) {
  if (!dateString) {
    return "No due date";
  }
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(dateString));
}

function formatDateTime(dateString) {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(dateString));
}

function getPrimaryStatus(assignment) {
  if (assignment.counts.total === 0) {
    return "no_submissions";
  }
  if (assignment.counts.needs_resubmission > 0) {
    return "needs_resubmission";
  }
  if (assignment.counts.under_review > 0) {
    return "under_review";
  }
  if (assignment.counts.submitted > 0) {
    return "submitted";
  }
  return "reviewed";
}

function formatStatusLabel(status) {
  const labels = {
    no_submissions: "No submissions",
    needs_resubmission: "Needs resubmission",
    reviewed: "Reviewed",
    submitted: "Submitted",
    under_review: "Under review",
  };
  return labels[status] ?? status;
}

function normalizeDisplayText(value) {
  return String(value ?? "").replace(/\s+/g, " ").trim();
}

function getSessionTopicCardCopy(sessionTopic, maxLength = 180) {
  const normalizedTopic = normalizeDisplayText(sessionTopic);
  if (normalizedTopic.length <= maxLength) {
    return normalizedTopic;
  }
  return `${normalizedTopic.slice(0, maxLength - 3).trimEnd()}...`;
}

function buildAccentStyle(accentConfig) {
  return [
    `--card-accent: ${accentConfig.accent}`,
    `--card-border: ${accentConfig.border}`,
    `--card-shadow: ${accentConfig.shadow}`,
    `--card-tint: ${accentConfig.tint}`,
  ].join("; ");
}

function getSessionById(sessionId) {
  return state.sessions.find((session) => session.session_id === sessionId) ?? null;
}

function getSelectedAssignment(workspace) {
  const storedSelection = state.selectedAssignmentIds[workspace.sessionId];
  if (!storedSelection) {
    return null;
  }
  const filteredAssignments = getFilteredAssignments(workspace);
  if (
    storedSelection &&
    filteredAssignments.some(
      (assignment) => assignment.assignmentRequirementId === storedSelection,
    )
  ) {
    return workspace.assignmentLookup.get(storedSelection) ?? null;
  }
  state.selectedAssignmentIds[workspace.sessionId] = null;
  return null;
}

function getFilteredAssignments(workspace) {
  const searchTerm = state.search.trim().toLowerCase();
  return workspace.assignments.filter((assignment) => {
    const primaryStatus = getPrimaryStatus(assignment);
    if (state.statusFilter !== "all" && primaryStatus !== state.statusFilter) {
      return false;
    }
    if (!searchTerm) {
      return true;
    }
    const searchableText = [
      assignment.title,
      assignment.description,
      ...assignment.requiredDeliverables,
      ...assignment.submissions.map((submission) => submission.student_full_name),
    ]
      .join(" ")
      .toLowerCase();
    return searchableText.includes(searchTerm);
  });
}

function matchesSubmissionFilter(submission, filterValue) {
  if (filterValue === "all") {
    return true;
  }
  if (filterValue === "pending") {
    return submission.status === "submitted" || submission.status === "under_review";
  }
  return submission.status === filterValue;
}

function getFilteredSubmissions(submissions) {
  return submissions.filter((submission) =>
    matchesSubmissionFilter(submission, state.submissionFilter),
  );
}

function getSubmissionFilterCount(submissions, filterValue) {
  return submissions.filter((submission) => matchesSubmissionFilter(submission, filterValue)).length;
}

function resetAssignmentsView() {
  state.selectedSessionId = null;
  state.openCardModal = null;
  state.search = "";
  state.statusFilter = "all";
  state.submissionFilter = "all";
}

function syncAssignmentModalState(isOpen) {
  document.body.classList.toggle("has-assignment-modal", isOpen);
}

function closeAssignmentModal(shouldRender = true) {
  state.openCardModal = null;
  syncAssignmentModalState(false);
  if (shouldRender) {
    void renderAssignmentsPage();
  }
}

function handleGlobalKeydown(event) {
  if (event.key !== "Escape") {
    return;
  }
  if (!state.openCardModal) {
    return;
  }
  event.preventDefault();
  closeAssignmentModal();
}

function getCardActionState(sessionId, kind) {
  return (
    state.cardActionStates[`${sessionId}:${kind}`] ?? {
      status: "idle",
      message: "",
    }
  );
}

function setCardActionState(sessionId, kind, actionState) {
  state.cardActionStates[`${sessionId}:${kind}`] = actionState;
}

function getSubmissionGradeState(submissionId) {
  return (
    state.submissionGradeStates[submissionId] ?? {
      status: "idle",
      message: "",
    }
  );
}

function setSubmissionGradeState(submissionId, actionState) {
  state.submissionGradeStates[submissionId] = actionState;
}

function getOpenCardModal(workspace, conceptsDocument) {
  if (!state.openCardModal || state.openCardModal.sessionId !== workspace.sessionId) {
    return null;
  }

  if (state.openCardModal.kind === "assignment") {
    const assignment = workspace.assignmentLookup.get(state.openCardModal.assignmentRequirementId);
    if (!assignment) {
      state.openCardModal = null;
      return null;
    }
    return {
      kind: "assignment",
      assignment,
    };
  }

  if (state.openCardModal.kind === "concepts") {
    return {
      kind: "concepts",
      conceptsDocument,
    };
  }

  if (state.openCardModal.kind === "requirements") {
    return {
      kind: "requirements",
      storedAssignmentRequirements: workspace.storedAssignmentRequirements,
    };
  }

  if (state.openCardModal.kind === "submission") {
    const submission = workspace.submissions.find(
      (submissionItem) => submissionItem.submission_id === state.openCardModal.submissionId,
    );
    if (!submission) {
      state.openCardModal = null;
      return null;
    }
    return {
      kind: "submission",
      submission,
    };
  }

  state.openCardModal = null;
  return null;
}

async function renderAssignmentsPage() {
  try {
    await ensureSessionsLoaded();
    if (state.sessions.length === 0) {
      dom.pageContent.innerHTML = '<div class="empty-state">No sessions are stored yet.</div>';
      return;
    }
    if (!state.selectedSessionId) {
      syncAssignmentModalState(false);
      setPageHeading(
        "Assignments",
        "Choose a session to inspect assignments and submissions.",
      );
      dom.pageHeaderActions.innerHTML = "";
      dom.pageContent.innerHTML = renderSessionOverview();
      bindSessionOverviewInteractions();
      return;
    }

    const [workspace, conceptsDocument] = await Promise.all([
      ensureSessionWorkspaceLoaded(state.selectedSessionId),
      ensureSessionConceptsLoaded(state.selectedSessionId),
    ]);
    const filteredAssignments = getFilteredAssignments(workspace);
    const selectedAssignment = getSelectedAssignment(workspace);
    const openAssignmentModal = getOpenCardModal(workspace, conceptsDocument);
    const session = getSessionById(state.selectedSessionId);
    const conceptsActionState = getCardActionState(workspace.sessionId, "concepts");
    const requirementsActionState = getCardActionState(workspace.sessionId, "requirements");

    setPageHeading(session?.session_title ?? "Session");
    dom.pageHeaderActions.innerHTML = "";

    dom.pageContent.innerHTML = `
      <section class="assignment-strip-list">
        ${
          filteredAssignments.length === 0
            ? '<div class="empty-state">No assignments are stored for this session.</div>'
            : filteredAssignments
                .map((assignment) => renderAssignmentStripCard(assignment))
                .join("")
        }
        ${renderConceptStripCard(conceptsDocument, conceptsActionState)}
        ${renderRequirementsStripCard(workspace, requirementsActionState)}
      </section>
      ${
        selectedAssignment
          ? `<section class="details-panel panel">${renderAssignmentDataSections(selectedAssignment, conceptsDocument, workspace.sessionId)}</section>`
          : ""
      }
      ${renderAssignmentModal(openAssignmentModal)}
    `;

    syncAssignmentModalState(Boolean(openAssignmentModal));
    injectIcons();
    bindAssignmentInteractions(workspace);
    bindSubmissionFilterInteractions();
    bindSubmissionGradeInteractions();
    bindSubmissionRowInteractions();
    bindAssignmentModalInteractions();
  } catch (error) {
    syncAssignmentModalState(false);
    dom.pageContent.innerHTML = `<div class="error-state">${escapeHtml(error.message)}</div>`;
  }
}

function renderSessionOverview() {
  return `
    <div class="session-overview-grid">
      ${state.sessions.map((session, index) => renderSessionCard(session, index)).join("")}
    </div>
  `;
}

function renderSessionCard(session, index) {
  const accentStyle = buildAccentStyle(
    SESSION_CARD_ACCENTS[index % SESSION_CARD_ACCENTS.length],
  );
  return `
    <button
      class="session-overview-card panel"
      type="button"
      data-session-card-id="${session.session_id}"
      style="${accentStyle}"
    >
      <div class="session-overview-card-header">
        <h2 class="session-overview-card-title">${escapeHtml(session.session_title)}</h2>
        <span class="course-status-pill">Active</span>
      </div>
      <p class="session-overview-card-copy">${escapeHtml(getSessionTopicCardCopy(session.session_topic))}</p>
    </button>
  `;
}

function renderAssignmentCard(assignment) {
  const primaryStatus = getPrimaryStatus(assignment);
  const isActive = assignment.assignmentRequirementId === state.selectedAssignmentIds[state.selectedSessionId];
  const accentStyle = buildAccentStyle(
    ASSIGNMENT_STATUS_ACCENTS[primaryStatus] ?? ASSIGNMENT_STATUS_ACCENTS.no_submissions,
  );
  return `
    <button
      class="assignment-card ${isActive ? "is-active" : ""}"
      type="button"
      data-assignment-id="${assignment.assignmentRequirementId}"
      style="${accentStyle}"
    >
      <div class="assignment-card-header">
        <h3 class="assignment-card-title">${escapeHtml(assignment.title)}</h3>
        <span class="status-pill status-${primaryStatus}">${formatStatusLabel(primaryStatus)}</span>
      </div>
      <div class="assignment-card-description">
        ${escapeHtml(assignment.description || "No assignment description stored yet.")}
      </div>
      <div class="assignment-card-footer">
        <span class="meta-pill">${formatDate(assignment.dueAt)}</span>
        <span class="meta-pill">${assignment.requiredDeliverables.length} deliverables</span>
        <span class="meta-pill">${assignment.requirements.length} extracted requirements</span>
        <span class="meta-pill">${assignment.counts.total} submissions</span>
      </div>
    </button>
  `;
}

function renderAssignmentStripCard(assignment) {
  const isSelected =
    assignment.assignmentRequirementId === state.selectedAssignmentIds[state.selectedSessionId];
  const accentStyle = buildAccentStyle(
    ASSIGNMENT_STATUS_ACCENTS[getPrimaryStatus(assignment)] ?? ASSIGNMENT_STATUS_ACCENTS.no_submissions,
  );
  return `
    <button
      class="assignment-strip-card panel ${isSelected ? "is-selected" : ""}"
      type="button"
      data-card-kind="assignment"
      data-assignment-id="${assignment.assignmentRequirementId}"
      aria-haspopup="dialog"
      style="${accentStyle}"
    >
      <div class="assignment-strip-main">
        <div class="assignment-strip-copy">
          <p class="assignment-strip-kicker">Assignment</p>
          <h2 class="assignment-strip-title">${escapeHtml(assignment.title)}</h2>
          <p class="assignment-strip-description">${escapeHtml(
            getSessionTopicCardCopy(
              assignment.description || "No assignment description stored yet.",
              220,
            ),
          )}</p>
        </div>
        <div class="assignment-strip-meta">
          <span class="summary-pill">${assignment.counts.total} submissions</span>
          <span class="summary-pill">${formatDate(assignment.dueAt)}</span>
        </div>
      </div>
      ${
        assignment.requiredDeliverables.length > 0
          ? `
            <div class="assignment-strip-deliverables">
              <div class="detail-metadata">
                ${assignment.requiredDeliverables.map((deliverable) => `<span class="detail-tag">${escapeHtml(deliverable)}</span>`).join("")}
              </div>
            </div>
          `
          : ""
      }
    </button>
  `;
}

function renderConceptStripCard(conceptsDocument, actionState) {
  const accentStyle = buildAccentStyle(SESSION_RESOURCE_CARD_ACCENTS.concepts);
  const conceptCount = conceptsDocument.concepts.length;
  const description =
    conceptCount > 0
      ? "Stored gradeable concepts are available for this session."
      : "No stored concepts are available for this session yet.";
  return renderSessionResourceCard({
    kind: "concepts",
    kicker: "Concepts",
    title: "Stored Session Concepts",
    description,
    metaItems: [`${conceptCount} stored`],
    tags: [],
    buttonLabel: "Synthesize",
    actionState,
    accentStyle,
  });
}

function renderRequirementsStripCard(workspace, actionState) {
  const accentStyle = buildAccentStyle(SESSION_RESOURCE_CARD_ACCENTS.requirements);
  const storedAssignments = workspace.storedAssignmentRequirements;
  const description =
    storedAssignments.length > 0
      ? `${storedAssignments.length} stored assignment${storedAssignments.length === 1 ? "" : "s"} currently include requirement data.`
      : "No stored assignments are available for this session yet.";
  return renderSessionResourceCard({
    kind: "requirements",
    kicker: "Requirements",
    title: "Stored Assignment Requirements",
    description,
    metaItems: [`${storedAssignments.length} stored`],
    tags: [],
    buttonLabel: "Synthesize",
    actionState,
    accentStyle,
  });
}

function renderSessionResourceCard({
  kind,
  kicker,
  title,
  description,
  metaItems,
  tags,
  buttonLabel,
  actionState,
  accentStyle,
}) {
  return `
    <article class="assignment-strip-card panel session-resource-card" style="${accentStyle}">
      <button
        class="session-resource-open"
        type="button"
        data-card-kind="${kind}"
        aria-haspopup="dialog"
      >
        <div class="assignment-strip-main">
          <div class="assignment-strip-copy">
            <p class="assignment-strip-kicker">${escapeHtml(kicker)}</p>
            <h2 class="assignment-strip-title">${escapeHtml(title)}</h2>
            <p class="assignment-strip-description">${escapeHtml(
              getSessionTopicCardCopy(description, 220),
            )}</p>
          </div>
          <div class="assignment-strip-meta">
            ${metaItems.map((item) => `<span class="summary-pill">${escapeHtml(item)}</span>`).join("")}
          </div>
        </div>
        ${
          tags.length > 0
            ? `
              <div class="assignment-strip-deliverables">
                <div class="detail-metadata">
                  ${tags.map((tag) => `<span class="detail-tag">${escapeHtml(tag)}</span>`).join("")}
                </div>
              </div>
            `
            : ""
        }
      </button>
      <div class="session-resource-footer">
        <button
          class="session-resource-action"
          type="button"
          data-synthesize-kind="${kind}"
          ${actionState.status === "loading" ? "disabled" : ""}
        >
          ${actionState.status === "loading" ? "Synthesizing..." : escapeHtml(buttonLabel)}
        </button>
        ${
          actionState.message
            ? `<div class="session-resource-feedback ${actionState.status === "error" ? "is-error" : ""}">${escapeHtml(actionState.message)}</div>`
            : ""
        }
      </div>
    </article>
  `;
}

function renderAssignmentModal(modalState) {
  if (!modalState) {
    return "";
  }

  if (modalState.kind === "assignment") {
    return renderAssignmentDetailModal(modalState.assignment);
  }
  if (modalState.kind === "concepts") {
    return renderConceptsDetailModal(modalState.conceptsDocument);
  }
  if (modalState.kind === "submission") {
    return renderSubmissionDetailModal(modalState.submission);
  }
  return renderRequirementsDetailModal(modalState.storedAssignmentRequirements);
}

function renderAssignmentDetailModal(assignment) {
  const primaryStatus = getPrimaryStatus(assignment);
  return `
    <div class="assignment-modal-screen" data-assignment-modal-backdrop="true">
      <article
        class="assignment-modal-card panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="assignment-modal-title"
      >
        <div class="assignment-modal-header">
          <div class="assignment-modal-heading">
            <p class="assignment-strip-kicker">Assignment</p>
            <h2 class="assignment-modal-title" id="assignment-modal-title">${escapeHtml(assignment.title)}</h2>
          </div>
          <button
            class="assignment-modal-close"
            type="button"
            aria-label="Close assignment details"
            data-assignment-modal-close="true"
          >
            <span data-icon="close"></span>
          </button>
        </div>
        <div class="assignment-modal-meta">
          <span class="status-pill status-${primaryStatus}">${formatStatusLabel(primaryStatus)}</span>
          <span class="summary-pill">${assignment.counts.total} submissions</span>
          <span class="summary-pill">${assignment.requirements.length} requirements</span>
          <span class="summary-pill">${formatDate(assignment.dueAt)}</span>
        </div>
        <div class="assignment-modal-body">
          <p class="assignment-modal-description">${escapeHtml(
            assignment.description || "No assignment description stored yet.",
          )}</p>
          ${
            assignment.requiredDeliverables.length > 0
              ? `
                <section class="assignment-modal-section">
                  <h3 class="assignment-modal-section-title">Deliverables</h3>
                  <div class="detail-metadata">
                    ${assignment.requiredDeliverables.map((deliverable) => `<span class="detail-tag">${escapeHtml(deliverable)}</span>`).join("")}
                  </div>
                </section>
              `
              : ""
          }
        </div>
      </article>
    </div>
  `;
}

function renderConceptsDetailModal(conceptsDocument) {
  return `
    <div class="assignment-modal-screen" data-assignment-modal-backdrop="true">
      <article
        class="assignment-modal-card panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="assignment-modal-title"
      >
        <div class="assignment-modal-header">
          <div class="assignment-modal-heading">
            <p class="assignment-strip-kicker">Concepts</p>
            <h2 class="assignment-modal-title" id="assignment-modal-title">Stored Session Concepts</h2>
          </div>
          <button
            class="assignment-modal-close"
            type="button"
            aria-label="Close concepts details"
            data-assignment-modal-close="true"
          >
            <span data-icon="close"></span>
          </button>
        </div>
        <div class="assignment-modal-meta">
          <span class="summary-pill">${conceptsDocument.concepts.length} concepts</span>
        </div>
        <div class="assignment-modal-body">
          <div class="assignment-modal-status" data-modal-editor-status></div>
          <div class="requirements-list" data-concepts-list>
            ${conceptsDocument.concepts.map((concept, index) => renderEditableConceptItem(concept, index)).join("")}
          </div>
          <div class="empty-state" data-concepts-empty ${conceptsDocument.concepts.length === 0 ? "" : "hidden"}>
            No concepts remain in this payload.
          </div>
          <div class="assignment-modal-actions">
            <button class="assignment-modal-save" type="button" data-modal-save-kind="concepts">
              Save Changes
            </button>
          </div>
        </div>
      </article>
    </div>
  `;
}

function renderRequirementsDetailModal(storedAssignments) {
  const totalRequirements = storedAssignments.reduce(
    (sum, assignment) => sum + assignment.requirements.length,
    0,
  );
  let requirementIndex = 0;
  return `
    <div class="assignment-modal-screen" data-assignment-modal-backdrop="true">
      <article
        class="assignment-modal-card panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="assignment-modal-title"
      >
        <div class="assignment-modal-header">
          <div class="assignment-modal-heading">
            <p class="assignment-strip-kicker">Requirements</p>
            <h2 class="assignment-modal-title" id="assignment-modal-title">Stored Assignment Requirements</h2>
          </div>
          <button
            class="assignment-modal-close"
            type="button"
            aria-label="Close assignment requirement details"
            data-assignment-modal-close="true"
          >
            <span data-icon="close"></span>
          </button>
        </div>
        <div class="assignment-modal-meta">
          <span class="summary-pill">${storedAssignments.length} stored assignments</span>
          <span class="summary-pill">${totalRequirements} requirements</span>
        </div>
        <div class="assignment-modal-body">
          <div class="assignment-modal-status" data-modal-editor-status></div>
          ${
            storedAssignments.length === 0
              ? '<div class="empty-state" data-requirements-empty>No stored requirements are available for this session yet.</div>'
              : `
                <div class="requirements-list" data-requirements-list>
                  ${storedAssignments
                    .map((assignment) => {
                      const groupMarkup = renderEditableAssignmentRequirementGroup(
                        assignment,
                        requirementIndex,
                      );
                      requirementIndex += assignment.requirements.length;
                      return groupMarkup;
                    })
                    .join("")}
                </div>
                <div class="empty-state" data-requirements-empty ${totalRequirements === 0 ? "" : "hidden"}>
                  No stored requirements are available for this session yet.
                </div>
              `
          }
          <div class="assignment-modal-actions">
            <button class="assignment-modal-save" type="button" data-modal-save-kind="requirements">
              Save Changes
            </button>
          </div>
        </div>
      </article>
    </div>
  `;
}

function renderSubmissionDetailModal(submission) {
  const conceptScores = normalizeScoreItems(submission.concept_scores);
  const assignmentRequirementScores = normalizeScoreItems(
    submission.assignment_requirement_scores,
  );
  const rubricScores = normalizeScoreItems(submission.rubric_scores);
  return `
    <div class="assignment-modal-screen" data-assignment-modal-backdrop="true">
      <article
        class="assignment-modal-card submission-detail-modal panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="assignment-modal-title"
      >
        <div class="assignment-modal-header">
          <div class="assignment-modal-heading">
            <p class="assignment-strip-kicker">Submission</p>
            <h2 class="assignment-modal-title" id="assignment-modal-title">${escapeHtml(submission.student_full_name)}</h2>
            <p class="submission-detail-subtitle">${escapeHtml(submission.assignment_title)} · ${escapeHtml(submission.student_code)}</p>
          </div>
          <button
            class="assignment-modal-close"
            type="button"
            aria-label="Close submission details"
            data-assignment-modal-close="true"
          >
            <span data-icon="close"></span>
          </button>
        </div>
        <div class="assignment-modal-meta">
          <span class="status-pill status-${submission.status}">${formatStatusLabel(submission.status)}</span>
          <span class="summary-pill">${escapeHtml(prettySourceType(submission.source_type))}</span>
          <span class="summary-pill">${formatDateTime(submission.submitted_at)}</span>
        </div>
        <div class="assignment-modal-body">
          <section class="assignment-modal-section submission-score-overview">
            ${renderSubmissionScoreStat("Concepts", conceptScores)}
            ${renderSubmissionScoreStat("Requirements", assignmentRequirementScores)}
            ${renderSubmissionScoreStat("Rubric", rubricScores)}
          </section>
          ${renderSubmissionScoreSection(
            "Concept Scores",
            conceptScores,
            "No concept scores are stored for this submission yet.",
            "concept",
          )}
          ${renderSubmissionScoreSection(
            "Assignment Requirement Scores",
            assignmentRequirementScores,
            "No assignment requirement scores are stored for this submission yet.",
            "requirement",
          )}
          ${renderSubmissionScoreSection(
            "Rubric Scores",
            rubricScores,
            "No rubric scores are stored for this submission yet.",
            "rubric",
          )}
        </div>
      </article>
    </div>
  `;
}

function renderSubmissionScoreStat(label, scoreItems) {
  const totals = summarizeScoreItems(scoreItems);
  return `
    <div class="submission-score-stat">
      <div class="submission-score-stat-label">${escapeHtml(label)}</div>
      <div class="submission-score-stat-value">${escapeHtml(totals.compactValue)}</div>
    </div>
  `;
}

function renderSubmissionScoreSection(title, scoreItems, emptyMessage, scoreType) {
  return `
    <section class="assignment-modal-section assignment-modal-section-framed">
      <div class="submission-score-section-header">
        <h3 class="assignment-modal-section-title">${escapeHtml(title)}</h3>
        <span class="summary-pill">${scoreItems.length} stored</span>
      </div>
      ${
        scoreItems.length === 0
          ? `<div class="empty-state submission-modal-empty-state">${escapeHtml(emptyMessage)}</div>`
          : `<div class="submission-score-list">${scoreItems
              .map((scoreItem, index) => renderSubmissionScoreItem(scoreItem, index, scoreType))
              .join("")}</div>`
      }
    </section>
  `;
}

function renderSubmissionScoreItem(scoreItem, index, scoreType) {
  const label = getSubmissionScoreItemLabel(scoreItem, index, scoreType);
  const scoreValue = getSubmissionScoreValue(scoreItem);
  const evidence = Array.isArray(scoreItem.evidence)
    ? scoreItem.evidence.map((evidenceItem) => String(evidenceItem))
    : [];
  const deductions = Array.isArray(scoreItem.deductions)
    ? scoreItem.deductions.map((deductionItem) => String(deductionItem))
    : [];
  const coverageLevel =
    typeof scoreItem.coverage_level === "string" ? formatCoverageLabel(scoreItem.coverage_level) : null;
  return `
    <article class="submission-score-item">
      <div class="submission-score-item-top">
        <div>
          <h4 class="submission-score-item-title">${escapeHtml(label)}</h4>
          ${
            coverageLevel
              ? `<p class="submission-score-item-meta">${escapeHtml(coverageLevel)}</p>`
              : ""
          }
        </div>
        ${
          scoreValue
            ? `<span class="submission-score-pill">${escapeHtml(scoreValue)}</span>`
            : ""
        }
      </div>
      ${
        evidence.length > 0
          ? `
            <div class="submission-score-copy-group">
              <div class="submission-score-copy-label">Evidence</div>
              <ul class="evidence-list submission-score-evidence-list">
                ${evidence.map((evidenceItem) => `<li>${escapeHtml(evidenceItem)}</li>`).join("")}
              </ul>
            </div>
          `
          : ""
      }
      ${
        deductions.length > 0
          ? `
            <div class="submission-score-copy-group">
              <div class="submission-score-copy-label">Deductions</div>
              <ul class="evidence-list submission-score-evidence-list">
                ${deductions.map((deductionItem) => `<li>${escapeHtml(deductionItem)}</li>`).join("")}
              </ul>
            </div>
          `
          : ""
      }
    </article>
  `;
}

function renderAssignmentDataSections(assignment, conceptsDocument, sessionId) {
  const filteredSubmissions = getFilteredSubmissions(assignment.submissions);
  return `
    <div class="submissions-board">
      <div class="submission-filter-bar">
        ${SUBMISSION_FILTER_OPTIONS.map(
          (option) => `
            <button
              class="submission-filter-tab ${state.submissionFilter === option.value ? "is-active" : ""}"
              type="button"
              data-submission-filter="${option.value}"
            >
              ${escapeHtml(option.label)} (${getSubmissionFilterCount(assignment.submissions, option.value)})
            </button>
          `,
        ).join("")}
      </div>
      ${
        assignment.submissions.length === 0
          ? '<div class="empty-state submission-empty-state">No student submission has been attached to this assignment yet.</div>'
          : filteredSubmissions.length === 0
            ? '<div class="empty-state submission-empty-state">No submissions match this filter yet.</div>'
            : `<div class="submissions-list">${filteredSubmissions
                .map((submission) => renderSubmissionRow(submission, conceptsDocument, sessionId))
                .join("")}</div>`
      }
    </div>
  `;
}

function renderRequirementItem(requirement) {
  return `
    <article class="requirement-item">
      <div class="requirement-header">
        <h4 class="requirement-title">${escapeHtml(requirement.title)}</h4>
      </div>
      <p class="requirement-summary">${escapeHtml(requirement.summary)}</p>
      <ul class="evidence-list">
        ${requirement.evidence.map((evidenceItem) => `<li>${escapeHtml(evidenceItem)}</li>`).join("")}
      </ul>
    </article>
  `;
}

function renderConceptItem(concept) {
  return `
    <article class="requirement-item">
      <div class="requirement-header">
        <div>
          <h4 class="requirement-title">${escapeHtml(concept.name)}</h4>
          <p class="requirement-meta">Importance ${escapeHtml(String(concept.concept_importance))}/10</p>
        </div>
      </div>
      <p class="requirement-summary">${escapeHtml(concept.summary)}</p>
      <p class="requirement-summary">${escapeHtml(concept.grading_reason)}</p>
      <ul class="evidence-list">
        ${concept.evidence.map((evidenceItem) => `<li>${escapeHtml(evidenceItem)}</li>`).join("")}
      </ul>
    </article>
  `;
}

function renderEditableConceptItem(concept, index) {
  return `
    <article class="requirement-item editor-item" data-concept-item>
      <div class="editor-item-header">
        <h4 class="requirement-title">Concept ${index + 1}</h4>
        <div class="editor-actions">
          <button
            class="editor-icon-button"
            type="button"
            data-toggle-edit="true"
            title="Edit concept"
            aria-label="Edit concept"
          >
            <span data-icon="edit"></span>
          </button>
          <button
            class="editor-icon-button is-danger"
            type="button"
            data-remove-concept="true"
            title="Remove concept"
            aria-label="Remove concept"
          >
            <span data-icon="trash"></span>
          </button>
        </div>
      </div>
      <div class="editor-preview">
        <div class="editor-preview-top">
          <div class="editor-preview-heading">
            <h5 class="editor-preview-title">${escapeHtml(concept.name)}</h5>
            <p class="editor-preview-meta">Importance ${escapeHtml(String(concept.concept_importance))}/10</p>
          </div>
        </div>
        <p class="editor-preview-copy">${escapeHtml(concept.summary)}</p>
        <p class="editor-preview-copy is-secondary">${escapeHtml(concept.grading_reason)}</p>
        <ul class="evidence-list">
          ${concept.evidence.map((evidenceItem) => `<li>${escapeHtml(evidenceItem)}</li>`).join("")}
        </ul>
      </div>
      <div class="editor-form">
        <div class="editor-grid editor-grid-concept">
          <label class="editor-field">
            <span class="visually-hidden">Concept name</span>
            <input
              class="editor-input"
              type="text"
              data-field="name"
              placeholder="Concept name"
              value="${escapeAttribute(concept.name)}"
            />
          </label>
          <label class="editor-field editor-field-compact">
            <span class="visually-hidden">Importance</span>
            <input
              class="editor-input"
              type="number"
              min="1"
              max="10"
              step="1"
              data-field="concept_importance"
              placeholder="Importance"
              value="${escapeAttribute(String(concept.concept_importance))}"
            />
          </label>
        </div>
        <label class="editor-field">
          <span class="visually-hidden">Summary</span>
          <textarea
            class="editor-textarea editor-textarea-compact"
            rows="3"
            data-field="summary"
            placeholder="Summary"
          >${escapeHtml(concept.summary)}</textarea>
        </label>
        <label class="editor-field">
          <span class="visually-hidden">Grading reason</span>
          <textarea
            class="editor-textarea editor-textarea-compact"
            rows="3"
            data-field="grading_reason"
            placeholder="Grading reason"
          >${escapeHtml(concept.grading_reason)}</textarea>
        </label>
        <label class="editor-field">
          <span class="visually-hidden">Evidence</span>
          <textarea
            class="editor-textarea editor-textarea-evidence"
            rows="5"
            data-field="evidence"
            placeholder="One evidence line per row"
          >${escapeHtml(concept.evidence.join("\n"))}</textarea>
        </label>
      </div>
    </article>
  `;
}

function renderEditableAssignmentRequirementGroup(assignment, startIndex) {
  return `
    <section
      class="assignment-requirement-group-shell"
      data-assignment-requirement-group
      data-assignment-requirement-id="${escapeAttribute(assignment.assignment_requirement_id)}"
      data-assignment-title="${escapeAttribute(assignment.assignment_title)}"
      data-assignment-description="${escapeAttribute(assignment.assignment_description ?? "")}"
      data-due-at="${escapeAttribute(assignment.due_at ?? "")}"
      data-required-deliverables="${escapeAttribute(JSON.stringify(assignment.required_deliverables ?? []))}"
    >
      <div class="requirements-list" data-requirement-list>
        ${assignment.requirements
          .map((requirement, index) => renderEditableRequirementItem(requirement, startIndex + index))
          .join("")}
      </div>
    </section>
  `;
}

function renderEditableRequirementItem(requirement, index) {
  return `
    <article class="requirement-item editor-item" data-requirement-item>
      <div class="editor-item-header">
        <h4 class="requirement-title">Requirement ${index + 1}</h4>
        <div class="editor-actions">
          <button
            class="editor-icon-button"
            type="button"
            data-toggle-edit="true"
            title="Edit requirement"
            aria-label="Edit requirement"
          >
            <span data-icon="edit"></span>
          </button>
          <button
            class="editor-icon-button is-danger"
            type="button"
            data-remove-requirement="true"
            title="Remove requirement"
            aria-label="Remove requirement"
          >
            <span data-icon="trash"></span>
          </button>
        </div>
      </div>
      <div class="editor-preview">
        <div class="editor-preview-top">
          <h5 class="editor-preview-title">${escapeHtml(requirement.title)}</h5>
        </div>
        <p class="editor-preview-copy">${escapeHtml(requirement.summary)}</p>
        <ul class="evidence-list">
          ${requirement.evidence.map((evidenceItem) => `<li>${escapeHtml(evidenceItem)}</li>`).join("")}
        </ul>
      </div>
      <div class="editor-form">
        <div class="editor-grid editor-grid-requirement">
          <label class="editor-field">
            <span class="visually-hidden">Requirement type</span>
            <select class="editor-select" data-field="requirement_type">
              ${REQUIREMENT_TYPE_OPTIONS.map(
                (option) => `
                  <option value="${escapeAttribute(option.value)}" ${option.value === requirement.requirement_type ? "selected" : ""}>
                    ${escapeHtml(option.label)}
                  </option>
                `,
              ).join("")}
            </select>
          </label>
          <label class="editor-field">
            <span class="visually-hidden">Title</span>
            <input
              class="editor-input"
              type="text"
              data-field="title"
              placeholder="Requirement title"
              value="${escapeAttribute(requirement.title)}"
            />
          </label>
        </div>
        <label class="editor-field">
          <span class="visually-hidden">Summary</span>
          <textarea
            class="editor-textarea editor-textarea-compact"
            rows="3"
            data-field="summary"
            placeholder="Requirement summary"
          >${escapeHtml(requirement.summary)}</textarea>
        </label>
        <label class="editor-field">
          <span class="visually-hidden">Evidence</span>
          <textarea
            class="editor-textarea editor-textarea-evidence"
            rows="5"
            data-field="evidence"
            placeholder="One evidence line per row"
          >${escapeHtml(requirement.evidence.join("\n"))}</textarea>
        </label>
      </div>
    </article>
  `;
}

function renderSubmissionRow(submission, conceptsDocument, sessionId) {
  const detailLinks = [];
  const conceptScores = normalizeScoreItems(submission.concept_scores);
  const assignmentRequirementScores = normalizeScoreItems(
    submission.assignment_requirement_scores,
  );
  const rubricScores = normalizeScoreItems(submission.rubric_scores);
  const hasStoredConcepts = conceptsDocument.concepts.length > 0;
  const hasValidSourceLocator = hasSubmissionSourceLocator(submission);
  const actionState = getSubmissionGradeState(submission.submission_id);
  const isLoading = actionState.status === "loading";
  const isDisabled = !hasStoredConcepts || !hasValidSourceLocator || isLoading;
  const actionLabel = isLoading
    ? "Grading..."
    : !hasStoredConcepts
      ? "No Concepts"
      : !hasValidSourceLocator
        ? "Source Missing"
        : "Grade Concepts";
  const conceptScoreSummary = summarizeScoreItems(conceptScores);
  const requirementScoreSummary = summarizeScoreItems(assignmentRequirementScores);
  const rubricScoreSummary = summarizeScoreItems(rubricScores);
  if (submission.repo_url) {
    detailLinks.push(renderSubmissionLink(submission.repo_url, "Repository", "github"));
  }
  if (submission.youtube_demo_url) {
    detailLinks.push(renderSubmissionLink(submission.youtube_demo_url, "Demo", "play"));
  }
  if (submission.linkedin_url) {
    detailLinks.push(renderSubmissionLink(submission.linkedin_url, "LinkedIn", "briefcase"));
  }

  return `
    <article
      class="submission-row"
      data-open-submission="true"
      data-session-id="${escapeAttribute(sessionId)}"
      data-submission-id="${escapeAttribute(submission.submission_id)}"
      role="button"
      tabindex="0"
      aria-haspopup="dialog"
    >
      <div class="submission-row-leading">
        <span class="submission-status-mark status-${submission.status}">
          <span data-icon="${getSubmissionStatusIcon(submission.status)}"></span>
        </span>
        <div class="submission-copy">
          <p class="submission-name">${escapeHtml(submission.student_full_name)}</p>
          <p class="submission-code">
            ${escapeHtml(submission.student_code)} · ${escapeHtml(prettySourceType(submission.source_type))} · ${escapeHtml(formatDate(submission.submitted_at))}
          </p>
        </div>
      </div>
      <div class="submission-row-meta">
        ${
          detailLinks.length > 0
            ? `<div class="submission-link-icons">${detailLinks.join("")}</div>`
            : ""
        }
        <div class="submission-grade-summary">
          ${renderSubmissionScoreSummaryPill("C", conceptScoreSummary)}
          ${renderSubmissionScoreSummaryPill("A", requirementScoreSummary)}
          ${renderSubmissionScoreSummaryPill("R", rubricScoreSummary)}
        </div>
        <div class="submission-action-stack">
          <button
            class="submission-grade-button ${actionState.status === "success" ? "is-success" : ""} ${actionState.status === "error" ? "is-error" : ""}"
            type="button"
            data-grade-concepts="true"
            data-session-id="${escapeAttribute(sessionId)}"
            data-submission-id="${escapeAttribute(submission.submission_id)}"
            ${isDisabled ? "disabled" : ""}
          >
            ${escapeHtml(actionLabel)}
          </button>
          ${
            actionState.message
              ? `<p class="submission-action-feedback ${actionState.status === "error" ? "is-error" : ""}">${escapeHtml(actionState.message)}</p>`
              : ""
          }
        </div>
        <span class="status-pill status-${submission.status}">${formatStatusLabel(submission.status)}</span>
        <span class="submission-row-chevron" data-icon="chevronRight"></span>
      </div>
    </article>
  `;
}

function renderSubmissionScoreSummaryPill(label, scoreSummary) {
  return `
    <span class="submission-score-summary-pill">
      <span class="submission-score-summary-label">${escapeHtml(label)}</span>
      <span class="submission-score-summary-value">${escapeHtml(scoreSummary.compactValue)}</span>
    </span>
  `;
}

function hasSubmissionSourceLocator(submission) {
  if (submission.source_type === "github_pr") {
    return Boolean(submission.repo_url);
  }
  if (submission.source_type === "local_folder") {
    return Boolean(submission.local_path);
  }
  if (submission.source_type === "zip_upload") {
    return Boolean(submission.zip_path);
  }
  return false;
}

function buildGradeConceptsPayload(submission, conceptsDocument, sessionId) {
  if (conceptsDocument.concepts.length === 0) {
    throw new Error("No stored concepts are available for this session.");
  }
  if (!hasSubmissionSourceLocator(submission)) {
    throw new Error("This submission is missing its source locator.");
  }

  return {
    student_id: submission.student_id,
    session_id: sessionId,
    source_type: submission.source_type,
    ...(submission.repo_url ? { repo_url: submission.repo_url } : {}),
    ...(submission.local_path ? { local_path: submission.local_path } : {}),
    ...(submission.zip_path ? { zip_path: submission.zip_path } : {}),
    reasoning_level: "medium",
    concepts: conceptsDocument.concepts.map((concept) => ({
      concept_name: concept.name,
      summary: concept.summary,
      grading_reason: concept.grading_reason,
      max_score: concept.concept_importance,
    })),
  };
}

function normalizeScoreItems(scoreItems) {
  return Array.isArray(scoreItems) ? scoreItems : [];
}

function summarizeScoreItems(scoreItems) {
  const normalizedScoreItems = normalizeScoreItems(scoreItems);
  let totalScore = 0;
  let totalMaxScore = 0;
  let hasNumericScores = false;
  for (const scoreItem of normalizedScoreItems) {
    if (
      typeof scoreItem.score === "number"
      && Number.isFinite(scoreItem.score)
      && typeof scoreItem.max_score === "number"
      && Number.isFinite(scoreItem.max_score)
    ) {
      totalScore += scoreItem.score;
      totalMaxScore += scoreItem.max_score;
      hasNumericScores = true;
    }
  }

  if (hasNumericScores) {
    return {
      compactValue: `${totalScore}/${totalMaxScore}`,
      totalScore,
      totalMaxScore,
    };
  }

  if (normalizedScoreItems.length > 0) {
    return {
      compactValue: String(normalizedScoreItems.length),
      totalScore: null,
      totalMaxScore: null,
    };
  }

  return {
    compactValue: "--",
    totalScore: null,
    totalMaxScore: null,
  };
}

function getSubmissionScoreItemLabel(scoreItem, index, scoreType) {
  const labelCandidates = [
    scoreItem.concept,
    scoreItem.requirement_title,
    scoreItem.criterion,
    scoreItem.title,
    scoreItem.name,
  ];
  const matchedLabel = labelCandidates.find(
    (candidate) => typeof candidate === "string" && normalizeDisplayText(candidate),
  );
  if (matchedLabel) {
    return normalizeDisplayText(matchedLabel);
  }
  if (scoreType === "concept") {
    return `Concept ${index + 1}`;
  }
  if (scoreType === "requirement") {
    return `Requirement ${index + 1}`;
  }
  return `Rubric ${index + 1}`;
}

function getSubmissionScoreValue(scoreItem) {
  if (
    typeof scoreItem.score === "number"
    && Number.isFinite(scoreItem.score)
    && typeof scoreItem.max_score === "number"
    && Number.isFinite(scoreItem.max_score)
  ) {
    return `${scoreItem.score}/${scoreItem.max_score}`;
  }
  if (typeof scoreItem.score === "number" && Number.isFinite(scoreItem.score)) {
    return String(scoreItem.score);
  }
  return null;
}

function formatCoverageLabel(coverageLevel) {
  return coverageLevel
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function getSubmissionStatusIcon(status) {
  if (status === "reviewed") {
    return "circleCheck";
  }
  if (status === "needs_resubmission") {
    return "alertCircle";
  }
  if (status === "under_review") {
    return "loader";
  }
  return "clock3";
}

function renderSubmissionLink(url, label, iconName) {
  return `
    <a
      class="submission-link-icon"
      href="${escapeAttribute(url)}"
      target="_blank"
      rel="noreferrer"
      title="${escapeAttribute(label)}"
      aria-label="${escapeAttribute(label)}"
    >
      <span data-icon="${iconName}"></span>
    </a>
  `;
}

function bindAssignmentInteractions(workspace) {
  document.querySelectorAll("[data-card-kind]").forEach((button) => {
    button.addEventListener("click", () => {
      const cardKind = button.getAttribute("data-card-kind");
      if (!cardKind) {
        return;
      }
      if (cardKind === "assignment") {
        const assignmentId = button.getAttribute("data-assignment-id");
        if (!assignmentId) {
          return;
        }
        state.selectedAssignmentIds[workspace.sessionId] = assignmentId;
        state.submissionFilter = "all";
        state.openCardModal = {
          kind: "assignment",
          sessionId: workspace.sessionId,
          assignmentRequirementId: assignmentId,
        };
      } else {
        state.openCardModal = {
          kind: cardKind,
          sessionId: workspace.sessionId,
        };
      }
      void renderAssignmentsPage();
    });
  });

  document.querySelectorAll("[data-synthesize-kind]").forEach((button) => {
    button.addEventListener("click", async () => {
      const synthesizeKind = button.getAttribute("data-synthesize-kind");
      if (!synthesizeKind) {
        return;
      }
      await synthesizeSessionCard(workspace.sessionId, synthesizeKind);
    });
  });
}

function bindSubmissionFilterInteractions() {
  document.querySelectorAll("[data-submission-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      const filterValue = button.getAttribute("data-submission-filter");
      if (!filterValue || filterValue === state.submissionFilter) {
        return;
      }
      state.submissionFilter = filterValue;
      void renderAssignmentsPage();
    });
  });
}

function bindSubmissionRowInteractions() {
  document.querySelectorAll("[data-open-submission]").forEach((row) => {
    const openSubmissionModal = () => {
      const sessionId = row.getAttribute("data-session-id");
      const submissionId = row.getAttribute("data-submission-id");
      if (!sessionId || !submissionId) {
        return;
      }
      state.openCardModal = {
        kind: "submission",
        sessionId,
        submissionId,
      };
      void renderAssignmentsPage();
    };

    row.addEventListener("click", (event) => {
      const target = event.target;
      if (!(target instanceof Element)) {
        return;
      }
      if (target.closest("a, button")) {
        return;
      }
      openSubmissionModal();
    });

    row.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" && event.key !== " ") {
        return;
      }
      const target = event.target;
      if (target instanceof Element && target.closest("a, button")) {
        return;
      }
      event.preventDefault();
      openSubmissionModal();
    });
  });
}

function bindSubmissionGradeInteractions() {
  document.querySelectorAll("[data-grade-concepts]").forEach((button) => {
    button.addEventListener("click", async () => {
      const sessionId = button.getAttribute("data-session-id");
      const submissionId = button.getAttribute("data-submission-id");
      if (!sessionId || !submissionId) {
        return;
      }
      await gradeSubmissionConcepts(sessionId, submissionId);
    });
  });
}

async function gradeSubmissionConcepts(sessionId, submissionId) {
  const workspace = await ensureSessionWorkspaceLoaded(sessionId);
  const conceptsDocument = await ensureSessionConceptsLoaded(sessionId);
  const submission = workspace.submissions.find(
    (submissionItem) => submissionItem.submission_id === submissionId,
  );
  if (!submission) {
    setSubmissionGradeState(submissionId, {
      status: "error",
      message: "Submission not found.",
    });
    await renderAssignmentsPage();
    return;
  }

  try {
    const payload = buildGradeConceptsPayload(submission, conceptsDocument, sessionId);
    setSubmissionGradeState(submissionId, {
      status: "loading",
      message: "",
    });
    await renderAssignmentsPage();
    const response = await postJson("/grade/concepts", payload);
    invalidateSessionWorkspace(sessionId);
    await ensureSessionWorkspaceLoaded(sessionId);
    setSubmissionGradeState(submissionId, {
      status: "success",
      message: `${response.concept_scores.length} scores saved.`,
    });
  } catch (error) {
    setSubmissionGradeState(submissionId, {
      status: "error",
      message: error instanceof Error ? error.message : "Unable to grade concepts.",
    });
  }

  await renderAssignmentsPage();
}

async function synthesizeSessionCard(sessionId, kind) {
  const endpointByKind = {
    concepts: `/sessions/${sessionId}/extract-concepts`,
    requirements: `/sessions/${sessionId}/extract-assignment-requirements`,
  };
  const successMessageByKind = {
    concepts: "Stored concepts refreshed.",
    requirements: "Stored assignment requirements refreshed.",
  };
  const endpoint = endpointByKind[kind];
  if (!endpoint) {
    return;
  }

  setCardActionState(sessionId, kind, {
    status: "loading",
    message: "",
  });
  await renderAssignmentsPage();

  try {
    await postJson(endpoint, {});
    if (kind === "concepts") {
      invalidateSessionConcepts(sessionId);
      await ensureSessionConceptsLoaded(sessionId);
    } else {
      invalidateSessionWorkspace(sessionId);
      await ensureSessionWorkspaceLoaded(sessionId);
    }
    setCardActionState(sessionId, kind, {
      status: "success",
      message: successMessageByKind[kind],
    });
  } catch (error) {
    setCardActionState(sessionId, kind, {
      status: "error",
      message: error instanceof Error ? error.message : "Unable to complete synthesis.",
    });
  }

  await renderAssignmentsPage();
}

function bindAssignmentModalInteractions() {
  const modalBackdrop = document.querySelector("[data-assignment-modal-backdrop]");
  if (modalBackdrop) {
    modalBackdrop.addEventListener("click", (event) => {
      if (event.target === modalBackdrop) {
        closeAssignmentModal();
      }
    });
  }
  document.querySelectorAll("[data-assignment-modal-close]").forEach((button) => {
    button.addEventListener("click", () => {
      closeAssignmentModal();
    });
  });
  document.querySelectorAll("[data-toggle-edit]").forEach((button) => {
    button.addEventListener("click", () => {
      const editorItem = button.closest(".editor-item");
      if (!editorItem) {
        return;
      }
      editorItem.classList.toggle("is-editing");
      button.classList.toggle("is-active", editorItem.classList.contains("is-editing"));
    });
  });
  document.querySelectorAll("[data-remove-concept]").forEach((button) => {
    button.addEventListener("click", () => {
      button.closest("[data-concept-item]")?.remove();
      refreshConceptEditorEmptyState();
    });
  });
  document.querySelectorAll("[data-remove-requirement]").forEach((button) => {
    button.addEventListener("click", () => {
      button.closest("[data-requirement-item]")?.remove();
      refreshRequirementsEditorEmptyState();
    });
  });
  document.querySelectorAll("[data-modal-save-kind]").forEach((button) => {
    button.addEventListener("click", async () => {
      const kind = button.getAttribute("data-modal-save-kind");
      if (!kind || !state.selectedSessionId) {
        return;
      }
      await saveModalEditorChanges(state.selectedSessionId, kind, button);
    });
  });
}

function bindSessionOverviewInteractions() {
  document.querySelectorAll("[data-session-card-id]").forEach((button) => {
    button.addEventListener("click", async () => {
      state.selectedSessionId = button.getAttribute("data-session-card-id");
      state.search = "";
      state.statusFilter = "all";
      state.submissionFilter = "all";
      state.openCardModal = null;
      if (state.selectedSessionId) {
        delete state.selectedAssignmentIds[state.selectedSessionId];
        await Promise.all([
          ensureSessionWorkspaceLoaded(state.selectedSessionId),
          ensureSessionConceptsLoaded(state.selectedSessionId),
        ]);
      }
      void renderAssignmentsPage();
    });
  });
}

function refreshConceptEditorEmptyState() {
  const list = document.querySelector("[data-concepts-list]");
  const emptyState = document.querySelector("[data-concepts-empty]");
  if (!list || !emptyState) {
    return;
  }
  emptyState.hidden = list.querySelectorAll("[data-concept-item]").length > 0;
}

function refreshRequirementsEditorEmptyState() {
  const list = document.querySelector("[data-requirements-list]");
  const emptyState = document.querySelector("[data-requirements-empty]");
  if (!list || !emptyState) {
    return;
  }
  emptyState.hidden = list.querySelectorAll("[data-requirement-item]").length > 0;
}

async function saveModalEditorChanges(sessionId, kind, saveButton) {
  const statusElement = document.querySelector("[data-modal-editor-status]");
  const previousLabel = saveButton.textContent;
  try {
    saveButton.disabled = true;
    saveButton.textContent = "Saving...";
    setModalEditorStatus(statusElement, "");
    if (kind === "concepts") {
      const payload = collectConceptsPutPayload();
      await requestJson(`/sessions/${sessionId}/concepts`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
      invalidateSessionConcepts(sessionId);
      await ensureSessionConceptsLoaded(sessionId);
    } else if (kind === "requirements") {
      const payload = collectAssignmentRequirementsPutPayload();
      await requestJson(`/sessions/${sessionId}/assignment-requirements`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
      invalidateSessionWorkspace(sessionId);
      await ensureSessionWorkspaceLoaded(sessionId);
    } else {
      throw new Error("Unsupported editor save target.");
    }
    await renderAssignmentsPage();
  } catch (error) {
    setModalEditorStatus(
      statusElement,
      error instanceof Error ? error.message : "Unable to save changes.",
      true,
    );
    saveButton.disabled = false;
    saveButton.textContent = previousLabel;
  }
}

function collectConceptsPutPayload() {
  const conceptItems = Array.from(document.querySelectorAll("[data-concept-item]"));
  return {
    concepts: conceptItems.map((item, index) => ({
      name: readRequiredField(item, "name", `Concept ${index + 1} name`),
      summary: readRequiredField(item, "summary", `Concept ${index + 1} summary`),
      grading_reason: readRequiredField(
        item,
        "grading_reason",
        `Concept ${index + 1} grading reason`,
      ),
      concept_importance: readIntegerField(
        item,
        "concept_importance",
        `Concept ${index + 1} importance`,
        1,
        10,
      ),
      evidence: readEvidenceField(item, `Concept ${index + 1} evidence`),
    })),
  };
}

function collectAssignmentRequirementsPutPayload() {
  const groups = Array.from(document.querySelectorAll("[data-assignment-requirement-group]"));
  return {
    assignment_requirements: groups.map((group, groupIndex) => ({
      assignment_requirement_id: group.getAttribute("data-assignment-requirement-id") ?? "",
      assignment_title: group.getAttribute("data-assignment-title") ?? "",
      assignment_description:
        normalizeOptionalField(group.getAttribute("data-assignment-description")) ?? null,
      due_at: normalizeOptionalField(group.getAttribute("data-due-at")) ?? null,
      required_deliverables: parseRequiredDeliverables(group),
      requirements: Array.from(group.querySelectorAll("[data-requirement-item]")).map(
        (item, itemIndex) => ({
          requirement_type: readRequiredField(
            item,
            "requirement_type",
            `Assignment ${groupIndex + 1} requirement ${itemIndex + 1} type`,
          ),
          title: readRequiredField(
            item,
            "title",
            `Assignment ${groupIndex + 1} requirement ${itemIndex + 1} title`,
          ),
          summary: readRequiredField(
            item,
            "summary",
            `Assignment ${groupIndex + 1} requirement ${itemIndex + 1} summary`,
          ),
          evidence: readEvidenceField(
            item,
            `Assignment ${groupIndex + 1} requirement ${itemIndex + 1} evidence`,
          ),
        }),
      ),
    })),
  };
}

function parseRequiredDeliverables(group) {
  const rawValue = group.getAttribute("data-required-deliverables") ?? "[]";
  try {
    const parsedValue = JSON.parse(rawValue);
    return Array.isArray(parsedValue) ? parsedValue.map((item) => String(item)) : [];
  } catch {
    return [];
  }
}

function readRequiredField(container, fieldName, label) {
  const field = container.querySelector(`[data-field="${fieldName}"]`);
  const value = normalizeDisplayText(field?.value ?? "");
  if (!value) {
    throw new Error(`${label} is required.`);
  }
  return value;
}

function readIntegerField(container, fieldName, label, minimum, maximum) {
  const rawValue = readRequiredField(container, fieldName, label);
  const parsedValue = Number.parseInt(rawValue, 10);
  if (!Number.isInteger(parsedValue) || parsedValue < minimum || parsedValue > maximum) {
    throw new Error(`${label} must be an integer between ${minimum} and ${maximum}.`);
  }
  return parsedValue;
}

function readEvidenceField(container, label) {
  const field = container.querySelector('[data-field="evidence"]');
  const values = String(field?.value ?? "")
    .split("\n")
    .map((item) => normalizeDisplayText(item))
    .filter(Boolean);
  if (values.length === 0) {
    throw new Error(`${label} must include at least one line.`);
  }
  return values;
}

function normalizeOptionalField(value) {
  const normalizedValue = normalizeDisplayText(value ?? "");
  return normalizedValue || null;
}

function setModalEditorStatus(statusElement, message, isError = false) {
  if (!statusElement) {
    return;
  }
  statusElement.textContent = message;
  statusElement.classList.toggle("is-error", isError);
}

async function renderDashboardPage() {
  dom.pageContent.innerHTML = `
    <div class="page-placeholder-layout">
      <section class="placeholder-panel panel">
        <div class="placeholder-panel-body">
          <div class="placeholder-copy">The assignments workspace is the default landing page for this build.</div>
        </div>
      </section>
    </div>
  `;
}

async function renderCoursesPage() {
  try {
    const sessions = await ensureSessionsLoaded();
    dom.pageHeaderActions.innerHTML = `
      <div class="tab-pill-group">
        <button class="tab-pill is-active" type="button">All (${sessions.length > 0 ? 1 : 0})</button>
        <button class="tab-pill" type="button">Active (${sessions.length > 0 ? 1 : 0})</button>
      </div>
      <label class="page-control search-control" aria-label="Search courses">
        <span class="page-control-icon" data-icon="search"></span>
        <input type="search" placeholder="Search courses..." disabled />
      </label>
    `;
    injectIcons();

    dom.pageContent.innerHTML = `
      <section class="course-card panel">
        <div class="assignment-card-header">
          <h2 class="course-card-title">EAG V3</h2>
          <span class="course-status-pill">Active</span>
        </div>
        <p class="course-card-description">
          ${sessions.length} sessions are currently stored in this workspace.
        </p>
        <div class="course-card-footer">
          <div class="course-card-meta">
            <span class="course-ring">${sessions.length}</span>
            <div>
              <div class="submission-name">${sessions.length}/${sessions.length} sessions</div>
              <div class="submission-code">Enrolled course</div>
            </div>
          </div>
          <span class="meta-pill">EAG V3</span>
        </div>
      </section>
    `;
  } catch (error) {
    dom.pageContent.innerHTML = `<div class="error-state">${escapeHtml(error.message)}</div>`;
  }
}

async function renderCalendarPage() {
  try {
    dom.pageHeaderActions.innerHTML = `
      <div class="page-control">All courses</div>
      <div class="calendar-mode-group">
        <button class="calendar-mode-button is-active" type="button">Month</button>
        <button class="calendar-mode-button" type="button">Agenda</button>
      </div>
    `;
    const assignments = await ensureAllAssignmentsLoaded();
    const currentDate = new Date();
    const calendarMarkup = buildCalendarMarkup(currentDate, assignments);
    dom.pageContent.innerHTML = `
      <div class="calendar-toolbar">
        <h2 class="panel-title">${calendarMarkup.monthLabel}</h2>
        <div class="summary-pill-list">
          <span class="summary-pill">${assignments.length} due items</span>
        </div>
      </div>
      <section class="calendar-panel panel">
        ${calendarMarkup.html}
      </section>
    `;
  } catch (error) {
    dom.pageContent.innerHTML = `<div class="error-state">${escapeHtml(error.message)}</div>`;
  }
}

async function renderGradesPage() {
  try {
    const assignments = await ensureAllAssignmentsLoaded();
    const reviewedCount = assignments.reduce((sum, assignment) => sum + assignment.counts.reviewed, 0);
    const pendingCount = assignments.reduce(
      (sum, assignment) => sum + assignment.counts.submitted + assignment.counts.under_review + assignment.counts.needs_resubmission,
      0,
    );
    dom.pageContent.innerHTML = `
      <section class="grade-panel panel">
        <div class="summary-stat-label">Reviewed submissions</div>
        <div class="grade-value">${reviewedCount}</div>
        <div class="grade-placeholder">
          ${pendingCount > 0 ? `${pendingCount} submissions are still pending a stored grade output.` : "No graded submissions are stored yet."}
        </div>
      </section>
    `;
  } catch (error) {
    dom.pageContent.innerHTML = `<div class="error-state">${escapeHtml(error.message)}</div>`;
  }
}

async function renderSettingsPage() {
  dom.pageContent.innerHTML = `
    <section class="placeholder-panel panel">
      <div class="placeholder-panel-body">
        <div class="placeholder-copy">Workspace settings stay in the same shell for now.</div>
      </div>
    </section>
  `;
}

function buildCalendarMarkup(date, assignments) {
  const year = date.getFullYear();
  const month = date.getMonth();
  const firstDay = new Date(year, month, 1);
  const firstVisibleDay = new Date(firstDay);
  firstVisibleDay.setDate(firstVisibleDay.getDate() - firstVisibleDay.getDay());

  const assignmentCountByDay = new Map();
  for (const assignment of assignments) {
    if (!assignment.dueAt) {
      continue;
    }
    const dueDate = new Date(assignment.dueAt);
    if (dueDate.getFullYear() !== year || dueDate.getMonth() !== month) {
      continue;
    }
    const dayKey = `${dueDate.getFullYear()}-${dueDate.getMonth()}-${dueDate.getDate()}`;
    assignmentCountByDay.set(dayKey, (assignmentCountByDay.get(dayKey) ?? 0) + 1);
  }

  const weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  let html = `<div class="calendar-grid"><div class="calendar-weekdays">${weekdays
    .map((weekday) => `<div class="calendar-weekday">${weekday}</div>`)
    .join("")}</div>`;

  const today = new Date();
  for (let rowIndex = 0; rowIndex < 6; rowIndex += 1) {
    html += '<div class="calendar-row">';
    for (let columnIndex = 0; columnIndex < 7; columnIndex += 1) {
      const cellDate = new Date(firstVisibleDay);
      cellDate.setDate(firstVisibleDay.getDate() + rowIndex * 7 + columnIndex);
      const isMuted = cellDate.getMonth() !== month;
      const isToday =
        cellDate.getFullYear() === today.getFullYear() &&
        cellDate.getMonth() === today.getMonth() &&
        cellDate.getDate() === today.getDate();
      const dayKey = `${cellDate.getFullYear()}-${cellDate.getMonth()}-${cellDate.getDate()}`;
      const itemCount = assignmentCountByDay.get(dayKey) ?? 0;
      html += `
        <div class="calendar-day ${isMuted ? "is-muted" : ""} ${isToday ? "is-today" : ""}">
          <div class="calendar-day-number">${cellDate.getDate()}</div>
          ${
            itemCount > 0
              ? `<div class="calendar-event-dots">${new Array(Math.min(itemCount, 3)).fill('<span class="calendar-event-dot"></span>').join("")}</div><div class="calendar-day-count">${itemCount} due</div>`
              : ""
          }
        </div>
      `;
    }
    html += "</div>";
  }

  html += "</div>";
  return {
    monthLabel: new Intl.DateTimeFormat("en-US", { month: "long", year: "numeric" }).format(date),
    html,
  };
}

function prettySourceType(sourceType) {
  const labels = {
    github_pr: "GitHub PR",
    local_folder: "Local folder",
    zip_upload: "Zip upload",
  };
  return labels[sourceType] ?? sourceType;
}

function formatRequirementType(requirementType) {
  const labels = {
    evidence_expectation: "Evidence expectation",
    forbidden_project_type: "Forbidden type",
    mandatory_deliverable: "Deliverable",
    scoring_criterion: "Scoring criterion",
  };
  return labels[requirementType] ?? requirementType;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function escapeAttribute(value) {
  return escapeHtml(value);
}
