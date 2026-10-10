// 教學網站前置程式：讓 MP4 支援分段讀取（iPhone Safari 播放需要 206 回應），其餘檔案照原樣回傳。
const NOINDEX = "noindex, nofollow, noarchive";

function withHeaders(res, extra) {
 const h = new Headers(res.headers);
 h.set("X-Robots-Tag", NOINDEX);
 h.set("X-Content-Type-Options", "nosniff");
 h.set("Referrer-Policy", "strict-origin-when-cross-origin");
 for (const [k, v] of Object.entries(extra || {})) h.set(k, v);
 return new Response(res.body, { status: res.status, statusText: res.statusText, headers: h });
}

export default {
 async fetch(request, env) {
 const url = new URL(request.url);
 const isVideo = url.pathname.endsWith(".mp4");
 if (!isVideo) return withHeaders(await env.ASSETS.fetch(request));

 const base = await env.ASSETS.fetch(new Request(url.toString(), { method: "GET" }));
 if (base.status !== 200) return withHeaders(base);
 if (request.method !== "GET" && request.method !== "HEAD") {
 return withHeaders(new Response(null, { status: 405 }), { Allow: "GET, HEAD" });
 }
 const range = request.method === "HEAD" ? null : request.headers.get("Range");
 const common = { "Accept-Ranges": "bytes", "Content-Type": "video/mp4", "Cache-Control": "public, max-age=86400" };
 if (!range) return withHeaders(request.method === "HEAD" ? new Response(null, { headers: base.headers }) : base, common);

 const buf = await base.arrayBuffer();
 const size = buf.byteLength;
 const m = /^bytes=(\d*)-(\d*)$/.exec(range.trim());
 if (!m || (m[1] === "" && m[2] === "")) {
 return withHeaders(new Response(null, { status: 416 }), { "Content-Range": `bytes */${size}` });
 }
 let start, end;
 if (m[1] === "") { start = Math.max(0, size - Number(m[2])); end = size - 1; }
 else { start = Number(m[1]); end = m[2] === "" ? size - 1 : Math.min(Number(m[2]), size - 1); }
 if (!Number.isSafeInteger(start) || !Number.isSafeInteger(end) || start >= size || start > end) {
 return withHeaders(new Response(null, { status: 416 }), { "Content-Range": `bytes */${size}` });
 }
 return withHeaders(new Response(buf.slice(start, end + 1), { status: 206 }), {
 ...common,
 "Content-Range": `bytes ${start}-${end}/${size}`,
 "Content-Length": String(end - start + 1),
 });
 },
};
