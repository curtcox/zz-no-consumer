import Foundation
import CoreImage

// Generate a reference QR with CoreImage and dump its modules as text.
let text = CommandLine.arguments[1]
let level = CommandLine.arguments[2]      // L M Q H
let out = CommandLine.arguments[3]
let filter = CIFilter(name: "CIQRCodeGenerator")!
filter.setValue(text.data(using: .isoLatin1) ?? Data(), forKey: "inputMessage")
filter.setValue(level, forKey: "inputCorrectionLevel")
let image = filter.outputImage!
let extent = image.extent
let context = CIContext()
let cg = context.createCGImage(image, from: extent)!
// CIQRCodeGenerator emits 1 pixel per module plus a 1-module quiet zone.
let w = cg.width, h = cg.height
var pixels = [UInt8](repeating: 0, count: w * h)
let space = CGColorSpaceCreateDeviceGray()
let ctx = CGContext(data: &pixels, width: w, height: h, bitsPerComponent: 8,
                    bytesPerRow: w, space: space, bitmapInfo: 0)!
ctx.draw(cg, in: CGRect(x: 0, y: 0, width: w, height: h))
var lines: [String] = []
for y in 0..<h {
    var line = ""
    for x in 0..<w { line += pixels[y * w + x] < 128 ? "1" : "0" }
    lines.append(line)
}
try! lines.joined(separator: "\n").write(toFile: out, atomically: true, encoding: .utf8)
print("\(w)x\(h)")
