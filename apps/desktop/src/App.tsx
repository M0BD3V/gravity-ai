import {
  Activity,
  Brain,
  HardDrive,
  MessageSquare,
  PlugZap,
  Send,
  ShieldCheck,
  Sparkles,
  TerminalSquare,
  WifiOff,
} from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";
import type { HealthResponse, ToolDefinition } from "@gravity-ai/shared";
import { getHealth, getTools, sendChat } from "./api/client";

type TranscriptMessage = {
  id: string;
  role: "assistant" | "user";
  content: string;
  meta?: string;
};

const initialMessages: TranscriptMessage[] = [
  {
    id: "welcome",
    role: "assistant",
    content: "Gravity AI foundation online. Runtime local, ferramentas seguras e plugins por manifesto estao prontos.",
    meta: "gravity-local",
  },
];

export function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [tools, setTools] = useState<ToolDefinition[]>([]);
  const [messages, setMessages] = useState<TranscriptMessage[]>(initialMessages);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    Promise.all([getHealth(), getTools()])
      .then(([healthResponse, toolResponse]) => {
        if (!active) return;
        setHealth(healthResponse);
        setTools(toolResponse);
        setApiError(null);
      })
      .catch(() => {
        if (!active) return;
        setApiError("API offline");
      });

    return () => {
      active = false;
    };
  }, []);

  const groupedTools = useMemo(() => {
    const safe = tools.filter((tool) => tool.risk === "safe" || tool.risk === "low");
    const sensitive = tools.filter((tool) => tool.risk !== "safe" && tool.risk !== "low");
    return { safe, sensitive };
  }, [tools]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const content = input.trim();
    if (!content || isSending) return;

    const userMessage: TranscriptMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content,
    };

    setMessages((current) => [...current, userMessage]);
    setInput("");
    setIsSending(true);

    try {
      const response = await sendChat(content);
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: response.message,
          meta: response.model,
        },
      ]);
      setApiError(null);
    } catch {
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: "Nao consegui alcancar a API local. Inicie o backend para continuar.",
          meta: "offline",
        },
      ]);
      setApiError("API offline");
    } finally {
      setIsSending(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="titlebar">
        <div className="brand-lockup">
          <div className="brand-mark">
            <Sparkles size={18} aria-hidden="true" />
          </div>
          <div>
            <p className="eyebrow">Gravity AI</p>
            <h1>Assistente Windows</h1>
          </div>
        </div>
        <div className="status-strip">
          <StatusPill
            icon={health ? Activity : WifiOff}
            label={health ? "API online" : apiError ?? "Conectando"}
            tone={health ? "online" : "offline"}
          />
          <StatusPill icon={ShieldCheck} label="Confirmacao ativa" tone="secure" />
        </div>
      </header>

      <section className="workspace">
        <aside className="sidebar" aria-label="Contexto do sistema">
          <section className="system-panel">
            <div className="section-heading">
              <Brain size={16} aria-hidden="true" />
              <span>Runtime</span>
            </div>
            <dl className="metrics">
              <div>
                <dt>Versao</dt>
                <dd>{health?.version ?? "0.1.0"}</dd>
              </div>
              <div>
                <dt>Ferramentas</dt>
                <dd>{health?.tools ?? tools.length}</dd>
              </div>
              <div>
                <dt>Plugins</dt>
                <dd>{health?.plugins ?? 0}</dd>
              </div>
            </dl>
          </section>

          <section className="system-panel">
            <div className="section-heading">
              <PlugZap size={16} aria-hidden="true" />
              <span>Plugins</span>
            </div>
            <div className="plugin-row">
              <span>example-file-assistant</span>
              <strong>loaded</strong>
            </div>
          </section>

          <section className="system-panel">
            <div className="section-heading">
              <HardDrive size={16} aria-hidden="true" />
              <span>Workspace</span>
            </div>
            <p className="path-line">{health?.rootDir ?? "E:\\Users\\Mob\\Nova pasta (2)\\Gravity Assistente"}</p>
          </section>
        </aside>

        <section className="conversation" aria-label="Conversa">
          <div className="conversation-header">
            <div>
              <p className="eyebrow">Session</p>
              <h2>Command Center</h2>
            </div>
            <TerminalSquare size={20} aria-hidden="true" />
          </div>

          <div className="message-list">
            {messages.map((message) => (
              <article className={`message ${message.role}`} key={message.id}>
                <div className="message-avatar">
                  {message.role === "assistant" ? <Sparkles size={16} /> : <MessageSquare size={16} />}
                </div>
                <div className="message-body">
                  <p>{message.content}</p>
                  {message.meta ? <span>{message.meta}</span> : null}
                </div>
              </article>
            ))}
          </div>

          <form className="composer" onSubmit={handleSubmit}>
            <input
              aria-label="Mensagem para Gravity AI"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Organize minha pasta Downloads"
            />
            <button type="submit" disabled={isSending || input.trim().length === 0} aria-label="Enviar">
              <Send size={18} aria-hidden="true" />
            </button>
          </form>
        </section>

        <aside className="tool-panel" aria-label="Ferramentas">
          <div className="tool-panel-header">
            <p className="eyebrow">Tools</p>
            <h2>Registry</h2>
          </div>

          <ToolGroup title="Baixo risco" tools={groupedTools.safe} />
          <ToolGroup title="Confirmacao" tools={groupedTools.sensitive} />
        </aside>
      </section>
    </main>
  );
}

function StatusPill({
  icon: Icon,
  label,
  tone,
}: {
  icon: typeof Activity;
  label: string;
  tone: "online" | "offline" | "secure";
}) {
  return (
    <span className={`status-pill ${tone}`}>
      <Icon size={15} aria-hidden="true" />
      {label}
    </span>
  );
}

function ToolGroup({ title, tools }: { title: string; tools: ToolDefinition[] }) {
  return (
    <section className="tool-group">
      <h3>{title}</h3>
      <div className="tool-list">
        {tools.length === 0 ? <p className="empty-state">Aguardando backend</p> : null}
        {tools.map((tool) => (
          <article className="tool-card" key={tool.name}>
            <div>
              <strong>{tool.name}</strong>
              <span>{tool.risk}</span>
            </div>
            <p>{tool.description}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

