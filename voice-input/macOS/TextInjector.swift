import Cocoa
import CoreGraphics

/// 把文字以「模拟键盘输入」的方式打进当前聚焦的应用。
/// 需要系统「辅助功能」权限（首次运行会弹出授权提示）。
enum TextInjector {
    private static let backspaceKeyCode: CGKeyCode = 51
    private static let chunkSize = 20 // CGEvent 单次最多携带 20 个 UTF-16 字符

    static func type(_ text: String) {
        guard !text.isEmpty else { return }
        let source = CGEventSource(stateID: .combinedSessionState)
        let utf16 = Array(text.utf16)
        var index = 0
        while index < utf16.count {
            let chunk = Array(utf16[index..<min(index + chunkSize, utf16.count)])
            postUnicode(chunk, keyDown: true, source: source)
            postUnicode(chunk, keyDown: false, source: source)
            index += chunkSize
            usleep(5000)
        }
    }

    static func backspace(_ count: Int) {
        guard count > 0 else { return }
        let source = CGEventSource(stateID: .combinedSessionState)
        for _ in 0..<count {
            CGEvent(keyboardEventSource: source, virtualKey: backspaceKeyCode, keyDown: true)?
                .post(tap: .cghidEventTap)
            CGEvent(keyboardEventSource: source, virtualKey: backspaceKeyCode, keyDown: false)?
                .post(tap: .cghidEventTap)
            usleep(2000)
        }
    }

    private static func postUnicode(_ chars: [UniChar], keyDown: Bool, source: CGEventSource?) {
        guard let event = CGEvent(keyboardEventSource: source, virtualKey: 0, keyDown: keyDown) else {
            return
        }
        event.keyboardSetUnicodeString(stringLength: chars.count, unicodeString: chars)
        event.post(tap: .cghidEventTap)
    }
}
