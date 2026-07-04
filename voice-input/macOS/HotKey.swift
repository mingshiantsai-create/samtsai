import Carbon.HIToolbox
import Foundation

/// 全局快捷键（默认 ⌃⌥D），基于 Carbon RegisterEventHotKey，无需额外权限。
final class HotKey {
    typealias Handler = () -> Void

    private var hotKeyRef: EventHotKeyRef?
    private var eventHandlerRef: EventHandlerRef?
    private let handler: Handler

    /// 默认注册 Control + Option + D
    init(keyCode: UInt32 = UInt32(kVK_ANSI_D),
         modifiers: UInt32 = UInt32(controlKey | optionKey),
         handler: @escaping Handler) {
        self.handler = handler

        var eventType = EventTypeSpec(eventClass: OSType(kEventClassKeyboard),
                                      eventKind: UInt32(kEventHotKeyPressed))
        let selfPointer = Unmanaged.passUnretained(self).toOpaque()

        InstallEventHandler(GetApplicationEventTarget(), { _, _, userData -> OSStatus in
            guard let userData else { return noErr }
            let hotKey = Unmanaged<HotKey>.fromOpaque(userData).takeUnretainedValue()
            DispatchQueue.main.async {
                hotKey.handler()
            }
            return noErr
        }, 1, &eventType, selfPointer, &eventHandlerRef)

        let hotKeyID = EventHotKeyID(signature: OSType(0x564F4943), id: 1) // 'VOIC'
        RegisterEventHotKey(keyCode, modifiers, hotKeyID,
                            GetApplicationEventTarget(), 0, &hotKeyRef)
    }

    deinit {
        if let hotKeyRef {
            UnregisterEventHotKey(hotKeyRef)
        }
        if let eventHandlerRef {
            RemoveEventHandler(eventHandlerRef)
        }
    }
}
