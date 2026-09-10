import Foundation
import CoreImage
import Vision

// Decode QR symbols in PNG files with the system scanner, and print
// "<path>\tOK\t<payload>" or "<path>\tFAIL\t<reason>" for each.
let paths = Array(CommandLine.arguments.dropFirst())
for path in paths {
    guard let image = CIImage(contentsOf: URL(fileURLWithPath: path)) else {
        print("\(path)\tFAIL\tunreadable"); continue
    }
    let request = VNDetectBarcodesRequest()
    request.symbologies = [.qr]
    let handler = VNImageRequestHandler(ciImage: image, options: [:])
    do {
        try handler.perform([request])
        let results = (request.results ?? []).compactMap { $0.payloadStringValue }
        if let payload = results.first {
            print("\(path)\tOK\t\(payload)")
        } else {
            print("\(path)\tFAIL\tno symbol found")
        }
    } catch {
        print("\(path)\tFAIL\t\(error)")
    }
}
