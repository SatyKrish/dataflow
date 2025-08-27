import React, { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Send,
  Paperclip,
  MoreVertical,
  BarChart3,
  Table2,
  FileDown,
  ChevronRight,
  Search,
  Pin as PinIcon,
  ExternalLink,
  Plus,
  Sun,
  Moon,
  AlertTriangle,
} from "lucide-react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
} from "recharts";

/***********************************
 * HEADLESS TYPES & CONTRACTS
 ***********************************/
export type Role = "user" | "agent" | "tool";

export type Artifact = {
  id: string;
  type: "chart.vegaLite" | "table.json" | "file";
  title: string;
  uri?: string; // blob path (no SAS)
  json?: any;   // small payloads (spec or table rows)
  meta?: Record<string, any>;
  pinned?: boolean;
};

export type Message = {
  id: string;
  role: Role;
  text: string;
  artifacts?: Artifact[];
  createdAt: string; // ISO string recommended from backend
};

export type Chat = {
  id: string;
  title: string;
  tags?: string[];
  lastActivity?: string; // free text or ISO; UI shows as-is
};

export interface DiscoveryAgentDataProvider {
  /** List chats visible to current user */
  listChats(signal?: AbortSignal): Promise<Chat[]>;
  /** Fetch messages for a chat (server should return newest last) */
  listMessages(chatId: string, signal?: AbortSignal): Promise<Message[]>;
  /** Send a message; optionally request to pin next artifact */
  sendMessage(params: { chatId: string; text: string; pinNext?: boolean }, signal?: AbortSignal): Promise<void>;
  /** Toggle pin status for an artifact id scoped to its chat/message */
  togglePin(params: { chatId: string; artifactId: string }, signal?: AbortSignal): Promise<void>;
  /** Optional: create a new chat and return its id */
  createChat?(params?: { title?: string }, signal?: AbortSignal): Promise<{ id: string }>;
  /** Optional: return a temporary, directly usable download URL for an artifact */
  getDownloadUrl?(params: { chatId: string; artifactId: string }, signal?: AbortSignal): Promise<string>;
}

/***********************************
 * PROVIDER GUARD & SAFE DEFAULTS
 ***********************************/
/**
 * No-op provider used when none is passed. It prevents runtime crashes
 * (like "Cannot read properties of undefined") while showing empty UI.
 * It also logs warnings so developers notice immediately.
 */
export const NoopProvider: DiscoveryAgentDataProvider = {
  async listChats() {
    if (typeof window !== "undefined") console.warn("[DiscoveryAgentUI] No provider supplied: listChats() returning []");
    return [];
  },
  async listMessages() {
    if (typeof window !== "undefined") console.warn("[DiscoveryAgentUI] No provider supplied: listMessages() returning []");
    return [];
  },
  async sendMessage() {
    if (typeof window !== "undefined") console.warn("[DiscoveryAgentUI] No provider supplied: sendMessage() ignored");
  },
  async togglePin() {
    if (typeof window !== "undefined") console.warn("[DiscoveryAgentUI] No provider supplied: togglePin() ignored");
  },
  async createChat() {
    if (typeof window !== "undefined") console.warn("[DiscoveryAgentUI] No provider supplied: createChat() ignored");
    return { id: "noop" };
  },
  async getDownloadUrl() {
    if (typeof window !== "undefined") console.warn("[DiscoveryAgentUI] No provider supplied: getDownloadUrl() ignored");
    return "";
  },
};

function isValidProvider(p: any): p is DiscoveryAgentDataProvider {
  return !!p && ["listChats", "listMessages", "sendMessage", "togglePin"].every((m) => typeof p[m] === "function");
}

/***********************************
 * THEME-AWARE PRIMITIVES
 ***********************************/
function ThemedLineChart({ data, height = "100%" }: { data: any[]; height?: number | string }) {
  const axisStroke = "hsl(var(--muted-foreground))";
  const gridStroke = "hsl(var(--border))";
  const lineStroke = "hsl(var(--foreground))";
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 10, right: 16, bottom: 10, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} />
        <XAxis dataKey="name" stroke={axisStroke} tick={{ fill: axisStroke }} />
        <YAxis stroke={axisStroke} tick={{ fill: axisStroke }} />
        <RechartsTooltip
          contentStyle={{
            background: "hsl(var(--popover))",
            color: "hsl(var(--popover-foreground))",
            border: "1px solid hsl(var(--border))",
            borderRadius: 12,
          }}
          labelStyle={{ color: "hsl(var(--popover-foreground))" }}
          itemStyle={{ color: "hsl(var(--popover-foreground))" }}
        />
        <Line type="monotone" dataKey="value" stroke={lineStroke} strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}

function formatWhen(iso?: string) {
  if (!iso) return "";
  const d = new Date(iso);
  const diff = (Date.now() - d.getTime()) / 1000;
  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return d.toLocaleString();
}

/***********************************
 * PRESENTATIONAL COMPONENTS
 ***********************************/
function EmptyState({ title, subtitle, action }: { title: string; subtitle?: string; action?: React.ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center text-center p-8 gap-2 text-muted-foreground">
      <div className="text-lg font-medium text-foreground/90">{title}</div>
      {subtitle && <div className="text-sm">{subtitle}</div>}
      {action}
    </div>
  );
}

function InlineWarning({ message }: { message: string }) {
  return (
    <div className="mx-4 my-2 flex items-center gap-2 rounded-md border border-yellow-500/40 bg-yellow-500/10 p-2 text-yellow-600 dark:text-yellow-400">
      <AlertTriangle className="h-4 w-4" />
      <span className="text-xs">{message}</span>
    </div>
  );
}

function LoadingRows({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="h-9 w-full rounded-md bg-muted animate-pulse" />
      ))}
    </div>
  );
}

function ChatList({
  chats,
  selectedId,
  onSelect,
  isLoading,
  collapsed = false,
  filter = "",
  onFilterChange,
  onNewChat,
}: {
  chats: Chat[];
  selectedId?: string;
  onSelect: (id: string) => void;
  isLoading?: boolean;
  collapsed?: boolean;
  filter?: string;
  onFilterChange?: (v: string) => void;
  onNewChat?: () => void;
}) {
  const filtered = filter
    ? chats.filter((c) => c.title.toLowerCase().includes(filter.toLowerCase()) || (c.tags ?? []).some((t) => t.toLowerCase().includes(filter.toLowerCase())))
    : chats;
  return (
    <div className="h-full flex flex-col">
      {/* Top search/filters */}
      <div className={cn("p-4", collapsed && "p-2")}>
        {!collapsed ? (
          <>
            <div className="flex items-center gap-2">
              <Search className="h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search chats…"
                className="h-8 placeholder:text-muted-foreground"
                value={filter}
                onChange={(e) => onFilterChange?.(e.target.value)}
              />
            </div>
            <div className="mt-3 flex gap-2">
              <Badge variant="secondary" className="bg-muted text-foreground">All</Badge>
            </div>
          </>
        ) : null}
      </div>

  {!collapsed && <Separator />}

      {/* List */}
      <ScrollArea className="flex-1">
        <div className={cn("p-2", collapsed && "p-1")}>
          {isLoading && <LoadingRows rows={6} />}
          {!isLoading && filtered.length === 0 && (
            <EmptyState title={collapsed ? "" : "No chats yet"} subtitle={collapsed ? "" : "Start a new conversation to see it here."} />
          )}
          {!isLoading && filtered.map((t) => (
            <button
              key={t.id}
              onClick={() => onSelect(t.id)}
              className={cn(
                "w-full text-left rounded-xl border transition mb-2",
                collapsed ? "p-2" : "p-3",
                "hover:shadow-sm hover:bg-muted/40",
                selectedId === t.id ? "bg-muted border-primary/40" : "bg-background border-border/60",
                "group"
              )}
              title={collapsed ? t.title : undefined}
            >
              <div className={cn("flex items-center justify-between", collapsed && "justify-center")}>
                <div className={cn("font-medium truncate text-foreground", collapsed && "truncate text-sm text-center")}>
                  {collapsed ? t.title.charAt(0).toUpperCase() : t.title}
                </div>
                {!collapsed && <ChevronRight className="h-4 w-4 text-muted-foreground" />}
              </div>

              {!collapsed && t.tags && t.tags.length > 0 && (
                <div className="mt-1 flex flex-wrap gap-1">
                  {t.tags.map((tag) => (
                    <Badge key={tag} variant="secondary" className="text-xs bg-muted text-foreground">{tag}</Badge>
                  ))}
                </div>
              )}

              {!collapsed && t.lastActivity && (
                <div className="text-xs text-muted-foreground mt-1">Last activity {formatWhen(t.lastActivity)}</div>
              )}
            </button>
          ))}
        </div>
      </ScrollArea>

      {/* Bottom action (fixed alignment) */}
      <div className={cn("mt-auto p-3 border-t", collapsed && "p-2")}>
        {collapsed ? (
          <Tooltip>
            <TooltipTrigger asChild>
              <Button className="w-full justify-center" size="icon" aria-label="New Chat">
                <Plus className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>New Chat</TooltipContent>
          </Tooltip>
        ) : (
          <Button className="w-full justify-center" size="sm" onClick={onNewChat}
            aria-label="New Chat">
            <Plus className="h-4 w-4 mr-2" /> New Chat
          </Button>
        )}
      </div>
    </div>
  );
}

function ArtifactPreview({ artifact, onExpand, onPin }: { artifact: Artifact; onExpand: (a: Artifact) => void; onPin: (id: string) => void }) {
  const renderThumb = () => {
    if (artifact.type === "chart.vegaLite") {
      if (!artifact.json?.series || artifact.json.series.length === 0) {
        return <EmptyState title="No chart data" subtitle="Agent will render series once available." />;
      }
      return (
        <div className="h-32">
          <ThemedLineChart data={artifact.json.series} height="100%" />
        </div>
      );
    }
    if (artifact.type === "table.json") {
      const rows: any[] = Array.isArray(artifact.json) ? artifact.json.slice(0, 3) : [];
      if (rows.length === 0) {
        return <EmptyState title="No rows" subtitle="Agent will attach table rows." />;
      }
      return (
        <Table>
          <TableHeader>
            <TableRow>
              {Object.keys(rows[0] ?? {}).map((k) => (
                <TableHead key={k} className="text-xs text-muted-foreground text-right first:text-left">{k}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((r: any, i: number) => (
              <TableRow key={i}>
                {Object.values(r).map((v: any, j: number) => (
                  <TableCell key={j} className="text-xs text-foreground text-right first:text-left tabular-nums">{typeof v === "number" ? v.toLocaleString() : String(v)}</TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      );
    }
    return (
      <div className="h-24 flex items-center justify-center bg-muted/40 rounded-md text-sm text-foreground">
        <FileDown className="h-4 w-4 mr-2" /> {artifact.title}
      </div>
    );
  };

  return (
    <Card className="rounded-2xl shadow-sm border-border/60">
      <CardHeader className="p-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-semibold truncate text-foreground">{artifact.title}</CardTitle>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-7 w-7 text-muted-foreground">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>Artifact</DropdownMenuLabel>
              <DropdownMenuItem onClick={() => onPin(artifact.id)}>
                <PinIcon className="h-4 w-4 mr-2" /> {artifact.pinned ? "Unpin" : "Pin"}
              </DropdownMenuItem>
              {artifact.uri && (
                <DropdownMenuItem onClick={() => window.open(artifact.uri!, "_blank")}> 
                  <div className="flex items-center">
                    <ExternalLink className="h-4 w-4 mr-2" /> Open source
                  </div>
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
        <CardDescription className="text-xs">
          <div className="flex items-center gap-2">
            {artifact.type.startsWith("chart") && (
              <Badge variant="secondary" className="bg-muted text-foreground">
                <BarChart3 className="h-3 w-3 mr-1" /> Chart
              </Badge>
            )}
            {artifact.type === "table.json" && (
              <Badge variant="secondary" className="bg-muted text-foreground">
                <Table2 className="h-3 w-3 mr-1" /> Table
              </Badge>
            )}
            {artifact.type === "file" && (
              <Badge variant="secondary" className="bg-muted text-foreground">
                <FileDown className="h-3 w-3 mr-1" /> File
              </Badge>
            )}
          </div>
        </CardDescription>
      </CardHeader>
      <CardContent className="p-4 pt-0">
        {renderThumb()}
      </CardContent>
      <CardFooter className="p-4 pt-0 flex gap-2">
        <Button size="sm" variant="outline" onClick={() => onExpand(artifact)}>
          Expand
        </Button>
        <Button size="sm" variant="ghost" onClick={() => onPin(artifact.id)} className="text-muted-foreground">
          <PinIcon className="h-4 w-4 mr-1" /> {artifact.pinned ? "Unpin" : "Pin"}
        </Button>
      </CardFooter>
    </Card>
  );
}

function MessageBubble({ m, onExpand, onPin }: { m: Message; onExpand: (a: Artifact) => void; onPin: (id: string) => void }) {
  const isUser = m.role === "user";
  return (
    <div className={cn("flex gap-3", isUser ? "justify-end" : "justify-start")}>
      {!isUser && (
        <Avatar className="h-8 w-8 mt-1">
          <AvatarFallback className="bg-muted text-foreground">A</AvatarFallback>
        </Avatar>
      )}
      <div className="max-w-[720px] w-full">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
          className={cn(
            "rounded-2xl p-4 border",
            isUser ? "bg-primary text-primary-foreground" : "bg-card text-card-foreground border-border/60"
          )}
        >
          <div className="text-sm leading-relaxed whitespace-pre-wrap">{m.text}</div>
        </motion.div>
        {m.artifacts && m.artifacts.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3 mt-3">
            {m.artifacts.map((a) => (
              <ArtifactPreview key={a.id} artifact={a} onExpand={onExpand} onPin={onPin} />
            ))}
          </div>
        )}
  <div className="text-xs text-muted-foreground mt-2">{formatWhen(m.createdAt)}</div>
      </div>
      {isUser && (
        <Avatar className="h-8 w-8 mt-1">
          <AvatarFallback className="bg-muted text-foreground">U</AvatarFallback>
        </Avatar>
      )}
    </div>
  );
}

function ArtifactViewer({ artifact }: { artifact: Artifact | null }) {
  if (!artifact) return null;
  return (
    <Tabs defaultValue="preview" className="w-full h-full">
      <TabsList className="grid grid-cols-4">
        <TabsTrigger value="preview">Preview</TabsTrigger>
        <TabsTrigger value="data">Data</TabsTrigger>
        <TabsTrigger value="meta">Meta</TabsTrigger>
        <TabsTrigger value="download">Download</TabsTrigger>
      </TabsList>
      <div className="mt-3 border rounded-xl h-[75vh] p-3 bg-background text-foreground border-border/60">
        <TabsContent value="preview" className="h-full">
          {artifact.type === "chart.vegaLite" && (
            <div className="h-full">
              {artifact.json?.series?.length ? (
                <ThemedLineChart data={artifact.json.series} />
              ) : (
                <EmptyState title="No chart data" />
              )}
            </div>
          )}
          {artifact.type === "table.json" && (
            <ScrollArea className="h-full">
              {Array.isArray(artifact.json) && artifact.json.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      {Object.keys((artifact.json?.[0]) ?? {}).map((k) => (
                        <TableHead key={k} className="text-foreground text-right first:text-left">{k}</TableHead>
                      ))}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {artifact.json.map((r: any, i: number) => (
                      <TableRow key={i}>
                        {Object.values(r).map((v: any, j: number) => (
                          <TableCell key={j} className="text-foreground text-right first:text-left tabular-nums">{typeof v === "number" ? v.toLocaleString() : String(v)}</TableCell>
                        ))}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <EmptyState title="No rows" />
              )}
            </ScrollArea>
          )}
          {artifact.type === "file" && (
            <div className="h-full flex items-center justify-center text-sm text-muted-foreground">
              <FileDown className="h-4 w-4 mr-2" /> {artifact.title}
            </div>
          )}
        </TabsContent>
        <TabsContent value="data" className="h-full">
          <ScrollArea className="h-full">
            <pre className="text-xs whitespace-pre-wrap bg-muted rounded-md p-3 text-foreground/90">{JSON.stringify(artifact.json ?? { uri: artifact.uri }, null, 2)}</pre>
          </ScrollArea>
        </TabsContent>
        <TabsContent value="meta" className="h-full">
          <ScrollArea className="h-full">
            <Table>
              <TableBody>
                {Object.entries(artifact.meta ?? {}).map(([k, v]) => (
                  <TableRow key={k}>
                    <TableCell className="font-medium text-foreground">{k}</TableCell>
                    <TableCell className="text-muted-foreground">{typeof v === "object" ? JSON.stringify(v) : String(v)}</TableCell>
                  </TableRow>
                ))}
                <TableRow>
                  <TableCell className="font-medium text-foreground">type</TableCell>
                  <TableCell className="text-muted-foreground">{artifact.type}</TableCell>
                </TableRow>
                {artifact.uri && (
                  <TableRow>
                    <TableCell className="font-medium text-foreground">blob path</TableCell>
                    <TableCell className="text-muted-foreground">{artifact.uri}</TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </ScrollArea>
        </TabsContent>
        <TabsContent value="download" className="h-full">
          <div className="h-full flex items-center justify-center">
            {artifact.uri ? (
              <a href={artifact.uri} target="_blank" rel="noreferrer">
                <Button variant="default">
                  <FileDown className="h-4 w-4 mr-2" /> Open Download
                </Button>
              </a>
            ) : (
              <Button variant="default" disabled>
                <FileDown className="h-4 w-4 mr-2" /> No download available
              </Button>
            )}
          </div>
        </TabsContent>
      </div>
    </Tabs>
  );
}

function ThemeToggle({ dark, setDark }: { dark: boolean; setDark: (b: boolean) => void }) {
  const nextLabel = dark ? "Switch to light mode" : "Switch to dark mode";
  return (
    <Button
      variant="outline"
      size="icon"
      onClick={() => setDark(!dark)}
      aria-label={nextLabel}
      title={nextLabel}
    >
      {dark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
    </Button>
  );
}

/***********************************
 * ROOT APP (HEADLESS)
 ***********************************/
export default function DiscoveryAgentUI({ provider, initialDark = true }: { provider?: DiscoveryAgentDataProvider; initialDark?: boolean }) {
  // pick a safe provider (either the real one or a no-op fallback)
  const safeProvider = useMemo(() => (isValidProvider(provider) ? (provider as DiscoveryAgentDataProvider) : NoopProvider), [provider]);
  const [dark, setDark] = useState(initialDark);
  // Initialize theme from localStorage if present (overrides initialDark)
  useEffect(() => {
    try {
      const saved = typeof window !== "undefined" ? localStorage.getItem("theme") : null;
      if (saved === "dark" || saved === "light") {
        setDark(saved === "dark");
      }
    } catch {}
  }, []);
  // Ensure Radix portals (Sheets/Tooltips) also get dark mode by toggling it on <html>
  useEffect(() => {
    if (typeof document !== "undefined") {
      document.documentElement.classList.toggle("dark", dark);
      document.documentElement.setAttribute("data-theme", dark ? "dark" : "light");
      try { localStorage.setItem("theme", dark ? "dark" : "light"); } catch {}
    }
  }, [dark]);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [chats, setChats] = useState<Chat[]>([]);
  const [selectedChatId, setSelectedChatId] = useState<string | undefined>();
  const [messages, setMessages] = useState<Message[]>([]);
  const [composer, setComposer] = useState("");
  const [selectedArtifact, setSelectedArtifact] = useState<Artifact | null>(null);
  const [loadingChats, setLoadingChats] = useState(false);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [providerWarning, setProviderWarning] = useState<string | null>(null);
  const [chatFilter, setChatFilter] = useState("");
  const bottomRef = React.useRef<HTMLDivElement | null>(null);

  function formatWhen(iso?: string) {
    if (!iso) return "";
    const d = new Date(iso);
    const diff = (Date.now() - d.getTime()) / 1000;
    if (diff < 60) return "just now";
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return d.toLocaleString();
  }

  // show a one-time warning if provider is missing/invalid
  useEffect(() => {
    if (safeProvider === NoopProvider) {
      setProviderWarning(
        "No DiscoveryAgentDataProvider was supplied. />."
      );
    } else {
      setProviderWarning(null);
    }
  }, [safeProvider]);

  // load chats
  useEffect(() => {
    const ac = new AbortController();
    setLoadingChats(true);
    safeProvider
      .listChats(ac.signal)
      .then((list) => {
        setChats(list);
        // auto-select first chat if none selected
        if (!selectedChatId && list[0]?.id) setSelectedChatId(list[0].id);
      })
      .catch((err) => {
        console.error("[DiscoveryAgentUI] listChats failed:", err);
        setProviderWarning("Provider.listChats failed: " + (err?.message || String(err)));
      })
      .finally(() => setLoadingChats(false));
    return () => ac.abort();
  }, [safeProvider]); // refresh if provider changes

  // load messages for selected chat
  useEffect(() => {
    if (!selectedChatId) return;
    const ac = new AbortController();
    setLoadingMessages(true);
    safeProvider
      .listMessages(selectedChatId, ac.signal)
      .then((list) => setMessages(list))
      .catch((err) => {
        console.error("[DiscoveryAgentUI] listMessages failed:", err);
        setProviderWarning("Provider.listMessages failed: " + (err?.message || String(err)));
      })
      .finally(() => setLoadingMessages(false));
    return () => ac.abort();
  }, [selectedChatId, safeProvider]);

  // scroll to bottom when messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length]);

  const selectedChat = useMemo(() => chats.find((c) => c.id === selectedChatId), [chats, selectedChatId]);

  const onSend = async () => {
    if (!composer.trim() || !selectedChatId) return;
    const text = composer.trim();
    setComposer("");
    // optimistic user message
    const localUser: Message = {
      id: `local-user-${Date.now()}`,
      role: "user",
      text,
      createdAt: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, localUser]);
    try {
      await safeProvider.sendMessage({
        chatId: selectedChatId,
        text,
        pinNext: (document.getElementById("pin-next") as HTMLInputElement)?.checked,
      });
      // poll for assistant response briefly (backend may be async)
      const start = Date.now();
      let attempts = 0;
      const baselineCount = messages.length + 1; // includes optimistic
      const poll = async () => {
        const ac = new AbortController();
        setLoadingMessages(true);
        try {
          const list = await safeProvider.listMessages(selectedChatId, ac.signal);
          setMessages(list);
          const newCount = list.length;
          const last = list[list.length - 1];
          const gotAssistant = newCount > baselineCount && last && last.role !== "user";
          if (!gotAssistant && Date.now() - start < 7000 && attempts < 12) {
            attempts++;
            setTimeout(poll, 500);
          }
        } catch {
          // keep trying briefly
          if (Date.now() - start < 7000 && attempts < 12) {
            attempts++;
            setTimeout(poll, 500);
          }
        } finally {
          setLoadingMessages(false);
        }
      };
      poll();
    } catch (err: any) {
      console.error("[DiscoveryAgentUI] sendMessage failed:", err);
      setProviderWarning("Provider.sendMessage failed: " + (err?.message || String(err)));
    }
  };

  const onNewChat = async () => {
    try {
      if (typeof (safeProvider as any).createChat === "function") {
        const { id } = await (safeProvider as any).createChat({ title: "Chat" });
        // refresh chats and select
        const list = await safeProvider.listChats();
        setChats(list);
        setSelectedChatId(id);
        setMessages([]);
      } else {
        setProviderWarning("Provider does not support creating chats.");
      }
    } catch (err: any) {
      setProviderWarning("Create chat failed: " + (err?.message || String(err)));
    }
  };

  const onPin = async (artifactId: string) => {
    if (!selectedChatId) return;
    try {
      await safeProvider.togglePin({ chatId: selectedChatId, artifactId });
      const ac = new AbortController();
      safeProvider.listMessages(selectedChatId, ac.signal).then(setMessages);
    } catch (err: any) {
      console.error("[DiscoveryAgentUI] togglePin failed:", err);
      setProviderWarning("Provider.togglePin failed: " + (err?.message || String(err)));
    }
  };

  return (
    <TooltipProvider>
      <div
        className={cn(
          dark && "dark",
          "h-screen w-full grid",
          sidebarCollapsed ? "grid-cols-[56px_1fr]" : "grid-cols-[280px_1fr] lg:grid-cols-[320px_1fr]",
          "bg-background text-foreground"
        )}
      >
        {/* Left rail: chats */}
        <div className="border-r bg-background flex flex-col">
          <div
            className={cn(
              "h-12 border-b flex items-center",
              sidebarCollapsed ? "justify-center px-2" : "justify-between px-3"
            )}
          >
            <div className={cn("min-w-0 flex-1", sidebarCollapsed && "hidden")}>
              <div className="text-lg font-semibold">Chats</div>
            </div>
            <div className="flex items-center gap-2">
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    onClick={() => setSidebarCollapsed((v) => !v)}
                    aria-label={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
                  >
                    {sidebarCollapsed ? (
                      <ChevronRight className="h-4 w-4" />
                    ) : (
                      <ChevronRight className="h-4 w-4 rotate-180" />
                    )}
                  </Button>
                </TooltipTrigger>
                <TooltipContent>{sidebarCollapsed ? "Expand" : "Collapse"}</TooltipContent>
              </Tooltip>
            </div>
          </div>

          <ChatList
            chats={chats}
            selectedId={selectedChatId}
            onSelect={setSelectedChatId}
            isLoading={loadingChats}
            collapsed={sidebarCollapsed}
            filter={chatFilter}
            onFilterChange={setChatFilter}
            onNewChat={onNewChat}
          />
        </div>

        {/* Center: chat + composer */}
        <div className="flex flex-col">
          {/* Header */}
          <div className="h-14 border-b flex items-center justify-between px-4 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="flex items-center gap-2">
              <div className="text-base font-semibold truncate max-w-[60vw] text-foreground">
                {selectedChat?.title ?? ""}
              </div>
              {selectedChat?.tags?.map((t) => (
                <Badge key={t} variant="outline" className="border-border/70">{t}</Badge>
              ))}
            </div>
            <div className="flex items-center gap-2">
              {/* Avatar */}
              <Avatar>
                <AvatarFallback className="bg-muted text-foreground">U</AvatarFallback>
              </Avatar>
              {/* Theme toggle */}
              <Tooltip>
                <TooltipTrigger asChild>
                  <span>
                    <ThemeToggle dark={dark} setDark={setDark} />
                  </span>
                </TooltipTrigger>
                <TooltipContent>{dark ? "Switch to light mode" : "Switch to dark mode"}</TooltipContent>
              </Tooltip>
              {/* Artifacts button */}
              <Sheet>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <SheetTrigger asChild>
                      <Button variant="outline" size="icon" aria-label="Artifacts">
                        <FileDown className="h-4 w-4" />
                      </Button>
                    </SheetTrigger>
                  </TooltipTrigger>
                  <TooltipContent>Artifacts</TooltipContent>
                </Tooltip>
                <SheetContent side="right" className="w-[420px] sm:w-[520px]">
                  <SheetHeader>
                    <SheetTitle>Pinned & Recent Artifacts</SheetTitle>
                  </SheetHeader>
                  <Separator className="my-3" />
                  <ScrollArea className="h-[85vh] pr-2">
                    <div className="grid grid-cols-1 gap-3">
                      {messages
                        .flatMap((m) => m.artifacts ?? [])
                        .filter((a, i, arr) => arr.findIndex((x) => x.id === a.id) === i)
                        .sort((a, b) => Number(b.pinned) - Number(a.pinned))
                        .map((a) => (
                          <ArtifactPreview key={a.id} artifact={a} onExpand={(art) => setSelectedArtifact(art)} onPin={onPin} />
                        ))}
                      {(!messages.flatMap((m) => m.artifacts ?? []).length) && (
                        <EmptyState title="No artifacts yet" subtitle="Ask the agent to generate charts, tables, or files." />
                      )}
                    </div>
                  </ScrollArea>
                </SheetContent>
              </Sheet>
            </div>
          </div>

          {providerWarning && <InlineWarning message={providerWarning} />}

          {/* Messages */}
          <ScrollArea className="flex-1 p-4">
            <div className="mx-auto w-full max-w-[980px] space-y-6">
              {loadingMessages && <LoadingRows rows={6} />}
              {!loadingMessages && messages.length === 0 && (
                <EmptyState title="Start the conversation." />
              )}
              {!loadingMessages && messages.map((m) => (
                <MessageBubble key={m.id} m={m} onExpand={setSelectedArtifact} onPin={(id) => onPin(id)} />
              ))}
              <div ref={bottomRef} />
            </div>
          </ScrollArea>

          {/* Composer */}
          <div className="border-t p-3">
            <div className="mx-auto w-full max-w-[980px]">
              <div className="rounded-2xl border p-2 bg-background">
                <Textarea
                  placeholder="Ask a question or attach files for the discovery agent…"
                  value={composer}
                  onChange={(e) => setComposer(e.target.value)}
                  className="min-h-[72px] resize-none border-0 focus-visible:ring-0 placeholder:text-muted-foreground text-foreground"
                />
                <div className="flex items-center justify-between px-2 pb-2">
                  <div className="flex items-center gap-2">
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button variant="ghost" size="icon" className="text-muted-foreground"><Paperclip className="h-4 w-4" /></Button>
                      </TooltipTrigger>
                      <TooltipContent>Attach file (stored in Blob)</TooltipContent>
                    </Tooltip>
                  </div>
                  <div className="flex items-center gap-2">
                    <Checkbox id="pin-next" />
                    <label htmlFor="pin-next" className="text-xs text-muted-foreground">Pin next artifact</label>
                    <Button size="sm" onClick={onSend}><Send className="h-4 w-4 mr-1" /> Send</Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right-side Artifact Viewer (Sheet) */}
      <Sheet open={!!selectedArtifact} onOpenChange={(open) => !open && setSelectedArtifact(null)}>
        <SheetContent side="right" className="w-[480px] sm:w-[600px]">
          <SheetHeader>
            <SheetTitle>{selectedArtifact?.title ?? "Artifact"}</SheetTitle>
          </SheetHeader>
          <div className="mt-3">
            <ArtifactViewer artifact={selectedArtifact} />
          </div>
        </SheetContent>
      </Sheet>
    </TooltipProvider>
  );
}
