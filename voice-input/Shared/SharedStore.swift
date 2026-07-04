import Foundation

/// 主 App 与键盘扩展之间通过 App Group 共享识别结果。
/// 如果你改了 Bundle ID，请把这里的 App Group ID 一并改掉，
/// 并同步修改 project.yml 里两个 entitlements 的值。
enum SharedStore {
    static let appGroupID = "group.com.example.voiceinput"
    private static let historyKey = "voice.history"
    private static let maxHistory = 20

    static var defaults: UserDefaults {
        UserDefaults(suiteName: appGroupID) ?? .standard
    }

    static var history: [String] {
        defaults.stringArray(forKey: historyKey) ?? []
    }

    static var latest: String? {
        history.first
    }

    static func save(_ text: String) {
        let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        var list = history.filter { $0 != trimmed }
        list.insert(trimmed, at: 0)
        if list.count > maxHistory {
            list = Array(list.prefix(maxHistory))
        }
        defaults.set(list, forKey: historyKey)
    }

    static func remove(at index: Int) {
        var list = history
        guard list.indices.contains(index) else { return }
        list.remove(at: index)
        defaults.set(list, forKey: historyKey)
    }

    static func clear() {
        defaults.removeObject(forKey: historyKey)
    }
}
