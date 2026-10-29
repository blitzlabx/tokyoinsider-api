/**
 * Blitz TokyoInsider Scraper API — Cloudflare Worker (edge proxy)
 * Author: Blitz (@blitzlabx)
 *
 * Proxies requests to your real backend (Render / Docker).
 * Does NOT run the Python scraper inside the Worker.
 */

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const backend = (env.BACKEND_URL || "").replace(/\/$/, "");

    // Health / identity at the edge
    if (url.pathname === "/" || url.pathname === "/health") {
      return Response.json(
        {
          name: "Blitz TokyoInsider Scraper API (Cloudflare edge)",
          author: "Blitz",
          handle: "@blitzlabx",
          github: "https://github.com/blitzlabx/tokyoinsider-api",
          mode: "proxy",
          backend: backend || null,
          note:
            "Workers cannot host the full Python scraper. " +
            "Set BACKEND_URL to your Render/Docker instance, or use Cloudflare Containers.",
        },
        {
          headers: {
            "Access-Control-Allow-Origin": "*",
            "X-Powered-By": "Blitz (@blitzlabx)",
          },
        }
      );
    }

    if (!backend) {
      return Response.json(
        {
          error: "no_backend",
          detail:
            "Set BACKEND_URL in wrangler.toml or via `wrangler secret` / dashboard. " +
            "Deploy the real API on Render or Docker first.",
          author: "Blitz (@blitzlabx)",
        },
        { status: 503, headers: { "Access-Control-Allow-Origin": "*" } }
      );
    }

    // Proxy everything else to the real API
    const target = backend + url.pathname + url.search;
    const headers = new Headers(request.headers);
    headers.delete("host");

    const init = {
      method: request.method,
      headers,
      redirect: "follow",
    };
    if (request.method !== "GET" && request.method !== "HEAD") {
      init.body = request.body;
    }

    try {
      const upstream = await fetch(target, init);
      const out = new Response(upstream.body, upstream);
      out.headers.set("Access-Control-Allow-Origin", "*");
      out.headers.set("X-Powered-By", "Blitz (@blitzlabx)");
      out.headers.set("X-Proxied-By", "cloudflare-worker");
      return out;
    } catch (err) {
      return Response.json(
        {
          error: "proxy_failed",
          detail: String(err),
          author: "Blitz (@blitzlabx)",
        },
        { status: 502, headers: { "Access-Control-Allow-Origin": "*" } }
      );
    }
  },
};
