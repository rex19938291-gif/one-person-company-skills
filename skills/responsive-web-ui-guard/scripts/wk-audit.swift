// 用法：swiftc -O wk-audit.swift -o wk-audit && ./wk-audit <網址> <檢查.js> <截圖前綴> <寬度> <截圖屏數(0=不截)>
import Cocoa
import WebKit
let a = CommandLine.arguments
let url = URL(string: a[1])!, js = try! String(contentsOfFile: a[2]), out = a[3]
let W = Double(a[4])!, maxShots = Int(a[5])!, H = 900.0
let app = NSApplication.shared
app.setActivationPolicy(.prohibited)
let win = NSWindow(contentRect: NSRect(x: 0, y: 0, width: W, height: H), styleMask: [.borderless], backing: .buffered, defer: false)
let cfg = WKWebViewConfiguration()
let wv = WKWebView(frame: NSRect(x: 0, y: 0, width: W, height: H), configuration: cfg)
if W < 700 { wv.customUserAgent = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1" }
win.contentView = wv
win.alphaValue = 0.02; win.ignoresMouseEvents = true; win.orderBack(nil)
wv.load(URLRequest(url: url))
var total = 0.0
func shot(_ i: Int) {
  if i >= maxShots || Double(i) * H >= total { exit(0) }
  wv.evaluateJavaScript("window.scrollTo(0,\(Double(i) * H));") { _, _ in
    DispatchQueue.main.asyncAfter(deadline: .now() + 0.6) {
      wv.takeSnapshot(with: nil) { img, err in
        if let img = img, let t = img.tiffRepresentation, let r = NSBitmapImageRep(data: t), let p = r.representation(using: .png, properties: [:]) {
          try! p.write(to: URL(fileURLWithPath: "\(out)-\(String(format: "%02d", i)).png"))
        }
        shot(i + 1)
      }
    }
  }
}
DispatchQueue.main.asyncAfter(deadline: .now() + 8) {
  wv.callAsyncJavaScript(js, arguments: [:], in: nil, in: .page) { r in
    switch r { case .success(let v): print(v ?? "nil"); case .failure(let e): print("JSERR", e) }
    wv.evaluateJavaScript("document.documentElement.scrollHeight") { h, _ in total = (h as? Double) ?? H; shot(0) }
  }
}
DispatchQueue.main.asyncAfter(deadline: .now() + 150) { exit(1) }
app.run()
