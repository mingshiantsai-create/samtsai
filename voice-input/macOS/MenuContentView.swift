import SwiftUI

struct MenuContentView: View {
    @ObservedObject var controller: DictationController
    @ObservedObject var speech: SpeechRecognizer

    init(controller: DictationController) {
        self.controller = controller
        self.speech = controller.speech
    }

    private let languages: [(id: String, name: String)] = [
        ("zh-TW", "國語（台灣）"),
        ("zh-CN", "普通话"),
        ("en-US", "English"),
        ("ja-JP", "日本語"),
    ]

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: speech.isRecording ? "mic.fill" : "mic")
                    .foregroundStyle(speech.isRecording ? .red : .secondary)
                Text(speech.isRecording ? "正在聆听…" : "语音输入")
                    .font(.headline)
                Spacer()
            }

            Picker("语言", selection: $controller.localeID) {
                ForEach(languages, id: \.id) { lang in
                    Text(lang.name).tag(lang.id)
                }
            }
            .disabled(speech.isRecording)

            Toggle("边说边输入（实时打字进当前应用）", isOn: $controller.liveTyping)
                .disabled(speech.isRecording)

            Button {
                controller.toggle()
            } label: {
                Label(speech.isRecording ? "停止听写" : "开始听写",
                      systemImage: speech.isRecording ? "stop.circle.fill" : "mic.circle.fill")
                    .frame(maxWidth: .infinity)
            }
            .controlSize(.large)
            .keyboardShortcut("d", modifiers: [.control, .option])

            if !speech.transcript.isEmpty {
                ScrollView {
                    Text(speech.transcript)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .textSelection(.enabled)
                }
                .frame(maxHeight: 100)
                .padding(8)
                .background(Color(nsColor: .textBackgroundColor))
                .clipShape(RoundedRectangle(cornerRadius: 8))

                Button("复制识别结果") {
                    controller.copyTranscript()
                }
            }

            if let error = speech.errorMessage {
                Text(error)
                    .font(.caption)
                    .foregroundStyle(.red)
            }

            if !controller.accessibilityGranted {
                Text("⚠️ 尚未授予「辅助功能」权限，无法自动打字。\n请在 系统设置 → 隐私与安全性 → 辅助功能 中勾选本应用。")
                    .font(.caption)
                    .foregroundStyle(.orange)
            }

            Divider()

            HStack {
                Text("全局快捷键：⌃⌥D（先点到目标输入框再按）")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Spacer()
                Button("退出") {
                    NSApplication.shared.terminate(nil)
                }
                .font(.caption)
            }
        }
        .padding(14)
        .frame(width: 320)
    }
}
