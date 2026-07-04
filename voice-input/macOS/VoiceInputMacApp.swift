import SwiftUI

@main
struct VoiceInputMacApp: App {
    @StateObject private var controller = DictationController()

    var body: some Scene {
        MenuBarExtra {
            MenuContentView(controller: controller)
        } label: {
            Image(systemName: controller.speech.isRecording ? "mic.fill" : "mic")
        }
        .menuBarExtraStyle(.window)
    }
}
