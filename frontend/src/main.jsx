import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

const API = (
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "");

async function api(path, opt = {}) {
  const r = await fetch(API + path, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(opt.headers || {}),
    },
    ...opt,
  });

  const d = await r.json().catch(() => ({}));

  if (!r.ok) {
    throw Error(d.error || d.detail || "Request failed");
  }

  return d;
}

function b64(s) {
  const m = "=".repeat((4 - (s.length % 4)) % 4);
  const x = (s + m).replace(/-/g, "+").replace(/_/g, "/");

  return Uint8Array.from(atob(x), (c) => c.charCodeAt(0));
}

function Login({ on }) {
  const [email, setEmail] = useState("admin@notifyhub.local");
  const [pw, setPw] = useState("Admin@12345");
  const [err, setErr] = useState("");

  const handleLogin = async () => {
    try {
      setErr("");

      await api("/api/login/", {
        method: "POST",
        body: JSON.stringify({
          email,
          password: pw,
        }),
      });

      on();
    } catch (e) {
      setErr(e.message);
    }
  };

  return (
    <div className="login">
      <div className="loginbox">
        <h1>NotifyHub</h1>
        <p>Admin Login</p>

        <input
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
        />

        <input
          value={pw}
          onChange={(e) => setPw(e.target.value)}
          type="password"
          placeholder="Password"
        />

        <button onClick={handleLogin}>Login</button>

        {err && <div className="error">{err}</div>}
      </div>
    </div>
  );
}

function App() {
  const [user, setUser] = useState(null);
  const [tr, setTr] = useState([]);
  const [logs, setLogs] = useState([]);
  const [msg, setMsg] = useState("");
  const [push, setPush] = useState(false);

  const load = async () => {
    try {
      const [triggerData, logData] = await Promise.all([
        api("/api/triggers/"),
        api("/api/logs/"),
      ]);

      setTr(triggerData);
      setLogs(logData);
    } catch (e) {
      setMsg(e.message);
    }
  };

  useEffect(() => {
    api("/api/me/")
      .then((data) => {
        if (data.authenticated !== false) {
          setUser(data);
        }
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (user) {
      load();
    }
  }, [user]);

  const enablePush = async () => {
    try {
      if (!("serviceWorker" in navigator) || !("PushManager" in window)) {
        throw Error("This browser does not support Web Push.");
      }

      const permission = await Notification.requestPermission();

      if (permission !== "granted") {
        throw Error("Browser notification permission was not granted.");
      }

      const reg = await navigator.serviceWorker.register("/sw.js");

      const key = (await api("/api/push/public-key/")).public_key;

      if (!key) {
        throw Error("VAPID public key is missing in backend .env");
      }

      const sub = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: b64(key),
      });

      await api("/api/push/subscribe/", {
        method: "POST",
        body: JSON.stringify(sub.toJSON()),
      });

      setPush(true);
      setMsg("Web Push connected.");
    } catch (e) {
      setMsg(e.message);
    }
  };

  const test = async (template) => {
    let recipient;

    if (template.channel === "email") {
      recipient = prompt(
        "Recipient email",
        user?.email || ""
      );
    } else if (template.channel === "whatsapp") {
      recipient = prompt(
        "WhatsApp number",
        "+91"
      );
    } else {
      recipient = "browser";
    }

    if (recipient === null) {
      return;
    }

    try {
      await api("/api/test-send/", {
        method: "POST",
        body: JSON.stringify({
          template_id: template.id,
          recipient,
        }),
      });

      setMsg(`${template.channel} sent successfully.`);
      await load();
    } catch (e) {
      setMsg(e.message);
      await load();
    }
  };

  const getTemplate = (trigger, channel) => {
    return trigger.templates?.find(
      (template) => template.channel === channel
    );
  };

  if (!user) {
    return (
      <Login
        on={() =>
          api("/api/me/")
            .then((data) => setUser(data))
            .catch(() => {})
        }
      />
    );
  }

  return (
    <div className="page">

      {/* HEADER */}
      <header>
        <div>
          <h1>NotifyHub</h1>
          <p>Notification control center</p>
        </div>

        <div className="header-actions">
          <span className={push ? "ok" : "pill"}>
            {push
              ? "Web Push Connected"
              : "Web Push not connected"}
          </span>

          <button
            onClick={() =>
              api("/api/logout/", {
                method: "POST",
              }).then(() => setUser(null))
            }
          >
            Logout
          </button>
        </div>
      </header>

      {msg && <div className="notice">{msg}</div>}

      {/* TRIGGERS */}
      <section className="card">
        <h2>Triggers</h2>

        <div className="trigger-table">

          <div className="trigger-header">
            <div>Trigger</div>
            <div>WhatsApp</div>
            <div>Email</div>
            <div>Web Push</div>
          </div>

          {tr.map((trigger) => (
            <div
              className="trigger-row"
              key={trigger.id}
            >
              <div>
                <strong>{trigger.name}</strong>

                <small>
                  {trigger.description}
                </small>
              </div>

              <div>
                {trigger.whatsapp_enabled ? "ON" : "OFF"}
              </div>

              <div>
                {trigger.email_enabled ? "ON" : "OFF"}
              </div>

              <div>
                {trigger.web_push_enabled ? "ON" : "OFF"}
              </div>
            </div>
          ))}

        </div>
      </section>

      {/* TEMPLATES */}
      <section className="card">

        <div className="row">
          <h2>Templates</h2>

          <button onClick={enablePush}>
            Enable browser notifications
          </button>
        </div>

        <div className="template-table">

          {/* HEADER */}
          <div className="template-header">

            <div>
              Trigger
            </div>

            <div>
              WhatsApp
            </div>

            <div>
              Email
            </div>

            <div>
              Web Push
            </div>

          </div>

          {/* ROWS */}
          {tr.map((trigger) => (

            <div
              className="template-row"
              key={trigger.id}
            >

              {/* TRIGGER */}
              <div className="trigger-name">

                <strong>
                  {trigger.name}
                </strong>

                <small>
                  {trigger.description}
                </small>

              </div>

              {/* CHANNELS */}
              {["whatsapp", "email", "web_push"].map(
                (channel) => {

                  const template =
                    getTemplate(trigger, channel);

                  return (

                    <div
                      className="template-cell"
                      key={channel}
                    >

                      {template ? (
                        <>
                          <div className="template-title">

                            <strong>
                              {template.name}
                            </strong>

                            <span>
                              {channel}
                            </span>

                          </div>

                          {template.subject && (
                            <div className="template-subject">
                              <strong>
                                Subject:
                              </strong>{" "}
                              {template.subject}
                            </div>
                          )}

                          <p>
                            {template.body}
                          </p>

                          <button
                            className="test-button"
                            onClick={() =>
                              test(template)
                            }
                          >
                            Test Send
                          </button>
                        </>
                      ) : (

                        <span className="not-configured">
                          Not configured
                        </span>

                      )}

                    </div>

                  );
                }
              )}

            </div>

          ))}

        </div>

      </section>

      {/* DELIVERY LOGS */}
      <section className="card">

        <h2>Delivery logs</h2>

        <div className="logs-table">

          <table>

            <thead>

              <tr>
                <th>Time</th>
                <th>Channel</th>
                <th>Recipient</th>
                <th>Status</th>
                <th>Message</th>
              </tr>

            </thead>

            <tbody>

              {logs.map((log) => (

                <tr key={log.id}>

                  <td>
                    {new Date(
                      log.created_at
                    ).toLocaleString()}
                  </td>

                  <td>
                    {log.channel}
                  </td>

                  <td>
                    {log.recipient}
                  </td>

                  <td
                    className={log.status}
                  >
                    {log.status}
                  </td>

                  <td>
                    {log.message}
                  </td>

                </tr>

              ))}

            </tbody>

          </table>

        </div>

      </section>

    </div>
  );
}

createRoot(
  document.getElementById("root")
).render(<App />);