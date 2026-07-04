import AppKit
import ApplicationServices
import Combine
import Foundation

/// Mac 端听写总控：全局快捷键 ⌃⌥D 开始/停止，
/// 「边说边输入」模式下实时把识别文字打进当前应用。
@MainActor
final class DictationController: ObservableObject {
    @Published var localeID = "zh-TW"
    @Published var liveTyping = true

    let speech = SpeechRecognizer()

    private var hotKey: HotKey?
    private var cancellables = Set<AnyCancellable>()
    /// 已经打进目标应用的字符，用来和最新识别结果做差量更新
    private var injectedChars: [Character] = []

    init() {
        // speech 是嵌套的 ObservableObject，把它的变更转发出去，
        // 菜单栏图标（mic / mic.fill）才能跟随录音状态刷新
        speech.objectWillChange
            .receive(on: RunLoop.main)
            .sink { [weak self] _ in
                self?.objectWillChange.send()
            }
            .store(in: &cancellables)

        speech.$transcript
            .receive(on: RunLoop.main)
            .sink { [weak self] text in
                self?.syncLiveTyping(with: text)
            }
            .store(in: &cancellables)

        hotKey = HotKey { [weak self] in
            Task { @MainActor in
                self?.toggle()
            }
        }

        requestAccessibilityIfNeeded()
    }

    var accessibilityGranted: Bool {
        AXIsProcessTrusted()
    }

    func toggle() {
        if speech.isRecording {
            stop()
        } else {
            start()
        }
    }

    func start() {
        injectedChars = []
        speech.start(localeIdentifier: localeID)
    }

    func stop() {
        speech.stop()
        let text = speech.transcript.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else { return }
        if !liveTyping {
            TextInjector.type(text)
        }
        SharedStore.save(text)
    }

    func copyTranscript() {
        let text = speech.transcript
        guard !text.isEmpty else { return }
        NSPasteboard.general.clearContents()
        NSPasteboard.general.setString(text, forType: .string)
    }

    // MARK: - 边说边输入（差量注入）

    private func syncLiveTyping(with text: String) {
        guard liveTyping, speech.isRecording else { return }
        let newChars = Array(text)
        let commonPrefix = zip(injectedChars, newChars).prefix { $0 == $1 }.count
        let deleteCount = injectedChars.count - commonPrefix
        if deleteCount > 0 {
            TextInjector.backspace(deleteCount)
        }
        if commonPrefix < newChars.count {
            TextInjector.type(String(newChars[commonPrefix...]))
        }
        injectedChars = newChars
    }

    private func requestAccessibilityIfNeeded() {
        let options = [kAXTrustedCheckOptionPrompt.takeUnretainedValue() as String: true] as CFDictionary
        AXIsProcessTrustedWithOptions(options)
    }
}
